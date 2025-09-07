#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Apostas Desportivas - Versão 2.0
Módulo: Autenticação e Segurança
Autor: Sistema de Apostas
Data: 2025
"""

import sqlite3
import secrets
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import customtkinter as ctk
from tkinter import messagebox
from usuarios import GestorUtilizadores, TipoUtilizador

class SessaoUtilizador:
    """Classe para gestão de sessões de utilizador"""
    
    def __init__(self):
        self.utilizador_atual = None
        self.token_sessao = None
        self.data_inicio = None
        self.permissoes = []
    
    def esta_autenticado(self) -> bool:
        """Verifica se utilizador está autenticado"""
        return self.utilizador_atual is not None and self.token_sessao is not None
    
    def tem_permissao(self, permissao: str) -> bool:
        """Verifica se utilizador tem permissão específica"""
        return permissao in self.permissoes
    
    def limpar_sessao(self):
        """Limpa dados da sessão"""
        self.utilizador_atual = None
        self.token_sessao = None
        self.data_inicio = None
        self.permissoes = []

class GestorAutenticacao:
    """Classe para gestão de autenticação e segurança"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.gestor_utilizadores = GestorUtilizadores(db_path)
        self.sessao_atual = SessaoUtilizador()
        self.max_tentativas_login = 5
        self.tempo_bloqueio_minutos = 30
    
    def autenticar_utilizador(self, username: str, password: str, 
                             ip_address: str = "localhost", 
                             user_agent: str = "Desktop App") -> Tuple[bool, str]:
        """Autentica utilizador no sistema"""
        try:
            # Verificar se utilizador existe
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, tipo_utilizador, 
                       ativo, tentativas_login, bloqueado_ate
                FROM utilizadores 
                WHERE username = ?
            """, (username,))
            
            utilizador = cursor.fetchone()
            
            if not utilizador:
                conn.close()
                return False, "Utilizador não encontrado"
            
            utilizador_id, username, email, password_hash, salt, tipo_utilizador, \
            ativo, tentativas_login, bloqueado_ate = utilizador
            
            # Verificar se utilizador está ativo
            if not ativo:
                conn.close()
                return False, "Conta desativada"
            
            # Verificar se utilizador está bloqueado
            if bloqueado_ate:
                bloqueio_dt = datetime.fromisoformat(bloqueado_ate)
                if datetime.now() < bloqueio_dt:
                    conn.close()
                    return False, f"Conta bloqueada até {bloqueio_dt.strftime('%H:%M:%S')}"
                else:
                    # Remover bloqueio expirado
                    cursor.execute("""
                        UPDATE utilizadores 
                        SET bloqueado_ate = NULL, tentativas_login = 0
                        WHERE id = ?
                    """, (utilizador_id,))
                    tentativas_login = 0
            
            # Verificar password
            if not self.gestor_utilizadores.verificar_password(password, password_hash, salt):
                # Incrementar tentativas de login
                tentativas_login += 1
                
                if tentativas_login >= self.max_tentativas_login:
                    # Bloquear conta
                    bloqueio_ate = datetime.now() + timedelta(minutes=self.tempo_bloqueio_minutos)
                    cursor.execute("""
                        UPDATE utilizadores 
                        SET tentativas_login = ?, bloqueado_ate = ?
                        WHERE id = ?
                    """, (tentativas_login, bloqueio_ate.isoformat(), utilizador_id))
                    
                    conn.commit()
                    conn.close()
                    return False, f"Muitas tentativas falhadas. Conta bloqueada por {self.tempo_bloqueio_minutos} minutos"
                else:
                    cursor.execute("""
                        UPDATE utilizadores 
                        SET tentativas_login = ?
                        WHERE id = ?
                    """, (tentativas_login, utilizador_id))
                    
                    conn.commit()
                    conn.close()
                    return False, f"Password incorreta. Tentativas restantes: {self.max_tentativas_login - tentativas_login}"
            
            # Login bem-sucedido
            # Resetar tentativas de login
            cursor.execute("""
                UPDATE utilizadores 
                SET tentativas_login = 0, ultimo_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (utilizador_id,))
            
            # Criar sessão
            token_sessao = self._criar_sessao(cursor, utilizador_id, ip_address, user_agent)
            
            # Carregar permissões
            permissoes = self.gestor_utilizadores.obter_permissoes_utilizador(utilizador_id)
            
            # Configurar sessão atual
            self.sessao_atual.utilizador_atual = {
                'id': utilizador_id,
                'username': username,
                'email': email,
                'tipo_utilizador': tipo_utilizador
            }
            self.sessao_atual.token_sessao = token_sessao
            self.sessao_atual.data_inicio = datetime.now()
            self.sessao_atual.permissoes = permissoes
            
            conn.commit()
            conn.close()
            
            return True, "Login realizado com sucesso"
            
        except Exception as e:
            return False, f"Erro no login: {str(e)}"
    
    def _criar_sessao(self, cursor, utilizador_id: int, ip_address: str, 
                     user_agent: str) -> str:
        """Cria nova sessão para o utilizador"""
        token_sessao = secrets.token_urlsafe(32)
        data_expiracao = datetime.now() + timedelta(hours=8)  # Sessão expira em 8 horas
        
        cursor.execute("""
            INSERT INTO sessoes 
            (utilizador_id, token_sessao, data_expiracao, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """, (utilizador_id, token_sessao, data_expiracao.isoformat(), 
              ip_address, user_agent))
        
        return token_sessao
    
    def logout(self) -> bool:
        """Termina sessão do utilizador"""
        try:
            if self.sessao_atual.token_sessao:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE sessoes 
                    SET ativo = 0
                    WHERE token_sessao = ?
                """, (self.sessao_atual.token_sessao,))
                
                conn.commit()
                conn.close()
            
            self.sessao_atual.limpar_sessao()
            return True
            
        except Exception as e:
            print(f"Erro no logout: {e}")
            return False
    
    def validar_sessao(self, token_sessao: str) -> bool:
        """Valida se sessão ainda é válida"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.utilizador_id, s.data_expiracao, u.username, u.email, u.tipo_utilizador
                FROM sessoes s
                JOIN utilizadores u ON s.utilizador_id = u.id
                WHERE s.token_sessao = ? AND s.ativo = 1 AND u.ativo = 1
            """, (token_sessao,))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False
            
            utilizador_id, data_expiracao, username, email, tipo_utilizador = resultado
            
            # Verificar se sessão expirou
            if datetime.now() > datetime.fromisoformat(data_expiracao):
                # Desativar sessão expirada
                cursor.execute("""
                    UPDATE sessoes SET ativo = 0 WHERE token_sessao = ?
                """, (token_sessao,))
                conn.commit()
                conn.close()
                return False
            
            # Recarregar dados da sessão
            permissoes = self.gestor_utilizadores.obter_permissoes_utilizador(utilizador_id)
            
            self.sessao_atual.utilizador_atual = {
                'id': utilizador_id,
                'username': username,
                'email': email,
                'tipo_utilizador': tipo_utilizador
            }
            self.sessao_atual.token_sessao = token_sessao
            self.sessao_atual.permissoes = permissoes
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro na validação de sessão: {e}")
            return False
    
    def obter_utilizador_atual(self) -> Optional[Dict]:
        """Obtém dados do utilizador atual"""
        return self.sessao_atual.utilizador_atual
    
    def tem_permissao(self, permissao: str) -> bool:
        """Verifica se utilizador atual tem permissão"""
        return self.sessao_atual.tem_permissao(permissao)
    
    def listar_sessoes_ativas(self) -> list:
        """Lista todas as sessões ativas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.id, u.username, s.data_inicio, s.data_expiracao, 
                       s.ip_address, s.user_agent
                FROM sessoes s
                JOIN utilizadores u ON s.utilizador_id = u.id
                WHERE s.ativo = 1 AND s.data_expiracao > CURRENT_TIMESTAMP
                ORDER BY s.data_inicio DESC
            """)
            
            resultados = cursor.fetchall()
            conn.close()
            
            sessoes = []
            for resultado in resultados:
                sessoes.append({
                    'id': resultado[0],
                    'username': resultado[1],
                    'data_inicio': resultado[2],
                    'data_expiracao': resultado[3],
                    'ip_address': resultado[4],
                    'user_agent': resultado[5]
                })
            
            return sessoes
            
        except Exception as e:
            print(f"Erro ao listar sessões: {e}")
            return []

class JanelaLogin(ctk.CTkToplevel):
    """Janela de login do sistema"""
    
    def __init__(self, parent, callback_sucesso=None):
        super().__init__(parent)
        
        self.callback_sucesso = callback_sucesso
        self.gestor_auth = GestorAutenticacao()
        
        self.configurar_janela()
        self.criar_interface()
        
        # Focar na janela
        self.lift()
        self.focus_force()
        self.grab_set()
    
    def configurar_janela(self):
        """Configura propriedades da janela"""
        self.title("Login - Sistema de Apostas Desportivas")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Centralizar janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"400x500+{x}+{y}")
    
    def criar_interface(self):
        """Cria interface da janela de login"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            main_frame, 
            text="Sistema de Apostas\nDesportivas v2.0",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=(30, 40))
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Campo username
        ctk.CTkLabel(form_frame, text="Utilizador:").pack(pady=(20, 5))
        self.entry_username = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Digite seu nome de utilizador",
            width=300
        )
        self.entry_username.pack(pady=(0, 15))
        
        # Campo password
        ctk.CTkLabel(form_frame, text="Password:").pack(pady=(0, 5))
        self.entry_password = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Digite sua password",
            show="*",
            width=300
        )
        self.entry_password.pack(pady=(0, 20))
        
        # Botão login
        self.btn_login = ctk.CTkButton(
            form_frame,
            text="Entrar",
            command=self.fazer_login,
            width=300,
            height=40
        )
        self.btn_login.pack(pady=(10, 20))
        
        # Link para criar conta
        btn_criar_conta = ctk.CTkButton(
            form_frame,
            text="Criar Nova Conta",
            command=self.abrir_criar_conta,
            width=300,
            height=35,
            fg_color="transparent",
            text_color=("gray10", "gray90")
        )
        btn_criar_conta.pack(pady=(0, 20))
        
        # Informações de login padrão
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text="Login Padrão:\nUtilizador: admin\nPassword: 17014601",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=15)
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.fazer_login())
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Return>', lambda e: self.fazer_login())
        
        # Focar no campo username
        self.entry_username.focus()
    
    def fazer_login(self):
        """Processa tentativa de login"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        
        if not username or not password:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
            return
        
        # Desabilitar botão durante login
        self.btn_login.configure(state="disabled", text="Entrando...")
        self.update()
        
        # Tentar autenticar
        sucesso, mensagem = self.gestor_auth.autenticar_utilizador(username, password)
        
        if sucesso:
            # Reabilitar botão antes de mostrar mensagem de sucesso
            self.btn_login.configure(state="normal", text="Entrar")
            messagebox.showinfo("Sucesso", mensagem)
            
            if self.callback_sucesso:
                # Obter dados do utilizador autenticado
                utilizador_data = self.gestor_auth.sessao_atual.utilizador_atual
                if utilizador_data:
                    utilizador_id = utilizador_data['id']
                    utilizador_nome = utilizador_data['username']
                    self.callback_sucesso(utilizador_id, utilizador_nome)
            
            self.destroy()
        else:
            messagebox.showerror("Erro de Login", mensagem)
            self.entry_password.delete(0, 'end')
            self.entry_password.focus()
            # Reabilitar botão apenas em caso de erro
            self.btn_login.configure(state="normal", text="Entrar")
    
    def abrir_criar_conta(self):
        """Abre janela para criar nova conta"""
        JanelaCriarConta(self, self.gestor_auth.gestor_utilizadores)

class JanelaCriarConta(ctk.CTkToplevel):
    """Janela para criar nova conta"""
    
    def __init__(self, parent, gestor_utilizadores):
        super().__init__(parent)
        
        self.gestor_utilizadores = gestor_utilizadores
        
        self.configurar_janela()
        self.criar_interface()
        
        # Focar na janela
        self.lift()
        self.focus_force()
        self.grab_set()
    
    def configurar_janela(self):
        """Configura propriedades da janela"""
        self.title("Criar Nova Conta")
        self.geometry("450x700")
        self.resizable(False, False)
        
        # Centralizar janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"450x700+{x}+{y}")
    
    def criar_interface(self):
        """Cria interface da janela"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            main_frame, 
            text="Criar Nova Conta",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(pady=(20, 30))
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Campo username
        ctk.CTkLabel(form_frame, text="Nome de Utilizador:").pack(pady=(20, 5))
        self.entry_username = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Digite o nome de utilizador",
            width=350
        )
        self.entry_username.pack(pady=(0, 15))
        
        # Campo email
        ctk.CTkLabel(form_frame, text="Email:").pack(pady=(0, 5))
        self.entry_email = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Digite o email",
            width=350
        )
        self.entry_email.pack(pady=(0, 15))
        
        # Campo password
        ctk.CTkLabel(form_frame, text="Password:").pack(pady=(0, 5))
        self.entry_password = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Digite a password",
            show="*",
            width=350
        )
        self.entry_password.pack(pady=(0, 15))
        
        # Campo confirmar password
        ctk.CTkLabel(form_frame, text="Confirmar Password:").pack(pady=(0, 5))
        self.entry_confirmar_password = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Confirme a password",
            show="*",
            width=350
        )
        self.entry_confirmar_password.pack(pady=(0, 15))
        
        # Tipo de utilizador
        ctk.CTkLabel(form_frame, text="Tipo de Utilizador:").pack(pady=(0, 5))
        self.combo_tipo = ctk.CTkComboBox(
            form_frame,
            values=["utilizador", "gestor"],
            width=350
        )
        self.combo_tipo.set("utilizador")
        self.combo_tipo.pack(pady=(0, 20))
        
        # Botões
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.pack(fill="x", pady=(10, 20))
        
        self.btn_criar = ctk.CTkButton(
            btn_frame,
            text="Criar Conta",
            command=self.criar_conta,
            width=150
        )
        self.btn_criar.pack(side="left", padx=(20, 10))
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=150,
            fg_color="gray"
        )
        btn_cancelar.pack(side="right", padx=(10, 20))
        
        # Focar no campo username
        self.entry_username.focus()
    
    def criar_conta(self):
        """Cria nova conta de utilizador"""
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        confirmar_password = self.entry_confirmar_password.get()
        tipo_str = self.combo_tipo.get()
        
        # Validações
        if not all([username, email, password, confirmar_password]):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
            return
        
        if password != confirmar_password:
            messagebox.showerror("Erro", "As passwords não coincidem")
            return
        
        if len(password) < 6:
            messagebox.showerror("Erro", "A password deve ter pelo menos 6 caracteres")
            return
        
        if "@" not in email:
            messagebox.showerror("Erro", "Email inválido")
            return
        
        # Converter tipo de utilizador
        tipo_utilizador = TipoUtilizador.UTILIZADOR if tipo_str == "utilizador" else TipoUtilizador.GESTOR
        
        # Desabilitar botão durante criação
        self.btn_criar.configure(state="disabled", text="Criando...")
        self.update()
        
        # Tentar criar utilizador
        sucesso = self.gestor_utilizadores.criar_utilizador(
            username, email, password, tipo_utilizador
        )
        
        if sucesso:
            messagebox.showinfo("Sucesso", "Conta criada com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao criar conta. Utilizador ou email já existe.")
            # Reabilitar botão apenas em caso de erro
            self.btn_criar.configure(state="normal", text="Criar Conta")

# Instância global do gestor de autenticação
gestor_autenticacao = GestorAutenticacao()