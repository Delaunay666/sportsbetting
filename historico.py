#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Histórico de Apostas
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date
from typing import Dict, List, Optional
from main import DatabaseManager, Aposta

class HistoricoFrame(ctk.CTkScrollableFrame):
    """Frame para exibir e gerir o histórico de apostas"""
    
    def __init__(self, parent, db: DatabaseManager, update_callback=None):
        super().__init__(parent)
        self.db = db
        self.update_callback = update_callback
        self.apostas = []
        self.create_widgets()
        self.load_apostas()
    
    def create_widgets(self):
        """Criar widgets do histórico"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="📋 Histórico de Apostas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame de filtros
        self.create_filters_frame()
        
        # Frame da tabela
        self.create_table_frame()
        
        # Frame de ações
        self.create_actions_frame()
    
    def create_filters_frame(self):
        """Criar frame de filtros"""
        filters_frame = ctk.CTkFrame(self)
        filters_frame.pack(fill="x", padx=20, pady=10)
        
        # Título dos filtros
        ctk.CTkLabel(
            filters_frame,
            text="🔍 Filtros",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Filtro por competição
        ctk.CTkLabel(filters_frame, text="Competição:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.competicao_filter = ctk.CTkComboBox(
            filters_frame,
            values=["Todas", "Premier League", "La Liga", "Serie A", "Bundesliga", "Liga Portugal"],
            command=self.apply_filters
        )
        self.competicao_filter.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.competicao_filter.set("Todas")
        
        # Filtro por resultado
        ctk.CTkLabel(filters_frame, text="Resultado:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.resultado_filter = ctk.CTkComboBox(
            filters_frame,
            values=["Todos", "Pendente", "Ganha", "Perdida", "Anulada"],
            command=self.apply_filters
        )
        self.resultado_filter.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        self.resultado_filter.set("Todos")
        
        # Filtro por equipa
        ctk.CTkLabel(filters_frame, text="Equipa:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.equipa_filter = ctk.CTkEntry(filters_frame, placeholder_text="Nome da equipa")
        self.equipa_filter.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.equipa_filter.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Botão limpar filtros
        clear_btn = ctk.CTkButton(
            filters_frame,
            text="🗑️ Limpar",
            command=self.clear_filters,
            width=100
        )
        clear_btn.grid(row=2, column=3, padx=10, pady=5)
        
        # Configurar grid
        filters_frame.grid_columnconfigure((1, 3), weight=1)
    
    def create_table_frame(self):
        """Criar frame da tabela"""
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Criar Treeview para a tabela
        columns = ("ID", "Data", "Competição", "Jogo", "Tipo", "Odd", "Valor", "Resultado", "Lucro")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configurar colunas
        column_widths = {"ID": 50, "Data": 120, "Competição": 120, "Jogo": 200, 
                        "Tipo": 100, "Odd": 60, "Valor": 80, "Resultado": 80, "Lucro": 80}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind eventos
        self.tree.bind("<Double-1>", self.on_item_double_click)
    
    def create_actions_frame(self):
        """Criar frame de ações"""
        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        # Botões de ação
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Editar Selecionada",
            command=self.edit_selected,
            height=35
        )
        edit_btn.pack(side="left", padx=10, pady=10)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Eliminar Selecionada",
            command=self.delete_selected,
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        delete_btn.pack(side="left", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Atualizar",
            command=self.load_apostas,
            height=35
        )
        refresh_btn.pack(side="right", padx=10, pady=10)
        
        # Estatísticas rápidas
        self.stats_label = ctk.CTkLabel(
            actions_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.stats_label.pack(side="right", padx=20, pady=10)
    
    def load_apostas(self):
        """Carregar apostas da base de dados"""
        try:
            self.apostas = self.db.get_apostas()
            self.update_table()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar apostas: {str(e)}")
    
    def update_table(self, apostas=None):
        """Atualizar tabela com apostas"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Usar apostas filtradas ou todas
        apostas_to_show = apostas if apostas is not None else self.apostas
        
        # Adicionar apostas à tabela
        for aposta in apostas_to_show:
            jogo = f"{aposta.equipa_casa} vs {aposta.equipa_fora}"
            lucro_str = f"€{aposta.lucro_prejuizo:.2f}" if aposta.resultado != "Pendente" else "-"
            
            # Cores baseadas no resultado
            tags = []
            if aposta.resultado == "Ganha":
                tags = ["ganha"]
            elif aposta.resultado == "Perdida":
                tags = ["perdida"]
            elif aposta.resultado == "Anulada":
                tags = ["anulada"]
            
            self.tree.insert("", "end", values=(
                aposta.id,
                aposta.data_hora,
                aposta.competicao,
                jogo,
                aposta.tipo_aposta,
                f"{aposta.odd:.2f}",
                f"€{aposta.valor_apostado:.2f}",
                aposta.resultado,
                lucro_str
            ), tags=tags)
        
        # Configurar cores das tags
        self.tree.tag_configure("ganha", background="#d4edda")
        self.tree.tag_configure("perdida", background="#f8d7da")
        self.tree.tag_configure("anulada", background="#fff3cd")
    
    def update_stats(self):
        """Atualizar estatísticas rápidas"""
        if not self.apostas:
            self.stats_label.configure(text="Nenhuma aposta encontrada")
            return
        
        total = len(self.apostas)
        pendentes = len([a for a in self.apostas if a.resultado == "Pendente"])
        ganhas = len([a for a in self.apostas if a.resultado == "Ganha"])
        perdidas = len([a for a in self.apostas if a.resultado == "Perdida"])
        
        stats_text = f"Total: {total} | Pendentes: {pendentes} | Ganhas: {ganhas} | Perdidas: {perdidas}"
        self.stats_label.configure(text=stats_text)
    
    def apply_filters(self):
        """Aplicar filtros às apostas"""
        filtros = {}
        
        # Filtro por competição
        if self.competicao_filter.get() != "Todas":
            filtros["competicao"] = self.competicao_filter.get()
        
        # Filtro por resultado
        if self.resultado_filter.get() != "Todos":
            filtros["resultado"] = self.resultado_filter.get()
        
        # Filtro por equipa
        if self.equipa_filter.get().strip():
            filtros["equipa"] = self.equipa_filter.get().strip()
        
        # Aplicar filtros
        try:
            apostas_filtradas = self.db.get_apostas(filtros)
            self.update_table(apostas_filtradas)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar filtros: {str(e)}")
    
    def clear_filters(self):
        """Limpar todos os filtros"""
        self.competicao_filter.set("Todas")
        self.resultado_filter.set("Todos")
        self.equipa_filter.delete(0, "end")
        self.load_apostas()
    
    def on_item_double_click(self, event):
        """Evento de duplo clique no item"""
        self.edit_selected()
    
    def edit_selected(self):
        """Editar aposta selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma aposta para editar.")
            return
        
        item = self.tree.item(selection[0])
        aposta_id = item["values"][0]
        
        # Encontrar aposta
        aposta = next((a for a in self.apostas if a.id == aposta_id), None)
        if not aposta:
            messagebox.showerror("Erro", "Aposta não encontrada.")
            return
        
        # Abrir janela de edição
        self.open_edit_window(aposta)
    
    def delete_selected(self):
        """Eliminar aposta selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma aposta para eliminar.")
            return
        
        item = self.tree.item(selection[0])
        aposta_id = item["values"][0]
        
        # Confirmar eliminação
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja eliminar a aposta #{aposta_id}?"):
            try:
                # Eliminar aposta da base de dados
                self.db.eliminar_aposta(aposta_id)
                messagebox.showinfo("Sucesso", "Aposta eliminada com sucesso!")
                self.load_apostas()
                if self.update_callback:
                    self.update_callback()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao eliminar aposta: {str(e)}")
    
    def open_edit_window(self, aposta: Aposta):
        """Abrir janela de edição de aposta"""
        edit_window = ctk.CTkToplevel(self)
        edit_window.title(f"Editar Aposta #{aposta.id}")
        edit_window.geometry("500x600")
        edit_window.transient(self)
        edit_window.grab_set()
        
        # Título
        title = ctk.CTkLabel(
            edit_window,
            text=f"✏️ Editar Aposta #{aposta.id}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(edit_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Campos não editáveis (apenas para visualização)
        ctk.CTkLabel(form_frame, text="Jogo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        jogo_label = ctk.CTkLabel(form_frame, text=f"{aposta.equipa_casa} vs {aposta.equipa_fora}")
        jogo_label.pack(anchor="w", padx=20)
        
        ctk.CTkLabel(form_frame, text="Valor Apostado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        valor_label = ctk.CTkLabel(form_frame, text=f"€{aposta.valor_apostado:.2f}")
        valor_label.pack(anchor="w", padx=20)
        
        ctk.CTkLabel(form_frame, text="Odd:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        odd_label = ctk.CTkLabel(form_frame, text=f"{aposta.odd:.2f}")
        odd_label.pack(anchor="w", padx=20)
        
        # Campo editável: Resultado
        ctk.CTkLabel(form_frame, text="Resultado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        resultado_combo = ctk.CTkComboBox(
            form_frame,
            values=["Pendente", "Ganha", "Perdida", "Anulada"],
            width=200
        )
        resultado_combo.pack(anchor="w", padx=20, pady=5)
        resultado_combo.set(aposta.resultado)
        
        # Campo para lucro/prejuízo (calculado automaticamente)
        ctk.CTkLabel(form_frame, text="Lucro/Prejuízo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        lucro_entry = ctk.CTkEntry(form_frame, width=200)
        lucro_entry.pack(anchor="w", padx=20, pady=5)
        
        def calcular_lucro():
            """Calcular lucro baseado no resultado"""
            resultado = resultado_combo.get()
            if resultado == "Ganha":
                lucro = aposta.valor_apostado * (aposta.odd - 1)
                lucro_entry.delete(0, "end")
                lucro_entry.insert(0, f"{lucro:.2f}")
            elif resultado == "Perdida":
                lucro_entry.delete(0, "end")
                lucro_entry.insert(0, f"{-aposta.valor_apostado:.2f}")
            elif resultado == "Anulada":
                lucro_entry.delete(0, "end")
                lucro_entry.insert(0, "0.00")
            else:  # Pendente
                lucro_entry.delete(0, "end")
                lucro_entry.insert(0, "0.00")
        
        # Calcular lucro inicial
        calcular_lucro()
        
        # Bind para recalcular quando resultado muda
        resultado_combo.configure(command=lambda x: calcular_lucro())
        
        # Botões
        buttons_frame = ctk.CTkFrame(edit_window)
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        def save_changes():
            """Guardar alterações"""
            try:
                novo_resultado = resultado_combo.get()
                novo_lucro = float(lucro_entry.get())
                
                # Atualizar na base de dados
                self.db.atualizar_resultado_aposta(aposta.id, novo_resultado, novo_lucro)
                
                messagebox.showinfo("Sucesso", "Aposta atualizada com sucesso!")
                edit_window.destroy()
                self.load_apostas()
                
                # Callback para atualizar outras partes da interface
                if self.update_callback:
                    self.update_callback()
                    
            except ValueError:
                messagebox.showerror("Erro", "Valor de lucro/prejuízo inválido.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar aposta: {str(e)}")
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Guardar",
            command=save_changes,
            fg_color="#28a745",
            hover_color="#218838"
        )
        save_btn.pack(side="left", padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancelar",
            command=edit_window.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(side="right", padx=10, pady=10)