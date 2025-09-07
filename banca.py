#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestão de Banca
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Dict, List, Optional
from main import DatabaseManager

class BancaFrame(ctk.CTkScrollableFrame):
    """Frame para gestão da banca"""
    
    def __init__(self, parent, db: DatabaseManager, update_callback=None):
        super().__init__(parent)
        self.db = db
        self.update_callback = update_callback
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Criar widgets da gestão de banca"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="💰 Gestão de Banca",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame de informações atuais
        self.create_current_info_frame()
        
        # Frame de movimentos
        self.create_movements_frame()
        
        # Frame de histórico
        self.create_history_frame()
        
        # Frame de gráfico
        self.create_chart_frame()
    
    def create_current_info_frame(self):
        """Criar frame de informações atuais"""
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="📊 Informações Atuais",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Grid de informações
        info_grid = ctk.CTkFrame(info_frame)
        info_grid.pack(fill="x", padx=20, pady=10)
        
        # Configurar grid
        for i in range(3):
            info_grid.grid_columnconfigure(i, weight=1)
        
        # Saldo atual
        saldo_card = ctk.CTkFrame(info_grid)
        saldo_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            saldo_card,
            text="💰 Saldo Atual",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.saldo_atual_label = ctk.CTkLabel(
            saldo_card,
            text="€0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00ff88"
        )
        self.saldo_atual_label.pack(pady=(0, 10))
        
        # Saldo inicial
        inicial_card = ctk.CTkFrame(info_grid)
        inicial_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            inicial_card,
            text="🏁 Saldo Inicial",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.saldo_inicial_label = ctk.CTkLabel(
            inicial_card,
            text="€0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffc107"
        )
        self.saldo_inicial_label.pack(pady=(0, 10))
        
        # Variação
        variacao_card = ctk.CTkFrame(info_grid)
        variacao_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            variacao_card,
            text="📈 Variação",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.variacao_label = ctk.CTkLabel(
            variacao_card,
            text="€0.00 (0%)",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#17a2b8"
        )
        self.variacao_label.pack(pady=(0, 10))
    
    def create_movements_frame(self):
        """Criar frame de movimentos"""
        movements_frame = ctk.CTkFrame(self)
        movements_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            movements_frame,
            text="💸 Adicionar Movimento",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Formulário de movimento
        form_frame = ctk.CTkFrame(movements_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Tipo de movimento
        ctk.CTkLabel(
            form_frame,
            text="Tipo de Movimento:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.tipo_movimento_combo = ctk.CTkComboBox(
            form_frame,
            values=["Depósito", "Levantamento", "Bónus", "Ajuste"],
            width=200
        )
        self.tipo_movimento_combo.grid(row=0, column=1, sticky="w", padx=20, pady=10)
        
        # Valor
        ctk.CTkLabel(
            form_frame,
            text="Valor (€):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        
        self.valor_movimento_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 100.00",
            width=200
        )
        self.valor_movimento_entry.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        
        # Descrição
        ctk.CTkLabel(
            form_frame,
            text="Descrição:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        
        self.descricao_movimento_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Descrição do movimento",
            width=300
        )
        self.descricao_movimento_entry.grid(row=2, column=1, sticky="w", padx=20, pady=10)
        
        # Botão adicionar
        add_btn = ctk.CTkButton(
            form_frame,
            text="➕ Adicionar Movimento",
            command=self.adicionar_movimento,
            height=35,
            fg_color="#28a745",
            hover_color="#218838"
        )
        add_btn.grid(row=3, column=1, sticky="w", padx=20, pady=20)
    
    def create_history_frame(self):
        """Criar frame de histórico"""
        history_frame = ctk.CTkFrame(self)
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            history_frame,
            text="📋 Histórico de Movimentos",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Criar Treeview para o histórico
        columns = ("ID", "Data", "Tipo", "Valor", "Saldo", "Descrição")
        
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Configurar colunas
        column_widths = {"ID": 0, "Data": 150, "Tipo": 100, "Valor": 100, "Saldo": 100, "Descrição": 300}
        
        for col in columns:
            if col == "ID":
                # Ocultar coluna ID
                self.history_tree.heading(col, text="")
                self.history_tree.column(col, width=0, minwidth=0, stretch=False)
            else:
                self.history_tree.heading(col, text=col)
                self.history_tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack widgets
        self.history_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        v_scrollbar.pack(side="right", fill="y", pady=10)
        
        # Botões de ação do histórico
        history_buttons_frame = ctk.CTkFrame(history_frame)
        history_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            history_buttons_frame,
            text="🗑️ Apagar Movimento",
            command=self.apagar_movimento_selecionado,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            history_buttons_frame,
            text="🔄 Atualizar",
            command=self.load_data,
            width=100
        ).pack(side="left", padx=5)
    
    def create_chart_frame(self):
        """Criar frame do gráfico"""
        chart_frame = ctk.CTkFrame(self)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            chart_frame,
            text="📈 Evolução da Banca",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Configurar matplotlib para tema escuro
        plt.style.use('dark_background')
        
        self.chart_fig = Figure(figsize=(12, 6), facecolor='#2b2b2b')
        self.chart_canvas = FigureCanvasTkAgg(self.chart_fig, chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_data(self):
        """Carregar dados da banca"""
        try:
            # Carregar saldo atual
            saldo_atual = self.db.get_saldo_atual()
            self.saldo_atual_label.configure(text=f"€{saldo_atual:.2f}")
            
            # Atualizar cor do saldo
            if saldo_atual >= 0:
                self.saldo_atual_label.configure(text_color="#00ff88")
            else:
                self.saldo_atual_label.configure(text_color="#ff4444")
            
            # Carregar saldo inicial
            saldo_inicial_str = self.db.get_configuracao("saldo_inicial")
            saldo_inicial = float(saldo_inicial_str) if saldo_inicial_str else 0.0
            self.saldo_inicial_label.configure(text=f"€{saldo_inicial:.2f}")
            
            # Calcular variação
            variacao = saldo_atual - saldo_inicial
            variacao_percent = (variacao / saldo_inicial * 100) if saldo_inicial > 0 else 0
            
            variacao_text = f"€{variacao:.2f} ({variacao_percent:+.1f}%)"
            self.variacao_label.configure(text=variacao_text)
            
            # Atualizar cor da variação
            if variacao >= 0:
                self.variacao_label.configure(text_color="#00ff88")
            else:
                self.variacao_label.configure(text_color="#ff4444")
            
            # Carregar histórico
            self.load_history()
            
            # Atualizar gráfico
            self.update_chart()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados da banca: {str(e)}")
    
    def load_history(self):
        """Carregar histórico de movimentos"""
        # Limpar árvore
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            # Obter histórico da base de dados
            conn = self.db.db_path
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, data, saldo, movimento, descricao
                FROM historico_banca
                ORDER BY created_at DESC
                LIMIT 50
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                movimento_id, data, saldo, movimento, descricao = row
                
                # Determinar tipo de movimento
                if "Saldo inicial" in descricao:
                    tipo = "Inicial"
                elif "Aposta #" in descricao and movimento < 0:
                    tipo = "Aposta"
                elif "ganha #" in descricao:
                    tipo = "Ganho"
                elif "anulada #" in descricao:
                    tipo = "Anulada"
                elif movimento > 0:
                    tipo = "Depósito"
                else:
                    tipo = "Levantamento"
                
                # Formatear valores
                valor_str = f"€{movimento:+.2f}"
                saldo_str = f"€{saldo:.2f}"
                
                # Cores baseadas no tipo de movimento
                tags = []
                if movimento > 0:
                    tags = ["positivo"]
                elif movimento < 0:
                    tags = ["negativo"]
                
                # Inserir com ID como primeiro valor (oculto)
                self.history_tree.insert("", "end", values=(
                    movimento_id, data, tipo, valor_str, saldo_str, descricao
                ), tags=tags)
            
            # Configurar cores das tags
            self.history_tree.tag_configure("positivo", background="#d4edda")
            self.history_tree.tag_configure("negativo", background="#f8d7da")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar histórico: {str(e)}")
    
    def apagar_movimento_selecionado(self):
        """Apagar movimento selecionado do histórico"""
        selection = self.history_tree.selection()
        
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um movimento para apagar.")
            return
        
        # Obter dados do movimento selecionado
        item = selection[0]
        values = self.history_tree.item(item, 'values')
        movimento_id = values[0]
        descricao = values[5]
        
        # Verificar se é movimento inicial
        if "Saldo inicial" in descricao:
            messagebox.showwarning("Aviso", "Não é possível apagar o movimento de saldo inicial.")
            return
        
        # Confirmar exclusão
        if messagebox.askyesno("Confirmar Exclusão", 
                             f"Tem certeza que deseja apagar este movimento?\n\n"
                             f"Descrição: {descricao}\n\n"
                             f"ATENÇÃO: Esta ação irá recalcular todos os saldos subsequentes."):
            
            try:
                self.apagar_movimento_e_recalcular(movimento_id)
                messagebox.showinfo("Sucesso", "Movimento apagado e saldos recalculados com sucesso!")
                
                # Recarregar dados
                self.load_data()
                
                if self.update_callback:
                    self.update_callback()
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao apagar movimento: {str(e)}")
    
    def apagar_movimento_e_recalcular(self, movimento_id):
        """Apagar movimento e recalcular saldos subsequentes"""
        import sqlite3
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Obter dados do movimento a ser apagado
            cursor.execute("""
                SELECT created_at, movimento FROM historico_banca 
                WHERE id = ?
            """, (movimento_id,))
            
            movimento_data = cursor.fetchone()
            if not movimento_data:
                raise Exception("Movimento não encontrado")
            
            created_at, valor_movimento = movimento_data
            
            # Apagar o movimento
            cursor.execute("DELETE FROM historico_banca WHERE id = ?", (movimento_id,))
            
            # Obter todos os movimentos posteriores para recalcular
            cursor.execute("""
                SELECT id, movimento FROM historico_banca 
                WHERE created_at > ?
                ORDER BY created_at ASC
            """, (created_at,))
            
            movimentos_posteriores = cursor.fetchall()
            
            # Recalcular saldos dos movimentos posteriores
            for mov_id, _ in movimentos_posteriores:
                # Obter saldo anterior
                cursor.execute("""
                    SELECT saldo FROM historico_banca 
                    WHERE created_at < (SELECT created_at FROM historico_banca WHERE id = ?)
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (mov_id,))
                
                saldo_anterior_result = cursor.fetchone()
                saldo_anterior = saldo_anterior_result[0] if saldo_anterior_result else 0.0
                
                # Obter movimento atual
                cursor.execute("""
                    SELECT movimento FROM historico_banca WHERE id = ?
                """, (mov_id,))
                
                movimento_atual = cursor.fetchone()[0]
                novo_saldo = saldo_anterior + movimento_atual
                
                # Atualizar saldo
                cursor.execute("""
                    UPDATE historico_banca SET saldo = ? WHERE id = ?
                """, (novo_saldo, mov_id))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_chart(self):
        """Atualizar gráfico de evolução"""
        self.chart_fig.clear()
        ax = self.chart_fig.add_subplot(111)
        
        try:
            # Obter dados do histórico
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data, saldo
                FROM historico_banca
                ORDER BY created_at ASC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                datas = []
                saldos = []
                
                for row in rows:
                    data_str, saldo = row
                    try:
                        data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                        datas.append(data)
                        saldos.append(saldo)
                    except:
                        continue
                
                if datas and saldos:
                    # Plotar linha principal
                    ax.plot(datas, saldos, linewidth=2, color='#00ff88', marker='o', markersize=3)
                    
                    # Linha do saldo inicial
                    saldo_inicial_str = self.db.get_configuracao("saldo_inicial")
                    saldo_inicial = float(saldo_inicial_str) if saldo_inicial_str else 0.0
                    ax.axhline(y=saldo_inicial, color='#ffc107', linestyle='--', alpha=0.7, label='Saldo Inicial')
                    
                    # Configurar gráfico
                    ax.set_title('Evolução da Banca ao Longo do Tempo', fontsize=14, fontweight='bold', color='white')
                    ax.set_xlabel('Data', color='white')
                    ax.set_ylabel('Saldo (€)', color='white')
                    ax.grid(True, alpha=0.3, color='white')
                    
                    # Configurar cores dos ticks e labels
                    ax.tick_params(axis='x', colors='white')
                    ax.tick_params(axis='y', colors='white')
                    ax.spines['bottom'].set_color('white')
                    ax.spines['top'].set_color('white')
                    ax.spines['right'].set_color('white')
                    ax.spines['left'].set_color('white')
                    
                    # Configurar legenda com cores claras
                    legend = ax.legend()
                    legend.get_frame().set_facecolor('#2b2b2b')
                    for text in legend.get_texts():
                        text.set_color('white')
                    
                    # Formatar eixo x
                    self.chart_fig.autofmt_xdate()
                    
                    # Área de lucro/prejuízo
                    ax.fill_between(datas, saldos, saldo_inicial, 
                                   where=[s >= saldo_inicial for s in saldos],
                                   color='#00ff88', alpha=0.2, label='Lucro')
                    ax.fill_between(datas, saldos, saldo_inicial,
                                   where=[s < saldo_inicial for s in saldos],
                                   color='#ff4444', alpha=0.2, label='Prejuízo')
            else:
                ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', 
                       transform=ax.transAxes, color='white', fontsize=14)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Erro ao carregar gráfico: {str(e)}', ha='center', va='center',
                   transform=ax.transAxes, color='red', fontsize=12)
        
        self.chart_canvas.draw()
    
    def adicionar_movimento(self):
        """Adicionar novo movimento à banca"""
        try:
            # Validar campos
            tipo = self.tipo_movimento_combo.get()
            valor_str = self.valor_movimento_entry.get()
            descricao = self.descricao_movimento_entry.get()
            
            if not all([tipo, valor_str, descricao]):
                messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
                return
            
            # Validar valor
            try:
                valor = float(valor_str)
                if valor <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número positivo.")
                return
            
            # Ajustar sinal baseado no tipo
            if tipo in ["Levantamento"]:
                valor = -valor
            
            # Verificar se há saldo suficiente para levantamentos
            if valor < 0:
                saldo_atual = self.db.get_saldo_atual()
                if abs(valor) > saldo_atual:
                    messagebox.showerror("Erro", f"Saldo insuficiente. Saldo atual: €{saldo_atual:.2f}")
                    return
            
            # Adicionar movimento
            descricao_completa = f"{tipo}: {descricao}"
            self.db.adicionar_movimento_banca(valor, descricao_completa)
            
            # Limpar formulário
            self.tipo_movimento_combo.set("")
            self.valor_movimento_entry.delete(0, "end")
            self.descricao_movimento_entry.delete(0, "end")
            
            # Atualizar interface
            self.load_data()
            
            # Callback para atualizar outras partes da interface
            if self.update_callback:
                self.update_callback()
            
            messagebox.showinfo("Sucesso", "Movimento adicionado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar movimento: {str(e)}")
    
    def configurar_saldo_inicial(self):
        """Configurar saldo inicial"""
        dialog = ctk.CTkInputDialog(
            text="Insira o novo saldo inicial (€):",
            title="Configurar Saldo Inicial"
        )
        
        novo_saldo = dialog.get_input()
        
        if novo_saldo:
            try:
                valor = float(novo_saldo)
                if valor < 0:
                    messagebox.showerror("Erro", "Saldo inicial não pode ser negativo.")
                    return
                
                # Confirmar alteração
                if messagebox.askyesno("Confirmar", 
                                     f"Tem certeza que deseja alterar o saldo inicial para €{valor:.2f}?\n\n"
                                     "ATENÇÃO: Esta ação irá afetar todos os cálculos de ROI e variação."):
                    
                    self.db.set_configuracao("saldo_inicial", str(valor))
                    self.load_data()
                    
                    if self.update_callback:
                        self.update_callback()
                    
                    messagebox.showinfo("Sucesso", "Saldo inicial atualizado com sucesso!")
                
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido. Insira um número válido.")