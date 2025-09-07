#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Comportamento de Risco
Versão 1.2 - Inteligência e Automação

Este módulo implementa:
- Detecção de comportamentos de risco
- Análise de sequências de perdas
- Monitoramento de apostas altas após perdas
- Alertas e recomendações de gestão de risco
- Análise psicológica do apostador
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from enum import Enum
from traducoes import t

class RiskLevel(Enum):
    """Níveis de risco"""
    BAIXO = "Baixo"
    MODERADO = "Moderado"
    ALTO = "Alto"
    CRITICO = "Crítico"

class AlertType(Enum):
    """Tipos de alerta"""
    SEQUENCIA_PERDAS = "Sequência de Perdas"
    APOSTA_ALTA_POS_PERDA = "Aposta Alta Após Perda"
    AUMENTO_PROGRESSIVO = "Aumento Progressivo de Stakes"
    PERSEGUICAO_PERDAS = "Perseguição de Perdas"
    APOSTAS_IMPULSIVAS = "Apostas Impulsivas"
    GESTAO_BANCA_INADEQUADA = "Gestão de Banca Inadequada"
    ODDS_EXCESSIVAS = "Apostas em Odds Excessivas"

@dataclass
class RiskAlert:
    """Alerta de risco"""
    type: AlertType
    level: RiskLevel
    message: str
    recommendation: str
    data: Dict[str, Any]
    timestamp: str
    severity_score: float

@dataclass
class RiskMetrics:
    """Métricas de risco"""
    current_losing_streak: int
    max_losing_streak: int
    avg_stake_after_loss: float
    avg_stake_normal: float
    stake_increase_ratio: float
    impulsive_bets_count: int
    high_risk_bets_count: int
    bankroll_risk_percentage: float
    emotional_betting_score: float
    discipline_score: float
    overall_risk_score: float
    risk_level: RiskLevel

