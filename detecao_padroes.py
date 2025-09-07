#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deteção de Padrões Lucrativos com IA
Versão 1.2 - Inteligência e Automação

Este módulo implementa algoritmos de machine learning para:
- Deteção de padrões lucrativos
- Análise preditiva com regressão
- Identificação de tendências
- Recomendações automáticas
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, r2_score
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')
from traducoes import t

@dataclass
class Pattern:
    """Representa um padrão identificado"""
    name: str
    description: str
    conditions: Dict[str, Any]
    profitability: float
    confidence: float
    sample_size: int
    win_rate: float
    avg_roi: float
    risk_level: str

@dataclass
class PredictionResult:
    """Resultado de uma predição"""
    prediction: float
    confidence: float
    features_importance: Dict[str, float]
    model_accuracy: float
    recommendation: str

class PatternDetector:
    """Detector de padrões lucrativos com IA"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.encoders = {}
    
    def load_data(self, days_back: int = 365) -> pd.DataFrame:
        """Carrega e prepara dados para análise"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Carregar todos os dados primeiro
            query = """
                SELECT 
                    data_hora as data,
                    equipa_casa,
                    equipa_fora,
                    competicao,
                    tipo_aposta,
                    valor_apostado as valor_aposta,
                    odd,
                    resultado,
                    lucro_prejuizo,
                    notas
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
                
                # Features temporais
                df['day_of_week'] = df['data'].dt.dayofweek
                df['month'] = df['data'].dt.month
                df['hour'] = df['data'].dt.hour
                
                # Features de odd
                df['odd_range'] = pd.cut(df['odd'], bins=[0, 1.5, 2.0, 3.0, 5.0, float('inf')], 
                                       labels=['Muito_Baixa', 'Baixa', 'Media', 'Alta', 'Muito_Alta'])
                
                # Features de valor
                df['valor_range'] = pd.cut(df['valor_aposta'], bins=5, labels=['Muito_Baixo', 'Baixo', 'Medio', 'Alto', 'Muito_Alto'])
                
                # Sequências
                df['sequencia_anterior'] = self._calculate_sequences(df)
                
            return df
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepara features para machine learning"""
        if df.empty:
            return pd.DataFrame(), pd.Series()
        
        # Features categóricas
        categorical_features = ['competicao', 'tipo_aposta', 'odd_range', 'valor_range']
        
        # Encoding das features categóricas
        df_encoded = df.copy()
        
        for feature in categorical_features:
            if feature in df_encoded.columns:
                if feature not in self.encoders:
                    self.encoders[feature] = LabelEncoder()
                    df_encoded[f'{feature}_encoded'] = self.encoders[feature].fit_transform(df_encoded[feature].astype(str))
                else:
                    # Para novos dados, usar o encoder já treinado
                    try:
                        df_encoded[f'{feature}_encoded'] = self.encoders[feature].transform(df_encoded[feature].astype(str))
                    except ValueError:
                        # Se houver categorias não vistas, usar a mais frequente
                        df_encoded[f'{feature}_encoded'] = 0
        
        # Features numéricas
        numeric_features = [
            'odd', 'valor_aposta', 'day_of_week', 'month', 'hour', 'sequencia_anterior'
        ] + [f'{f}_encoded' for f in categorical_features if f in df_encoded.columns]
        
        # Selecionar apenas features que existem
        available_features = [f for f in numeric_features if f in df_encoded.columns]
        
        X = df_encoded[available_features].fillna(0)
        y = df_encoded['won'] if 'won' in df_encoded.columns else pd.Series()
        
        return X, y
    
    def detect_profitable_patterns(self, df: pd.DataFrame, min_sample_size: int = 10) -> List[Pattern]:
        """Detecta padrões lucrativos nos dados"""
        patterns = []
        
        if df.empty:
            return patterns
        
        # Padrões por dia da semana
        patterns.extend(self._analyze_day_patterns(df, min_sample_size))
        
        # Padrões por faixa de odd
        patterns.extend(self._analyze_odds_patterns(df, min_sample_size))
        
        # Padrões por competição
        patterns.extend(self._analyze_competition_patterns(df, min_sample_size))
        
        # Padrões por tipo de aposta
        patterns.extend(self._analyze_bet_type_patterns(df, min_sample_size))
        
        # Padrões combinados
        patterns.extend(self._analyze_combination_patterns(df, min_sample_size))
        
        # Ordenar por lucratividade
        patterns.sort(key=lambda x: x.avg_roi, reverse=True)
        
        return patterns
    
    def _analyze_day_patterns(self, df: pd.DataFrame, min_sample_size: int) -> List[Pattern]:
        """Analisa padrões por dia da semana"""
        patterns = []
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for day_num in range(7):
            day_data = df[df['day_of_week'] == day_num]
            
            if len(day_data) >= min_sample_size:
                win_rate = (day_data['won'].sum() / len(day_data)) * 100
                avg_roi = day_data['roi'].mean()
                
                if avg_roi > 0:  # Apenas padrões lucrativos
                    risk_level = 'Baixo' if win_rate > 60 else 'Médio' if win_rate > 45 else 'Alto'
                    
                    pattern = Pattern(
                        name=f"Apostas às {days[day_num]}s",
                        description=f"Padrão lucrativo para apostas realizadas às {days[day_num]}s",
                        conditions={'day_of_week': day_num},
                        profitability=avg_roi,
                        confidence=min(win_rate / 50, 1.0),  # Normalizar confiança
                        sample_size=len(day_data),
                        win_rate=win_rate,
                        avg_roi=avg_roi,
                        risk_level=risk_level
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_odds_patterns(self, df: pd.DataFrame, min_sample_size: int) -> List[Pattern]:
        """Analisa padrões por faixa de odds"""
        patterns = []
        
        # Definir faixas de odds
        odd_ranges = [
            (1.0, 1.5, "Odds Muito Baixas"),
            (1.5, 2.0, "Odds Baixas"),
            (2.0, 3.0, "Odds Médias"),
            (3.0, 5.0, "Odds Altas"),
            (5.0, float('inf'), "Odds Muito Altas")
        ]
        
        for min_odd, max_odd, range_name in odd_ranges:
            if max_odd == float('inf'):
                range_data = df[df['odd'] >= min_odd]
            else:
                range_data = df[(df['odd'] >= min_odd) & (df['odd'] < max_odd)]
            
            if len(range_data) >= min_sample_size:
                win_rate = (range_data['won'].sum() / len(range_data)) * 100
                avg_roi = range_data['roi'].mean()
                
                if avg_roi > 0:
                    risk_level = 'Baixo' if win_rate > 60 else 'Médio' if win_rate > 45 else 'Alto'
                    
                    pattern = Pattern(
                        name=range_name,
                        description=f"Padrão lucrativo para {range_name.lower()} ({min_odd:.1f} - {max_odd if max_odd != float('inf') else '∞'})",
                        conditions={'odd_min': min_odd, 'odd_max': max_odd},
                        profitability=avg_roi,
                        confidence=min(win_rate / 50, 1.0),
                        sample_size=len(range_data),
                        win_rate=win_rate,
                        avg_roi=avg_roi,
                        risk_level=risk_level
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_competition_patterns(self, df: pd.DataFrame, min_sample_size: int) -> List[Pattern]:
        """Analisa padrões por competição"""
        patterns = []
        
        for competition in df['competicao'].unique():
            comp_data = df[df['competicao'] == competition]
            
            if len(comp_data) >= min_sample_size:
                win_rate = (comp_data['won'].sum() / len(comp_data)) * 100
                avg_roi = comp_data['roi'].mean()
                
                if avg_roi > 0:
                    risk_level = 'Baixo' if win_rate > 60 else 'Médio' if win_rate > 45 else 'Alto'
                    
                    pattern = Pattern(
                        name=f"Competição: {competition}",
                        description=f"Padrão lucrativo para apostas na {competition}",
                        conditions={'competicao': competition},
                        profitability=avg_roi,
                        confidence=min(win_rate / 50, 1.0),
                        sample_size=len(comp_data),
                        win_rate=win_rate,
                        avg_roi=avg_roi,
                        risk_level=risk_level
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_bet_type_patterns(self, df: pd.DataFrame, min_sample_size: int) -> List[Pattern]:
        """Analisa padrões por tipo de aposta"""
        patterns = []
        
        for bet_type in df['tipo_aposta'].unique():
            type_data = df[df['tipo_aposta'] == bet_type]
            
            if len(type_data) >= min_sample_size:
                win_rate = (type_data['won'].sum() / len(type_data)) * 100
                avg_roi = type_data['roi'].mean()
                
                if avg_roi > 0:
                    risk_level = 'Baixo' if win_rate > 60 else 'Médio' if win_rate > 45 else 'Alto'
                    
                    pattern = Pattern(
                        name=f"Tipo: {bet_type}",
                        description=f"Padrão lucrativo para apostas do tipo {bet_type}",
                        conditions={'tipo_aposta': bet_type},
                        profitability=avg_roi,
                        confidence=min(win_rate / 50, 1.0),
                        sample_size=len(type_data),
                        win_rate=win_rate,
                        avg_roi=avg_roi,
                        risk_level=risk_level
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_combination_patterns(self, df: pd.DataFrame, min_sample_size: int) -> List[Pattern]:
        """Analisa padrões combinados"""
        patterns = []
        
        # Combinação: Competição + Tipo de Aposta
        for competition in df['competicao'].unique():
            for bet_type in df['tipo_aposta'].unique():
                combo_data = df[(df['competicao'] == competition) & (df['tipo_aposta'] == bet_type)]
                
                if len(combo_data) >= min_sample_size:
                    win_rate = (combo_data['won'].sum() / len(combo_data)) * 100
                    avg_roi = combo_data['roi'].mean()
                    
                    if avg_roi > 5:  # Threshold mais alto para padrões combinados
                        risk_level = 'Baixo' if win_rate > 65 else 'Médio' if win_rate > 50 else 'Alto'
                        
                        pattern = Pattern(
                            name=f"{competition} + {bet_type}",
                            description=f"Padrão combinado: {bet_type} na {competition}",
                            conditions={'competicao': competition, 'tipo_aposta': bet_type},
                            profitability=avg_roi,
                            confidence=min(win_rate / 50, 1.0),
                            sample_size=len(combo_data),
                            win_rate=win_rate,
                            avg_roi=avg_roi,
                            risk_level=risk_level
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def train_prediction_model(self, df: pd.DataFrame, model_type: str = 'random_forest') -> Dict[str, Any]:
        """Treina modelo de predição"""
        try:
            X, y = self.prepare_features(df)
            
            if X.empty or y.empty:
                return {'error': 'Dados insuficientes para treinar modelo'}
            
            # Split dos dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Escalar features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Treinar modelo
            if model_type == 'random_forest':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == 'logistic':
                model = LogisticRegression(random_state=42)
            else:
                return {'error': f'Tipo de modelo não suportado: {model_type}'}
            
            model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = model.predict(X_test_scaled)
            
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1': f1_score(y_test, y_pred)
            }
            
            # Importância das features (se disponível)
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                for i, importance in enumerate(model.feature_importances_):
                    feature_importance[X.columns[i]] = importance
            
            # Salvar modelo e scaler
            self.models[model_type] = model
            self.scalers[model_type] = scaler
            
            return {
                'model_type': model_type,
                'metrics': metrics,
                'feature_importance': feature_importance,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            return {'error': f'Erro ao treinar modelo: {str(e)}'}
    
    def predict_bet_outcome(self, bet_data: Dict[str, Any], model_type: str = 'random_forest') -> Optional[PredictionResult]:
        """Prediz o resultado de uma aposta"""
        try:
            if model_type not in self.models:
                return None
            
            model = self.models[model_type]
            scaler = self.scalers[model_type]
            
            # Preparar dados da aposta
            bet_df = pd.DataFrame([bet_data])
            
            # Aplicar mesmo preprocessing
            X, _ = self.prepare_features(bet_df)
            
            if X.empty:
                return None
            
            # Escalar
            X_scaled = scaler.transform(X)
            
            # Predição
            prediction = model.predict_proba(X_scaled)[0][1]  # Probabilidade de ganhar
            
            # Importância das features
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                for i, importance in enumerate(model.feature_importances_):
                    feature_importance[X.columns[i]] = importance
            
            # Recomendação
            if prediction > 0.6:
                recommendation = "Aposta Recomendada - Alta probabilidade de sucesso"
            elif prediction > 0.45:
                recommendation = "Aposta Neutra - Probabilidade moderada"
            else:
                recommendation = "Aposta Não Recomendada - Baixa probabilidade de sucesso"
            
            return PredictionResult(
                prediction=prediction,
                confidence=abs(prediction - 0.5) * 2,  # Confiança baseada na distância de 0.5
                features_importance=feature_importance,
                model_accuracy=0.0,  # Seria necessário calcular separadamente
                recommendation=recommendation
            )
            
        except Exception as e:
            print(f"Erro na predição: {e}")
            return None
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """Gera relatório de insights"""
        try:
            df = self.load_data()
            patterns = self.detect_profitable_patterns(df)
            
            if not patterns:
                return {'error': 'Nenhum padrão encontrado'}
            
            # Estatísticas gerais
            total_patterns = len(patterns)
            high_confidence_patterns = len([p for p in patterns if p.confidence > 0.7])
            avg_profitability = np.mean([p.avg_roi for p in patterns])
            
            # Top padrões
            top_patterns = patterns[:5]
            
            # Recomendações
            recommendations = []
            for pattern in top_patterns:
                recommendations.append({
                    'pattern': pattern.name,
                    'action': f"Focar em {pattern.description.lower()}",
                    'expected_roi': pattern.avg_roi,
                    'risk': pattern.risk_level
                })
            
            return {
                'total_patterns': total_patterns,
                'high_confidence_patterns': high_confidence_patterns,
                'avg_profitability': avg_profitability,
                'top_patterns': [{
                    'name': p.name,
                    'roi': p.avg_roi,
                    'win_rate': p.win_rate,
                    'sample_size': p.sample_size,
                    'risk': p.risk_level
                } for p in top_patterns],
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {'error': f'Erro ao gerar relatório: {str(e)}'}
    
    def plot_patterns_analysis(self, save_path: Optional[str] = None):
        """Cria visualizações dos padrões"""
        try:
            df = self.load_data()
            patterns = self.detect_profitable_patterns(df)
            
            if not patterns:
                return None
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análise de Padrões Lucrativos', fontsize=16, fontweight='bold')
            
            # 1. Top Padrões por ROI
            ax1 = axes[0, 0]
            top_patterns = patterns[:10]
            names = [p.name[:20] + '...' if len(p.name) > 20 else p.name for p in top_patterns]
            rois = [p.avg_roi for p in top_patterns]
            
            bars = ax1.barh(names, rois, color='green', alpha=0.7)
            ax1.set_title('Top 10 Padrões por ROI')
            ax1.set_xlabel('ROI Médio (%)')
            
            # 2. Win Rate vs ROI
            ax2 = axes[0, 1]
            win_rates = [p.win_rate for p in patterns]
            avg_rois = [p.avg_roi for p in patterns]
            sizes = [p.sample_size for p in patterns]
            
            scatter = ax2.scatter(win_rates, avg_rois, s=sizes, alpha=0.6, c=avg_rois, cmap='RdYlGn')
            ax2.set_title('Win Rate vs ROI')
            ax2.set_xlabel('Win Rate (%)')
            ax2.set_ylabel('ROI Médio (%)')
            ax2.grid(True, alpha=0.3)
            
            plt.colorbar(scatter, ax=ax2, label='ROI (%)')
            
            # 3. Distribuição por Nível de Risco
            ax3 = axes[1, 0]
            risk_counts = {}
            for pattern in patterns:
                risk_counts[pattern.risk_level] = risk_counts.get(pattern.risk_level, 0) + 1
            
            colors = {'Baixo': 'green', 'Médio': 'orange', 'Alto': 'red'}
            wedges, texts, autotexts = ax3.pie(risk_counts.values(), labels=risk_counts.keys(), 
                                              autopct='%1.1f%%', colors=[colors.get(k, 'gray') for k in risk_counts.keys()])
            ax3.set_title('Distribuição por Nível de Risco')
            
            # 4. Evolução Temporal (se houver dados suficientes)
            ax4 = axes[1, 1]
            if not df.empty:
                monthly_roi = df.groupby(df['data'].dt.to_period('M'))['roi'].mean()
                monthly_roi.plot(ax=ax4, kind='line', marker='o')
                ax4.set_title('Evolução do ROI Mensal')
                ax4.set_xlabel('Mês')
                ax4.set_ylabel('ROI Médio (%)')
                ax4.grid(True, alpha=0.3)
                ax4.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            else:
                ax4.text(0.5, 0.5, 'Dados insuficientes\npara análise temporal', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Evolução Temporal')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            print(f"Erro ao criar gráficos: {e}")
            return None
    
    def _calculate_sequences(self, df: pd.DataFrame) -> pd.Series:
        """Calcula sequências de vitórias/derrotas anteriores"""
        sequences = []
        current_sequence = 0
        
        for _, row in df.iterrows():
            sequences.append(current_sequence)
            
            if row['won']:
                current_sequence = max(0, current_sequence) + 1
            else:
                current_sequence = min(0, current_sequence) - 1
        
        return pd.Series(sequences)

if __name__ == "__main__":
    detector = PatternDetector()
    
    # Carregar dados
    df = detector.load_data(days_back=180)
    
    if not df.empty:
        print(f"Dados carregados: {len(df)} apostas")
        
        # Detectar padrões
        patterns = detector.detect_profitable_patterns(df)
        print(f"\nPadrões detectados: {len(patterns)}")
        
        # Mostrar top 5 padrões
        for i, pattern in enumerate(patterns[:5], 1):
            print(f"\n{i}. {pattern.name}")
            print(f"   ROI: {pattern.avg_roi:.1f}%")
            print(f"   Win Rate: {pattern.win_rate:.1f}%")
            print(f"   Amostra: {pattern.sample_size} apostas")
            print(f"   Risco: {pattern.risk_level}")
        
        # Treinar modelo
        print("\nTreinando modelo de predição...")
        model_result = detector.train_prediction_model(df)
        if 'error' not in model_result:
            print(f"Modelo treinado com {model_result['training_samples']} amostras")
            print(f"Accuracy: {model_result['metrics']['accuracy']:.3f}")
        
        # Gerar relatório
        report = detector.generate_insights_report()
        if 'error' not in report:
            print(f"\n=== RELATÓRIO DE INSIGHTS ===")
            print(f"Total de padrões: {report['total_patterns']}")
            print(f"Lucratividade média: {report['avg_profitability']:.1f}%")
            print(f"Padrões de alta confiança: {report['high_confidence_patterns']}")
        
        # Plotar análise
        fig = detector.plot_patterns_analysis()
        if fig:
            plt.show()
    else:
        print("Nenhum dado encontrado para análise")