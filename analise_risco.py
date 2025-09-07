#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Análise de Risco Avançada
Cálculos de risco, Kelly Criterion, VaR, Drawdown e otimização de apostas
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sqlite3
from main import DatabaseManager
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class RiskAnalyzer:
    """Analisador de risco para apostas desportivas"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.df_apostas = None
        self.load_data()
    
    def load_data(self):
        """Carregar dados das apostas"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            self.df_apostas = pd.read_sql_query("""
                SELECT * FROM apostas 
                WHERE resultado IN ('Ganha', 'Perdida')
                ORDER BY data_hora
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
                
                # Calcular retornos
                self.df_apostas['return'] = self.df_apostas['lucro_prejuizo'] / self.df_apostas['valor_apostado']
                self.df_apostas['roi'] = self.df_apostas['return'] * 100
                
                # Adicionar resultado binário
                self.df_apostas['win'] = (self.df_apostas['resultado'] == 'Ganha').astype(int)
                
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def calculate_basic_metrics(self) -> Dict[str, float]:
        """Calcular métricas básicas de risco"""
        if self.df_apostas is None or self.df_apostas.empty:
            return {}
        
        returns = self.df_apostas['return'].values
        
        metrics = {
            'total_bets': len(self.df_apostas),
            'win_rate': self.df_apostas['win'].mean() * 100,
            'avg_return': np.mean(returns) * 100,
            'volatility': np.std(returns) * 100,
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'sortino_ratio': self.calculate_sortino_ratio(returns),
            'calmar_ratio': self.calculate_calmar_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(returns),
            'var_95': self.calculate_var(returns, 0.95),
            'var_99': self.calculate_var(returns, 0.99),
            'cvar_95': self.calculate_cvar(returns, 0.95),
            'skewness': stats.skew(returns),
            'kurtosis': stats.kurtosis(returns),
            'profit_factor': self.calculate_profit_factor()
        }
        
        return metrics
    
    def calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
        """Calcular Sharpe Ratio"""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        
        excess_return = np.mean(returns) - risk_free_rate
        return excess_return / np.std(returns)
    
    def calculate_sortino_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
        """Calcular Sortino Ratio (considera apenas volatilidade negativa)"""
        if len(returns) == 0:
            return 0.0
        
        excess_return = np.mean(returns) - risk_free_rate
        downside_returns = returns[returns < risk_free_rate]
        
        if len(downside_returns) == 0:
            return float('inf') if excess_return > 0 else 0.0
        
        downside_deviation = np.std(downside_returns)
        return excess_return / downside_deviation if downside_deviation > 0 else 0.0
    
    def calculate_calmar_ratio(self, returns: np.ndarray) -> float:
        """Calcular Calmar Ratio (retorno anualizado / max drawdown)"""
        if len(returns) == 0:
            return 0.0
        
        annual_return = np.mean(returns) * 252  # Assumindo 252 dias de trading por ano
        max_dd = abs(self.calculate_max_drawdown(returns))
        
        return annual_return / max_dd if max_dd > 0 else 0.0
    
    def calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calcular Maximum Drawdown"""
        if len(returns) == 0:
            return 0.0
        
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        
        return np.min(drawdown) * 100  # Converter para percentual
    
    def calculate_var(self, returns: np.ndarray, confidence_level: float) -> float:
        """Calcular Value at Risk"""
        if len(returns) == 0:
            return 0.0
        
        return np.percentile(returns, (1 - confidence_level) * 100) * 100
    
    def calculate_cvar(self, returns: np.ndarray, confidence_level: float) -> float:
        """Calcular Conditional Value at Risk (Expected Shortfall)"""
        if len(returns) == 0:
            return 0.0
        
        var_threshold = np.percentile(returns, (1 - confidence_level) * 100)
        tail_losses = returns[returns <= var_threshold]
        
        return np.mean(tail_losses) * 100 if len(tail_losses) > 0 else 0.0
    
    def calculate_profit_factor(self) -> float:
        """Calcular Profit Factor (lucros totais / perdas totais)"""
        if self.df_apostas is None or self.df_apostas.empty:
            return 0.0
        
        wins = self.df_apostas[self.df_apostas['lucro_prejuizo'] > 0]['lucro_prejuizo'].sum()
        losses = abs(self.df_apostas[self.df_apostas['lucro_prejuizo'] < 0]['lucro_prejuizo'].sum())
        
        return wins / losses if losses > 0 else float('inf') if wins > 0 else 0.0
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calcular Kelly Criterion para otimização de stake"""
        if avg_loss == 0:
            return 0.0
        
        b = avg_win / abs(avg_loss)  # Ratio win/loss
        p = win_rate / 100  # Probabilidade de ganhar
        q = 1 - p  # Probabilidade de perder
        
        kelly = (b * p - q) / b
        return max(0, min(kelly, 0.25))  # Limitar a 25% para segurança
    
    def calculate_optimal_kelly(self) -> Dict[str, float]:
        """Calcular Kelly Criterion otimizado por diferentes critérios"""
        if self.df_apostas is None or self.df_apostas.empty:
            return {}
        
        # Kelly geral
        win_rate = self.df_apostas['win'].mean() * 100
        wins = self.df_apostas[self.df_apostas['lucro_prejuizo'] > 0]['lucro_prejuizo']
        losses = self.df_apostas[self.df_apostas['lucro_prejuizo'] < 0]['lucro_prejuizo']
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        
        kelly_general = self.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
        
        # Kelly por competição
        kelly_by_competition = {}
        for comp in self.df_apostas['competicao'].unique():
            comp_data = self.df_apostas[self.df_apostas['competicao'] == comp]
            if len(comp_data) >= 10:  # Mínimo 10 apostas
                comp_win_rate = comp_data['win'].mean() * 100
                comp_wins = comp_data[comp_data['lucro_prejuizo'] > 0]['lucro_prejuizo']
                comp_losses = comp_data[comp_data['lucro_prejuizo'] < 0]['lucro_prejuizo']
                
                comp_avg_win = comp_wins.mean() if len(comp_wins) > 0 else 0
                comp_avg_loss = comp_losses.mean() if len(comp_losses) > 0 else 0
                
                kelly_by_competition[comp] = self.calculate_kelly_criterion(
                    comp_win_rate, comp_avg_win, comp_avg_loss
                )
        
        # Kelly por tipo de aposta
        kelly_by_bet_type = {}
        for bet_type in self.df_apostas['tipo_aposta'].unique():
            type_data = self.df_apostas[self.df_apostas['tipo_aposta'] == bet_type]
            if len(type_data) >= 10:  # Mínimo 10 apostas
                type_win_rate = type_data['win'].mean() * 100
                type_wins = type_data[type_data['lucro_prejuizo'] > 0]['lucro_prejuizo']
                type_losses = type_data[type_data['lucro_prejuizo'] < 0]['lucro_prejuizo']
                
                type_avg_win = type_wins.mean() if len(type_wins) > 0 else 0
                type_avg_loss = type_losses.mean() if len(type_losses) > 0 else 0
                
                kelly_by_bet_type[bet_type] = self.calculate_kelly_criterion(
                    type_win_rate, type_avg_win, type_avg_loss
                )
        
        return {
            'kelly_general': kelly_general,
            'kelly_by_competition': kelly_by_competition,
            'kelly_by_bet_type': kelly_by_bet_type
        }
    
    def calculate_risk_adjusted_returns(self) -> Dict[str, float]:
        """Calcular retornos ajustados ao risco"""
        if self.df_apostas is None or self.df_apostas.empty:
            return {}
        
        returns = self.df_apostas['return'].values
        
        # Information Ratio
        benchmark_return = 0  # Assumindo benchmark de 0%
        excess_returns = returns - benchmark_return
        tracking_error = np.std(excess_returns)
        information_ratio = np.mean(excess_returns) / tracking_error if tracking_error > 0 else 0
        
        # Treynor Ratio (assumindo beta = 1 para simplicidade)
        beta = 1.0
        treynor_ratio = np.mean(returns) / beta
        
        # Jensen's Alpha (assumindo CAPM com beta = 1)
        market_return = 0  # Assumindo retorno de mercado de 0%
        risk_free_rate = 0
        jensens_alpha = np.mean(returns) - (risk_free_rate + beta * (market_return - risk_free_rate))
        
        return {
            'information_ratio': information_ratio,
            'treynor_ratio': treynor_ratio,
            'jensens_alpha': jensens_alpha * 100
        }
    
    def analyze_drawdown_periods(self) -> List[Dict]:
        """Analisar períodos de drawdown"""
        if self.df_apostas is None or self.df_apostas.empty:
            return []
        
        returns = self.df_apostas['return'].values
        dates = self.df_apostas['data_hora'].values
        
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        
        # Identificar períodos de drawdown
        in_drawdown = drawdown < 0
        drawdown_periods = []
        
        start_idx = None
        for i, is_dd in enumerate(in_drawdown):
            if is_dd and start_idx is None:
                start_idx = i
            elif not is_dd and start_idx is not None:
                # Fim do período de drawdown
                end_idx = i - 1
                period_drawdown = drawdown[start_idx:end_idx+1]
                max_dd_in_period = np.min(period_drawdown)
                
                drawdown_periods.append({
                    'start_date': dates[start_idx],
                    'end_date': dates[end_idx],
                    'duration_days': pd.Timedelta(dates[end_idx] - dates[start_idx]).days,
                    'max_drawdown': max_dd_in_period * 100,
                    'recovery_time': None  # Será calculado se houver recuperação
                })
                
                start_idx = None
        
        # Se ainda estamos em drawdown
        if start_idx is not None:
            period_drawdown = drawdown[start_idx:]
            max_dd_in_period = np.min(period_drawdown)
            
            drawdown_periods.append({
                'start_date': dates[start_idx],
                'end_date': dates[-1],
                'duration_days': pd.Timedelta(dates[-1] - dates[start_idx]).days,
                'max_drawdown': max_dd_in_period * 100,
                'recovery_time': None,
                'ongoing': True
            })
        
        return drawdown_periods
    
    def calculate_risk_metrics_by_period(self, period_days: int = 30) -> pd.DataFrame:
        """Calcular métricas de risco por período"""
        if self.df_apostas is None or self.df_apostas.empty:
            return pd.DataFrame()
        
        # Agrupar por períodos
        self.df_apostas['period'] = self.df_apostas['data_hora'].dt.to_period(f'{period_days}D')
        
        period_metrics = []
        
        for period, group in self.df_apostas.groupby('period'):
            if len(group) >= 5:  # Mínimo 5 apostas por período
                returns = group['return'].values
                
                metrics = {
                    'period': str(period),
                    'start_date': group['data_hora'].min(),
                    'end_date': group['data_hora'].max(),
                    'num_bets': len(group),
                    'win_rate': group['win'].mean() * 100,
                    'avg_return': np.mean(returns) * 100,
                    'volatility': np.std(returns) * 100,
                    'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                    'max_drawdown': self.calculate_max_drawdown(returns),
                    'var_95': self.calculate_var(returns, 0.95),
                    'total_profit': group['lucro_prejuizo'].sum()
                }
                
                period_metrics.append(metrics)
        
        return pd.DataFrame(period_metrics)
    
    def monte_carlo_simulation(self, num_simulations: int = 1000, num_bets: int = 100) -> Dict:
        """Simulação Monte Carlo para projeção de resultados"""
        if self.df_apostas is None or self.df_apostas.empty:
            return {}
        
        # Parâmetros históricos
        win_rate = self.df_apostas['win'].mean()
        avg_win = self.df_apostas[self.df_apostas['lucro_prejuizo'] > 0]['return'].mean()
        avg_loss = self.df_apostas[self.df_apostas['lucro_prejuizo'] < 0]['return'].mean()
        
        if pd.isna(avg_win):
            avg_win = 0
        if pd.isna(avg_loss):
            avg_loss = 0
        
        simulation_results = []
        
        for _ in range(num_simulations):
            cumulative_return = 0
            max_drawdown = 0
            current_drawdown = 0
            peak = 0
            
            for _ in range(num_bets):
                # Simular resultado da aposta
                if np.random.random() < win_rate:
                    bet_return = avg_win
                else:
                    bet_return = avg_loss
                
                cumulative_return += bet_return
                
                # Calcular drawdown
                if cumulative_return > peak:
                    peak = cumulative_return
                    current_drawdown = 0
                else:
                    current_drawdown = peak - cumulative_return
                    max_drawdown = max(max_drawdown, current_drawdown)
            
            simulation_results.append({
                'final_return': cumulative_return * 100,
                'max_drawdown': max_drawdown * 100
            })
        
        results_df = pd.DataFrame(simulation_results)
        
        return {
            'mean_return': results_df['final_return'].mean(),
            'std_return': results_df['final_return'].std(),
            'percentile_5': results_df['final_return'].quantile(0.05),
            'percentile_25': results_df['final_return'].quantile(0.25),
            'percentile_50': results_df['final_return'].quantile(0.50),
            'percentile_75': results_df['final_return'].quantile(0.75),
            'percentile_95': results_df['final_return'].quantile(0.95),
            'prob_profit': (results_df['final_return'] > 0).mean() * 100,
            'prob_loss_10': (results_df['final_return'] < -10).mean() * 100,
            'prob_loss_20': (results_df['final_return'] < -20).mean() * 100,
            'avg_max_drawdown': results_df['max_drawdown'].mean(),
            'worst_drawdown': results_df['max_drawdown'].max()
        }
    
    def calculate_position_sizing(self, bankroll: float, risk_level: str = 'moderate') -> Dict:
        """Calcular tamanhos de posição recomendados"""
        kelly_data = self.calculate_optimal_kelly()
        kelly_general = kelly_data.get('kelly_general', 0)
        
        # Fatores de ajuste baseados no nível de risco
        risk_factors = {
            'conservative': 0.25,
            'moderate': 0.5,
            'aggressive': 0.75,
            'full_kelly': 1.0
        }
        
        risk_factor = risk_factors.get(risk_level, 0.5)
        adjusted_kelly = kelly_general * risk_factor
        
        # Diferentes estratégias de sizing
        strategies = {
            'fixed_amount': bankroll * 0.02,  # 2% fixo
            'fixed_percentage': bankroll * 0.05,  # 5% fixo
            'kelly_criterion': bankroll * adjusted_kelly,
            'volatility_adjusted': bankroll * (0.02 / max(0.01, self.df_apostas['return'].std())),
            'confidence_based': bankroll * 0.01 * (self.df_apostas['win'].mean() * 10)
        }
        
        # Limites de segurança
        max_bet = bankroll * 0.1  # Máximo 10% da banca
        for strategy in strategies:
            strategies[strategy] = min(strategies[strategy], max_bet)
            strategies[strategy] = max(strategies[strategy], bankroll * 0.001)  # Mínimo 0.1%
        
        return {
            'bankroll': bankroll,
            'kelly_percentage': kelly_general * 100,
            'adjusted_kelly_percentage': adjusted_kelly * 100,
            'recommended_strategies': strategies,
            'risk_level': risk_level
        }
    
    def generate_risk_report(self) -> Dict:
        """Gerar relatório completo de risco"""
        if self.df_apostas is None or self.df_apostas.empty:
            return {'error': 'Dados insuficientes para análise de risco'}
        
        basic_metrics = self.calculate_basic_metrics()
        kelly_data = self.calculate_optimal_kelly()
        risk_adjusted = self.calculate_risk_adjusted_returns()
        drawdown_periods = self.analyze_drawdown_periods()
        monte_carlo = self.monte_carlo_simulation()
        
        # Classificação de risco
        risk_score = self.calculate_risk_score(basic_metrics)
        
        return {
            'basic_metrics': basic_metrics,
            'kelly_criterion': kelly_data,
            'risk_adjusted_returns': risk_adjusted,
            'drawdown_analysis': {
                'periods': drawdown_periods,
                'num_periods': len(drawdown_periods),
                'avg_duration': np.mean([p['duration_days'] for p in drawdown_periods]) if drawdown_periods else 0,
                'worst_drawdown': min([p['max_drawdown'] for p in drawdown_periods]) if drawdown_periods else 0
            },
            'monte_carlo_projection': monte_carlo,
            'risk_classification': {
                'score': risk_score,
                'level': self.classify_risk_level(risk_score),
                'recommendations': self.get_risk_recommendations(risk_score)
            }
        }
    
    def calculate_risk_score(self, metrics: Dict) -> float:
        """Calcular score de risco (0-100, onde 100 é mais arriscado)"""
        score = 0
        
        # Volatilidade (0-30 pontos)
        volatility = metrics.get('volatility', 0)
        score += min(30, volatility * 3)
        
        # Max Drawdown (0-25 pontos)
        max_dd = abs(metrics.get('max_drawdown', 0))
        score += min(25, max_dd * 2.5)
        
        # Sharpe Ratio (0-20 pontos, invertido)
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 0:
            score += max(0, 20 - sharpe * 10)
        else:
            score += 20
        
        # Win Rate (0-15 pontos, invertido)
        win_rate = metrics.get('win_rate', 0)
        score += max(0, 15 - win_rate * 0.3)
        
        # VaR 95% (0-10 pontos)
        var_95 = abs(metrics.get('var_95', 0))
        score += min(10, var_95 * 2)
        
        return min(100, score)
    
    def classify_risk_level(self, risk_score: float) -> str:
        """Classificar nível de risco baseado no score"""
        if risk_score <= 20:
            return 'Muito Baixo'
        elif risk_score <= 40:
            return 'Baixo'
        elif risk_score <= 60:
            return 'Moderado'
        elif risk_score <= 80:
            return 'Alto'
        else:
            return 'Muito Alto'
    
    def get_risk_recommendations(self, risk_score: float) -> List[str]:
        """Obter recomendações baseadas no nível de risco"""
        recommendations = []
        
        if risk_score > 80:
            recommendations.extend([
                "⚠️ Risco muito alto detectado",
                "Reduza significativamente o tamanho das apostas",
                "Revise sua estratégia de apostas",
                "Considere fazer uma pausa para análise",
                "Implemente stop-loss rigoroso"
            ])
        elif risk_score > 60:
            recommendations.extend([
                "⚡ Risco elevado",
                "Reduza o tamanho das apostas",
                "Diversifique mais suas apostas",
                "Monitore o drawdown de perto",
                "Considere estratégias mais conservadoras"
            ])
        elif risk_score > 40:
            recommendations.extend([
                "📊 Risco moderado",
                "Mantenha disciplina na gestão de banca",
                "Continue monitorando as métricas",
                "Considere otimizar com Kelly Criterion"
            ])
        else:
            recommendations.extend([
                "✅ Risco controlado",
                "Continue com a estratégia atual",
                "Monitore regularmente as métricas",
                "Considere aumentar gradualmente as posições"
            ])
        
        return recommendations

