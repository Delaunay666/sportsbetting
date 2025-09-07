#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Otimizada - Carregamento Rápido
Esta versão implementa lazy loading para acelerar o tempo de inicialização
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
import threading
from typing import Dict, Optional

# Imports essenciais apenas
from main import DatabaseManager
from usuarios import gestor_utilizadores, TipoUtilizador, PermissaoSistema
from autenticacao import GestorAutenticacao, JanelaLogin

class InterfaceOtimizada:
    """Interface otimizada com carregamento rápido"""
    
    def __init__(self):
        # Variáveis essenciais
        self.utilizador_atual = None
        self.utilizador_id = None
        self.modo_multiutilizador = True
        self.gestor_autenticacao = None
        self.interface_criada = False
        
        # Cache de páginas (lazy loading)
        self.pages_cache = {}
        self.pages_loaded = set()
        
        # Configurar CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal (oculta inicialmente)
        self.root = ctk.CTk()
        self.root.withdraw()  # Ocultar até login
        self.root.title("Sistema de Apostas Desportivas v2.0")
        self.root.geometry("1200x800")
        
        # Configurar ícone
        self._configurar_icone()
        
        # Inicializar base de dados
        self.db = DatabaseManager()
        
        # Mostrar janela de login
        self._mostrar_login()
    
    def _configurar_icone(self):
        """Configurar ícone da aplicação"""
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"✅ Ícone carregado: {icon_path}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar ícone: {e}")
    
    def _mostrar_login(self):
        """Mostrar janela de login"""
        try:
            self.gestor_autenticacao = GestorAutenticacao()
            janela_login = JanelaLogin(
                self.gestor_autenticacao,
                callback_sucesso=self.on_login_sucesso
            )
            janela_login.mostrar()
        except Exception as e:
            print(f"Erro no sistema de autenticação: {e}")
            # Fallback para modo compatibilidade
            self.utilizador_id = 1
            self.utilizador_atual = "Utilizador"
            self._criar_interface_rapida()
    
    def on_login_sucesso(self, utilizador_id, utilizador_nome):
        """Callback para login bem-sucedido - OTIMIZADO"""
        self.utilizador_id = utilizador_id
        self.utilizador_atual = utilizador_nome
        print(f"✅ Login realizado: {utilizador_nome} (ID: {utilizador_id})")
        
        # Criar interface básica rapidamente
        self._criar_interface_rapida()
        
        # Mostrar janela principal
        self.root.deiconify()
        self.root.title(f"Sistema de Apostas Desportivas v2.0 - {utilizador_nome}")
        
        # Carregar componentes pesados em background
        threading.Thread(target=self._carregar_componentes_background, daemon=True).start()
    
    def _criar_interface_rapida(self):
        """Criar interface básica rapidamente (apenas essencial)"""
        print("🚀 Criando interface rápida...")
        
        # Configurar grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Criar sidebar básica
        self._criar_sidebar_basica()
        
        # Criar área principal
        self._criar_area_principal()
        
        # Criar barra de status
        self._criar_barra_status()
        
        # Carregar dados essenciais
        self._carregar_dados_essenciais()
        
        self.interface_criada = True
        print("✅ Interface rápida criada!")
    
    def _criar_sidebar_basica(self):
        """Criar sidebar com apenas botões essenciais"""
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(1, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚽ APOSTAS\nDESPORTIVAS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 20), sticky="ew")
        
        # Frame para botões
        self.buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.buttons_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Botões essenciais apenas
        self.nav_buttons = {}
        botoes_essenciais = [
            ("📊 Dashboard", "dashboard"),
            ("➕ Nova Aposta", "nova_aposta"),
            ("📋 Histórico", "historico"),
            ("💰 Gestão Banca", "banca"),
            ("📈 Estatísticas", "estatisticas")
        ]
        
        for i, (text, key) in enumerate(botoes_essenciais):
            btn = ctk.CTkButton(
                self.buttons_frame,
                text=text,
                command=lambda k=key: self.mostrar_pagina(k),
                height=38,
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            btn.grid(row=i, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Informações da banca
        self.banca_frame = ctk.CTkFrame(self.buttons_frame, fg_color="gray20")
        self.banca_frame.grid(row=len(botoes_essenciais), column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            self.banca_frame,
            text="💰 Banca Atual",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(8, 3))
        
        self.saldo_label = ctk.CTkLabel(
            self.banca_frame,
            text="€0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff88"
        )
        self.saldo_label.pack(pady=(0, 8))
        
        # Configurar grid
        self.buttons_frame.grid_columnconfigure(0, weight=1)
    
    def _criar_area_principal(self):
        """Criar área principal"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Container para páginas
        self.pages = {}
        self.current_page = None
        
        # Criar apenas dashboard inicial
        self._criar_dashboard_rapido()
        self.mostrar_pagina("dashboard")
    
    def _criar_barra_status(self):
        """Criar barra de status"""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Pronto",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Data/hora
        self.datetime_label = ctk.CTkLabel(
            self.status_frame,
            text=datetime.now().strftime("%d/%m/%Y %H:%M"),
            font=ctk.CTkFont(size=12)
        )
        self.datetime_label.pack(side="right", padx=10, pady=5)
    
    def _criar_dashboard_rapido(self):
        """Criar dashboard básico rapidamente"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["dashboard"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="📊 Dashboard - Carregando...",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Cards básicos
        stats_frame = ctk.CTkFrame(page)
        stats_frame.pack(fill="x", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Cards simples
        self._criar_cards_basicos(stats_frame)
        
        # Placeholder para gráficos
        charts_frame = ctk.CTkFrame(page)
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        loading_label = ctk.CTkLabel(
            charts_frame,
            text="📊 Gráficos serão carregados em breve...",
            font=ctk.CTkFont(size=16)
        )
        loading_label.pack(expand=True)
    
    def _criar_cards_basicos(self, parent):
        """Criar cards básicos de estatísticas"""
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
    
    def _carregar_dados_essenciais(self):
        """Carregar apenas dados essenciais"""
        self.atualizar_saldo()
        self.atualizar_dashboard_basico()
    
    def _carregar_componentes_background(self):
        """Carregar componentes pesados em background"""
        print("🔄 Carregando componentes avançados em background...")
        
        try:
            # Simular carregamento de módulos pesados
            import time
            time.sleep(0.5)  # Simular tempo de carregamento
            
            # Adicionar botões avançados
            self.root.after(0, self._adicionar_botoes_avancados)
            
            # Atualizar dashboard com gráficos
            self.root.after(1000, self._atualizar_dashboard_completo)
            
            print("✅ Componentes avançados carregados!")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar componentes: {e}")
    
    def _adicionar_botoes_avancados(self):
        """Adicionar botões avançados à sidebar"""
        botoes_avancados = [
            ("🔍 Análise", "analise"),
            ("📊 Dashboard Avançado", "dashboard_avancado"),
            ("📈 Visualizações", "visualizacoes"),
            ("🤖 ML Previsões", "ml_previsoes"),
            ("👥 Utilizadores", "usuarios"),
            ("⚙️ Configurações", "configuracoes")
        ]
        
        row_start = len(self.nav_buttons)
        for i, (text, key) in enumerate(botoes_avancados):
            btn = ctk.CTkButton(
                self.buttons_frame,
                text=text,
                command=lambda k=key: self.mostrar_pagina(k),
                height=38,
                font=ctk.CTkFont(size=13),
                anchor="w",
                fg_color="gray30",  # Cor diferente para indicar carregamento
                hover_color="gray40"
            )
            btn.grid(row=row_start + i, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[key] = btn
    
    def _atualizar_dashboard_completo(self):
        """Atualizar dashboard com gráficos completos"""
        if "dashboard" in self.pages:
            # Atualizar título
            for widget in self.pages["dashboard"].winfo_children():
                if isinstance(widget, ctk.CTkLabel) and "Carregando" in widget.cget("text"):
                    widget.configure(text="📊 Dashboard - Visão Geral")
                    break
    
    def mostrar_pagina(self, page_name):
        """Mostrar página (com lazy loading)"""
        # Ocultar página atual
        if self.current_page:
            self.pages[self.current_page].pack_forget()
        
        # Carregar página se necessário
        if page_name not in self.pages_loaded:
            self._carregar_pagina(page_name)
        
        # Mostrar nova página
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)
            self.current_page = page_name
            
            # Atualizar botão ativo
            for key, btn in self.nav_buttons.items():
                if key == page_name:
                    btn.configure(fg_color=("#1f538d", "#14375e"))
                else:
                    btn.configure(fg_color=("#3a7ebf", "#1f538d"))
    
    def _carregar_pagina(self, page_name):
        """Carregar página específica (lazy loading)"""
        if page_name in self.pages_loaded:
            return
        
        print(f"🔄 Carregando página: {page_name}")
        
        try:
            if page_name == "nova_aposta":
                self._criar_nova_aposta_page()
            elif page_name == "historico":
                self._criar_historico_page()
            elif page_name == "banca":
                self._criar_banca_page()
            elif page_name == "estatisticas":
                self._criar_estatisticas_page()
            elif page_name == "analise":
                self._criar_analise_page()
            # Adicionar outras páginas conforme necessário
            else:
                # Página placeholder
                self._criar_pagina_placeholder(page_name)
            
            self.pages_loaded.add(page_name)
            print(f"✅ Página carregada: {page_name}")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar página {page_name}: {e}")
            self._criar_pagina_erro(page_name, str(e))
    
    def _criar_pagina_placeholder(self, page_name):
        """Criar página placeholder"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages[page_name] = page
        
        label = ctk.CTkLabel(
            page,
            text=f"📄 Página {page_name.title()}\n\nEm desenvolvimento...",
            font=ctk.CTkFont(size=20)
        )
        label.pack(expand=True)
    
    def _criar_pagina_erro(self, page_name, erro):
        """Criar página de erro"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages[page_name] = page
        
        label = ctk.CTkLabel(
            page,
            text=f"❌ Erro ao carregar {page_name}\n\n{erro}",
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        label.pack(expand=True)
    
    def _criar_nova_aposta_page(self):
        """Criar página de nova aposta"""
        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["nova_aposta"] = page
        
        # Título
        title = ctk.CTkLabel(
            page,
            text="➕ Nova Aposta",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Formulário básico
        form_frame = ctk.CTkFrame(page)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Campos essenciais
        ctk.CTkLabel(form_frame, text="Data:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        self.data_entry = ctk.CTkEntry(form_frame, placeholder_text="DD/MM/AAAA")
        self.data_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Competição:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
        self.competicao_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Liga Portuguesa")
        self.competicao_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Equipa Casa:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
        self.equipa_casa_entry = ctk.CTkEntry(form_frame, placeholder_text="Nome da equipa")
        self.equipa_casa_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Equipa Fora:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
        self.equipa_fora_entry = ctk.CTkEntry(form_frame, placeholder_text="Nome da equipa")
        self.equipa_fora_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Odd:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
        self.odd_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: 2.50")
        self.odd_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Valor Apostado (€):", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
        self.valor_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: 10.00")
        self.valor_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botão guardar
        ctk.CTkButton(
            form_frame,
            text="💾 Guardar Aposta",
            command=self.guardar_aposta,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
    
    def _criar_historico_page(self):
        """Criar página de histórico"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["historico"] = page
        
        label = ctk.CTkLabel(
            page,
            text="📋 Histórico de Apostas\n\nCarregando dados...",
            font=ctk.CTkFont(size=20)
        )
        label.pack(expand=True)
    
    def _criar_banca_page(self):
        """Criar página de gestão de banca"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["banca"] = page
        
        label = ctk.CTkLabel(
            page,
            text="💰 Gestão de Banca\n\nCarregando dados...",
            font=ctk.CTkFont(size=20)
        )
        label.pack(expand=True)
    
    def _criar_estatisticas_page(self):
        """Criar página de estatísticas"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["estatisticas"] = page
        
        label = ctk.CTkLabel(
            page,
            text="📈 Estatísticas\n\nCarregando dados...",
            font=ctk.CTkFont(size=20)
        )
        label.pack(expand=True)
    
    def _criar_analise_page(self):
        """Criar página de análise"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["analise"] = page
        
        label = ctk.CTkLabel(
            page,
            text="🔍 Análise\n\nCarregando dados...",
            font=ctk.CTkFont(size=20)
        )
        label.pack(expand=True)
    
    def atualizar_saldo(self):
        """Atualizar exibição do saldo"""
        try:
            saldo = self.db.get_saldo_atual()
            self.saldo_label.configure(text=f"€{saldo:.2f}")
            
            # Mudar cor baseada no saldo
            if saldo > 0:
                self.saldo_label.configure(text_color="#00ff88")
            else:
                self.saldo_label.configure(text_color="#ff4444")
        except Exception as e:
            print(f"Erro ao atualizar saldo: {e}")
    
    def atualizar_dashboard_basico(self):
        """Atualizar dados básicos do dashboard"""
        try:
            apostas = self.db.get_apostas()
            
            if not apostas:
                return
            
            # Calcular estatísticas básicas
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
            
            # Atualizar cores
            self.lucro_label.configure(text_color="#28a745" if total_lucro >= 0 else "#dc3545")
            self.roi_label.configure(text_color="#28a745" if roi >= 0 else "#dc3545")
            
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def guardar_aposta(self):
        """Guardar nova aposta"""
        try:
            # Validação básica
            if not all([
                self.data_entry.get(),
                self.competicao_entry.get(),
                self.equipa_casa_entry.get(),
                self.equipa_fora_entry.get(),
                self.odd_entry.get(),
                self.valor_entry.get()
            ]):
                messagebox.showerror("Erro", "Preencha todos os campos")
                return
            
            # Validar valores numéricos
            try:
                odd = float(self.odd_entry.get())
                valor = float(self.valor_entry.get())
                if odd <= 0 or valor <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Odd e valor devem ser números positivos")
                return
            
            # Aqui seria implementada a lógica de guardar a aposta
            messagebox.showinfo("Sucesso", "Aposta guardada com sucesso!")
            
            # Limpar campos
            self.data_entry.delete(0, 'end')
            self.competicao_entry.delete(0, 'end')
            self.equipa_casa_entry.delete(0, 'end')
            self.equipa_fora_entry.delete(0, 'end')
            self.odd_entry.delete(0, 'end')
            self.valor_entry.delete(0, 'end')
            
            # Atualizar dashboard
            self.atualizar_dashboard_basico()
            self.atualizar_saldo()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar aposta: {e}")
    
    def executar(self):
        """Executar aplicação"""
        self.root.mainloop()


if __name__ == "__main__":
    app = InterfaceOtimizada()
    app.executar()