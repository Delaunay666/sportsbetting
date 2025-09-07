#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Estratégias de Apostas
Versão 1.2 - Inteligência e Automação

Este módulo implementa diferentes estratégias de gestão de banca:
- Flat Betting (valor fixo)
- Kelly Criterion (baseado em probabilidades)
- Percentagem da Banca (% fixa do bankroll)
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from traducoes import t

@dataclass
class SimulationResult:
    """Resultado de uma simulação de estratégia"""
    strategy_name: str
    initial_bankroll: float
    final_bankroll: float
    total_bets: int
    winning_bets: int
    total_profit: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_bet_size: float
    max_bet_size: float
    min_bet_size: float
    bankroll_evolution: List[float]
    bet_sizes: List[float]

class StrategySimulator:
    """Simulador de estratégias de apostas"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.strategies = {
            'flat': self._flat_betting,
            'kelly': self._kelly_criterion,
            'percentage': self._percentage_betting,
            'martingale': self._martingale,
            'fibonacci': self._fibonacci
        }
    
    def get_historical_data(self, days_back: int = 365) -> pd.DataFrame:
        """Carrega dados históricos das apostas"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Carregar todos os dados primeiro
            query = """
                SELECT 
                    data_hora as data,
                    valor_apostado as valor_aposta,
                    odd,
                    resultado,
                    lucro_prejuizo,
                    competicao,
                    tipo_aposta
                FROM apostas 
                ORDER BY id DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(query, conn, params=(days_back * 5,))  # Multiplicar para garantir dados suficientes
            
            conn.close()
            
            if not df.empty:
                # Converter data para datetime
                df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y %H:%M', errors='coerce')
                
                # Filtrar por período se necessário
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                df = df[df['data'] >= start_date]
                
                # Preparar features
                df['won'] = df['resultado'] == 'Ganha'
                df['roi'] = (df['lucro_prejuizo'] / df['valor_aposta']) * 100
                
                # Calcular probabilidade implícita
                df['implied_prob'] = 1 / df['odd']
                
                # Estimar probabilidade real baseada no histórico
                df['real_prob'] = df.groupby(['competicao', 'tipo_aposta'])['won'].transform('mean')
                
            return df
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _flat_betting(self, data: pd.DataFrame, bet_amount: float, **kwargs) -> SimulationResult:
        """Estratégia Flat Betting - valor fixo"""
        initial_bankroll = kwargs.get('initial_bankroll', 1000)
        bankroll = initial_bankroll
        bankroll_evolution = [bankroll]
        bet_sizes = []
        
        winning_bets = 0
        total_profit = 0
        
        for _, row in data.iterrows():
            if bankroll < bet_amount:
                break
                
            bet_sizes.append(bet_amount)
            bankroll -= bet_amount
            
            if row['won']:
                winning_bets += 1
                profit = bet_amount * (row['odd'] - 1)
                bankroll += bet_amount + profit
                total_profit += profit
            else:
                total_profit -= bet_amount
                
            bankroll_evolution.append(bankroll)
        
        return self._calculate_metrics(
            'Flat Betting', initial_bankroll, bankroll, data[:len(bet_sizes)], 
            bankroll_evolution, bet_sizes
        )
    
    def _kelly_criterion(self, data: pd.DataFrame, **kwargs) -> SimulationResult:
        """Estratégia Kelly Criterion"""
        initial_bankroll = kwargs.get('initial_bankroll', 1000)
        max_bet_pct = kwargs.get('max_bet_pct', 0.25)  # Máximo 25% da banca
        
        bankroll = initial_bankroll
        bankroll_evolution = [bankroll]
        bet_sizes = []
        
        winning_bets = 0
        total_profit = 0
        
        for _, row in data.iterrows():
            # Fórmula Kelly: f = (bp - q) / b
            # onde b = odd-1, p = prob real, q = 1-p
            b = row['odd'] - 1
            p = row['real_prob']
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # Limitar a fração Kelly
            kelly_fraction = max(0, min(kelly_fraction, max_bet_pct))
            
            bet_amount = bankroll * kelly_fraction
            
            if bet_amount < 1 or bankroll < bet_amount:
                break
                
            bet_sizes.append(bet_amount)
            bankroll -= bet_amount
            
            if row['won']:
                winning_bets += 1
                profit = bet_amount * b
                bankroll += bet_amount + profit
                total_profit += profit
            else:
                total_profit -= bet_amount
                
            bankroll_evolution.append(bankroll)
        
        return self._calculate_metrics(
            'Kelly Criterion', initial_bankroll, bankroll, data[:len(bet_sizes)], 
            bankroll_evolution, bet_sizes
        )
    
    def _percentage_betting(self, data: pd.DataFrame, percentage: float, **kwargs) -> SimulationResult:
        """Estratégia de percentagem fixa da banca"""
        initial_bankroll = kwargs.get('initial_bankroll', 1000)
        bankroll = initial_bankroll
        bankroll_evolution = [bankroll]
        bet_sizes = []
        
        winning_bets = 0
        total_profit = 0
        
        for _, row in data.iterrows():
            bet_amount = bankroll * (percentage / 100)
            
            if bet_amount < 1 or bankroll < bet_amount:
                break
                
            bet_sizes.append(bet_amount)
            bankroll -= bet_amount
            
            if row['won']:
                winning_bets += 1
                profit = bet_amount * (row['odd'] - 1)
                bankroll += bet_amount + profit
                total_profit += profit
            else:
                total_profit -= bet_amount
                
            bankroll_evolution.append(bankroll)
        
        return self._calculate_metrics(
            f'Percentage ({percentage}%)', initial_bankroll, bankroll, data[:len(bet_sizes)], 
            bankroll_evolution, bet_sizes
        )
    
    def _martingale(self, data: pd.DataFrame, base_bet: float, **kwargs) -> SimulationResult:
        """Estratégia Martingale"""
        initial_bankroll = kwargs.get('initial_bankroll', 1000)
        max_multiplier = kwargs.get('max_multiplier', 8)
        
        bankroll = initial_bankroll
        bankroll_evolution = [bankroll]
        bet_sizes = []
        
        winning_bets = 0
        total_profit = 0
        current_bet = base_bet
        consecutive_losses = 0
        
        for _, row in data.iterrows():
            if bankroll < current_bet:
                break
                
            bet_sizes.append(current_bet)
            bankroll -= current_bet
            
            if row['won']:
                winning_bets += 1
                profit = current_bet * (row['odd'] - 1)
                bankroll += current_bet + profit
                total_profit += profit
                current_bet = base_bet  # Reset
                consecutive_losses = 0
            else:
                total_profit -= current_bet
                consecutive_losses += 1
                # Dobrar a aposta (limitado pelo multiplicador máximo)
                multiplier = min(2 ** consecutive_losses, max_multiplier)
                current_bet = base_bet * multiplier
                
            bankroll_evolution.append(bankroll)
        
        return self._calculate_metrics(
            'Martingale', initial_bankroll, bankroll, data[:len(bet_sizes)], 
            bankroll_evolution, bet_sizes
        )
    
    def _fibonacci(self, data: pd.DataFrame, base_bet: float, **kwargs) -> SimulationResult:
        """Estratégia Fibonacci"""
        initial_bankroll = kwargs.get('initial_bankroll', 1000)
        
        # Sequência Fibonacci
        fib_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        
        bankroll = initial_bankroll
        bankroll_evolution = [bankroll]
        bet_sizes = []
        
        winning_bets = 0
        total_profit = 0
        fib_index = 0
        
        for _, row in data.iterrows():
            current_bet = base_bet * fib_sequence[fib_index]
            
            if bankroll < current_bet:
                break
                
            bet_sizes.append(current_bet)
            bankroll -= current_bet
            
            if row['won']:
                winning_bets += 1
                profit = current_bet * (row['odd'] - 1)
                bankroll += current_bet + profit
                total_profit += profit
                # Voltar 2 posições na sequência (ou para o início)
                fib_index = max(0, fib_index - 2)
            else:
                total_profit -= current_bet
                # Avançar na sequência Fibonacci
                fib_index = min(fib_index + 1, len(fib_sequence) - 1)
                
            bankroll_evolution.append(bankroll)
        
        return self._calculate_metrics(
            'Fibonacci', initial_bankroll, bankroll, data[:len(bet_sizes)], 
            bankroll_evolution, bet_sizes
        )
    
    def _calculate_metrics(self, strategy_name: str, initial_bankroll: float, 
                          final_bankroll: float, data: pd.DataFrame, 
                          bankroll_evolution: List[float], bet_sizes: List[float]) -> SimulationResult:
        """Calcula métricas da simulação"""
        
        total_bets = len(bet_sizes)
        if total_bets == 0:
            return SimulationResult(
                strategy_name=strategy_name,
                initial_bankroll=initial_bankroll,
                final_bankroll=initial_bankroll,
                total_bets=0,
                winning_bets=0,
                total_profit=0,
                roi=0,
                max_drawdown=0,
                sharpe_ratio=0,
                win_rate=0,
                avg_bet_size=0,
                max_bet_size=0,
                min_bet_size=0,
                bankroll_evolution=[initial_bankroll],
                bet_sizes=[]
            )
        
        winning_bets = data['won'].sum()
        total_profit = final_bankroll - initial_bankroll
        roi = (total_profit / initial_bankroll) * 100
        win_rate = (winning_bets / total_bets) * 100
        
        # Calcular drawdown máximo
        peak = initial_bankroll
        max_drawdown = 0
        for value in bankroll_evolution:
            if value > peak:
                peak = value
            drawdown = ((peak - value) / peak) * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calcular Sharpe Ratio (simplificado)
        returns = []
        for i in range(1, len(bankroll_evolution)):
            ret = (bankroll_evolution[i] - bankroll_evolution[i-1]) / bankroll_evolution[i-1]
            returns.append(ret)
        
        if len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        return SimulationResult(
            strategy_name=strategy_name,
            initial_bankroll=initial_bankroll,
            final_bankroll=final_bankroll,
            total_bets=total_bets,
            winning_bets=winning_bets,
            total_profit=total_profit,
            roi=roi,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            avg_bet_size=np.mean(bet_sizes),
            max_bet_size=max(bet_sizes),
            min_bet_size=min(bet_sizes),
            bankroll_evolution=bankroll_evolution,
            bet_sizes=bet_sizes
        )
    
    def run_simulation(self, strategy: str, **kwargs) -> Optional[SimulationResult]:
        """Executa uma simulação de estratégia"""
        if strategy not in self.strategies:
            return None
            
        days_back = kwargs.get('days_back', 365)
        data = self.get_historical_data(days_back)
        
        if data.empty:
            return None
            
        return self.strategies[strategy](data, **kwargs)
    
    def compare_strategies(self, strategies_config: Dict, days_back: int = 365) -> List[SimulationResult]:
        """Compara múltiplas estratégias"""
        results = []
        data = self.get_historical_data(days_back)
        
        if data.empty:
            return results
            
        for strategy_name, config in strategies_config.items():
            if strategy_name in self.strategies:
                result = self.strategies[strategy_name](data, **config)
                if result:
                    results.append(result)
                    
        return results
    
    def plot_comparison(self, results: List[SimulationResult], save_path: Optional[str] = None):
        """Cria gráficos de comparação das estratégias"""
        if not results:
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Comparação de Estratégias de Apostas', fontsize=16, fontweight='bold')
        
        # 1. Evolução da Banca
        ax1 = axes[0, 0]
        for result in results:
            ax1.plot(result.bankroll_evolution, label=result.strategy_name, linewidth=2)
        ax1.set_title('Evolução da Banca')
        ax1.set_xlabel('Número de Apostas')
        ax1.set_ylabel('Valor da Banca (€)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. ROI Comparison
        ax2 = axes[0, 1]
        strategies = [r.strategy_name for r in results]
        rois = [r.roi for r in results]
        colors = ['green' if roi > 0 else 'red' for roi in rois]
        bars = ax2.bar(strategies, rois, color=colors, alpha=0.7)
        ax2.set_title('ROI por Estratégia')
        ax2.set_ylabel('ROI (%)')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, roi in zip(bars, rois):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (1 if height > 0 else -3),
                    f'{roi:.1f}%', ha='center', va='bottom' if height > 0 else 'top')
        
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        # 3. Win Rate vs Max Drawdown
        ax3 = axes[1, 0]
        win_rates = [r.win_rate for r in results]
        drawdowns = [r.max_drawdown for r in results]
        
        scatter = ax3.scatter(win_rates, drawdowns, s=100, alpha=0.7, c=rois, cmap='RdYlGn')
        
        for i, result in enumerate(results):
            ax3.annotate(result.strategy_name, (win_rates[i], drawdowns[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax3.set_title('Win Rate vs Max Drawdown')
        ax3.set_xlabel('Win Rate (%)')
        ax3.set_ylabel('Max Drawdown (%)')
        ax3.grid(True, alpha=0.3)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('ROI (%)')
        
        # 4. Métricas Resumo
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        # Tabela de métricas
        table_data = []
        headers = ['Estratégia', 'ROI (%)', 'Win Rate (%)', 'Sharpe', 'Max DD (%)']
        
        for result in results:
            table_data.append([
                result.strategy_name,
                f'{result.roi:.1f}',
                f'{result.win_rate:.1f}',
                f'{result.sharpe_ratio:.2f}',
                f'{result.max_drawdown:.1f}'
            ])
        
        table = ax4.table(cellText=table_data, colLabels=headers, 
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        
        # Colorir células baseado no ROI
        for i, result in enumerate(results):
            color = 'lightgreen' if result.roi > 0 else 'lightcoral'
            table[(i+1, 1)].set_facecolor(color)
        
        ax4.set_title('Resumo das Métricas', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig

if __name__ == "__main__":
    simulator = StrategySimulator()
    
    # Configuração das estratégias para teste
    strategies_config = {
        'flat': {'bet_amount': 50, 'initial_bankroll': 1000},
        'kelly': {'initial_bankroll': 1000, 'max_bet_pct': 0.15},
        'percentage': {'percentage': 5, 'initial_bankroll': 1000},
        'martingale': {'base_bet': 25, 'initial_bankroll': 1000, 'max_multiplier': 8}
    }
    
    # Executar comparação
    results = simulator.compare_strategies(strategies_config, days_back=180)
    
    # Mostrar resultados
    for result in results:
        print(f"\n=== {result.strategy_name} ===")
        print(f"ROI: {result.roi:.2f}%")
        print(f"Lucro Total: €{result.total_profit:.2f}")
        print(f"Win Rate: {result.win_rate:.1f}%")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Max Drawdown: {result.max_drawdown:.1f}%")
    
    # Plotar comparação
    if results:
        fig = simulator.plot_comparison(results)
        plt.show()