class ComportamentoRisco:
    """Analisador de comportamento de risco"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.risk_thresholds = {
            'max_losing_streak': 5,
            'stake_increase_ratio': 2.0,
            'high_odds_threshold': 5.0,
            'bankroll_risk_percentage': 10.0,
            'impulsive_time_threshold': 300  # 5 minutos
        }
    
    def init_database(self):
        """Inicializa tabelas para análise de risco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de alertas de risco
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    data TEXT,
                    timestamp TEXT NOT NULL,
                    severity_score REAL NOT NULL,
                    acknowledged BOOLEAN DEFAULT 0
                )
            """)
            
            # Tabela de configurações de risco
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT UNIQUE NOT NULL,
                    setting_value REAL NOT NULL,
                    description TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao inicializar base de dados de risco: {e}")
    
    def analyze_risk_behavior(self, days_back: int = 30) -> Tuple[RiskMetrics, List[RiskAlert]]:
        """Analisa comportamento de risco"""
        try:
            df = self._load_betting_data(days_back)
            
            if df.empty:
                return self._create_empty_metrics(), []
            
            # Calcular métricas de risco
            metrics = self._calculate_risk_metrics(df)
            
            # Detectar alertas
            alerts = self._detect_risk_alerts(df, metrics)
            
            # Salvar alertas na base de dados
            self._save_alerts(alerts)
            
            return metrics, alerts
            
        except Exception as e:
            print(f"Erro na análise de comportamento de risco: {e}")
            return self._create_empty_metrics(), []
    
    def _load_betting_data(self, days_back: int) -> pd.DataFrame:
        """Carrega dados de apostas para análise"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
                SELECT 
                    data,
                    hora,
                    valor_aposta,
                    odd,
                    resultado,
                    lucro_prejuizo,
                    tipo_aposta,
                    competicao
                FROM apostas 
                WHERE data >= ? AND data <= ?
                ORDER BY data ASC, hora ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ))
            
            conn.close()
            
            if not df.empty:
                # Preparar dados
                df['datetime'] = pd.to_datetime(df['data'] + ' ' + df['hora'].fillna('12:00'))
                df['won'] = df['resultado'] == 'Ganhou'
                df['lost'] = df['resultado'] == 'Perdeu'
                
                # Calcular diferenças de tempo entre apostas
                df['time_diff'] = df['datetime'].diff().dt.total_seconds().fillna(0)
                
                # Identificar sequências
                df['losing_streak'] = self._calculate_losing_streaks(df)
                df['winning_streak'] = self._calculate_winning_streaks(df)
                
            return df
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _calculate_risk_metrics(self, df: pd.DataFrame) -> RiskMetrics:
        """Calcula métricas de risco"""
        if df.empty:
            return self._create_empty_metrics()
        
        # Sequências de perdas
        current_losing_streak = self._get_current_losing_streak(df)
        max_losing_streak = df['losing_streak'].max()
        
        # Análise de stakes após perdas
        stakes_after_loss = self._analyze_stakes_after_losses(df)
        avg_stake_after_loss = stakes_after_loss['avg_stake_after_loss']
        avg_stake_normal = stakes_after_loss['avg_stake_normal']
        stake_increase_ratio = avg_stake_after_loss / avg_stake_normal if avg_stake_normal > 0 else 1.0
        
        # Apostas impulsivas (feitas muito rapidamente após uma perda)
        impulsive_bets_count = self._count_impulsive_bets(df)
        
        # Apostas de alto risco (odds muito altas)
        high_risk_bets_count = len(df[df['odd'] > self.risk_thresholds['high_odds_threshold']])
        
        # Percentagem de risco da banca
        bankroll_risk_percentage = self._calculate_bankroll_risk(df)
        
        # Scores comportamentais
        emotional_betting_score = self._calculate_emotional_betting_score(df)
        discipline_score = self._calculate_discipline_score(df)
        
        # Score geral de risco
        overall_risk_score = self._calculate_overall_risk_score(
            current_losing_streak, stake_increase_ratio, impulsive_bets_count,
            high_risk_bets_count, emotional_betting_score, discipline_score
        )
        
        # Nível de risco
        risk_level = self._determine_risk_level(overall_risk_score)
        
        return RiskMetrics(
            current_losing_streak=current_losing_streak,
            max_losing_streak=max_losing_streak,
            avg_stake_after_loss=avg_stake_after_loss,
            avg_stake_normal=avg_stake_normal,
            stake_increase_ratio=stake_increase_ratio,
            impulsive_bets_count=impulsive_bets_count,
            high_risk_bets_count=high_risk_bets_count,
            bankroll_risk_percentage=bankroll_risk_percentage,
            emotional_betting_score=emotional_betting_score,
            discipline_score=discipline_score,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level
        )
    
    def _detect_risk_alerts(self, df: pd.DataFrame, metrics: RiskMetrics) -> List[RiskAlert]:
        """Detecta alertas de risco"""
        alerts = []
        
        # Alerta: Sequência de perdas
        if metrics.current_losing_streak >= self.risk_thresholds['max_losing_streak']:
            alerts.append(RiskAlert(
                type=AlertType.SEQUENCIA_PERDAS,
                level=RiskLevel.ALTO if metrics.current_losing_streak >= 7 else RiskLevel.MODERADO,
                message=f"Sequência atual de {metrics.current_losing_streak} perdas consecutivas",
                recommendation="Considere fazer uma pausa e reavaliar a estratégia",
                data={'losing_streak': metrics.current_losing_streak},
                timestamp=datetime.now().isoformat(),
                severity_score=min(10.0, metrics.current_losing_streak * 1.5)
            ))
        
        # Alerta: Aumento de stake após perdas
        if metrics.stake_increase_ratio >= self.risk_thresholds['stake_increase_ratio']:
            alerts.append(RiskAlert(
                type=AlertType.APOSTA_ALTA_POS_PERDA,
                level=RiskLevel.ALTO if metrics.stake_increase_ratio >= 3.0 else RiskLevel.MODERADO,
                message=f"Stakes {metrics.stake_increase_ratio:.1f}x maiores após perdas",
                recommendation="Mantenha stakes consistentes independentemente dos resultados anteriores",
                data={'stake_ratio': metrics.stake_increase_ratio},
                timestamp=datetime.now().isoformat(),
                severity_score=min(10.0, metrics.stake_increase_ratio * 2)
            ))
        
        # Alerta: Apostas impulsivas
        if metrics.impulsive_bets_count > 3:
            alerts.append(RiskAlert(
                type=AlertType.APOSTAS_IMPULSIVAS,
                level=RiskLevel.MODERADO,
                message=f"{metrics.impulsive_bets_count} apostas feitas impulsivamente",
                recommendation="Implemente um período de reflexão antes de apostar",
                data={'impulsive_count': metrics.impulsive_bets_count},
                timestamp=datetime.now().isoformat(),
                severity_score=min(10.0, metrics.impulsive_bets_count * 1.2)
            ))
        
        # Alerta: Gestão de banca inadequada
        if metrics.bankroll_risk_percentage > self.risk_thresholds['bankroll_risk_percentage']:
            alerts.append(RiskAlert(
                type=AlertType.GESTAO_BANCA_INADEQUADA,
                level=RiskLevel.CRITICO if metrics.bankroll_risk_percentage > 20 else RiskLevel.ALTO,
                message=f"Risco de {metrics.bankroll_risk_percentage:.1f}% da banca por aposta",
                recommendation="Reduza o tamanho das apostas para máximo 5% da banca",
                data={'bankroll_risk': metrics.bankroll_risk_percentage},
                timestamp=datetime.now().isoformat(),
                severity_score=min(10.0, metrics.bankroll_risk_percentage / 2)
            ))
        
        # Alerta: Odds excessivas
        if metrics.high_risk_bets_count > len(df) * 0.3:  # Mais de 30% das apostas em odds altas
            alerts.append(RiskAlert(
                type=AlertType.ODDS_EXCESSIVAS,
                level=RiskLevel.MODERADO,
                message=f"{metrics.high_risk_bets_count} apostas em odds muito altas",
                recommendation="Equilibre o portfólio com apostas de menor risco",
                data={'high_odds_count': metrics.high_risk_bets_count},
                timestamp=datetime.now().isoformat(),
                severity_score=min(10.0, (metrics.high_risk_bets_count / len(df)) * 10)
            ))
        
        # Alerta: Score emocional alto
        if metrics.emotional_betting_score > 7.0:
            alerts.append(RiskAlert(
                type=AlertType.PERSEGUICAO_PERDAS,
                level=RiskLevel.ALTO,
                message="Padrão de apostas emocionais detectado",
                recommendation="Implemente regras rígidas de gestão de risco e considere apostar apenas com a mente fria",
                data={'emotional_score': metrics.emotional_betting_score},
                timestamp=datetime.now().isoformat(),
                severity_score=metrics.emotional_betting_score
            ))
        
        return alerts
    
    def _calculate_losing_streaks(self, df: pd.DataFrame) -> pd.Series:
        """Calcula sequências de perdas"""
        streaks = []
        current_streak = 0
        
        for _, row in df.iterrows():
            if row['lost']:
                current_streak += 1
            else:
                current_streak = 0
            streaks.append(current_streak)
        
        return pd.Series(streaks)
    
    def _calculate_winning_streaks(self, df: pd.DataFrame) -> pd.Series:
        """Calcula sequências de vitórias"""
        streaks = []
        current_streak = 0
        
        for _, row in df.iterrows():
            if row['won']:
                current_streak += 1
            else:
                current_streak = 0
            streaks.append(current_streak)
        
        return pd.Series(streaks)
    
    def _get_current_losing_streak(self, df: pd.DataFrame) -> int:
        """Obtém a sequência atual de perdas"""
        if df.empty:
            return 0
        
        current_streak = 0
        for i in range(len(df) - 1, -1, -1):
            if df.iloc[i]['lost']:
                current_streak += 1
            else:
                break
        
        return current_streak
    
    def _analyze_stakes_after_losses(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analisa stakes após perdas"""
        if len(df) < 2:
            return {'avg_stake_after_loss': 0, 'avg_stake_normal': 0}
        
        stakes_after_loss = []
        normal_stakes = []
        
        for i in range(1, len(df)):
            current_stake = df.iloc[i]['valor_aposta']
            previous_result = df.iloc[i-1]['lost']
            
            if previous_result:
                stakes_after_loss.append(current_stake)
            else:
                normal_stakes.append(current_stake)
        
        avg_stake_after_loss = np.mean(stakes_after_loss) if stakes_after_loss else 0
        avg_stake_normal = np.mean(normal_stakes) if normal_stakes else 0
        
        return {
            'avg_stake_after_loss': avg_stake_after_loss,
            'avg_stake_normal': avg_stake_normal
        }
    
    def _count_impulsive_bets(self, df: pd.DataFrame) -> int:
        """Conta apostas impulsivas (feitas rapidamente após uma perda)"""
        if len(df) < 2:
            return 0
        
        impulsive_count = 0
        threshold = self.risk_thresholds['impulsive_time_threshold']
        
        for i in range(1, len(df)):
            if (df.iloc[i-1]['lost'] and 
                df.iloc[i]['time_diff'] < threshold and 
                df.iloc[i]['time_diff'] > 0):
                impulsive_count += 1
        
        return impulsive_count
    
    def _calculate_bankroll_risk(self, df: pd.DataFrame) -> float:
        """Calcula percentagem de risco da banca"""
        if df.empty:
            return 0.0
        
        # Estimar banca baseada no maior stake
        max_stake = df['valor_aposta'].max()
        avg_stake = df['valor_aposta'].mean()
        
        # Assumir que a banca é pelo menos 20x o maior stake
        estimated_bankroll = max(max_stake * 20, avg_stake * 50)
        
        # Calcular percentagem de risco
        risk_percentage = (max_stake / estimated_bankroll) * 100
        
        return risk_percentage
    
    def _calculate_emotional_betting_score(self, df: pd.DataFrame) -> float:
        """Calcula score de apostas emocionais (0-10)"""
        if len(df) < 5:
            return 0.0
        
        score = 0.0
        
        # Fator 1: Variação de stakes
        stake_cv = df['valor_aposta'].std() / df['valor_aposta'].mean()
        score += min(3.0, stake_cv * 2)
        
        # Fator 2: Apostas após perdas
        stakes_analysis = self._analyze_stakes_after_losses(df)
        if stakes_analysis['avg_stake_normal'] > 0:
            ratio = stakes_analysis['avg_stake_after_loss'] / stakes_analysis['avg_stake_normal']
            score += min(3.0, (ratio - 1) * 2)
        
        # Fator 3: Frequência de apostas impulsivas
        impulsive_ratio = self._count_impulsive_bets(df) / len(df)
        score += min(2.0, impulsive_ratio * 10)
        
        # Fator 4: Apostas em odds extremas após perdas
        extreme_odds_after_loss = 0
        for i in range(1, len(df)):
            if df.iloc[i-1]['lost'] and df.iloc[i]['odd'] > 5.0:
                extreme_odds_after_loss += 1
        
        score += min(2.0, (extreme_odds_after_loss / len(df)) * 10)
        
        return min(10.0, score)
    
    def _calculate_discipline_score(self, df: pd.DataFrame) -> float:
        """Calcula score de disciplina (0-10)"""
        if len(df) < 5:
            return 5.0  # Score neutro para poucos dados
        
        score = 10.0
        
        # Penalizar variação excessiva de stakes
        stake_cv = df['valor_aposta'].std() / df['valor_aposta'].mean()
        score -= min(3.0, stake_cv * 2)
        
        # Penalizar aumento de stakes após perdas
        stakes_analysis = self._analyze_stakes_after_losses(df)
        if stakes_analysis['avg_stake_normal'] > 0:
            ratio = stakes_analysis['avg_stake_after_loss'] / stakes_analysis['avg_stake_normal']
            score -= min(3.0, max(0, ratio - 1) * 2)
        
        # Penalizar apostas impulsivas
        impulsive_ratio = self._count_impulsive_bets(df) / len(df)
        score -= min(2.0, impulsive_ratio * 10)
        
        # Penalizar sequências longas de perdas (indica falta de pausa)
        max_losing_streak = df['losing_streak'].max()
        score -= min(2.0, max(0, max_losing_streak - 3) * 0.5)
        
        return max(0.0, score)
    
    def _calculate_overall_risk_score(self, losing_streak: int, stake_ratio: float, 
                                    impulsive_count: int, high_risk_count: int,
                                    emotional_score: float, discipline_score: float) -> float:
        """Calcula score geral de risco (0-10)"""
        score = 0.0
        
        # Sequência de perdas (peso: 20%)
        score += min(2.0, losing_streak * 0.3)
        
        # Ratio de stakes (peso: 25%)
        score += min(2.5, max(0, stake_ratio - 1) * 1.5)
        
        # Apostas impulsivas (peso: 15%)
        score += min(1.5, impulsive_count * 0.3)
        
        # Apostas de alto risco (peso: 10%)
        score += min(1.0, high_risk_count * 0.1)
        
        # Score emocional (peso: 20%)
        score += emotional_score * 0.2
        
        # Score de disciplina invertido (peso: 10%)
        score += (10 - discipline_score) * 0.1
        
        return min(10.0, score)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determina nível de risco baseado no score"""
        if risk_score >= 8.0:
            return RiskLevel.CRITICO
        elif risk_score >= 6.0:
            return RiskLevel.ALTO
        elif risk_score >= 3.0:
            return RiskLevel.MODERADO
        else:
            return RiskLevel.BAIXO
    
    def _save_alerts(self, alerts: List[RiskAlert]):
        """Salva alertas na base de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for alert in alerts:
                cursor.execute("""
                    INSERT INTO risk_alerts 
                    (alert_type, risk_level, message, recommendation, data, timestamp, severity_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.type.value,
                    alert.level.value,
                    alert.message,
                    alert.recommendation,
                    str(alert.data),
                    alert.timestamp,
                    alert.severity_score
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao salvar alertas: {e}")
    
    def get_recent_alerts(self, days_back: int = 7, acknowledged: bool = False) -> List[Dict[str, Any]]:
        """Obtém alertas recentes"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            query = """
                SELECT * FROM risk_alerts 
                WHERE timestamp >= ? AND acknowledged = ?
                ORDER BY timestamp DESC, severity_score DESC
            """
            
            df = pd.read_sql_query(query, conn, params=(start_date, acknowledged))
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Erro ao obter alertas: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Marca alerta como reconhecido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE risk_alerts SET acknowledged = 1 WHERE id = ?",
                (alert_id,)
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao reconhecer alerta: {e}")
            return False
    
    def plot_risk_analysis(self, days_back: int = 30, save_path: Optional[str] = None):
        """Cria visualizações da análise de risco"""
        try:
            df = self._load_betting_data(days_back)
            metrics, alerts = self.analyze_risk_behavior(days_back)
            
            if df.empty:
                return None
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise de Comportamento de Risco', fontsize=16, fontweight='bold')
            
            # 1. Evolução dos stakes
            ax1 = axes[0, 0]
            ax1.plot(df.index, df['valor_aposta'], marker='o', linewidth=1, markersize=4)
            
            # Destacar apostas após perdas
            for i in range(1, len(df)):
                if df.iloc[i-1]['lost']:
                    ax1.scatter(i, df.iloc[i]['valor_aposta'], color='red', s=50, alpha=0.7)
            
            ax1.set_title('Evolução dos Stakes')
            ax1.set_ylabel('Valor da Aposta (€)')
            ax1.set_xlabel('Aposta #')
            ax1.grid(True, alpha=0.3)
            
            # 2. Sequências de perdas
            ax2 = axes[0, 1]
            ax2.plot(df.index, df['losing_streak'], color='red', linewidth=2)
            ax2.fill_between(df.index, df['losing_streak'], alpha=0.3, color='red')
            ax2.axhline(y=self.risk_thresholds['max_losing_streak'], 
                       color='orange', linestyle='--', label='Threshold de Risco')
            ax2.set_title('Sequências de Perdas')
            ax2.set_ylabel('Perdas Consecutivas')
            ax2.set_xlabel('Aposta #')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. Distribuição de odds
            ax3 = axes[1, 0]
            bins = [1, 1.5, 2, 3, 5, 10, float('inf')]
            labels = ['1.0-1.5', '1.5-2.0', '2.0-3.0', '3.0-5.0', '5.0-10.0', '10.0+']
            
            odds_counts = pd.cut(df['odd'], bins=bins, labels=labels).value_counts()
            
            colors = ['green', 'lightgreen', 'yellow', 'orange', 'red', 'darkred']
            bars = ax3.bar(odds_counts.index, odds_counts.values, color=colors[:len(odds_counts)])
            ax3.set_title('Distribuição de Odds')
            ax3.set_ylabel('Número de Apostas')
            ax3.set_xlabel('Faixa de Odds')
            plt.setp(ax3.get_xticklabels(), rotation=45)
            
            # 4. Métricas de risco
            ax4 = axes[1, 1]
            risk_metrics = {
                'Score Geral': metrics.overall_risk_score,
                'Score Emocional': metrics.emotional_betting_score,
                'Score Disciplina': metrics.discipline_score,
                'Ratio Stakes': min(10, metrics.stake_increase_ratio * 2)
            }
            
            bars = ax4.bar(risk_metrics.keys(), risk_metrics.values(), 
                          color=['red', 'orange', 'green', 'blue'])
            ax4.set_title('Métricas de Risco')
            ax4.set_ylabel('Score (0-10)')
            ax4.set_ylim(0, 10)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, risk_metrics.values()):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.setp(ax4.get_xticklabels(), rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            print(f"Erro ao criar gráficos: {e}")
            return None
    
    def generate_risk_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Gera relatório completo de risco"""
        try:
            metrics, alerts = self.analyze_risk_behavior(days_back)
            recent_alerts = self.get_recent_alerts(days_back)
            
            # Recomendações baseadas no nível de risco
            recommendations = self._generate_risk_recommendations(metrics, alerts)
            
            return {
                'analysis_period': f'{days_back} dias',
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'risk_level': metrics.risk_level.value,
                'overall_risk_score': metrics.overall_risk_score,
                'metrics': {
                    'current_losing_streak': metrics.current_losing_streak,
                    'max_losing_streak': metrics.max_losing_streak,
                    'stake_increase_ratio': metrics.stake_increase_ratio,
                    'impulsive_bets_count': metrics.impulsive_bets_count,
                    'high_risk_bets_count': metrics.high_risk_bets_count,
                    'emotional_betting_score': metrics.emotional_betting_score,
                    'discipline_score': metrics.discipline_score
                },
                'active_alerts': len([a for a in recent_alerts if not a['acknowledged']]),
                'total_alerts': len(recent_alerts),
                'critical_alerts': len([a for a in recent_alerts if a['risk_level'] == 'Crítico']),
                'recommendations': recommendations,
                'alerts': recent_alerts
            }
            
        except Exception as e:
            return {'error': f'Erro ao gerar relatório: {str(e)}'}
    
    def _generate_risk_recommendations(self, metrics: RiskMetrics, alerts: List[RiskAlert]) -> List[str]:
        """Gera recomendações baseadas na análise de risco"""
        recommendations = []
        
        if metrics.risk_level == RiskLevel.CRITICO:
            recommendations.append("🚨 PARE IMEDIATAMENTE de apostar e procure ajuda profissional")
            recommendations.append("Implemente um período de pausa obrigatório de pelo menos 1 semana")
        
        elif metrics.risk_level == RiskLevel.ALTO:
            recommendations.append("⚠️ Reduza significativamente o tamanho das apostas")
            recommendations.append("Implemente regras rígidas de gestão de banca")
            recommendations.append("Considere fazer uma pausa de alguns dias")
        
        elif metrics.risk_level == RiskLevel.MODERADO:
            recommendations.append("⚡ Revise e ajuste a sua estratégia de apostas")
            recommendations.append("Mantenha stakes consistentes")
            recommendations.append("Evite apostar após perdas consecutivas")
        
        else:
            recommendations.append("✅ Continue com a estratégia atual")
            recommendations.append("Mantenha a disciplina e consistência")
        
        # Recomendações específicas baseadas em alertas
        for alert in alerts:
            if alert.type == AlertType.SEQUENCIA_PERDAS:
                recommendations.append("Implemente uma regra de pausa após 3 perdas consecutivas")
            elif alert.type == AlertType.APOSTA_ALTA_POS_PERDA:
                recommendations.append("Nunca aumente stakes após uma perda")
            elif alert.type == AlertType.APOSTAS_IMPULSIVAS:
                recommendations.append("Aguarde pelo menos 30 minutos antes de fazer a próxima aposta")
        
        return list(set(recommendations))  # Remover duplicatas
    
    def get_recommendations(self, days_back: int = 30) -> List[str]:
        """Obter recomendações de gestão de risco"""
        try:
            metrics, alerts = self.analyze_risk_behavior(days_back)
            return self._generate_risk_recommendations(metrics, alerts)
        except Exception as e:
            print(f"Erro ao obter recomendações: {e}")
            return ["Erro ao gerar recomendações. Verifique os dados."]

    def get_risk_alerts(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Obter alertas de risco formatados"""
        try:
            _, alerts = self.analyze_risk_behavior(days_back)
            formatted_alerts = []
            
            for alert in alerts:
                formatted_alerts.append({
                    'tipo': alert.type.value,
                    'nivel': alert.level.value,
                    'mensagem': alert.message,
                    'recomendacao': alert.recommendation,
                    'timestamp': alert.timestamp,
                    'severity_score': alert.severity_score
                })
            
            return formatted_alerts
        except Exception as e:
            print(f"Erro ao obter alertas de risco: {e}")
            return []

    def _create_empty_metrics(self) -> RiskMetrics:
        """Cria métricas vazias"""
        return RiskMetrics(
            current_losing_streak=0,
            max_losing_streak=0,
            avg_stake_after_loss=0.0,
            avg_stake_normal=0.0,
            stake_increase_ratio=1.0,
            impulsive_bets_count=0,
            high_risk_bets_count=0,
            bankroll_risk_percentage=0.0,
            emotional_betting_score=0.0,
            discipline_score=10.0,
            overall_risk_score=0.0,
            risk_level=RiskLevel.BAIXO
        )

if __name__ == "__main__":
    analyzer = ComportamentoRisco()
    analyzer.init_database()
    
    # Analisar comportamento de risco
    metrics, alerts = analyzer.analyze_risk_behavior(days_back=30)
    
    print("=== ANÁLISE DE COMPORTAMENTO DE RISCO ===")
    print(f"Nível de Risco: {metrics.risk_level.value}")
    print(f"Score Geral: {metrics.overall_risk_score:.1f}/10")
    print(f"Sequência Atual de Perdas: {metrics.current_losing_streak}")
    print(f"Ratio de Stakes após Perdas: {metrics.stake_increase_ratio:.1f}x")
    print(f"Score Emocional: {metrics.emotional_betting_score:.1f}/10")
    print(f"Score de Disciplina: {metrics.discipline_score:.1f}/10")
    
    if alerts:
        print(f"\n=== ALERTAS ATIVOS ({len(alerts)}) ===")
        for alert in alerts:
            print(f"🚨 {alert.type.value} - {alert.level.value}")
            print(f"   {alert.message}")
            print(f"   Recomendação: {alert.recommendation}")
            print()
    
    # Gerar relatório
    report = analyzer.generate_risk_report(30)
    if 'error' not in report:
        print(f"\n=== RECOMENDAÇÕES ===")
        for rec in report['recommendations']:
            print(f"• {rec}")
    
    # Criar gráficos
    fig = analyzer.plot_risk_analysis(30)
    if fig:
        plt.show()