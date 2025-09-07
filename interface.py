#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica Principal - Programa de Apostas Desportivas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from datetime import datetime, date
import threading
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
# import seaborn as sns  # Temporariamente comentado
import pandas as pd


from main import DatabaseManager, Aposta
from historico import HistoricoFrame
from estatisticas import EstatisticasFrame
from banca import BancaFrame
from analise import AnaliseFrame
from dashboard_avancado import DashboardAvancado
from visualizacoes_avancadas import VisualizacoesAvancadas
from validacao import SmartEntry, DataValidator, AutoCompleter
from analise_risco import RiskAnalyzer
from importacao_dados import ImportExportInterface
from alertas_inteligentes import AlertsInterface, check_bet_alerts
# Novos módulos da versão 1.1
from relatorios import GeradorRelatorios
from seguranca import GestorSeguranca
from temas import GestorTemas, EditorTemas
from traducoes import GestorTraducoes, Idioma, t
# Novos módulos da versão 1.2 - Inteligência e Automação
from simulador_estrategias import StrategySimulator
from detecao_padroes import PatternDetector
from tipster_tracker import TipsterTracker
from comportamento_risco import ComportamentoRisco

# Novos módulos da Versão 2.0 - Plataforma Profissional
try:
    from usuarios import gestor_utilizadores, TipoUtilizador, PermissaoSistema
    from autenticacao import GestorAutenticacao, JanelaLogin
    from ml_previsoes import GestorML
    from ml_rapido import GestorMLRapido
    VERSAO_2_DISPONIVEL = True
except ImportError:
    VERSAO_2_DISPONIVEL = False
    print("ℹ️ Módulos da Versão 2.0 não disponíveis - executando em modo compatibilidade")

# API removida para simplificar o programa
import json
import os
from pathlib import Path

