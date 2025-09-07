#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Alertas Inteligentes
Sistema de notificações e alertas baseados em análise de dados
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from main import DatabaseManager
from analise_risco import RiskAnalyzer
import threading
import time
import warnings
warnings.filterwarnings('ignore')

class AlertSystem:
    """Sistema de alertas inteligentes"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.risk_analyzer = RiskAnalyzer(db)
        self.alerts_config = self.load_alerts_config()
        self.active_alerts = []
        self.alert_history = []
        
    def load_alerts_config(self) -> Dict:
        """Carregar configurações de alertas"""
        default_config = {
            'drawdown_threshold': 10.0,  # % de drawdown para alerta
            'losing_streak_threshold': 3,  # Sequência de perdas
            'roi_threshold': -5.0,  # ROI negativo para alerta
            'bankroll_threshold': 20.0,  # % da banca para alerta
            'odd_threshold': 5.0,  # Odds muito altas
            'value_bet_threshold': 1.1,  # Valor esperado mínimo
            'kelly_threshold': 0.25,  # Kelly muito alto
            'variance_threshold': 2.0,  # Variância alta
            'check_interval': 300,  # Intervalo de verificação (segundos)
            'enabled_alerts': {
                'drawdown': True,
                'losing_streak': True,
                'roi_warning': True,
                'bankroll_low': True,
                'high_risk_bet': True,
                'value_opportunity': True,
                'kelly_warning': True,
                'performance_anomaly': True
            }
        }
        
        try:
            config_path = Path('config/alerts_config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
        except Exception:
            pass
        
        return default_config
    
    def save_alerts_config(self):
        """Salvar configurações de alertas"""
        try:
            config_path = Path('config')
            config_path.mkdir(exist_ok=True)
            
            with open(config_path / 'alerts_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.alerts_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def check_all_alerts(self) -> List[Dict]:
        """Verificar todos os tipos de alertas"""
        new_alerts = []
        
        if self.alerts_config['enabled_alerts']['drawdown']:
            drawdown_alerts = self.check_drawdown_alert()
            new_alerts.extend(drawdown_alerts)
        
        if self.alerts_config['enabled_alerts']['losing_streak']:
            streak_alerts = self.check_losing_streak_alert()
            new_alerts.extend(streak_alerts)
        
        if self.alerts_config['enabled_alerts']['roi_warning']:
            roi_alerts = self.check_roi_alert()
            new_alerts.extend(roi_alerts)
        
        if self.alerts_config['enabled_alerts']['bankroll_low']:
            bankroll_alerts = self.check_bankroll_alert()
            new_alerts.extend(bankroll_alerts)
        
        if self.alerts_config['enabled_alerts']['performance_anomaly']:
            anomaly_alerts = self.check_performance_anomaly()
            new_alerts.extend(anomaly_alerts)
        
        # Adicionar novos alertas à lista ativa
        for alert in new_alerts:
            alert['timestamp'] = datetime.now()
            alert['id'] = len(self.alert_history) + 1
            self.active_alerts.append(alert)
            self.alert_history.append(alert)
        
        return new_alerts
    
    def check_drawdown_alert(self) -> List[Dict]:
        """Verificar alerta de drawdown"""
        alerts = []
        
        try:
            # Calcular drawdown atual
            risk_metrics = self.risk_analyzer.calculate_basic_metrics()
            
            if 'max_drawdown' in risk_metrics:
                current_drawdown = abs(risk_metrics['max_drawdown']) * 100
                
                if current_drawdown > self.alerts_config['drawdown_threshold']:
                    alerts.append({
                        'type': 'drawdown',
                        'severity': 'high' if current_drawdown > 20 else 'medium',
                        'title': '⚠️ Drawdown Elevado',
                        'message': f'Drawdown atual: {current_drawdown:.1f}%',
                        'details': f'O drawdown ultrapassou o limite de {self.alerts_config["drawdown_threshold"]}%',
                        'value': current_drawdown,
                        'threshold': self.alerts_config['drawdown_threshold']
                    })
        except Exception as e:
            print(f"Erro ao verificar drawdown: {e}")
        
        return alerts
    
    def check_losing_streak_alert(self) -> List[Dict]:
        """Verificar alerta de sequência de perdas"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            
            # Buscar últimas apostas
            query = """
                SELECT resultado 
                FROM apostas 
                WHERE resultado IN ('Ganha', 'Perdida')
                ORDER BY data_hora DESC 
                LIMIT 20
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                # Contar sequência atual de perdas
                losing_streak = 0
                for resultado in df['resultado']:
                    if resultado == 'Perdida':
                        losing_streak += 1
                    else:
                        break
                
                if losing_streak >= self.alerts_config['losing_streak_threshold']:
                    alerts.append({
                        'type': 'losing_streak',
                        'severity': 'high' if losing_streak >= 5 else 'medium',
                        'title': '🔴 Sequência de Perdas',
                        'message': f'{losing_streak} apostas perdidas consecutivas',
                        'details': 'Considere revisar sua estratégia ou fazer uma pausa',
                        'value': losing_streak,
                        'threshold': self.alerts_config['losing_streak_threshold']
                    })
        except Exception as e:
            print(f"Erro ao verificar sequência de perdas: {e}")
        
        return alerts
    
    def check_roi_alert(self) -> List[Dict]:
        """Verificar alerta de ROI baixo"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            
            # Calcular ROI dos últimos 30 dias
            query = """
                SELECT 
                    SUM(valor_apostado) as total_apostado,
                    SUM(lucro_prejuizo) as lucro_total
                FROM apostas 
                WHERE resultado IN ('Ganha', 'Perdida')
                AND date(data_hora, 'localtime') >= date('now', '-30 days')
            """
            
            result = conn.execute(query).fetchone()
            conn.close()
            
            if result and result[0] and result[0] > 0:
                roi = (result[1] / result[0]) * 100
                
                if roi < self.alerts_config['roi_threshold']:
                    alerts.append({
                        'type': 'roi_warning',
                        'severity': 'medium' if roi > -10 else 'high',
                        'title': '📉 ROI Baixo',
                        'message': f'ROI dos últimos 30 dias: {roi:.1f}%',
                        'details': 'Performance abaixo do esperado no último mês',
                        'value': roi,
                        'threshold': self.alerts_config['roi_threshold']
                    })
        except Exception as e:
            print(f"Erro ao verificar ROI: {e}")
        
        return alerts
    
    def check_bankroll_alert(self) -> List[Dict]:
        """Verificar alerta de banca baixa"""
        alerts = []
        
        try:
            # Obter saldo atual e inicial
            saldo_atual = self.db.get_saldo_atual()
            saldo_inicial = self.db.obter_saldo_inicial()
            
            if saldo_inicial > 0:
                percentual_restante = (saldo_atual / saldo_inicial) * 100
                
                if percentual_restante < self.alerts_config['bankroll_threshold']:
                    alerts.append({
                        'type': 'bankroll_low',
                        'severity': 'high' if percentual_restante < 10 else 'medium',
                        'title': '💰 Banca Baixa',
                        'message': f'Restam {percentual_restante:.1f}% da banca inicial',
                        'details': f'Saldo atual: €{saldo_atual:.2f} de €{saldo_inicial:.2f}',
                        'value': percentual_restante,
                        'threshold': self.alerts_config['bankroll_threshold']
                    })
        except Exception as e:
            print(f"Erro ao verificar banca: {e}")
        
        return alerts
    
    def check_performance_anomaly(self) -> List[Dict]:
        """Verificar anomalias de performance"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            
            # Analisar performance por período
            query = """
                SELECT 
                    date(data_hora, 'localtime') as data,
                    COUNT(*) as apostas,
                    SUM(CASE WHEN resultado = 'Ganha' THEN 1 ELSE 0 END) as ganhas,
                    SUM(valor_apostado) as total_apostado,
                    SUM(lucro_prejuizo) as lucro
                FROM apostas 
                WHERE resultado IN ('Ganha', 'Perdida')
                AND date(data_hora, 'localtime') >= date('now', '-14 days')
                GROUP BY date(data_hora, 'localtime')
                ORDER BY data DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) >= 7:  # Pelo menos uma semana de dados
                # Calcular métricas
                df['win_rate'] = df['ganhas'] / df['apostas']
                df['roi'] = df['lucro'] / df['total_apostado']
                
                # Detectar anomalias
                recent_win_rate = df['win_rate'].head(3).mean()  # Últimos 3 dias
                historical_win_rate = df['win_rate'].tail(7).mean()  # Últimos 7 dias
                
                recent_roi = df['roi'].head(3).mean()
                historical_roi = df['roi'].tail(7).mean()
                
                # Alerta se performance recente muito diferente
                if abs(recent_win_rate - historical_win_rate) > 0.3:  # 30% de diferença
                    trend = "melhorou" if recent_win_rate > historical_win_rate else "piorou"
                    alerts.append({
                        'type': 'performance_anomaly',
                        'severity': 'low',
                        'title': '📊 Mudança de Performance',
                        'message': f'Taxa de acerto {trend} significativamente',
                        'details': f'Recente: {recent_win_rate:.1%} vs Histórica: {historical_win_rate:.1%}',
                        'value': recent_win_rate,
                        'comparison': historical_win_rate
                    })
                
                if abs(recent_roi - historical_roi) > 0.2:  # 20% de diferença no ROI
                    trend = "melhorou" if recent_roi > historical_roi else "piorou"
                    alerts.append({
                        'type': 'performance_anomaly',
                        'severity': 'low',
                        'title': '📈 Mudança no ROI',
                        'message': f'ROI {trend} significativamente',
                        'details': f'Recente: {recent_roi:.1%} vs Histórico: {historical_roi:.1%}',
                        'value': recent_roi,
                        'comparison': historical_roi
                    })
        except Exception as e:
            print(f"Erro ao verificar anomalias: {e}")
        
        return alerts
    
    def check_bet_alert(self, equipa_casa: str, equipa_fora: str, odd: float, valor: float) -> List[Dict]:
        """Verificar alertas para uma aposta específica"""
        alerts = []
        
        try:
            # Alerta de odd muito alta
            if self.alerts_config['enabled_alerts']['high_risk_bet'] and odd > self.alerts_config['odd_threshold']:
                alerts.append({
                    'type': 'high_risk_bet',
                    'severity': 'medium',
                    'title': '⚡ Odd Elevada',
                    'message': f'Odd {odd:.2f} é considerada de alto risco',
                    'details': 'Apostas com odds altas têm menor probabilidade de sucesso',
                    'value': odd,
                    'threshold': self.alerts_config['odd_threshold']
                })
            
            # Alerta de valor da aposta vs banca
            saldo_atual = self.db.obter_saldo_atual()
            percentual_banca = (valor / saldo_atual) * 100 if saldo_atual > 0 else 0
            
            if percentual_banca > 10:  # Mais de 10% da banca
                alerts.append({
                    'type': 'high_stake',
                    'severity': 'high' if percentual_banca > 20 else 'medium',
                    'title': '💸 Valor Alto',
                    'message': f'Apostando {percentual_banca:.1f}% da banca',
                    'details': 'Considere reduzir o valor para gerenciar o risco',
                    'value': percentual_banca,
                    'threshold': 10
                })
            
            # Calcular Kelly Criterion se possível
            try:
                implied_prob = 1 / odd
                # Estimar probabilidade real baseada no histórico (simplificado)
                estimated_prob = self.estimate_win_probability(equipa_casa, equipa_fora)
                
                if estimated_prob > implied_prob:
                    # Calcular Kelly
                    kelly = (estimated_prob * odd - 1) / (odd - 1)
                    
                    if kelly > self.alerts_config['kelly_threshold']:
                        alerts.append({
                            'type': 'kelly_warning',
                            'severity': 'medium',
                            'title': '📊 Kelly Elevado',
                            'message': f'Kelly sugere {kelly:.1%} da banca',
                            'details': 'Valor sugerido pode ser muito alto para esta aposta',
                            'value': kelly,
                            'threshold': self.alerts_config['kelly_threshold']
                        })
                    
                    # Oportunidade de valor
                    if self.alerts_config['enabled_alerts']['value_opportunity']:
                        expected_value = (estimated_prob * odd) - 1
                        if expected_value > 0.1:  # 10% de valor esperado
                            alerts.append({
                                'type': 'value_opportunity',
                                'severity': 'low',
                                'title': '💎 Oportunidade de Valor',
                                'message': f'Valor esperado: +{expected_value:.1%}',
                                'details': 'Esta aposta pode ter valor positivo',
                                'value': expected_value,
                                'threshold': 0.1
                            })
            except Exception:
                pass  # Ignorar erros no cálculo de Kelly
            
        except Exception as e:
            print(f"Erro ao verificar alertas da aposta: {e}")
        
        return alerts
    
    def estimate_win_probability(self, equipa_casa: str, equipa_fora: str) -> float:
        """Estimar probabilidade de vitória baseada no histórico"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            
            # Buscar histórico das equipas
            query = """
                SELECT resultado 
                FROM apostas 
                WHERE (equipa_casa = ? OR equipa_fora = ? OR equipa_casa = ? OR equipa_fora = ?)
                AND resultado IN ('Ganha', 'Perdida')
                ORDER BY data_hora DESC 
                LIMIT 20
            """
            
            df = pd.read_sql_query(query, conn, params=[equipa_casa, equipa_casa, equipa_fora, equipa_fora])
            conn.close()
            
            if not df.empty:
                win_rate = (df['resultado'] == 'Ganha').mean()
                return max(0.1, min(0.9, win_rate))  # Limitar entre 10% e 90%
            
            return 0.5  # Probabilidade neutra se não há dados
            
        except Exception:
            return 0.5
    
    def dismiss_alert(self, alert_id: int):
        """Dispensar um alerta"""
        self.active_alerts = [alert for alert in self.active_alerts if alert.get('id') != alert_id]
    
    def get_active_alerts(self) -> List[Dict]:
        """Obter alertas ativos"""
        return self.active_alerts
    
    def get_alert_history(self, days: int = 7) -> List[Dict]:
        """Obter histórico de alertas"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [alert for alert in self.alert_history if alert.get('timestamp', datetime.now()) >= cutoff_date]
    
    def clear_old_alerts(self, hours: int = 24):
        """Limpar alertas antigos"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.active_alerts = [
            alert for alert in self.active_alerts 
            if alert.get('timestamp', datetime.now()) >= cutoff_time
        ]

class AlertMonitor:
    """Monitor de alertas em background"""
    
    def __init__(self, alert_system: AlertSystem, callback=None):
        self.alert_system = alert_system
        self.callback = callback
        self.running = False
        self.thread = None
    
    def start_monitoring(self):
        """Iniciar monitoramento"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Verificar alertas
                new_alerts = self.alert_system.check_all_alerts()
                
                # Chamar callback se há novos alertas
                if new_alerts and self.callback:
                    self.callback(new_alerts)
                
                # Limpar alertas antigos
                self.alert_system.clear_old_alerts()
                
                # Aguardar próxima verificação
                interval = self.alert_system.alerts_config.get('check_interval', 300)
                time.sleep(interval)
                
            except Exception as e:
                print(f"Erro no monitor de alertas: {e}")
                time.sleep(60)  # Aguardar 1 minuto em caso de erro

