#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Machine Learning para Previsões de Apostas
Versão simplificada e funcional com análise de dados históricos reais
"""

import sqlite3
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AnalisadorHistoricoReal:
    """Analisador simplificado de dados históricos reais"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.padroes_sucesso = {}
    
    def carregar_dados_completos(self) -> pd.DataFrame:
        """Carrega todos os dados históricos do banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT 
                data_hora,
                competicao,
                tipo_aposta,
                odd,
                valor_apostado,
                resultado,
                lucro_prejuizo
            FROM apostas 
            ORDER BY data_hora
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                print("Nenhum dado encontrado na base de dados")
                return pd.DataFrame()
            
            # Converter data_hora com diferentes formatos
            try:
                df['data_hora'] = pd.to_datetime(df['data_hora'], format='%d/%m/%Y %H:%M')
            except:
                try:
                    df['data_hora'] = pd.to_datetime(df['data_hora'], format='%m/%d/%Y %H:%M')
                except:
                    try:
                        df['data_hora'] = pd.to_datetime(df['data_hora'], dayfirst=True)
                    except:
                        df['data_hora'] = pd.to_datetime(df['data_hora'], format='mixed')
            
            # Criar resultado binário (aceitar diferentes formatos)
            df['resultado_binario'] = ((df['resultado'] == 'Ganhou') | 
                                     (df['resultado'] == 'Ganha') | 
                                     (df['resultado'] == 'G')).astype(int)
            
            return df
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def extrair_features_avancadas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrai features básicas dos dados"""
        if df.empty:
            return df
        
        df = df.copy()
        df = df.sort_values('data_hora').reset_index(drop=True)
        
        # Features temporais
        df['dia_semana'] = df['data_hora'].dt.dayofweek
        df['mes'] = df['data_hora'].dt.month
        df['hora'] = df['data_hora'].dt.hour
        df['fim_semana'] = (df['dia_semana'] >= 5).astype(int)
        
        # Taxa de sucesso móvel simples
        for janela in [5, 10, 20, 30]:
            df[f'taxa_sucesso_{janela}'] = df['resultado_binario'].rolling(
                window=janela, min_periods=1
            ).mean()
        
        # Features de odd
        df['faixa_odd_num'] = 2  # Valor padrão
        df.loc[df['odd'] <= 1.5, 'faixa_odd_num'] = 0  # baixa
        df.loc[(df['odd'] > 1.5) & (df['odd'] <= 2.0), 'faixa_odd_num'] = 1  # media_baixa
        df.loc[(df['odd'] > 2.0) & (df['odd'] <= 3.0), 'faixa_odd_num'] = 2  # media
        df.loc[(df['odd'] > 3.0) & (df['odd'] <= 5.0), 'faixa_odd_num'] = 3  # alta
        df.loc[df['odd'] > 5.0, 'faixa_odd_num'] = 4  # muito_alta
        
        # Features de valor
        valor_q33 = df['valor_apostado'].quantile(0.33)
        valor_q66 = df['valor_apostado'].quantile(0.66)
        
        df['categoria_valor_num'] = 1  # Valor padrão (médio)
        df.loc[df['valor_apostado'] <= valor_q33, 'categoria_valor_num'] = 0  # baixo
        df.loc[df['valor_apostado'] > valor_q66, 'categoria_valor_num'] = 2  # alto
        
        # Sequências de vitórias/derrotas
        df['sequencia_vitorias'] = 0
        df['sequencia_derrotas'] = 0
        
        seq_vit = 0
        seq_der = 0
        
        for i in range(len(df)):
            if df.iloc[i]['resultado_binario'] == 1:
                seq_vit += 1
                seq_der = 0
            else:
                seq_der += 1
                seq_vit = 0
            
            df.at[i, 'sequencia_vitorias'] = seq_vit
            df.at[i, 'sequencia_derrotas'] = seq_der
        
        # ROI móvel simples
        for janela in [10, 20, 30]:
            lucro_janela = df['lucro_prejuizo'].rolling(window=janela, min_periods=1).sum()
            investimento_janela = df['valor_apostado'].rolling(window=janela, min_periods=1).sum()
            df[f'roi_{janela}'] = lucro_janela / (investimento_janela + 0.001)  # Evitar divisão por zero
        
        # Volatilidade das odds
        df['volatilidade_odd'] = df['odd'].rolling(window=5, min_periods=1).std()
        
        # Média de odds recentes
        df['media_odd_10'] = df['odd'].rolling(window=10, min_periods=1).mean()
        
        # Momentum de vitórias
        df['momentum_5'] = df['resultado_binario'].rolling(window=5, min_periods=1).sum()
        
        # Tendência de melhoria
        df['tendencia_melhoria'] = (
            df['taxa_sucesso_10'] > df['taxa_sucesso_20']
        ).astype(int)
        
        # Features de tipo de aposta
        df['tipo_1x2'] = (df['tipo_aposta'] == '1X2').astype(int)
        df['tipo_over_under'] = (df['tipo_aposta'].str.contains('Total', na=False)).astype(int)
        df['tipo_handicap'] = (df['tipo_aposta'].str.contains('Handicap', na=False)).astype(int)
        
        # Features de competição
        comp_principais = df['competicao'].value_counts().head(5).index.tolist()
        for i, comp in enumerate(comp_principais):
            df[f'comp_principal_{i}'] = (df['competicao'] == comp).astype(int)
        
        # Preencher valores nulos
        df = df.fillna(0)
        
        return df
    
    def analisar_padroes_sucesso(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões específicos que levam ao sucesso"""
        padroes = {}
        
        # Análise por dia da semana
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        padroes_dia = {}
        for dia in range(7):
            mask = df['dia_semana'] == dia
            if mask.sum() > 0:
                taxa_sucesso = df[mask]['resultado_binario'].mean()
                padroes_dia[dias_semana[dia]] = {
                    'taxa_sucesso': taxa_sucesso,
                    'total_apostas': mask.sum()
                }
        padroes['dias_semana'] = padroes_dia
        
        # Análise por faixa de odd
        faixas_odd = ['Baixa (≤1.5)', 'Média-Baixa (1.5-2.0)', 'Média (2.0-3.0)', 'Alta (3.0-5.0)', 'Muito Alta (>5.0)']
        padroes_odd = {}
        for i, faixa in enumerate(faixas_odd):
            mask = df['faixa_odd_num'] == i
            if mask.sum() > 0:
                taxa_sucesso = df[mask]['resultado_binario'].mean()
                padroes_odd[faixa] = {
                    'taxa_sucesso': taxa_sucesso,
                    'total_apostas': mask.sum()
                }
        padroes['faixas_odd'] = padroes_odd
        
        # Análise por tipo de aposta
        if 'tipo_aposta' in df.columns:
            tipos_aposta = df['tipo_aposta'].value_counts().head(5).index.tolist()
            padroes_tipo = {}
            for tipo in tipos_aposta:
                mask = df['tipo_aposta'] == tipo
                if mask.sum() > 0:
                    taxa_sucesso = df[mask]['resultado_binario'].mean()
                    padroes_tipo[tipo] = {
                        'taxa_sucesso': taxa_sucesso,
                        'total_apostas': mask.sum()
                    }
            padroes['tipos_aposta'] = padroes_tipo
        
        # Análise de sequências
        padroes_seq = {}
        for n in range(1, 6):
            mask = df['sequencia_derrotas'] == n
            if mask.sum() > 0:
                # Próxima aposta após N derrotas
                indices_proximas = mask[mask].index + 1
                indices_validos = indices_proximas[indices_proximas < len(df)]
                if len(indices_validos) > 0:
                    prob_vitoria = df.loc[indices_validos, 'resultado_binario'].mean()
                    padroes_seq[f'apos_{n}_derrotas'] = {
                        'prob_vitoria_proxima': prob_vitoria,
                        'ocorrencias': len(indices_validos)
                    }
        padroes['sequencias'] = padroes_seq
        
        self.padroes_sucesso = padroes
        return padroes
    
    def processar_dados(self, df: pd.DataFrame, treino: bool = True) -> pd.DataFrame:
        """Processa dados para machine learning"""
        df = df.copy()
        
        # Criar target binário (1 = ganha, 0 = perde)
        if 'status' in df.columns:
            df['resultado_binario'] = (df['status'] == 'ganha').astype(int)
        elif 'resultado' in df.columns:
            df['resultado_binario'] = (df['resultado'] == 'Ganha').astype(int)
        
        # Converter data_aposta para datetime se necessário
        if 'data_aposta' in df.columns:
            df['data_aposta'] = pd.to_datetime(df['data_aposta'], errors='coerce')
        
        # Extrair features avançadas
        df = self.extrair_features_avancadas(df)
        
        # Preencher valores nulos
        df = df.fillna(0)
        
        return df
    
    def obter_features_modelo(self) -> List[str]:
        """Retorna lista de features para o modelo"""
        features = [
            'odd', 'valor_apostado', 'dia_semana', 'mes', 'hora', 'fim_semana',
            'taxa_sucesso_10', 'sequencia_vitorias', 'roi_10', 'volatilidade_odd',
            'faixa_odd_num', 'categoria_valor_num', 'momentum_5', 'tendencia_melhoria',
            'tipo_1x2', 'tipo_over_under', 'tipo_handicap'
        ]
        
        return features

class ModeloMLSimples:
    """Modelo de Machine Learning simplificado para previsões de apostas"""
    
    def __init__(self):
        self.pesos = {}
        self.padroes = {}
        self.features_importantes = []
        self.metricas = {}
        
    def treinar(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Treina o modelo usando regressão logística manual e análise de padrões"""
        if len(X) < 10:
            raise ValueError("Dados insuficientes para treino (mínimo 10 amostras)")
        
        # Dividir dados temporalmente (80% treino, 20% teste)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Selecionar features numéricas (excluir target)
        features_numericas = X_train.select_dtypes(include=[np.number]).columns.tolist()
        # Remover a variável target se estiver presente
        if 'resultado_binario' in features_numericas:
            features_numericas.remove('resultado_binario')
        if 'lucro_prejuizo' in features_numericas:
            features_numericas.remove('lucro_prejuizo')  # Também é derivada do resultado
        
        X_train_num = X_train[features_numericas].fillna(0)
        X_test_num = X_test[features_numericas].fillna(0)
        
        # Normalizar dados
        for col in features_numericas:
            mean_val = X_train_num[col].mean()
            std_val = X_train_num[col].std()
            if std_val > 0:
                X_train_num[col] = (X_train_num[col] - mean_val) / std_val
                X_test_num[col] = (X_test_num[col] - mean_val) / std_val
        
        # Regressão logística manual (gradiente descendente)
        self.pesos = {col: 0.0 for col in features_numericas}
        learning_rate = 0.01
        epochs = 1000
        
        for epoch in range(epochs):
            for i in range(len(X_train_num)):
                # Forward pass
                z = sum(self.pesos[col] * X_train_num.iloc[i][col] for col in features_numericas)
                pred = 1 / (1 + np.exp(-z)) if z > -500 else 0.0
                
                # Backward pass
                error = y_train.iloc[i] - pred
                for col in features_numericas:
                    self.pesos[col] += learning_rate * error * X_train_num.iloc[i][col]
        
        # Fazer previsões
        y_pred_train = []
        for i in range(len(X_train_num)):
            z = sum(self.pesos[col] * X_train_num.iloc[i][col] for col in features_numericas)
            prob = 1 / (1 + np.exp(-z)) if z > -500 else 0.0
            y_pred_train.append(1 if prob > 0.5 else 0)
        
        y_pred_test = []
        for i in range(len(X_test_num)):
            z = sum(self.pesos[col] * X_test_num.iloc[i][col] for col in features_numericas)
            prob = 1 / (1 + np.exp(-z)) if z > -500 else 0.0
            y_pred_test.append(1 if prob > 0.5 else 0)
        
        # Calcular métricas
        acuracia_treino = sum(1 for i in range(len(y_train)) if y_pred_train[i] == y_train.iloc[i]) / len(y_train)
        acuracia_teste = sum(1 for i in range(len(y_test)) if y_pred_test[i] == y_test.iloc[i]) / len(y_test) if len(y_test) > 0 else 0
        
        # Importância das features (valor absoluto dos pesos)
        feature_importance = [(col, abs(peso)) for col, peso in self.pesos.items()]
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        self.features_importantes = feature_importance[:10]
        
        self.metricas = {
            'acuracia_treino': acuracia_treino,
            'acuracia_teste': acuracia_teste,
            'total_amostras': len(X),
            'amostras_treino': len(X_train),
            'amostras_teste': len(X_test),
            'balanco_classes': y.value_counts().to_dict(),
            'feature_importance': self.features_importantes
        }
        
        return self.metricas
    
    def prever(self, X: pd.DataFrame) -> tuple:
        """Faz previsões com o modelo treinado"""
        if not self.pesos:
            raise ValueError("Modelo não foi treinado")
        
        # Preparar dados
        X_num = X.select_dtypes(include=[np.number]).fillna(0)
        
        # Calcular probabilidade
        z = sum(self.pesos.get(col, 0) * X_num.iloc[0][col] for col in X_num.columns if col in self.pesos)
        probabilidade = 1 / (1 + np.exp(-z)) if z > -500 else 0.0
        
        predicao = 1 if probabilidade > 0.5 else 0
        confianca = abs(probabilidade - 0.5) * 2
        
        return probabilidade, predicao, confianca

class ModeloPrevisao:
    """Classe para modelo de previsão de resultados"""
    
    def __init__(self, tipo_modelo: str = 'random_forest'):
        self.tipo_modelo = tipo_modelo
        self.modelo = None
        self.preprocessador = AnalisadorHistoricoReal()
        self.metricas = {}
        self.data_treino = None
        
        # Inicializar modelo baseado no tipo
        if tipo_modelo == 'random_forest':
            try:
                from sklearn.ensemble import RandomForestClassifier
                self.modelo = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
            except ImportError:
                self.modelo = ModeloMLSimples()
        elif tipo_modelo == 'gradient_boosting':
            try:
                from sklearn.ensemble import GradientBoostingClassifier
                self.modelo = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
            except ImportError:
                self.modelo = ModeloMLSimples()
        elif tipo_modelo == 'logistic_regression':
            try:
                from sklearn.linear_model import LogisticRegression
                self.modelo = LogisticRegression(
                    random_state=42,
                    max_iter=1000
                )
            except ImportError:
                self.modelo = ModeloMLSimples()
        else:
            self.modelo = ModeloMLSimples()
    
    def treinar(self, dados: pd.DataFrame) -> Dict:
        """Treina o modelo com os dados fornecidos usando análise simplificada"""
        try:
            # Usar dados históricos completos se disponível
            if hasattr(dados, 'empty') and not dados.empty:
                # Se dados já foram passados, usar diretamente
                df_raw = dados
            else:
                # Carregar dados completos do analisador
                df_raw = self.preprocessador.carregar_dados_completos()
            
            if df_raw.empty or len(df_raw) < 10:
                return {
                    'sucesso': False,
                    'erro': f'Dados insuficientes para treino (apenas {len(df_raw)} registros, mínimo 10)'
                }
            
            # Extrair features avançadas
            df_processed = self.preprocessador.extrair_features_avancadas(df_raw)
            
            # Preparar dados para treino
            X = df_processed.select_dtypes(include=[np.number]).fillna(0)
            y = df_processed['resultado_binario']
            
            # Remover linhas com valores nulos no target
            mask_valido = ~y.isna()
            X = X[mask_valido]
            y = y[mask_valido]
            
            if len(X) < 10:
                return {
                    'sucesso': False,
                    'erro': f'Dados válidos insuficientes para treino (apenas {len(X)} registros válidos)'
                }
            
            # Treinar modelo
            if isinstance(self.modelo, ModeloMLSimples):
                resultado_treino = self.modelo.treinar(X, y)
                
                # Analisar padrões de sucesso nos dados processados
                try:
                    padroes = self.preprocessador.analisar_padroes_sucesso(df_processed)
                    resultado_treino['padroes_sucesso'] = padroes
                except:
                    pass  # Se falhar, continuar sem padrões
                
                self.data_treino = datetime.now()
                self.metricas = resultado_treino
                
                return {
                    'sucesso': True,
                    'metricas': resultado_treino,
                    'data_treino': self.data_treino.isoformat(),
                    'acuracia_treino': resultado_treino.get('acuracia_treino', 0),
                    'acuracia_teste': resultado_treino.get('acuracia_teste', 0),
                    'auc_score': 0,
                    'features_importantes': resultado_treino.get('feature_importance', [])[:5]
                }
            else:
                # Fallback para sklearn se disponível
                try:
                    from sklearn.metrics import accuracy_score, roc_auc_score, cross_val_score
                    
                    # Divisão temporal dos dados (mais realista)
                    # 80% mais antigos para treino, 20% mais recentes para teste
                    split_idx = int(len(X) * 0.8)
                    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
                    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
                    
                    # Treinar modelo
                    self.modelo.fit(X_train, y_train)
                    
                    # Avaliar modelo
                    y_pred_train = self.modelo.predict(X_train)
                    y_pred_test = self.modelo.predict(X_test)
                    y_pred_proba_test = self.modelo.predict_proba(X_test)[:, 1]
                    
                    # Salvar features do treino para usar na previsão
                    self.features_treino = X.columns.tolist()
                    
                    # Calcular métricas detalhadas
                    acuracia_treino = accuracy_score(y_train, y_pred_train)
                    acuracia_teste = accuracy_score(y_test, y_pred_test)
                    auc_score = roc_auc_score(y_test, y_pred_proba_test)
                    
                    self.metricas = {
                        'acuracia_treino': acuracia_treino,
                        'acuracia_teste': acuracia_teste,
                        'auc_score': auc_score,
                        'total_amostras': len(X),
                        'amostras_treino': len(X_train),
                        'amostras_teste': len(X_test),
                        'features_utilizadas': X.columns.tolist(),
                        'balanceamento_classes': y.value_counts().to_dict()
                    }
                    
                    # Cross-validation se houver dados suficientes
                    if len(X) >= 50:
                        cv_scores = cross_val_score(self.modelo, X, y, cv=5, scoring='accuracy')
                        self.metricas['cv_media'] = cv_scores.mean()
                        self.metricas['cv_std'] = cv_scores.std()
                    
                    # Importância das features
                    features_importantes = []
                    if hasattr(self.modelo, 'feature_importances_'):
                        importancias = dict(zip(X.columns, self.modelo.feature_importances_))
                        features_importantes = sorted(
                            importancias.items(), key=lambda x: x[1], reverse=True
                        )
                        self.metricas['importancia_features'] = features_importantes
                    
                    # Analisar padrões de sucesso nos dados processados
                    try:
                        padroes = self.preprocessador.analisar_padroes_sucesso(df_processed)
                        self.metricas['padroes_sucesso'] = padroes
                    except:
                        pass  # Se falhar, continuar sem padrões
                    
                    self.data_treino = datetime.now()
                    
                    return {
                        'sucesso': True,
                        'metricas': self.metricas,
                        'data_treino': self.data_treino.isoformat(),
                        'acuracia_treino': acuracia_treino,
                        'acuracia_teste': acuracia_teste,
                        'auc_score': auc_score,
                        'features_importantes': features_importantes[:5]
                    }
                    
                except ImportError:
                    # Se sklearn não estiver disponível, usar modelo simples
                    modelo_simples = ModeloMLSimples()
                    resultado_treino = modelo_simples.treinar(X, y)
                    
                    self.modelo = modelo_simples
                    self.data_treino = datetime.now()
                    self.metricas = resultado_treino
                    
                    return {
                        'sucesso': True,
                        'metricas': resultado_treino,
                        'data_treino': self.data_treino.isoformat(),
                        'acuracia_treino': resultado_treino.get('acuracia_treino', 0),
                        'acuracia_teste': resultado_treino.get('acuracia_teste', 0),
                        'auc_score': 0,
                        'features_importantes': resultado_treino.get('feature_importance', [])[:5]
                    }
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro no treino: {str(e)}'
            }
    
    def prever(self, dados: pd.DataFrame) -> Dict:
        """Faz previsão para novos dados"""
        try:
            if self.modelo is None:
                return {
                    'sucesso': False,
                    'erro': 'Modelo não foi treinado'
                }
            
            # Preprocessar dados
            dados_processados = self.preprocessador.processar_dados(dados, treino=False)
            
            # Obter features
            features = self.preprocessador.obter_features_modelo()
            features_disponiveis = [f for f in features if f in dados_processados.columns]
            
            # Garantir que temos as mesmas features do treino
            if hasattr(self, 'features_treino'):
                features_disponiveis = [f for f in self.features_treino if f in dados_processados.columns]
            
            X = dados_processados[features_disponiveis]
            
            # Verificar se X tem a forma correta (2D)
            if X.ndim != 2:
                X = X.values.reshape(1, -1) if X.ndim == 1 else X.values
            
            # Verificar se é ModeloMLSimples ou modelo sklearn
            if hasattr(self.modelo, 'prever') and callable(getattr(self.modelo, 'prever')):
                # É ModeloMLSimples - usar interface específica
                probabilidade, previsao, confianca = self.modelo.prever(X)
                
                resultados = [{
                    'previsao': 'ganha' if previsao == 1 else 'perde',
                    'probabilidade_ganha': probabilidade,
                    'probabilidade_perde': 1 - probabilidade,
                    'confianca': confianca
                }]
            else:
                # É modelo sklearn - usar interface padrão
                probabilidades = self.modelo.predict_proba(X)
                previsoes = self.modelo.predict(X)
                
                resultados = []
                for i, (prev, prob) in enumerate(zip(previsoes, probabilidades)):
                    resultados.append({
                        'previsao': 'ganha' if prev == 1 else 'perde',
                        'probabilidade_ganha': prob[1] if len(prob) > 1 else prob[0],
                        'probabilidade_perde': prob[0] if len(prob) > 1 else 1 - prob[0],
                        'confianca': max(prob)
                    })
            
            return {
                'sucesso': True,
                'previsoes': resultados
            }
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro na previsão: {str(e)}'
            }
    
    def salvar_modelo(self, caminho: str) -> bool:
        """Salva modelo treinado"""
        try:
            if self.modelo is None:
                return False
            
            dados_modelo = {
                'modelo': self.modelo,
                'preprocessador': self.preprocessador,
                'metricas': self.metricas,
                'tipo_modelo': self.tipo_modelo,
                'data_treino': self.data_treino.isoformat() if self.data_treino else None
            }
            
            import json
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump({
                    'tipo_modelo': self.tipo_modelo,
                    'data_treino': dados_modelo['data_treino'],
                    'metricas': dados_modelo['metricas'],
                    'pesos': dados_modelo['modelo'].pesos if isinstance(dados_modelo['modelo'], ModeloMLSimples) else {},
                    'features_importantes': dados_modelo['modelo'].features_importantes if isinstance(dados_modelo['modelo'], ModeloMLSimples) else []
                }, f, indent=2, ensure_ascii=False)
            return True
        
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
            return False
    
    def carregar_modelo(self, caminho: str) -> bool:
        """Carrega modelo salvo"""
        try:
            if not os.path.exists(caminho):
                return False
            
            import json
            with open(caminho, 'r', encoding='utf-8') as f:
                dados_modelo = json.load(f)
            
            self.modelo = ModeloMLSimples()
            if 'pesos' in dados_modelo:
                self.modelo.pesos = dados_modelo['pesos']
            if 'features_importantes' in dados_modelo:
                self.modelo.features_importantes = dados_modelo['features_importantes']
            
            self.preprocessador = AnalisadorHistoricoReal()
            self.metricas = dados_modelo.get('metricas', {})
            self.tipo_modelo = dados_modelo.get('tipo_modelo', 'modelo_simples')
            
            if dados_modelo.get('data_treino'):
                self.data_treino = datetime.fromisoformat(dados_modelo['data_treino'])
            
            return True
        
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False

