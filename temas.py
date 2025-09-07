#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestão de Temas Visuais
Versão 1.1 - Sistema de Apostas Desportivas

Este módulo é responsável pela gestão de temas visuais,
incluindo modo escuro, personalização de cores e estilos.
"""

import os
import json
import customtkinter as ctk
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import tkinter as tk
from tkinter import colorchooser, messagebox

class TipoTema(Enum):
    """Tipos de tema disponíveis."""
    CLARO = "light"
    ESCURO = "dark"
    PERSONALIZADO = "custom"

@dataclass
class ConfiguracaoTema:
    """Configuração de um tema visual."""
    nome: str
    tipo: TipoTema
    cores_primarias: Dict[str, str]
    cores_secundarias: Dict[str, str]
    cores_texto: Dict[str, str]
    cores_botoes: Dict[str, str]
    cores_graficos: List[str]
    fonte_principal: str
    tamanho_fonte: int
    espacamento: int

class GestorTemas:
    """Classe responsável pela gestão de temas visuais."""
    
    def __init__(self):
        self.config_path = "config_temas.json"
        self.temas_path = "temas"
        self.tema_atual = None
        self.configuracoes = {}
        self._criar_diretorios()
        self._carregar_temas_padrao()
        self._carregar_configuracoes()
        
        # Aplicar tema automaticamente na inicialização
        self._aplicar_tema_inicial()
    
    def _criar_diretorios(self):
        """Cria diretórios necessários para temas."""
        os.makedirs(self.temas_path, exist_ok=True)
    
    def _carregar_temas_padrao(self):
        """Carrega temas padrão do sistema."""
        # Tema Claro Padrão
        self.tema_claro = ConfiguracaoTema(
            nome="Claro Padrão",
            tipo=TipoTema.CLARO,
            cores_primarias={
                "fundo_principal": "#FFFFFF",
                "fundo_secundario": "#F0F0F0",
                "fundo_sidebar": "#E8E8E8",
                "fundo_cards": "#FAFAFA",
                "bordas": "#CCCCCC"
            },
            cores_secundarias={
                "destaque": "#007ACC",
                "sucesso": "#28A745",
                "aviso": "#FFC107",
                "erro": "#DC3545",
                "info": "#17A2B8"
            },
            cores_texto={
                "primario": "#212529",
                "secundario": "#6C757D",
                "destaque": "#007ACC",
                "inverso": "#FFFFFF"
            },
            cores_botoes={
                "primario": "#007ACC",
                "primario_hover": "#0056A3",
                "secundario": "#6C757D",
                "secundario_hover": "#545B62",
                "sucesso": "#28A745",
                "sucesso_hover": "#1E7E34",
                "perigo": "#DC3545",
                "perigo_hover": "#C82333"
            },
            cores_graficos=[
                "#007ACC", "#28A745", "#FFC107", "#DC3545", "#17A2B8",
                "#6F42C1", "#E83E8C", "#20C997", "#FD7E14", "#6C757D"
            ],
            fonte_principal="Segoe UI",
            tamanho_fonte=12,
            espacamento=10
        )
        
        # Tema Escuro Padrão
        self.tema_escuro = ConfiguracaoTema(
            nome="Escuro Padrão",
            tipo=TipoTema.ESCURO,
            cores_primarias={
                "fundo_principal": "#1E1E1E",
                "fundo_secundario": "#2D2D2D",
                "fundo_sidebar": "#252526",
                "fundo_cards": "#2D2D2D",
                "bordas": "#3E3E42"
            },
            cores_secundarias={
                "destaque": "#0078D4",
                "sucesso": "#107C10",
                "aviso": "#FFB900",
                "erro": "#D13438",
                "info": "#00BCF2"
            },
            cores_texto={
                "primario": "#FFFFFF",
                "secundario": "#CCCCCC",
                "destaque": "#0078D4",
                "inverso": "#000000"
            },
            cores_botoes={
                "primario": "#0078D4",
                "primario_hover": "#106EBE",
                "secundario": "#8A8886",
                "secundario_hover": "#605E5C",
                "sucesso": "#107C10",
                "sucesso_hover": "#0E6B0E",
                "perigo": "#D13438",
                "perigo_hover": "#A4262C"
            },
            cores_graficos=[
                "#0078D4", "#107C10", "#FFB900", "#D13438", "#00BCF2",
                "#8764B8", "#E3008C", "#00CC6A", "#FF8C00", "#8A8886"
            ],
            fonte_principal="Segoe UI",
            tamanho_fonte=12,
            espacamento=10
        )
        
        # Tema Azul Profissional
        self.tema_azul = ConfiguracaoTema(
            nome="Azul Profissional",
            tipo=TipoTema.PERSONALIZADO,
            cores_primarias={
                "fundo_principal": "#F8F9FA",
                "fundo_secundario": "#E9ECEF",
                "fundo_sidebar": "#1F3A93",
                "fundo_cards": "#FFFFFF",
                "bordas": "#DEE2E6"
            },
            cores_secundarias={
                "destaque": "#1F3A93",
                "sucesso": "#28A745",
                "aviso": "#FFC107",
                "erro": "#DC3545",
                "info": "#17A2B8"
            },
            cores_texto={
                "primario": "#212529",
                "secundario": "#6C757D",
                "destaque": "#1F3A93",
                "inverso": "#FFFFFF"
            },
            cores_botoes={
                "primario": "#1F3A93",
                "primario_hover": "#162D75",
                "secundario": "#6C757D",
                "secundario_hover": "#545B62",
                "sucesso": "#28A745",
                "sucesso_hover": "#1E7E34",
                "perigo": "#DC3545",
                "perigo_hover": "#C82333"
            },
            cores_graficos=[
                "#1F3A93", "#28A745", "#FFC107", "#DC3545", "#17A2B8",
                "#6F42C1", "#E83E8C", "#20C997", "#FD7E14", "#495057"
            ],
            fonte_principal="Segoe UI",
            tamanho_fonte=12,
            espacamento=12
        )
        
        # Tema Verde Natureza
        self.tema_verde = ConfiguracaoTema(
            nome="Verde Natureza",
            tipo=TipoTema.PERSONALIZADO,
            cores_primarias={
                "fundo_principal": "#F8FFF8",
                "fundo_secundario": "#E8F5E8",
                "fundo_sidebar": "#2E7D32",
                "fundo_cards": "#FFFFFF",
                "bordas": "#C8E6C9"
            },
            cores_secundarias={
                "destaque": "#2E7D32",
                "sucesso": "#4CAF50",
                "aviso": "#FF9800",
                "erro": "#F44336",
                "info": "#2196F3"
            },
            cores_texto={
                "primario": "#1B5E20",
                "secundario": "#388E3C",
                "destaque": "#2E7D32",
                "inverso": "#FFFFFF"
            },
            cores_botoes={
                "primario": "#2E7D32",
                "primario_hover": "#1B5E20",
                "secundario": "#66BB6A",
                "secundario_hover": "#4CAF50",
                "sucesso": "#4CAF50",
                "sucesso_hover": "#388E3C",
                "perigo": "#F44336",
                "perigo_hover": "#D32F2F"
            },
            cores_graficos=[
                "#2E7D32", "#4CAF50", "#8BC34A", "#CDDC39", "#FFC107",
                "#FF9800", "#FF5722", "#795548", "#607D8B", "#9E9E9E"
            ],
            fonte_principal="Segoe UI",
            tamanho_fonte=12,
            espacamento=10
        )
    
    def _carregar_configuracoes(self):
        """Carrega configurações salvas de temas."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.configuracoes = json.load(f)
            else:
                self.configuracoes = {
                    "tema_atual": "Claro Padrão",
                    "temas_personalizados": {},
                    "preferencias": {
                        "aplicar_automaticamente": True,
                        "salvar_preferencias": True
                    }
                }
                self._salvar_configuracoes()
        except Exception as e:
            print(f"Erro ao carregar configurações de temas: {e}")
            self.configuracoes = {"tema_atual": "Claro Padrão", "temas_personalizados": {}, "preferencias": {}}
    
    def _salvar_configuracoes(self):
        """Salva configurações de temas."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.configuracoes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações de temas: {e}")
    
    def _aplicar_tema_inicial(self):
        """Aplica o tema configurado na inicialização."""
        try:
            nome_tema = self.configuracoes.get("tema_atual", "Claro Padrão")
            print(f"🎨 Aplicando tema inicial: {nome_tema}")
            
            tema = self.obter_tema(nome_tema)
            if tema:
                # Configurar CustomTkinter
                if tema.tipo == TipoTema.ESCURO:
                    ctk.set_appearance_mode("dark")
                    print("🌙 Modo escuro aplicado")
                else:
                    ctk.set_appearance_mode("light")
                    print("☀️ Modo claro aplicado")
                
                self.tema_atual = tema
                print(f"✅ Tema '{nome_tema}' aplicado com sucesso")
            else:
                print(f"❌ Tema '{nome_tema}' não encontrado, usando padrão")
                ctk.set_appearance_mode("light")
                
        except Exception as e:
            print(f"❌ Erro ao aplicar tema inicial: {e}")
            ctk.set_appearance_mode("light")
    
    def obter_temas_disponiveis(self) -> List[str]:
        """Retorna lista de temas disponíveis."""
        temas_padrao = ["Claro Padrão", "Escuro Padrão", "Azul Profissional", "Verde Natureza"]
        temas_personalizados = list(self.configuracoes.get("temas_personalizados", {}).keys())
        return temas_padrao + temas_personalizados
    
    def obter_tema(self, nome_tema: str) -> Optional[ConfiguracaoTema]:
        """Obtém configuração de um tema específico."""
        # Verificar temas padrão
        if nome_tema == "Claro Padrão":
            return self.tema_claro
        elif nome_tema == "Escuro Padrão":
            return self.tema_escuro
        elif nome_tema == "Azul Profissional":
            return self.tema_azul
        elif nome_tema == "Verde Natureza":
            return self.tema_verde
        
        # Verificar temas personalizados
        temas_personalizados = self.configuracoes.get("temas_personalizados", {})
        if nome_tema in temas_personalizados:
            config_dict = temas_personalizados[nome_tema]
            return ConfiguracaoTema(**config_dict)
        
        return None
    
    def aplicar_tema(self, nome_tema: str) -> bool:
        """Aplica um tema ao sistema."""
        try:
            tema = self.obter_tema(nome_tema)
            if not tema:
                return False
            
            # Configurar CustomTkinter
            if tema.tipo == TipoTema.ESCURO:
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
            
            # Definir tema de cores personalizado
            self._aplicar_cores_customtkinter(tema)
            
            # Salvar tema atual
            self.configuracoes["tema_atual"] = nome_tema
            self.tema_atual = tema
            self._salvar_configuracoes()
            
            return True
            
        except Exception as e:
            print(f"Erro ao aplicar tema: {e}")
            return False
    
    def aplicar_tema_por_nome(self, nome_tema: str) -> bool:
        """Aplica um tema específico pelo nome (alias para aplicar_tema)."""
        return self.aplicar_tema(nome_tema)
    
    def _aplicar_cores_customtkinter(self, tema: ConfiguracaoTema):
        """Aplica cores personalizadas ao CustomTkinter."""
        try:
            # Criar dicionário de cores para CustomTkinter
            cores_ctk = {
                "CTkFrame": {
                    "fg_color": [tema.cores_primarias["fundo_cards"], tema.cores_primarias["fundo_secundario"]],
                    "border_color": [tema.cores_primarias["bordas"], tema.cores_primarias["bordas"]]
                },
                "CTkButton": {
                    "fg_color": [tema.cores_botoes["primario"], tema.cores_botoes["primario"]],
                    "hover_color": [tema.cores_botoes["primario_hover"], tema.cores_botoes["primario_hover"]],
                    "text_color": [tema.cores_texto["inverso"], tema.cores_texto["inverso"]]
                },
                "CTkEntry": {
                    "fg_color": [tema.cores_primarias["fundo_cards"], tema.cores_primarias["fundo_secundario"]],
                    "border_color": [tema.cores_primarias["bordas"], tema.cores_primarias["bordas"]],
                    "text_color": [tema.cores_texto["primario"], tema.cores_texto["primario"]]
                },
                "CTkLabel": {
                    "text_color": [tema.cores_texto["primario"], tema.cores_texto["primario"]]
                }
            }
            
            # Aplicar configurações (CustomTkinter não suporta temas dinâmicos completos)
            # Esta é uma implementação básica - seria necessário reiniciar a interface
            
        except Exception as e:
            print(f"Erro ao aplicar cores CustomTkinter: {e}")
    
    def criar_tema_personalizado(self, nome: str, base_tema: str = "Claro Padrão") -> ConfiguracaoTema:
        """Cria um novo tema personalizado baseado em um tema existente."""
        tema_base = self.obter_tema(base_tema)
        if not tema_base:
            tema_base = self.tema_claro
        
        # Criar cópia do tema base
        novo_tema = ConfiguracaoTema(
            nome=nome,
            tipo=TipoTema.PERSONALIZADO,
            cores_primarias=tema_base.cores_primarias.copy(),
            cores_secundarias=tema_base.cores_secundarias.copy(),
            cores_texto=tema_base.cores_texto.copy(),
            cores_botoes=tema_base.cores_botoes.copy(),
            cores_graficos=tema_base.cores_graficos.copy(),
            fonte_principal=tema_base.fonte_principal,
            tamanho_fonte=tema_base.tamanho_fonte,
            espacamento=tema_base.espacamento
        )
        
        return novo_tema
    
    def salvar_tema_personalizado(self, tema: ConfiguracaoTema) -> bool:
        """Salva um tema personalizado."""
        try:
            if "temas_personalizados" not in self.configuracoes:
                self.configuracoes["temas_personalizados"] = {}
            
            # Converter tema para dicionário
            tema_dict = {
                "nome": tema.nome,
                "tipo": tema.tipo.value,
                "cores_primarias": tema.cores_primarias,
                "cores_secundarias": tema.cores_secundarias,
                "cores_texto": tema.cores_texto,
                "cores_botoes": tema.cores_botoes,
                "cores_graficos": tema.cores_graficos,
                "fonte_principal": tema.fonte_principal,
                "tamanho_fonte": tema.tamanho_fonte,
                "espacamento": tema.espacamento
            }
            
            self.configuracoes["temas_personalizados"][tema.nome] = tema_dict
            self._salvar_configuracoes()
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar tema personalizado: {e}")
            return False
    
    def excluir_tema_personalizado(self, nome_tema: str) -> bool:
        """Exclui um tema personalizado."""
        try:
            if nome_tema in self.configuracoes.get("temas_personalizados", {}):
                del self.configuracoes["temas_personalizados"][nome_tema]
                self._salvar_configuracoes()
                return True
            return False
        except Exception as e:
            print(f"Erro ao excluir tema: {e}")
            return False
    
    def obter_tema_atual(self) -> Optional[ConfiguracaoTema]:
        """Retorna o tema atualmente aplicado."""
        if self.tema_atual:
            return self.tema_atual
        
        nome_tema_atual = self.configuracoes.get("tema_atual", "Claro Padrão")
        return self.obter_tema(nome_tema_atual)
    
    def exportar_tema(self, nome_tema: str, caminho_arquivo: str) -> bool:
        """Exporta um tema para arquivo JSON."""
        try:
            tema = self.obter_tema(nome_tema)
            if not tema:
                return False
            
            tema_dict = {
                "nome": tema.nome,
                "tipo": tema.tipo.value,
                "cores_primarias": tema.cores_primarias,
                "cores_secundarias": tema.cores_secundarias,
                "cores_texto": tema.cores_texto,
                "cores_botoes": tema.cores_botoes,
                "cores_graficos": tema.cores_graficos,
                "fonte_principal": tema.fonte_principal,
                "tamanho_fonte": tema.tamanho_fonte,
                "espacamento": tema.espacamento,
                "versao": "1.1",
                "data_exportacao": "2024-08-25"
            }
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(tema_dict, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao exportar tema: {e}")
            return False
    
    def importar_tema(self, caminho_arquivo: str) -> bool:
        """Importa um tema de arquivo JSON."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                tema_dict = json.load(f)
            
            # Validar estrutura do tema
            campos_obrigatorios = ['nome', 'cores_primarias', 'cores_secundarias', 
                                 'cores_texto', 'cores_botoes', 'cores_graficos']
            
            for campo in campos_obrigatorios:
                if campo not in tema_dict:
                    raise ValueError(f"Campo obrigatório ausente: {campo}")
            
            # Criar objeto ConfiguracaoTema
            tema = ConfiguracaoTema(
                nome=tema_dict['nome'],
                tipo=TipoTema(tema_dict.get('tipo', 'custom')),
                cores_primarias=tema_dict['cores_primarias'],
                cores_secundarias=tema_dict['cores_secundarias'],
                cores_texto=tema_dict['cores_texto'],
                cores_botoes=tema_dict['cores_botoes'],
                cores_graficos=tema_dict['cores_graficos'],
                fonte_principal=tema_dict.get('fonte_principal', 'Segoe UI'),
                tamanho_fonte=tema_dict.get('tamanho_fonte', 12),
                espacamento=tema_dict.get('espacamento', 10)
            )
            
            # Salvar tema
            return self.salvar_tema_personalizado(tema)
            
        except Exception as e:
            print(f"Erro ao importar tema: {e}")
            return False
    
    def obter_cores_para_graficos(self) -> List[str]:
        """Retorna cores do tema atual para uso em gráficos."""
        tema_atual = self.obter_tema_atual()
        if tema_atual:
            return tema_atual.cores_graficos
        return self.tema_claro.cores_graficos
    
    def obter_cor_por_categoria(self, categoria: str, subcategoria: str = "primario") -> str:
        """Obtém cor específica do tema atual."""
        tema_atual = self.obter_tema_atual()
        if not tema_atual:
            tema_atual = self.tema_claro
        
        if categoria == "primarias":
            return tema_atual.cores_primarias.get(subcategoria, "#FFFFFF")
        elif categoria == "secundarias":
            return tema_atual.cores_secundarias.get(subcategoria, "#007ACC")
        elif categoria == "texto":
            return tema_atual.cores_texto.get(subcategoria, "#000000")
        elif categoria == "botoes":
            return tema_atual.cores_botoes.get(subcategoria, "#007ACC")
        
        return "#000000"

