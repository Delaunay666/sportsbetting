#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Segurança e Criptografia
Versão 1.1 - Sistema de Apostas Desportivas

Este módulo é responsável pela criptografia de dados sensíveis,
gestão de chaves e segurança geral do sistema.
"""

import os
import json
import hashlib
import secrets
import sqlite3
from typing import Optional, Dict, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import logging
from datetime import datetime, timedelta
import getpass

class GestorSeguranca:
    """Classe responsável pela gestão de segurança e criptografia."""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.config_path = "config_seguranca.json"
        self.chave_path = ".chave_sistema"
        self.salt_path = ".salt_sistema"
        self.fernet = None
        self.configurar_logging()
        
    def configurar_logging(self):
        """Configura sistema de logging para segurança."""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename='logs/seguranca.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def gerar_chave_mestre(self, senha: str) -> bytes:
        """Gera chave mestre baseada em senha do utilizador."""
        # Gerar ou carregar salt
        if os.path.exists(self.salt_path):
            with open(self.salt_path, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_path, 'wb') as f:
                f.write(salt)
            # Tornar arquivo oculto no Windows
            if os.name == 'nt':
                os.system(f'attrib +h "{self.salt_path}"')
        
        # Derivar chave da senha
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        chave = base64.urlsafe_b64encode(kdf.derive(senha.encode()))
        return chave
    
    def inicializar_sistema_seguranca(self, senha: Optional[str] = None) -> bool:
        """Inicializa o sistema de segurança."""
        try:
            if not senha:
                senha = getpass.getpass("Digite a senha mestre para o sistema: ")
            
            # Gerar chave mestre
            chave_mestre = self.gerar_chave_mestre(senha)
            
            # Criar instância Fernet
            self.fernet = Fernet(chave_mestre)
            
            # Salvar configurações de segurança
            config_seguranca = {
                "inicializado": True,
                "data_inicializacao": datetime.now().isoformat(),
                "versao_seguranca": "1.1",
                "algoritmo_criptografia": "Fernet (AES 128)",
                "iteracoes_pbkdf2": 100000
            }
            
            # Criptografar e salvar configurações
            config_criptografada = self.fernet.encrypt(json.dumps(config_seguranca).encode())
            
            with open(self.config_path, 'wb') as f:
                f.write(config_criptografada)
            
            # Tornar arquivo oculto no Windows
            if os.name == 'nt':
                os.system(f'attrib +h "{self.config_path}"')
            
            self.logger.info("Sistema de segurança inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sistema de segurança: {e}")
            return False
    
    def autenticar(self, senha: str) -> bool:
        """Autentica utilizador com senha mestre."""
        try:
            # Verificar se sistema está inicializado
            if not os.path.exists(self.config_path):
                return self.inicializar_sistema_seguranca(senha)
            
            # Gerar chave da senha fornecida
            chave_teste = self.gerar_chave_mestre(senha)
            fernet_teste = Fernet(chave_teste)
            
            # Tentar descriptografar configurações
            with open(self.config_path, 'rb') as f:
                config_criptografada = f.read()
            
            config_descriptografada = fernet_teste.decrypt(config_criptografada)
            config = json.loads(config_descriptografada.decode())
            
            # Se chegou até aqui, senha está correta
            self.fernet = fernet_teste
            self.logger.info("Autenticação realizada com sucesso")
            return True
            
        except Exception as e:
            self.logger.warning(f"Tentativa de autenticação falhada: {e}")
            return False
    
    def criptografar_dados(self, dados: Union[str, Dict, Any]) -> str:
        """Criptografa dados sensíveis."""
        if not self.fernet:
            raise ValueError("Sistema de segurança não inicializado")
        
        try:
            # Converter dados para string JSON se necessário
            if isinstance(dados, (dict, list)):
                dados_str = json.dumps(dados)
            else:
                dados_str = str(dados)
            
            # Criptografar
            dados_criptografados = self.fernet.encrypt(dados_str.encode())
            
            # Retornar como string base64
            return base64.urlsafe_b64encode(dados_criptografados).decode()
            
        except Exception as e:
            self.logger.error(f"Erro ao criptografar dados: {e}")
            raise
    
    def descriptografar_dados(self, dados_criptografados: str) -> str:
        """Descriptografa dados sensíveis."""
        if not self.fernet:
            raise ValueError("Sistema de segurança não inicializado")
        
        try:
            # Decodificar base64
            dados_bytes = base64.urlsafe_b64decode(dados_criptografados.encode())
            
            # Descriptografar
            dados_descriptografados = self.fernet.decrypt(dados_bytes)
            
            return dados_descriptografados.decode()
            
        except Exception as e:
            self.logger.error(f"Erro ao descriptografar dados: {e}")
            raise
    
    def criptografar_campo_db(self, tabela: str, campo: str, id_registro: int, valor: str):
        """Criptografa um campo específico na base de dados."""
        try:
            valor_criptografado = self.criptografar_dados(valor)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"UPDATE {tabela} SET {campo} = ? WHERE id = ?"
            cursor.execute(query, (valor_criptografado, id_registro))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Campo {campo} da tabela {tabela} criptografado (ID: {id_registro})")
            
        except Exception as e:
            self.logger.error(f"Erro ao criptografar campo da DB: {e}")
            raise
    
    def descriptografar_campo_db(self, tabela: str, campo: str, id_registro: int) -> str:
        """Descriptografa um campo específico da base de dados."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = f"SELECT {campo} FROM {tabela} WHERE id = ?"
            cursor.execute(query, (id_registro,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0]:
                return self.descriptografar_dados(resultado[0])
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Erro ao descriptografar campo da DB: {e}")
            raise
    
    def criar_backup_seguro(self, caminho_backup: str) -> str:
        """Cria backup criptografado da base de dados."""
        try:
            # Ler base de dados
            with open(self.db_path, 'rb') as f:
                dados_db = f.read()
            
            # Criptografar dados
            dados_criptografados = self.fernet.encrypt(dados_db)
            
            # Salvar backup criptografado
            backup_path = f"{caminho_backup}.encrypted"
            with open(backup_path, 'wb') as f:
                f.write(dados_criptografados)
            
            # Criar arquivo de metadados
            metadados = {
                "data_backup": datetime.now().isoformat(),
                "tamanho_original": len(dados_db),
                "tamanho_criptografado": len(dados_criptografados),
                "algoritmo": "Fernet",
                "versao": "1.1"
            }
            
            metadados_path = f"{caminho_backup}.meta"
            with open(metadados_path, 'w') as f:
                json.dump(metadados, f, indent=2)
            
            self.logger.info(f"Backup seguro criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup seguro: {e}")
            raise
    
    def restaurar_backup_seguro(self, caminho_backup: str) -> bool:
        """Restaura backup criptografado da base de dados."""
        try:
            backup_path = f"{caminho_backup}.encrypted"
            
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup não encontrado: {backup_path}")
            
            # Ler backup criptografado
            with open(backup_path, 'rb') as f:
                dados_criptografados = f.read()
            
            # Descriptografar dados
            dados_descriptografados = self.fernet.decrypt(dados_criptografados)
            
            # Criar backup da DB atual
            if os.path.exists(self.db_path):
                backup_atual = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.db_path, backup_atual)
            
            # Restaurar base de dados
            with open(self.db_path, 'wb') as f:
                f.write(dados_descriptografados)
            
            self.logger.info(f"Backup restaurado com sucesso: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def gerar_hash_integridade(self, arquivo: str) -> str:
        """Gera hash SHA-256 para verificação de integridade."""
        try:
            with open(arquivo, 'rb') as f:
                conteudo = f.read()
            
            hash_sha256 = hashlib.sha256(conteudo).hexdigest()
            return hash_sha256
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar hash de integridade: {e}")
            raise
    
    def verificar_integridade(self, arquivo: str, hash_esperado: str) -> bool:
        """Verifica integridade de arquivo usando hash SHA-256."""
        try:
            hash_atual = self.gerar_hash_integridade(arquivo)
            return hash_atual == hash_esperado
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar integridade: {e}")
            return False
    
    def limpar_dados_temporarios(self):
        """Remove dados temporários e sensíveis da memória."""
        try:
            # Limpar instância Fernet
            self.fernet = None
            
            # Remover arquivos temporários
            temp_files = [f for f in os.listdir('.') if f.startswith('temp_') and f.endswith('.png')]
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            self.logger.info("Dados temporários limpos")
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar dados temporários: {e}")
    
    def gerar_token_sessao(self) -> str:
        """Gera token seguro para sessão."""
        return secrets.token_urlsafe(32)
    
    def validar_token_sessao(self, token: str, token_esperado: str) -> bool:
        """Valida token de sessão."""
        return secrets.compare_digest(token, token_esperado)
    
    def obter_configuracoes_seguranca(self) -> Dict:
        """Obtém configurações de segurança (descriptografadas)."""
        if not self.fernet:
            raise ValueError("Sistema de segurança não inicializado")
        
        try:
            with open(self.config_path, 'rb') as f:
                config_criptografada = f.read()
            
            config_descriptografada = self.fernet.decrypt(config_criptografada)
            return json.loads(config_descriptografada.decode())
            
        except Exception as e:
            self.logger.error(f"Erro ao obter configurações: {e}")
            raise
    
    def atualizar_configuracoes_seguranca(self, novas_configs: Dict):
        """Atualiza configurações de segurança."""
        if not self.fernet:
            raise ValueError("Sistema de segurança não inicializado")
        
        try:
            # Obter configurações atuais
            config_atual = self.obter_configuracoes_seguranca()
            
            # Atualizar com novas configurações
            config_atual.update(novas_configs)
            config_atual["ultima_atualizacao"] = datetime.now().isoformat()
            
            # Criptografar e salvar
            config_criptografada = self.fernet.encrypt(json.dumps(config_atual).encode())
            
            with open(self.config_path, 'wb') as f:
                f.write(config_criptografada)
            
            self.logger.info("Configurações de segurança atualizadas")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configurações: {e}")
            raise
    
    def verificar_configuracao(self) -> bool:
        """Verifica se o sistema de segurança está configurado."""
        return os.path.exists(self.config_path) and os.path.exists(self.salt_path)
    
    def verificar_sistema_seguranca(self) -> Dict[str, bool]:
        """Verifica estado do sistema de segurança."""
        verificacoes = {
            "sistema_inicializado": os.path.exists(self.config_path),
            "salt_presente": os.path.exists(self.salt_path),
            "fernet_ativo": self.fernet is not None,
            "logs_funcionando": os.path.exists('logs/seguranca.log'),
            "db_presente": os.path.exists(self.db_path)
        }
        
        return verificacoes
    
    def configurar_autenticacao(self, usuario: str, senha: str) -> bool:
        """Configura sistema de autenticação com usuário e senha."""
        try:
            if not self.fernet:
                raise ValueError("Sistema de segurança não inicializado")
            
            # Criar hash da senha
            senha_hash = hashlib.pbkdf2_hmac('sha256', senha.encode(), 
                                           secrets.token_bytes(32), 100000)
            
            # Dados de autenticação
            auth_data = {
                "usuario": usuario,
                "senha_hash": base64.b64encode(senha_hash).decode(),
                "data_configuracao": datetime.now().isoformat(),
                "ativo": True
            }
            
            # Criptografar e salvar dados de autenticação
            auth_criptografada = self.fernet.encrypt(json.dumps(auth_data).encode())
            
            auth_path = "auth_config.json"
            with open(auth_path, 'wb') as f:
                f.write(auth_criptografada)
            
            # Tornar arquivo oculto no Windows
            if os.name == 'nt':
                os.system(f'attrib +h "{auth_path}"')
            
            self.logger.info(f"Autenticação configurada para usuário: {usuario}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar autenticação: {e}")
            return False

class ContextoSeguranca:
    """Context manager para operações seguras."""
    
    def __init__(self, gestor_seguranca: GestorSeguranca, senha: str):
        self.gestor = gestor_seguranca
        self.senha = senha
        self.autenticado = False
    
    def __enter__(self):
        self.autenticado = self.gestor.autenticar(self.senha)
        if not self.autenticado:
            raise ValueError("Falha na autenticação")
        return self.gestor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gestor.limpar_dados_temporarios()

# Funções de conveniência
def inicializar_seguranca(senha: Optional[str] = None) -> GestorSeguranca:
    """Inicializa sistema de segurança."""
    gestor = GestorSeguranca()
    if gestor.inicializar_sistema_seguranca(senha):
        return gestor
    else:
        raise RuntimeError("Falha ao inicializar sistema de segurança")

def criar_contexto_seguro(senha: str) -> ContextoSeguranca:
    """Cria contexto seguro para operações."""
    gestor = GestorSeguranca()
    return ContextoSeguranca(gestor, senha)

if __name__ == "__main__":
    # Teste do módulo
    try:
        gestor = GestorSeguranca()
        
        # Teste de inicialização
        senha_teste = "senha_teste_123"
        if gestor.inicializar_sistema_seguranca(senha_teste):
            print("Sistema de segurança inicializado com sucesso")
            
            # Teste de criptografia
            dados_teste = "Dados sensíveis para teste"
            dados_criptografados = gestor.criptografar_dados(dados_teste)
            dados_descriptografados = gestor.descriptografar_dados(dados_criptografados)
            
            print(f"Dados originais: {dados_teste}")
            print(f"Dados criptografados: {dados_criptografados[:50]}...")
            print(f"Dados descriptografados: {dados_descriptografados}")
            print(f"Teste bem-sucedido: {dados_teste == dados_descriptografados}")
            
        else:
            print("Falha ao inicializar sistema de segurança")
            
    except Exception as e:
        print(f"Erro no teste: {e}")