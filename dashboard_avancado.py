#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Avançado para Análise de Apostas Desportivas
Interface moderna com métricas em tempo real, gráficos interativos e análises avançadas
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from main import DatabaseManager
from analise_risco import RiskAnalyzer
from validacao import DataValidator
from traducoes import t
import warnings
warnings.filterwarnings('ignore')

# Configurar tema do seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")

class DashboardAvancado(ctk.CTkFrame):
    """Dashboard avançado com análises em tempo real"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.risk_analyzer = RiskAnalyzer(db)
        self.validator = DataValidator(db)
        
        # Configurações de estilo
        self.configure_style()
        
        # Variáveis de controle
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = 30000  # 30 segundos
        self.last_update = None
        
        # Dados em cache
        self.cached_data = {}
        self.cache_timestamp = None
        
        self.setup_ui()
        self.load_initial_data()
        self.start_auto_refresh()
    
    def configure_style(self):
        """Configurar estilos personalizados"""
        # Cores do tema
        self.colors = {
            'primary': '#1f538d',
            'secondary': '#14375e',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'surface': '#f5f5f5'
        }
        
        # Configurar matplotlib
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        })
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        # Frame principal com scroll
        self.main_canvas = tk.Canvas(self, bg='white')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout principal
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Cabeçalho
        self.create_header()
        
        # Seções do dashboard
        self.create_metrics_overview()
        self.create_performance_charts()
        self.create_risk_analysis()
        self.create_kelly_analysis()
        self.create_trend_analysis()
        self.create_alerts_section()
        
        # Rodapé com controles
        self.create_footer()
    
    def create_header(self):
        """Criar cabeçalho do dashboard"""
        header_frame = ctk.CTkFrame(self.scrollable_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 " + t("dashboard_avancado_apostas"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Status e controles
        controls_frame = ctk.CTkFrame(header_frame)
        controls_frame.pack(side="right", padx=20, pady=10)
        
        # Status da última atualização
        self.status_label = ctk.CTkLabel(
            controls_frame,
            text=t("ultima_atualizacao") + ": --",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="top", padx=10, pady=2)
        
        # Controles
        controls_inner = ctk.CTkFrame(controls_frame)
        controls_inner.pack(side="bottom", padx=10, pady=5)
        
        # Auto-refresh toggle
        auto_refresh_cb = ctk.CTkCheckBox(
            controls_inner,
            text=t("auto_refresh"),
            variable=self.auto_refresh,
            command=self.toggle_auto_refresh
        )
        auto_refresh_cb.pack(side="left", padx=5)
        
        # Botão de refresh manual
        refresh_btn = ctk.CTkButton(
            controls_inner,
            text="🔄 " + t("atualizar"),
            command=self.manual_refresh,
            width=100
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Botão de exportar
        export_btn = ctk.CTkButton(
            controls_inner,
            text="📤 " + t("exportar"),
            command=self.export_dashboard,
            width=100
        )
        export_btn.pack(side="left", padx=5)
    
    def create_metrics_overview(self):
        """Criar visão geral das métricas principais"""
        metrics_frame = ctk.CTkFrame(self.scrollable_frame)
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(
            metrics_frame,
            text="📈 " + t("metricas_principais"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Grid de métricas
        self.metrics_grid = ctk.CTkFrame(metrics_frame)
        self.metrics_grid.pack(fill="x", padx=20, pady=10)
        
        # Criar cards de métricas
        self.metric_cards = {}
        metrics_config = [
            ('total_bets', t('total_apostas'), '🎯', 'info'),
            ('win_rate', t('taxa_acerto'), '🏆', 'success'),
            ('avg_return', t('retorno_medio'), '💰', 'primary'),
            ('sharpe_ratio', t('sharpe_ratio'), '📊', 'warning'),
            ('max_drawdown', t('max_drawdown'), '📉', 'danger'),
            ('profit_factor', t('profit_factor'), '⚡', 'success')
        ]
        
        for i, (key, label, icon, color) in enumerate(metrics_config):
            row = i // 3
            col = i % 3
            
            card = self.create_metric_card(
                self.metrics_grid, key, label, icon, color
            )
            card.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            self.metric_cards[key] = card
        
        # Configurar grid weights
        for i in range(3):
            self.metrics_grid.grid_columnconfigure(i, weight=1)
    
    def create_metric_card(self, parent, key: str, label: str, icon: str, color: str):
        """Criar card individual de métrica"""
        card = ctk.CTkFrame(parent)
        
        # Header do card
        header = ctk.CTkFrame(card)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        icon_label = ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=20)
        )
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(side="left", padx=(10, 0))
        
        # Valor principal
        value_label = ctk.CTkLabel(
            card,
            text="--",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.pack(pady=(0, 5))
        
        # Variação
        change_label = ctk.CTkLabel(
            card,
            text="--",
            font=ctk.CTkFont(size=10)
        )
        change_label.pack(pady=(0, 10))
        
        # Armazenar referências
        card.value_label = value_label
        card.change_label = change_label
        card.key = key
        
        return card
    
    def create_performance_charts(self):
        """Criar gráficos de performance"""
        charts_frame = ctk.CTkFrame(self.scrollable_frame)
        charts_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(
            charts_frame,
            text="📊 " + t("analise_performance"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Notebook para diferentes gráficos
        self.charts_notebook = ttk.Notebook(charts_frame)
        self.charts_notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba 1: Evolução do Lucro
        self.profit_tab = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.profit_tab, text=t("evolucao_lucro"))
        self.create_profit_evolution_chart()
        
        # Aba 2: Distribuição de Retornos
        self.returns_tab = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.returns_tab, text=t("distribuicao_retornos"))
        self.create_returns_distribution_chart()
        
        # Aba 3: Performance por Competição
        self.competition_tab = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.competition_tab, text=t("por_competicao"))
        self.create_competition_performance_chart()
        
        # Aba 4: Heatmap de Performance
        self.heatmap_tab = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.heatmap_tab, text=t("heatmap"))
        self.create_performance_heatmap()
    
    def create_profit_evolution_chart(self):
        """Criar gráfico de evolução do lucro"""
        fig = Figure(figsize=(12, 6), dpi=100)
        self.profit_ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, self.profit_tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.profit_canvas = canvas
        self.profit_fig = fig
    
    def create_returns_distribution_chart(self):
        """Criar gráfico de distribuição de retornos"""
        fig = Figure(figsize=(12, 6), dpi=100)
        self.returns_ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, self.returns_tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.returns_canvas = canvas
        self.returns_fig = fig
    
    def create_competition_performance_chart(self):
        """Criar gráfico de performance por competição"""
        fig = Figure(figsize=(12, 6), dpi=100)
        self.competition_ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, self.competition_tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.competition_canvas = canvas
        self.competition_fig = fig
    
    def create_performance_heatmap(self):
        """Criar heatmap de performance"""
        fig = Figure(figsize=(12, 6), dpi=100)
        self.heatmap_ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, self.heatmap_tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.heatmap_canvas = canvas
        self.heatmap_fig = fig
    
    def create_risk_analysis(self):
        """Criar seção de análise de risco"""
        risk_frame = ctk.CTkFrame(self.scrollable_frame)
        risk_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(
            risk_frame,
            text="⚠️ Análise de Risco",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Grid de métricas de risco
        risk_grid = ctk.CTkFrame(risk_frame)
        risk_grid.pack(fill="x", padx=20, pady=10)
        
        # Risk Score
        self.risk_score_frame = ctk.CTkFrame(risk_grid)
        self.risk_score_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        risk_score_title = ctk.CTkLabel(
            self.risk_score_frame,
            text="🎯 Risk Score",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        risk_score_title.pack(pady=5)
        
        self.risk_score_label = ctk.CTkLabel(
            self.risk_score_frame,
            text="--",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.risk_score_label.pack()
        
        self.risk_level_label = ctk.CTkLabel(
            self.risk_score_frame,
            text="--",
            font=ctk.CTkFont(size=12)
        )
        self.risk_level_label.pack(pady=(0, 10))
        
        # VaR e CVaR
        var_frame = ctk.CTkFrame(risk_grid)
        var_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        var_title = ctk.CTkLabel(
            var_frame,
            text="📉 Value at Risk",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        var_title.pack(pady=5)
        
        self.var_95_label = ctk.CTkLabel(
            var_frame,
            text="VaR 95%: --",
            font=ctk.CTkFont(size=12)
        )
        self.var_95_label.pack()
        
        self.cvar_95_label = ctk.CTkLabel(
            var_frame,
            text="CVaR 95%: --",
            font=ctk.CTkFont(size=12)
        )
        self.cvar_95_label.pack(pady=(0, 10))
        
        # Drawdown
        dd_frame = ctk.CTkFrame(risk_grid)
        dd_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        dd_title = ctk.CTkLabel(
            dd_frame,
            text="📊 Drawdown",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dd_title.pack(pady=5)
        
        self.max_dd_label = ctk.CTkLabel(
            dd_frame,
            text="Max DD: --",
            font=ctk.CTkFont(size=12)
        )
        self.max_dd_label.pack()
        
        self.current_dd_label = ctk.CTkLabel(
            dd_frame,
            text="Atual: --",
            font=ctk.CTkFont(size=12)
        )
        self.current_dd_label.pack(pady=(0, 10))
        
        # Configurar grid weights
        for i in range(3):
            risk_grid.grid_columnconfigure(i, weight=1)
    
    def create_kelly_analysis(self):
        """Criar seção de análise Kelly"""
        kelly_frame = ctk.CTkFrame(self.scrollable_frame)
        kelly_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(
            kelly_frame,
            text="🎲 Análise Kelly Criterion",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Kelly geral
        kelly_general_frame = ctk.CTkFrame(kelly_frame)
        kelly_general_frame.pack(fill="x", padx=20, pady=5)
        
        kelly_general_title = ctk.CTkLabel(
            kelly_general_frame,
            text="Kelly Geral",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        kelly_general_title.pack(side="left", padx=10, pady=10)
        
        self.kelly_general_label = ctk.CTkLabel(
            kelly_general_frame,
            text="--",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.kelly_general_label.pack(side="right", padx=10, pady=10)
        
        # Kelly por competição (top 5)
        self.kelly_competition_frame = ctk.CTkFrame(kelly_frame)
        self.kelly_competition_frame.pack(fill="x", padx=20, pady=5)
        
        kelly_comp_title = ctk.CTkLabel(
            self.kelly_competition_frame,
            text="Top 5 Competições (Kelly %)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        kelly_comp_title.pack(pady=5)
    
    def create_trend_analysis(self):
        """Criar seção de análise de tendências"""
        trend_frame = ctk.CTkFrame(self.scrollable_frame)
        trend_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(
            trend_frame,
            text="📈 Análise de Tendências",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Métricas de tendência
        trend_grid = ctk.CTkFrame(trend_frame)
        trend_grid.pack(fill="x", padx=20, pady=10)
        
        # Últimos 7 dias
        week_frame = ctk.CTkFrame(trend_grid)
        week_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        week_title = ctk.CTkLabel(
            week_frame,
            text="📅 Últimos 7 dias",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        week_title.pack(pady=5)
        
        self.week_roi_label = ctk.CTkLabel(
            week_frame,
            text="ROI: --",
            font=ctk.CTkFont(size=11)
        )
        self.week_roi_label.pack()
        
        self.week_bets_label = ctk.CTkLabel(
            week_frame,
            text="Apostas: --",
            font=ctk.CTkFont(size=11)
        )
        self.week_bets_label.pack(pady=(0, 10))
        
        # Últimos 30 dias
        month_frame = ctk.CTkFrame(trend_grid)
        month_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        month_title = ctk.CTkLabel(
            month_frame,
            text="📅 Últimos 30 dias",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        month_title.pack(pady=5)
        
        self.month_roi_label = ctk.CTkLabel(
            month_frame,
            text="ROI: --",
            font=ctk.CTkFont(size=11)
        )
        self.month_roi_label.pack()
        
        self.month_bets_label = ctk.CTkLabel(
            month_frame,
            text="Apostas: --",
            font=ctk.CTkFont(size=11)
        )
        self.month_bets_label.pack(pady=(0, 10))
        
        # Tendência geral
        trend_general_frame = ctk.CTkFrame(trend_grid)
        trend_general_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        trend_general_title = ctk.CTkLabel(
            trend_general_frame,
            text="📊 Tendência",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        trend_general_title.pack(pady=5)
        
        self.trend_direction_label = ctk.CTkLabel(
            trend_general_frame,
            text="--",
            font=ctk.CTkFont(size=11)
        )
        self.trend_direction_label.pack()
        
        self.trend_strength_label = ctk.CTkLabel(
            trend_general_frame,
            text="--",
            font=ctk.CTkFont(size=11)
        )
        self.trend_strength_label.pack(pady=(0, 10))
        
        # Configurar grid weights
        for i in range(3):
            trend_grid.grid_columnconfigure(i, weight=1)
    
    def create_alerts_section(self):
        """Criar seção de alertas e recomendações"""
        alerts_frame = ctk.CTkFrame(self.scrollable_frame)
        alerts_frame.pack(fill="x", padx=10, pady=5)
        
        title = ctk.CTkLabel(
            alerts_frame,
            text="🚨 Alertas e Recomendações",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Lista de alertas
        self.alerts_list_frame = ctk.CTkScrollableFrame(
            alerts_frame,
            height=150
        )
        self.alerts_list_frame.pack(fill="x", padx=20, pady=10)
    
    def create_footer(self):
        """Criar rodapé com informações adicionais"""
        footer_frame = ctk.CTkFrame(self.scrollable_frame)
        footer_frame.pack(fill="x", padx=10, pady=5)
        
        # Informações do sistema
        info_label = ctk.CTkLabel(
            footer_frame,
            text="Dashboard Avançado v1.0 | Dados atualizados em tempo real",
            font=ctk.CTkFont(size=10)
        )
        info_label.pack(pady=10)
    
    def load_initial_data(self):
        """Carregar dados iniciais"""
        self.refresh_data()
    
    def refresh_data(self):
        """Atualizar todos os dados do dashboard"""
        try:
            # Recarregar dados do risk analyzer
            self.risk_analyzer.load_data()
            
            # Atualizar métricas principais
            self.update_main_metrics()
            
            # Atualizar gráficos
            self.update_charts()
            
            # Atualizar análise de risco
            self.update_risk_analysis()
            
            # Atualizar Kelly analysis
            self.update_kelly_analysis()
            
            # Atualizar tendências
            self.update_trend_analysis()
            
            # Atualizar alertas
            self.update_alerts()
            
            # Atualizar timestamp
            self.last_update = datetime.now()
            self.status_label.configure(
                text=f"{t('ultima_atualizacao')}: {self.last_update.strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def update_main_metrics(self):
        """Atualizar métricas principais"""
        metrics = self.risk_analyzer.calculate_basic_metrics()
        
        if not metrics:
            return
        
        # Atualizar cada card de métrica
        metric_formats = {
            'total_bets': lambda x: f"{int(x)}",
            'win_rate': lambda x: f"{x:.1f}%",
            'avg_return': lambda x: f"{x:.2f}%",
            'sharpe_ratio': lambda x: f"{x:.2f}",
            'max_drawdown': lambda x: f"{x:.1f}%",
            'profit_factor': lambda x: f"{x:.2f}"
        }
        
        for key, card in self.metric_cards.items():
            if key in metrics:
                value = metrics[key]
                formatted_value = metric_formats[key](value)
                card.value_label.configure(text=formatted_value)
                
                # Calcular mudança (simulada por enquanto)
                change = np.random.uniform(-5, 5)  # Placeholder
                change_text = f"{'↗️' if change > 0 else '↘️'} {abs(change):.1f}%"
                card.change_label.configure(text=change_text)
    
    def update_charts(self):
        """Atualizar todos os gráficos"""
        if self.risk_analyzer.df_apostas is None or self.risk_analyzer.df_apostas.empty:
            return
        
        df = self.risk_analyzer.df_apostas.copy()
        
        # Gráfico de evolução do lucro
        self.profit_ax.clear()
        df['cumulative_profit'] = df['lucro_prejuizo'].cumsum()
        self.profit_ax.plot(df.index, df['cumulative_profit'], linewidth=2, color='#1f538d')
        self.profit_ax.set_title('Evolução do Lucro Acumulado')
        self.profit_ax.set_xlabel('Número da Aposta')
        self.profit_ax.set_ylabel('Lucro Acumulado (€)')
        self.profit_ax.grid(True, alpha=0.3)
        self.profit_fig.tight_layout()
        self.profit_canvas.draw()
        
        # Gráfico de distribuição de retornos
        self.returns_ax.clear()
        returns = df['return'] * 100
        self.returns_ax.hist(returns, bins=30, alpha=0.7, color='#28a745', edgecolor='black')
        self.returns_ax.axvline(returns.mean(), color='red', linestyle='--', label=f'Média: {returns.mean():.2f}%')
        self.returns_ax.set_title('Distribuição de Retornos')
        self.returns_ax.set_xlabel('Retorno (%)')
        self.returns_ax.set_ylabel('Frequência')
        self.returns_ax.legend()
        self.returns_ax.grid(True, alpha=0.3)
        self.returns_fig.tight_layout()
        self.returns_canvas.draw()
        
        # Performance por competição
        self.competition_ax.clear()
        comp_performance = df.groupby('competicao').agg({
            'lucro_prejuizo': 'sum',
            'win': 'mean'
        }).sort_values('lucro_prejuizo', ascending=True)
        
        if len(comp_performance) > 0:
            y_pos = np.arange(len(comp_performance))
            colors = ['red' if x < 0 else 'green' for x in comp_performance['lucro_prejuizo']]
            
            bars = self.competition_ax.barh(y_pos, comp_performance['lucro_prejuizo'], color=colors, alpha=0.7)
            self.competition_ax.set_yticks(y_pos)
            self.competition_ax.set_yticklabels(comp_performance.index, fontsize=8)
            self.competition_ax.set_xlabel('Lucro Total (€)')
            self.competition_ax.set_title('Performance por Competição')
            self.competition_ax.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for i, (bar, value) in enumerate(zip(bars, comp_performance['lucro_prejuizo'])):
                self.competition_ax.text(
                    value + (0.01 * max(abs(comp_performance['lucro_prejuizo']))),
                    bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}€',
                    va='center',
                    fontsize=8
                )
        
        self.competition_fig.tight_layout()
        self.competition_canvas.draw()
        
        # Heatmap de performance
        self.heatmap_ax.clear()
        
        # Criar matriz de performance por mês e dia da semana
        df['month'] = df['data_hora'].dt.month
        df['weekday'] = df['data_hora'].dt.day_name()
        
        heatmap_data = df.groupby(['month', 'weekday'])['lucro_prejuizo'].sum().unstack(fill_value=0)
        
        if not heatmap_data.empty:
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt='.1f',
                cmap='RdYlGn',
                center=0,
                ax=self.heatmap_ax,
                cbar_kws={'label': 'Lucro (€)'}
            )
            self.heatmap_ax.set_title('Heatmap de Performance (Mês vs Dia da Semana)')
            self.heatmap_ax.set_xlabel('Dia da Semana')
            self.heatmap_ax.set_ylabel('Mês')
        
        self.heatmap_fig.tight_layout()
        self.heatmap_canvas.draw()
    
    def update_risk_analysis(self):
        """Atualizar análise de risco"""
        risk_report = self.risk_analyzer.generate_risk_report()
        
        if 'error' in risk_report:
            return
        
        # Risk Score
        risk_class = risk_report['risk_classification']
        score = risk_class['score']
        level = risk_class['level']
        
        self.risk_score_label.configure(text=f"{score:.0f}/100")
        self.risk_level_label.configure(text=level)
        
        # VaR e CVaR
        basic_metrics = risk_report['basic_metrics']
        var_95 = basic_metrics.get('var_95', 0)
        cvar_95 = basic_metrics.get('cvar_95', 0)
        
        self.var_95_label.configure(text=f"VaR 95%: {var_95:.2f}%")
        self.cvar_95_label.configure(text=f"CVaR 95%: {cvar_95:.2f}%")
        
        # Drawdown
        max_dd = basic_metrics.get('max_drawdown', 0)
        self.max_dd_label.configure(text=f"Max DD: {max_dd:.1f}%")
        
        # Calcular drawdown atual (simplificado)
        if self.risk_analyzer.df_apostas is not None and not self.risk_analyzer.df_apostas.empty:
            returns = self.risk_analyzer.df_apostas['return'].values
            cumulative = np.cumsum(returns)
            current_dd = (max(cumulative) - cumulative[-1]) * 100 if len(cumulative) > 0 else 0
            self.current_dd_label.configure(text=f"Atual: {current_dd:.1f}%")
    
    def update_kelly_analysis(self):
        """Atualizar análise Kelly"""
        kelly_data = self.risk_analyzer.calculate_optimal_kelly()
        
        if not kelly_data:
            return
        
        # Kelly geral
        kelly_general = kelly_data.get('kelly_general', 0) * 100
        self.kelly_general_label.configure(text=f"{kelly_general:.2f}%")
        
        # Limpar frame de competições
        for widget in self.kelly_competition_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget('text') != "Top 5 Competições (Kelly %)":
                widget.destroy()
        
        # Top 5 competições
        kelly_by_comp = kelly_data.get('kelly_by_competition', {})
        if kelly_by_comp:
            sorted_comps = sorted(kelly_by_comp.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for i, (comp, kelly_pct) in enumerate(sorted_comps):
                comp_label = ctk.CTkLabel(
                    self.kelly_competition_frame,
                    text=f"{comp}: {kelly_pct*100:.2f}%",
                    font=ctk.CTkFont(size=11)
                )
                comp_label.pack(pady=2)
    
    def update_trend_analysis(self):
        """Atualizar análise de tendências"""
        if self.risk_analyzer.df_apostas is None or self.risk_analyzer.df_apostas.empty:
            return
        
        df = self.risk_analyzer.df_apostas.copy()
        now = datetime.now()
        
        # Últimos 7 dias
        week_ago = now - timedelta(days=7)
        week_data = df[df['data_hora'] >= week_ago]
        
        if not week_data.empty:
            week_roi = (week_data['lucro_prejuizo'].sum() / week_data['valor_apostado'].sum()) * 100
            week_bets = len(week_data)
            self.week_roi_label.configure(text=f"ROI: {week_roi:.2f}%")
            self.week_bets_label.configure(text=f"Apostas: {week_bets}")
        
        # Últimos 30 dias
        month_ago = now - timedelta(days=30)
        month_data = df[df['data_hora'] >= month_ago]
        
        if not month_data.empty:
            month_roi = (month_data['lucro_prejuizo'].sum() / month_data['valor_apostado'].sum()) * 100
            month_bets = len(month_data)
            self.month_roi_label.configure(text=f"ROI: {month_roi:.2f}%")
            self.month_bets_label.configure(text=f"Apostas: {month_bets}")
        
        # Tendência geral (comparar últimas 2 semanas)
        two_weeks_ago = now - timedelta(days=14)
        recent_data = df[df['data_hora'] >= two_weeks_ago]
        older_data = df[(df['data_hora'] >= month_ago) & (df['data_hora'] < two_weeks_ago)]
        
        if not recent_data.empty and not older_data.empty:
            recent_roi = (recent_data['lucro_prejuizo'].sum() / recent_data['valor_apostado'].sum()) * 100
            older_roi = (older_data['lucro_prejuizo'].sum() / older_data['valor_apostado'].sum()) * 100
            
            trend_diff = recent_roi - older_roi
            
            if trend_diff > 2:
                direction = "📈 Melhorando"
                strength = "Forte" if abs(trend_diff) > 5 else "Moderada"
            elif trend_diff < -2:
                direction = "📉 Piorando"
                strength = "Forte" if abs(trend_diff) > 5 else "Moderada"
            else:
                direction = "➡️ Estável"
                strength = "Neutro"
            
            self.trend_direction_label.configure(text=direction)
            self.trend_strength_label.configure(text=f"Força: {strength}")
    
    def update_alerts(self):
        """Atualizar alertas e recomendações"""
        # Limpar alertas existentes
        for widget in self.alerts_list_frame.winfo_children():
            widget.destroy()
        
        # Obter recomendações do risk analyzer
        risk_report = self.risk_analyzer.generate_risk_report()
        
        if 'error' not in risk_report:
            recommendations = risk_report['risk_classification']['recommendations']
            
            for i, rec in enumerate(recommendations[:5]):  # Máximo 5 alertas
                alert_frame = ctk.CTkFrame(self.alerts_list_frame)
                alert_frame.pack(fill="x", padx=5, pady=2)
                
                alert_label = ctk.CTkLabel(
                    alert_frame,
                    text=rec,
                    font=ctk.CTkFont(size=11),
                    wraplength=400
                )
                alert_label.pack(padx=10, pady=5)
        
        # Adicionar alertas personalizados baseados em métricas
        self.add_custom_alerts()
    
    def add_custom_alerts(self):
        """Adicionar alertas personalizados"""
        if self.risk_analyzer.df_apostas is None or self.risk_analyzer.df_apostas.empty:
            return
        
        df = self.risk_analyzer.df_apostas
        
        # Alert para sequência de perdas
        recent_results = df.tail(5)['resultado'].tolist()
        if recent_results.count('Perdida') >= 3:
            alert_frame = ctk.CTkFrame(self.alerts_list_frame)
            alert_frame.pack(fill="x", padx=5, pady=2)
            
            alert_label = ctk.CTkLabel(
                alert_frame,
                text="⚠️ Sequência de perdas detectada - Considere revisar estratégia",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            alert_label.pack(padx=10, pady=5)
        
        # Alert para ROI baixo
        total_roi = (df['lucro_prejuizo'].sum() / df['valor_apostado'].sum()) * 100
        if total_roi < -10:
            alert_frame = ctk.CTkFrame(self.alerts_list_frame)
            alert_frame.pack(fill="x", padx=5, pady=2)
            
            alert_label = ctk.CTkLabel(
                alert_frame,
                text="🚨 ROI muito baixo - Reavalie sua estratégia de apostas",
                font=ctk.CTkFont(size=11),
                text_color="red"
            )
            alert_label.pack(padx=10, pady=5)
    
    def toggle_auto_refresh(self):
        """Alternar auto-refresh"""
        if self.auto_refresh.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Iniciar auto-refresh"""
        if self.auto_refresh.get():
            self.refresh_data()
            self.after(self.refresh_interval, self.start_auto_refresh)
    
    def stop_auto_refresh(self):
        """Parar auto-refresh"""
        # O auto-refresh para automaticamente quando auto_refresh é False
        pass
    
    def manual_refresh(self):
        """Refresh manual"""
        self.refresh_data()
    
    def export_dashboard(self):
        """Exportar dados do dashboard"""
        try:
            from tkinter import filedialog
            import json
            
            # Preparar dados para exportação
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'basic_metrics': self.risk_analyzer.calculate_basic_metrics(),
                'kelly_analysis': self.risk_analyzer.calculate_optimal_kelly(),
                'risk_report': self.risk_analyzer.generate_risk_report()
            }
            
            # Salvar arquivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Exportar Dashboard"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                
                # Mostrar confirmação
                alert_frame = ctk.CTkFrame(self.alerts_list_frame)
                alert_frame.pack(fill="x", padx=5, pady=2)
                
                alert_label = ctk.CTkLabel(
                    alert_frame,
                    text=f"✅ Dashboard exportado para: {filename}",
                    font=ctk.CTkFont(size=11),
                    text_color="green"
                )
                alert_label.pack(padx=10, pady=5)
                
                # Remover após 5 segundos
                self.after(5000, alert_frame.destroy)
        
        except Exception as e:
            print(f"Erro ao exportar dashboard: {e}")

# Função para integrar o dashboard na aplicação principal
def create_dashboard_tab(parent, db: DatabaseManager):
    """Criar aba do dashboard na aplicação principal"""
    dashboard = DashboardAvancado(parent, db)
    return dashboard