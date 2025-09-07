#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programa de Registo de Apostas Desportivas
Versão: 1.0
Autor: Sistema de Gestão de Apostas
Descrição: Aplicação completa para gestão e análise de apostas de futebol
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date
import sqlite3
import json
import os
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from dataclasses import dataclass
import threading
import requests
from pathlib import Path

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

@dataclass
class Aposta:
    """Classe para representar uma aposta"""
    id: Optional[int] = None
    data_hora: str = ""
    competicao: str = ""
    equipa_casa: str = ""
    equipa_fora: str = ""
    tipo_aposta: str = ""
    odd: float = 0.0
    valor_apostado: float = 0.0
    resultado: str = "Pendente"  # Ganha, Perdida, Anulada, Pendente
    lucro_prejuizo: float = 0.0
    notas: str = ""

class DatabaseManager:
    """Gestor da base de dados SQLite"""
    
    def __init__(self, db_path: str = "apostas.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa a base de dados com as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de apostas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL,
                competicao TEXT NOT NULL,
                equipa_casa TEXT NOT NULL,
                equipa_fora TEXT NOT NULL,
                tipo_aposta TEXT NOT NULL,
                odd REAL NOT NULL,
                valor_apostado REAL NOT NULL,
                resultado TEXT DEFAULT 'Pendente',
                lucro_prejuizo REAL DEFAULT 0.0,
                notas TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de banca
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_banca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                saldo REAL NOT NULL,
                movimento REAL NOT NULL,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Configurar saldo inicial se não existir
        self.init_saldo_inicial()
    
    def init_saldo_inicial(self):
        """Inicializa o saldo inicial se não existir"""
        saldo = self.get_configuracao("saldo_inicial")
        if saldo is None:
            self.set_configuracao("saldo_inicial", "0.0")
            # Não adiciona movimento inicial quando saldo é 0
    
    def get_configuracao(self, chave: str) -> Optional[str]:
        """Obtém uma configuração da base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def set_configuracao(self, chave: str, valor: str):
        """Define uma configuração na base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO configuracoes (chave, valor, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (chave, valor))
        conn.commit()
        conn.close()
    
    def adicionar_aposta(self, aposta: Aposta) -> int:
        """Adiciona uma nova aposta à base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO apostas (data_hora, competicao, equipa_casa, equipa_fora,
                               tipo_aposta, odd, valor_apostado, resultado,
                               lucro_prejuizo, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (aposta.data_hora, aposta.competicao, aposta.equipa_casa,
              aposta.equipa_fora, aposta.tipo_aposta, aposta.odd,
              aposta.valor_apostado, aposta.resultado, aposta.lucro_prejuizo,
              aposta.notas))
        
        aposta_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Atualizar banca
        self.adicionar_movimento_banca(-aposta.valor_apostado, f"Aposta #{aposta_id}")
        
        return aposta_id
    
    def atualizar_resultado_aposta(self, aposta_id: int, resultado: str, lucro_prejuizo: float):
        """Atualiza o resultado de uma aposta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obter aposta atual
        cursor.execute("SELECT valor_apostado, resultado, lucro_prejuizo FROM apostas WHERE id = ?", (aposta_id,))
        aposta_atual = cursor.fetchone()
        
        if aposta_atual:
            valor_apostado, resultado_anterior, lucro_anterior = aposta_atual
            
            # Atualizar aposta
            cursor.execute("""
                UPDATE apostas SET resultado = ?, lucro_prejuizo = ?
                WHERE id = ?
            """, (resultado, lucro_prejuizo, aposta_id))
            
            conn.commit()
            conn.close()
            
            # Atualizar banca apenas se o resultado mudou
            if resultado_anterior != resultado:
                if resultado == "Ganha":
                    movimento = valor_apostado + lucro_prejuizo
                    self.adicionar_movimento_banca(movimento, f"Aposta ganha #{aposta_id}")
                elif resultado == "Anulada" and resultado_anterior == "Pendente":
                    self.adicionar_movimento_banca(valor_apostado, f"Aposta anulada #{aposta_id}")
    
    def adicionar_movimento_banca(self, movimento: float, descricao: str):
        """Adiciona um movimento à banca"""
        saldo_atual = self.get_saldo_atual()
        novo_saldo = saldo_atual + movimento
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historico_banca (data, saldo, movimento, descricao)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), novo_saldo, movimento, descricao))
        conn.commit()
        conn.close()
    
    def get_saldo_atual(self) -> float:
        """Obtém o saldo atual da banca"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT saldo FROM historico_banca ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0.0
        except Exception as e:
            print(f"Erro ao obter saldo atual: {e}")
            return 0.0
    
    def obter_saldo_inicial(self) -> float:
        """Obtém o saldo inicial da banca"""
        try:
            saldo_str = self.get_configuracao("saldo_inicial")
            return float(saldo_str) if saldo_str else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def get_apostas(self, filtros: Dict = None) -> List[Aposta]:
        """Obtém apostas com filtros opcionais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM apostas WHERE 1=1"
        params = []
        
        if filtros:
            if filtros.get("competicao"):
                query += " AND competicao LIKE ?"
                params.append(f"%{filtros['competicao']}%")
            if filtros.get("equipa"):
                query += " AND (equipa_casa LIKE ? OR equipa_fora LIKE ?)"
                params.extend([f"%{filtros['equipa']}%", f"%{filtros['equipa']}%"])
            if filtros.get("resultado"):
                query += " AND resultado = ?"
                params.append(filtros["resultado"])
            if filtros.get("data_inicio"):
                query += " AND date(data_hora) >= ?"
                params.append(filtros["data_inicio"])
            if filtros.get("data_fim"):
                query += " AND date(data_hora) <= ?"
                params.append(filtros["data_fim"])
        
        query += " ORDER BY data_hora DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        apostas = []
        for row in rows:
            aposta = Aposta(
                id=row[0], data_hora=row[1], competicao=row[2],
                equipa_casa=row[3], equipa_fora=row[4], tipo_aposta=row[5],
                odd=row[6], valor_apostado=row[7], resultado=row[8],
                lucro_prejuizo=row[9], notas=row[10]
            )
            apostas.append(aposta)
        
        return apostas
    
    def editar_aposta(self, aposta_id: int, aposta: Aposta):
        """Edita uma aposta existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE apostas SET data_hora = ?, competicao = ?, equipa_casa = ?,
                             equipa_fora = ?, tipo_aposta = ?, odd = ?,
                             valor_apostado = ?, resultado = ?, lucro_prejuizo = ?,
                             notas = ?
            WHERE id = ?
        """, (aposta.data_hora, aposta.competicao, aposta.equipa_casa,
              aposta.equipa_fora, aposta.tipo_aposta, aposta.odd,
              aposta.valor_apostado, aposta.resultado, aposta.lucro_prejuizo,
              aposta.notas, aposta_id))
        conn.commit()
        conn.close()
    
    def eliminar_aposta(self, aposta_id: int):
        """Elimina uma aposta e os movimentos relacionados da banca"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Primeiro, obter informações da aposta antes de eliminar
        cursor.execute("SELECT valor_apostado, lucro_prejuizo, resultado FROM apostas WHERE id = ?", (aposta_id,))
        aposta_info = cursor.fetchone()
        
        if aposta_info:
            valor_apostado, lucro_prejuizo, resultado = aposta_info
            
            # Eliminar a aposta
            cursor.execute("DELETE FROM apostas WHERE id = ?", (aposta_id,))
            
            # Eliminar movimentos relacionados da banca
            cursor.execute("DELETE FROM historico_banca WHERE descricao LIKE ?", (f"%Aposta #{aposta_id}%",))
            
            conn.commit()
            
            # Recalcular saldos da banca após eliminação
            self.recalcular_saldos_banca()
        
        conn.close()
    
    def recalcular_saldos_banca(self):
        """Recalcula todos os saldos do histórico da banca"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obter todos os movimentos ordenados por data de criação
            cursor.execute("""
                SELECT id, movimento FROM historico_banca 
                ORDER BY created_at ASC
            """)
            
            movimentos = cursor.fetchall()
            saldo_acumulado = 0.0
            
            # Recalcular cada saldo
            for movimento_id, movimento in movimentos:
                saldo_acumulado += movimento
                cursor.execute("""
                    UPDATE historico_banca SET saldo = ? WHERE id = ?
                """, (saldo_acumulado, movimento_id))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_estatisticas(self) -> Dict:
        """Obtém estatísticas das apostas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de apostas
        cursor.execute("SELECT COUNT(*) FROM apostas")
        total_apostas = cursor.fetchone()[0]
        
        # Apostas ganhas
        cursor.execute("SELECT COUNT(*) FROM apostas WHERE resultado = 'Ganha'")
        apostas_ganhas = cursor.fetchone()[0]
        
        # Apostas perdidas
        cursor.execute("SELECT COUNT(*) FROM apostas WHERE resultado = 'Perdida'")
        apostas_perdidas = cursor.fetchone()[0]
        
        # Total investido
        cursor.execute("SELECT SUM(valor_apostado) FROM apostas")
        total_investido = cursor.fetchone()[0] or 0
        
        # Lucro/Prejuízo total
        cursor.execute("SELECT SUM(lucro_prejuizo) FROM apostas WHERE resultado IN ('Ganha', 'Perdida')")
        lucro_total = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Calcular percentagens
        taxa_acerto = (apostas_ganhas / total_apostas * 100) if total_apostas > 0 else 0
        roi = (lucro_total / total_investido * 100) if total_investido > 0 else 0
        
        return {
             'total_apostas': total_apostas,
             'apostas_ganhas': apostas_ganhas,
             'apostas_perdidas': apostas_perdidas,
             'taxa_acerto': taxa_acerto,
             'total_investido': total_investido,
             'lucro_total': lucro_total,
             'roi': roi
         }
    
    def adicionar_movimento_banca(self, valor, descricao):
        """Adicionar movimento à banca"""
        try:
            saldo_atual = self.get_saldo_atual()
            novo_saldo = saldo_atual + valor
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO historico_banca (data, saldo, movimento, descricao)
                VALUES (?, ?, ?, ?)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), novo_saldo, valor, descricao))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao adicionar movimento à banca: {e}")
    
    def get_configuracao(self, chave):
        """Obter configuração"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"Erro ao obter configuração: {e}")
            return None
    
    def set_configuracao(self, chave, valor):
        """Definir configuração"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO configuracoes (chave, valor)
                VALUES (?, ?)
            """, (chave, valor))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao definir configuração: {e}")

if __name__ == "__main__":
    # Teste básico da base de dados
    db = DatabaseManager()
    print(f"Saldo atual: €{db.get_saldo_atual():.2f}")
    print("Base de dados inicializada com sucesso!")