class AlertsInterface(ctk.CTkFrame):
    """Interface para gerenciamento de alertas"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.alert_system = AlertSystem(db)
        self.monitor = AlertMonitor(self.alert_system, self.on_new_alerts)
        
        self.setup_ui()
        self.load_alerts()
        
        # Iniciar monitoramento após um pequeno delay para garantir que a interface esteja pronta
        self.after(1000, self.start_monitoring)
    
    def start_monitoring(self):
        """Iniciar o monitoramento de alertas"""
        try:
            self.monitor.start_monitoring()
        except Exception as e:
            print(f"Erro ao iniciar monitor de alertas: {e}")
    
    def setup_ui(self):
        """Configurar interface"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="🔔 Sistema de Alertas Inteligentes",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Notebook para separar alertas e configurações
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba de Alertas Ativos
        self.notebook.add("Alertas Ativos")
        self.create_alerts_tab()
        
        # Aba de Configurações
        self.notebook.add("Configurações")
        self.create_config_tab()
        
        # Aba de Histórico
        self.notebook.add("Histórico")
        self.create_history_tab()
    
    def create_alerts_tab(self):
        """Criar aba de alertas ativos"""
        alerts_frame = self.notebook.tab("Alertas Ativos")
        
        # Botões de controle
        controls_frame = ctk.CTkFrame(alerts_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Atualizar",
            command=self.refresh_alerts,
            width=120
        )
        refresh_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️ Limpar Todos",
            command=self.clear_all_alerts,
            width=120
        )
        clear_btn.pack(side="left", padx=5)
        
        # Frame para lista de alertas
        self.alerts_list_frame = ctk.CTkScrollableFrame(alerts_frame)
        self.alerts_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_config_tab(self):
        """Criar aba de configurações"""
        config_frame = self.notebook.tab("Configurações")
        
        # Scroll frame para configurações
        scroll_frame = ctk.CTkScrollableFrame(config_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurações de limites
        limits_frame = ctk.CTkFrame(scroll_frame)
        limits_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            limits_frame,
            text="Limites de Alerta",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Criar campos de configuração
        self.config_vars = {}
        
        config_fields = [
            ('drawdown_threshold', 'Drawdown Máximo (%)', 'float'),
            ('losing_streak_threshold', 'Sequência de Perdas', 'int'),
            ('roi_threshold', 'ROI Mínimo (%)', 'float'),
            ('bankroll_threshold', 'Banca Mínima (%)', 'float'),
            ('odd_threshold', 'Odd Máxima', 'float'),
            ('kelly_threshold', 'Kelly Máximo (%)', 'float'),
            ('check_interval', 'Intervalo de Verificação (seg)', 'int')
        ]
        
        for key, label, var_type in config_fields:
            field_frame = ctk.CTkFrame(limits_frame)
            field_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(field_frame, text=label, width=200).pack(side="left", padx=10)
            
            if var_type == 'float':
                var = ctk.DoubleVar(value=self.alert_system.alerts_config.get(key, 0.0))
            else:
                var = ctk.IntVar(value=self.alert_system.alerts_config.get(key, 0))
            
            entry = ctk.CTkEntry(field_frame, textvariable=var, width=100)
            entry.pack(side="right", padx=10)
            
            self.config_vars[key] = var
        
        # Configurações de alertas habilitados
        enabled_frame = ctk.CTkFrame(scroll_frame)
        enabled_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            enabled_frame,
            text="Alertas Habilitados",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.enabled_vars = {}
        
        enabled_alerts = [
            ('drawdown', 'Alerta de Drawdown'),
            ('losing_streak', 'Sequência de Perdas'),
            ('roi_warning', 'Aviso de ROI Baixo'),
            ('bankroll_low', 'Banca Baixa'),
            ('high_risk_bet', 'Apostas de Alto Risco'),
            ('value_opportunity', 'Oportunidades de Valor'),
            ('kelly_warning', 'Aviso de Kelly'),
            ('performance_anomaly', 'Anomalias de Performance')
        ]
        
        for key, label in enabled_alerts:
            var = ctk.BooleanVar(
                value=self.alert_system.alerts_config['enabled_alerts'].get(key, True)
            )
            
            checkbox = ctk.CTkCheckBox(
                enabled_frame,
                text=label,
                variable=var
            )
            checkbox.pack(anchor="w", padx=20, pady=5)
            
            self.enabled_vars[key] = var
        
        # Botão para salvar configurações
        save_btn = ctk.CTkButton(
            scroll_frame,
            text="💾 Salvar Configurações",
            command=self.save_config,
            width=200,
            height=40
        )
        save_btn.pack(pady=20)
    
    def create_history_tab(self):
        """Criar aba de histórico"""
        history_frame = self.notebook.tab("Histórico")
        
        # Controles de filtro
        filter_frame = ctk.CTkFrame(history_frame)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Últimos:").pack(side="left", padx=10)
        
        self.history_days = ctk.CTkComboBox(
            filter_frame,
            values=["1 dia", "3 dias", "7 dias", "30 dias"],
            width=100
        )
        self.history_days.set("7 dias")
        self.history_days.pack(side="left", padx=5)
        
        refresh_history_btn = ctk.CTkButton(
            filter_frame,
            text="🔄 Atualizar",
            command=self.refresh_history,
            width=100
        )
        refresh_history_btn.pack(side="left", padx=10)
        
        # Lista de histórico
        self.history_list_frame = ctk.CTkScrollableFrame(history_frame)
        self.history_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_alerts(self):
        """Carregar alertas ativos"""
        # Limpar lista atual
        for widget in self.alerts_list_frame.winfo_children():
            widget.destroy()
        
        active_alerts = self.alert_system.get_active_alerts()
        
        if not active_alerts:
            no_alerts_label = ctk.CTkLabel(
                self.alerts_list_frame,
                text="✅ Nenhum alerta ativo",
                font=ctk.CTkFont(size=16)
            )
            no_alerts_label.pack(pady=50)
            return
        
        # Ordenar por severidade
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        active_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 2))
        
        for alert in active_alerts:
            self.create_alert_widget(alert)
    
    def create_alert_widget(self, alert: Dict):
        """Criar widget para um alerta"""
        # Cores por severidade
        colors = {
            'high': ("#ff4444", "#ffeeee"),
            'medium': ("#ff8800", "#fff4e6"),
            'low': ("#4488ff", "#eef4ff")
        }
        
        severity = alert.get('severity', 'low')
        border_color, bg_color = colors.get(severity, colors['low'])
        
        alert_frame = ctk.CTkFrame(
            self.alerts_list_frame,
            border_width=2,
            border_color=border_color
        )
        alert_frame.pack(fill="x", padx=5, pady=5)
        
        # Cabeçalho do alerta
        header_frame = ctk.CTkFrame(alert_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=alert.get('title', 'Alerta'),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left")
        
        # Timestamp
        timestamp = alert.get('timestamp', datetime.now())
        time_label = ctk.CTkLabel(
            header_frame,
            text=timestamp.strftime("%H:%M"),
            font=ctk.CTkFont(size=10)
        )
        time_label.pack(side="right")
        
        # Botão de dispensar
        dismiss_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            command=lambda: self.dismiss_alert(alert.get('id')),
            width=30,
            height=30
        )
        dismiss_btn.pack(side="right", padx=5)
        
        # Mensagem do alerta
        message_label = ctk.CTkLabel(
            alert_frame,
            text=alert.get('message', ''),
            font=ctk.CTkFont(size=12)
        )
        message_label.pack(anchor="w", padx=15, pady=2)
        
        # Detalhes (se houver)
        if alert.get('details'):
            details_label = ctk.CTkLabel(
                alert_frame,
                text=alert.get('details'),
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            details_label.pack(anchor="w", padx=15, pady=2)
    
    def refresh_alerts(self):
        """Atualizar lista de alertas"""
        # Verificar novos alertas
        self.alert_system.check_all_alerts()
        
        # Recarregar interface
        self.load_alerts()
    
    def clear_all_alerts(self):
        """Limpar todos os alertas"""
        self.alert_system.active_alerts.clear()
        self.load_alerts()
    
    def dismiss_alert(self, alert_id: int):
        """Dispensar um alerta específico"""
        self.alert_system.dismiss_alert(alert_id)
        self.load_alerts()
    
    def save_config(self):
        """Salvar configurações"""
        try:
            # Atualizar configurações de limites
            for key, var in self.config_vars.items():
                self.alert_system.alerts_config[key] = var.get()
            
            # Atualizar configurações de alertas habilitados
            for key, var in self.enabled_vars.items():
                self.alert_system.alerts_config['enabled_alerts'][key] = var.get()
            
            # Salvar no arquivo
            self.alert_system.save_alerts_config()
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def refresh_history(self):
        """Atualizar histórico de alertas"""
        # Limpar lista atual
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
        
        # Obter número de dias
        days_text = self.history_days.get()
        days = int(days_text.split()[0])
        
        history = self.alert_system.get_alert_history(days)
        
        if not history:
            no_history_label = ctk.CTkLabel(
                self.history_list_frame,
                text="📝 Nenhum alerta no período selecionado",
                font=ctk.CTkFont(size=16)
            )
            no_history_label.pack(pady=50)
            return
        
        # Ordenar por timestamp (mais recente primeiro)
        history.sort(key=lambda x: x.get('timestamp', datetime.now()), reverse=True)
        
        for alert in history:
            self.create_history_widget(alert)
    
    def create_history_widget(self, alert: Dict):
        """Criar widget para histórico de alerta"""
        history_frame = ctk.CTkFrame(self.history_list_frame)
        history_frame.pack(fill="x", padx=5, pady=2)
        
        # Timestamp
        timestamp = alert.get('timestamp', datetime.now())
        time_label = ctk.CTkLabel(
            history_frame,
            text=timestamp.strftime("%d/%m %H:%M"),
            font=ctk.CTkFont(size=10),
            width=80
        )
        time_label.pack(side="left", padx=5)
        
        # Título e mensagem
        content_frame = ctk.CTkFrame(history_frame)
        content_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text=alert.get('title', 'Alerta'),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(anchor="w")
        
        message_label = ctk.CTkLabel(
            content_frame,
            text=alert.get('message', ''),
            font=ctk.CTkFont(size=10)
        )
        message_label.pack(anchor="w")
        
        # Indicador de severidade
        severity_colors = {
            'high': "#ff4444",
            'medium': "#ff8800",
            'low': "#4488ff"
        }
        
        severity = alert.get('severity', 'low')
        severity_indicator = ctk.CTkFrame(
            history_frame,
            width=10,
            height=40,
            fg_color=severity_colors.get(severity, "#4488ff")
        )
        severity_indicator.pack(side="right", padx=5)
    
    def on_new_alerts(self, new_alerts: List[Dict]):
        """Callback para novos alertas"""
        # Atualizar interface na thread principal
        self.after(0, self.load_alerts)
        
        # Mostrar notificação para alertas de alta severidade
        high_severity_alerts = [alert for alert in new_alerts if alert.get('severity') == 'high']
        
        if high_severity_alerts:
            self.after(0, lambda: self.show_alert_notification(high_severity_alerts))
    
    def show_alert_notification(self, alerts: List[Dict]):
        """Mostrar notificação de alertas importantes"""
        if len(alerts) == 1:
            alert = alerts[0]
            messagebox.showwarning(
                alert.get('title', 'Alerta'),
                alert.get('message', '') + '\n\n' + alert.get('details', '')
            )
        else:
            message = f"Foram detectados {len(alerts)} alertas importantes:\n\n"
            for alert in alerts[:3]:  # Mostrar apenas os primeiros 3
                message += f"• {alert.get('title', 'Alerta')}: {alert.get('message', '')}\n"
            
            if len(alerts) > 3:
                message += f"\n... e mais {len(alerts) - 3} alertas"
            
            messagebox.showwarning("Múltiplos Alertas", message)
    
    def __del__(self):
        """Destructor para parar o monitor"""
        if hasattr(self, 'monitor'):
            self.monitor.stop_monitoring()

# Função para integrar na aplicação principal
def create_alerts_tab(parent, db: DatabaseManager):
    """Criar aba de alertas na aplicação principal"""
    return AlertsInterface(parent, db)

# Função para verificar alertas de uma aposta
def check_bet_alerts(db: DatabaseManager, equipa_casa: str, equipa_fora: str, odd: float, valor: float) -> List[Dict]:
    """Verificar alertas para uma aposta específica"""
    alert_system = AlertSystem(db)
    return alert_system.check_bet_alert(equipa_casa, equipa_fora, odd, valor)