#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Geração de Relatórios PDF
Versão 1.1 - Sistema de Apostas Desportivas

Este módulo é responsável por gerar relatórios profissionais em PDF
com gráficos integrados e análises detalhadas.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import pandas as pd
import numpy as np
from io import BytesIO
import base64

class GeradorRelatorios:
    """Classe responsável pela geração de relatórios PDF profissionais."""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
        
    def _configurar_estilos(self):
        """Configura estilos personalizados para o relatório."""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        ))
        
        # Estilo para texto destacado
        self.styles.add(ParagraphStyle(
            name='Destaque',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        ))
    
    def _conectar_db(self) -> sqlite3.Connection:
        """Estabelece conexão com a base de dados."""
        return sqlite3.connect(self.db_path)
    
    def _obter_dados_apostas(self, data_inicio: Optional[str] = None, 
                            data_fim: Optional[str] = None) -> pd.DataFrame:
        """Obtém dados das apostas para análise."""
        conn = self._conectar_db()
        
        query = """
        SELECT 
            data_hora,
            competicao,
            equipa_casa,
            equipa_fora,
            tipo_aposta,
            odd,
            valor_apostado,
            resultado,
            lucro_prejuizo,
            notas
        FROM apostas
        """
        
        params = []
        if data_inicio and data_fim:
            query += " WHERE data_hora BETWEEN ? AND ?"
            params = [data_inicio, data_fim]
        
        query += " ORDER BY data_hora DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def _gerar_grafico_evolucao_banca(self, df: pd.DataFrame) -> str:
        """Gera gráfico da evolução da banca."""
        plt.figure(figsize=(12, 6))
        
        # Calcular evolução da banca
        df['data_aposta'] = pd.to_datetime(df['data_aposta'])
        df = df.sort_values('data_aposta')
        df['banca_acumulada'] = df['lucro_prejuizo'].cumsum()
        
        plt.plot(df['data_aposta'], df['banca_acumulada'], 
                linewidth=2, color='#2E8B57', marker='o', markersize=4)
        
        plt.title('Evolução da Banca ao Longo do Tempo', fontsize=16, fontweight='bold')
        plt.xlabel('Data', fontsize=12)
        plt.ylabel('Valor Acumulado (€)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Formatação do eixo X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Salvar gráfico
        caminho_grafico = 'temp_evolucao_banca.png'
        plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
        plt.close()
        
        return caminho_grafico
    
    def _gerar_grafico_distribuicao_resultados(self, df: pd.DataFrame) -> str:
        """Gera gráfico de distribuição de resultados."""
        plt.figure(figsize=(10, 6))
        
        # Contar resultados
        resultados = df['resultado'].value_counts()
        cores = ['#32CD32', '#FF6347', '#FFD700']  # Verde, Vermelho, Amarelo
        
        plt.pie(resultados.values, labels=resultados.index, autopct='%1.1f%%',
               colors=cores, startangle=90, textprops={'fontsize': 12})
        
        plt.title('Distribuição de Resultados das Apostas', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        # Salvar gráfico
        caminho_grafico = 'temp_distribuicao_resultados.png'
        plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
        plt.close()
        
        return caminho_grafico
    
    def _gerar_grafico_performance_desporto(self, df: pd.DataFrame) -> str:
        """Gera gráfico de performance por desporto."""
        plt.figure(figsize=(12, 6))
        
        # Agrupar por desporto
        performance = df.groupby('desporto').agg({
            'lucro_prejuizo': 'sum',
            'resultado': lambda x: (x == 'Ganha').sum() / len(x) * 100
        }).round(2)
        
        performance.columns = ['Lucro/Prejuízo', 'Taxa de Sucesso (%)']
        
        # Criar gráfico de barras
        ax = performance.plot(kind='bar', figsize=(12, 6), 
                             color=['#4CAF50', '#2196F3'], alpha=0.8)
        
        plt.title('Performance por Desporto', fontsize=16, fontweight='bold')
        plt.xlabel('Desporto', fontsize=12)
        plt.ylabel('Valor', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar gráfico
        caminho_grafico = 'temp_performance_desporto.png'
        plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
        plt.close()
        
        return caminho_grafico
    
    def _calcular_estatisticas(self, df: pd.DataFrame) -> Dict:
        """Calcula estatísticas principais."""
        total_apostas = len(df)
        apostas_ganhas = len(df[df['resultado'] == 'Ganha'])
        apostas_perdidas = len(df[df['resultado'] == 'Perdida'])
        apostas_pendentes = len(df[df['resultado'] == 'Pendente'])
        
        taxa_sucesso = (apostas_ganhas / total_apostas * 100) if total_apostas > 0 else 0
        
        valor_total_apostado = df['valor_apostado'].sum()
        lucro_prejuizo_total = df['lucro_prejuizo'].sum()
        
        roi = (lucro_prejuizo_total / valor_total_apostado * 100) if valor_total_apostado > 0 else 0
        
        valor_medio_aposta = df['valor_apostado'].mean() if total_apostas > 0 else 0
        odds_media = df['odds'].mean() if total_apostas > 0 else 0
        
        return {
            'total_apostas': total_apostas,
            'apostas_ganhas': apostas_ganhas,
            'apostas_perdidas': apostas_perdidas,
            'apostas_pendentes': apostas_pendentes,
            'taxa_sucesso': round(taxa_sucesso, 2),
            'valor_total_apostado': round(valor_total_apostado, 2),
            'lucro_prejuizo_total': round(lucro_prejuizo_total, 2),
            'roi': round(roi, 2),
            'valor_medio_aposta': round(valor_medio_aposta, 2),
            'odds_media': round(odds_media, 2)
        }
    
    def gerar_relatorio_completo(self, data_inicio: Optional[str] = None,
                                data_fim: Optional[str] = None,
                                nome_arquivo: Optional[str] = None,
                                incluir_graficos: bool = True,
                                incluir_analise: bool = True,
                                incluir_recomendacoes: bool = True) -> str:
        """Gera relatório completo em PDF."""
        
        # Definir nome do arquivo
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_apostas_{timestamp}.pdf"
        
        # Garantir que o diretório exports existe
        os.makedirs('exports', exist_ok=True)
        caminho_arquivo = os.path.join('exports', nome_arquivo)
        
        # Obter dados
        df = self._obter_dados_apostas(data_inicio, data_fim)
        
        if df.empty:
            print("⚠️ Aviso: Não foram encontrados dados para o período especificado.")
            # Retornar None quando não há dados para evitar erro de arquivo não encontrado
            return None
        
        # Calcular estatísticas
        stats = self._calcular_estatisticas(df)
        
        # Gerar gráficos
        grafico_evolucao = self._gerar_grafico_evolucao_banca(df)
        grafico_distribuicao = self._gerar_grafico_distribuicao_resultados(df)
        grafico_performance = self._gerar_grafico_performance_desporto(df)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4)
        story = []
        
        # Título principal
        titulo = Paragraph("📊 RELATÓRIO DE APOSTAS DESPORTIVAS", self.styles['TituloPrincipal'])
        story.append(titulo)
        story.append(Spacer(1, 20))
        
        # Informações do período
        periodo_texto = f"Período: {data_inicio or 'Início'} até {data_fim or 'Presente'}"
        data_geracao = f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        
        story.append(Paragraph(periodo_texto, self.styles['Normal']))
        story.append(Paragraph(data_geracao, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Resumo executivo
        story.append(Paragraph("📈 RESUMO EXECUTIVO", self.styles['Subtitulo']))
        
        resumo_data = [
            ['Métrica', 'Valor'],
            ['Total de Apostas', str(stats['total_apostas'])],
            ['Apostas Ganhas', str(stats['apostas_ganhas'])],
            ['Apostas Perdidas', str(stats['apostas_perdidas'])],
            ['Apostas Pendentes', str(stats['apostas_pendentes'])],
            ['Taxa de Sucesso', f"{stats['taxa_sucesso']}%"],
            ['Valor Total Apostado', f"€{stats['valor_total_apostado']}"],
            ['Lucro/Prejuízo Total', f"€{stats['lucro_prejuizo_total']}"],
            ['ROI', f"{stats['roi']}%"],
            ['Valor Médio por Aposta', f"€{stats['valor_medio_aposta']}"],
            ['Odds Média', str(stats['odds_media'])]
        ]
        
        tabela_resumo = Table(resumo_data, colWidths=[3*inch, 2*inch])
        tabela_resumo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(tabela_resumo)
        story.append(Spacer(1, 30))
        
        # Gráfico de evolução da banca
        story.append(Paragraph("📊 EVOLUÇÃO DA BANCA", self.styles['Subtitulo']))
        story.append(Image(grafico_evolucao, width=6*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        # Gráfico de distribuição de resultados
        story.append(Paragraph("🎯 DISTRIBUIÇÃO DE RESULTADOS", self.styles['Subtitulo']))
        story.append(Image(grafico_distribuicao, width=5*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        # Gráfico de performance por desporto
        story.append(Paragraph("🏆 PERFORMANCE POR DESPORTO", self.styles['Subtitulo']))
        story.append(Image(grafico_performance, width=6*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        # Análise e recomendações
        story.append(Paragraph("💡 ANÁLISE E RECOMENDAÇÕES", self.styles['Subtitulo']))
        
        # Análise automática baseada nos dados
        analise_texto = self._gerar_analise_automatica(stats, df)
        for paragrafo in analise_texto:
            story.append(Paragraph(paragrafo, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Construir PDF
        doc.build(story)
        
        # Limpar arquivos temporários
        for arquivo_temp in [grafico_evolucao, grafico_distribuicao, grafico_performance]:
            if os.path.exists(arquivo_temp):
                os.remove(arquivo_temp)
        
        return caminho_arquivo
    
    def _gerar_analise_automatica(self, stats: Dict, df: pd.DataFrame) -> List[str]:
        """Gera análise automática baseada nos dados."""
        analise = []
        
        # Análise da taxa de sucesso
        if stats['taxa_sucesso'] >= 60:
            analise.append("✅ <b>Excelente performance:</b> Sua taxa de sucesso está acima de 60%, indicando boa capacidade de análise.")
        elif stats['taxa_sucesso'] >= 50:
            analise.append("⚠️ <b>Performance moderada:</b> Taxa de sucesso entre 50-60%. Há espaço para melhorias na seleção de apostas.")
        else:
            analise.append("❌ <b>Performance baixa:</b> Taxa de sucesso abaixo de 50%. Recomenda-se revisar a estratégia de apostas.")
        
        # Análise do ROI
        if stats['roi'] > 10:
            analise.append("💰 <b>ROI excelente:</b> Retorno superior a 10% indica gestão eficiente do bankroll.")
        elif stats['roi'] > 0:
            analise.append("📈 <b>ROI positivo:</b> Está no caminho certo, mas pode otimizar para maiores retornos.")
        else:
            analise.append("📉 <b>ROI negativo:</b> Necessário reavaliar estratégia e gestão de risco.")
        
        # Análise do valor médio das apostas
        if stats['valor_medio_aposta'] > 0:
            percentual_banca = (stats['valor_medio_aposta'] / stats['valor_total_apostado']) * 100
            if percentual_banca <= 5:
                analise.append("✅ <b>Gestão conservadora:</b> Valor médio por aposta está dentro dos padrões recomendados.")
            else:
                analise.append("⚠️ <b>Atenção à gestão:</b> Valor médio por aposta pode estar alto. Considere reduzir para melhor gestão de risco.")
        
        # Recomendações gerais
        analise.append("<b>Recomendações:</b>")
        analise.append("• Mantenha registros detalhados de todas as apostas")
        analise.append("• Defina limites claros de perda diária e mensal")
        analise.append("• Diversifique entre diferentes desportos e mercados")
        analise.append("• Analise regularmente sua performance para identificar padrões")
        
        return analise
    
    def gerar_relatorio_mensal(self, ano: int, mes: int) -> str:
        """Gera relatório específico para um mês."""
        data_inicio = f"{ano}-{mes:02d}-01"
        
        # Calcular último dia do mês
        if mes == 12:
            proximo_mes = 1
            proximo_ano = ano + 1
        else:
            proximo_mes = mes + 1
            proximo_ano = ano
        
        ultimo_dia = (datetime(proximo_ano, proximo_mes, 1) - timedelta(days=1)).day
        data_fim = f"{ano}-{mes:02d}-{ultimo_dia}"
        
        nome_arquivo = f"relatorio_mensal_{ano}_{mes:02d}.pdf"
        
        return self.gerar_relatorio_completo(data_inicio, data_fim, nome_arquivo)
    
    def gerar_relatorio_anual(self, ano: int) -> str:
        """Gera relatório específico para um ano."""
        data_inicio = f"{ano}-01-01"
        data_fim = f"{ano}-12-31"
        nome_arquivo = f"relatorio_anual_{ano}.pdf"
        
        return self.gerar_relatorio_completo(data_inicio, data_fim, nome_arquivo)

# Função de conveniência para uso direto
def gerar_relatorio_pdf(data_inicio: Optional[str] = None,
                       data_fim: Optional[str] = None,
                       nome_arquivo: Optional[str] = None) -> str:
    """Função de conveniência para gerar relatório PDF."""
    gerador = GeradorRelatorios()
    return gerador.gerar_relatorio_completo(data_inicio, data_fim, nome_arquivo)

if __name__ == "__main__":
    # Teste do módulo
    try:
        gerador = GeradorRelatorios()
        arquivo = gerador.gerar_relatorio_completo()
        print(f"Relatório gerado com sucesso: {arquivo}")
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")