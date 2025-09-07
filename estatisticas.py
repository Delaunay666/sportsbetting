#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Estatísticas e Análises
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from main import DatabaseManager, Aposta
from collections import defaultdict

class EstatisticasFrame(ctk.CTkScrollableFrame):
    """Frame para exibir estatísticas e análises"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.apostas = []
        
        # Inicializar dicionário de labels
        self.stat_labels = {}
        
        # Configurar matplotlib para tema escuro
        plt.style.use('dark_background')
        sns.set_theme(style="darkgrid")
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Criar widgets das estatísticas"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="📈 Estatísticas e Análises",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame de controles
        self.create_controls_frame()
        
        # Frame de estatísticas gerais
        self.create_general_stats_frame()
        
        # Frame de gráficos
        self.create_charts_frame()
        
        # Frame de análises avançadas
        self.create_advanced_analysis_frame()
    
    def create_controls_frame(self):
        """Criar frame de controles"""
        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Período de análise
        ctk.CTkLabel(
            controls_frame,
            text="📅 Período de Análise:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.periodo_combo = ctk.CTkComboBox(
            controls_frame,
            values=["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano", "Todos os tempos"],
            command=self.update_analysis
        )
        self.periodo_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.periodo_combo.set("Todos os tempos")
        
        # Botão de atualização
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Atualizar",
            command=self.load_data,
            width=100
        )
        refresh_btn.grid(row=0, column=2, padx=10, pady=10)
        
        controls_frame.grid_columnconfigure(1, weight=1)
    
    def create_general_stats_frame(self):
        """Criar frame de estatísticas gerais"""
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Estatísticas Gerais",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Grid de estatísticas
        stats_grid = ctk.CTkFrame(stats_frame)
        stats_grid.pack(fill="x", padx=20, pady=10)
        
        # Configurar grid
        for i in range(4):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # Estatísticas básicas
        self.create_stat_card(stats_grid, "💰 Total Apostado", "€0.00", 0, 0, "total_apostado")
        self.create_stat_card(stats_grid, "📈 Lucro Total", "€0.00", 0, 1, "lucro_total")
        self.create_stat_card(stats_grid, "🎯 Taxa de Acerto", "0%", 0, 2, "taxa_acerto")
        self.create_stat_card(stats_grid, "📊 ROI", "0%", 0, 3, "roi")
        
        self.create_stat_card(stats_grid, "🏆 Apostas Ganhas", "0", 1, 0, "apostas_ganhas")
        self.create_stat_card(stats_grid, "❌ Apostas Perdidas", "0", 1, 1, "apostas_perdidas")
        self.create_stat_card(stats_grid, "⏳ Apostas Pendentes", "0", 1, 2, "apostas_pendentes")
        self.create_stat_card(stats_grid, "🔄 Apostas Anuladas", "0", 1, 3, "apostas_anuladas")
        
        # Estatísticas avançadas
        advanced_frame = ctk.CTkFrame(stats_frame)
        advanced_frame.pack(fill="x", padx=20, pady=10)
        
        for i in range(3):
            advanced_frame.grid_columnconfigure(i, weight=1)
        
        self.create_stat_card(advanced_frame, "📏 Odd Média", "0.00", 0, 0, "odd_media")
        self.create_stat_card(advanced_frame, "💵 Aposta Média", "€0.00", 0, 1, "aposta_media")
        self.create_stat_card(advanced_frame, "🎲 Maior Odd Ganha", "0.00", 0, 2, "maior_odd")
    
    def create_stat_card(self, parent, title, value, row, col, key):
        """Criar card de estatística"""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff88"
        )
        value_label.pack(pady=(0, 10))
        
        self.stat_labels[key] = value_label
    
    def create_charts_frame(self):
        """Criar frame de gráficos"""
        charts_frame = ctk.CTkFrame(self)
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            charts_frame,
            text="📊 Gráficos e Análises Visuais",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Notebook para diferentes gráficos
        self.charts_notebook = ttk.Notebook(charts_frame)
        self.charts_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Criar abas dos gráficos
        self.create_evolution_chart()
        self.create_distribution_chart()
        self.create_performance_chart()
        self.create_competition_chart()
    
    def create_evolution_chart(self):
        """Criar gráfico de evolução da banca"""
        frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(frame, text="📈 Evolução da Banca")
        
        self.evolution_fig = Figure(figsize=(10, 6), facecolor='#2b2b2b')
        self.evolution_canvas = FigureCanvasTkAgg(self.evolution_fig, frame)
        self.evolution_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_distribution_chart(self):
        """Criar gráfico de distribuição de resultados"""
        frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(frame, text="🎯 Distribuição de Resultados")
        
        self.distribution_fig = Figure(figsize=(10, 6), facecolor='#2b2b2b')
        self.distribution_canvas = FigureCanvasTkAgg(self.distribution_fig, frame)
        self.distribution_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_performance_chart(self):
        """Criar gráfico de performance por mês"""
        frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(frame, text="📅 Performance Mensal")
        
        self.performance_fig = Figure(figsize=(10, 6), facecolor='#2b2b2b')
        self.performance_canvas = FigureCanvasTkAgg(self.performance_fig, frame)
        self.performance_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_competition_chart(self):
        """Criar gráfico de performance por competição"""
        frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(frame, text="🏆 Por Competição")
        
        self.competition_fig = Figure(figsize=(10, 6), facecolor='#2b2b2b')
        self.competition_canvas = FigureCanvasTkAgg(self.competition_fig, frame)
        self.competition_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_advanced_analysis_frame(self):
        """Criar frame de análises avançadas"""
        analysis_frame = ctk.CTkFrame(self)
        analysis_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            analysis_frame,
            text="🧠 Análises Avançadas",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Análise de padrões
        patterns_frame = ctk.CTkFrame(analysis_frame)
        patterns_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            patterns_frame,
            text="🔍 Padrões Identificados",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.patterns_text = ctk.CTkTextbox(patterns_frame, height=150)
        self.patterns_text.pack(fill="x", padx=10, pady=10)
        
        # Recomendações
        recommendations_frame = ctk.CTkFrame(analysis_frame)
        recommendations_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            recommendations_frame,
            text="💡 Recomendações",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.recommendations_text = ctk.CTkTextbox(recommendations_frame, height=150)
        self.recommendations_text.pack(fill="x", padx=10, pady=10)
    
    def load_data(self):
        """Carregar dados e atualizar análises"""
        try:
            self.apostas = self.db.get_apostas()
            self.update_analysis()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def update_analysis(self, *args):
        """Atualizar todas as análises"""
        if not self.apostas:
            return
        
        # Filtrar apostas por período
        apostas_filtradas = self.filter_by_period()
        
        # Atualizar estatísticas gerais
        self.update_general_stats(apostas_filtradas)
        
        # Atualizar gráficos
        self.update_evolution_chart(apostas_filtradas)
        self.update_distribution_chart(apostas_filtradas)
        self.update_performance_chart(apostas_filtradas)
        self.update_competition_chart(apostas_filtradas)
        
        # Atualizar análises avançadas
        self.update_advanced_analysis(apostas_filtradas)
    
    def filter_by_period(self):
        """Filtrar apostas por período selecionado"""
        periodo = self.periodo_combo.get()
        
        if periodo == "Todos os tempos":
            return self.apostas
        
        # Calcular data limite
        hoje = datetime.now()
        if periodo == "Último mês":
            data_limite = hoje - timedelta(days=30)
        elif periodo == "Últimos 3 meses":
            data_limite = hoje - timedelta(days=90)
        elif periodo == "Últimos 6 meses":
            data_limite = hoje - timedelta(days=180)
        elif periodo == "Último ano":
            data_limite = hoje - timedelta(days=365)
        else:
            return self.apostas
        
        # Filtrar apostas
        apostas_filtradas = []
        for aposta in self.apostas:
            try:
                data_aposta = datetime.strptime(aposta.data_hora, "%d/%m/%Y %H:%M")
                if data_aposta >= data_limite:
                    apostas_filtradas.append(aposta)
            except:
                continue
        
        return apostas_filtradas
    
    def update_general_stats(self, apostas):
        """Atualizar estatísticas gerais"""
        if not apostas:
            return
        
        # Calcular estatísticas
        total_apostado = sum(a.valor_apostado for a in apostas)
        lucro_total = sum(a.lucro_prejuizo for a in apostas if a.resultado in ["Ganha", "Perdida"])
        
        apostas_ganhas = len([a for a in apostas if a.resultado == "Ganha"])
        apostas_perdidas = len([a for a in apostas if a.resultado == "Perdida"])
        apostas_pendentes = len([a for a in apostas if a.resultado == "Pendente"])
        apostas_anuladas = len([a for a in apostas if a.resultado == "Anulada"])
        
        apostas_finalizadas = apostas_ganhas + apostas_perdidas
        taxa_acerto = (apostas_ganhas / apostas_finalizadas * 100) if apostas_finalizadas > 0 else 0
        roi = (lucro_total / total_apostado * 100) if total_apostado > 0 else 0
        
        odd_media = sum(a.odd for a in apostas) / len(apostas) if apostas else 0
        aposta_media = total_apostado / len(apostas) if apostas else 0
        
        apostas_ganhas_obj = [a for a in apostas if a.resultado == "Ganha"]
        maior_odd = max(a.odd for a in apostas_ganhas_obj) if apostas_ganhas_obj else 0
        
        # Atualizar labels
        self.stat_labels["total_apostado"].configure(text=f"€{total_apostado:.2f}")
        self.stat_labels["lucro_total"].configure(
            text=f"€{lucro_total:.2f}",
            text_color="#00ff88" if lucro_total >= 0 else "#ff4444"
        )
        self.stat_labels["taxa_acerto"].configure(text=f"{taxa_acerto:.1f}%")
        self.stat_labels["roi"].configure(
            text=f"{roi:.1f}%",
            text_color="#00ff88" if roi >= 0 else "#ff4444"
        )
        
        self.stat_labels["apostas_ganhas"].configure(text=str(apostas_ganhas))
        self.stat_labels["apostas_perdidas"].configure(text=str(apostas_perdidas))
        self.stat_labels["apostas_pendentes"].configure(text=str(apostas_pendentes))
        self.stat_labels["apostas_anuladas"].configure(text=str(apostas_anuladas))
        
        self.stat_labels["odd_media"].configure(text=f"{odd_media:.2f}")
        self.stat_labels["aposta_media"].configure(text=f"€{aposta_media:.2f}")
        self.stat_labels["maior_odd"].configure(text=f"{maior_odd:.2f}")
    
    def update_evolution_chart(self, apostas):
        """Atualizar gráfico de evolução da banca"""
        self.evolution_fig.clear()
        ax = self.evolution_fig.add_subplot(111)
        
        if not apostas:
            ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', transform=ax.transAxes, color='white', fontsize=14)
            self.evolution_canvas.draw()
            return
        
        # Ordenar apostas por data
        apostas_ordenadas = sorted(apostas, key=lambda x: x.data_hora)
        
        # Calcular evolução da banca
        saldo_inicial = self.db.get_configuracao("saldo_inicial")
        saldo_inicial = float(saldo_inicial) if saldo_inicial else 0.0
        
        datas = []
        saldos = [saldo_inicial]
        saldo_atual = saldo_inicial
        
        for aposta in apostas_ordenadas:
            if aposta.resultado in ["Ganha", "Perdida", "Anulada"]:
                try:
                    data = datetime.strptime(aposta.data_hora, "%d/%m/%Y %H:%M")
                    datas.append(data)
                    
                    if aposta.resultado == "Ganha":
                        saldo_atual += aposta.lucro_prejuizo
                    elif aposta.resultado == "Perdida":
                        saldo_atual += aposta.lucro_prejuizo  # já é negativo
                    # Anulada não altera saldo
                    
                    saldos.append(saldo_atual)
                except:
                    continue
        
        if datas:
            ax.plot(datas, saldos[1:], linewidth=2, color='#00ff88', marker='o', markersize=4)
            ax.axhline(y=saldo_inicial, color='#ffc107', linestyle='--', alpha=0.7, label='Saldo Inicial')
            
            ax.set_title('Evolução da Banca', fontsize=14, fontweight='bold', color='white')
            ax.set_xlabel('Data', color='white')
            ax.set_ylabel('Saldo (€)', color='white')
            ax.grid(True, alpha=0.3, color='white')
            
            # Configurar cores dos ticks e labels
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            
            # Configurar legenda com cores claras
            legend = ax.legend()
            legend.get_frame().set_facecolor('#2b2b2b')
            for text in legend.get_texts():
                text.set_color('white')
            
            # Formatar eixo x
            self.evolution_fig.autofmt_xdate()
        
        self.evolution_canvas.draw()
    
    def update_distribution_chart(self, apostas):
        """Atualizar gráfico de distribuição de resultados"""
        self.distribution_fig.clear()
        ax = self.distribution_fig.add_subplot(111)
        
        if not apostas:
            ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', transform=ax.transAxes, color='white', fontsize=14)
            self.distribution_canvas.draw()
            return
        
        # Contar resultados
        resultados = defaultdict(int)
        for aposta in apostas:
            resultados[aposta.resultado] += 1
        
        if resultados:
            labels = list(resultados.keys())
            sizes = list(resultados.values())
            colors = {'Ganha': '#00ff88', 'Perdida': '#ff4444', 'Pendente': '#ffc107', 'Anulada': '#6c757d'}
            chart_colors = [colors.get(label, '#888888') for label in labels]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=chart_colors, autopct='%1.1f%%', startangle=90)
            
            # Configurar texto
            for text in texts:
                text.set_color('white')
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Distribuição de Resultados', fontsize=14, fontweight='bold', color='white')
        
        self.distribution_canvas.draw()
    
    def update_performance_chart(self, apostas):
        """Atualizar gráfico de performance mensal"""
        self.performance_fig.clear()
        ax = self.performance_fig.add_subplot(111)
        
        if not apostas:
            ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', transform=ax.transAxes, color='white', fontsize=14)
            self.performance_canvas.draw()
            return
        
        # Agrupar por mês
        performance_mensal = defaultdict(lambda: {'lucro': 0, 'apostas': 0})
        
        for aposta in apostas:
            if aposta.resultado in ["Ganha", "Perdida"]:
                try:
                    data = datetime.strptime(aposta.data_hora, "%d/%m/%Y %H:%M")
                    mes_ano = data.strftime("%Y-%m")
                    performance_mensal[mes_ano]['lucro'] += aposta.lucro_prejuizo
                    performance_mensal[mes_ano]['apostas'] += 1
                except:
                    continue
        
        if performance_mensal:
            meses = sorted(performance_mensal.keys())
            lucros = [performance_mensal[mes]['lucro'] for mes in meses]
            
            colors = ['#00ff88' if lucro >= 0 else '#ff4444' for lucro in lucros]
            bars = ax.bar(meses, lucros, color=colors, alpha=0.8)
            
            ax.set_title('Performance Mensal', fontsize=14, fontweight='bold', color='white')
            ax.set_xlabel('Mês', color='white')
            ax.set_ylabel('Lucro/Prejuízo (€)', color='white')
            ax.grid(True, alpha=0.3, color='white')
            ax.axhline(y=0, color='white', linestyle='-', alpha=0.5)
            
            # Configurar cores dos ticks e labels
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            
            # Rotacionar labels do eixo x
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.performance_canvas.draw()
    
    def update_competition_chart(self, apostas):
        """Atualizar gráfico de performance por competição"""
        self.competition_fig.clear()
        ax = self.competition_fig.add_subplot(111)
        
        if not apostas:
            ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', transform=ax.transAxes, color='white', fontsize=14)
            self.competition_canvas.draw()
            return
        
        # Agrupar por competição
        performance_comp = defaultdict(lambda: {'lucro': 0, 'apostas': 0, 'ganhas': 0})
        
        for aposta in apostas:
            comp = aposta.competicao
            performance_comp[comp]['apostas'] += 1
            if aposta.resultado == "Ganha":
                performance_comp[comp]['ganhas'] += 1
                performance_comp[comp]['lucro'] += aposta.lucro_prejuizo
            elif aposta.resultado == "Perdida":
                performance_comp[comp]['lucro'] += aposta.lucro_prejuizo
        
        if performance_comp:
            competicoes = list(performance_comp.keys())
            lucros = [performance_comp[comp]['lucro'] for comp in competicoes]
            
            colors = ['#00ff88' if lucro >= 0 else '#ff4444' for lucro in lucros]
            bars = ax.barh(competicoes, lucros, color=colors, alpha=0.8)
            
            ax.set_title('Performance por Competição', fontsize=14, fontweight='bold', color='white')
            ax.set_xlabel('Lucro/Prejuízo (€)', color='white')
            ax.set_ylabel('Competição', color='white')
            ax.grid(True, alpha=0.3, color='white')
            ax.axvline(x=0, color='white', linestyle='-', alpha=0.5)
            
            # Configurar cores dos ticks e labels
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
        
        self.competition_canvas.draw()
    
    def update_advanced_analysis(self, apostas):
        """Atualizar análises avançadas"""
        if not apostas:
            return
        
        # Análise de padrões
        patterns = self.analyze_patterns(apostas)
        self.patterns_text.delete("1.0", "end")
        self.patterns_text.insert("1.0", patterns)
        
        # Recomendações
        recommendations = self.generate_recommendations(apostas)
        self.recommendations_text.delete("1.0", "end")
        self.recommendations_text.insert("1.0", recommendations)
    
    def analyze_patterns(self, apostas):
        """Analisar padrões nas apostas"""
        patterns = []
        
        # Análise por tipo de aposta
        tipos_performance = defaultdict(lambda: {'total': 0, 'ganhas': 0, 'lucro': 0})
        for aposta in apostas:
            tipo = aposta.tipo_aposta
            tipos_performance[tipo]['total'] += 1
            if aposta.resultado == "Ganha":
                tipos_performance[tipo]['ganhas'] += 1
                tipos_performance[tipo]['lucro'] += aposta.lucro_prejuizo
            elif aposta.resultado == "Perdida":
                tipos_performance[tipo]['lucro'] += aposta.lucro_prejuizo
        
        patterns.append("🎯 ANÁLISE POR TIPO DE APOSTA:")
        for tipo, stats in tipos_performance.items():
            if stats['total'] > 0:
                taxa = (stats['ganhas'] / stats['total']) * 100
                patterns.append(f"• {tipo}: {taxa:.1f}% de acerto ({stats['ganhas']}/{stats['total']}) - Lucro: €{stats['lucro']:.2f}")
        
        patterns.append("\n📊 ANÁLISE DE ODDS:")
        odds_ranges = {'Baixas (1.0-1.5)': [], 'Médias (1.5-2.5)': [], 'Altas (2.5-5.0)': [], 'Muito Altas (>5.0)': []}
        
        for aposta in apostas:
            if aposta.odd <= 1.5:
                odds_ranges['Baixas (1.0-1.5)'].append(aposta)
            elif aposta.odd <= 2.5:
                odds_ranges['Médias (1.5-2.5)'].append(aposta)
            elif aposta.odd <= 5.0:
                odds_ranges['Altas (2.5-5.0)'].append(aposta)
            else:
                odds_ranges['Muito Altas (>5.0)'].append(aposta)
        
        for range_name, apostas_range in odds_ranges.items():
            if apostas_range:
                ganhas = len([a for a in apostas_range if a.resultado == "Ganha"])
                total = len([a for a in apostas_range if a.resultado in ["Ganha", "Perdida"]])
                if total > 0:
                    taxa = (ganhas / total) * 100
                    patterns.append(f"• {range_name}: {taxa:.1f}% de acerto ({ganhas}/{total})")
        
        return "\n".join(patterns)
    
    def generate_recommendations(self, apostas):
        """Gerar recomendações baseadas na análise"""
        recommendations = []
        
        if not apostas:
            return "Sem dados suficientes para gerar recomendações."
        
        # Análise geral
        apostas_finalizadas = [a for a in apostas if a.resultado in ["Ganha", "Perdida"]]
        if apostas_finalizadas:
            ganhas = len([a for a in apostas_finalizadas if a.resultado == "Ganha"])
            taxa_acerto = (ganhas / len(apostas_finalizadas)) * 100
            
            recommendations.append("💡 RECOMENDAÇÕES GERAIS:")
            
            if taxa_acerto < 40:
                recommendations.append("• ⚠️ Taxa de acerto baixa. Considere ser mais seletivo nas apostas.")
            elif taxa_acerto > 60:
                recommendations.append("• ✅ Excelente taxa de acerto! Continue com a estratégia atual.")
            else:
                recommendations.append("• 📊 Taxa de acerto razoável. Foque em melhorar a gestão de banca.")
            
            # Análise de lucro
            lucro_total = sum(a.lucro_prejuizo for a in apostas_finalizadas)
            if lucro_total < 0:
                recommendations.append("• 💰 Resultado negativo. Revise sua estratégia e reduza o valor das apostas.")
            
            # Análise de odds
            odd_media = sum(a.odd for a in apostas) / len(apostas)
            if odd_media > 3.0:
                recommendations.append("• 🎲 Odds muito altas em média. Considere apostas mais conservadoras.")
            elif odd_media < 1.5:
                recommendations.append("• 🔒 Odds muito baixas. Pode não compensar o risco.")
        
        recommendations.append("\n🎯 DICAS ESPECÍFICAS:")
        recommendations.append("• 📈 Mantenha um registo detalhado de todas as apostas")
        recommendations.append("• 💵 Nunca aposte mais de 5% da sua banca numa única aposta")
        recommendations.append("• 🧠 Analise as estatísticas regularmente para identificar padrões")
        recommendations.append("• ⏰ Evite apostas impulsivas - sempre analise antes de apostar")
        recommendations.append("• 📊 Diversifique entre diferentes competições e tipos de aposta")
        
        return "\n".join(recommendations)