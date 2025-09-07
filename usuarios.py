#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Apostas Desportivas - Versão 2.0
Módulo: Gestão de Utilizadores e Permissões
Autor: Sistema de Apostas
Data: 2025
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Importar sistema de notificações por email
try:
    from notificacoes_email import gestor_notificacoes
    EMAIL_DISPONIVEL = True
except ImportError:
    EMAIL_DISPONIVEL = False
    print("⚠️ Sistema de notificações por email não disponível")

class TipoUtilizador(Enum):
    """Tipos de utilizador do sistema"""
    ADMIN = "admin"
    GESTOR = "gestor"
    UTILIZADOR = "utilizador"
    CONVIDADO = "convidado"

class PermissaoSistema(Enum):
    """Permissões do sistema"""
    # Apostas
    CRIAR_APOSTAS = "criar_apostas"
    EDITAR_APOSTAS = "editar_apostas"
    ELIMINAR_APOSTAS = "eliminar_apostas"
    VER_APOSTAS = "ver_apostas"
    
    # Relatórios
    VER_RELATORIOS = "ver_relatorios"
    EXPORTAR_RELATORIOS = "exportar_relatorios"
    RELATORIOS_AVANCADOS = "relatorios_avancados"
    
    # Configurações
    CONFIGURAR_SISTEMA = "configurar_sistema"
    GERIR_UTILIZADORES = "gerir_utilizadores"
    CONFIGURAR_SEGURANCA = "configurar_seguranca"
    
    # Dados
    IMPORTAR_DADOS = "importar_dados"
    EXPORTAR_DADOS = "exportar_dados"
    BACKUP_SISTEMA = "backup_sistema"
    
    # Machine Learning
    VER_PREVISOES = "ver_previsoes"
    TREINAR_MODELOS = "treinar_modelos"
    CONFIGURAR_ML = "configurar_ml"