class ApostasApp:
    """Aplicação principal de gestão de apostas"""
    
    def __init__(self):
        # Inicializar variáveis da Versão 2.0
        self.utilizador_atual = None
        self.utilizador_id = None  # Não definir ID até login
        self.modo_multiutilizador = True  # Forçar modo multiutilizador
        self.gestor_autenticacao = None
        # Widget de gamificação removido
        self.interface_criada = False  # Flag para controlar criação da interface
        
        # Configurar scaling do CustomTkinter com patch abrangente para valores inteiros
        try:
            # Patch abrangente para interceptar todas as configurações do Tkinter
            import tkinter as tk
            
            # Função para converter valores para inteiros
            def force_int_values(kwargs):
                for key in ['width', 'height', 'x', 'y']:
                    if key in kwargs and kwargs[key] is not None:
                        try:
                            kwargs[key] = int(float(str(kwargs[key])))
                        except (ValueError, TypeError):
                            pass
                return kwargs
            
            # Patch para Canvas.configure
            original_canvas_configure = tk.Canvas.configure
            def patched_canvas_configure(self, cnf=None, **kw):
                if cnf is None:
                    cnf = {}
                if isinstance(cnf, dict):
                    cnf = force_int_values(cnf)
                kw = force_int_values(kw)
                return original_canvas_configure(self, cnf, **kw)
            tk.Canvas.configure = patched_canvas_configure
            
            # Patch para Widget.__init__
            original_widget_init = tk.Widget.__init__
            def patched_widget_init(self, master, widgetName, cnf={}, kw=None, extra=()):
                if kw is None:
                    kw = {}
                cnf = force_int_values(cnf.copy() if isinstance(cnf, dict) else {})
                kw = force_int_values(kw.copy())
                return original_widget_init(self, master, widgetName, cnf, kw, extra)
            tk.Widget.__init__ = patched_widget_init
            
            ctk.set_widget_scaling(1.0)
            ctk.set_window_scaling(1.0)
            ctk.set_appearance_mode("dark")
            print("✅ CustomTkinter configurado com patch abrangente para valores inteiros")
        except Exception as e:
            print(f"⚠️ Aviso ao configurar CustomTkinter: {e}")
        
        self.db = DatabaseManager()
        
        # Criar janela principal com configurações básicas
        try:
            self.root = ctk.CTk()
            self.root.geometry("1200x800")  # Tamanho mais conservador
            self.root.minsize(1000, 700)
            self.root.state('zoomed')  # Abrir maximizada no Windows
            
            # Configurar ícone da aplicação
            try:
                icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    self.root.title("Sistema de Apostas Desportivas v2.0")
                    print(f"✅ Ícone carregado: {icon_path}")
                else:
                    self.root.title("⚽ Sistema de Apostas Desportivas v2.0")
                    print("⚠️ Ícone não encontrado, usando emoji no título")
            except Exception as icon_error:
                print(f"⚠️ Aviso: Não foi possível carregar o ícone: {icon_error}")
                self.root.title("⚽ Sistema de Apostas Desportivas v2.0")
            
            print("✅ Janela principal criada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar janela: {e}")
            raise
        
        # Inicializar validador, autocompleter e analisador de risco
        self.validator = DataValidator(self.db)
        self.autocompleter = AutoCompleter(self.db)
        self.risk_analyzer = RiskAnalyzer(self.db)
        
        # Inicializar novos módulos da versão 1.1
        self.gestor_temas = GestorTemas()
        self.gestor_traducoes = GestorTraducoes()
        self.gestor_seguranca = GestorSeguranca()
        self.gerador_relatorios = GeradorRelatorios(self.db.db_path)
        
        # Inicializar novos módulos da versão 1.2 - Inteligência e Automação
        self.strategy_simulator = StrategySimulator(self.db.db_path)
        self.pattern_detector = PatternDetector(self.db.db_path)
        self.tipster_tracker = TipsterTracker(self.db.db_path)
        self.risk_analyzer_v2 = ComportamentoRisco(self.db.db_path)
        
        # Inicializar Gestor ML se disponível
        if VERSAO_2_DISPONIVEL:
            try:
                print("🤖 Inicializando sistema ML...")
                self.gestor_ml = GestorML(self.db.db_path)
                print(f"✅ GestorML inicializado: {type(self.gestor_ml)}")
                
                self.gestor_ml_rapido = GestorMLRapido(self.db.db_path)  # Versão otimizada
                print(f"✅ GestorMLRapido inicializado: {type(self.gestor_ml_rapido)}")
                
                # Carregar modelos salvos
                self.gestor_ml.carregar_modelos_salvos()
                print(f"📊 Modelos carregados: {list(self.gestor_ml.modelos.keys())}")
                print(f"🎯 Modelo ativo: {self.gestor_ml.modelo_ativo}")
                
            except Exception as e:
                print(f"❌ Erro ao inicializar GestorML: {e}")
                import traceback
                traceback.print_exc()
                self.gestor_ml = None
                self.gestor_ml_rapido = None
        else:
            print("⚠️ Versão 2.0 não disponível - ML desabilitado")
            self.gestor_ml = None
            self.gestor_ml_rapido = None
        
        # PRIORIZAR LOGIN - Mostrar login antes de criar interface completa
        if VERSAO_2_DISPONIVEL:
            try:
                self.gestor_autenticacao = GestorAutenticacao()
                # Esconder janela principal e mostrar login
                self.root.withdraw()
                self.mostrar_login_prioritario()
            except Exception as e:
                print(f"Erro ao inicializar autenticação: {e}")
                messagebox.showerror("Erro", f"Erro no sistema de autenticação: {e}")
                # Se falhar, criar interface normalmente
                self._criar_interface_completa()
        else:
            print("⚠️ Sistema de login não disponível - executando em modo compatibilidade")
            self.utilizador_id = 1
            self._criar_interface_completa()
    
    def _criar_interface_completa(self):
        """Criar a interface completa após autenticação - OTIMIZADO"""
        print("🚀 Criando interface otimizada...")
        
        # Configuração rápida da janela
        self.setup_window()
        
        # Criar apenas componentes essenciais primeiro
        self.create_sidebar()
        self.create_main_content_rapido()
        self.create_status_bar()
        
        # Aplicar configurações básicas
        try:
            tema_atual = self.gestor_temas.obter_tema_atual()
            if tema_atual:
                self.gestor_temas.aplicar_tema(tema_atual.nome)
        except:
            pass
        
        # Carregar dados essenciais
        self.load_data_rapido()
        
        self.interface_criada = True
        print("✅ Interface principal criada (modo rápido)")
        
        # Carregar componentes pesados em background
        import threading
        threading.Thread(target=self._carregar_resto_background, daemon=True).start()
    
    def setup_window(self):
        """Configuração da janela principal"""
        self.root.title(f"⚽ {t('titulo_aplicacao')} v1.2 - Inteligência e Automação")
        # Geometria já configurada no __init__
        
        # Configurar grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Cores personalizadas
        self.colors = {
            'primary': '#1f538d',
            'secondary': '#14375e',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'dark': '#343a40',
            'light': '#f8f9fa'
        }
    
    def create_widgets(self):
        """Criar todos os widgets da interface"""
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
    

    def create_sidebar(self):
        """Criar barra lateral de navegação com scroll"""
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(1, weight=1)
        
        # Logo/Título fixo no topo
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚽ APOSTAS\nDESPORTIVAS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 20), sticky="ew")
        
        # Frame scrollável para os botões
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            width=230,
            corner_radius=0,
            fg_color="transparent"
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Botões de navegação
        self.nav_buttons = {}
        nav_items = [
            (f"📊 {t('dashboard')}", "dashboard"),
            (f"📈 {t('dashboard_avancado')}", "dashboard_avancado"),
            (f"📊 {t('visualizacoes')}", "visualizacoes"),
            (f"➕ {t('nova_aposta')}", "nova_aposta"),
            (f"📋 {t('historico')}", "historico"),
            (f"💰 {t('gestao_banca')}", "banca"),
            (f"📈 {t('estatisticas')}", "estatisticas"),
            (f"🔍 {t('analise')}", "analise"),
            (f"🤖 Simulador Estratégias", "simulador_estrategias"),
            (f"🧠 Deteção de Padrões", "detecao_padroes"),
            (f"👥 Tipster Tracker", "tipster_tracker"),
            (f"⚠️ Análise de Risco", "comportamento_risco"),
            (f"📥 {t('import_export')}", "import_export"),
            (f"🔔 {t('alertas')}", "alertas"),
            (f"📄 {t('relatorios')}", "relatorios"),
            (f"⚙️ {t('configuracoes')}", "configuracoes")
        ]
        
        # Adicionar botões da Versão 2.0 se disponíveis
        if VERSAO_2_DISPONIVEL:
            nav_items.extend([
                ("🤖 ML Previsões", "ml_previsoes"),
                # Gamificação removida
                ("👥 Utilizadores", "usuarios")
            ])
        
        # Adicionar botões ao frame scrollável
        for i, (text, key) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.scrollable_frame,
                text=text,
                command=lambda k=key: self.show_page(k),
                height=38,
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            btn.grid(row=i, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Separador
        separator = ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray30")
        separator.grid(row=len(nav_items), column=0, padx=10, pady=10, sticky="ew")
        
        # Informações da banca
        self.banca_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="gray20")
        self.banca_frame.grid(row=len(nav_items)+1, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            self.banca_frame,
            text=f"💰 {t('banca_atual')}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(8, 3))
        
        self.saldo_label = ctk.CTkLabel(
            self.banca_frame,
            text="€0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff88"
        )
        self.saldo_label.pack(pady=(0, 8))
        
        # Botão de backup
        backup_btn = ctk.CTkButton(
            self.scrollable_frame,
            text=f"💾 {t('backup')}",
            command=self.criar_backup,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(size=13)
        )
        backup_btn.grid(row=len(nav_items)+2, column=0, padx=10, pady=5, sticky="ew")
        
        # Configurar grid do frame scrollável
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def create_main_content(self):
        """Criar área de conteúdo principal"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Container para as páginas
        self.pages = {}
        self.current_page = None
        
        # Criar todas as páginas
        self.create_dashboard_page()
        self.create_dashboard_avancado_page()
        self.create_visualizacoes_page()
        self.create_nova_aposta_page()
        self.create_historico_page()
        self.create_banca_page()
        self.create_estatisticas_page()
        self.create_analise_page()
        self.create_import_export_page()
        self.create_alertas_page()
        self.create_relatorios_page()
        self.create_configuracoes_page()
        # Criar páginas da versão 1.2
        self.create_simulador_estrategias_page()
        self.create_detecao_padroes_page()
        self.create_tipster_tracker_page()
        self.create_comportamento_risco_page()
        
        # Criar páginas da Versão 2.0 se disponíveis
        if VERSAO_2_DISPONIVEL:
            # Página de gamificação removida
            self.create_usuarios_page()
            self.create_ml_previsoes_page()
        
        # Mostrar dashboard por padrão
        self.show_page("dashboard")
    
    def create_main_content_rapido(self):
        """Criar área de conteúdo principal com carregamento rápido"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Container para as páginas
        self.pages = {}
        self.current_page = None
        
        # Criar apenas dashboard inicial
        self.create_dashboard_page()
        
        # Mostrar dashboard por padrão
        self.show_page("dashboard")
    
    def create_status_bar(self):
        """Criar barra de status"""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Pronto",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Data/hora atual
        self.datetime_label = ctk.CTkLabel(
            self.status_frame,
            text=datetime.now().strftime("%d/%m/%Y %H:%M"),
            font=ctk.CTkFont(size=12)
        )
        self.datetime_label.pack(side="right", padx=10, pady=5)
        
        # Atualizar data/hora a cada minuto
        self.update_datetime()
    
    def create_dashboard_page(self):
        """Criar página do dashboard"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["dashboard"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="📊 Dashboard - Visão Geral",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame para cards de estatísticas
        stats_frame = ctk.CTkFrame(page)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Cards de estatísticas rápidas
        self.create_stats_cards(stats_frame)
        
        # Frame para gráficos
        charts_frame = ctk.CTkFrame(page)
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.create_dashboard_charts(charts_frame)
    
    def create_stats_cards(self, parent):
        """Criar cards de estatísticas rápidas"""
        parent.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Card 1: Total Apostado
        card1 = ctk.CTkFrame(parent)
        card1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(card1, text="💰 Total Apostado", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.total_apostado_label = ctk.CTkLabel(card1, text="€0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffc107")
        self.total_apostado_label.pack(pady=(0, 10))
        
        # Card 2: Lucro/Prejuízo
        card2 = ctk.CTkFrame(parent)
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(card2, text="📈 Lucro/Prejuízo", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.lucro_label = ctk.CTkLabel(card2, text="€0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#28a745")
        self.lucro_label.pack(pady=(0, 10))
        
        # Card 3: Taxa de Acerto
        card3 = ctk.CTkFrame(parent)
        card3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(card3, text="🎯 Taxa de Acerto", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.taxa_acerto_label = ctk.CTkLabel(card3, text="0%", font=ctk.CTkFont(size=18, weight="bold"), text_color="#17a2b8")
        self.taxa_acerto_label.pack(pady=(0, 10))
        
        # Card 4: ROI
        card4 = ctk.CTkFrame(parent)
        card4.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(card4, text="📊 ROI", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.roi_label = ctk.CTkLabel(card4, text="0%", font=ctk.CTkFont(size=18, weight="bold"), text_color="#dc3545")
        self.roi_label.pack(pady=(0, 10))
    
    def create_dashboard_charts(self, parent):
        """Criar gráficos do dashboard"""
        parent.grid_columnconfigure((0, 1), weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Gráfico de evolução da banca
        chart1_frame = ctk.CTkFrame(parent)
        chart1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(chart1_frame, text="📈 Evolução da Banca", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Placeholder para gráfico
        self.chart1_placeholder = ctk.CTkLabel(chart1_frame, text="Gráfico será carregado aqui", height=200)
        self.chart1_placeholder.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Gráfico de distribuição de resultados
        chart2_frame = ctk.CTkFrame(parent)
        chart2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(chart2_frame, text="🎯 Distribuição de Resultados", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Placeholder para gráfico
        self.chart2_placeholder = ctk.CTkLabel(chart2_frame, text="Gráfico será carregado aqui", height=200)
        self.chart2_placeholder.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_nova_aposta_page(self):
        """Criar página de nova aposta"""
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["nova_aposta"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="➕ Registar Nova Aposta",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Formulário
        form_frame = ctk.CTkFrame(page)
        form_frame.pack(fill="x", padx=50, pady=20)
        
        # Data e Hora
        ctk.CTkLabel(form_frame, text="📅 Data e Hora:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.data_entry = ctk.CTkEntry(form_frame, placeholder_text="DD/MM/AAAA HH:MM")
        self.data_entry.grid(row=0, column=1, sticky="ew", padx=20, pady=10)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        # Competição (com validação e auto-complete)
        ctk.CTkLabel(form_frame, text="🏆 Competição:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.competicao_combo = ctk.CTkComboBox(
            form_frame,
            values=["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Liga Portugal", "Champions League", "Europa League", "Outras"]
        )
        self.competicao_combo.grid(row=1, column=1, sticky="ew", padx=20, pady=10)
        
        # Equipas (com validação e auto-complete)
        ctk.CTkLabel(form_frame, text="🏠 " + t("equipa_casa") + ":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        self.equipa_casa_entry = SmartEntry(
            form_frame, 
            self.validator, 
            self.autocompleter,
            entry_type="team",
            placeholder_text=t("placeholder_equipa_casa")
        )
        self.equipa_casa_entry.grid(row=2, column=1, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="✈️ " + t("equipa_fora") + ":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self.equipa_fora_entry = SmartEntry(
            form_frame, 
            self.validator, 
            self.autocompleter,
            entry_type="team",
            placeholder_text=t("placeholder_equipa_fora")
        )
        self.equipa_fora_entry.grid(row=3, column=1, sticky="ew", padx=20, pady=10)
        
        # Tipo de Aposta
        ctk.CTkLabel(form_frame, text="🎯 " + t("tipo_aposta") + ":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=4, column=0, sticky="w", padx=20, pady=10)
        self.tipo_aposta_combo = ctk.CTkComboBox(
            form_frame,
            values=[t("1x2"), t("over_under_golos"), t("over_under_cantos"), t("handicap_asiatico"), t("ambas_marcam"), t("dupla_hipotese"), t("resultado_exato"), t("outros")]
        )
        self.tipo_aposta_combo.grid(row=4, column=1, sticky="ew", padx=20, pady=10)
        
        # Odd (com validação)
        ctk.CTkLabel(form_frame, text="📊 " + t("odd_cotacao") + ":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=5, column=0, sticky="w", padx=20, pady=10)
        self.odd_entry = SmartEntry(
            form_frame, 
            self.validator, 
            entry_type="odd",
            placeholder_text=t("placeholder_odd")
        )
        self.odd_entry.grid(row=5, column=1, sticky="ew", padx=20, pady=10)
        
        # Valor Apostado (com validação)
        ctk.CTkLabel(form_frame, text="💰 " + t("valor_apostado") + " (€):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=6, column=0, sticky="w", padx=20, pady=10)
        self.valor_entry = SmartEntry(
            form_frame, 
            self.validator, 
            entry_type="value",
            placeholder_text=t("placeholder_valor")
        )
        self.valor_entry.grid(row=6, column=1, sticky="ew", padx=20, pady=10)
        
        # Notas
        ctk.CTkLabel(form_frame, text="📝 " + t("notas_opcional") + ":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=7, column=0, sticky="w", padx=20, pady=10)
        self.notas_entry = ctk.CTkTextbox(form_frame, height=80)
        self.notas_entry.grid(row=7, column=1, sticky="ew", padx=20, pady=10)
        
        # Configurar grid
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botões
        buttons_frame = ctk.CTkFrame(page)
        buttons_frame.pack(fill="x", padx=50, pady=20)
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 " + t("guardar_aposta"),
            command=self.guardar_aposta,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        save_btn.pack(side="left", padx=10, pady=10)
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ " + t("limpar"),
            command=self.limpar_formulario,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        clear_btn.pack(side="right", padx=10, pady=10)
    
    def show_page(self, page_name):
        """Mostrar uma página específica"""
        # Esconder página atual
        if self.current_page:
            self.pages[self.current_page].pack_forget()
        
        # Mostrar nova página
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)
            self.current_page = page_name
            
            # Atualizar botões de navegação
            for key, btn in self.nav_buttons.items():
                if key == page_name:
                    btn.configure(fg_color="#1f538d")
                else:
                    btn.configure(fg_color="#2b2b2b")
            
            # Atualizar dados se necessário
            if page_name == "dashboard":
                self.update_dashboard()
            elif page_name == "dashboard_avancado":
                if hasattr(self.pages["dashboard_avancado"], 'refresh_data'):
                    self.pages["dashboard_avancado"].refresh_data()
            elif page_name == "visualizacoes":
                if hasattr(self.pages["visualizacoes"], 'refresh_data'):
                    self.pages["visualizacoes"].refresh_data()
            elif page_name == "historico":
                if hasattr(self.pages["historico"], 'load_apostas'):
                    self.pages["historico"].load_apostas()
            elif page_name == "estatisticas":
                if hasattr(self.pages["estatisticas"], 'load_data'):
                    self.pages["estatisticas"].load_data()
            elif page_name == "banca":
                if hasattr(self.pages["banca"], 'load_data'):
                    self.pages["banca"].load_data()
            elif page_name == "analise":
                if hasattr(self.pages["analise"], 'load_data'):
                    self.pages["analise"].load_data()
            elif page_name == "import_export":
                if hasattr(self.pages["import_export"], 'refresh_data'):
                    self.pages["import_export"].refresh_data()
            elif page_name == "alertas":
                if hasattr(self.pages["alertas"], 'refresh_alerts'):
                    self.pages["alertas"].refresh_alerts()
    
    def load_data(self):
        """Carregar dados iniciais"""
        self.update_saldo_display()
        self.update_dashboard()
    
    def load_data_rapido(self):
        """Carregar apenas dados essenciais rapidamente"""
        try:
            self.update_saldo_display()
            # Atualizar dashboard em background
            import threading
            threading.Thread(target=self._update_dashboard_background, daemon=True).start()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def _update_dashboard_background(self):
        """Atualizar dashboard em background"""
        try:
            import time
            time.sleep(0.5)  # Pequena pausa
            self.root.after(0, self.update_dashboard)
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def _carregar_resto_background(self):
        """Carregar resto dos componentes em background"""
        try:
            print("🔄 Carregando componentes restantes...")
            import time
            time.sleep(1)  # Pausa para não sobrecarregar
            
            # Criar páginas restantes
            self.root.after(0, self._criar_paginas_restantes)
            
            print("✅ Componentes restantes carregados!")
        except Exception as e:
            print(f"Erro ao carregar componentes: {e}")
    
    def _criar_paginas_restantes(self):
        """Criar páginas restantes"""
        try:
            # Criar páginas que não foram criadas ainda
            if "dashboard_avancado" not in self.pages:
                self.create_dashboard_avancado_page()
            if "visualizacoes" not in self.pages:
                self.create_visualizacoes_page()
            if "nova_aposta" not in self.pages:
                self.create_nova_aposta_page()
            if "historico" not in self.pages:
                self.create_historico_page()
            if "banca" not in self.pages:
                self.create_banca_page()
            if "estatisticas" not in self.pages:
                self.create_estatisticas_page()
            if "analise" not in self.pages:
                self.create_analise_page()
            if "import_export" not in self.pages:
                self.create_import_export_page()
            if "alertas" not in self.pages:
                self.create_alertas_page()
            if "relatorios" not in self.pages:
                self.create_relatorios_page()
            if "configuracoes" not in self.pages:
                self.create_configuracoes_page()
            
            # Páginas da versão 1.2
            if "simulador_estrategias" not in self.pages:
                self.create_simulador_estrategias_page()
            if "detecao_padroes" not in self.pages:
                self.create_detecao_padroes_page()
            if "tipster_tracker" not in self.pages:
                self.create_tipster_tracker_page()
            if "comportamento_risco" not in self.pages:
                self.create_comportamento_risco_page()
            
            # Páginas da Versão 2.0
            if VERSAO_2_DISPONIVEL:
                if "usuarios" not in self.pages:
                    self.create_usuarios_page()
                if "ml_previsoes" not in self.pages:
                    self.create_ml_previsoes_page()
            
            print("✅ Todas as páginas criadas")
        except Exception as e:
            print(f"Erro ao criar páginas restantes: {e}")
    
    def update_saldo_display(self):
        """Atualizar exibição do saldo"""
        saldo = self.db.get_saldo_atual()
        self.saldo_label.configure(text=f"€{saldo:.2f}")
        
        # Mudar cor baseada no saldo
        if saldo > 0:
            self.saldo_label.configure(text_color="#00ff88")
        else:
            self.saldo_label.configure(text_color="#ff4444")
    
    def update_datetime(self):
        """Atualizar data/hora na barra de status"""
        self.datetime_label.configure(text=datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.root.after(60000, self.update_datetime)  # Atualizar a cada minuto
    
    def update_dashboard(self):
        """Atualizar dados do dashboard"""
        try:
            # Verificar se os widgets existem antes de atualizar
            if not hasattr(self, 'total_apostado_label') or not hasattr(self, 'lucro_label'):
                return
                
            apostas = self.db.get_apostas()
            
            if not apostas:
                return
            
            # Calcular estatísticas
            total_apostado = sum(a.valor_apostado for a in apostas)
            total_lucro = sum(a.lucro_prejuizo for a in apostas if a.resultado in ["Ganha", "Perdida"])
            apostas_ganhas = len([a for a in apostas if a.resultado == "Ganha"])
            apostas_finalizadas = len([a for a in apostas if a.resultado in ["Ganha", "Perdida"]])
            
            taxa_acerto = (apostas_ganhas / apostas_finalizadas * 100) if apostas_finalizadas > 0 else 0
            roi = (total_lucro / total_apostado * 100) if total_apostado > 0 else 0
            
            # Atualizar labels
            self.total_apostado_label.configure(text=f"€{total_apostado:.2f}")
            self.lucro_label.configure(text=f"€{total_lucro:.2f}")
            self.taxa_acerto_label.configure(text=f"{taxa_acerto:.1f}%")
            self.roi_label.configure(text=f"{roi:.1f}%")
            
            # Atualizar cores baseadas nos valores
            self.lucro_label.configure(text_color="#28a745" if total_lucro >= 0 else "#dc3545")
            self.roi_label.configure(text_color="#28a745" if roi >= 0 else "#dc3545")
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def guardar_aposta(self):
        """Guardar nova aposta"""
        try:
            # Validar campos obrigatórios
            if not all([
                self.data_entry.get(),
                self.competicao_combo.get(),
                self.equipa_casa_entry.get(),
                self.equipa_fora_entry.get(),
                self.tipo_aposta_combo.get(),
                self.odd_entry.get(),
                self.valor_entry.get()
            ]):
                messagebox.showerror(t("erro"), t("preencha_campos"))
                return
            
            # Validar valores numéricos
            try:
                odd = float(self.odd_entry.get())
                valor = float(self.valor_entry.get())
                if odd <= 0 or valor <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror(t("erro"), t("valores_positivos"))
                return
            
            # Verificar se há saldo suficiente
            saldo_atual = self.db.get_saldo_atual()
            if valor > saldo_atual:
                messagebox.showerror("Erro", f"Saldo insuficiente. Saldo atual: €{saldo_atual:.2f}")
                return
            
            # Criar aposta
            aposta = Aposta(
                data_hora=self.data_entry.get(),
                competicao=self.competicao_combo.get(),
                equipa_casa=self.equipa_casa_entry.get(),
                equipa_fora=self.equipa_fora_entry.get(),
                tipo_aposta=self.tipo_aposta_combo.get(),
                odd=odd,
                valor_apostado=valor,
                resultado="Pendente",
                lucro_prejuizo=0.0,
                notas=self.notas_entry.get("1.0", "end-1c")
            )
            
            # Verificar alertas para esta aposta
            try:
                alerts = check_bet_alerts(
                    self.db,
                    self.equipa_casa_entry.get(),
                    self.equipa_fora_entry.get(),
                    odd,
                    valor
                )
                
                if alerts:
                    # Mostrar alertas de alta severidade
                    high_alerts = [alert for alert in alerts if alert.get('severity') == 'high']
                    medium_alerts = [alert for alert in alerts if alert.get('severity') == 'medium']
                    
                    if high_alerts or medium_alerts:
                        alert_message = "⚠️ Alertas detectados para esta aposta:\n\n"
                        
                        for alert in high_alerts + medium_alerts:
                            alert_message += f"• {alert.get('title', 'Alerta')}: {alert.get('message', '')}\n"
                        
                        alert_message += "\nDeseja continuar mesmo assim?"
                        
                        if not messagebox.askyesno("Alertas de Risco", alert_message):
                            return
            except Exception as e:
                print(f"Erro ao verificar alertas: {e}")
            
            # Guardar na base de dados
            aposta_id = self.db.adicionar_aposta(aposta)
            
            # Atualizar interface
            self.update_saldo_display()
            self.update_dashboard()
            
            # Limpar formulário
            self.limpar_formulario()
            
            messagebox.showinfo("Sucesso", f"Aposta #{aposta_id} registada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar aposta: {str(e)}")
    
    def limpar_formulario(self):
        """Limpar formulário de nova aposta"""
        self.data_entry.delete(0, "end")
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.competicao_combo.set("")
        self.equipa_casa_entry.set("")  # Usar método set para SmartEntry
        self.equipa_fora_entry.set("")  # Usar método set para SmartEntry
        self.tipo_aposta_combo.set("")
        self.odd_entry.set("")  # Usar método set para SmartEntry
        self.valor_entry.set("")  # Usar método set para SmartEntry
        self.notas_entry.delete("1.0", "end")
    
    def criar_backup(self):
        """Criar backup da base de dados"""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"apostas_backup_{timestamp}.db"
            
            # Copiar base de dados
            import shutil
            shutil.copy2("apostas.db", backup_file)
            
            messagebox.showinfo("Backup", f"Backup criado com sucesso:\n{backup_file}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar backup: {str(e)}")
    
    def run(self):
        """Executar a aplicação"""
        self.root.mainloop()

# Métodos placeholder para as outras páginas
    def create_dashboard_avancado_page(self):
        page = DashboardAvancado(self.main_frame, self.db)
        self.pages["dashboard_avancado"] = page
    
    def create_visualizacoes_page(self):
        page = VisualizacoesAvancadas(self.main_frame, self.db)
        self.pages["visualizacoes"] = page
    
    def create_historico_page(self):
        page = HistoricoFrame(self.main_frame, self.db, self.update_dashboard)
        self.pages["historico"] = page
    
    def create_banca_page(self):
        page = BancaFrame(self.main_frame, self.db, self.update_dashboard)
        self.pages["banca"] = page
    
    def create_estatisticas_page(self):
        page = EstatisticasFrame(self.main_frame, self.db)
        self.pages["estatisticas"] = page
    
    def create_analise_page(self):
        page = AnaliseFrame(self.main_frame, self.db)
        self.pages["analise"] = page
    
    def create_import_export_page(self):
        page = ImportExportInterface(self.main_frame, self.db)
        self.pages["import_export"] = page
    
    def create_alertas_page(self):
        page = AlertsInterface(self.main_frame, self.db)
        self.pages["alertas"] = page
    
    # Função API removida para simplificar o programa
    
    def create_configuracoes_page(self):
        """Criar página de configurações"""
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["configuracoes"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="⚙️ Configurações",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Configurações de Banca
        banca_frame = ctk.CTkFrame(page)
        banca_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            banca_frame,
            text="💰 Configurações de Banca",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Saldo inicial
        saldo_frame = ctk.CTkFrame(banca_frame)
        saldo_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            saldo_frame,
            text="Saldo Inicial (€):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.saldo_inicial_entry = ctk.CTkEntry(
            saldo_frame,
            placeholder_text="Ex: 1000.00",
            width=150
        )
        self.saldo_inicial_entry.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            saldo_frame,
            text="💾 Salvar",
            command=self.salvar_saldo_inicial,
            width=100
        ).pack(side="left", padx=10, pady=10)
        
        # Configurações de Backup
        backup_frame = ctk.CTkFrame(page)
        backup_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            backup_frame,
            text=f"💾 {t('backup_exportacao')}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        backup_buttons = ctk.CTkFrame(backup_frame)
        backup_buttons.pack(pady=10)
        
        ctk.CTkButton(
            backup_buttons,
            text=f"📁 {t('criar_backup')}",
            command=self.criar_backup,
            width=150,
            height=35
        ).pack(side="left", padx=10)
        
        # Configurações da Interface
        interface_frame = ctk.CTkFrame(page)
        interface_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            interface_frame,
            text=f"🎨 {t('aparencia')}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Idioma
        idioma_frame = ctk.CTkFrame(interface_frame)
        idioma_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            idioma_frame,
            text=f"{t('idioma')}:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.idioma_combo = ctk.CTkComboBox(
            idioma_frame,
            values=["Português", "English", "Español"],
            command=self.alterar_idioma,
            width=150
        )
        self.idioma_combo.pack(side="left", padx=10, pady=10)
        self.idioma_combo.set("Português")
        
        # Tema
        tema_frame = ctk.CTkFrame(interface_frame)
        tema_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            tema_frame,
            text=f"{t('tema')}:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        temas_disponiveis = self.gestor_temas.obter_temas_disponiveis()
        self.tema_combo = ctk.CTkComboBox(
            tema_frame,
            values=temas_disponiveis,
            command=self.alterar_tema_avancado,
            width=200
        )
        self.tema_combo.pack(side="left", padx=10, pady=10)
        
        # Definir tema atual
        tema_atual = self.gestor_temas.obter_tema_atual()
        if tema_atual:
            self.tema_combo.set(tema_atual.nome)
        else:
            self.tema_combo.set("Claro Padrão")
        
        # Botão para editor de temas
        ctk.CTkButton(
            tema_frame,
            text=f"🎨 {t('editor_temas')}",
            command=self.abrir_editor_temas,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        # Configurações de Segurança
        seguranca_frame = ctk.CTkFrame(page)
        seguranca_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            seguranca_frame,
            text=f"🔒 {t('seguranca')}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Opções de segurança
        seg_opcoes_frame = ctk.CTkFrame(seguranca_frame)
        seg_opcoes_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            seg_opcoes_frame,
            text=f"🔐 {t('criptografia')}",
            command=self.configurar_criptografia,
            width=200,
            height=35
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            seg_opcoes_frame,
            text=f"💾 {t('backup_seguro')}",
            command=self.criar_backup_seguro,
            width=200,
            height=35
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            seg_opcoes_frame,
            text=f"🔑 {t('configurar_autenticacao')}",
            command=self.configurar_autenticacao,
            width=200,
            height=35
        ).pack(side="left", padx=10)
        
        # Informações da Aplicação
        info_frame = ctk.CTkFrame(page)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"ℹ️ {t('sobre')}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Botão para abrir ficheiro Sobre.txt
        ctk.CTkButton(
            info_frame,
            text="📄 Ver Informações Completas",
            command=self.abrir_ficheiro_sobre,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#17a2b8",
            hover_color="#138496"
        ).pack(pady=10)
        
        # Seção de Apoio ao Desenvolvimento
        apoio_frame = ctk.CTkFrame(page)
        apoio_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            apoio_frame,
            text="💝 Apoiar o Desenvolvimento",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            apoio_frame,
            text="Gosta da aplicação? Ajude-nos a continuar o desenvolvimento!",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 10))
        
        # Botão de doação PayPal
        ctk.CTkButton(
            apoio_frame,
            text="💳 Fazer Doação via PayPal",
            command=self.abrir_link_doacao,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#0070ba",
            hover_color="#005ea6"
        ).pack(pady=10)
        
        # Botão de Salvar Configurações Geral
        save_config_frame = ctk.CTkFrame(page)
        save_config_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            save_config_frame,
            text="💾 Salvar Todas as Configurações",
            command=self.salvar_todas_configuracoes,
            width=300,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(pady=20)
    
    def abrir_ficheiro_sobre(self):
        """Abrir ficheiro Sobre.txt com informações completas"""
        import os
        import subprocess
        try:
            ficheiro_sobre = os.path.join(os.path.dirname(__file__), "Sobre.txt")
            if os.path.exists(ficheiro_sobre):
                # Tentar abrir com o programa padrão do sistema
                if os.name == 'nt':  # Windows
                    os.startfile(ficheiro_sobre)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.call(['xdg-open', ficheiro_sobre])
                messagebox.showinfo(
                    "Sobre", 
                    "Ficheiro de informações aberto com sucesso!"
                )
            else:
                messagebox.showerror(
                    "Erro", 
                    "Ficheiro Sobre.txt não encontrado!"
                )
        except Exception as e:
            messagebox.showerror(
                "Erro", 
                f"Erro ao abrir ficheiro: {e}"
            )
    
    def abrir_link_doacao(self):
        """Abrir link de doação PayPal no navegador"""
        import webbrowser
        try:
            webbrowser.open("https://www.paypal.com/donate?hosted_button_id=FKX6MYMC62CYA")
            messagebox.showinfo(
                "Obrigado!", 
                "Obrigado pelo seu apoio!\nO link de doação foi aberto no seu navegador."
            )
        except Exception as e:
            messagebox.showerror(
                "Erro", 
                f"Erro ao abrir link de doação: {e}\n\nLink: https://www.paypal.com/donate?hosted_button_id=FKX6MYMC62CYA"
            )
    
    def salvar_saldo_inicial(self):
        """Salvar saldo inicial"""
        try:
            saldo = float(self.saldo_inicial_entry.get())
            if saldo < 0:
                messagebox.showerror("Erro", "O saldo inicial deve ser positivo.")
                return
            
            # Confirmar alteração
            if messagebox.askyesno(t("confirmacao"), 
                                 f"Tem certeza que deseja alterar o saldo inicial para €{saldo:.2f}?\n\n"
                                 f"{t('atencao')}: {t('afetar_calculos')}"):
                
                self.db.set_configuracao("saldo_inicial", str(saldo))
                self.update_dashboard()
                messagebox.showinfo(t("sucesso"), "Saldo inicial salvo com sucesso!")
            
        except ValueError:
            messagebox.showerror(t("erro"), t("valor_numerico"))
    
    def _aplicar_configuracoes_iniciais(self):
        """Aplica configurações salvas de tema e idioma."""
        try:
            # Aplicar tema salvo
            tema_atual = self.gestor_temas.obter_tema_atual()
            if tema_atual:
                self.gestor_temas.aplicar_tema(tema_atual.nome)
            
            # Aplicar idioma salvo
            idioma_atual = self.gestor_traducoes.obter_idioma_atual()
            if idioma_atual:
                self.gestor_traducoes.definir_idioma(idioma_atual)
                
                # Atualizar combo box do idioma se existir
                if hasattr(self, 'idioma_combo'):
                    mapa_idiomas_reverso = {
                        Idioma.PORTUGUES: "Português",
                        Idioma.INGLES: "English",
                        Idioma.ESPANHOL: "Español"
                    }
                    nome_idioma = mapa_idiomas_reverso.get(idioma_atual, "Português")
                    self.idioma_combo.set(nome_idioma)
                
        except Exception as e:
            print(f"Erro ao aplicar configurações iniciais: {e}")
    
    def create_relatorios_page(self):
        """Criar página de relatórios."""
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["relatorios"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text=f"📄 {t('relatorios')}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame para tipos de relatório
        tipos_frame = ctk.CTkFrame(page)
        tipos_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            tipos_frame,
            text=f"📊 {t('gerar_relatorio')}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Botões para diferentes tipos de relatório
        botoes_frame = ctk.CTkFrame(tipos_frame)
        botoes_frame.pack(pady=10)
        
        ctk.CTkButton(
            botoes_frame,
            text=f"📅 {t('relatorio_mensal')}",
            command=self.gerar_relatorio_mensal,
            width=200,
            height=40
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            botoes_frame,
            text=f"📆 {t('relatorio_anual')}",
            command=self.gerar_relatorio_anual,
            width=200,
            height=40
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            botoes_frame,
            text=f"🎯 {t('relatorio_personalizado')}",
            command=self.gerar_relatorio_personalizado,
            width=200,
            height=40
        ).pack(side="left", padx=10)
        
        # Frame para configurações de relatório
        config_frame = ctk.CTkFrame(page)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            config_frame,
            text="⚙️ Configurações do Relatório",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Período personalizado
        periodo_frame = ctk.CTkFrame(config_frame)
        periodo_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(periodo_frame, text=f"{t('data_inicio')}:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.data_inicio_entry = ctk.CTkEntry(periodo_frame, placeholder_text="DD/MM/AAAA")
        self.data_inicio_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(periodo_frame, text=f"{t('data_fim')}:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.data_fim_entry = ctk.CTkEntry(periodo_frame, placeholder_text="DD/MM/AAAA")
        self.data_fim_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # Opções de conteúdo
        opcoes_frame = ctk.CTkFrame(config_frame)
        opcoes_frame.pack(fill="x", padx=20, pady=10)
        
        self.incluir_graficos = ctk.CTkCheckBox(opcoes_frame, text="Incluir Gráficos")
        self.incluir_graficos.pack(side="left", padx=10, pady=5)
        self.incluir_graficos.select()
        
        self.incluir_analise = ctk.CTkCheckBox(opcoes_frame, text=t("incluir_analise_detalhada"))
        self.incluir_analise.pack(side="left", padx=10, pady=5)
        self.incluir_analise.select()
        
        self.incluir_recomendacoes = ctk.CTkCheckBox(opcoes_frame, text=t("incluir_recomendacoes"))
        self.incluir_recomendacoes.pack(side="left", padx=10, pady=5)
        self.incluir_recomendacoes.select()
    
    def gerar_relatorio_mensal(self):
        """Gerar relatório mensal."""
        try:
            from datetime import datetime, timedelta
            
            # Período do mês atual
            hoje = datetime.now()
            inicio_mes = hoje.replace(day=1)
            
            # Gerar relatório
            caminho = self.gerador_relatorios.gerar_relatorio_completo(
                data_inicio=inicio_mes,
                data_fim=hoje,
                incluir_graficos=True,
                incluir_analise=True,
                incluir_recomendacoes=True
            )
            
            if caminho:
                messagebox.showinfo(t('sucesso'), f"Relatório mensal gerado com sucesso!\nSalvo em: {caminho}")
                # Abrir arquivo
                os.startfile(caminho)
            else:
                messagebox.showwarning(t("aviso"), f"{t('sem_dados_relatorio')}\n{t('adicione_apostas')}")
                
        except Exception as e:
            messagebox.showerror(t('erro'), f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_anual(self):
        """Gerar relatório anual."""
        try:
            from datetime import datetime, timedelta
            
            # Período do ano atual
            hoje = datetime.now()
            inicio_ano = hoje.replace(month=1, day=1)
            
            # Gerar relatório
            caminho = self.gerador_relatorios.gerar_relatorio_completo(
                data_inicio=inicio_ano,
                data_fim=hoje,
                incluir_graficos=True,
                incluir_analise=True,
                incluir_recomendacoes=True
            )
            
            if caminho:
                messagebox.showinfo(t('sucesso'), f"Relatório anual gerado com sucesso!\nSalvo em: {caminho}")
                # Abrir arquivo
                os.startfile(caminho)
            else:
                messagebox.showwarning(t("aviso"), f"{t('sem_dados_relatorio')}\n{t('adicione_apostas')}")
                
        except Exception as e:
            messagebox.showerror(t('erro'), f"Erro ao gerar relatório: {str(e)}")
    
    def gerar_relatorio_personalizado(self):
        """Gerar relatório personalizado."""
        try:
            from datetime import datetime
            
            # Validar datas
            data_inicio_str = self.data_inicio_entry.get().strip()
            data_fim_str = self.data_fim_entry.get().strip()
            
            if not data_inicio_str or not data_fim_str:
                messagebox.showerror(t('erro'), t("preencha_datas"))
                return
            
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
                data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror(t('erro'), t("formato_data_invalido"))
                return
            
            if data_inicio > data_fim:
                messagebox.showerror(t('erro'), t("data_inicio_anterior"))
                return
            
            # Obter opções
            incluir_graficos = self.incluir_graficos.get()
            incluir_analise = self.incluir_analise.get()
            incluir_recomendacoes = self.incluir_recomendacoes.get()
            
            # Gerar relatório
            caminho = self.gerador_relatorios.gerar_relatorio_completo(
                data_inicio=data_inicio,
                data_fim=data_fim,
                incluir_graficos=incluir_graficos,
                incluir_analise=incluir_analise,
                incluir_recomendacoes=incluir_recomendacoes
            )
            
            if caminho:
                messagebox.showinfo(t('sucesso'), f"Relatório personalizado gerado com sucesso!\nSalvo em: {caminho}")
                # Abrir arquivo
                os.startfile(caminho)
            else:
                messagebox.showwarning(t("aviso"), f"{t('sem_dados_periodo')}\n{t('tente_periodo_diferente')}")
                
        except Exception as e:
            messagebox.showerror(t('erro'), f"Erro ao gerar relatório: {str(e)}")
    
    def alterar_tema(self, tema):
        """Altera o tema da aplicação (método legado)"""
        try:
            ctk.set_appearance_mode(tema)
            self.salvar_configuracoes()
        except Exception as e:
            print(f"Erro ao alterar tema: {e}")
    
    def alterar_tema_avancado(self, nome_tema):
        """Altera o tema usando o gestor avançado"""
        try:
            self.gestor_temas.aplicar_tema_por_nome(nome_tema)
            self.salvar_configuracoes()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo(
                "Tema Alterado",
                f"Tema '{nome_tema}' aplicado com sucesso!"
            )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao aplicar tema: {e}"
            )
    
    def alterar_idioma(self, idioma_selecionado):
        """Altera o idioma da aplicação"""
        try:
            # Mapear idiomas para objetos Idioma
            mapa_idiomas = {
                "Português": Idioma.PORTUGUES,
                "English": Idioma.INGLES,
                "Español": Idioma.ESPANHOL
            }
            
            idioma_obj = mapa_idiomas.get(idioma_selecionado, Idioma.PORTUGUES)
            self.gestor_traducoes.definir_idioma(idioma_obj)
            
            # Salvar configuração
            self.salvar_configuracoes()
            
        except Exception as e:
            messagebox.showerror(
                t("erro"),
                f"{t('erro_alterar_idioma')}: {e}"
            )
    
    def abrir_editor_temas(self):
        """Abre o editor de temas personalizado"""
        try:
            from temas import EditorTemas
            editor = EditorTemas(self, self.gestor_temas)
            editor.mainloop()
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir editor de temas: {e}"
            )
    
    def configurar_criptografia(self):
        """Configura a criptografia de dados"""
        try:
            from tkinter import simpledialog
            
            # Verificar se já existe configuração
            if self.gestor_seguranca.verificar_configuracao():
                resposta = messagebox.askyesno(
                    "Criptografia",
                    "Criptografia já configurada. Deseja reconfigurar?"
                )
                if not resposta:
                    return
            
            # Solicitar senha mestra
            senha = simpledialog.askstring(
                "Configurar Criptografia",
                "Digite uma senha mestra para criptografia:",
                show='*'
            )
            
            if senha:
                self.gestor_seguranca.inicializar_sistema_seguranca(senha)
                messagebox.showinfo(
                    "Sucesso",
                    "Criptografia configurada com sucesso!"
                )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao configurar criptografia: {e}"
            )
    
    def criar_backup_seguro(self):
        """Cria um backup seguro com criptografia"""
        try:
            if not self.gestor_seguranca.verificar_configuracao():
                messagebox.showwarning(
                    "Aviso",
                    "Configure a criptografia primeiro!"
                )
                return
            
            # Solicitar localização do backup
            pasta_backup = filedialog.askdirectory(
                title="Selecione a pasta para o backup seguro"
            )
            
            if pasta_backup:
                arquivo_backup = self.gestor_seguranca.criar_backup_seguro(
                    pasta_backup
                )
                messagebox.showinfo(
                    "Backup Criado",
                    f"Backup seguro criado em:\n{arquivo_backup}"
                )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao criar backup seguro: {e}"
            )
    
    def configurar_autenticacao(self):
        """Configura sistema de autenticação"""
        try:
            # Criar janela de configuração de autenticação
            auth_window = ctk.CTkToplevel(self.root)
            auth_window.title("Configurar Autenticação")
            auth_window.geometry("400x300")
            auth_window.transient(self.root)
            auth_window.grab_set()
            
            # Centralizar janela
            auth_window.update_idletasks()
            x = (auth_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (auth_window.winfo_screenheight() // 2) - (300 // 2)
            auth_window.geometry(f"400x300+{x}+{y}")
            
            # Título
            ctk.CTkLabel(
                auth_window,
                text="🔑 Configurar Autenticação",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=20)
            
            # Campos de entrada
            ctk.CTkLabel(
                auth_window,
                text="Nome de usuário:"
            ).pack(pady=5)
            
            entry_usuario = ctk.CTkEntry(
                auth_window,
                width=300,
                placeholder_text="Digite o nome de usuário"
            )
            entry_usuario.pack(pady=5)
            
            ctk.CTkLabel(
                auth_window,
                text="Senha:"
            ).pack(pady=5)
            
            entry_senha = ctk.CTkEntry(
                auth_window,
                width=300,
                placeholder_text="Digite a senha",
                show="*"
            )
            entry_senha.pack(pady=5)
            
            ctk.CTkLabel(
                auth_window,
                text="Confirmar senha:"
            ).pack(pady=5)
            
            entry_confirmar = ctk.CTkEntry(
                auth_window,
                width=300,
                placeholder_text="Confirme a senha",
                show="*"
            )
            entry_confirmar.pack(pady=5)
            
            def salvar_autenticacao():
                usuario = entry_usuario.get().strip()
                senha = entry_senha.get()
                confirmar = entry_confirmar.get()
                
                if not usuario or not senha:
                    messagebox.showerror(t("erro"), t("preencha_campos"))
                    return
                
                if senha != confirmar:
                    messagebox.showerror(t("erro"), "Senhas não coincidem!")
                    return
                
                try:
                    self.gestor_seguranca.configurar_autenticacao(usuario, senha)
                    messagebox.showinfo(t("sucesso"), "Autenticação configurada!")
                    auth_window.destroy()
                except Exception as e:
                    messagebox.showerror(t("erro"), f"Erro ao configurar: {e}")
            
            # Botões
            botoes_frame = ctk.CTkFrame(auth_window)
            botoes_frame.pack(pady=20)
            
            ctk.CTkButton(
                botoes_frame,
                text="Salvar",
                command=salvar_autenticacao,
                width=120
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                botoes_frame,
                text="Cancelar",
                command=auth_window.destroy,
                width=120
            ).pack(side="left", padx=10)
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao configurar autenticação: {e}"
            )
    
    def salvar_configuracoes(self):
        """Salva as configurações da aplicação"""
        try:
            config = {
                'tema_atual': self.gestor_temas.obter_tema_atual().nome if self.gestor_temas.obter_tema_atual() else 'Claro Padrão',
                'idioma_atual': self.gestor_traducoes.obter_idioma_atual().value
            }
            
            config_path = Path('config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def salvar_todas_configuracoes(self):
        """Salva todas as configurações selecionadas na interface"""
        try:
            # Salvar tema selecionado
            tema_selecionado = self.tema_combo.get()
            if tema_selecionado:
                self.gestor_temas.aplicar_tema(tema_selecionado)
                self.gestor_temas._salvar_configuracoes()
            
            # Salvar idioma selecionado
            idioma_selecionado = self.idioma_combo.get()
            if idioma_selecionado:
                mapa_idiomas = {
                    "Português": Idioma.PORTUGUES,
                    "English": Idioma.INGLES,
                    "Español": Idioma.ESPANHOL
                }
                idioma_obj = mapa_idiomas.get(idioma_selecionado, Idioma.PORTUGUES)
                self.gestor_traducoes.definir_idioma(idioma_obj)
                self.gestor_traducoes._salvar_configuracoes()
            
            # Salvar configurações gerais
            self.salvar_configuracoes()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo(
                "Configurações Salvas",
                "Todas as configurações foram salvas com sucesso!\n\n"
                "Algumas alterações podem requerer reinicialização da aplicação."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao salvar configurações: {e}"
            )
    
    def create_simulador_estrategias_page(self):
        """Criar página do simulador de estratégias"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["simulador_estrategias"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="🤖 Simulador de Estratégias",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(page)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame de controles
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Seleção de estratégia
        strategy_label = ctk.CTkLabel(controls_frame, text="Estratégia:")
        strategy_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.strategy_var = ctk.StringVar(value="flat")
        strategy_combo = ctk.CTkComboBox(
            controls_frame,
            values=["flat", "kelly", "percentage", "martingale", "fibonacci"],
            variable=self.strategy_var
        )
        strategy_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Valor inicial
        initial_label = ctk.CTkLabel(controls_frame, text="Valor Inicial (€):")
        initial_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.initial_value_var = ctk.StringVar(value="100")
        initial_entry = ctk.CTkEntry(controls_frame, textvariable=self.initial_value_var)
        initial_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # Botão simular
        simulate_btn = ctk.CTkButton(
            controls_frame,
            text="Simular",
            command=self.simular_estrategia
        )
        simulate_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Frame para resultados
        self.results_frame = ctk.CTkFrame(main_frame)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_detecao_padroes_page(self):
        """Criar página de deteção de padrões"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["detecao_padroes"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="🧠 Deteção de Padrões com IA",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(page)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame de controles
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Tipo de análise
        analysis_label = ctk.CTkLabel(controls_frame, text="Tipo de Análise:")
        analysis_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.analysis_var = ctk.StringVar(value="day")
        analysis_combo = ctk.CTkComboBox(
            controls_frame,
            values=["day", "odds", "competition", "bet_type", "combinations"],
            variable=self.analysis_var
        )
        analysis_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Botão analisar
        analyze_btn = ctk.CTkButton(
            controls_frame,
            text="Analisar Padrões",
            command=self.analisar_padroes
        )
        analyze_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Botão treinar modelo
        train_btn = ctk.CTkButton(
            controls_frame,
            text="Treinar Modelo IA",
            command=self.treinar_modelo
        )
        train_btn.grid(row=0, column=3, padx=10, pady=5)
        
        # Frame para resultados
        self.patterns_frame = ctk.CTkFrame(main_frame)
        self.patterns_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_tipster_tracker_page(self):
        """Criar página do tipster tracker"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["tipster_tracker"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="👥 Tipster Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(page)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame de controles
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Adicionar tipster
        tipster_label = ctk.CTkLabel(controls_frame, text="Nome do Tipster:")
        tipster_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.tipster_name_var = ctk.StringVar()
        tipster_entry = ctk.CTkEntry(controls_frame, textvariable=self.tipster_name_var)
        tipster_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Botão adicionar
        add_btn = ctk.CTkButton(
            controls_frame,
            text="Adicionar Tipster",
            command=self.adicionar_tipster
        )
        add_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Botão estatísticas
        stats_btn = ctk.CTkButton(
            controls_frame,
            text="Ver Estatísticas",
            command=self.ver_estatisticas_tipster
        )
        stats_btn.grid(row=0, column=3, padx=10, pady=5)
        
        # Botão ranking
        ranking_btn = ctk.CTkButton(
            controls_frame,
            text="Ranking",
            command=self.ver_ranking_tipsters
        )
        ranking_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Frame para resultados
        self.tipster_frame = ctk.CTkFrame(main_frame)
        self.tipster_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_comportamento_risco_page(self):
        """Criar página de análise de comportamento de risco"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["comportamento_risco"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="⚠️ Análise de Comportamento de Risco",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(page)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame de controles
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Botão analisar
        analyze_btn = ctk.CTkButton(
            controls_frame,
            text="Analisar Comportamento",
            command=self.analisar_comportamento_risco
        )
        analyze_btn.grid(row=0, column=0, padx=10, pady=5)
        
        # Botão alertas
        alerts_btn = ctk.CTkButton(
            controls_frame,
            text="Ver Alertas",
            command=self.ver_alertas_risco
        )
        alerts_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Botão recomendações
        recommendations_btn = ctk.CTkButton(
            controls_frame,
            text="Recomendações",
            command=self.ver_recomendacoes_risco
        )
        recommendations_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Frame para resultados
        self.risk_frame = ctk.CTkFrame(main_frame)
        self.risk_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def simular_estrategia(self):
        """Simular estratégia selecionada"""
        try:
            strategy = self.strategy_var.get()
            initial_value = float(self.initial_value_var.get())
            
            # Limpar frame anterior
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Executar simulação
            results = self.strategy_simulator.run_simulation(
                strategy, 
                initial_bankroll=initial_value,
                bet_amount=initial_value * 0.02 if strategy == 'flat' else None,
                percentage=2 if strategy == 'percentage' else None,
                base_bet=initial_value * 0.01 if strategy in ['martingale', 'fibonacci'] else None
            )
            
            if results:
                # Mostrar resultados
                results_text = ctk.CTkTextbox(self.results_frame, height=400)
                results_text.pack(fill="both", expand=True, padx=10, pady=10)
                
                results_text.insert("1.0", f"Resultados da Simulação - {strategy.upper()}\n\n")
                results_text.insert("end", f"Valor Inicial: €{results.initial_bankroll:.2f}\n")
                results_text.insert("end", f"Valor Final: €{results.final_bankroll:.2f}\n")
                results_text.insert("end", f"ROI: {results.roi:.2f}%\n")
                results_text.insert("end", f"Número de Apostas: {results.total_bets}\n")
                results_text.insert("end", f"Taxa de Vitória: {results.win_rate:.2f}%\n")
                results_text.insert("end", f"Lucro Total: €{results.total_profit:.2f}\n")
                results_text.insert("end", f"Max Drawdown: {results.max_drawdown:.2f}%\n")
                results_text.insert("end", f"Sharpe Ratio: {results.sharpe_ratio:.2f}\n")
            else:
                messagebox.showwarning("Aviso", "Não foi possível executar a simulação. Verifique se há dados históricos suficientes.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na simulação: {str(e)}")
    
    def analisar_padroes(self):
        """Analisar padrões com IA"""
        try:
            analysis_type = self.analysis_var.get()
            days_back = int(self.days_var.get()) if hasattr(self, 'days_var') else 365
            
            # Limpar frame anterior
            for widget in self.patterns_frame.winfo_children():
                widget.destroy()
            
            # Carregar dados
            df = self.pattern_detector.load_data(days_back=days_back)
            
            if df.empty:
                messagebox.showwarning("Aviso", "Não há dados suficientes para análise de padrões.")
                return
            
            # Executar análise
            patterns = self.pattern_detector.detect_profitable_patterns(df, min_sample_size=5)
            
            # Mostrar resultados
            results_text = ctk.CTkTextbox(self.patterns_frame, height=400)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            results_text.insert("1.0", f"Padrões Detectados - Análise de {days_back} dias\n\n")
            
            if patterns:
                results_text.insert("end", f"Total de padrões encontrados: {len(patterns)}\n\n")
                
                for i, pattern in enumerate(patterns[:10], 1):  # Mostrar top 10
                    results_text.insert("end", f"{i}. {pattern.name}\n")
                    results_text.insert("end", f"   Descrição: {pattern.description}\n")
                    results_text.insert("end", f"   ROI Médio: {pattern.avg_roi:.2f}%\n")
                    results_text.insert("end", f"   Taxa de Acerto: {pattern.win_rate:.1f}%\n")
                    results_text.insert("end", f"   Amostra: {pattern.sample_size} apostas\n")
                    results_text.insert("end", f"   Nível de Risco: {pattern.risk_level}\n")
                    results_text.insert("end", f"   Confiança: {pattern.confidence:.2f}\n")
                    results_text.insert("end", "-" * 50 + "\n\n")
            else:
                results_text.insert("end", "Nenhum padrão lucrativo significativo foi detectado no período analisado.\n")
                results_text.insert("end", "Tente aumentar o período de análise ou verificar se há dados suficientes.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na análise: {str(e)}")
    
    def treinar_modelo(self):
        """Treinar modelo de IA"""
        try:
            # Carregar dados para treino
            df = self.pattern_detector.load_data(days_back=730)  # 2 anos de dados
            
            if df.empty:
                messagebox.showwarning("Aviso", "Não há dados suficientes para treinar o modelo.")
                return
            
            # Treinar modelo diretamente com o DataFrame
            result = self.pattern_detector.train_prediction_model(df)
            
            if 'error' in result:
                messagebox.showerror("Erro", f"Erro no treino: {result['error']}")
            else:
                accuracy = result['metrics']['accuracy'] * 100  # Converter para percentagem
                messagebox.showinfo(
                    "Sucesso", 
                    f"Modelo treinado com sucesso!\nPrecisão: {accuracy:.1f}%\nAmostras de treino: {result['training_samples']}"
                )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no treino: {str(e)}")
    
    def adicionar_tipster(self):
        """Adicionar novo tipster"""
        try:
            name = self.tipster_name_var.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Por favor, insira o nome do tipster.")
                return
            
            self.tipster_tracker.add_tipster(name)
            self.tipster_name_var.set("")
            
            messagebox.showinfo("Sucesso", f"Tipster '{name}' adicionado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar tipster: {str(e)}")
    
    def ver_estatisticas_tipster(self):
        """Ver estatísticas dos tipsters"""
        try:
            # Limpar frame anterior
            for widget in self.tipster_frame.winfo_children():
                widget.destroy()
            
            # Obter estatísticas
            stats = self.tipster_tracker.get_detailed_stats()
            
            # Mostrar resultados
            results_text = ctk.CTkTextbox(self.tipster_frame, height=400)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            results_text.insert("1.0", "Estatísticas dos Tipsters\n\n")
            
            for tipster, data in stats.items():
                results_text.insert("end", f"Tipster: {tipster}\n")
                results_text.insert("end", f"ROI: {data.get('roi', 0):.2f}%\n")
                results_text.insert("end", f"Taxa de Vitória: {data.get('win_rate', 0):.2f}%\n")
                results_text.insert("end", f"Lucro Total: €{data.get('total_profit', 0):.2f}\n")
                results_text.insert("end", f"Número de Apostas: {data.get('num_bets', 0)}\n")
                results_text.insert("end", "-" * 40 + "\n")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter estatísticas: {str(e)}")
    
    def ver_ranking_tipsters(self):
        """Ver ranking dos tipsters"""
        try:
            # Limpar frame anterior
            for widget in self.tipster_frame.winfo_children():
                widget.destroy()
            
            # Obter ranking
            ranking = self.tipster_tracker.generate_ranking()
            
            # Mostrar resultados
            results_text = ctk.CTkTextbox(self.tipster_frame, height=400)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            if not ranking:
                results_text.insert("1.0", "Nenhum tipster encontrado com dados suficientes.\n")
                return
            
            results_text.insert("1.0", "🏆 RANKING DOS TIPSTERS\n\n")
            
            for entry in ranking:
                posicao = entry['posicao']
                tipster = entry['tipster']
                roi = entry['roi']
                win_rate = entry['win_rate']
                total_tips = entry['total_tips']
                profit = entry['profit']
                risk_level = entry['risk_level']
                
                results_text.insert("end", f"{posicao}º - {tipster}\n")
                results_text.insert("end", f"   📊 ROI: {roi:.1f}% | Win Rate: {win_rate:.1f}%\n")
                results_text.insert("end", f"   💰 Lucro: {profit:.2f}€ | Tips: {total_tips} | Risco: {risk_level}\n\n")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter ranking: {str(e)}")
    
    def analisar_comportamento_risco(self):
        """Analisar comportamento de risco"""
        try:
            # Limpar frame anterior
            for widget in self.risk_frame.winfo_children():
                widget.destroy()
            
            # Executar análise - desempacotar a tupla retornada
            metrics, alerts = self.risk_analyzer_v2.analyze_risk_behavior()
            
            # Mostrar resultados
            results_text = ctk.CTkTextbox(self.risk_frame, height=400)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            results_text.insert("1.0", "Análise de Comportamento de Risco\n\n")
            results_text.insert("end", f"Nível de Risco: {metrics.risk_level.value}\n")
            results_text.insert("end", f"Sequência Atual de Perdas: {metrics.current_losing_streak}\n")
            results_text.insert("end", f"Maior Sequência de Perdas: {metrics.max_losing_streak}\n")
            results_text.insert("end", f"Apostas Impulsivas: {metrics.impulsive_bets_count}\n")
            results_text.insert("end", f"Score de Risco Geral: {metrics.overall_risk_score:.2f}/10\n")
            results_text.insert("end", f"Score Emocional: {metrics.emotional_betting_score:.2f}/10\n")
            results_text.insert("end", f"Score de Disciplina: {metrics.discipline_score:.2f}/10\n")
            
            if alerts:
                results_text.insert("end", f"\n=== ALERTAS ATIVOS ({len(alerts)}) ===\n")
                for alert in alerts:
                    results_text.insert("end", f"🚨 {alert.type.value} - {alert.level.value}\n")
                    results_text.insert("end", f"   {alert.message}\n")
                    results_text.insert("end", f"   Recomendação: {alert.recommendation}\n\n")
            else:
                results_text.insert("end", "\n✅ Nenhum alerta de risco ativo\n")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na análise: {str(e)}")
    
    def ver_alertas_risco(self):
        """Ver alertas de risco"""
        try:
            # Limpar frame anterior
            for widget in self.risk_frame.winfo_children():
                widget.destroy()
            
            # Obter alertas
            alerts = self.risk_analyzer_v2.get_risk_alerts()
            
            # Mostrar resultados
            results_text = ctk.CTkTextbox(self.risk_frame, height=400)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            results_text.insert("1.0", "Alertas de Risco\n\n")
            
            for alert in alerts:
                results_text.insert("end", f"⚠️ {alert.get('message', 'N/A')}\n")
                results_text.insert("end", f"Severidade: {alert.get('severity', 'N/A')}\n")
                results_text.insert("end", f"Data: {alert.get('date', 'N/A')}\n")
                results_text.insert("end", "-" * 40 + "\n")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter alertas: {str(e)}")
    
    def ver_recomendacoes_risco(self):
        """Ver recomendações de risco"""
        try:
            # Limpar frame anterior
            for widget in self.risk_frame.winfo_children():
                widget.destroy()
            
            # Obter recomendações
            recommendations = self.risk_analyzer_v2.get_recommendations()
            
            # Mostrar resultados
            results_text = ctk.CTkTextbox(self.risk_frame, height=400)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            results_text.insert("1.0", "Recomendações de Gestão de Risco\n\n")
            
            for rec in recommendations:
                results_text.insert("end", f"💡 {rec}\n\n")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter recomendações: {str(e)}")
    
    # ==================== MÉTODOS DE MACHINE LEARNING ====================
    
    def treinar_modelo_ml(self):
        """Treinar modelo de Machine Learning"""
        # Desabilitar botão durante treinamento
        self.btn_treinar.configure(state="disabled", text="🔄 Treinando...")
        
        # Limpar frame de resultados
        for widget in self.ml_results_frame.winfo_children():
            widget.destroy()
        
        # Mostrar status de treinamento com progresso
        self.status_label = ctk.CTkLabel(
            self.ml_results_frame,
            text="🔄 Iniciando treinamento do modelo...",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=20)
        
        # Adicionar barra de progresso visual
        self.progress_label = ctk.CTkLabel(
            self.ml_results_frame,
            text="⏳ Isso pode levar alguns minutos. Por favor, aguarde...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.progress_label.pack(pady=5)
        
        # Executar treinamento em thread separada
        thread = threading.Thread(target=self._executar_treinamento_ml, daemon=True)
        thread.start()
        
        # Iniciar animação de progresso
        self._animar_progresso()
    
    def _executar_treinamento_ml(self):
        """Executar treinamento em thread separada"""
        try:
            # Usar o gestor ML rápido se disponível, senão usar o normal
            if hasattr(self, 'gestor_ml_rapido') and self.gestor_ml_rapido:
                resultado = self.gestor_ml_rapido.treinar_modelo_rapido()
            elif self.gestor_ml:
                resultado = self.gestor_ml.treinar_modelo()
            else:
                resultado = {'sucesso': False, 'erro': 'Nenhum gestor ML disponível'}
            
            # Atualizar interface na thread principal
            self.root.after(0, self._finalizar_treinamento_ml, resultado)
            
        except Exception as e:
            # Atualizar interface com erro na thread principal
            self.root.after(0, self._finalizar_treinamento_ml, {'sucesso': False, 'erro': str(e)})
    
    def _animar_progresso(self):
        """Anima o progresso do treinamento"""
        if hasattr(self, 'progress_label') and self.progress_label.winfo_exists():
            current_text = self.progress_label.cget("text")
            if "⏳" in current_text:
                dots = current_text.count(".")
                if dots >= 6:
                    new_text = "⏳ Treinando"
                else:
                    new_text = current_text + "."
                self.progress_label.configure(text=new_text)
            
            # Continuar animação se o treinamento ainda estiver rodando
            self.root.after(500, self._animar_progresso)
    
    def _finalizar_treinamento_ml(self, resultado):
        """Finalizar treinamento e atualizar interface"""
        try:
            # Limpar status anterior
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.destroy()
            
            # Limpar label de progresso
            if hasattr(self, 'progress_label') and self.progress_label.winfo_exists():
                self.progress_label.destroy()
            
            if resultado['sucesso']:
                # Mostrar resultados do treinamento
                success_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text="✅ Modelo treinado com sucesso!",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="green"
                )
                success_label.pack(pady=10)
                
                # Mostrar métricas
                metricas_frame = ctk.CTkFrame(self.ml_results_frame)
                metricas_frame.pack(fill="x", padx=20, pady=10)
                
                metricas_label = ctk.CTkLabel(
                    metricas_frame,
                    text="📊 Métricas do Modelo:",
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                metricas_label.pack(pady=10)
                
                for metrica, valor in resultado.get('metricas', {}).items():
                    # Formatar valor baseado no tipo
                    if isinstance(valor, (int, float)):
                        valor_formatado = f"{valor:.4f}" if isinstance(valor, float) else str(valor)
                    elif isinstance(valor, list):
                        valor_formatado = f"{len(valor)} features"
                    else:
                        valor_formatado = str(valor)
                    
                    metrica_text = ctk.CTkLabel(
                        metricas_frame,
                        text=f"{metrica}: {valor_formatado}",
                        font=ctk.CTkFont(size=14)
                    )
                    metrica_text.pack(pady=2)
            else:
                # Mostrar erro
                error_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text=f"❌ Erro no treinamento: {resultado.get('erro', 'Erro desconhecido')}",
                    font=ctk.CTkFont(size=16),
                    text_color="red"
                )
                error_label.pack(pady=20)
                
        except Exception as e:
            # Limpar frame em caso de erro
            for widget in self.ml_results_frame.winfo_children():
                widget.destroy()
            
            error_label = ctk.CTkLabel(
                self.ml_results_frame,
                text=f"❌ Erro inesperado: {str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.pack(pady=20)
        
        finally:
            # Reabilitar botão
            self.btn_treinar.configure(state="normal", text="📊 Treinar Modelo")
    
    def fazer_previsao_ml(self):
        """Fazer previsão com Machine Learning"""
        try:
            # Limpar frame de resultados
            for widget in self.ml_results_frame.winfo_children():
                widget.destroy()
            
            # Verificar se gestor ML está disponível
            if not self.gestor_ml:
                warning_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text="❌ Sistema ML não disponível. Reinicie a aplicação.",
                    font=ctk.CTkFont(size=16),
                    text_color="red"
                )
                warning_label.pack(pady=20)
                return
            
            # Verificar se modelo está treinado
            if not hasattr(self.gestor_ml, 'modelo_ativo') or self.gestor_ml.modelo_ativo is None:
                warning_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text="⚠️ Modelo não treinado. Treine o modelo primeiro.",
                    font=ctk.CTkFont(size=16),
                    text_color="orange"
                )
                warning_label.pack(pady=20)
                return
            
            # Mostrar status de previsão
            status_label = ctk.CTkLabel(
                self.ml_results_frame,
                text="🔮 Fazendo previsão...",
                font=ctk.CTkFont(size=16)
            )
            status_label.pack(pady=20)
            
            # Atualizar interface
            self.root.update()
            
            # Fazer previsão usando GestorML com dados de exemplo
            dados_exemplo = {
                'tipo_aposta': 'Resultado Final',
                'odd': 2.5,
                'valor_apostado': 10.0,
                'categoria_evento': 'Futebol'
            }
            resultado = self.gestor_ml.fazer_previsao(dados_exemplo)
            
            # Limpar status anterior
            status_label.destroy()
            
            if resultado['sucesso']:
                # Mostrar resultados da previsão
                success_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text="✅ Previsão realizada com sucesso!",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="green"
                )
                success_label.pack(pady=10)
                
                # Mostrar previsões
                previsoes_frame = ctk.CTkFrame(self.ml_results_frame)
                previsoes_frame.pack(fill="x", padx=20, pady=10)
                
                previsoes_label = ctk.CTkLabel(
                    previsoes_frame,
                    text="🎯 Previsões:",
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                previsoes_label.pack(pady=10)
                
                # Mostrar resultado da previsão
                previsao_text = ctk.CTkLabel(
                    previsoes_frame,
                    text=f"Previsão: {resultado.get('previsao', 'N/A')} | Probabilidade de Vitória: {resultado.get('probabilidade_vitoria', 0):.2%} | Confiança: {resultado.get('confianca', 0):.2%}",
                    font=ctk.CTkFont(size=14)
                )
                previsao_text.pack(pady=2)
                
                modelo_text = ctk.CTkLabel(
                    previsoes_frame,
                    text=f"Modelo Utilizado: {resultado.get('modelo_utilizado', 'N/A')}",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                modelo_text.pack(pady=2)
            else:
                # Mostrar erro
                error_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text=f"❌ Erro na previsão: {resultado.get('erro', 'Erro desconhecido')}",
                    font=ctk.CTkFont(size=16),
                    text_color="red"
                )
                error_label.pack(pady=20)
                
        except Exception as e:
            # Limpar frame em caso de erro
            for widget in self.ml_results_frame.winfo_children():
                widget.destroy()
            
            error_label = ctk.CTkLabel(
                self.ml_results_frame,
                text=f"❌ Erro inesperado: {str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.pack(pady=20)
    
    def calcular_previsao_ml(self):
        """Calcular previsão personalizada com Machine Learning"""
        try:
            # Limpar frame de resultados
            for widget in self.ml_results_frame.winfo_children():
                widget.destroy()
            
            # Verificar se gestor ML está disponível
            if not self.gestor_ml:
                warning_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text="❌ Sistema ML não disponível. Reinicie a aplicação.",
                    font=ctk.CTkFont(size=16),
                    text_color="red"
                )
                warning_label.pack(pady=20)
                return
            
            # Verificar se modelo está treinado
            if not self.gestor_ml.modelo_ativo or self.gestor_ml.modelo_ativo not in self.gestor_ml.modelos:
                warning_label = ctk.CTkLabel(
                    self.ml_results_frame,
                    text="⚠️ Modelo não treinado. Treine o modelo primeiro.",
                    font=ctk.CTkFont(size=16),
                    text_color="orange"
                )
                warning_label.pack(pady=20)
                return
            
            # Criar formulário para entrada de dados
            form_frame = ctk.CTkFrame(self.ml_results_frame)
            form_frame.pack(fill="x", padx=20, pady=10)
            
            form_label = ctk.CTkLabel(
                form_frame,
                text="📝 Dados para Previsão Personalizada:",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            form_label.pack(pady=10)
            
            # Campos de entrada
            campos_frame = ctk.CTkFrame(form_frame)
            campos_frame.pack(fill="x", padx=20, pady=10)
            
            # Time da casa
            casa_label = ctk.CTkLabel(campos_frame, text="Time da Casa:")
            casa_label.pack(pady=5)
            casa_entry = ctk.CTkEntry(campos_frame, placeholder_text="Ex: Benfica")
            casa_entry.pack(pady=5, fill="x")
            
            # Time visitante
            visitante_label = ctk.CTkLabel(campos_frame, text="Time Visitante:")
            visitante_label.pack(pady=5)
            visitante_entry = ctk.CTkEntry(campos_frame, placeholder_text="Ex: Porto")
            visitante_entry.pack(pady=5, fill="x")
            
            # Odds
            odds_label = ctk.CTkLabel(campos_frame, text="Odds (separadas por vírgula):")
            odds_label.pack(pady=5)
            odds_entry = ctk.CTkEntry(campos_frame, placeholder_text="Ex: 2.1, 3.2, 3.8")
            odds_entry.pack(pady=5, fill="x")
            
            # Botão calcular
            def calcular():
                try:
                    casa = casa_entry.get().strip()
                    visitante = visitante_entry.get().strip()
                    odds_text = odds_entry.get().strip()
                    
                    if not casa or not visitante or not odds_text:
                        messagebox.showwarning("Aviso", "Preencha todos os campos")
                        return
                    
                    # Processar odds
                    try:
                        odds = [float(x.strip()) for x in odds_text.split(',')]
                    except:
                        messagebox.showerror("Erro", "Formato de odds inválido")
                        return
                    
                    # Fazer cálculo personalizado
                    dados_jogo = {
                        'casa': casa,
                        'visitante': visitante,
                        'odds': odds
                    }
                    
                    resultado = self.gestor_ml.calcular_previsao_personalizada(dados_jogo)
                    
                    # Mostrar resultado
                    if resultado['sucesso']:
                        resultado_frame = ctk.CTkFrame(self.ml_results_frame)
                        resultado_frame.pack(fill="x", padx=20, pady=10)
                        
                        resultado_label = ctk.CTkLabel(
                            resultado_frame,
                            text="🎯 Resultado da Previsão:",
                            font=ctk.CTkFont(size=16, weight="bold")
                        )
                        resultado_label.pack(pady=10)
                        
                        previsao = resultado['previsao']
                        resultado_text = ctk.CTkLabel(
                            resultado_frame,
                            text=f"Resultado Previsto: {previsao.get('resultado', 'N/A')}\nConfiança: {previsao.get('confianca', 0):.2%}\nProbabilidades: {previsao.get('probabilidades', {})}",
                            font=ctk.CTkFont(size=14)
                        )
                        resultado_text.pack(pady=10)
                    else:
                        messagebox.showerror("Erro", resultado.get('erro', 'Erro no cálculo'))
                        
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            
            calcular_btn = ctk.CTkButton(
                form_frame,
                text="🧮 Calcular Previsão",
                command=calcular,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            calcular_btn.pack(pady=20)
            
        except Exception as e:
            # Limpar frame em caso de erro
            for widget in self.ml_results_frame.winfo_children():
                widget.destroy()
            
            error_label = ctk.CTkLabel(
                self.ml_results_frame,
                text=f"❌ Erro inesperado: {str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.pack(pady=20)
    
    # ==================== MÉTODOS DA VERSÃO 2.0 ====================
    
    def verificar_modo_multiutilizador(self):
        """Verificar se o modo multiutilizador está ativo"""
        try:
            config_path = Path("configuracoes.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('modo_multiutilizador', False)
            return False
        except:
            return False
    
    def mostrar_login_prioritario(self):
        """Mostrar janela de login como prioridade antes da interface principal"""
        try:
            # Criar janela de login modal
            janela_login = JanelaLogin(self.root, self.on_login_sucesso_prioritario)
            print("🔐 Sistema de login ativo - autenticação obrigatória")
            print("👤 Utilizador padrão: admin | Password: 17014601")
        except Exception as e:
            print(f"Erro ao mostrar login: {e}")
            messagebox.showerror("Erro", f"Erro no sistema de login: {e}")
            self.root.destroy()
    
    def mostrar_login(self):
        """Mostrar janela de login (método original para compatibilidade)"""
        try:
            self.gestor_autenticacao = GestorAutenticacao()
            janela_login = JanelaLogin(self.root, self.on_login_sucesso)
            # A janela já é mostrada automaticamente no __init__
        except Exception as e:
            print(f"Erro ao mostrar login: {e}")
            # Continuar em modo compatibilidade
            self.utilizador_id = 1
    
    def on_login_sucesso_prioritario(self, utilizador_id, utilizador_nome):
        """Callback para login bem-sucedido no modo prioritário"""
        self.utilizador_id = utilizador_id
        self.utilizador_atual = utilizador_nome
        print(f"✅ Login realizado: {utilizador_nome} (ID: {utilizador_id})")
        
        # Criar interface completa após login bem-sucedido
        self._criar_interface_completa()
        
        # Mostrar janela principal após criar interface
        self.root.deiconify()
        self.root.title(f"Sistema de Apostas Desportivas v2.0 - {utilizador_nome}")
        
        # Widget de gamificação removido
    
    def on_login_sucesso(self, utilizador_id, utilizador_nome):
        """Callback para login bem-sucedido (método original)"""
        self.utilizador_id = utilizador_id
        self.utilizador_atual = utilizador_nome
        print(f"✅ Login realizado: {utilizador_nome} (ID: {utilizador_id})")
        
        # Atualizar interface com dados do utilizador
        if hasattr(self, 'root') and self.root:
            self.root.title(f"Sistema de Apostas Desportivas v2.0 - {utilizador_nome}")
    
    # Função de gamificação removida
    
    # Página de gamificação removida
    
    def create_usuarios_page(self):
        """Criar página de gestão de utilizadores"""
        if not VERSAO_2_DISPONIVEL:
            return
            
        frame = ctk.CTkFrame(self.main_frame)
        
        # Título
        titulo = ctk.CTkLabel(frame, text="👥 Gestão de Utilizadores", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        titulo.pack(pady=20)
        
        # Verificar permissões
        if self.utilizador_atual and gestor_utilizadores.verificar_permissao(self.utilizador_id, PermissaoSistema.GERIR_UTILIZADORES):
            # Interface de administração
            self.criar_interface_admin_utilizadores(frame)
        else:
            # Interface de utilizador normal
            self.criar_interface_utilizador_normal(frame)
        
        self.pages["usuarios"] = frame
    
    def create_ml_previsoes_page(self):
        """Criar página de previsões com Machine Learning"""
        # Frame principal
        ml_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["ml_previsoes"] = ml_frame
        
        # Título
        title_label = ctk.CTkLabel(
            ml_frame, 
            text="🤖 Previsões com Machine Learning",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Frame de controles
        controls_frame = ctk.CTkFrame(ml_frame)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Botões principais
        buttons_frame = ctk.CTkFrame(controls_frame)
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        # Botão Treinar Modelo
        self.btn_treinar = ctk.CTkButton(
            buttons_frame,
            text="📊 Treinar Modelo",
            command=self.treinar_modelo_ml,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.btn_treinar.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Botão Fazer Previsão
        self.btn_prever = ctk.CTkButton(
            buttons_frame,
            text="🔮 Fazer Previsão",
            command=self.fazer_previsao_ml,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.btn_prever.pack(side="left", padx=10, fill="x", expand=True)
        
        # Botão Calcular Previsão
        self.btn_calcular = ctk.CTkButton(
            buttons_frame,
            text="📈 Calcular Previsão",
            command=self.calcular_previsao_ml,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.btn_calcular.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Frame de resultados
        self.ml_results_frame = ctk.CTkFrame(ml_frame)
        self.ml_results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Label de status inicial
        self.ml_status_label = ctk.CTkLabel(
            self.ml_results_frame,
            text="Selecione uma opção acima para começar",
            font=ctk.CTkFont(size=16)
        )
        self.ml_status_label.pack(pady=50)
    
    def criar_interface_admin_utilizadores(self, parent):
        """Criar interface de administração de utilizadores"""
        # Lista de utilizadores
        lista_frame = ctk.CTkFrame(parent)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Implementar lista e gestão de utilizadores
        info_label = ctk.CTkLabel(lista_frame, text="Interface de administração em desenvolvimento")
        info_label.pack(pady=20)
    
    def criar_interface_utilizador_normal(self, parent):
        """Criar interface para utilizador normal"""
        # Perfil do utilizador
        perfil_frame = ctk.CTkFrame(parent)
        perfil_frame.pack(fill="x", padx=20, pady=10)
        
        # Implementar perfil do utilizador
        info_label = ctk.CTkLabel(perfil_frame, text="Perfil do utilizador em desenvolvimento")
        info_label.pack(pady=20)
    
    # Função criar_interface_ml removida conforme solicitado
    
    # Funções de Machine Learning removidas conforme solicitado

if __name__ == "__main__":
    app = ApostasApp()
    app.run()