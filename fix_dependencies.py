#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Corrigir Dependências e Problemas Comuns
Resolve problemas específicos que podem causar falhas na compilação
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

class FixDependencies:
    def __init__(self):
        self.projeto_dir = Path.cwd()
        
    def verificar_python_version(self):
        """Verifica se a versão do Python é compatível"""
        print("🐍 Verificando versão do Python...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatível")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Incompatível")
            print("Requer Python 3.8 ou superior")
            return False
    
    def instalar_dependencias_criticas(self):
        """Instala/atualiza dependências críticas"""
        print("📦 Instalando/atualizando dependências críticas...")
        
        dependencias = [
            'pyinstaller>=5.0',
            'customtkinter>=5.0.0',
            'pandas>=1.5.0',
            'matplotlib>=3.5.0',
            'numpy>=1.21.0',
            'pillow>=9.0.0',
            'cryptography>=3.4.0',
            'seaborn>=0.11.0',
            'plotly>=5.0.0',
            'reportlab>=3.6.0',
            'psutil>=5.8.0',
            'pywin32>=227'
        ]
        
        for dep in dependencias:
            try:
                print(f"📥 Instalando {dep}...")
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '--upgrade', dep],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ {dep} instalado com sucesso")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Erro ao instalar {dep}: {e}")
                print(f"Saída: {e.stdout}")
                print(f"Erro: {e.stderr}")
        
        return True
    
    def corrigir_imports_problematicos(self):
        """Corrige imports que podem causar problemas na compilação"""
        print("🔧 Verificando imports problemáticos...")
        
        # Lista de arquivos Python no projeto
        arquivos_python = list(self.projeto_dir.glob('*.py'))
        
        imports_problematicos = {
            'from collections import': 'from collections.abc import',
            'import imp': '# import imp  # Deprecated',
            'from imp import': '# from imp import  # Deprecated'
        }
        
        arquivos_modificados = []
        
        for arquivo in arquivos_python:
            if arquivo.name.startswith('compile') or arquivo.name.startswith('fix'):
                continue
                
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                conteudo_original = conteudo
                
                for import_antigo, import_novo in imports_problematicos.items():
                    if import_antigo in conteudo:
                        conteudo = conteudo.replace(import_antigo, import_novo)
                        print(f"🔄 Corrigido import em {arquivo.name}")
                
                if conteudo != conteudo_original:
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    arquivos_modificados.append(arquivo.name)
                    
            except Exception as e:
                print(f"⚠️ Erro ao processar {arquivo.name}: {e}")
        
        if arquivos_modificados:
            print(f"✅ Imports corrigidos em: {', '.join(arquivos_modificados)}")
        else:
            print("✅ Nenhum import problemático encontrado")
        
        return True
    
    def criar_hook_customizado(self):
        """Cria hooks customizados para resolver problemas específicos"""
        print("🪝 Criando hooks customizados...")
        
        hooks_dir = self.projeto_dir / 'hooks'
        hooks_dir.mkdir(exist_ok=True)
        
        # Hook para customtkinter
        hook_customtkinter = '''
# Hook para customtkinter
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('customtkinter')
hiddenimports = collect_submodules('customtkinter')
'''
        
        # Hook para matplotlib
        hook_matplotlib = '''
# Hook para matplotlib
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('matplotlib')
hiddenimports = collect_submodules('matplotlib')
hiddenimports += ['matplotlib.backends.backend_tkagg']
'''
        
        hooks = {
            'hook-customtkinter.py': hook_customtkinter,
            'hook-matplotlib.py': hook_matplotlib
        }
        
        for nome_hook, conteudo_hook in hooks.items():
            try:
                hook_path = hooks_dir / nome_hook
                with open(hook_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo_hook)
                print(f"✅ Hook criado: {nome_hook}")
            except Exception as e:
                print(f"❌ Erro ao criar hook {nome_hook}: {e}")
        
        return True
    
    def verificar_arquivos_essenciais(self):
        """Verifica se todos os arquivos essenciais estão presentes"""
        print("📁 Verificando arquivos essenciais...")
        
        arquivos_essenciais = [
            'run_app.py',
            'interface.py',
            'apostas.db',
            'icon.ico'
        ]
        
        diretorios_essenciais = [
            'config',
            'data',
            'logs',
            'exports',
            'backups',
            'temas',
            'traducoes'
        ]
        
        todos_presentes = True
        
        for arquivo in arquivos_essenciais:
            arquivo_path = self.projeto_dir / arquivo
            if arquivo_path.exists():
                print(f"✅ {arquivo} - Encontrado")
            else:
                print(f"❌ {arquivo} - FALTANDO")
                todos_presentes = False
        
        for diretorio in diretorios_essenciais:
            dir_path = self.projeto_dir / diretorio
            if dir_path.exists():
                print(f"✅ {diretorio}/ - Encontrado")
            else:
                print(f"⚠️ {diretorio}/ - Criando...")
                dir_path.mkdir(exist_ok=True)
        
        return todos_presentes
    
    def otimizar_requirements(self):
        """Otimiza o arquivo requirements.txt"""
        print("📋 Otimizando requirements.txt...")
        
        requirements_otimizado = '''
# Dependências principais
customtkinter>=5.0.0
pandas>=1.5.0
matplotlib>=3.5.0
numpy>=1.21.0
Pillow>=9.0.0
cryptography>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0
reportlab>=3.6.0
psutil>=5.8.0

# Dependências Windows
pywin32>=227; sys_platform == "win32"

# Dependências de compilação
pyinstaller>=5.0

# Dependências opcionais
scikit-learn>=1.0.0
requests>=2.25.0
flask>=2.0.0
'''
        
        try:
            requirements_path = self.projeto_dir / 'requirements.txt'
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_otimizado)
            print("✅ requirements.txt otimizado")
            return True
        except Exception as e:
            print(f"❌ Erro ao otimizar requirements.txt: {e}")
            return False
    
    def executar_correcoes(self):
        """Executa todas as correções"""
        print("🔧 Iniciando Correções de Dependências e Problemas")
        print("=" * 60)
        
        etapas = [
            ("Verificar versão Python", self.verificar_python_version),
            ("Verificar arquivos essenciais", self.verificar_arquivos_essenciais),
            ("Otimizar requirements.txt", self.otimizar_requirements),
            ("Instalar dependências críticas", self.instalar_dependencias_criticas),
            ("Corrigir imports problemáticos", self.corrigir_imports_problematicos),
            ("Criar hooks customizados", self.criar_hook_customizado)
        ]
        
        sucesso_total = True
        
        for nome_etapa, funcao_etapa in etapas:
            print(f"\n🔄 {nome_etapa}...")
            try:
                if funcao_etapa():
                    print(f"✅ {nome_etapa} - Concluída")
                else:
                    print(f"⚠️ {nome_etapa} - Concluída com avisos")
            except Exception as e:
                print(f"❌ {nome_etapa} - Falhou: {e}")
                sucesso_total = False
        
        if sucesso_total:
            print("\n🎉 Todas as correções foram aplicadas com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Execute: python compile_melhorado.py")
            print("2. Teste o executável gerado")
        else:
            print("\n⚠️ Algumas correções falharam. Verifique os erros acima.")
        
        return sucesso_total

if __name__ == "__main__":
    fixer = FixDependencies()
    fixer.executar_correcoes()