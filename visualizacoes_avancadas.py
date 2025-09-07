#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Visualizações Avançadas
Gráficos interativos e análises visuais aprimoradas
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from main import DatabaseManager
import sqlite3
from collections import defaultdict
import calendar
from traducoes import t

# Configurar estilo dos gráficos
plt.style.use('dark_background')
sns.set_palette("husl")

class VisualizacoesAvancadas(ctk.CTkScrollableFrame):
    """Frame para visualizações avançadas"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.df_apostas = None
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Criar widgets das visualizações"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="📊 " + t("visualizacoes_avancadas"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Notebook para diferentes tipos de gráficos
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Criar abas
        self.create_heatmap_tab()
        self.create_waterfall_tab()
        self.create_correlation_tab()
        self.create_performance_tab()
        self.create_risk_tab()
    
    def create_heatmap_tab(self):
        """Criar aba de heatmaps"""
        heatmap_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(heatmap_frame, text="🔥 " + t("heatmaps"))
        
        # Controles
        controls_frame = ctk.CTkFrame(heatmap_frame)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            controls_frame,
            text=t("tipo_de_heatmap") + ":",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.heatmap_type = ctk.CTkComboBox(
            controls_frame,
            values=[
                t("performance_por_dia_semana"),
                t("performance_por_hora"),
                t("performance_por_mes"),
                t("performance_por_competicao"),
                t("odds_vs_resultado"),
                t("valor_vs_roi")
            ],
            command=self.update_heatmap
        )
        self.heatmap_type.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.heatmap_type.set(t("performance_por_dia_semana"))
        
        update_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 " + t("atualizar"),
            command=self.update_heatmap,
            width=100
        )
        update_btn.grid(row=0, column=2, padx=10, pady=10)
        
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para o gráfico
        self.heatmap_chart_frame = ctk.CTkFrame(heatmap_frame)
        self.heatmap_chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_waterfall_tab(self):
        """Criar aba de gráfico waterfall"""
        waterfall_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(waterfall_frame, text="💧 " + t("waterfall"))
        
        # Controles
        controls_frame = ctk.CTkFrame(waterfall_frame)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            controls_frame,
            text=t("periodo") + ":",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.waterfall_period = ctk.CTkComboBox(
            controls_frame,
            values=[t("ultimo_mes"), t("ultimos_3_meses"), t("ultimos_6_meses"), t("ultimo_ano")],
            command=self.update_waterfall
        )
        self.waterfall_period.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.waterfall_period.set(t("ultimos_3_meses"))
        
        update_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 " + t("atualizar"),
            command=self.update_waterfall,
            width=100
        )
        update_btn.grid(row=0, column=2, padx=10, pady=10)
        
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para o gráfico
        self.waterfall_chart_frame = ctk.CTkFrame(waterfall_frame)
        self.waterfall_chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_correlation_tab(self):
        """Criar aba de análise de correlação"""
        correlation_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(correlation_frame, text="🔗 " + t("correlacoes"))
        
        # Frame para o gráfico
        self.correlation_chart_frame = ctk.CTkFrame(correlation_frame)
        self.correlation_chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botão de atualização
        update_btn = ctk.CTkButton(
            correlation_frame,
            text="🔄 " + t("atualizar_correlacoes"),
            command=self.update_correlation,
            height=35
        )
        update_btn.pack(pady=10)
    
    def create_performance_tab(self):
        """Criar aba de análise de performance"""
        performance_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(performance_frame, text="📈 " + t("performance"))
        
        # Frame para múltiplos gráficos
        self.performance_chart_frame = ctk.CTkFrame(performance_frame)
        self.performance_chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botão de atualização
        update_btn = ctk.CTkButton(
            performance_frame,
            text="🔄 " + t("atualizar_performance"),
            command=self.update_performance,
            height=35
        )
        update_btn.pack(pady=10)
    
    def create_risk_tab(self):
        """Criar aba de análise de risco"""
        risk_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(risk_frame, text="⚠️ " + t("analise_de_risco"))
        
        # Frame para gráficos de risco
        self.risk_chart_frame = ctk.CTkFrame(risk_frame)
        self.risk_chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame para métricas de risco
        metrics_frame = ctk.CTkFrame(risk_frame)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        self.risk_metrics_labels = {}
        metrics = [t("var_95"), t("drawdown_maximo"), t("sharpe_ratio"), t("volatilidade")]
        
        for i, metric in enumerate(metrics):
            label = ctk.CTkLabel(
                metrics_frame,
                text=f"{metric}: " + t("calculando"),
                font=ctk.CTkFont(size=12, weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.risk_metrics_labels[metric] = label
        
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Botão de atualização
        update_btn = ctk.CTkButton(
            risk_frame,
            text="🔄 " + t("atualizar_analise_risco"),
            command=self.update_risk_analysis,
            height=35
        )
        update_btn.pack(pady=10)
    
    def load_data(self):
        """Carregar dados das apostas"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            self.df_apostas = pd.read_sql_query("""
                SELECT * FROM apostas ORDER BY data_hora
            """, conn)
            conn.close()
            
            if not self.df_apostas.empty:
                # Converter data_hora para datetime
                self.df_apostas['data_hora'] = pd.to_datetime(
                    self.df_apostas['data_hora'], 
                    format='%d/%m/%Y %H:%M',
                    dayfirst=True,
                    errors='coerce'
                )
                
                # Adicionar colunas derivadas
                self.df_apostas['dia_semana'] = self.df_apostas['data_hora'].dt.day_name()
                self.df_apostas['hora'] = self.df_apostas['data_hora'].dt.hour
                self.df_apostas['mes'] = self.df_apostas['data_hora'].dt.month
                self.df_apostas['ano'] = self.df_apostas['data_hora'].dt.year
                
                # Calcular ROI por aposta
                self.df_apostas['roi'] = (self.df_apostas['lucro_prejuizo'] / self.df_apostas['valor_apostado']) * 100
                
                # Atualizar todas as visualizações
                self.update_all_charts()
        
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def update_all_charts(self):
        """Atualizar todos os gráficos"""
        self.update_heatmap()
        self.update_waterfall()
        self.update_correlation()
        self.update_performance()
        self.update_risk_analysis()
    
    def update_heatmap(self, *args):
        """Atualizar heatmap"""
        if self.df_apostas is None or self.df_apostas.empty:
            return
        
        # Limpar frame anterior
        for widget in self.heatmap_chart_frame.winfo_children():
            widget.destroy()
        
        heatmap_type = self.heatmap_type.get()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#2b2b2b')
        
        try:
            if heatmap_type == "Performance por Dia da Semana":
                self.create_weekday_heatmap(ax)
            elif heatmap_type == "Performance por Hora":
                self.create_hour_heatmap(ax)
            elif heatmap_type == "Performance por Mês":
                self.create_month_heatmap(ax)
            elif heatmap_type == "Performance por Competição":
                self.create_competition_heatmap(ax)
            elif heatmap_type == "Odds vs Resultado":
                self.create_odds_result_heatmap(ax)
            elif heatmap_type == "Valor vs ROI":
                self.create_value_roi_heatmap(ax)
            
            plt.tight_layout()
            
            # Adicionar ao frame
            canvas = FigureCanvasTkAgg(fig, self.heatmap_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Erro ao criar heatmap: {e}")
        finally:
            plt.close(fig)
    
    def create_weekday_heatmap(self, ax):
        """Criar heatmap de performance por dia da semana"""
        # Agrupar por dia da semana e resultado
        weekday_performance = self.df_apostas.groupby(['dia_semana', 'resultado']).size().unstack(fill_value=0)
        
        # Reordenar dias da semana
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_performance = weekday_performance.reindex(weekday_order, fill_value=0)
        
        # Calcular percentuais
        weekday_percentage = weekday_performance.div(weekday_performance.sum(axis=1), axis=0) * 100
        
        sns.heatmap(
            weekday_percentage,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            ax=ax,
            cbar_kws={'label': 'Percentual (%)'}
        )
        
        ax.set_title('Performance por Dia da Semana (%)', fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Resultado', fontsize=12, color='white')
        ax.set_ylabel('Dia da Semana', fontsize=12, color='white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
    
    def create_hour_heatmap(self, ax):
        """Criar heatmap de performance por hora"""
        # Agrupar por hora e calcular ROI médio
        hour_roi = self.df_apostas.groupby('hora')['roi'].mean()
        hour_count = self.df_apostas.groupby('hora').size()
        
        # Criar matriz para heatmap
        hours = range(24)
        data = []
        
        for hour in hours:
            roi = hour_roi.get(hour, 0)
            count = hour_count.get(hour, 0)
            data.append([roi, count])
        
        data_array = np.array(data).T
        
        sns.heatmap(
            data_array,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            ax=ax,
            xticklabels=[f"{h}h" for h in hours],
            yticklabels=['ROI Médio (%)', 'Número de Apostas']
        )
        
        ax.set_title('Performance por Hora do Dia', fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Hora', fontsize=12, color='white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
    
    def create_month_heatmap(self, ax):
        """Criar heatmap de performance por mês"""
        # Agrupar por ano e mês
        month_data = self.df_apostas.groupby(['ano', 'mes']).agg({
            'roi': 'mean',
            'lucro_prejuizo': 'sum',
            'valor_apostado': 'sum'
        })
        
        # Criar pivot table
        roi_pivot = month_data['roi'].unstack(fill_value=0)
        
        sns.heatmap(
            roi_pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            ax=ax,
            xticklabels=[calendar.month_abbr[i] for i in range(1, 13)],
            cbar_kws={'label': 'ROI Médio (%)'}
        )
        
        ax.set_title('Performance por Mês e Ano', fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Mês', fontsize=12, color='white')
        ax.set_ylabel('Ano', fontsize=12, color='white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
    
    def create_competition_heatmap(self, ax):
        """Criar heatmap de performance por competição"""
        comp_data = self.df_apostas.groupby(['competicao', 'tipo_aposta']).agg({
            'roi': 'mean',
            'id': 'count'
        }).round(2)
        
        # Filtrar combinações com pelo menos 3 apostas
        comp_data = comp_data[comp_data['id'] >= 3]
        
        if not comp_data.empty:
            roi_pivot = comp_data['roi'].unstack(fill_value=0)
            
            sns.heatmap(
                roi_pivot,
                annot=True,
                fmt='.1f',
                cmap='RdYlGn',
                ax=ax,
                cbar_kws={'label': 'ROI Médio (%)'}
            )
            
            ax.set_title('ROI por Competição e Tipo de Aposta', fontsize=16, fontweight='bold', color='white')
            ax.set_xlabel('Tipo de Aposta', fontsize=12, color='white')
            ax.set_ylabel('Competição', fontsize=12, color='white')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
        else:
            ax.text(0.5, 0.5, 'Dados insuficientes\n(mínimo 3 apostas por combinação)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14, color='white')
    
    def create_odds_result_heatmap(self, ax):
        """Criar heatmap de odds vs resultado"""
        # Criar bins para odds
        self.df_apostas['odd_bin'] = pd.cut(
            self.df_apostas['odd'], 
            bins=[0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, float('inf')],
            labels=['1.0-1.5', '1.5-2.0', '2.0-2.5', '2.5-3.0', '3.0-4.0', '4.0-5.0', '5.0+']
        )
        
        # Agrupar por bin de odd e resultado
        odds_result = self.df_apostas.groupby(['odd_bin', 'resultado']).size().unstack(fill_value=0)
        
        # Calcular percentuais
        odds_percentage = odds_result.div(odds_result.sum(axis=1), axis=0) * 100
        
        sns.heatmap(
            odds_percentage,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            ax=ax,
            cbar_kws={'label': 'Percentual (%)'}
        )
        
        ax.set_title('Distribuição de Resultados por Faixa de Odd', fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Resultado', fontsize=12, color='white')
        ax.set_ylabel('Faixa de Odd', fontsize=12, color='white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
    
    def create_value_roi_heatmap(self, ax):
        """Criar heatmap de valor apostado vs ROI"""
        # Criar bins para valores
        self.df_apostas['valor_bin'] = pd.cut(
            self.df_apostas['valor_apostado'],
            bins=5,
            labels=['Muito Baixo', 'Baixo', 'Médio', 'Alto', 'Muito Alto']
        )
        
        # Agrupar por bin de valor e calcular estatísticas
        value_stats = self.df_apostas.groupby('valor_bin').agg({
            'roi': ['mean', 'std', 'count'],
            'lucro_prejuizo': 'sum'
        }).round(2)
        
        # Preparar dados para heatmap
        heatmap_data = value_stats['roi'][['mean', 'std']].T
        
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            ax=ax,
            cbar_kws={'label': 'Valor'}
        )
        
        ax.set_title('ROI Médio e Desvio Padrão por Faixa de Valor', fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel('Faixa de Valor Apostado', fontsize=12, color='white')
        ax.set_ylabel('Métrica', fontsize=12, color='white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
    
    def update_waterfall(self, *args):
        """Atualizar gráfico waterfall"""
        if self.df_apostas is None or self.df_apostas.empty:
            return
        
        # Limpar frame anterior
        for widget in self.waterfall_chart_frame.winfo_children():
            widget.destroy()
        
        period = self.waterfall_period.get()
        
        # Filtrar por período
        end_date = datetime.now()
        if period == "Último mês":
            start_date = end_date - timedelta(days=30)
        elif period == "Últimos 3 meses":
            start_date = end_date - timedelta(days=90)
        elif period == "Últimos 6 meses":
            start_date = end_date - timedelta(days=180)
        else:  # Último ano
            start_date = end_date - timedelta(days=365)
        
        df_filtered = self.df_apostas[
            (self.df_apostas['data_hora'] >= start_date) & 
            (self.df_apostas['data_hora'] <= end_date)
        ]
        
        if df_filtered.empty:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#2b2b2b')
        
        try:
            # Agrupar por semana e calcular lucro acumulado
            df_filtered['semana'] = df_filtered['data_hora'].dt.to_period('W')
            weekly_profit = df_filtered.groupby('semana')['lucro_prejuizo'].sum()
            
            # Criar gráfico waterfall
            x_pos = range(len(weekly_profit))
            cumulative = np.cumsum(weekly_profit.values)
            
            colors = ['green' if x >= 0 else 'red' for x in weekly_profit.values]
            
            # Barras do waterfall
            for i, (profit, cum) in enumerate(zip(weekly_profit.values, cumulative)):
                if i == 0:
                    ax.bar(i, profit, color=colors[i], alpha=0.7)
                else:
                    ax.bar(i, profit, bottom=cumulative[i-1], color=colors[i], alpha=0.7)
            
            # Linha de evolução
            ax.plot(x_pos, cumulative, 'o-', color='white', linewidth=2, markersize=6)
            
            ax.set_title(f'Evolução Semanal da Banca - {period}', fontsize=16, fontweight='bold', color='white')
            ax.set_xlabel('Semana', fontsize=12, color='white')
            ax.set_ylabel('Lucro/Prejuízo (€)', fontsize=12, color='white')
            ax.grid(True, alpha=0.3, color='white')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('white')
            
            # Formatação do eixo X
            ax.set_xticks(x_pos[::max(1, len(x_pos)//10)])
            ax.set_xticklabels([str(weekly_profit.index[i]) for i in x_pos[::max(1, len(x_pos)//10)]], rotation=45)
            
            plt.tight_layout()
            
            # Adicionar ao frame
            canvas = FigureCanvasTkAgg(fig, self.waterfall_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Erro ao criar waterfall: {e}")
        finally:
            plt.close(fig)
    
    def update_correlation(self, *args):
        """Atualizar análise de correlação"""
        if self.df_apostas is None or self.df_apostas.empty:
            return
        
        # Limpar frame anterior
        for widget in self.correlation_chart_frame.winfo_children():
            widget.destroy()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.patch.set_facecolor('#2b2b2b')
        
        try:
            # 1. Correlação entre variáveis numéricas
            numeric_cols = ['odd', 'valor_apostado', 'lucro_prejuizo', 'roi']
            correlation_matrix = self.df_apostas[numeric_cols].corr()
            
            sns.heatmap(
                correlation_matrix,
                annot=True,
                fmt='.2f',
                cmap='RdBu_r',
                center=0,
                ax=ax1,
                square=True
            )
            ax1.set_title('Matriz de Correlação', fontsize=14, fontweight='bold', color='white')
            ax1.tick_params(colors='white')
            ax1.xaxis.label.set_color('white')
            ax1.yaxis.label.set_color('white')
            
            # 2. Scatter plot: Odd vs ROI
            scatter = ax2.scatter(
                self.df_apostas['odd'], 
                self.df_apostas['roi'],
                c=self.df_apostas['valor_apostado'],
                cmap='viridis',
                alpha=0.6
            )
            ax2.set_xlabel('Odd', color='white')
            ax2.set_ylabel('ROI (%)', color='white')
            ax2.set_title('Odd vs ROI (cor = valor apostado)', fontsize=14, fontweight='bold', color='white')
            ax2.tick_params(colors='white')
            ax2.grid(True, alpha=0.3, color='white')
            for spine in ax2.spines.values():
                spine.set_color('white')
            plt.colorbar(scatter, ax=ax2, label='Valor Apostado (€)')
            
            # 3. Box plot: ROI por tipo de aposta
            roi_by_type = []
            types = []
            for tipo in self.df_apostas['tipo_aposta'].unique():
                roi_data = self.df_apostas[self.df_apostas['tipo_aposta'] == tipo]['roi']
                if len(roi_data) >= 3:  # Mínimo 3 apostas
                    roi_by_type.append(roi_data)
                    types.append(tipo)
            
            if roi_by_type:
                ax3.boxplot(roi_by_type, labels=types)
                ax3.set_ylabel('ROI (%)', color='white')
                ax3.set_title('Distribuição de ROI por Tipo de Aposta', fontsize=14, fontweight='bold', color='white')
                ax3.tick_params(axis='x', rotation=45, colors='white')
                ax3.tick_params(axis='y', colors='white')
                ax3.grid(True, alpha=0.3, color='white')
                for spine in ax3.spines.values():
                    spine.set_color('white')
            
            # 4. Histograma de distribuição de lucros
            ax4.hist(
                self.df_apostas['lucro_prejuizo'], 
                bins=20, 
                alpha=0.7, 
                color='skyblue',
                edgecolor='black'
            )
            ax4.axvline(0, color='red', linestyle='--', linewidth=2, label='Break-even')
            ax4.set_xlabel('Lucro/Prejuízo (€)', color='white')
            ax4.set_ylabel('Frequência', color='white')
            ax4.set_title('Distribuição de Lucros/Prejuízos', fontsize=14, fontweight='bold', color='white')
            ax4.tick_params(colors='white')
            ax4.grid(True, alpha=0.3, color='white')
            for spine in ax4.spines.values():
                spine.set_color('white')
            legend = ax4.legend()
            legend.get_frame().set_facecolor('#2b2b2b')
            for text in legend.get_texts():
                text.set_color('white')
            
            plt.tight_layout()
            
            # Adicionar ao frame
            canvas = FigureCanvasTkAgg(fig, self.correlation_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Erro ao criar correlações: {e}")
        finally:
            plt.close(fig)
    
    def update_performance(self, *args):
        """Atualizar análise de performance"""
        if self.df_apostas is None or self.df_apostas.empty:
            return
        
        # Limpar frame anterior
        for widget in self.performance_chart_frame.winfo_children():
            widget.destroy()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.patch.set_facecolor('#2b2b2b')
        
        try:
            # 1. Evolução do ROI acumulado
            self.df_apostas_sorted = self.df_apostas.sort_values('data_hora')
            cumulative_roi = self.df_apostas_sorted['roi'].cumsum()
            
            ax1.plot(cumulative_roi.index, cumulative_roi.values, linewidth=2, color='cyan')
            ax1.fill_between(cumulative_roi.index, cumulative_roi.values, alpha=0.3, color='cyan')
            ax1.set_title('Evolução do ROI Acumulado', fontsize=14, fontweight='bold', color='white')
            ax1.set_ylabel('ROI Acumulado (%)', color='white')
            ax1.tick_params(colors='white')
            ax1.grid(True, alpha=0.3, color='white')
            for spine in ax1.spines.values():
                spine.set_color('white')
            
            # 2. Performance por competição
            comp_performance = self.df_apostas.groupby('competicao').agg({
                'roi': 'mean',
                'id': 'count'
            }).sort_values('roi', ascending=True)
            
            # Filtrar competições com pelo menos 3 apostas
            comp_performance = comp_performance[comp_performance['id'] >= 3]
            
            if not comp_performance.empty:
                colors = ['green' if x >= 0 else 'red' for x in comp_performance['roi']]
                ax2.barh(range(len(comp_performance)), comp_performance['roi'], color=colors, alpha=0.7)
                ax2.set_yticks(range(len(comp_performance)))
                ax2.set_yticklabels(comp_performance.index)
                ax2.set_xlabel('ROI Médio (%)', color='white')
                ax2.set_title('Performance por Competição', fontsize=14, fontweight='bold', color='white')
                ax2.tick_params(colors='white')
                ax2.grid(True, alpha=0.3, color='white')
                for spine in ax2.spines.values():
                    spine.set_color('white')
            
            # 3. Análise de sequências (streaks)
            results = self.df_apostas_sorted['resultado'].map({'Ganha': 1, 'Perdida': -1, 'Anulada': 0})
            streaks = []
            current_streak = 0
            
            for result in results:
                if result == 1:  # Ganha
                    current_streak = max(1, current_streak + 1)
                elif result == -1:  # Perdida
                    current_streak = min(-1, current_streak - 1)
                else:  # Anulada
                    current_streak = 0
                streaks.append(current_streak)
            
            ax3.plot(range(len(streaks)), streaks, linewidth=2, color='orange')
            ax3.axhline(0, color='white', linestyle='--', alpha=0.5)
            ax3.set_title('Sequências de Vitórias/Derrotas', fontsize=14, fontweight='bold', color='white')
            ax3.set_ylabel('Streak (+ vitórias, - derrotas)', color='white')
            ax3.set_xlabel('Número da Aposta', color='white')
            ax3.tick_params(colors='white')
            ax3.grid(True, alpha=0.3, color='white')
            for spine in ax3.spines.values():
                spine.set_color('white')
            
            # 4. Distribuição de odds vs taxa de acerto
            odd_bins = pd.cut(self.df_apostas['odd'], bins=10)
            odd_analysis = self.df_apostas.groupby(odd_bins).agg({
                'resultado': lambda x: (x == 'Ganha').mean() * 100,
                'id': 'count'
            })
            
            # Filtrar bins com pelo menos 5 apostas
            odd_analysis = odd_analysis[odd_analysis['id'] >= 5]
            
            if not odd_analysis.empty:
                ax4.bar(range(len(odd_analysis)), odd_analysis['resultado'], alpha=0.7, color='lightgreen')
                ax4.set_xticks(range(len(odd_analysis)))
                ax4.set_xticklabels([f"{interval.left:.1f}-{interval.right:.1f}" for interval in odd_analysis.index], rotation=45)
                ax4.set_ylabel('Taxa de Acerto (%)', color='white')
                ax4.set_xlabel('Faixa de Odd', color='white')
                ax4.set_title('Taxa de Acerto por Faixa de Odd', fontsize=14, fontweight='bold', color='white')
                ax4.tick_params(colors='white')
                ax4.grid(True, alpha=0.3, color='white')
                for spine in ax4.spines.values():
                    spine.set_color('white')
            
            plt.tight_layout()
            
            # Adicionar ao frame
            canvas = FigureCanvasTkAgg(fig, self.performance_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Erro ao criar performance: {e}")
        finally:
            plt.close(fig)
    
    def update_risk_analysis(self, *args):
        """Atualizar análise de risco"""
        if self.df_apostas is None or self.df_apostas.empty:
            return
        
        # Limpar frame anterior
        for widget in self.risk_chart_frame.winfo_children():
            widget.destroy()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.patch.set_facecolor('#2b2b2b')
        
        try:
            # Calcular métricas de risco
            returns = self.df_apostas['roi'].values
            
            # 1. Value at Risk (VaR)
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            
            # 2. Drawdown
            cumulative_returns = np.cumsum(returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = cumulative_returns - running_max
            max_drawdown = np.min(drawdown)
            
            # 3. Sharpe Ratio (assumindo risk-free rate = 0)
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # 4. Volatilidade
            volatility = np.std(returns)
            
            # Atualizar labels de métricas
            self.risk_metrics_labels["VaR (95%)"].configure(text=f"VaR (95%): {var_95:.2f}%")
            self.risk_metrics_labels["Drawdown Máximo"].configure(text=f"Drawdown Máximo: {max_drawdown:.2f}%")
            self.risk_metrics_labels["Sharpe Ratio"].configure(text=f"Sharpe Ratio: {sharpe_ratio:.2f}")
            self.risk_metrics_labels["Volatilidade"].configure(text=f"Volatilidade: {volatility:.2f}%")
            
            # Gráfico 1: Distribuição de retornos com VaR
            ax1.hist(returns, bins=30, alpha=0.7, color='lightblue', edgecolor='black')
            ax1.axvline(var_95, color='red', linestyle='--', linewidth=2, label=f'VaR 95%: {var_95:.2f}%')
            ax1.axvline(var_99, color='darkred', linestyle='--', linewidth=2, label=f'VaR 99%: {var_99:.2f}%')
            ax1.axvline(0, color='green', linestyle='-', linewidth=2, label='Break-even')
            ax1.set_xlabel('ROI (%)', color='white')
            ax1.set_ylabel('Frequência', color='white')
            ax1.set_title('Distribuição de Retornos e VaR', fontsize=14, fontweight='bold', color='white')
            ax1.tick_params(colors='white')
            ax1.grid(True, alpha=0.3, color='white')
            for spine in ax1.spines.values():
                spine.set_color('white')
            legend = ax1.legend()
            legend.get_frame().set_facecolor('#2b2b2b')
            for text in legend.get_texts():
                text.set_color('white')
            
            # Gráfico 2: Evolução do Drawdown
            ax2.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.7, color='red')
            ax2.plot(range(len(drawdown)), drawdown, linewidth=2, color='darkred')
            ax2.set_xlabel('Número da Aposta', color='white')
            ax2.set_ylabel('Drawdown (%)', color='white')
            ax2.set_title('Evolução do Drawdown', fontsize=14, fontweight='bold', color='white')
            ax2.tick_params(colors='white')
            ax2.grid(True, alpha=0.3, color='white')
            for spine in ax2.spines.values():
                spine.set_color('white')
            
            # Gráfico 3: Rolling Sharpe Ratio (janela de 20 apostas)
            if len(returns) >= 20:
                rolling_sharpe = []
                window = 20
                for i in range(window, len(returns)):
                    window_returns = returns[i-window:i]
                    window_sharpe = np.mean(window_returns) / np.std(window_returns) if np.std(window_returns) > 0 else 0
                    rolling_sharpe.append(window_sharpe)
                
                ax3.plot(range(window, len(returns)), rolling_sharpe, linewidth=2, color='purple')
                ax3.axhline(0, color='white', linestyle='--', alpha=0.5)
                ax3.set_xlabel('Número da Aposta', color='white')
                ax3.set_ylabel('Sharpe Ratio', color='white')
                ax3.set_title(f'Sharpe Ratio Móvel (janela {window})', fontsize=14, fontweight='bold', color='white')
                ax3.tick_params(colors='white')
                ax3.grid(True, alpha=0.3, color='white')
                for spine in ax3.spines.values():
                    spine.set_color('white')
            
            # Gráfico 4: Risk-Return Scatter por competição
            comp_risk_return = self.df_apostas.groupby('competicao').agg({
                'roi': ['mean', 'std', 'count']
            })
            comp_risk_return.columns = ['return', 'risk', 'count']
            comp_risk_return = comp_risk_return[comp_risk_return['count'] >= 5]  # Mínimo 5 apostas
            
            if not comp_risk_return.empty:
                scatter = ax4.scatter(
                    comp_risk_return['risk'], 
                    comp_risk_return['return'],
                    s=comp_risk_return['count'] * 10,  # Tamanho proporcional ao número de apostas
                    alpha=0.7,
                    c=comp_risk_return['return'],
                    cmap='RdYlGn'
                )
                
                # Adicionar labels
                for i, comp in enumerate(comp_risk_return.index):
                    ax4.annotate(
                        comp[:10] + '...' if len(comp) > 10 else comp,
                        (comp_risk_return['risk'].iloc[i], comp_risk_return['return'].iloc[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=8
                    )
                
                ax4.set_xlabel('Risco (Desvio Padrão %)', color='white')
                ax4.set_ylabel('Retorno Médio (%)', color='white')
                ax4.set_title('Risco vs Retorno por Competição', fontsize=14, fontweight='bold', color='white')
                ax4.tick_params(colors='white')
                ax4.grid(True, alpha=0.3, color='white')
                for spine in ax4.spines.values():
                    spine.set_color('white')
                plt.colorbar(scatter, ax=ax4, label='Retorno Médio (%)')
            
            plt.tight_layout()
            
            # Adicionar ao frame
            canvas = FigureCanvasTkAgg(fig, self.risk_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Erro ao criar análise de risco: {e}")
        finally:
            plt.close(fig)