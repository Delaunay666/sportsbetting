#!/usr/bin/env python3
"""
Aplicação de Gestão de Apostas Desportivas - Versão 2.0
Script de Inicialização Otimizado

Este script implementa as melhores práticas de inicialização:
- Verificação de dependências
- Configuração de logging
- Tratamento de erros robusto
- Validação do ambiente
- Inicialização segura
- Inicialização dos módulos da Versão 2.0

Autor: Sistema de Gestão de Apostas
Versão: 2.0.0
Data: 2025
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional, List
import json
from datetime import datetime
import time
import tkinter as tk
from tkinter import ttk
import threading

def safe_input(prompt: str = "") -> str:
    """
    Função segura para input que funciona tanto em modo console quanto executável.
    
    Args:
        prompt: Mensagem a exibir
        
    Returns:
        String vazia se stdin não estiver disponível
    """
    try:
        # Verificar se stdin está disponível
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            return input(prompt)
        else:
            # Em executáveis, apenas aguardar um tempo e retornar
            print(prompt)
            time.sleep(2)  # Aguardar 2 segundos
            return ""
    except (EOFError, OSError, RuntimeError):
        # Se houver erro com stdin, apenas aguardar e retornar
        print(prompt)
        time.sleep(2)
        return ""

# Configurar DPI awareness para Windows
if sys.platform.startswith('win'):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass  # Ignorar se não conseguir configurar DPI awareness

# Configuração de logging estruturado
# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app_startup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LoadingScreen:
    """
    Tela de loading moderna e bonita com animações e design atrativo.
    """
    
    def __init__(self):
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.progress_bar = None
        self.is_closed = False
        self.animation_running = False
        self.dots_count = 0
        
    def show(self):
        """Mostra a tela de loading moderna."""
        # Usar sempre a versão tkinter padrão para maior estabilidade
        return self._show_simple_fallback()
    
    def _show_simple_fallback(self):
        """Versão de fallback moderna usando tkinter padrão."""
        try:
            self.root = tk.Tk()
            self.root.title("Sistema de Apostas Desportivas")
            
            # Configurar geometria de forma segura
            width = 500
            height = 400
            
            # Obter dimensões da tela
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calcular posição central
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            # Definir geometria com posição específica
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            self.root.resizable(False, False)
            self.root.configure(bg='#1a1a2e')
            
            # Configurar ícone se disponível
            try:
                icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except Exception:
                pass
            
            # Frame principal
            main_frame = tk.Frame(self.root, bg='#1a1a2e')
            main_frame.pack(fill='both', expand=True, padx=30, pady=30)
            
            # Logo/Ícone principal
            logo_label = tk.Label(
                main_frame,
                text="🎯",
                font=('Arial', 48),
                fg='#00d4ff',
                bg='#1a1a2e'
            )
            logo_label.pack(pady=(20, 10))
            
            # Título principal
            title_label = tk.Label(
                main_frame,
                text="Sistema de Gestão de Apostas",
                font=('Arial', 18, 'bold'),
                fg='white',
                bg='#1a1a2e'
            )
            title_label.pack(pady=(0, 5))
            
            # Subtítulo
            subtitle_label = tk.Label(
                main_frame,
                text="Versão 2.0 - Profissional",
                font=('Arial', 11),
                fg='#a0a0a0',
                bg='#1a1a2e'
            )
            subtitle_label.pack(pady=(0, 30))
            
            # Status com animação
            self.status_var = tk.StringVar()
            self.status_var.set("Inicializando")
            status_label = tk.Label(
                main_frame,
                textvariable=self.status_var,
                font=('Arial', 10),
                fg='#00d4ff',
                bg='#1a1a2e'
            )
            status_label.pack(pady=(0, 15))
            
            # Frame para barra de progresso
            progress_frame = tk.Frame(main_frame, bg='#1a1a2e')
            progress_frame.pack(pady=(0, 10))
            
            # Barra de progresso
            self.progress_var = tk.DoubleVar()
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Custom.Horizontal.TProgressbar',
                          background='#00d4ff',
                          troughcolor='#2a2a3e',
                          borderwidth=0,
                          lightcolor='#00d4ff',
                          darkcolor='#00d4ff')
            
            self.progress_bar = ttk.Progressbar(
                progress_frame,
                variable=self.progress_var,
                maximum=100,
                length=350,
                mode='determinate',
                style='Custom.Horizontal.TProgressbar'
            )
            self.progress_bar.pack()
            
            # Label de porcentagem
            self.percent_var = tk.StringVar()
            self.percent_var.set("0%")
            percent_label = tk.Label(
                main_frame,
                textvariable=self.percent_var,
                font=('Arial', 10, 'bold'),
                fg='white',
                bg='#1a1a2e'
            )
            percent_label.pack(pady=(10, 20))
            
            # Informação adicional
            info_label = tk.Label(
                main_frame,
                text="Carregando módulos e configurações...",
                font=('Arial', 9),
                fg='#808080',
                bg='#1a1a2e'
            )
            info_label.pack(pady=(0, 20))
            
            # Iniciar animação dos pontos
            self._start_dots_animation()
            
            # Mostrar janela e trazer para frente
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            self.root.update()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de loading fallback: {e}")
            return False
    
    def _start_dots_animation(self):
        """Inicia animação dos pontos no status."""
        if not self.is_closed and self.root:
            self.animation_running = True
            self._animate_dots()
    
    def _animate_dots(self):
        """Anima os pontos no texto de status."""
        if not self.animation_running or self.is_closed or not self.root:
            return
            
        try:
            current_text = self.status_var.get()
            # Remove pontos existentes
            base_text = current_text.rstrip('.')
            
            # Adiciona pontos (0 a 3)
            self.dots_count = (self.dots_count + 1) % 4
            new_text = base_text + '.' * self.dots_count
            
            self.status_var.set(new_text)
            
            # Agendar próxima animação
            self.root.after(500, self._animate_dots)
            
        except Exception:
            pass
    
    def update_progress(self, value, status=""):
        """Atualiza o progresso da barra de loading."""
        if self.root and not self.is_closed:
            try:
                # Atualizar barra de progresso (CustomTkinter usa valores de 0 a 1)
                if hasattr(self.progress_bar, 'set'):
                    # CustomTkinter ProgressBar
                    self.progress_bar.set(value / 100.0)
                else:
                    # Tkinter Progressbar (fallback)
                    self.progress_var.set(value)
                
                # Atualizar porcentagem
                self.percent_var.set(f"{int(value)}%")
                
                # Atualizar status
                if status:
                    # Parar animação temporariamente para mostrar status específico
                    self.animation_running = False
                    self.status_var.set(status)
                    # Reiniciar animação após um tempo
                    if value < 100:
                        self.root.after(1000, self._restart_animation)
                
                self.root.update()
            except Exception as e:
                logger.error(f"Erro ao atualizar progresso: {e}")
    
    def _restart_animation(self):
        """Reinicia a animação dos pontos."""
        if not self.is_closed and self.root:
            self.animation_running = True
            self._animate_dots()
    
    def close(self):
        """Fecha a tela de loading."""
        if self.root and not self.is_closed:
            try:
                self.is_closed = True
                self.animation_running = False  # Parar animação
                self.root.destroy()
                self.root = None
            except Exception as e:
                logger.error(f"Erro ao fechar tela de loading: {e}")

class AppInitializer:
    """
    Classe responsável pela inicialização segura da aplicação.
    
    Implementa verificações de pré-requisitos, configuração do ambiente
    e inicialização dos componentes principais.
    """
    
    def __init__(self):
        # Determinar diretório da aplicação corretamente para executáveis PyInstaller
        if getattr(sys, 'frozen', False):
            # Executável PyInstaller - usar diretório do executável
            self.app_dir = Path(sys.executable).parent
        else:
            # Execução normal do Python - usar diretório do script
            self.app_dir = Path(__file__).parent
        self.required_modules = [
            'customtkinter',
            'pandas',
            'matplotlib',
            'cryptography',
            'reportlab'
        ]
        self.optional_modules_v2 = [
            'flask',
            'scikit-learn',
            'kivy',
            'bcrypt',
            'PyJWT'
        ]
        self.required_files = [
            'interface.py',
            'apostas.db',
            'requirements.txt'
        ]
        self.optional_files_v2 = [
            'usuarios.py',
            'autenticacao.py',
            'api_mobile.py',
            'ml_previsoes.py',
            # Ficheiros de gamificação removidos
        ]
        
    def verificar_python_version(self) -> bool:
        """
        Verifica se a versão do Python é compatível.
        
        Returns:
            bool: True se a versão for compatível
        """
        version_info = sys.version_info
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            logger.error(f"Python 3.8+ é necessário. Versão atual: {sys.version}")
            return False
        
        logger.info(f"✅ Python {sys.version} - Compatível")
        return True
    
    def verificar_dependencias(self) -> bool:
        """
        Verifica se todas as dependências estão instaladas.
        
        Returns:
            bool: True se todas as dependências estiverem disponíveis
        """
        missing_modules = []
        
        # Verificar módulos obrigatórios
        for module in self.required_modules:
            try:
                __import__(module)
                logger.info(f"✅ Módulo {module} - Disponível")
            except ImportError:
                missing_modules.append(module)
                logger.error(f"❌ Módulo {module} - Não encontrado")
        
        # Verificar módulos opcionais da v2.0
        for module in self.optional_modules_v2:
            try:
                __import__(module)
                logger.info(f"✅ Módulo {module} - Disponível (v2.0)")
            except ImportError:
                logger.info(f"ℹ️ Módulo {module} - Não encontrado (funcionalidade v2.0 não disponível)")
        
        if missing_modules:
            logger.error(f"Módulos em falta: {', '.join(missing_modules)}")
            logger.info("Execute: pip install -r requirements.txt")
            return False
        
        return True
    
    def verificar_arquivos(self) -> bool:
        """
        Verifica se todos os arquivos necessários existem.
        
        Returns:
            bool: True se todos os arquivos estiverem presentes
        """
        missing_files = []
        
        # Verificar arquivos obrigatórios
        for file_name in self.required_files:
            # Para executáveis PyInstaller, procurar primeiro na pasta _internal
            if getattr(sys, 'frozen', False):
                file_path = self.app_dir / '_internal' / file_name
                if not file_path.exists():
                    file_path = self.app_dir / file_name
            else:
                file_path = self.app_dir / file_name
                
            if file_path.exists():
                logger.info(f"✅ Arquivo {file_name} - Encontrado")
            else:
                missing_files.append(file_name)
                logger.error(f"❌ Arquivo {file_name} - Não encontrado")
        
        # Verificar arquivos opcionais da v2.0
        for file_name in self.optional_files_v2:
            # Para executáveis PyInstaller, procurar primeiro na pasta _internal
            if getattr(sys, 'frozen', False):
                file_path = self.app_dir / '_internal' / file_name
                if not file_path.exists():
                    file_path = self.app_dir / file_name
            else:
                file_path = self.app_dir / file_name
                
            if file_path.exists():
                logger.info(f"✅ Arquivo {file_name} - Encontrado (v2.0)")
            else:
                logger.info(f"ℹ️ Arquivo {file_name} - Não encontrado (funcionalidade v2.0 não disponível)")
        
        if missing_files:
            logger.error(f"Arquivos em falta: {', '.join(missing_files)}")
            return False
        
        return True
    
    def criar_diretorios(self) -> bool:
        """
        Cria diretórios necessários se não existirem.
        
        Returns:
            bool: True se todos os diretórios foram criados/verificados
        """
        directories = ['logs', 'exports', 'backups', 'data', 'traducoes', 'temas']
        
        try:
            for dir_name in directories:
                # Para executáveis PyInstaller, criar diretórios no diretório do executável
                dir_path = self.app_dir / dir_name
                dir_path.mkdir(exist_ok=True)
                logger.info(f"✅ Diretório {dir_name} - Verificado")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar diretórios: {e}")
            return False
    
    def verificar_configuracoes(self) -> bool:
        """
        Verifica e cria configurações padrão se necessário.
        
        Returns:
            bool: True se as configurações estão válidas
        """
        try:
            # Verificar configuração de idioma
            config_idioma_path = self.app_dir / 'config_idioma.json'
            if not config_idioma_path.exists():
                config_idioma = {
                    'idioma_atual': 'pt',
                    'idiomas_disponiveis': ['pt', 'en', 'es']
                }
                with open(config_idioma_path, 'w', encoding='utf-8') as f:
                    json.dump(config_idioma, f, indent=2, ensure_ascii=False)
                logger.info("✅ Configuração de idioma criada")
            
            # Verificar configuração de temas
            config_temas_path = self.app_dir / 'config_temas.json'
            if not config_temas_path.exists():
                config_temas = {
                    'tema_atual': 'Claro Padrão',
                    'temas_personalizados': []
                }
                with open(config_temas_path, 'w', encoding='utf-8') as f:
                    json.dump(config_temas, f, indent=2, ensure_ascii=False)
                logger.info("✅ Configuração de temas criada")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar configurações: {e}")
            return False
    
    def log_system_info(self) -> None:
        """
        Registra informações do sistema para diagnóstico.
        """
        logger.info("=" * 50)
        logger.info("INFORMAÇÕES DO SISTEMA")
        logger.info("=" * 50)
        logger.info(f"Sistema Operacional: {os.name}")
        logger.info(f"Plataforma: {sys.platform}")
        logger.info(f"Versão Python: {sys.version}")
        logger.info(f"Diretório da Aplicação: {self.app_dir}")
        logger.info(f"Data/Hora de Inicialização: {datetime.now()}")
        logger.info("=" * 50)
    
    def inicializar(self, loading_screen=None) -> bool:
        """
        Executa todas as verificações e inicializações necessárias.
        
        Args:
            loading_screen: Instância do ecrã de loading (opcional)
        
        Returns:
            bool: True se a inicialização foi bem-sucedida
        """
        logger.info("🚀 Iniciando Aplicação de Gestão de Apostas Desportivas v2.0")
        
        if loading_screen:
            loading_screen.update_progress(5, "Registando informações do sistema...")
            time.sleep(0.2)
        
        self.log_system_info()
        
        # Sequência de verificações com progresso
        checks = [
            ("Versão do Python", self.verificar_python_version, 15, "Verificando versão do Python..."),
            ("Dependências", self.verificar_dependencias, 35, "Carregando dependências..."),
            ("Arquivos necessários", self.verificar_arquivos, 55, "Verificando base de dados..."),
            ("Diretórios", self.criar_diretorios, 70, "Criando estrutura de pastas..."),
            ("Configurações", self.verificar_configuracoes, 85, "Carregando configurações...")
        ]
        
        for check_name, check_func, progress, status in checks:
            if loading_screen:
                loading_screen.update_progress(progress, status)
                time.sleep(0.3)
            
            logger.info(f"🔍 Verificando: {check_name}")
            if not check_func():
                logger.error(f"❌ Falha na verificação: {check_name}")
                return False
            logger.info(f"✅ {check_name} - OK")
        
        if loading_screen:
            loading_screen.update_progress(95, "Finalizando inicialização...")
            time.sleep(0.2)
        
        logger.info("✅ Todas as verificações passaram!")
        return True
    
    def inicializar_modulos_v2(self) -> None:
        """
        Inicializa os módulos da Versão 2.0 se disponíveis.
        """
        try:
            # Inicializar sistema de usuários
            if (self.app_dir / 'usuarios.py').exists():
                logger.info("🔧 Inicializando sistema de usuários...")
                from usuarios import gestor_utilizadores
                gestor_utilizadores.inicializar_base_dados()
                logger.info("✅ Sistema de usuários inicializado")
            
            # Sistema de gamificação removido
            
            # Verificar disponibilidade da API mobile
            if (self.app_dir / 'api_mobile.py').exists():
                logger.info("📱 API Mobile disponível")
            
            # Verificar disponibilidade do ML
            if (self.app_dir / 'ml_previsoes.py').exists():
                logger.info("🤖 Sistema de ML disponível")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar módulos v2.0: {e}")
            # Não é crítico, continuar execução
    
    def executar_aplicacao(self) -> None:
        """
        Executa a aplicação principal.
        """
        try:
            logger.info("🎯 Carregando interface principal...")
            
            # Inicializar módulos da Versão 2.0
            self.inicializar_modulos_v2()
            
            # Importar e executar a interface
            from interface import ApostasApp
            
            logger.info("✅ Interface carregada com sucesso")
            logger.info("🎉 Aplicação iniciada!")
            
            # Criar e executar a aplicação
            app = ApostasApp()
            app.run()
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar aplicação: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

def main() -> int:
    """
    Função principal de entrada da aplicação.
    
    Returns:
        int: Código de saída (0 = sucesso, 1 = erro)
    """
    loading_screen = None
    
    try:
        # Criar e mostrar ecrã de loading
        loading_screen = LoadingScreen()
        if loading_screen.show():
            loading_screen.update_progress(5, "Inicializando sistema...")
            time.sleep(0.3)
        else:
            loading_screen = None
        
        # Criar inicializador
        if loading_screen:
            loading_screen.update_progress(15, "Verificando dependências...")
            time.sleep(0.2)
        
        initializer = AppInitializer()
        
        # Executar inicialização com loading screen
        if not initializer.inicializar(loading_screen):
            if loading_screen:
                loading_screen.close()
            logger.error("❌ Falha na inicialização da aplicação")
            safe_input("Pressione Enter para sair...")
            return 1
        
        # Carregar módulos
        if loading_screen:
            loading_screen.update_progress(85, "Carregando módulos...")
            time.sleep(0.3)
        
        # Preparar interface
        if loading_screen:
            loading_screen.update_progress(95, "Preparando interface...")
            time.sleep(0.2)
        
        # Finalizar loading screen
        if loading_screen:
            loading_screen.update_progress(100, "Carregamento concluído!")
            time.sleep(0.5)
            loading_screen.close()
        
        # Executar aplicação
        initializer.executar_aplicacao()
        
        logger.info("👋 Aplicação encerrada normalmente")
        return 0
        
    except KeyboardInterrupt:
        if loading_screen:
            loading_screen.close()
        logger.info("⚠️ Aplicação interrompida pelo usuário")
        return 0
    except Exception as e:
        if loading_screen:
            loading_screen.close()
        logger.error(f"💥 Erro crítico: {e}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        safe_input("Pressione Enter para sair...")
        return 1

if __name__ == "__main__":
    # Configurar encoding para Windows
    if sys.platform.startswith('win'):
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
            except locale.Error:
                pass  # Usar configuração padrão
    
    # Executar aplicação
    exit_code = main()
    sys.exit(exit_code)