# Funções utilitárias para cálculos específicos
def calculate_implied_probability(odd: float) -> float:
    """Calcular probabilidade implícita de uma odd"""
    return (1 / odd) * 100 if odd > 0 else 0

def calculate_expected_value(odd: float, true_probability: float, stake: float) -> float:
    """Calcular valor esperado de uma aposta"""
    win_amount = (odd - 1) * stake
    lose_amount = -stake
    
    prob_win = true_probability / 100
    prob_lose = 1 - prob_win
    
    return (prob_win * win_amount) + (prob_lose * lose_amount)

def is_value_bet(odd: float, true_probability: float) -> bool:
    """Verificar se uma aposta tem valor positivo"""
    implied_prob = calculate_implied_probability(odd)
    return true_probability > implied_prob

def calculate_optimal_stake_kelly(odd: float, true_probability: float, bankroll: float) -> float:
    """Calcular stake ótimo usando Kelly Criterion"""
    prob_win = true_probability / 100
    prob_lose = 1 - prob_win
    b = odd - 1  # Net odds
    
    kelly_fraction = (b * prob_win - prob_lose) / b
    
    # Limitar a 25% da banca para segurança
    kelly_fraction = max(0, min(kelly_fraction, 0.25))
    
    return bankroll * kelly_fraction