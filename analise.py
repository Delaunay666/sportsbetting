#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Análise Avançada e Machine Learning
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from main import DatabaseManager
import sqlite3
from pathlib import Path

# Machine Learning removido conforme solicitado

# Imports para relatórios
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class AnaliseFrame(ctk.CTkScrollableFrame):
    """Frame para análise avançada e machine learning"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.df_apostas = None
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Criar widgets da análise"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="🧠 Análise Avançada",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Notebook para diferentes análises
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Abas
        self.create_patterns_tab()
        self.create_reports_tab()
        self.create_predictions_tab()
    
    def create_patterns_tab(self):
        """Criar aba de padrões identificados"""
        patterns_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(patterns_frame, text="📊 Padrões")
        
        # Título da seção
        ctk.CTkLabel(
            patterns_frame,
            text="🔍 Padrões Identificados",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame de análises
        self.patterns_content = ctk.CTkScrollableFrame(patterns_frame)
        self.patterns_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botão para atualizar análise
        update_btn = ctk.CTkButton(
            patterns_frame,
            text="🔄 Atualizar Análise",
            command=self.analyze_patterns,
            height=35
        )
        update_btn.pack(pady=10)
    
    # Aba de Machine Learning removida conforme solicitado
    
    def create_reports_tab(self):
        """Criar aba de relatórios"""
        reports_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(reports_frame, text="📄 Relatórios")
        
        # Título
        ctk.CTkLabel(
            reports_frame,
            text="📄 Geração de Relatórios",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame de opções
        options_frame = ctk.CTkFrame(reports_frame)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Período do relatório
        ctk.CTkLabel(
            options_frame,
            text="Período do Relatório:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        period_frame = ctk.CTkFrame(options_frame)
        period_frame.pack(pady=10)
        
        self.period_combo = ctk.CTkComboBox(
            period_frame,
            values=["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano", "Todos os dados"],
            width=200
        )
        self.period_combo.pack(side="left", padx=10)
        
        # Tipo de relatório
        ctk.CTkLabel(
            options_frame,
            text="Tipo de Relatório:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 5))
        
        report_frame = ctk.CTkFrame(options_frame)
        report_frame.pack(pady=10)
        
        self.report_type_combo = ctk.CTkComboBox(
            report_frame,
            values=["Relatório Completo", "Resumo Executivo", "Análise de Performance", "Relatório de Banca"],
            width=200
        )
        self.report_type_combo.pack(side="left", padx=10)
        
        # Botões de exportação
        export_frame = ctk.CTkFrame(reports_frame)
        export_frame.pack(pady=20)
        
        if PDF_AVAILABLE:
            ctk.CTkButton(
                export_frame,
                text="📄 Exportar PDF",
                command=self.export_pdf,
                height=35,
                width=150,
                fg_color="#dc3545",
                hover_color="#c82333"
            ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            export_frame,
            text="📊 Exportar Excel",
            command=self.export_excel,
            height=35,
            width=150,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            export_frame,
            text="💾 Backup Completo",
            command=self.create_backup,
            height=35,
            width=150,
            fg_color="#17a2b8",
            hover_color="#138496"
        ).pack(side="left", padx=10)
    
    def create_predictions_tab(self):
        """Criar aba de previsões e sugestões"""
        pred_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(pred_frame, text="🔮 Previsões")
        
        # Título
        ctk.CTkLabel(
            pred_frame,
            text="🔮 Previsões e Sugestões",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Área de sugestões
        self.suggestions_text = ctk.CTkTextbox(
            pred_frame,
            height=400,
            font=ctk.CTkFont(size=12)
        )
        self.suggestions_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botão para gerar sugestões
        ctk.CTkButton(
            pred_frame,
            text="💡 Gerar Sugestões",
            command=self.generate_suggestions,
            height=35
        ).pack(pady=10)
    
    def load_data(self):
        """Carregar dados para análise"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            
            # Carregar apostas
            query = """
                SELECT * FROM apostas
                ORDER BY data_hora DESC
            """
            
            self.df_apostas = pd.read_sql_query(query, conn)
            conn.close()
            
            # Processar dados
            if not self.df_apostas.empty:
                self.df_apostas['data'] = pd.to_datetime(self.df_apostas['data_hora'])
                self.df_apostas['lucro_numerico'] = pd.to_numeric(self.df_apostas['lucro_prejuizo'], errors='coerce')
                self.df_apostas['odd_numerica'] = pd.to_numeric(self.df_apostas['odd'], errors='coerce')
                self.df_apostas['valor_numerico'] = pd.to_numeric(self.df_apostas['valor_apostado'], errors='coerce')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def analyze_patterns(self):
        """Analisar padrões nas apostas"""
        # Limpar conteúdo anterior
        for widget in self.patterns_content.winfo_children():
            widget.destroy()
        
        if self.df_apostas is None or self.df_apostas.empty:
            ctk.CTkLabel(
                self.patterns_content,
                text="❌ Sem dados suficientes para análise",
                font=ctk.CTkFont(size=16),
                text_color="#ff6b6b"
            ).pack(pady=20)
            return
        
        try:
            # Análise de performance por competição
            self.analyze_competition_performance()
            
            # Análise de tipos de aposta
            self.analyze_bet_types()
            
            # Análise de odds
            self.analyze_odds_patterns()
            
            # Análise temporal
            self.analyze_temporal_patterns()
            
            # Análise de sequências
            self.analyze_sequences()
            
        except Exception as e:
            ctk.CTkLabel(
                self.patterns_content,
                text=f"❌ Erro na análise: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="#ff6b6b"
            ).pack(pady=10)
    
    def analyze_competition_performance(self):
        """Analisar performance por competição"""
        comp_frame = ctk.CTkFrame(self.patterns_content)
        comp_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            comp_frame,
            text="🏆 Performance por Competição",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Agrupar por competição
        comp_stats = self.df_apostas.groupby('competicao').agg({
            'resultado': ['count', lambda x: (x == 'Ganha').sum()],
            'lucro_numerico': 'sum',
            'valor_numerico': 'sum'
        }).round(2)
        
        comp_stats.columns = ['Total', 'Ganhas', 'Lucro', 'Apostado']
        comp_stats['Taxa_Acerto'] = (comp_stats['Ganhas'] / comp_stats['Total'] * 100).round(1)
        comp_stats['ROI'] = (comp_stats['Lucro'] / comp_stats['Apostado'] * 100).round(1)
        
        # Mostrar top 5 competições
        top_comps = comp_stats.nlargest(5, 'ROI')
        
        for idx, (comp, stats) in enumerate(top_comps.iterrows()):
            color = "#00ff88" if stats['ROI'] > 0 else "#ff6b6b"
            
            comp_label = ctk.CTkLabel(
                comp_frame,
                text=f"{idx+1}. {comp}: {stats['Taxa_Acerto']:.1f}% acerto, ROI: {stats['ROI']:.1f}%",
                text_color=color
            )
            comp_label.pack(anchor="w", padx=20, pady=2)
    
    def analyze_bet_types(self):
        """Analisar tipos de aposta"""
        type_frame = ctk.CTkFrame(self.patterns_content)
        type_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            type_frame,
            text="🎯 Performance por Tipo de Aposta",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Agrupar por tipo
        type_stats = self.df_apostas.groupby('tipo_aposta').agg({
            'resultado': ['count', lambda x: (x == 'Ganha').sum()],
            'lucro_numerico': 'sum',
            'valor_numerico': 'sum'
        }).round(2)
        
        type_stats.columns = ['Total', 'Ganhas', 'Lucro', 'Apostado']
        type_stats['Taxa_Acerto'] = (type_stats['Ganhas'] / type_stats['Total'] * 100).round(1)
        type_stats['ROI'] = (type_stats['Lucro'] / type_stats['Apostado'] * 100).round(1)
        
        for tipo, stats in type_stats.iterrows():
            color = "#00ff88" if stats['ROI'] > 0 else "#ff6b6b"
            
            type_label = ctk.CTkLabel(
                type_frame,
                text=f"{tipo}: {stats['Taxa_Acerto']:.1f}% acerto, ROI: {stats['ROI']:.1f}%",
                text_color=color
            )
            type_label.pack(anchor="w", padx=20, pady=2)
    
    def analyze_odds_patterns(self):
        """Analisar padrões de odds"""
        odds_frame = ctk.CTkFrame(self.patterns_content)
        odds_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            odds_frame,
            text="📈 Análise de Odds",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Criar faixas de odds
        self.df_apostas['faixa_odd'] = pd.cut(
            self.df_apostas['odd_numerica'],
            bins=[0, 1.5, 2.0, 3.0, 5.0, float('inf')],
            labels=['Muito Baixa (<1.5)', 'Baixa (1.5-2.0)', 'Média (2.0-3.0)', 'Alta (3.0-5.0)', 'Muito Alta (>5.0)']
        )
        
        odds_stats = self.df_apostas.groupby('faixa_odd').agg({
            'resultado': ['count', lambda x: (x == 'Ganha').sum()],
            'lucro_numerico': 'sum'
        }).round(2)
        
        odds_stats.columns = ['Total', 'Ganhas', 'Lucro']
        odds_stats['Taxa_Acerto'] = (odds_stats['Ganhas'] / odds_stats['Total'] * 100).round(1)
        
        for faixa, stats in odds_stats.iterrows():
            color = "#00ff88" if stats['Lucro'] > 0 else "#ff6b6b"
            
            odds_label = ctk.CTkLabel(
                odds_frame,
                text=f"{faixa}: {stats['Taxa_Acerto']:.1f}% acerto, Lucro: €{stats['Lucro']:.2f}",
                text_color=color
            )
            odds_label.pack(anchor="w", padx=20, pady=2)
    
    def analyze_temporal_patterns(self):
        """Analisar padrões temporais"""
        temp_frame = ctk.CTkFrame(self.patterns_content)
        temp_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            temp_frame,
            text="⏰ Padrões Temporais",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Análise por dia da semana
        self.df_apostas['dia_semana'] = self.df_apostas['data'].dt.day_name()
        
        day_stats = self.df_apostas.groupby('dia_semana').agg({
            'resultado': ['count', lambda x: (x == 'Ganha').sum()],
            'lucro_numerico': 'sum'
        }).round(2)
        
        day_stats.columns = ['Total', 'Ganhas', 'Lucro']
        day_stats['Taxa_Acerto'] = (day_stats['Ganhas'] / day_stats['Total'] * 100).round(1)
        
        # Ordenar por dias da semana
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats = day_stats.reindex([day for day in day_order if day in day_stats.index])
        
        best_day = day_stats.loc[day_stats['Taxa_Acerto'].idxmax()]
        worst_day = day_stats.loc[day_stats['Taxa_Acerto'].idxmin()]
        
        ctk.CTkLabel(
            temp_frame,
            text=f"🏆 Melhor dia: {best_day.name} ({best_day['Taxa_Acerto']:.1f}% acerto)",
            text_color="#00ff88"
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(
            temp_frame,
            text=f"❌ Pior dia: {worst_day.name} ({worst_day['Taxa_Acerto']:.1f}% acerto)",
            text_color="#ff6b6b"
        ).pack(anchor="w", padx=20, pady=2)
    
    def analyze_sequences(self):
        """Analisar sequências de vitórias/derrotas"""
        seq_frame = ctk.CTkFrame(self.patterns_content)
        seq_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            seq_frame,
            text="🔄 Análise de Sequências",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Calcular sequências
        results = self.df_apostas.sort_values('data')['resultado'].tolist()
        
        win_sequences = []
        loss_sequences = []
        current_win_seq = 0
        current_loss_seq = 0
        
        for result in results:
            if result == 'Ganha':
                current_win_seq += 1
                if current_loss_seq > 0:
                    loss_sequences.append(current_loss_seq)
                    current_loss_seq = 0
            elif result == 'Perdida':
                current_loss_seq += 1
                if current_win_seq > 0:
                    win_sequences.append(current_win_seq)
                    current_win_seq = 0
        
        # Adicionar sequência atual
        if current_win_seq > 0:
            win_sequences.append(current_win_seq)
        if current_loss_seq > 0:
            loss_sequences.append(current_loss_seq)
        
        if win_sequences:
            max_win_seq = max(win_sequences)
            avg_win_seq = np.mean(win_sequences)
            
            ctk.CTkLabel(
                seq_frame,
                text=f"🏆 Maior sequência de vitórias: {max_win_seq} (média: {avg_win_seq:.1f})",
                text_color="#00ff88"
            ).pack(anchor="w", padx=20, pady=2)
        
        if loss_sequences:
            max_loss_seq = max(loss_sequences)
            avg_loss_seq = np.mean(loss_sequences)
            
            ctk.CTkLabel(
                seq_frame,
                text=f"❌ Maior sequência de derrotas: {max_loss_seq} (média: {avg_loss_seq:.1f})",
                text_color="#ff6b6b"
            ).pack(anchor="w", padx=20, pady=2)
    
    # Função train_model removida conforme solicitado
    
    # Função make_prediction removida conforme solicitado
    
    def export_pdf(self):
        """Exportar relatório em PDF"""
        if not PDF_AVAILABLE:
            messagebox.showerror("Erro", "Módulo reportlab não disponível")
            return
        
        try:
            # Selecionar arquivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Salvar Relatório PDF"
            )
            
            if not filename:
                return
            
            # Criar PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            story.append(Paragraph("📊 Relatório de Apostas Desportivas", title_style))
            story.append(Spacer(1, 20))
            
            # Período
            period = self.period_combo.get()
            story.append(Paragraph(f"Período: {period}", styles['Normal']))
            story.append(Paragraph(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Estatísticas gerais
            if not self.df_apostas.empty:
                total_apostas = len(self.df_apostas)
                apostas_ganhas = len(self.df_apostas[self.df_apostas['resultado'] == 'Ganha'])
                taxa_acerto = (apostas_ganhas / total_apostas * 100) if total_apostas > 0 else 0
                lucro_total = self.df_apostas['lucro_numerico'].sum()
                valor_total = self.df_apostas['valor_numerico'].sum()
                roi = (lucro_total / valor_total * 100) if valor_total > 0 else 0
                
                stats_data = [
                    ['Métrica', 'Valor'],
                    ['Total de Apostas', str(total_apostas)],
                    ['Apostas Ganhas', str(apostas_ganhas)],
                    ['Taxa de Acerto', f"{taxa_acerto:.1f}%"],
                    ['Lucro Total', f"€{lucro_total:.2f}"],
                    ['Valor Total Apostado', f"€{valor_total:.2f}"],
                    ['ROI', f"{roi:.1f}%"]
                ]
                
                stats_table = Table(stats_data)
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(Paragraph("📈 Estatísticas Gerais", styles['Heading2']))
                story.append(stats_table)
                story.append(Spacer(1, 20))
            
            # Construir PDF
            doc.build(story)
            
            messagebox.showinfo("Sucesso", f"Relatório PDF exportado com sucesso!\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")
    
    def export_excel(self):
        """Exportar dados para Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Salvar Dados Excel"
            )
            
            if not filename:
                return
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Apostas
                if not self.df_apostas.empty:
                    self.df_apostas.to_excel(writer, sheet_name='Apostas', index=False)
                
                # Estatísticas por competição
                if not self.df_apostas.empty:
                    comp_stats = self.df_apostas.groupby('competicao').agg({
                        'resultado': ['count', lambda x: (x == 'Ganha').sum()],
                        'lucro_numerico': 'sum',
                        'valor_numerico': 'sum'
                    }).round(2)
                    
                    comp_stats.columns = ['Total', 'Ganhas', 'Lucro', 'Apostado']
                    comp_stats['Taxa_Acerto'] = (comp_stats['Ganhas'] / comp_stats['Total'] * 100).round(1)
                    comp_stats['ROI'] = (comp_stats['Lucro'] / comp_stats['Apostado'] * 100).round(1)
                    
                    comp_stats.to_excel(writer, sheet_name='Por_Competicao')
                
                # Histórico de banca
                conn = sqlite3.connect(self.db.db_path)
                df_banca = pd.read_sql_query("SELECT * FROM historico_banca ORDER BY created_at", conn)
                conn.close()
                
                if not df_banca.empty:
                    df_banca.to_excel(writer, sheet_name='Historico_Banca', index=False)
            
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso!\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar Excel: {str(e)}")
    
    def create_backup(self):
        """Criar backup completo"""
        try:
            # Criar pasta de backup
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_completo_{timestamp}.db"
            
            # Copiar base de dados
            import shutil
            shutil.copy2(self.db.db_path, backup_file)
            
            messagebox.showinfo("Sucesso", f"Backup criado com sucesso!\n{backup_file}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar backup: {str(e)}")
    
    def generate_suggestions(self):
        """Gerar sugestões baseadas nos dados"""
        self.suggestions_text.delete("1.0", "end")
        
        if self.df_apostas is None or self.df_apostas.empty:
            self.suggestions_text.insert("end", "❌ Sem dados suficientes para gerar sugestões.")
            return
        
        try:
            suggestions = []
            
            # Análise de performance geral
            total_apostas = len(self.df_apostas)
            apostas_ganhas = len(self.df_apostas[self.df_apostas['resultado'] == 'Ganha'])
            taxa_acerto = (apostas_ganhas / total_apostas * 100) if total_apostas > 0 else 0
            
            suggestions.append("🔮 SUGESTÕES PERSONALIZADAS\n" + "="*50)
            
            # Sugestões baseadas na taxa de acerto
            if taxa_acerto < 40:
                suggestions.append("\n⚠️ ALERTA: Taxa de acerto baixa ({:.1f}%)".format(taxa_acerto))
                suggestions.append("💡 Sugestões:")
                suggestions.append("   • Reduza o valor das apostas temporariamente")
                suggestions.append("   • Foque em odds mais baixas (1.5-2.5)")
                suggestions.append("   • Analise melhor os jogos antes de apostar")
            elif taxa_acerto > 60:
                suggestions.append("\n🏆 EXCELENTE: Taxa de acerto alta ({:.1f}%)".format(taxa_acerto))
                suggestions.append("💡 Sugestões:")
                suggestions.append("   • Considere aumentar gradualmente o valor das apostas")
                suggestions.append("   • Mantenha a estratégia atual")
                suggestions.append("   • Explore apostas com odds ligeiramente mais altas")
            
            # Análise de competições
            if not self.df_apostas.empty:
                comp_stats = self.df_apostas.groupby('competicao').agg({
                    'resultado': ['count', lambda x: (x == 'Ganha').sum()],
                    'lucro_numerico': 'sum'
                }).round(2)
                
                comp_stats.columns = ['Total', 'Ganhas', 'Lucro']
                comp_stats['Taxa_Acerto'] = (comp_stats['Ganhas'] / comp_stats['Total'] * 100).round(1)
                
                # Melhores competições
                best_comps = comp_stats[comp_stats['Total'] >= 3].nlargest(3, 'Taxa_Acerto')
                if not best_comps.empty:
                    suggestions.append("\n🏆 COMPETIÇÕES RECOMENDADAS:")
                    for comp, stats in best_comps.iterrows():
                        suggestions.append(f"   • {comp}: {stats['Taxa_Acerto']:.1f}% acerto")
                
                # Piores competições
                worst_comps = comp_stats[comp_stats['Total'] >= 3].nsmallest(2, 'Taxa_Acerto')
                if not worst_comps.empty:
                    suggestions.append("\n⚠️ COMPETIÇÕES A EVITAR:")
                    for comp, stats in worst_comps.iterrows():
                        suggestions.append(f"   • {comp}: {stats['Taxa_Acerto']:.1f}% acerto")
            
            # Análise de gestão de banca
            saldo_atual = self.db.get_saldo_atual()
            saldo_inicial_str = self.db.get_configuracao("saldo_inicial")
            saldo_inicial = float(saldo_inicial_str) if saldo_inicial_str else 0.0
            
            if saldo_inicial > 0:
                variacao_percent = ((saldo_atual - saldo_inicial) / saldo_inicial * 100)
                
                suggestions.append("\n💰 GESTÃO DE BANCA:")
                if variacao_percent < -20:
                    suggestions.append("   ⚠️ ALERTA: Perda significativa da banca ({:.1f}%)".format(variacao_percent))
                    suggestions.append("   💡 Reduza drasticamente o valor das apostas")
                    suggestions.append("   💡 Considere uma pausa para reavaliar a estratégia")
                elif variacao_percent > 20:
                    suggestions.append("   🏆 EXCELENTE: Crescimento da banca ({:.1f}%)".format(variacao_percent))
                    suggestions.append("   💡 Mantenha a disciplina atual")
                    suggestions.append("   💡 Considere retirar parte dos lucros")
            
            # Análise de odds
            if 'odd_numerica' in self.df_apostas.columns:
                odds_stats = self.df_apostas.groupby(
                    pd.cut(self.df_apostas['odd_numerica'], 
                          bins=[0, 1.8, 2.5, 4.0, float('inf')],
                          labels=['Baixa', 'Média', 'Alta', 'Muito Alta'])
                ).agg({
                    'resultado': ['count', lambda x: (x == 'Ganha').sum()]
                }).round(2)
                
                odds_stats.columns = ['Total', 'Ganhas']
                odds_stats['Taxa_Acerto'] = (odds_stats['Ganhas'] / odds_stats['Total'] * 100).round(1)
                
                best_odds_range = odds_stats.loc[odds_stats['Taxa_Acerto'].idxmax()]
                
                suggestions.append("\n📈 ANÁLISE DE ODDS:")
                suggestions.append(f"   🎯 Melhor faixa: {best_odds_range.name} ({best_odds_range['Taxa_Acerto']:.1f}% acerto)")
                suggestions.append(f"   💡 Foque mais em apostas nesta faixa de odds")
            
            # Sugestões gerais
            suggestions.append("\n💡 DICAS GERAIS:")
            suggestions.append("   • Nunca aposte mais de 5% da banca numa única aposta")
            suggestions.append("   • Mantenha registos detalhados de todas as apostas")
            suggestions.append("   • Analise os padrões regularmente")
            suggestions.append("   • Defina limites de perda diários/semanais")
            suggestions.append("   • Aposte apenas quando tiver convicção")
            
            # Mostrar sugestões
            self.suggestions_text.insert("end", "\n".join(suggestions))
            
        except Exception as e:
            self.suggestions_text.insert("end", f"❌ Erro ao gerar sugestões: {str(e)}")