class GestorUtilizadores:
    """Classe para gestão de utilizadores e permissões"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.inicializar_base_dados()
        self.criar_admin_padrao()
    
    def inicializar_base_dados(self):
        """Inicializar base de dados e tabelas"""
        self.inicializar_tabelas()
    
    def inicializar_tabelas(self):
        """Inicializa as tabelas de utilizadores e permissões"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de utilizadores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilizadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                tipo_utilizador TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP,
                tentativas_login INTEGER DEFAULT 0,
                bloqueado_ate TIMESTAMP,
                configuracoes TEXT DEFAULT '{}'
            )
        """)
        
        # Tabela de permissões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissoes_utilizador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizador_id INTEGER,
                permissao TEXT NOT NULL,
                concedida BOOLEAN DEFAULT 1,
                data_concessao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (utilizador_id) REFERENCES utilizadores (id)
            )
        """)
        
        # Tabela de sessões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizador_id INTEGER,
                token_sessao TEXT UNIQUE NOT NULL,
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_expiracao TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (utilizador_id) REFERENCES utilizadores (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def criar_admin_padrao(self):
        """Cria utilizador admin padrão se não existir"""
        if not self.utilizador_existe("admin"):
            self.criar_utilizador(
                username="admin",
                email="admin@apostas.local",
                password="17014601",
                tipo_utilizador=TipoUtilizador.ADMIN
            )
    
    def gerar_hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Gera hash seguro da password"""
        if salt is None:
            salt = os.urandom(32).hex()
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return password_hash, salt
    
    def verificar_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verifica se a password está correta"""
        hash_verificacao, _ = self.gerar_hash_password(password, salt)
        return hash_verificacao == password_hash
    
    def criar_utilizador(self, username: str, email: str, password: str, 
                        tipo_utilizador: TipoUtilizador) -> bool:
        """Cria novo utilizador"""
        try:
            if self.utilizador_existe(username) or self.email_existe(email):
                return False
            
            password_hash, salt = self.gerar_hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO utilizadores 
                (username, email, password_hash, salt, tipo_utilizador)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, tipo_utilizador.value))
            
            utilizador_id = cursor.lastrowid
            
            # Atribuir permissões padrão
            self._atribuir_permissoes_padrao(cursor, utilizador_id, tipo_utilizador)
            
            conn.commit()
            conn.close()
            
            # Enviar notificação por email sobre novo registo
            if EMAIL_DISPONIVEL:
                try:
                    gestor_notificacoes.notificar_novo_registo(
                        username=username,
                        email_utilizador=email,
                        tipo_utilizador=tipo_utilizador.value
                    )
                    print(f"📧 Notificação de novo registo enviada para {username}")
                except Exception as e:
                    print(f"⚠️ Erro ao enviar notificação por email: {e}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar utilizador: {e}")
            return False
    
    def _atribuir_permissoes_padrao(self, cursor, utilizador_id: int, 
                                   tipo_utilizador: TipoUtilizador):
        """Atribui permissões padrão baseadas no tipo de utilizador"""
        permissoes = []
        
        if tipo_utilizador == TipoUtilizador.ADMIN:
            # Admin tem todas as permissões
            permissoes = [p.value for p in PermissaoSistema]
        
        elif tipo_utilizador == TipoUtilizador.GESTOR:
            permissoes = [
                PermissaoSistema.CRIAR_APOSTAS.value,
                PermissaoSistema.EDITAR_APOSTAS.value,
                PermissaoSistema.VER_APOSTAS.value,
                PermissaoSistema.VER_RELATORIOS.value,
                PermissaoSistema.EXPORTAR_RELATORIOS.value,
                PermissaoSistema.RELATORIOS_AVANCADOS.value,
                PermissaoSistema.IMPORTAR_DADOS.value,
                PermissaoSistema.EXPORTAR_DADOS.value,
                PermissaoSistema.VER_PREVISOES.value
            ]
        
        elif tipo_utilizador == TipoUtilizador.UTILIZADOR:
            permissoes = [
                PermissaoSistema.CRIAR_APOSTAS.value,
                PermissaoSistema.EDITAR_APOSTAS.value,
                PermissaoSistema.VER_APOSTAS.value,
                PermissaoSistema.VER_RELATORIOS.value,
                PermissaoSistema.VER_PREVISOES.value
            ]
        
        elif tipo_utilizador == TipoUtilizador.CONVIDADO:
            permissoes = [
                PermissaoSistema.VER_APOSTAS.value,
                PermissaoSistema.VER_RELATORIOS.value
            ]
        
        for permissao in permissoes:
            cursor.execute("""
                INSERT INTO permissoes_utilizador (utilizador_id, permissao)
                VALUES (?, ?)
            """, (utilizador_id, permissao))
    
    def utilizador_existe(self, username: str) -> bool:
        """Verifica se utilizador existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM utilizadores WHERE username = ?", 
            (username,)
        )
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado is not None
    
    def email_existe(self, email: str) -> bool:
        """Verifica se email existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM utilizadores WHERE email = ?", 
            (email,)
        )
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado is not None
    
    def obter_utilizador(self, username: str) -> Optional[Dict]:
        """Obtém dados do utilizador"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, tipo_utilizador, ativo, 
                   data_criacao, ultimo_login, configuracoes
            FROM utilizadores 
            WHERE username = ?
        """, (username,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            return {
                'id': resultado[0],
                'username': resultado[1],
                'email': resultado[2],
                'tipo_utilizador': resultado[3],
                'ativo': bool(resultado[4]),
                'data_criacao': resultado[5],
                'ultimo_login': resultado[6],
                'configuracoes': json.loads(resultado[7] or '{}')
            }
        
        return None
    
    def listar_utilizadores(self) -> List[Dict]:
        """Lista todos os utilizadores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, tipo_utilizador, ativo, 
                   data_criacao, ultimo_login
            FROM utilizadores 
            ORDER BY data_criacao DESC
        """)
        
        resultados = cursor.fetchall()
        conn.close()
        
        utilizadores = []
        for resultado in resultados:
            utilizadores.append({
                'id': resultado[0],
                'username': resultado[1],
                'email': resultado[2],
                'tipo_utilizador': resultado[3],
                'ativo': bool(resultado[4]),
                'data_criacao': resultado[5],
                'ultimo_login': resultado[6]
            })
        
        return utilizadores
    
    def verificar_permissao(self, utilizador_id: int, permissao: PermissaoSistema) -> bool:
        """Verifica se utilizador tem permissão específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT concedida FROM permissoes_utilizador 
            WHERE utilizador_id = ? AND permissao = ?
        """, (utilizador_id, permissao.value))
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado and bool(resultado[0])
    
    def obter_permissoes_utilizador(self, utilizador_id: int) -> List[str]:
        """Obtém todas as permissões do utilizador"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT permissao FROM permissoes_utilizador 
            WHERE utilizador_id = ? AND concedida = 1
        """, (utilizador_id,))
        
        resultados = cursor.fetchall()
        conn.close()
        
        return [resultado[0] for resultado in resultados]
    
    def atualizar_utilizador(self, utilizador_id: int, **kwargs) -> bool:
        """Atualiza dados do utilizador"""
        try:
            campos_permitidos = ['email', 'tipo_utilizador', 'ativo', 'configuracoes']
            campos_atualizacao = []
            valores = []
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos:
                    if campo == 'configuracoes':
                        valor = json.dumps(valor)
                    campos_atualizacao.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos_atualizacao:
                return False
            
            valores.append(utilizador_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"UPDATE utilizadores SET {', '.join(campos_atualizacao)} WHERE id = ?"
            cursor.execute(query, valores)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar utilizador: {e}")
            return False
    
    def eliminar_utilizador(self, utilizador_id: int) -> bool:
        """Elimina utilizador (soft delete)"""
        return self.atualizar_utilizador(utilizador_id, ativo=False)
    
    def alterar_password(self, utilizador_id: int, nova_password: str) -> bool:
        """Altera password do utilizador"""
        try:
            password_hash, salt = self.gerar_hash_password(nova_password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE utilizadores 
                SET password_hash = ?, salt = ?
                WHERE id = ?
            """, (password_hash, salt, utilizador_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Erro ao alterar password: {e}")
            return False

# Instância global do gestor de utilizadores
gestor_utilizadores = GestorUtilizadores()