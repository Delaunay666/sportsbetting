#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Tradução Multilíngue
Versão 1.1 - Sistema de Apostas Desportivas

Este módulo é responsável pela gestão de traduções e
internacionalização do sistema (PT/EN/ES).
"""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class Idioma(Enum):
    """Idiomas suportados pelo sistema."""
    PORTUGUES = "pt"
    INGLES = "en"
    ESPANHOL = "es"

class GestorTraducoes:
    """Classe responsável pela gestão de traduções."""
    
    def __init__(self):
        self.idioma_atual = Idioma.PORTUGUES
        self.traducoes = {}
        self.config_path = "config_idioma.json"
        self.traducoes_path = "traducoes"
        self._criar_diretorios()
        self._carregar_traducoes_padrao()
        self._carregar_configuracoes()
    
    def _criar_diretorios(self):
        """Cria diretórios necessários para traduções."""
        os.makedirs(self.traducoes_path, exist_ok=True)
    
    def _carregar_configuracoes(self):
        """Carrega configurações de idioma."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    idioma_salvo = config.get('idioma_atual', 'pt')
                    self.idioma_atual = Idioma(idioma_salvo)
            else:
                self._salvar_configuracoes()
        except Exception as e:
            print(f"Erro ao carregar configurações de idioma: {e}")
            self.idioma_atual = Idioma.PORTUGUES
    
    def _salvar_configuracoes(self):
        """Salva configurações de idioma."""
        try:
            config = {
                'idioma_atual': self.idioma_atual.value,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações de idioma: {e}")
    
    def _carregar_traducoes_padrao(self):
        """Carrega traduções padrão do sistema."""
        # Traduções em Português (padrão)
        self.traducoes[Idioma.PORTUGUES] = {
            # Interface Principal
            "titulo_aplicacao": "Sistema de Apostas Desportivas",
            "dashboard": "Dashboard",
            "nova_aposta": "Nova Aposta",
            "historico": "Histórico",
            "estatisticas": "Estatísticas",
            "configuracoes": "Configurações",
            "sair": "Sair",
            
            # Dashboard
            "saldo_atual": "Saldo Atual",
            "total_apostas": "Total de Apostas",
            "apostas_ganhas": "Apostas Ganhas",
            "apostas_perdidas": "Apostas Perdidas",
            "taxa_sucesso": "Taxa de Sucesso",
            "lucro_prejuizo": "Lucro/Prejuízo",
            "roi": "ROI",
            "evolucao_bankroll": "Evolução do Bankroll",
            "ultimas_apostas": "Últimas Apostas",
            
            # Nova Aposta
            "dados_aposta": "Dados da Aposta",
            "evento": "Evento",
            "tipo_aposta": "Tipo de Aposta",
            "odd": "Odd",
            "valor_aposta": "Valor da Aposta",
            "data_evento": "Data do Evento",
            "descricao": "Descrição",
            "salvar_aposta": "Salvar Aposta",
            "cancelar": "Cancelar",
            "competicao": "Competição",
            "equipa_casa": "Equipa Casa",
            "equipa_fora": "Equipa Fora",
            "odd_cotacao": "Odd (Cotação)",
            "valor_apostar": "Valor a Apostar",
            "limpar_formulario": "Limpar Formulário",
            "criar_backup": "Criar Backup",
            "editor_temas": "Editor de Temas",
            "salvar_todas_configuracoes": "Salvar Todas as Configurações",
            "valor_apostado": "Valor Apostado",
            "notas_opcional": "Notas (opcional)",
            "guardar_aposta": "Guardar Aposta",
            "limpar": "Limpar",
            "dashboard_avancado": "Dashboard Avançado",
            "visualizacoes": "Visualizações",
            "gestao_banca": "Gestão Banca",
            "analise": "Análise",
            "import_export": "Import/Export",
            "alertas": "Alertas",
            "banca_atual": "Banca Atual",
            "backup": "Backup",
            "backup_exportacao": "Backup e Exportação",
            "criar_backup": "Criar Backup",
            "configurar_autenticacao": "Configurar Autenticação",
            
            # Tipos de Aposta
            "simples": "Simples",
            "multipla": "Múltipla",
            "sistema": "Sistema",
            "handicap": "Handicap",
            "over_under": "Over/Under",
            
            # Esportes
            "futebol": "Futebol",
            "basquetebol": "Basquetebol",
            "tenis": "Ténis",
            "voleibol": "Voleibol",
            "andebol": "Andebol",
            "outros": "Outros",
            
            # Status
            "pendente": "Pendente",
            "ganha": "Ganha",
            "perdida": "Perdida",
            "cancelada": "Cancelada",
            "meio_ganha": "Meio Ganha",
            "meio_perdida": "Meio Perdida",
            
            # Histórico
            "filtrar_por": "Filtrar por",
            "data_inicio": "Data Início",
            "data_fim": "Data Fim",
            "esporte": "Esporte",
            "status": "Status",
            "aplicar_filtros": "Aplicar Filtros",
            "limpar_filtros": "Limpar Filtros",
            "exportar": "Exportar",
            
            # Estatísticas
            "resumo_geral": "Resumo Geral",
            "por_esporte": "Por Esporte",
            "por_mes": "Por Mês",
            "analise_risco": "Análise de Risco",
            "tendencias": "Tendências",
            
            # Configurações
            "geral": "Geral",
            "aparencia": "Aparência",
            "idioma": "Idioma",
            "tema": "Tema",
            "backup": "Backup",
            "sobre": "Sobre",
            
            # Mensagens
            "sucesso": "Sucesso",
            "erro": "Erro",
            "aviso": "Aviso",
            "confirmacao": "Confirmação",
            "aposta_salva": "Aposta salva com sucesso!",
            "erro_salvar": "Erro ao salvar aposta",
            "confirmar_exclusao": "Tem certeza que deseja excluir?",
            "dados_invalidos": "Dados inválidos",
            "campo_obrigatorio": "Campo obrigatório",
            "idioma_alterado": "Idioma Alterado",
            "idioma_alterado_msg": "Idioma alterado com sucesso! Reinicie a aplicação para ver todas as alterações.",
            "erro_alterar_idioma": "Erro ao alterar idioma",
            "preencha_campos": "Por favor, preencha todos os campos obrigatórios.",
            "valores_positivos": "Odd e valor apostado devem ser números positivos.",
            "valor_numerico": "Por favor, insira um valor numérico válido.",
            "atencao": "ATENÇÃO",
            "afetar_calculos": "Esta ação irá afetar todos os cálculos de ROI e variação.",
            "relatorio_gerado": "Relatório gerado com sucesso!",
            "salvo_em": "Salvo em:",
            "sem_dados_relatorio": "Não foram encontrados dados para gerar o relatório.",
            "adicione_apostas": "Adicione algumas apostas primeiro.",
            "sem_dados_periodo": "Não foram encontrados dados para o período especificado.",
            "tente_periodo_diferente": "Tente um período diferente ou adicione apostas primeiro.",
            "preencha_datas": "Por favor, preencha as datas de início e fim",
            "formato_data_invalido": "Formato de data inválido. Use DD/MM/AAAA",
            "data_inicio_anterior": "A data de início deve ser anterior à data de fim",
            "criptografia_configurada": "Criptografia já configurada. Deseja reconfigurar?",
            "configurar_autenticacao": "Configurar Autenticação",
            "nome_usuario": "Nome de usuário:",
            "salvar_configuracoes": "Salvar Todas as Configurações",
            "configuracoes_salvas": "Todas as configurações foram salvas com sucesso!",
            "erro_salvar_config": "Erro ao salvar configurações",
            
            # Botões
            "sim": "Sim",
            "nao": "Não",
            "ok": "OK",
            "fechar": "Fechar",
            "editar": "Editar",
            "excluir": "Excluir",
            "atualizar": "Atualizar",
            "novo": "Novo",
            
            # Relatórios
            "relatorios": "Relatórios",
            "gerar_relatorio": "Gerar Relatório",
            "relatorio_mensal": "Relatório Mensal",
            "relatorio_anual": "Relatório Anual",
            "relatorio_personalizado": "Relatório Personalizado",
            "exportar_pdf": "Exportar PDF",
            
            # Segurança
            "seguranca": "Segurança",
            "criptografia": "Criptografia",
            "backup_seguro": "Backup Seguro",
            "autenticacao": "Autenticação",
            "senha": "Senha",
            "confirmar_senha": "Confirmar Senha",
            
            # Temas
            "tema_claro": "Tema Claro",
            "tema_escuro": "Tema Escuro",
            "tema_personalizado": "Tema Personalizado",
            "cores": "Cores",
            "fonte": "Fonte",
            "tamanho_fonte": "Tamanho da Fonte",
            
            # Placeholder texts
            "placeholder_equipa_casa": "Nome da equipa da casa",
            "placeholder_equipa_fora": "Nome da equipa visitante",
            "placeholder_odd": "Ex: 2.50",
            "placeholder_valor": "Ex: 10.00",
            
            # Tipos de aposta específicos
            "1x2": "1X2",
            "over_under_golos": "Over/Under Golos",
            "over_under_cantos": "Over/Under Cantos",
            "handicap_asiatico": "Handicap Asiático",
            "ambas_marcam": "Ambas Marcam",
            "dupla_hipotese": "Dupla Hipótese",
            "resultado_exato": "Resultado Exato",
            
            # Informações da aplicação
            "versao_info": "Versão: 1.1 - Refinamento e Estabilidade",
            "desenvolvido_info": "Desenvolvido em Python com CustomTkinter",
            "base_dados_info": "Base de dados: SQLite com criptografia",
            "funcionalidades_info": "Funcionalidades: Registo, Análise, ML, Relatórios PDF",
            "novidades_versao": "Novidades da Versão 1.1:",
            "suporte_multilingue": "Suporte multilíngue (PT/EN/ES)",
            "sistema_temas": "Sistema de temas personalizáveis",
            "relatorios_pdf": "Relatórios PDF com gráficos",
            "criptografia_dados": "Criptografia de dados sensíveis",
            "modo_escuro": "Modo escuro aprimorado",
            "dicas_titulo": "Dicas:",
            "dica_backup": "Faça backups regulares dos seus dados",
            "dica_analise": "Analise os padrões regularmente",
            "dica_banca": "Use a gestão de banca responsavelmente",
            "dica_ml": "Aproveite as análises de ML para melhorar",
            "dica_temas": "Experimente os novos temas e idiomas",
            
            # Relatórios
            "incluir_analise_detalhada": "Incluir Análise Detalhada",
            "incluir_recomendacoes": "Incluir Recomendações",
            
            # Dashboard Avançado
            "dashboard_avancado_titulo": "Dashboard Avançado de Apostas",
            "ultima_atualizacao": "Última atualização",
            "auto_refresh": "Auto-refresh",
            "atualizar": "Atualizar",
            "exportar": "Exportar",
            "metricas_principais": "Métricas Principais",
            "total_de_apostas": "Total de Apostas",
            "taxa_de_acerto": "Taxa de Acerto",
            "retorno_medio": "Retorno Médio",
            "sharpe_ratio": "Sharpe Ratio",
            "max_drawdown": "Max Drawdown",
            "profit_factor": "Profit Factor",
            "analise_de_performance": "Análise de Performance",
            "evolucao_do_lucro": "Evolução do Lucro",
            "distribuicao_de_retornos": "Distribuição de Retornos",
            "por_competicao": "Por Competição",
            "heatmap": "Heatmap",
            
            # Visualizações Avançadas
            "visualizacoes_avancadas": "Visualizações Avançadas",
            "heatmaps": "Heatmaps",
            "waterfall": "Waterfall",
            "correlacoes": "Correlações",
            "performance": "Performance",
            "analise_de_risco": "Análise de Risco",
            "tipo_de_heatmap": "Tipo de Heatmap",
            "performance_por_dia_semana": "Performance por Dia da Semana",
            "performance_por_hora": "Performance por Hora",
            "performance_por_mes": "Performance por Mês",
            "performance_por_competicao": "Performance por Competição",
            "odds_vs_resultado": "Odds vs Resultado",
            "valor_vs_roi": "Valor vs ROI",
            "periodo": "Período",
            "ultimo_mes": "Último mês",
            "ultimos_3_meses": "Últimos 3 meses",
            "ultimos_6_meses": "Últimos 6 meses",
            "ultimo_ano": "Último ano",
            "atualizar_correlacoes": "Atualizar Correlações",
            "atualizar_performance": "Atualizar Performance",
            "atualizar_analise_risco": "Atualizar Análise de Risco",
            "var_95": "VaR (95%)",
            "drawdown_maximo": "Drawdown Máximo",
            "volatilidade": "Volatilidade",
            "calculando": "Calculando...",
            
            # Versão 1.2 - IA e Automação
            "ai_automation": "IA e Automação",
            "ai_dashboard": "Dashboard IA",
            "strategy_simulator": "Simulador de Estratégias",
            "pattern_detection": "Detecção de Padrões",
            "tipster_tracker": "Rastreador de Tipsters",
            "risk_behavior": "Análise de Risco",
            "classic_modules": "Módulos Clássicos",
            "classic_dashboard": "Dashboard Clássico",
            "advanced_visualizations": "Visualizações Avançadas",
            "system_status": "Estado do Sistema",
            "active_alerts": "Alertas Ativos",
            "no_alerts": "Sem alertas",
            "risk_analysis_unavailable": "Análise de risco indisponível",
            "critical_risk_alert": "ALERTA CRÍTICO DE RISCO",
            "high_risk_behavior_detected": "Comportamentos de alto risco detectados. Recomenda-se pausa imediata nas apostas.",
            "recommendation": "Recomendação",
            "intelligent_dashboard": "Dashboard Inteligente",
            "risk_score": "Pontuação de Risco",
            "risk_level": "Nível de Risco",
            "best_tipster": "Melhor Tipster",
            "rating": "Classificação",
            "tipsters": "Tipsters",
            "none_registered": "Nenhum registrado",
            "profitable_patterns": "Padrões Rentáveis",
            "total": "Total",
            "patterns": "Padrões",
            "analysis_unavailable": "Análise indisponível",
            "ai_insights": "Insights de IA",
            "healthy_betting_behavior": "Comportamento de apostas saudável detectado!",
            "behavior_analysis_unavailable": "Análise de comportamento indisponível",
            "quick_analysis": "Análise Rápida",
            "simulate_strategy": "Simular Estratégia",
            "detect_patterns": "Detectar Padrões",
            "manage_tipsters": "Gerir Tipsters",
            "visual_summary": "Resumo Visual",
            "recent_evolution": "Evolução Recente (Últimas 30 Apostas)",
            "date": "Data",
            "accumulated_profit": "Lucro Acumulado (€)",
            "insufficient_data_visual": "Dados insuficientes para análise visual",
            "error_generating_charts": "Erro ao gerar gráficos",
            "strategy": "Estratégia",
            "initial_bankroll": "Banca Inicial (€)",
            "days_to_simulate": "Dias a Simular",
            "fixed_bet_amount": "Valor Fixo de Aposta (€)",
            "kelly_fraction": "Fração Kelly",
            "bankroll_percentage": "Percentagem da Banca (%)",
            "base_bet": "Aposta Base (€)",
            "max_sequence": "Sequência Máx.",
            "max_level": "Nível Máximo",
            "execute_simulation": "Executar Simulação",
            "executing_simulation": "Executando simulação...",
            "final_profit": "Lucro Final",
            "roi": "ROI",
            "max_drawdown_short": "Drawdown Máx.",
            "bankroll_evolution": "Evolução da Banca",
            "bet_number": "Aposta #",
            "bankroll_value": "Valor da Banca (€)",
            "simulation_error": "Erro na simulação. Verifique os dados históricos.",
            "strategy_comparison": "Comparação de Estratégias",
            "compare_all_strategies": "Comparar Todas as Estratégias",
            "comparing_strategies": "Comparando estratégias...",
            "comparison_error": "Erro na comparação",
            "pattern_detection_ai": "Detecção de Padrões com IA",
            "analysis_type": "Tipo de Análise",
            "patterns_by_weekday": "Padrões por Dia da Semana",
            "patterns_by_odds_range": "Padrões por Intervalo de Odds",
            "patterns_by_competition": "Padrões por Competição",
            "patterns_by_bet_type": "Padrões por Tipo de Aposta",
            "combined_analysis": "Análise Combinada",
            "analysis_period_days": "Período de Análise (dias)",
            "analyze_patterns": "Analisar Padrões",
            "analyzing_patterns": "Analisando padrões...",
            "patterns_found": "padrões encontrados!",
            "profitable_patterns_detected": "Padrões Rentáveis Detectados",
            "pattern": "Padrão",
            "win_rate": "Taxa de Acerto",
            "num_bets": "Nº Apostas",
            "description": "Descrição",
            "confidence": "Confiança",
            "risk_patterns_detected": "Padrões de Risco Detectados",
            "no_significant_patterns": "Não foram detectados padrões significativos no período analisado.",
            "ai_predictions": "Previsões de IA",
            "train_prediction_model": "Treinar Modelo de Previsão",
            "training_ai_model": "Treinando modelo de IA...",
            "model_trained_successfully": "Modelo treinado com sucesso! Precisão:",
            "prediction_next_bet": "Previsão para Próxima Aposta",
            "odds": "Odds",
            "value": "Valor (€)",
            "weekday": "Dia da Semana",
            "make_prediction": "Fazer Previsão",
            "win_probability": "Probabilidade de Vitória",
            "prediction_error": "Erro na previsão",
            "training_error": "Erro no treino. Verifique os dados históricos.",
            "training_error_general": "Erro no treino",
            "ranking": "Ranking",
            "add_tipster": "Adicionar Tipster",
            "statistics": "Estatísticas",
            "link_bets": "Vincular Apostas",
            "tipster_ranking": "Ranking de Tipsters",
            "period": "Período",
            "update_ranking": "Atualizar Ranking",
            "tipster": "Tipster",
            "tips": "Tips",
            "profit": "Lucro",
            "trend": "Tendência",
            "top_3_tipsters": "Top 3 Tipsters",
            "no_tipsters_registered": "Ainda não há tipsters registrados.",
            "error_loading_ranking": "Erro ao carregar ranking",
            "add_new_tipster": "Adicionar Novo Tipster",
            "tipster_name": "Nome do Tipster*",
            "source": "Fonte (ex: Telegram, YouTube)*",
            "category": "Categoria",
            "football": "Futebol",
            "basketball": "Basquetebol",
            "tennis": "Ténis",
            "others": "Outros",
            "notes_optional": "Notas (opcional)",
            "tipster_added_successfully": "Tipster adicionado com sucesso! ID:",
            "name_source_required": "Nome e fonte são obrigatórios!",
            "detailed_statistics": "Estatísticas Detalhadas",
            "select_tipster": "Selecionar Tipster",
            "analysis_period": "Período de Análise",
            "generate_statistics": "Gerar Estatísticas",
            "calculating_statistics": "Calculando estatísticas...",
            "total_tips": "Total Tips",
            "total_roi": "ROI Total",
            "total_profit": "Lucro Total",
            "amount_bet": "Valor Apostado",
            "best_sequence": "Melhor Sequência",
            "wins": "vitórias",
            "current_sequence": "Sequência Atual",
            "additional_info": "Informação Adicional",
            "days_active": "Dias Ativo",
            "tips_per_month": "Tips por Mês",
            "average_odds": "Odd Média",
            "average_value": "Valor Médio",
            "last_tip": "Último Tip",
            "rising": "Subindo",
            "falling": "Descendo",
            "stable": "Estável",
            "insufficient_data_tipster": "Dados insuficientes para este tipster no período selecionado.",
            "no_tipsters_add_first": "Não há tipsters registrados. Adicione um tipster primeiro.",
            "error_loading_statistics": "Erro ao carregar estatísticas",
            "link_bets_to_tipsters": "Vincular Apostas a Tipsters",
            "bets_without_tipster_found": "apostas sem tipster associado encontradas.",
            "select_bet": "Selecionar Aposta",
            "tip_source_optional": "Fonte do Tip (opcional)",
            "link": "Vincular",
            "bet_linked_successfully": "Aposta vinculada com sucesso!",
            "error_linking_bet": "Erro ao vincular aposta.",
            "no_tipsters_available": "Não há tipsters disponíveis. Adicione tipsters primeiro.",
            "all_bets_have_tipsters": "Todas as apostas já têm tipsters associados!",
            "error_loading_bets": "Erro ao carregar apostas",
            "risk_behavior_analysis": "Análise de Comportamento de Risco",
            "general_risk_score": "Pontuação Geral de Risco",
            "risk_level_low": "Baixo",
            "risk_level_medium": "Médio",
            "risk_level_high": "Alto",
            "risk_level_critical": "Crítico",
            "largest_loss_sequence": "Maior Seq. Perdas",
            "impulse_bets": "Apostas Impulso",
            "value_variation": "Variação de Valores",
            "personalized_recommendations": "Recomendações Personalizadas",
            "temporal_risk_patterns": "Padrões Temporais de Risco",
            "risk_hours": "Horas de Risco",
            "risk_days": "Dias de Risco",
            "no_risk_hours_identified": "Não foram identificadas horas de risco",
            "no_risk_days_identified": "Não foram identificados dias de risco",
            "error_risk_analysis": "Erro na análise de risco",
            "real_time_risk_detection": "Detecção de Padrões de Risco em Tempo Real",
            "detection_period": "Período de Detecção",
            "detect_risk_patterns": "Detectar Padrões de Risco",
            "analyzing_risk_patterns": "Analisando padrões de risco...",
            "new_risk_patterns_detected": "novos padrões de risco detectados!",
            "type": "Tipo",
            "involved_value": "Valor Envolvido",
            "no_risk_patterns_detected": "Não foram detectados padrões de risco no período analisado!",
            "detection_error": "Erro na detecção",
            "resolve_alert": "Resolver Alerta",
            "alert_resolved": "Alerta resolvido!",
            "error_resolving_alert": "Erro ao resolver alerta",
            "no_active_alerts": "Não há alertas ativos neste momento!",
            "error_loading_alerts": "Erro ao carregar alertas",
            "risk_visualization": "Visualização de Risco",
            "generate_risk_charts": "Gerar Gráficos de Risco",
            "generating_visualizations": "Gerando visualizações...",
            "insufficient_data_visualization": "Dados insuficientes para visualização",
            "error_generating_charts_risk": "Erro ao gerar gráficos"
        }
        
        # Traduções em Inglês
        self.traducoes[Idioma.INGLES] = {
            # Main Interface
            "titulo_aplicacao": "Sports Betting System",
            "dashboard": "Dashboard",
            "nova_aposta": "New Bet",
            "historico": "History",
            "estatisticas": "Statistics",
            "configuracoes": "Settings",
            "sair": "Exit",
            
            # Dashboard
            "saldo_atual": "Current Balance",
            "total_apostas": "Total Bets",
            "apostas_ganhas": "Won Bets",
            "apostas_perdidas": "Lost Bets",
            "taxa_sucesso": "Success Rate",
            "lucro_prejuizo": "Profit/Loss",
            "roi": "ROI",
            "evolucao_bankroll": "Bankroll Evolution",
            "ultimas_apostas": "Recent Bets",
            
            # New Bet
            "dados_aposta": "Bet Data",
            "evento": "Event",
            "tipo_aposta": "Bet Type",
            "odd": "Odds",
            "valor_aposta": "Bet Amount",
            "data_evento": "Event Date",
            "descricao": "Description",
            "salvar_aposta": "Save Bet",
            "cancelar": "Cancel",
            "competicao": "Competition",
            "equipa_casa": "Home Team",
            "equipa_fora": "Away Team",
            "odd_cotacao": "Odds (Quote)",
            "valor_apostar": "Amount to Bet",
            "limpar_formulario": "Clear Form",
            "criar_backup": "Create Backup",
            "editor_temas": "Theme Editor",
            "salvar_todas_configuracoes": "Save All Settings",
            "valor_apostado": "Bet Amount",
            "notas_opcional": "Notes (optional)",
            "guardar_aposta": "Save Bet",
            "limpar": "Clear",
            "dashboard_avancado": "Advanced Dashboard",
            "visualizacoes": "Visualizations",
            "gestao_banca": "Bankroll Management",
            "analise": "Analysis",
            "import_export": "Import/Export",
            "alertas": "Alerts",
            "banca_atual": "Current Bankroll",
            "backup": "Backup",
            "backup_exportacao": "Backup and Export",
            "criar_backup": "Create Backup",
            "configurar_autenticacao": "Configure Authentication",
            
            # Bet Types
            "simples": "Single",
            "multipla": "Multiple",
            "sistema": "System",
            "handicap": "Handicap",
            "over_under": "Over/Under",
            
            # Sports
            "futebol": "Football",
            "basquetebol": "Basketball",
            "tenis": "Tennis",
            "voleibol": "Volleyball",
            "andebol": "Handball",
            "outros": "Others",
            
            # Status
            "pendente": "Pending",
            "ganha": "Won",
            "perdida": "Lost",
            "cancelada": "Cancelled",
            "meio_ganha": "Half Won",
            "meio_perdida": "Half Lost",
            
            # History
            "filtrar_por": "Filter by",
            "data_inicio": "Start Date",
            "data_fim": "End Date",
            "esporte": "Sport",
            "status": "Status",
            "aplicar_filtros": "Apply Filters",
            "limpar_filtros": "Clear Filters",
            "exportar": "Export",
            
            # Statistics
            "resumo_geral": "General Summary",
            "por_esporte": "By Sport",
            "por_mes": "By Month",
            "analise_risco": "Risk Analysis",
            "tendencias": "Trends",
            
            # Settings
            "geral": "General",
            "aparencia": "Appearance",
            "idioma": "Language",
            "tema": "Theme",
            "backup": "Backup",
            "sobre": "About",
            
            # Messages
            "sucesso": "Success",
            "erro": "Error",
            "aviso": "Warning",
            "confirmacao": "Confirmation",
            "aposta_salva": "Bet saved successfully!",
            "erro_salvar": "Error saving bet",
            "confirmar_exclusao": "Are you sure you want to delete?",
            "dados_invalidos": "Invalid data",
            "campo_obrigatorio": "Required field",
            "idioma_alterado": "Language Changed",
            "idioma_alterado_msg": "Language changed successfully! Restart the application to see all changes.",
            "erro_alterar_idioma": "Error changing language",
            "preencha_campos": "Please fill in all required fields.",
            "valores_positivos": "Odds and bet amount must be positive numbers.",
            "valor_numerico": "Please enter a valid numeric value.",
            "atencao": "WARNING",
            "afetar_calculos": "This action will affect all ROI and variance calculations.",
            "relatorio_gerado": "Report generated successfully!",
            "salvo_em": "Saved in:",
            "sem_dados_relatorio": "No data found to generate the report.",
            "adicione_apostas": "Add some bets first.",
            "sem_dados_periodo": "No data found for the specified period.",
            "tente_periodo_diferente": "Try a different period or add bets first.",
            "preencha_datas": "Please fill in start and end dates",
            "formato_data_invalido": "Invalid date format. Use DD/MM/YYYY",
            "data_inicio_anterior": "Start date must be before end date",
            "criptografia_configurada": "Encryption already configured. Do you want to reconfigure?",
            "configurar_autenticacao": "Configure Authentication",
            "nome_usuario": "Username:",
            "salvar_configuracoes": "Save All Settings",
            "configuracoes_salvas": "All settings have been saved successfully!",
            "erro_salvar_config": "Error saving settings",
            
            # Buttons
            "sim": "Yes",
            "nao": "No",
            "ok": "OK",
            "fechar": "Close",
            "editar": "Edit",
            "excluir": "Delete",
            "atualizar": "Update",
            "novo": "New",
            
            # Reports
            "relatorios": "Reports",
            "gerar_relatorio": "Generate Report",
            "relatorio_mensal": "Monthly Report",
            "relatorio_anual": "Annual Report",
            "relatorio_personalizado": "Custom Report",
            "exportar_pdf": "Export PDF",
            
            # Security
            "seguranca": "Security",
            "criptografia": "Encryption",
            "backup_seguro": "Secure Backup",
            "autenticacao": "Authentication",
            "senha": "Password",
            "confirmar_senha": "Confirm Password",
            
            # Themes
            "tema_claro": "Light Theme",
            "tema_escuro": "Dark Theme",
            "tema_personalizado": "Custom Theme",
            "cores": "Colors",
            "fonte": "Font",
            "tamanho_fonte": "Font Size",
            
            # Placeholder texts
            "placeholder_equipa_casa": "Home team name",
            "placeholder_equipa_fora": "Away team name",
            "placeholder_odd": "Ex: 2.50",
            "placeholder_valor": "Ex: 10.00",
            
            # Tipos de aposta específicos
            "1x2": "1X2",
            "over_under_golos": "Over/Under Goals",
            "over_under_cantos": "Over/Under Corners",
            "handicap_asiatico": "Asian Handicap",
            "ambas_marcam": "Both Teams to Score",
            "dupla_hipotese": "Double Chance",
            "resultado_exato": "Exact Score",
            
            # Informações da aplicação
            "versao_info": "Version: 1.1 - Refinement and Stability",
            "desenvolvido_info": "Developed in Python with CustomTkinter",
            "base_dados_info": "Database: SQLite with encryption",
            "funcionalidades_info": "Features: Registration, Analysis, ML, PDF Reports",
            "novidades_versao": "Version 1.1 New Features:",
            "suporte_multilingue": "Multilingual support (PT/EN/ES)",
            "sistema_temas": "Customizable theme system",
            "relatorios_pdf": "PDF reports with charts",
            "criptografia_dados": "Sensitive data encryption",
            "modo_escuro": "Enhanced dark mode",
            "dicas_titulo": "Tips:",
            "dica_backup": "Make regular backups of your data",
            "dica_analise": "Analyze patterns regularly",
            "dica_banca": "Use bankroll management responsibly",
            "dica_ml": "Take advantage of ML analysis to improve",
            "dica_temas": "Try the new themes and languages",
            
            # Relatórios
            "incluir_analise_detalhada": "Include Detailed Analysis",
            "incluir_recomendacoes": "Include Recommendations",
            
            # Dashboard Avançado
            "dashboard_avancado_titulo": "Advanced Betting Dashboard",
            "ultima_atualizacao": "Last update",
            "auto_refresh": "Auto-refresh",
            "atualizar": "Update",
            "exportar": "Export",
            "metricas_principais": "Main Metrics",
            "total_de_apostas": "Total Bets",
            "taxa_de_acerto": "Hit Rate",
            "retorno_medio": "Average Return",
            "sharpe_ratio": "Sharpe Ratio",
            "max_drawdown": "Max Drawdown",
            "profit_factor": "Profit Factor",
            "analise_de_performance": "Performance Analysis",
            "evolucao_do_lucro": "Profit Evolution",
            "distribuicao_de_retornos": "Returns Distribution",
            "por_competicao": "By Competition",
            "heatmap": "Heatmap",
            
            # Visualizações Avançadas
            "visualizacoes_avancadas": "Advanced Visualizations",
            "heatmaps": "Heatmaps",
            "waterfall": "Waterfall",
            "correlacoes": "Correlations",
            "performance": "Performance",
            "analise_de_risco": "Risk Analysis",
            "tipo_de_heatmap": "Heatmap Type",
            "performance_por_dia_semana": "Performance by Day of Week",
            "performance_por_hora": "Performance by Hour",
            "performance_por_mes": "Performance by Month",
            "performance_por_competicao": "Performance by Competition",
            "odds_vs_resultado": "Odds vs Result",
            "valor_vs_roi": "Value vs ROI",
            "periodo": "Period",
            "ultimo_mes": "Last month",
            "ultimos_3_meses": "Last 3 months",
            "ultimos_6_meses": "Last 6 months",
            "ultimo_ano": "Last year",
            "atualizar_correlacoes": "Update Correlations",
            "atualizar_performance": "Update Performance",
            "atualizar_analise_risco": "Update Risk Analysis",
            "var_95": "VaR (95%)",
            "drawdown_maximo": "Maximum Drawdown",
            "volatilidade": "Volatility",
            "calculando": "Calculating...",
            
            # Version 1.2 - AI and Automation
            "ai_automation": "AI & Automation",
            "ai_dashboard": "AI Dashboard",
            "strategy_simulator": "Strategy Simulator",
            "pattern_detection": "Pattern Detection",
            "tipster_tracker": "Tipster Tracker",
            "risk_behavior": "Risk Analysis",
            "classic_modules": "Classic Modules",
            "classic_dashboard": "Classic Dashboard",
            "advanced_visualizations": "Advanced Visualizations",
            "system_status": "System Status",
            "active_alerts": "Active Alerts",
            "no_alerts": "No alerts",
            "risk_analysis_unavailable": "Risk analysis unavailable",
            "critical_risk_alert": "CRITICAL RISK ALERT",
            "high_risk_behavior_detected": "High-risk behaviors detected. Immediate pause in betting is recommended.",
            "recommendation": "Recommendation",
            "intelligent_dashboard": "Intelligent Dashboard",
            "risk_score": "Risk Score",
            "risk_level": "Risk Level",
            "best_tipster": "Best Tipster",
            "rating": "Rating",
            "tipsters": "Tipsters",
            "none_registered": "None registered",
            "profitable_patterns": "Profitable Patterns",
            "total": "Total",
            "patterns": "Patterns",
            "analysis_unavailable": "Analysis unavailable",
            "ai_insights": "AI Insights",
            "healthy_betting_behavior": "Healthy betting behavior detected!",
            "behavior_analysis_unavailable": "Behavior analysis unavailable",
            "quick_analysis": "Quick Analysis",
            "simulate_strategy": "Simulate Strategy",
            "detect_patterns": "Detect Patterns",
            "manage_tipsters": "Manage Tipsters",
            "visual_summary": "Visual Summary",
            "recent_evolution": "Recent Evolution (Last 30 Bets)",
            "date": "Date",
            "accumulated_profit": "Accumulated Profit (€)",
            "insufficient_data_visual": "Insufficient data for visual analysis",
            "error_generating_charts": "Error generating charts",
            "strategy": "Strategy",
            "initial_bankroll": "Initial Bankroll (€)",
            "days_to_simulate": "Days to Simulate",
            "fixed_bet_amount": "Fixed Bet Amount (€)",
            "kelly_fraction": "Kelly Fraction",
            "bankroll_percentage": "Bankroll Percentage (%)",
            "base_bet": "Base Bet (€)",
            "max_sequence": "Max Sequence",
            "max_level": "Max Level",
            "execute_simulation": "Execute Simulation",
            "executing_simulation": "Executing simulation...",
            "final_profit": "Final Profit",
            "roi": "ROI",
            "max_drawdown_short": "Max Drawdown",
            "bankroll_evolution": "Bankroll Evolution",
            "bet_number": "Bet #",
            "bankroll_value": "Bankroll Value (€)",
            "simulation_error": "Simulation error. Check historical data.",
            "strategy_comparison": "Strategy Comparison",
            "compare_all_strategies": "Compare All Strategies",
            "comparing_strategies": "Comparing strategies...",
            "comparison_error": "Comparison error",
            "pattern_detection_ai": "Pattern Detection with AI",
            "analysis_type": "Analysis Type",
            "patterns_by_weekday": "Patterns by Weekday",
            "patterns_by_odds_range": "Patterns by Odds Range",
            "patterns_by_competition": "Patterns by Competition",
            "patterns_by_bet_type": "Patterns by Bet Type",
            "combined_analysis": "Combined Analysis",
            "analysis_period_days": "Analysis Period (days)",
            "analyze_patterns": "Analyze Patterns",
            "analyzing_patterns": "Analyzing patterns...",
            "patterns_found": "patterns found!",
            "profitable_patterns_detected": "Profitable Patterns Detected",
            "pattern": "Pattern",
            "win_rate": "Win Rate",
            "num_bets": "No. Bets",
            "description": "Description",
            "confidence": "Confidence",
            "risk_patterns_detected": "Risk Patterns Detected",
            "no_significant_patterns": "No significant patterns detected in the analyzed period.",
            "ai_predictions": "AI Predictions",
            "train_prediction_model": "Train Prediction Model",
            "training_ai_model": "Training AI model...",
            "model_trained_successfully": "Model trained successfully! Accuracy:",
            "prediction_next_bet": "Prediction for Next Bet",
            "odds": "Odds",
            "value": "Value (€)",
            "weekday": "Weekday",
            "make_prediction": "Make Prediction",
            "win_probability": "Win Probability",
            "prediction_error": "Prediction error",
            "training_error": "Training error. Check historical data.",
            "training_error_general": "Training error",
            "ranking": "Ranking",
            "add_tipster": "Add Tipster",
            "statistics": "Statistics",
            "link_bets": "Link Bets",
            "tipster_ranking": "Tipster Ranking",
            "period": "Period",
            "update_ranking": "Update Ranking",
            "tipster": "Tipster",
            "tips": "Tips",
            "profit": "Profit",
            "trend": "Trend",
            "top_3_tipsters": "Top 3 Tipsters",
            "no_tipsters_registered": "No tipsters registered yet.",
            "error_loading_ranking": "Error loading ranking",
            "add_new_tipster": "Add New Tipster",
            "tipster_name": "Tipster Name*",
            "source": "Source (e.g., Telegram, YouTube)*",
            "category": "Category",
            "football": "Football",
            "basketball": "Basketball",
            "tennis": "Tennis",
            "others": "Others",
            "notes_optional": "Notes (optional)",
            "tipster_added_successfully": "Tipster added successfully! ID:",
            "name_source_required": "Name and source are required!",
            "detailed_statistics": "Detailed Statistics",
            "select_tipster": "Select Tipster",
            "analysis_period": "Analysis Period",
            "generate_statistics": "Generate Statistics",
            "calculating_statistics": "Calculating statistics...",
            "total_tips": "Total Tips",
            "total_roi": "Total ROI",
            "total_profit": "Total Profit",
            "amount_bet": "Amount Bet",
            "best_sequence": "Best Sequence",
            "wins": "wins",
            "current_sequence": "Current Sequence",
            "additional_info": "Additional Information",
            "days_active": "Days Active",
            "tips_per_month": "Tips per Month",
            "average_odds": "Average Odds",
            "average_value": "Average Value",
            "last_tip": "Last Tip",
            "rising": "Rising",
            "falling": "Falling",
            "stable": "Stable",
            "insufficient_data_tipster": "Insufficient data for this tipster in the selected period.",
            "no_tipsters_add_first": "No tipsters registered. Add a tipster first.",
            "error_loading_statistics": "Error loading statistics",
            "link_bets_to_tipsters": "Link Bets to Tipsters",
            "bets_without_tipster_found": "bets without associated tipster found.",
            "select_bet": "Select Bet",
            "tip_source_optional": "Tip Source (optional)",
            "link": "Link",
            "bet_linked_successfully": "Bet linked successfully!",
            "error_linking_bet": "Error linking bet.",
            "no_tipsters_available": "No tipsters available. Add tipsters first.",
            "all_bets_have_tipsters": "All bets already have associated tipsters!",
            "error_loading_bets": "Error loading bets",
            "risk_behavior_analysis": "Risk Behavior Analysis",
            "general_risk_score": "General Risk Score",
            "risk_level_low": "Low",
            "risk_level_medium": "Medium",
            "risk_level_high": "High",
            "risk_level_critical": "Critical",
            "largest_loss_sequence": "Largest Loss Seq.",
            "impulse_bets": "Impulse Bets",
            "value_variation": "Value Variation",
            "personalized_recommendations": "Personalized Recommendations",
            "temporal_risk_patterns": "Temporal Risk Patterns",
            "risk_hours": "Risk Hours",
            "risk_days": "Risk Days",
            "no_risk_hours_identified": "No risk hours identified",
            "no_risk_days_identified": "No risk days identified",
            "error_risk_analysis": "Error in risk analysis",
            "real_time_risk_detection": "Real-time Risk Pattern Detection",
            "detection_period": "Detection Period",
            "detect_risk_patterns": "Detect Risk Patterns",
            "analyzing_risk_patterns": "Analyzing risk patterns...",
            "new_risk_patterns_detected": "new risk patterns detected!",
            "type": "Type",
            "involved_value": "Involved Value",
            "no_risk_patterns_detected": "No risk patterns detected in the analyzed period!",
            "detection_error": "Detection error",
            "resolve_alert": "Resolve Alert",
            "alert_resolved": "Alert resolved!",
            "error_resolving_alert": "Error resolving alert",
            "no_active_alerts": "No active alerts at the moment!",
            "error_loading_alerts": "Error loading alerts",
            "risk_visualization": "Risk Visualization",
            "generate_risk_charts": "Generate Risk Charts",
            "generating_visualizations": "Generating visualizations...",
            "insufficient_data_visualization": "Insufficient data for visualization",
            "error_generating_charts_risk": "Error generating charts"
        }
        
        # Traduções em Espanhol
        self.traducoes[Idioma.ESPANHOL] = {
            # Interfaz Principal
            "titulo_aplicacao": "Sistema de Apuestas Deportivas",
            "dashboard": "Panel de Control",
            "nova_aposta": "Nueva Apuesta",
            "historico": "Historial",
            "estatisticas": "Estadísticas",
            "configuracoes": "Configuración",
            "sair": "Salir",
            
            # Dashboard
            "saldo_atual": "Saldo Actual",
            "total_apostas": "Total de Apuestas",
            "apostas_ganhas": "Apuestas Ganadas",
            "apostas_perdidas": "Apuestas Perdidas",
            "taxa_sucesso": "Tasa de Éxito",
            "lucro_prejuizo": "Ganancia/Pérdida",
            "roi": "ROI",
            "evolucao_bankroll": "Evolución del Bankroll",
            "ultimas_apostas": "Últimas Apuestas",
            
            # Nueva Apuesta
            "dados_aposta": "Datos de la Apuesta",
            "evento": "Evento",
            "tipo_aposta": "Tipo de Apuesta",
            "odd": "Cuota",
            "valor_aposta": "Valor de la Apuesta",
            "data_evento": "Fecha del Evento",
            "descricao": "Descripción",
            "salvar_aposta": "Guardar Apuesta",
            "cancelar": "Cancelar",
            "competicao": "Competición",
            "equipa_casa": "Equipo Local",
            "equipa_fora": "Equipo Visitante",
            "odd_cotacao": "Cuota (Cotización)",
            "valor_apostar": "Cantidad a Apostar",
            "limpar_formulario": "Limpiar Formulario",
            "criar_backup": "Crear Copia de Seguridad",
            "editor_temas": "Editor de Temas",
            "salvar_todas_configuracoes": "Guardar Todas las Configuraciones",
            "valor_apostado": "Valor Apostado",
            "notas_opcional": "Notas (opcional)",
            "guardar_aposta": "Guardar Apuesta",
            "limpar": "Limpiar",
            "dashboard_avancado": "Panel Avanzado",
            "visualizacoes": "Visualizaciones",
            "gestao_banca": "Gestión de Banca",
            "analise": "Análisis",
            "import_export": "Importar/Exportar",
            "alertas": "Alertas",
            "banca_atual": "Banca Actual",
            "backup": "Copia de Seguridad",
            "backup_exportacao": "Copia de Seguridad y Exportación",
            "criar_backup": "Crear Copia de Seguridad",
            "configurar_autenticacao": "Configurar Autenticación",
            
            # Tipos de Apuesta
            "simples": "Simple",
            "multipla": "Múltiple",
            "sistema": "Sistema",
            "handicap": "Hándicap",
            "over_under": "Más/Menos",
            
            # Deportes
            "futebol": "Fútbol",
            "basquetebol": "Baloncesto",
            "tenis": "Tenis",
            "voleibol": "Voleibol",
            "andebol": "Balonmano",
            "outros": "Otros",
            
            # Estado
            "pendente": "Pendiente",
            "ganha": "Ganada",
            "perdida": "Perdida",
            "cancelada": "Cancelada",
            "meio_ganha": "Medio Ganada",
            "meio_perdida": "Medio Perdida",
            
            # Historial
            "filtrar_por": "Filtrar por",
            "data_inicio": "Fecha Inicio",
            "data_fim": "Fecha Fin",
            "esporte": "Deporte",
            "status": "Estado",
            "aplicar_filtros": "Aplicar Filtros",
            "limpar_filtros": "Limpiar Filtros",
            "exportar": "Exportar",
            
            # Estadísticas
            "resumo_geral": "Resumen General",
            "por_esporte": "Por Deporte",
            "por_mes": "Por Mes",
            "analise_risco": "Análisis de Riesgo",
            "tendencias": "Tendencias",
            
            # Configuración
            "geral": "General",
            "aparencia": "Apariencia",
            "idioma": "Idioma",
            "tema": "Tema",
            "backup": "Copia de Seguridad",
            "sobre": "Acerca de",
            
            # Mensajes
            "sucesso": "Éxito",
            "erro": "Error",
            "aviso": "Aviso",
            "confirmacao": "Confirmación",
            "aposta_salva": "¡Apuesta guardada con éxito!",
            "erro_salvar": "Error al guardar apuesta",
            "confirmar_exclusao": "¿Está seguro de que desea eliminar?",
            "dados_invalidos": "Datos inválidos",
            "campo_obrigatorio": "Campo obligatorio",
            "idioma_alterado": "Idioma Cambiado",
            "idioma_alterado_msg": "¡Idioma cambiado con éxito! Reinicie la aplicación para ver todos los cambios.",
            "erro_alterar_idioma": "Error al cambiar idioma",
            "preencha_campos": "Por favor, complete todos los campos obligatorios.",
            "valores_positivos": "Las cuotas y el monto de la apuesta deben ser números positivos.",
            "valor_numerico": "Por favor, ingrese un valor numérico válido.",
            "atencao": "ATENCIÓN",
            "afetar_calculos": "Esta acción afectará todos los cálculos de ROI y varianza.",
            "relatorio_gerado": "¡Informe generado con éxito!",
            "salvo_em": "Guardado en:",
            "sem_dados_relatorio": "No se encontraron datos para generar el informe.",
            "adicione_apostas": "Agregue algunas apuestas primero.",
            "sem_dados_periodo": "No se encontraron datos para el período especificado.",
            "tente_periodo_diferente": "Pruebe un período diferente o agregue apuestas primero.",
            "preencha_datas": "Por favor, complete las fechas de inicio y fin",
            "formato_data_invalido": "Formato de fecha inválido. Use DD/MM/AAAA",
            "data_inicio_anterior": "La fecha de inicio debe ser anterior a la fecha de fin",
            "criptografia_configurada": "Cifrado ya configurado. ¿Desea reconfigurar?",
            "configurar_autenticacao": "Configurar Autenticación",
            "nome_usuario": "Nombre de usuario:",
            "salvar_configuracoes": "Guardar Todas las Configuraciones",
            "configuracoes_salvas": "¡Todas las configuraciones se han guardado con éxito!",
            "erro_salvar_config": "Error al guardar configuraciones",
            
            # Botones
            "sim": "Sí",
            "nao": "No",
            "ok": "OK",
            "fechar": "Cerrar",
            "editar": "Editar",
            "excluir": "Eliminar",
            "atualizar": "Actualizar",
            "novo": "Nuevo",
            
            # Informes
            "relatorios": "Informes",
            "gerar_relatorio": "Generar Informe",
            "relatorio_mensal": "Informe Mensual",
            "relatorio_anual": "Informe Anual",
            "relatorio_personalizado": "Informe Personalizado",
            "exportar_pdf": "Exportar PDF",
            
            # Seguridad
            "seguranca": "Seguridad",
            "criptografia": "Cifrado",
            "backup_seguro": "Copia Segura",
            "autenticacao": "Autenticación",
            "senha": "Contraseña",
            "confirmar_senha": "Confirmar Contraseña",
            
            # Temas
            "tema_claro": "Tema Claro",
            "tema_escuro": "Tema Oscuro",
            "tema_personalizado": "Tema Personalizado",
            "cores": "Colores",
            "fonte": "Fuente",
            "tamanho_fonte": "Tamaño de Fuente",
            
            # Placeholder texts
            "placeholder_equipa_casa": "Nombre del equipo local",
            "placeholder_equipa_fora": "Nombre del equipo visitante",
            "placeholder_odd": "Ej: 2.50",
            "placeholder_valor": "Ej: 10.00",
            
            # Tipos de aposta específicos
            "1x2": "1X2",
            "over_under_golos": "Over/Under Goles",
            "over_under_cantos": "Over/Under Córners",
            "handicap_asiatico": "Hándicap Asiático",
            "ambas_marcam": "Ambos Equipos Marcan",
            "dupla_hipotese": "Doble Oportunidad",
            "resultado_exato": "Resultado Exacto",
            
            # Informações da aplicação
            "versao_info": "Versión: 1.1 - Refinamiento y Estabilidad",
            "desenvolvido_info": "Desarrollado en Python con CustomTkinter",
            "base_dados_info": "Base de datos: SQLite con encriptación",
            "funcionalidades_info": "Funcionalidades: Registro, Análisis, ML, Informes PDF",
            "novidades_versao": "Novedades de la Versión 1.1:",
            "suporte_multilingue": "Soporte multiidioma (PT/EN/ES)",
            "sistema_temas": "Sistema de temas personalizables",
            "relatorios_pdf": "Informes PDF con gráficos",
            "criptografia_dados": "Encriptación de datos sensibles",
            "modo_escuro": "Modo oscuro mejorado",
            "dicas_titulo": "Consejos:",
            "dica_backup": "Haga copias de seguridad regulares de sus datos",
            "dica_analise": "Analice los patrones regularmente",
            "dica_banca": "Use la gestión de banca responsablemente",
            "dica_ml": "Aproveche los análisis de ML para mejorar",
            "dica_temas": "Pruebe los nuevos temas e idiomas",
            
            # Relatórios
            "incluir_analise_detalhada": "Incluir Análisis Detallado",
            "incluir_recomendacoes": "Incluir Recomendaciones",
            
            # Dashboard Avançado
            "dashboard_avancado_titulo": "Panel Avanzado de Apuestas",
            "ultima_atualizacao": "Última actualización",
            "auto_refresh": "Auto-actualizar",
            "atualizar": "Actualizar",
            "exportar": "Exportar",
            "metricas_principais": "Métricas Principales",
            "total_de_apostas": "Total de Apuestas",
            "taxa_de_acerto": "Tasa de Acierto",
            "retorno_medio": "Retorno Promedio",
            "sharpe_ratio": "Ratio de Sharpe",
            "max_drawdown": "Drawdown Máximo",
            "profit_factor": "Factor de Beneficio",
            "analise_de_performance": "Análisis de Rendimiento",
            "evolucao_do_lucro": "Evolución del Beneficio",
            "distribuicao_de_retornos": "Distribución de Retornos",
            "por_competicao": "Por Competición",
            "heatmap": "Mapa de Calor",
            
            # Visualizações Avançadas
            "visualizacoes_avancadas": "Visualizaciones Avanzadas",
            "heatmaps": "Mapas de Calor",
            "waterfall": "Cascada",
            "correlacoes": "Correlaciones",
            "performance": "Rendimiento",
            "analise_de_risco": "Análisis de Riesgo",
            "tipo_de_heatmap": "Tipo de Mapa de Calor",
            "performance_por_dia_semana": "Rendimiento por Día de la Semana",
            "performance_por_hora": "Rendimiento por Hora",
            "performance_por_mes": "Rendimiento por Mes",
            "performance_por_competicao": "Rendimiento por Competición",
            "odds_vs_resultado": "Cuotas vs Resultado",
            "valor_vs_roi": "Valor vs ROI",
            "periodo": "Período",
            "ultimo_mes": "Último mes",
            "ultimos_3_meses": "Últimos 3 meses",
            "ultimos_6_meses": "Últimos 6 meses",
            "ultimo_ano": "Último año",
            "atualizar_correlacoes": "Actualizar Correlaciones",
            "atualizar_performance": "Actualizar Rendimiento",
            "atualizar_analise_risco": "Actualizar Análisis de Riesgo",
            "var_95": "VaR (95%)",
            "drawdown_maximo": "Drawdown Máximo",
            "volatilidade": "Volatilidad",
            "calculando": "Calculando...",
            
            # Versión 1.2 - IA y Automatización
            "ai_automation": "IA y Automatización",
            "ai_dashboard": "Dashboard IA",
            "strategy_simulator": "Simulador de Estrategias",
            "pattern_detection": "Detección de Patrones",
            "tipster_tracker": "Rastreador de Tipsters",
            "risk_behavior": "Análisis de Riesgo",
            "classic_modules": "Módulos Clásicos",
            "classic_dashboard": "Dashboard Clásico",
            "advanced_visualizations": "Visualizaciones Avanzadas",
            "system_status": "Estado del Sistema",
            "active_alerts": "Alertas Activas",
            "no_alerts": "Sin alertas",
            "risk_analysis_unavailable": "Análisis de riesgo no disponible",
            "critical_risk_alert": "ALERTA CRÍTICA DE RIESGO",
            "high_risk_behavior_detected": "Se detectaron comportamientos de alto riesgo. Se recomienda pausa inmediata en las apuestas.",
            "recommendation": "Recomendación",
            "intelligent_dashboard": "Dashboard Inteligente",
            "risk_score": "Puntuación de Riesgo",
            "risk_level": "Nivel de Riesgo",
            "best_tipster": "Mejor Tipster",
            "rating": "Calificación",
            "tipsters": "Tipsters",
            "none_registered": "Ninguno registrado",
            "profitable_patterns": "Patrones Rentables",
            "total": "Total",
            "patterns": "Patrones",
            "analysis_unavailable": "Análisis no disponible",
            "ai_insights": "Insights de IA",
            "healthy_betting_behavior": "¡Comportamiento de apuestas saludable detectado!",
            "behavior_analysis_unavailable": "Análisis de comportamiento no disponible",
            "quick_analysis": "Análisis Rápido",
            "simulate_strategy": "Simular Estrategia",
            "detect_patterns": "Detectar Patrones",
            "manage_tipsters": "Gestionar Tipsters",
            "visual_summary": "Resumen Visual",
            "recent_evolution": "Evolución Reciente (Últimas 30 Apuestas)",
            "date": "Fecha",
            "accumulated_profit": "Beneficio Acumulado (€)",
            "insufficient_data_visual": "Datos insuficientes para análisis visual",
            "error_generating_charts": "Error al generar gráficos",
            "strategy": "Estrategia",
            "initial_bankroll": "Banca Inicial (€)",
            "days_to_simulate": "Días a Simular",
            "fixed_bet_amount": "Cantidad Fija de Apuesta (€)",
            "kelly_fraction": "Fracción Kelly",
            "bankroll_percentage": "Porcentaje de Banca (%)",
            "base_bet": "Apuesta Base (€)",
            "max_sequence": "Secuencia Máx.",
            "max_level": "Nivel Máximo",
            "execute_simulation": "Ejecutar Simulación",
            "executing_simulation": "Ejecutando simulación...",
            "final_profit": "Beneficio Final",
            "roi": "ROI",
            "max_drawdown_short": "Drawdown Máx.",
            "bankroll_evolution": "Evolución de la Banca",
            "bet_number": "Apuesta #",
            "bankroll_value": "Valor de la Banca (€)",
            "simulation_error": "Error en la simulación. Verifique los datos históricos.",
            "strategy_comparison": "Comparación de Estrategias",
            "compare_all_strategies": "Comparar Todas las Estrategias",
            "comparing_strategies": "Comparando estrategias...",
            "comparison_error": "Error en la comparación",
            "pattern_detection_ai": "Detección de Patrones con IA",
            "analysis_type": "Tipo de Análisis",
            "patterns_by_weekday": "Patrones por Día de la Semana",
            "patterns_by_odds_range": "Patrones por Rango de Cuotas",
            "patterns_by_competition": "Patrones por Competición",
            "patterns_by_bet_type": "Patrones por Tipo de Apuesta",
            "combined_analysis": "Análisis Combinado",
            "analysis_period_days": "Período de Análisis (días)",
            "analyze_patterns": "Analizar Patrones",
            "analyzing_patterns": "Analizando patrones...",
            "patterns_found": "patrones encontrados!",
            "profitable_patterns_detected": "Patrones Rentables Detectados",
            "pattern": "Patrón",
            "win_rate": "Tasa de Acierto",
            "num_bets": "Nº Apuestas",
            "description": "Descripción",
            "confidence": "Confianza",
            "risk_patterns_detected": "Patrones de Riesgo Detectados",
            "no_significant_patterns": "No se detectaron patrones significativos en el período analizado.",
            "ai_predictions": "Predicciones de IA",
            "train_prediction_model": "Entrenar Modelo de Predicción",
            "training_ai_model": "Entrenando modelo de IA...",
            "model_trained_successfully": "¡Modelo entrenado con éxito! Precisión:",
            "prediction_next_bet": "Predicción para Próxima Apuesta",
            "odds": "Cuotas",
            "value": "Valor (€)",
            "weekday": "Día de la Semana",
            "make_prediction": "Hacer Predicción",
            "win_probability": "Probabilidad de Victoria",
            "prediction_error": "Error en la predicción",
            "training_error": "Error en el entrenamiento. Verifique los datos históricos.",
            "training_error_general": "Error en el entrenamiento",
            "ranking": "Ranking",
            "add_tipster": "Agregar Tipster",
            "statistics": "Estadísticas",
            "link_bets": "Vincular Apuestas",
            "tipster_ranking": "Ranking de Tipsters",
            "period": "Período",
            "update_ranking": "Actualizar Ranking",
            "tipster": "Tipster",
            "tips": "Tips",
            "profit": "Beneficio",
            "trend": "Tendencia",
            "top_3_tipsters": "Top 3 Tipsters",
            "no_tipsters_registered": "Aún no hay tipsters registrados.",
            "error_loading_ranking": "Error al cargar ranking",
            "add_new_tipster": "Agregar Nuevo Tipster",
            "tipster_name": "Nombre del Tipster*",
            "source": "Fuente (ej: Telegram, YouTube)*",
            "category": "Categoría",
            "football": "Fútbol",
            "basketball": "Baloncesto",
            "tennis": "Tenis",
            "others": "Otros",
            "notes_optional": "Notas (opcional)",
            "tipster_added_successfully": "¡Tipster agregado con éxito! ID:",
            "name_source_required": "¡Nombre y fuente son obligatorios!",
            "detailed_statistics": "Estadísticas Detalladas",
            "select_tipster": "Seleccionar Tipster",
            "analysis_period": "Período de Análisis",
            "generate_statistics": "Generar Estadísticas",
            "calculating_statistics": "Calculando estadísticas...",
            "total_tips": "Total Tips",
            "total_roi": "ROI Total",
            "total_profit": "Beneficio Total",
            "amount_bet": "Cantidad Apostada",
            "best_sequence": "Mejor Secuencia",
            "wins": "victorias",
            "current_sequence": "Secuencia Actual",
            "additional_info": "Información Adicional",
            "days_active": "Días Activo",
            "tips_per_month": "Tips por Mes",
            "average_odds": "Cuota Promedio",
            "average_value": "Valor Promedio",
            "last_tip": "Último Tip",
            "rising": "Subiendo",
            "falling": "Bajando",
            "stable": "Estable",
            "insufficient_data_tipster": "Datos insuficientes para este tipster en el período seleccionado.",
            "no_tipsters_add_first": "No hay tipsters registrados. Agregue un tipster primero.",
            "error_loading_statistics": "Error al cargar estadísticas",
            "link_bets_to_tipsters": "Vincular Apuestas a Tipsters",
            "bets_without_tipster_found": "apuestas sin tipster asociado encontradas.",
            "select_bet": "Seleccionar Apuesta",
            "tip_source_optional": "Fuente del Tip (opcional)",
            "link": "Vincular",
            "bet_linked_successfully": "¡Apuesta vinculada con éxito!",
            "error_linking_bet": "Error al vincular apuesta.",
            "no_tipsters_available": "No hay tipsters disponibles. Agregue tipsters primero.",
            "all_bets_have_tipsters": "¡Todas las apuestas ya tienen tipsters asociados!",
            "error_loading_bets": "Error al cargar apuestas",
            "risk_behavior_analysis": "Análisis de Comportamiento de Riesgo",
            "general_risk_score": "Puntuación General de Riesgo",
            "risk_level_low": "Bajo",
            "risk_level_medium": "Medio",
            "risk_level_high": "Alto",
            "risk_level_critical": "Crítico",
            "largest_loss_sequence": "Mayor Sec. Pérdidas",
            "impulse_bets": "Apuestas Impulso",
            "value_variation": "Variación de Valores",
            "personalized_recommendations": "Recomendaciones Personalizadas",
            "temporal_risk_patterns": "Patrones Temporales de Riesgo",
            "risk_hours": "Horas de Riesgo",
            "risk_days": "Días de Riesgo",
            "no_risk_hours_identified": "No se identificaron horas de riesgo",
            "no_risk_days_identified": "No se identificaron días de riesgo",
            "error_risk_analysis": "Error en el análisis de riesgo",
            "real_time_risk_detection": "Detección de Patrones de Riesgo en Tiempo Real",
            "detection_period": "Período de Detección",
            "detect_risk_patterns": "Detectar Patrones de Riesgo",
            "analyzing_risk_patterns": "Analizando patrones de riesgo...",
            "new_risk_patterns_detected": "nuevos patrones de riesgo detectados!",
            "type": "Tipo",
            "involved_value": "Valor Involucrado",
            "no_risk_patterns_detected": "¡No se detectaron patrones de riesgo en el período analizado!",
            "detection_error": "Error en la detección",
            "resolve_alert": "Resolver Alerta",
            "alert_resolved": "¡Alerta resuelta!",
            "error_resolving_alert": "Error al resolver alerta",
            "no_active_alerts": "¡No hay alertas activas en este momento!",
            "error_loading_alerts": "Error al cargar alertas",
            "risk_visualization": "Visualización de Riesgo",
            "generate_risk_charts": "Generar Gráficos de Riesgo",
            "generating_visualizations": "Generando visualizaciones...",
            "insufficient_data_visualization": "Datos insuficientes para visualización",
            "error_generating_charts_risk": "Error al generar gráficos"
        }
        
        # Salvar traduções em arquivos JSON
        self._salvar_traducoes_arquivos()
    
    def _salvar_traducoes_arquivos(self):
        """Salva traduções em arquivos JSON separados."""
        try:
            for idioma, traducoes in self.traducoes.items():
                arquivo_path = os.path.join(self.traducoes_path, f"{idioma.value}.json")
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    json.dump(traducoes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar arquivos de tradução: {e}")
    
    def carregar_traducoes_arquivo(self, idioma: Idioma) -> bool:
        """Carrega traduções de arquivo JSON."""
        try:
            arquivo_path = os.path.join(self.traducoes_path, f"{idioma.value}.json")
            if os.path.exists(arquivo_path):
                with open(arquivo_path, 'r', encoding='utf-8') as f:
                    self.traducoes[idioma] = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Erro ao carregar traduções do arquivo: {e}")
            return False
    
    def definir_idioma(self, idioma: Idioma) -> bool:
        """Define o idioma atual do sistema."""
        try:
            if idioma in self.traducoes:
                self.idioma_atual = idioma
                self._salvar_configuracoes()
                return True
            return False
        except Exception as e:
            print(f"Erro ao definir idioma: {e}")
            return False
    
    def obter_idioma_atual(self) -> Idioma:
        """Retorna o idioma atual."""
        return self.idioma_atual
    
    def obter_idiomas_disponiveis(self) -> List[Idioma]:
        """Retorna lista de idiomas disponíveis."""
        return list(self.traducoes.keys())
    
    def traduzir(self, chave: str, idioma: Optional[Idioma] = None) -> str:
        """Traduz uma chave para o idioma especificado ou atual."""
        if idioma is None:
            idioma = self.idioma_atual
        
        if idioma in self.traducoes:
            return self.traducoes[idioma].get(chave, chave)
        
        # Fallback para português se idioma não encontrado
        return self.traducoes[Idioma.PORTUGUES].get(chave, chave)
    
    def traduzir_multiplas(self, chaves: List[str], idioma: Optional[Idioma] = None) -> Dict[str, str]:
        """Traduz múltiplas chaves de uma vez."""
        resultado = {}
        for chave in chaves:
            resultado[chave] = self.traduzir(chave, idioma)
        return resultado
    
    def adicionar_traducao(self, chave: str, traducoes_dict: Dict[Idioma, str]) -> bool:
        """Adiciona nova tradução para todos os idiomas."""
        try:
            for idioma, traducao in traducoes_dict.items():
                if idioma in self.traducoes:
                    self.traducoes[idioma][chave] = traducao
            
            # Salvar em arquivos
            self._salvar_traducoes_arquivos()
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar tradução: {e}")
            return False
    
    def remover_traducao(self, chave: str) -> bool:
        """Remove uma tradução de todos os idiomas."""
        try:
            for idioma in self.traducoes:
                if chave in self.traducoes[idioma]:
                    del self.traducoes[idioma][chave]
            
            # Salvar em arquivos
            self._salvar_traducoes_arquivos()
            return True
            
        except Exception as e:
            print(f"Erro ao remover tradução: {e}")
            return False
    
    def obter_todas_chaves(self) -> List[str]:
        """Retorna todas as chaves de tradução disponíveis."""
        if self.idioma_atual in self.traducoes:
            return list(self.traducoes[self.idioma_atual].keys())
        return []
    
    def verificar_traducoes_faltantes(self) -> Dict[Idioma, List[str]]:
        """Verifica traduções faltantes em cada idioma."""
        todas_chaves = set()
        
        # Coletar todas as chaves de todos os idiomas
        for traducoes in self.traducoes.values():
            todas_chaves.update(traducoes.keys())
        
        faltantes = {}
        for idioma, traducoes in self.traducoes.items():
            chaves_faltantes = todas_chaves - set(traducoes.keys())
            if chaves_faltantes:
                faltantes[idioma] = list(chaves_faltantes)
        
        return faltantes
    
    def exportar_traducoes(self, idioma: Idioma, caminho_arquivo: str) -> bool:
        """Exporta traduções de um idioma para arquivo."""
        try:
            if idioma in self.traducoes:
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(self.traducoes[idioma], f, indent=2, ensure_ascii=False)
                return True
            return False
        except Exception as e:
            print(f"Erro ao exportar traduções: {e}")
            return False
    
    def importar_traducoes(self, idioma: Idioma, caminho_arquivo: str) -> bool:
        """Importa traduções de arquivo para um idioma."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                traducoes_importadas = json.load(f)
            
            if idioma not in self.traducoes:
                self.traducoes[idioma] = {}
            
            self.traducoes[idioma].update(traducoes_importadas)
            self._salvar_traducoes_arquivos()
            return True
            
        except Exception as e:
            print(f"Erro ao importar traduções: {e}")
            return False
    
    def obter_estatisticas_traducoes(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre as traduções."""
        stats = {
            "total_idiomas": len(self.traducoes),
            "idioma_atual": self.idioma_atual.value,
            "por_idioma": {}
        }
        
        for idioma, traducoes in self.traducoes.items():
            stats["por_idioma"][idioma.value] = {
                "total_chaves": len(traducoes),
                "nome_idioma": self._obter_nome_idioma(idioma)
            }
        
        # Verificar completude
        faltantes = self.verificar_traducoes_faltantes()
        stats["traducoes_faltantes"] = {idioma.value: len(chaves) for idioma, chaves in faltantes.items()}
        
        return stats
    
    def _obter_nome_idioma(self, idioma: Idioma) -> str:
        """Retorna nome legível do idioma."""
        nomes = {
            Idioma.PORTUGUES: "Português",
            Idioma.INGLES: "English",
            Idioma.ESPANHOL: "Español"
        }
        return nomes.get(idioma, idioma.value)

# Instância global do gestor de traduções
_gestor_traducoes = None

def inicializar_traducoes() -> GestorTraducoes:
    """Inicializa o sistema de traduções."""
    global _gestor_traducoes
    if _gestor_traducoes is None:
        _gestor_traducoes = GestorTraducoes()
    return _gestor_traducoes

def t(chave: str, idioma: Optional[Idioma] = None) -> str:
    """Função de conveniência para tradução rápida."""
    global _gestor_traducoes
    if _gestor_traducoes is None:
        _gestor_traducoes = GestorTraducoes()
    return _gestor_traducoes.traduzir(chave, idioma)

def definir_idioma_global(idioma: Idioma) -> bool:
    """Define idioma global do sistema."""
    global _gestor_traducoes
    if _gestor_traducoes is None:
        _gestor_traducoes = GestorTraducoes()
    return _gestor_traducoes.definir_idioma(idioma)

def obter_idioma_atual() -> Idioma:
    """Obtém idioma atual do sistema."""
    global _gestor_traducoes
    if _gestor_traducoes is None:
        _gestor_traducoes = GestorTraducoes()
    return _gestor_traducoes.obter_idioma_atual()

def obter_gestor_traducoes() -> GestorTraducoes:
    """Obtém instância do gestor de traduções."""
    global _gestor_traducoes
    if _gestor_traducoes is None:
        _gestor_traducoes = GestorTraducoes()
    return _gestor_traducoes

if __name__ == "__main__":
    # Teste do módulo
    try:
        gestor = GestorTraducoes()
        
        print("Idiomas disponíveis:")
        for idioma in gestor.obter_idiomas_disponiveis():
            print(f"- {gestor._obter_nome_idioma(idioma)} ({idioma.value})")
        
        print(f"\nIdioma atual: {gestor._obter_nome_idioma(gestor.obter_idioma_atual())}")
        
        # Teste de traduções
        print("\nTeste de traduções:")
        chaves_teste = ["titulo_aplicacao", "dashboard", "nova_aposta", "historico"]
        
        for idioma in [Idioma.PORTUGUES, Idioma.INGLES, Idioma.ESPANHOL]:
            print(f"\n{gestor._obter_nome_idioma(idioma)}:")
            for chave in chaves_teste:
                print(f"  {chave}: {gestor.traduzir(chave, idioma)}")
        
        # Estatísticas
        print("\nEstatísticas:")
        stats = gestor.obter_estatisticas_traducoes()
        for idioma, info in stats["por_idioma"].items():
            print(f"  {info['nome_idioma']}: {info['total_chaves']} traduções")
        
        # Teste da função de conveniência
        print(f"\nTeste função t(): {t('titulo_aplicacao')}")
        
    except Exception as e:
        print(f"Erro no teste: {e}")