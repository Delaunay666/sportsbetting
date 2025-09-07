#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tipster Tracker - Gestão e Estatísticas de Tipsters
Versão 1.2 - Inteligência e Automação

Este módulo implementa:
- Registo e gestão de tipsters
- Estatísticas detalhadas por fonte
- Ranking e comparação de performance
- Análise de tendências
- Recomendações de seguimento
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, asdict
import json
from traducoes import t

@dataclass
class TipsterStats:
    """Estatísticas de um tipster"""
    name: str
    total_tips: int
    wins: int
    losses: int
    win_rate: float
    total_stake: float
    total_profit: float
    roi: float
    avg_odd: float
    max_win_streak: int
    max_loss_streak: int
    current_streak: int
    streak_type: str  # 'win' ou 'loss'
    last_tip_date: str
    active_days: int
    tips_per_day: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    consistency_score: float
    risk_level: str
    recommendation: str

@dataclass
class TipsterComparison:
    """Comparação entre tipsters"""
    tipster1: str
    tipster2: str
    better_roi: str
    better_winrate: str
    better_consistency: str
    overall_winner: str
    recommendation: str

class TipsterTracker:
    """Sistema de tracking de tipsters"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.init_tipster_tables()
    
    def init_tipster_tables(self):
        """Inicializa tabelas específicas para tipsters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de tipsters
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tipsters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    website TEXT,
                    telegram TEXT,
                    especialidade TEXT,
                    data_registo TEXT NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    notas TEXT
                )
            """)
            
            # Verificar se a coluna tipster existe na tabela apostas
            cursor.execute("PRAGMA table_info(apostas)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'tipster' not in columns:
                cursor.execute("ALTER TABLE apostas ADD COLUMN tipster TEXT DEFAULT 'Próprio'")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao inicializar tabelas de tipsters: {e}")
    
    def add_tipster(self, nome: str, descricao: str = "", website: str = "", 
                   telegram: str = "", especialidade: str = "", notas: str = "") -> bool:
        """Adiciona um novo tipster"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tipsters (nome, descricao, website, telegram, especialidade, data_registo, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, descricao, website, telegram, especialidade, 
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notas))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            return False  # Tipster já existe
        except Exception as e:
            print(f"Erro ao adicionar tipster: {e}")
            return False
    
    def get_tipsters(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obtém lista de tipsters"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = "SELECT * FROM tipsters"
            if active_only:
                query += " WHERE ativo = 1"
            query += " ORDER BY nome"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Erro ao obter tipsters: {e}")
            return []
    
    def update_tipster(self, tipster_id: int, **kwargs) -> bool:
        """Atualiza informações de um tipster"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query dinamicamente
            fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['nome', 'descricao', 'website', 'telegram', 'especialidade', 'ativo', 'notas']:
                    fields.append(f"{field} = ?")
                    values.append(value)
            
            if fields:
                values.append(tipster_id)
                query = f"UPDATE tipsters SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar tipster: {e}")
            return False
    
    def delete_tipster(self, tipster_id: int) -> bool:
        """Remove um tipster (marca como inativo)"""
        return self.update_tipster(tipster_id, ativo=False)
    
    def get_tipster_stats(self, tipster_name: str, days_back: int = 365) -> Optional[TipsterStats]:
        """Calcula estatísticas detalhadas de um tipster"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
                SELECT 
                    data,
                    valor_aposta,
                    odd,
                    resultado,
                    lucro_prejuizo
                FROM apostas 
                WHERE tipster = ? AND data >= ? AND data <= ?
                ORDER BY data ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(
                tipster_name,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ))
            
            conn.close()
            
            if df.empty:
                return None
            
            # Calcular estatísticas básicas
            total_tips = len(df)
            wins = len(df[df['resultado'] == 'Ganhou'])
            losses = len(df[df['resultado'] == 'Perdeu'])
            win_rate = (wins / total_tips) * 100 if total_tips > 0 else 0
            
            total_stake = df['valor_aposta'].sum()
            total_profit = df['lucro_prejuizo'].sum()
            roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
            avg_odd = df['odd'].mean()
            
            # Calcular streaks
            streaks = self._calculate_streaks(df)
            max_win_streak = streaks['max_win_streak']
            max_loss_streak = streaks['max_loss_streak']
            current_streak = streaks['current_streak']
            streak_type = streaks['streak_type']
            
            # Datas e atividade
            df['data'] = pd.to_datetime(df['data'])
            last_tip_date = df['data'].max().strftime('%Y-%m-%d')
            first_tip_date = df['data'].min()
            active_days = (df['data'].max() - first_tip_date).days + 1
            tips_per_day = total_tips / active_days if active_days > 0 else 0
            
            # Métricas avançadas
            profit_factor = self._calculate_profit_factor(df)
            sharpe_ratio = self._calculate_sharpe_ratio(df)
            max_drawdown = self._calculate_max_drawdown(df)
            consistency_score = self._calculate_consistency_score(df)
            
            # Classificação de risco
            risk_level = self._classify_risk_level(win_rate, roi, max_drawdown, consistency_score)
            
            # Recomendação
            recommendation = self._generate_recommendation(win_rate, roi, consistency_score, risk_level)
            
            return TipsterStats(
                name=tipster_name,
                total_tips=total_tips,
                wins=wins,
                losses=losses,
                win_rate=win_rate,
                total_stake=total_stake,
                total_profit=total_profit,
                roi=roi,
                avg_odd=avg_odd,
                max_win_streak=max_win_streak,
                max_loss_streak=max_loss_streak,
                current_streak=current_streak,
                streak_type=streak_type,
                last_tip_date=last_tip_date,
                active_days=active_days,
                tips_per_day=tips_per_day,
                profit_factor=profit_factor,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                consistency_score=consistency_score,
                risk_level=risk_level,
                recommendation=recommendation
            )
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas do tipster: {e}")
            return None
    
    def get_all_tipsters_stats(self, days_back: int = 365) -> List[TipsterStats]:
        """Obtém estatísticas de todos os tipsters"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Obter todos os tipsters únicos das apostas
            query = "SELECT DISTINCT tipster FROM apostas WHERE tipster IS NOT NULL"
            tipsters_df = pd.read_sql_query(query, conn)
            conn.close()
            
            stats_list = []
            for tipster in tipsters_df['tipster']:
                stats = self.get_tipster_stats(tipster, days_back)
                if stats:
                    stats_list.append(stats)
            
            # Ordenar por ROI
            stats_list.sort(key=lambda x: x.roi, reverse=True)
            
            return stats_list
            
        except Exception as e:
            print(f"Erro ao obter estatísticas de todos os tipsters: {e}")
            return []
    
    def compare_tipsters(self, tipster1: str, tipster2: str, days_back: int = 365) -> Optional[TipsterComparison]:
        """Compara dois tipsters"""
        stats1 = self.get_tipster_stats(tipster1, days_back)
        stats2 = self.get_tipster_stats(tipster2, days_back)
        
        if not stats1 or not stats2:
            return None
        
        better_roi = tipster1 if stats1.roi > stats2.roi else tipster2
        better_winrate = tipster1 if stats1.win_rate > stats2.win_rate else tipster2
        better_consistency = tipster1 if stats1.consistency_score > stats2.consistency_score else tipster2
        
        # Determinar vencedor geral (peso: ROI 40%, Win Rate 30%, Consistência 30%)
        score1 = (stats1.roi * 0.4) + (stats1.win_rate * 0.3) + (stats1.consistency_score * 0.3)
        score2 = (stats2.roi * 0.4) + (stats2.win_rate * 0.3) + (stats2.consistency_score * 0.3)
        
        overall_winner = tipster1 if score1 > score2 else tipster2
        
        # Recomendação
        if abs(score1 - score2) < 5:
            recommendation = "Ambos os tipsters têm performance similar. Considere diversificar."
        else:
            winner_stats = stats1 if overall_winner == tipster1 else stats2
            recommendation = f"{overall_winner} é superior com ROI de {winner_stats.roi:.1f}% e win rate de {winner_stats.win_rate:.1f}%"
        
        return TipsterComparison(
            tipster1=tipster1,
            tipster2=tipster2,
            better_roi=better_roi,
            better_winrate=better_winrate,
            better_consistency=better_consistency,
            overall_winner=overall_winner,
            recommendation=recommendation
        )
    
    def get_tipster_ranking(self, days_back: int = 365, min_tips: int = 10) -> List[Dict[str, Any]]:
        """Gera ranking de tipsters"""
        all_stats = self.get_all_tipsters_stats(days_back)
        
        # Filtrar por número mínimo de tips
        filtered_stats = [s for s in all_stats if s.total_tips >= min_tips]
        
        ranking = []
        for i, stats in enumerate(filtered_stats, 1):
            ranking.append({
                'posicao': i,
                'tipster': stats.name,
                'roi': stats.roi,
                'win_rate': stats.win_rate,
                'total_tips': stats.total_tips,
                'profit': stats.total_profit,
                'consistency': stats.consistency_score,
                'risk_level': stats.risk_level,
                'recommendation': stats.recommendation
            })
        
        return ranking
    
    def analyze_tipster_trends(self, tipster_name: str, days_back: int = 365) -> Dict[str, Any]:
        """Analisa tendências de um tipster"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
                SELECT 
                    data,
                    valor_aposta,
                    odd,
                    resultado,
                    lucro_prejuizo,
                    competicao,
                    tipo_aposta
                FROM apostas 
                WHERE tipster = ? AND data >= ? AND data <= ?
                ORDER BY data ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(
                tipster_name,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ))
            
            conn.close()
            
            if df.empty:
                return {'error': 'Nenhum dado encontrado'}
            
            df['data'] = pd.to_datetime(df['data'])
            df['won'] = df['resultado'] == 'Ganhou'
            
            # Tendência temporal
            monthly_stats = df.groupby(df['data'].dt.to_period('M')).agg({
                'won': ['count', 'sum'],
                'lucro_prejuizo': 'sum',
                'valor_aposta': 'sum'
            }).round(2)
            
            monthly_stats.columns = ['total_tips', 'wins', 'profit', 'stake']
            monthly_stats['win_rate'] = (monthly_stats['wins'] / monthly_stats['total_tips'] * 100).round(1)
            monthly_stats['roi'] = (monthly_stats['profit'] / monthly_stats['stake'] * 100).round(1)
            
            # Tendência por competição
            comp_stats = df.groupby('competicao').agg({
                'won': ['count', 'sum'],
                'lucro_prejuizo': 'sum'
            }).round(2)
            
            comp_stats.columns = ['total', 'wins', 'profit']
            comp_stats['win_rate'] = (comp_stats['wins'] / comp_stats['total'] * 100).round(1)
            comp_stats = comp_stats.sort_values('profit', ascending=False)
            
            # Tendência por tipo de aposta
            type_stats = df.groupby('tipo_aposta').agg({
                'won': ['count', 'sum'],
                'lucro_prejuizo': 'sum'
            }).round(2)
            
            type_stats.columns = ['total', 'wins', 'profit']
            type_stats['win_rate'] = (type_stats['wins'] / type_stats['total'] * 100).round(1)
            type_stats = type_stats.sort_values('profit', ascending=False)
            
            # Análise de forma recente (últimos 30 dias)
            recent_data = df[df['data'] >= (datetime.now() - timedelta(days=30))]
            recent_form = {
                'tips': len(recent_data),
                'wins': len(recent_data[recent_data['won']]),
                'win_rate': (len(recent_data[recent_data['won']]) / len(recent_data) * 100) if len(recent_data) > 0 else 0,
                'profit': recent_data['lucro_prejuizo'].sum(),
                'roi': (recent_data['lucro_prejuizo'].sum() / recent_data['valor_aposta'].sum() * 100) if recent_data['valor_aposta'].sum() > 0 else 0
            }
            
            return {
                'monthly_trends': monthly_stats.to_dict('index'),
                'best_competitions': comp_stats.head(5).to_dict('index'),
                'best_bet_types': type_stats.head(5).to_dict('index'),
                'recent_form': recent_form,
                'total_period_days': days_back,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {'error': f'Erro na análise de tendências: {str(e)}'}
    
    def plot_tipster_performance(self, tipster_name: str, days_back: int = 365, save_path: Optional[str] = None):
        """Cria gráficos de performance do tipster"""
        try:
            stats = self.get_tipster_stats(tipster_name, days_back)
            trends = self.analyze_tipster_trends(tipster_name, days_back)
            
            if not stats or 'error' in trends:
                return None
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Performance de {tipster_name}', fontsize=16, fontweight='bold')
            
            # 1. Evolução mensal do ROI
            ax1 = axes[0, 0]
            monthly_data = trends['monthly_trends']
            if monthly_data:
                months = list(monthly_data.keys())
                rois = [monthly_data[month]['roi'] for month in months]
                
                ax1.plot(range(len(months)), rois, marker='o', linewidth=2, markersize=6)
                ax1.set_title('Evolução Mensal do ROI')
                ax1.set_ylabel('ROI (%)')
                ax1.set_xlabel('Mês')
                ax1.grid(True, alpha=0.3)
                ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
                
                # Configurar labels do eixo x
                ax1.set_xticks(range(len(months)))
                ax1.set_xticklabels([str(m) for m in months], rotation=45)
            
            # 2. Melhores competições
            ax2 = axes[0, 1]
            comp_data = trends['best_competitions']
            if comp_data:
                comps = list(comp_data.keys())[:5]
                profits = [comp_data[comp]['profit'] for comp in comps]
                
                bars = ax2.barh(comps, profits, color='green' if all(p >= 0 for p in profits) else 'red')
                ax2.set_title('Top 5 Competições por Lucro')
                ax2.set_xlabel('Lucro (€)')
            
            # 3. Distribuição de resultados
            ax3 = axes[1, 0]
            labels = ['Vitórias', 'Derrotas']
            sizes = [stats.wins, stats.losses]
            colors = ['green', 'red']
            
            wedges, texts, autotexts = ax3.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
            ax3.set_title(f'Distribuição de Resultados\n(Win Rate: {stats.win_rate:.1f}%)')
            
            # 4. Métricas principais
            ax4 = axes[1, 1]
            metrics = ['ROI', 'Win Rate', 'Consistency', 'Profit Factor']
            values = [stats.roi, stats.win_rate, stats.consistency_score, stats.profit_factor]
            
            bars = ax4.bar(metrics, values, color=['blue', 'green', 'orange', 'purple'])
            ax4.set_title('Métricas Principais')
            ax4.set_ylabel('Valor')
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            print(f"Erro ao criar gráficos: {e}")
            return None
    
    def export_tipster_report(self, tipster_name: str, file_path: str, days_back: int = 365) -> bool:
        """Exporta relatório completo do tipster"""
        try:
            stats = self.get_tipster_stats(tipster_name, days_back)
            trends = self.analyze_tipster_trends(tipster_name, days_back)
            
            if not stats:
                return False
            
            report = {
                'tipster': tipster_name,
                'periodo_analise': f'{days_back} dias',
                'data_relatorio': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estatisticas': asdict(stats),
                'tendencias': trends
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")
            return False
    
    # Métodos auxiliares
    def _calculate_streaks(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calcula sequências de vitórias e derrotas"""
        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        current_streak = 0
        streak_type = 'none'
        
        for _, row in df.iterrows():
            if row['resultado'] == 'Ganhou':
                current_win_streak += 1
                current_loss_streak = 0
                current_streak = current_win_streak
                streak_type = 'win'
                max_win_streak = max(max_win_streak, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                current_streak = current_loss_streak
                streak_type = 'loss'
                max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        return {
            'max_win_streak': max_win_streak,
            'max_loss_streak': max_loss_streak,
            'current_streak': current_streak,
            'streak_type': streak_type
        }
    
    def _calculate_profit_factor(self, df: pd.DataFrame) -> float:
        """Calcula o profit factor"""
        wins = df[df['resultado'] == 'Ganhou']['lucro_prejuizo'].sum()
        losses = abs(df[df['resultado'] == 'Perdeu']['lucro_prejuizo'].sum())
        
        return wins / losses if losses > 0 else float('inf')
    
    def _calculate_sharpe_ratio(self, df: pd.DataFrame) -> float:
        """Calcula o Sharpe ratio"""
        returns = df['lucro_prejuizo'] / df['valor_aposta']
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        return mean_return / std_return if std_return > 0 else 0.0
    
    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calcula o máximo drawdown"""
        cumulative = df['lucro_prejuizo'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        
        return abs(drawdown.min()) if not drawdown.empty else 0.0
    
    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calcula score de consistência (0-100)"""
        if len(df) < 10:
            return 0.0
        
        # Dividir em períodos e calcular ROI de cada período
        df_sorted = df.sort_values('data')
        period_size = max(5, len(df) // 10)  # Pelo menos 5 apostas por período
        
        period_rois = []
        for i in range(0, len(df_sorted), period_size):
            period_data = df_sorted.iloc[i:i+period_size]
            if len(period_data) >= 3:  # Mínimo 3 apostas por período
                period_roi = (period_data['lucro_prejuizo'].sum() / period_data['valor_aposta'].sum()) * 100
                period_rois.append(period_roi)
        
        if len(period_rois) < 3:
            return 0.0
        
        # Consistência baseada na variação dos ROIs dos períodos
        roi_std = np.std(period_rois)
        roi_mean = np.mean(period_rois)
        
        # Score inversamente proporcional à variação
        if roi_std == 0:
            return 100.0
        
        consistency = max(0, 100 - (roi_std / max(abs(roi_mean), 1)) * 50)
        return min(100, consistency)
    
    def _classify_risk_level(self, win_rate: float, roi: float, max_drawdown: float, consistency: float) -> str:
        """Classifica o nível de risco"""
        risk_score = 0
        
        # Win rate (peso: 25%)
        if win_rate >= 60:
            risk_score += 25
        elif win_rate >= 50:
            risk_score += 15
        elif win_rate >= 40:
            risk_score += 5
        
        # ROI (peso: 30%)
        if roi >= 10:
            risk_score += 30
        elif roi >= 5:
            risk_score += 20
        elif roi >= 0:
            risk_score += 10
        
        # Max Drawdown (peso: 25%)
        if max_drawdown <= 10:
            risk_score += 25
        elif max_drawdown <= 20:
            risk_score += 15
        elif max_drawdown <= 30:
            risk_score += 5
        
        # Consistência (peso: 20%)
        if consistency >= 70:
            risk_score += 20
        elif consistency >= 50:
            risk_score += 15
        elif consistency >= 30:
            risk_score += 10
        
        if risk_score >= 70:
            return 'Baixo'
        elif risk_score >= 40:
            return 'Médio'
        else:
            return 'Alto'
    
    def _generate_recommendation(self, win_rate: float, roi: float, consistency: float, risk_level: str) -> str:
        """Gera recomendação baseada nas métricas"""
        if roi >= 10 and win_rate >= 55 and risk_level == 'Baixo':
            return 'SEGUIR - Excelente performance e baixo risco'
        elif roi >= 5 and win_rate >= 50 and consistency >= 50:
            return 'SEGUIR - Boa performance com risco controlado'
        elif roi >= 0 and win_rate >= 45:
            return 'OBSERVAR - Performance moderada, monitorar evolução'
        elif roi < 0 or win_rate < 40:
            return 'EVITAR - Performance insatisfatória'
        else:
            return 'NEUTRO - Necessita mais dados para avaliação'

    def get_detailed_stats(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """Obter estatísticas detalhadas de todos os tipsters"""
        try:
            stats_list = self.get_all_tipsters_stats(days_back)
            detailed_stats = []
            
            for stats in stats_list:
                detailed_stats.append({
                    'nome': stats.name,
                    'total_tips': stats.total_tips,
                    'win_rate': stats.win_rate,
                    'roi': stats.roi,
                    'lucro_total': stats.total_profit,
                    'sequencia_atual': f"{stats.current_streak} {stats.streak_type}s",
                    'nivel_risco': stats.risk_level,
                    'recomendacao': stats.recommendation,
                    'consistency_score': stats.consistency_score,
                    'sharpe_ratio': stats.sharpe_ratio
                })
            
            return detailed_stats
        except Exception as e:
            print(f"Erro ao obter estatísticas detalhadas: {e}")
            return []

    def generate_ranking(self, days_back: int = 365, min_tips: int = 5) -> List[Dict[str, Any]]:
        """Gerar ranking de tipsters"""
        try:
            return self.get_tipster_ranking(days_back, min_tips)
        except Exception as e:
            print(f"Erro ao gerar ranking: {e}")
            return []

if __name__ == "__main__":
    tracker = TipsterTracker()
    
    # Adicionar alguns tipsters de exemplo
    tracker.add_tipster("João Silva", "Especialista em futebol português", 
                       "www.joaosilva.com", "@joaosilva", "Futebol")
    tracker.add_tipster("Maria Santos", "Analista de basquetebol", 
                       "", "@mariasantos", "Basquetebol")
    
    # Obter ranking
    ranking = tracker.get_tipster_ranking(days_back=180, min_tips=5)
    
    print("=== RANKING DE TIPSTERS ===")
    for entry in ranking:
        print(f"{entry['posicao']}. {entry['tipster']} - ROI: {entry['roi']:.1f}% - Win Rate: {entry['win_rate']:.1f}%")
    
    # Estatísticas detalhadas do primeiro tipster
    if ranking:
        top_tipster = ranking[0]['tipster']
        stats = tracker.get_tipster_stats(top_tipster)
        
        if stats:
            print(f"\n=== ESTATÍSTICAS DE {top_tipster.upper()} ===")
            print(f"Total de Tips: {stats.total_tips}")
            print(f"Win Rate: {stats.win_rate:.1f}%")
            print(f"ROI: {stats.roi:.1f}%")
            print(f"Lucro Total: {stats.total_profit:.2f}€")
            print(f"Sequência Atual: {stats.current_streak} {stats.streak_type}s")
            print(f"Nível de Risco: {stats.risk_level}")
            print(f"Recomendação: {stats.recommendation}")
            
            # Análise de tendências
            trends = tracker.analyze_tipster_trends(top_tipster, 180)
            if 'error' not in trends:
                print(f"\n=== FORMA RECENTE (30 dias) ===")
                recent = trends['recent_form']
                print(f"Tips: {recent['tips']}")
                print(f"Win Rate: {recent['win_rate']:.1f}%")
                print(f"ROI: {recent['roi']:.1f}%")
    
    print("\n=== TIPSTERS REGISTADOS ===")
    tipsters = tracker.get_tipsters()
    for tipster in tipsters:
        print(f"- {tipster['nome']} ({tipster['especialidade']})")