class GestorML:
    """Classe principal para gestão de machine learning"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.modelos = {}
        self.modelo_ativo = None
        self.diretorio_modelos = "modelos_ml"
        self.analisador = AnalisadorHistoricoReal(db_path)
        self.modelo_ml = ModeloMLSimples()
        self.historico_treinos = []
        
        # Criar diretório de modelos se não existir
        if not os.path.exists(self.diretorio_modelos):
            os.makedirs(self.diretorio_modelos)
    
    def carregar_dados_apostas(self, limite_dias: int = 365) -> pd.DataFrame:
        """Carrega dados de apostas usando o analisador melhorado"""
        try:
            # Usar o método melhorado do analisador
            analisador = AnalisadorHistoricoReal(self.db_path)
            df_completo = analisador.carregar_dados_completos()
            
            if df_completo.empty:
                return df_completo
            
            # Filtrar pelos últimos N dias se especificado
            if limite_dias > 0:
                data_limite = datetime.now() - timedelta(days=limite_dias)
                df_filtrado = df_completo[df_completo['data_hora'] >= data_limite]
                
                # Adicionar campos necessários para compatibilidade
                if not df_filtrado.empty:
                    df_filtrado = df_filtrado.copy()
                    df_filtrado['evento'] = df_filtrado.apply(
                        lambda row: f"{row.get('equipa_casa', 'Casa')} vs {row.get('equipa_fora', 'Fora')}", 
                        axis=1
                    )
                    df_filtrado['data_aposta'] = df_filtrado['data_hora']
                    df_filtrado['status'] = df_filtrado['resultado'].map({
                        'Ganha': 'ganha',
                        'Perdida': 'perdida'
                    }).fillna('pendente')
                    
                    # Adicionar categoria do evento baseada na competição
                    if 'competicao' in df_filtrado.columns:
                        df_filtrado['categoria_evento'] = df_filtrado['competicao'].apply(self._extrair_categoria_evento)
                
                return df_filtrado
            
            return df_completo
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _extrair_categoria_evento(self, competicao: str) -> str:
        """Extrai categoria do evento baseada na competição"""
        if not competicao:
            return 'outros'
            
        comp_lower = competicao.lower()
        
        # Ligas de futebol
        if any(palavra in comp_lower for palavra in ['liga', 'premier', 'bundesliga', 'serie a', 'la liga', 'ligue', 'championship', 'primeira']):
            return 'futebol'
        elif any(palavra in comp_lower for palavra in ['nba', 'euroleague', 'basquete', 'basketball']):
            return 'basquete'
        elif any(palavra in comp_lower for palavra in ['atp', 'wta', 'tenis', 'tennis', 'roland garros', 'wimbledon']):
            return 'tenis'
        elif any(palavra in comp_lower for palavra in ['nfl', 'nhl', 'mlb']):
            return 'americano'
        else:
            return 'futebol'  # Default para futebol
    
    def treinar_modelo(self, tipo_modelo: str = 'random_forest', 
                      limite_dias: int = 365) -> Dict:
        """Treina novo modelo de previsão"""
        try:
            # Carregar dados
            dados = self.carregar_dados_apostas(limite_dias)
            
            if dados.empty:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum dado disponível para treino'
                }
            
            # Criar e treinar modelo
            modelo = ModeloPrevisao(tipo_modelo)
            resultado_treino = modelo.treinar(dados)
            
            if resultado_treino['sucesso']:
                # Salvar modelo
                nome_modelo = f"{tipo_modelo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                caminho_modelo = os.path.join(self.diretorio_modelos, f"{nome_modelo}.json")
                
                if modelo.salvar_modelo(caminho_modelo):
                    self.modelos[nome_modelo] = {
                        'modelo': modelo,
                        'caminho': caminho_modelo,
                        'tipo': tipo_modelo,
                        'data_treino': datetime.now(),
                        'metricas': resultado_treino['metricas']
                    }
                    
                    # Definir como modelo ativo se for o primeiro ou melhor
                    if (self.modelo_ativo is None or 
                        resultado_treino['metricas']['acuracia_teste'] > 
                        self.modelos[self.modelo_ativo]['metricas']['acuracia_teste']):
                        self.modelo_ativo = nome_modelo
                    
                    resultado_treino['nome_modelo'] = nome_modelo
                    resultado_treino['modelo_ativo'] = (nome_modelo == self.modelo_ativo)
            
            return resultado_treino
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro no treino do modelo: {str(e)}'
            }
    
    def fazer_previsao(self, dados_aposta) -> Dict:
        """Faz previsão para uma nova aposta"""
        try:
            if self.modelo_ativo is None:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum modelo ativo disponível'
                }
            
            # Converter dados para DataFrame se necessário
            if isinstance(dados_aposta, dict):
                df = pd.DataFrame([dados_aposta])
            elif isinstance(dados_aposta, pd.DataFrame):
                df = dados_aposta.copy()
            else:
                return {
                    'sucesso': False,
                    'erro': 'Dados devem ser dict ou DataFrame'
                }
            
            # Adicionar dados históricos para calcular features históricas
            dados_historicos = self.carregar_dados_apostas(30)  # Últimos 30 dias
            if not dados_historicos.empty:
                # Combinar dados históricos com nova aposta
                df_completo = pd.concat([dados_historicos, df], ignore_index=True)
            else:
                df_completo = df.copy()
            
            # Fazer previsão com dados completos
            modelo = self.modelos[self.modelo_ativo]['modelo']
            resultado = modelo.prever(df_completo)
            
            if resultado['sucesso']:
                # Retornar a última previsão (da nova aposta)
                previsao = resultado['previsoes'][-1]
                
                return {
                    'sucesso': True,
                    'previsao': previsao['previsao'],
                    'probabilidade_vitoria': previsao['probabilidade_ganha'],
                    'probabilidade_derrota': previsao['probabilidade_perde'],
                    'confianca': previsao['confianca'],
                    'modelo_utilizado': self.modelo_ativo,
                    'data_previsao': datetime.now().isoformat()
                }
            
            return resultado
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro na previsão: {str(e)}'
            }
    
    def listar_modelos(self) -> List[Dict]:
        """Lista todos os modelos disponíveis"""
        modelos_info = []
        
        for nome, info in self.modelos.items():
            modelos_info.append({
                'nome': nome,
                'tipo': info['tipo'],
                'data_treino': info['data_treino'].isoformat(),
                'acuracia_teste': info['metricas'].get('acuracia_teste', 0),
                'total_amostras': info['metricas'].get('total_amostras', 0),
                'ativo': (nome == self.modelo_ativo)
            })
        
        return sorted(modelos_info, key=lambda x: x['data_treino'], reverse=True)
    
    def definir_modelo_ativo(self, nome_modelo: str) -> bool:
        """Define modelo ativo"""
        if nome_modelo in self.modelos:
            self.modelo_ativo = nome_modelo
            return True
        return False
    
    def carregar_modelos_salvos(self):
        """Carrega modelos salvos do disco"""
        try:
            if not os.path.exists(self.diretorio_modelos):
                return
            
            for arquivo in os.listdir(self.diretorio_modelos):
                if arquivo.endswith('.json'):
                    caminho_completo = os.path.join(self.diretorio_modelos, arquivo)
                    nome_modelo = arquivo[:-5]  # Remover .json
                    
                    modelo = ModeloPrevisao()
                    if modelo.carregar_modelo(caminho_completo):
                        self.modelos[nome_modelo] = {
                            'modelo': modelo,
                            'caminho': caminho_completo,
                            'tipo': modelo.tipo_modelo,
                            'data_treino': modelo.data_treino,
                            'metricas': modelo.metricas
                        }
                        
                        # Definir primeiro modelo como ativo
                        if self.modelo_ativo is None:
                            self.modelo_ativo = nome_modelo
        
        except Exception as e:
            print(f"Erro ao carregar modelos salvos: {e}")
    
    def avaliar_modelo_atual(self) -> Dict:
        """Avalia performance do modelo atual com dados recentes"""
        try:
            if self.modelo_ativo is None:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum modelo ativo'
                }
            
            # Carregar dados recentes
            dados_recentes = self.carregar_dados_apostas(30)
            
            if dados_recentes.empty:
                return {
                    'sucesso': False,
                    'erro': 'Sem dados recentes para avaliação'
                }
            
            modelo = self.modelos[self.modelo_ativo]['modelo']
            resultado = modelo.prever(dados_recentes)
            
            if resultado['sucesso']:
                # Calcular acurácia nas previsões recentes
                previsoes = resultado['previsoes']
                resultados_reais = (dados_recentes['status'] == 'ganha').astype(int).tolist()
                previsoes_binarias = [1 if p['previsao'] == 'ganha' else 0 for p in previsoes]
                
                acuracia_recente = accuracy_score(resultados_reais, previsoes_binarias)
                
                return {
                    'sucesso': True,
                    'acuracia_recente': acuracia_recente,
                    'total_previsoes': len(previsoes),
                    'modelo': self.modelo_ativo,
                    'periodo_avaliacao': '30 dias'
                }
            
            return resultado
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro na avaliação: {str(e)}'
            }
    
    def calcular_previsao_personalizada(self, dados_jogo: Dict) -> Dict:
        """Calcula previsão personalizada para um jogo específico"""
        try:
            if self.modelo_ativo is None:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum modelo ativo disponível'
                }
            
            # Criar DataFrame com os dados do jogo
            dados_aposta = {
                'evento': f"{dados_jogo.get('casa', 'Casa')} vs {dados_jogo.get('visitante', 'Visitante')}",
                'tipo_aposta': '1X2',  # Tipo padrão
                'odd': dados_jogo.get('odds', [2.0])[0] if dados_jogo.get('odds') else 2.0,
                'valor_apostado': 10.0,  # Valor padrão para cálculo
                'competicao': 'Liga',  # Competição padrão
                'data_aposta': datetime.now().isoformat()
            }
            
            # Fazer previsão usando o método existente
            resultado_previsao = self.fazer_previsao(dados_aposta)
            
            if resultado_previsao['sucesso']:
                # Calcular probabilidades para todos os resultados (1, X, 2)
                odds = dados_jogo.get('odds', [2.0, 3.0, 3.5])
                
                # Probabilidades implícitas das odds
                prob_implicitas = [1/odd for odd in odds] if len(odds) >= 3 else [0.5, 0.3, 0.2]
                total_prob = sum(prob_implicitas)
                prob_normalizadas = [p/total_prob for p in prob_implicitas]
                
                # Ajustar com a previsão do modelo
                confianca_modelo = resultado_previsao['confianca']
                prob_vitoria_modelo = resultado_previsao['probabilidade_vitoria']
                
                # Combinar probabilidades do modelo com odds do mercado
                peso_modelo = min(confianca_modelo, 0.7)  # Máximo 70% de peso para o modelo
                peso_mercado = 1 - peso_modelo
                
                prob_final_casa = (peso_modelo * prob_vitoria_modelo + 
                                 peso_mercado * prob_normalizadas[0])
                prob_final_empate = peso_mercado * prob_normalizadas[1]
                prob_final_fora = (peso_modelo * (1 - prob_vitoria_modelo) + 
                                 peso_mercado * prob_normalizadas[2])
                
                # Normalizar probabilidades finais
                total_final = prob_final_casa + prob_final_empate + prob_final_fora
                prob_final_casa /= total_final
                prob_final_empate /= total_final
                prob_final_fora /= total_final
                
                # Determinar resultado mais provável
                probabilidades = {
                    'Casa': prob_final_casa,
                    'Empate': prob_final_empate,
                    'Fora': prob_final_fora
                }
                
                resultado_previsto = max(probabilidades, key=probabilidades.get)
                confianca_final = max(probabilidades.values())
                
                return {
                    'sucesso': True,
                    'previsao': {
                        'resultado': resultado_previsto,
                        'confianca': confianca_final,
                        'probabilidades': probabilidades,
                        'jogo': f"{dados_jogo.get('casa', 'Casa')} vs {dados_jogo.get('visitante', 'Visitante')}",
                        'odds_utilizadas': odds,
                        'modelo_utilizado': self.modelo_ativo
                    }
                }
            else:
                return resultado_previsao
                
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro no cálculo personalizado: {str(e)}'
            }

class GestorMLSimples:
    """Gestor simplificado do sistema de Machine Learning"""
    
    def __init__(self):
        self.analisador = AnalisadorHistoricoReal()
        self.modelo_ml = ModeloMLSimples()
        self.modelo_previsao = ModeloPrevisao(tipo_modelo='simples')
        self.historico_treinos = []
        
    def treinar_modelo(self, forcar_retreino: bool = False) -> dict:
        """Treina o modelo ML com dados históricos usando sistema simplificado"""
        try:
            print("=== INICIANDO TREINO DO MODELO ML SIMPLIFICADO ===")
            
            # Carregar dados históricos
            dados = self.analisador.carregar_dados_completos()
            
            if dados.empty:
                return {'erro': 'Nenhum dado histórico disponível'}
            
            print(f"Dados carregados: {len(dados)} registros")
            
            # Extrair features básicas
            dados_processados = self.analisador.extrair_features_avancadas(dados)
            print(f"Features extraídas: {dados_processados.shape[1]} colunas")
            
            # Preparar dados para ML
            X = dados_processados.select_dtypes(include=[np.number]).fillna(0)
            y = dados_processados['resultado_binario']
            
            # Remover dados com target nulo
            mask_valido = ~y.isna()
            X = X[mask_valido]
            y = y[mask_valido]
            
            if len(X) < 10:
                return {'erro': f'Dados insuficientes para ML: {len(X)} amostras'}
            
            print(f"Dados para ML: {len(X)} amostras")
            print(f"Features utilizadas: {len(X.columns)}")
            print(f"Distribuição de classes: {y.value_counts().to_dict()}")
            
            # Treinar apenas o modelo ML (evitar duplicação)
            print("Treinando modelo ML...")
            resultado_ml = self.modelo_ml.treinar(X, y)
            
            # Analisar padrões de sucesso (usar dados processados)
            print("Analisando padrões de sucesso...")
            padroes_sucesso = self.analisador.analisar_padroes_sucesso(dados_processados)
            
            # Compilar resultado final
            resultado_final = {
                'sucesso': True,
                'timestamp': datetime.now().isoformat(),
                'dados_utilizados': len(dados),
                'amostras_ml': len(X),
                'features_ml': len(X.columns),
                'modelo_ml': resultado_ml,
                'padroes_sucesso': padroes_sucesso,
                'metricas': {
                    'acuracia_treino': resultado_ml.get('acuracia_treino', 0),
                    'acuracia_teste': resultado_ml.get('acuracia_teste', 0),
                    'total_amostras': len(X)
                },
                'resumo': {
                    'acuracia_ml': resultado_ml.get('acuracia_teste', 0),
                    'features_importantes': resultado_ml.get('feature_importance', [])[:5],
                    'melhor_dia': max(padroes_sucesso.get('dias_semana', {}).items(), 
                                    key=lambda x: x[1]['taxa_sucesso'], default=('N/A', {'taxa_sucesso': 0}))[0],
                    'melhor_faixa_odd': max(padroes_sucesso.get('faixas_odd', {}).items(), 
                                          key=lambda x: x[1]['taxa_sucesso'], default=('N/A', {'taxa_sucesso': 0}))[0]
                }
            }
            
            # Salvar no histórico
            self.historico_treinos.append(resultado_final)
            
            print("\n=== TREINO CONCLUÍDO COM SUCESSO ===")
            print(f"Acurácia ML: {resultado_ml.get('acuracia_teste', 0):.1%}")
            print(f"Features importantes: {[f[0] for f in resultado_ml.get('feature_importance', [])[:3]]}")
            
            return resultado_final
            
        except Exception as e:
            print(f"Erro durante treino: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'sucesso': False,
                'erro': str(e)
            }    
    
    def fazer_previsao(self, odd: float, valor: float, tipo_aposta: str = '1X2', competicao: str = 'Geral') -> dict:
        """Faz uma previsão usando o modelo treinado"""
        try:
            # Criar dados de entrada
            dados_entrada = pd.DataFrame({
                'odd': [odd],
                'valor_apostado': [valor],
                'tipo_aposta': [tipo_aposta],
                'competicao': [competicao]
            })
            
            # Fazer previsão
            prob, pred, conf = self.modelo_ml.prever(dados_entrada)
            
            # Determinar recomendação
            if prob > 0.6 and conf > 0.3:
                recomendacao = "APOSTAR"
                nivel_confianca = "Alta"
            elif prob > 0.5 and conf > 0.2:
                recomendacao = "CONSIDERAR"
                nivel_confianca = "Média"
            else:
                recomendacao = "NÃO APOSTAR"
                nivel_confianca = "Baixa"
            
            return {
                'probabilidade_vitoria': prob,
                'predicao': pred,
                'confianca': conf,
                'recomendacao': recomendacao,
                'nivel_confianca': nivel_confianca,
                'odd': odd,
                'valor_apostado': valor
            }
            
        except Exception as e:
            return {'erro': f'Erro na previsão: {str(e)}'}

# Instância global do gestor ML
gestor_ml = GestorML()

# Carregar modelos salvos na inicialização
gestor_ml.carregar_modelos_salvos()

# Exemplo de uso
if __name__ == "__main__":
    gestor = GestorMLSimples()
    resultado = gestor.treinar_modelo()
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))