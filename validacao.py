#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Validação e Autocompletar
Melhorias na entrada e validação de dados
"""

import re
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import sqlite3
from main import DatabaseManager

class DataValidator:
    """Classe para validação de dados de apostas"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.equipas_cache = set()
        self.competicoes_cache = set()
        self.load_cache()
    
    def load_cache(self):
        """Carregar cache de equipas e competições existentes"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Carregar equipas únicas
            cursor.execute("SELECT DISTINCT equipa_casa FROM apostas")
            equipas_casa = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT equipa_fora FROM apostas")
            equipas_fora = [row[0] for row in cursor.fetchall()]
            
            self.equipas_cache = set(equipas_casa + equipas_fora)
            
            # Carregar competições únicas
            cursor.execute("SELECT DISTINCT competicao FROM apostas")
            competicoes = [row[0] for row in cursor.fetchall()]
            self.competicoes_cache = set(competicoes)
            
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
    
    def validate_data_hora(self, data_hora: str) -> Tuple[bool, str]:
        """Validar formato de data e hora"""
        try:
            # Tentar diferentes formatos
            formatos = [
                "%d/%m/%Y %H:%M",
                "%Y-%m-%d %H:%M",
                "%d-%m-%Y %H:%M",
                "%d/%m/%Y"
            ]
            
            for formato in formatos:
                try:
                    dt = datetime.strptime(data_hora, formato)
                    # Verificar se a data não é muito antiga ou muito futura
                    hoje = datetime.now()
                    if dt.year < 2020 or dt.year > hoje.year + 2:
                        return False, "Data deve estar entre 2020 e dois anos no futuro"
                    return True, "Data válida"
                except ValueError:
                    continue
            
            return False, "Formato de data inválido. Use: DD/MM/AAAA HH:MM"
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"
    
    def validate_odd(self, odd: str) -> Tuple[bool, str, float]:
        """Validar odd"""
        try:
            odd_float = float(odd.replace(',', '.'))
            
            if odd_float <= 1.0:
                return False, "Odd deve ser maior que 1.0", 0.0
            
            if odd_float > 1000:
                return False, "Odd muito alta (máximo 1000)", 0.0
            
            return True, "Odd válida", odd_float
        except ValueError:
            return False, "Odd deve ser um número válido", 0.0
    
    def validate_valor(self, valor: str) -> Tuple[bool, str, float]:
        """Validar valor apostado"""
        try:
            valor_float = float(valor.replace(',', '.'))
            
            if valor_float <= 0:
                return False, "Valor deve ser maior que zero", 0.0
            
            if valor_float > 10000:
                return False, "Valor muito alto (máximo €10.000)", 0.0
            
            return True, "Valor válido", valor_float
        except ValueError:
            return False, "Valor deve ser um número válido", 0.0
    
    def validate_equipa(self, equipa: str) -> Tuple[bool, str]:
        """Validar nome da equipa"""
        if not equipa or len(equipa.strip()) < 2:
            return False, "Nome da equipa deve ter pelo menos 2 caracteres"
        
        # Verificar caracteres especiais problemáticos
        if re.search(r'[<>"\'\/\\]', equipa):
            return False, "Nome da equipa contém caracteres inválidos"
        
        return True, "Nome válido"
    
    def validate_competicao(self, competicao: str) -> Tuple[bool, str]:
        """Validar competição"""
        if not competicao or len(competicao.strip()) < 2:
            return False, "Nome da competição deve ter pelo menos 2 caracteres"
        
        return True, "Competição válida"
    
    def validate_tipo_aposta(self, tipo_aposta: str) -> Tuple[bool, str]:
        """Validar tipo de aposta"""
        tipos_validos = [
            "1X2", "Over/Under Golos", "Over/Under Cantos", 
            "Handicap Asiático", "Ambas Marcam", "Dupla Hipótese", 
            "Resultado Exato", "Outros"
        ]
        
        if not tipo_aposta or tipo_aposta.strip() == "":
            return False, "Tipo de aposta é obrigatório"
        
        if tipo_aposta not in tipos_validos:
            return False, f"Tipo de aposta inválido. Tipos válidos: {', '.join(tipos_validos)}"
        
        return True, "Tipo de aposta válido"
    
    def check_duplicate(self, data_hora: str, equipa_casa: str, equipa_fora: str, tipo_aposta: str) -> Tuple[bool, str]:
        """Verificar se a aposta já existe"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM apostas 
                WHERE data_hora = ? AND equipa_casa = ? AND equipa_fora = ? AND tipo_aposta = ?
            """, (data_hora, equipa_casa, equipa_fora, tipo_aposta))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, f"Aposta duplicada encontrada (ID: {result[0]})"
            
            return False, "Aposta única"
        except Exception as e:
            return False, f"Erro ao verificar duplicata: {str(e)}"

class AutoCompleter:
    """Classe para autocompletar dados"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.equipas = []
        self.competicoes = []
        self.load_suggestions()
    
    def load_suggestions(self):
        """Carregar sugestões de autocompletar"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Equipas mais frequentes
            cursor.execute("""
                SELECT equipa, COUNT(*) as freq FROM (
                    SELECT equipa_casa as equipa FROM apostas
                    UNION ALL
                    SELECT equipa_fora as equipa FROM apostas
                ) GROUP BY equipa ORDER BY freq DESC
            """)
            
            self.equipas = [row[0] for row in cursor.fetchall()]
            
            # Competições mais frequentes
            cursor.execute("""
                SELECT competicao, COUNT(*) as freq FROM apostas 
                GROUP BY competicao ORDER BY freq DESC
            """)
            
            self.competicoes = [row[0] for row in cursor.fetchall()]
            
            # Adicionar competições padrão se não existirem
            competicoes_padrao = [
                "Premier League", "La Liga", "Serie A", "Bundesliga",
                "Liga Portugal", "Champions League", "Europa League",
                "Ligue 1", "Eredivisie", "Liga NOS"
            ]
            
            for comp in competicoes_padrao:
                if comp not in self.competicoes:
                    self.competicoes.append(comp)
            
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar sugestões: {e}")
    
    def get_equipa_suggestions(self, text: str, limit: int = 10) -> List[str]:
        """Obter sugestões de equipas"""
        if not text:
            return self.equipas[:limit]
        
        text_lower = text.lower()
        suggestions = []
        
        # Correspondências exatas no início
        for equipa in self.equipas:
            if equipa.lower().startswith(text_lower):
                suggestions.append(equipa)
                if len(suggestions) >= limit:
                    break
        
        # Correspondências parciais
        if len(suggestions) < limit:
            for equipa in self.equipas:
                if text_lower in equipa.lower() and equipa not in suggestions:
                    suggestions.append(equipa)
                    if len(suggestions) >= limit:
                        break
        
        return suggestions
    
    def get_competicao_suggestions(self, text: str, limit: int = 10) -> List[str]:
        """Obter sugestões de competições"""
        if not text:
            return self.competicoes[:limit]
        
        text_lower = text.lower()
        suggestions = []
        
        # Correspondências exatas no início
        for comp in self.competicoes:
            if comp.lower().startswith(text_lower):
                suggestions.append(comp)
                if len(suggestions) >= limit:
                    break
        
        # Correspondências parciais
        if len(suggestions) < limit:
            for comp in self.competicoes:
                if text_lower in comp.lower() and comp not in suggestions:
                    suggestions.append(comp)
                    if len(suggestions) >= limit:
                        break
        
        return suggestions
    
    def add_equipa(self, equipa: str):
        """Adicionar nova equipa às sugestões"""
        if equipa and equipa not in self.equipas:
            self.equipas.insert(0, equipa)
    
    def add_competicao(self, competicao: str):
        """Adicionar nova competição às sugestões"""
        if competicao and competicao not in self.competicoes:
            self.competicoes.insert(0, competicao)

class SmartEntry:
    """Widget de entrada inteligente com validação e autocompletar"""
    
    def __init__(self, parent, validator: DataValidator, autocompleter: AutoCompleter = None, entry_type: str = "text", **kwargs):
        import customtkinter as ctk
        
        self.parent = parent
        self.validator = validator
        self.autocompleter = autocompleter
        self.entry_type = entry_type
        
        # Criar o frame principal
        self.frame = ctk.CTkFrame(parent)
        
        # Criar a entrada
        self.entry = ctk.CTkEntry(self.frame, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Label de status
        self.status_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            width=20,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right", padx=(5, 0))
        
        # Configurar validação
        self.setup_validation()
        
        # Configurar autocompletar se disponível
        if self.autocompleter and entry_type in ["team", "competition"]:
            self.setup_autocomplete()
    
    def setup_validation(self):
        """Configurar validação em tempo real"""
        def validate(*args):
            value = self.entry.get()
            if not value:
                self.status_label.configure(text="", text_color="gray")
                return
            
            valid, msg = True, ""
            
            if self.entry_type == "team":
                valid, msg = self.validator.validate_equipa(value)
            elif self.entry_type == "competition":
                valid, msg = self.validator.validate_competicao(value)
            elif self.entry_type == "odd":
                valid, msg, _ = self.validator.validate_odd(value)
            elif self.entry_type == "value":
                valid, msg, _ = self.validator.validate_valor(value)
            elif self.entry_type == "datetime":
                valid, msg = self.validator.validate_data_hora(value)
            
            if valid:
                self.status_label.configure(text="✓", text_color="green")
            else:
                self.status_label.configure(text="✗", text_color="red")
        
        self.entry.bind("<KeyRelease>", validate)
        self.entry.bind("<FocusOut>", validate)
    
    def setup_autocomplete(self):
        """Configurar autocompletar"""
        import tkinter as tk
        
        # Frame para sugestões
        self.suggestions_frame = None
        self.suggestions_listbox = None
        
        def show_suggestions(*args):
            text = self.entry.get()
            
            if self.entry_type == "team":
                suggestions = self.autocompleter.get_equipa_suggestions(text)
            elif self.entry_type == "competition":
                suggestions = self.autocompleter.get_competicao_suggestions(text)
            else:
                suggestions = []
            
            if suggestions and len(text) > 0:
                if not self.suggestions_frame:
                    self.create_suggestions_widget()
                
                self.suggestions_listbox.delete(0, "end")
                for suggestion in suggestions:
                    self.suggestions_listbox.insert("end", suggestion)
                
                self.suggestions_frame.pack(fill="x", pady=(2, 0))
            else:
                self.hide_suggestions()
        
        def on_suggestion_select(event):
            if self.suggestions_listbox:
                selection = self.suggestions_listbox.curselection()
                if selection:
                    value = self.suggestions_listbox.get(selection[0])
                    self.entry.delete(0, "end")
                    self.entry.insert(0, value)
                    self.hide_suggestions()
        
        self.entry.bind("<KeyRelease>", show_suggestions)
        
        if hasattr(self, 'suggestions_listbox') and self.suggestions_listbox:
            self.suggestions_listbox.bind("<Double-Button-1>", on_suggestion_select)
    
    def create_suggestions_widget(self):
        """Criar widget de sugestões"""
        import tkinter as tk
        import customtkinter as ctk
        
        self.suggestions_frame = ctk.CTkFrame(self.frame)
        self.suggestions_listbox = tk.Listbox(
            self.suggestions_frame,
            height=5,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f538d",
            font=("Arial", 10)
        )
        self.suggestions_listbox.pack(fill="both", expand=True)
    
    def hide_suggestions(self):
        """Ocultar sugestões"""
        if self.suggestions_frame:
            self.suggestions_frame.pack_forget()
    
    def get(self):
        """Obter valor da entrada"""
        return self.entry.get()
    
    def set(self, value):
        """Definir valor da entrada"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    
    def grid(self, **kwargs):
        """Posicionar o widget"""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Posicionar o widget"""
        self.frame.pack(**kwargs)

# Funções utilitárias
def format_currency(value: float) -> str:
    """Formatar valor como moeda"""
    return f"€{value:,.2f}".replace(',', ' ').replace('.', ',')

def parse_currency(text: str) -> float:
    """Converter texto de moeda para float"""
    # Remover símbolos e converter
    clean_text = re.sub(r'[€\s]', '', text)
    clean_text = clean_text.replace(',', '.')
    return float(clean_text)

def calculate_implied_probability(odd: float) -> float:
    """Calcular probabilidade implícita da odd"""
    return (1 / odd) * 100

def calculate_expected_value(odd: float, probability: float, stake: float) -> float:
    """Calcular valor esperado da aposta"""
    return (probability / 100) * (odd - 1) * stake - ((100 - probability) / 100) * stake

def calculate_kelly_criterion(odd: float, probability: float) -> float:
    """Calcular critério de Kelly para otimização de stake"""
    if probability <= 0 or probability >= 100:
        return 0
    
    p = probability / 100
    q = 1 - p
    b = odd - 1
    
    kelly = (b * p - q) / b
    return max(0, kelly)  # Não apostar se Kelly for negativo