class EditorTemas:
    """Interface para edição de temas."""
    
    def __init__(self, gestor_temas: GestorTemas):
        self.gestor = gestor_temas
        self.tema_editando = None
        self.janela = None
    
    def abrir_editor(self, tema_base: str = "Claro Padrão"):
        """Abre interface de edição de temas."""
        self.tema_editando = self.gestor.criar_tema_personalizado("Novo Tema", tema_base)
        
        self.janela = ctk.CTkToplevel()
        self.janela.title("Editor de Temas")
        self.janela.geometry("800x600")
        
        self._criar_interface_editor()
    
    def _criar_interface_editor(self):
        """Cria interface do editor de temas."""
        # Frame principal
        main_frame = ctk.CTkFrame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Nome do tema
        nome_frame = ctk.CTkFrame(main_frame)
        nome_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(nome_frame, text="Nome do Tema:").pack(side="left", padx=5)
        self.entry_nome = ctk.CTkEntry(nome_frame, placeholder_text="Digite o nome do tema")
        self.entry_nome.pack(side="left", fill="x", expand=True, padx=5)
        
        # Notebook para categorias
        notebook = ctk.CTkTabview(main_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba Cores Primárias
        tab_primarias = notebook.add("Cores Primárias")
        self._criar_secao_cores(tab_primarias, "primarias")
        
        # Aba Cores Secundárias
        tab_secundarias = notebook.add("Cores Secundárias")
        self._criar_secao_cores(tab_secundarias, "secundarias")
        
        # Aba Cores de Texto
        tab_texto = notebook.add("Cores de Texto")
        self._criar_secao_cores(tab_texto, "texto")
        
        # Aba Cores de Botões
        tab_botoes = notebook.add("Cores de Botões")
        self._criar_secao_cores(tab_botoes, "botoes")
        
        # Botões de ação
        botoes_frame = ctk.CTkFrame(main_frame)
        botoes_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(botoes_frame, text="Salvar Tema", 
                     command=self._salvar_tema).pack(side="left", padx=5)
        ctk.CTkButton(botoes_frame, text="Aplicar Tema", 
                     command=self._aplicar_tema).pack(side="left", padx=5)
        ctk.CTkButton(botoes_frame, text="Cancelar", 
                     command=self.janela.destroy).pack(side="right", padx=5)
    
    def _criar_secao_cores(self, parent, categoria):
        """Cria seção de edição de cores."""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Obter cores da categoria
        if categoria == "primarias":
            cores = self.tema_editando.cores_primarias
        elif categoria == "secundarias":
            cores = self.tema_editando.cores_secundarias
        elif categoria == "texto":
            cores = self.tema_editando.cores_texto
        elif categoria == "botoes":
            cores = self.tema_editando.cores_botoes
        
        # Criar controles para cada cor
        for nome_cor, valor_cor in cores.items():
            cor_frame = ctk.CTkFrame(frame)
            cor_frame.pack(fill="x", padx=5, pady=2)
            
            # Label da cor
            ctk.CTkLabel(cor_frame, text=nome_cor.replace("_", " ").title()).pack(side="left", padx=5)
            
            # Entry para valor da cor
            entry_cor = ctk.CTkEntry(cor_frame, width=100)
            entry_cor.insert(0, valor_cor)
            entry_cor.pack(side="left", padx=5)
            
            # Botão para escolher cor
            def escolher_cor(entry=entry_cor):
                cor = colorchooser.askcolor(color=entry.get())[1]
                if cor:
                    entry.delete(0, tk.END)
                    entry.insert(0, cor)
            
            ctk.CTkButton(cor_frame, text="Escolher", width=80, 
                         command=escolher_cor).pack(side="left", padx=5)
    
    def _salvar_tema(self):
        """Salva o tema editado."""
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Digite um nome para o tema")
            return
        
        self.tema_editando.nome = nome
        
        if self.gestor.salvar_tema_personalizado(self.tema_editando):
            messagebox.showinfo("Sucesso", "Tema salvo com sucesso!")
            self.janela.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao salvar tema")
    
    def _aplicar_tema(self):
        """Aplica o tema sendo editado."""
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Digite um nome para o tema")
            return
        
        self.tema_editando.nome = nome
        
        if self.gestor.salvar_tema_personalizado(self.tema_editando):
            if self.gestor.aplicar_tema(nome):
                messagebox.showinfo("Sucesso", "Tema aplicado com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao aplicar tema")
        else:
            messagebox.showerror("Erro", "Erro ao salvar tema")

# Funções de conveniência
def inicializar_temas() -> GestorTemas:
    """Inicializa sistema de temas."""
    return GestorTemas()

def aplicar_tema_padrao(modo: str = "light") -> bool:
    """Aplica tema padrão (light ou dark)."""
    gestor = GestorTemas()
    if modo == "dark":
        return gestor.aplicar_tema("Escuro Padrão")
    else:
        return gestor.aplicar_tema("Claro Padrão")

def obter_cores_tema_atual() -> Dict[str, str]:
    """Obtém cores do tema atual para uso em componentes."""
    gestor = GestorTemas()
    tema = gestor.obter_tema_atual()
    
    if tema:
        cores = {}
        cores.update(tema.cores_primarias)
        cores.update(tema.cores_secundarias)
        cores.update(tema.cores_texto)
        cores.update(tema.cores_botoes)
        return cores
    
    return {}

if __name__ == "__main__":
    # Teste do módulo
    try:
        gestor = GestorTemas()
        
        print("Temas disponíveis:")
        for tema in gestor.obter_temas_disponiveis():
            print(f"- {tema}")
        
        # Teste de aplicação de tema
        print("\nAplicando tema escuro...")
        if gestor.aplicar_tema("Escuro Padrão"):
            print("Tema escuro aplicado com sucesso")
        
        # Teste de criação de tema personalizado
        print("\nCriando tema personalizado...")
        tema_custom = gestor.criar_tema_personalizado("Meu Tema", "Azul Profissional")
        tema_custom.cores_primarias["fundo_principal"] = "#F0F8FF"
        
        if gestor.salvar_tema_personalizado(tema_custom):
            print("Tema personalizado salvo com sucesso")
        
        print("\nCores para gráficos:", gestor.obter_cores_para_graficos())
        
    except Exception as e:
        print(f"Erro no teste: {e}")