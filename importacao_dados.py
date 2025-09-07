#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Importação e Exportação de Dados
Permite importar dados de diferentes formatos e exportar relatórios
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from main import DatabaseManager
from validacao import DataValidator
import warnings
warnings.filterwarnings('ignore')

class DataImporter:
    """Classe para importação de dados de diferentes fontes"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.validator = DataValidator(db)
        self.supported_formats = {
            '.csv': self.import_csv,
            '.xlsx': self.import_excel,
            '.xls': self.import_excel,
            '.json': self.import_json,
            '.xml': self.import_xml,
            '.txt': self.import_txt
        }
    
    def import_file(self, file_path: str) -> Dict:
        """Importar arquivo baseado na extensão"""
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            
            if extension not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Formato {extension} não suportado',
                    'supported_formats': list(self.supported_formats.keys())
                }
            
            # Chamar método específico para o formato
            result = self.supported_formats[extension](file_path)
            
            if result['success']:
                # Validar e processar dados
                processed_result = self.process_imported_data(result['data'])
                return processed_result
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao importar arquivo: {str(e)}'
            }
    
    def import_csv(self, file_path: Path) -> Dict:
        """Importar dados de arquivo CSV"""
        try:
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                return {
                    'success': False,
                    'error': 'Não foi possível ler o arquivo com nenhum encoding suportado'
                }
            
            return {
                'success': True,
                'data': df,
                'format': 'CSV',
                'rows': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao ler CSV: {str(e)}'
            }
    
    def import_excel(self, file_path: Path) -> Dict:
        """Importar dados de arquivo Excel"""
        try:
            # Ler todas as abas
            excel_file = pd.ExcelFile(file_path)
            sheets = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets[sheet_name] = df
            
            # Se há apenas uma aba, retornar diretamente
            if len(sheets) == 1:
                df = list(sheets.values())[0]
                return {
                    'success': True,
                    'data': df,
                    'format': 'Excel',
                    'rows': len(df)
                }
            
            # Se há múltiplas abas, retornar a primeira ou permitir seleção
            main_sheet = list(sheets.values())[0]
            return {
                'success': True,
                'data': main_sheet,
                'format': 'Excel',
                'rows': len(main_sheet),
                'all_sheets': sheets
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao ler Excel: {str(e)}'
            }
    
    def import_json(self, file_path: Path) -> Dict:
        """Importar dados de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converter para DataFrame se possível
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Se é um dict, tentar encontrar a lista principal
                if 'apostas' in data:
                    df = pd.DataFrame(data['apostas'])
                elif 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    # Tentar converter o dict diretamente
                    df = pd.DataFrame([data])
            else:
                return {
                    'success': False,
                    'error': 'Formato JSON não reconhecido'
                }
            
            return {
                'success': True,
                'data': df,
                'format': 'JSON',
                'rows': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao ler JSON: {str(e)}'
            }
    
    def import_xml(self, file_path: Path) -> Dict:
        """Importar dados de arquivo XML"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Converter XML para lista de dicts
            data = []
            
            # Procurar por elementos que parecem apostas
            for element in root.iter():
                if element.tag.lower() in ['aposta', 'bet', 'record', 'row']:
                    record = {}
                    
                    # Atributos do elemento
                    record.update(element.attrib)
                    
                    # Elementos filhos
                    for child in element:
                        record[child.tag] = child.text
                    
                    if record:  # Se há dados no record
                        data.append(record)
            
            if not data:
                # Se não encontrou estrutura específica, tentar converter tudo
                def xml_to_dict(element):
                    result = {}
                    for child in element:
                        if len(child) == 0:
                            result[child.tag] = child.text
                        else:
                            result[child.tag] = xml_to_dict(child)
                    return result
                
                data = [xml_to_dict(root)]
            
            df = pd.DataFrame(data)
            
            return {
                'success': True,
                'data': df,
                'format': 'XML',
                'rows': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao ler XML: {str(e)}'
            }
    
    def import_txt(self, file_path: Path) -> Dict:
        """Importar dados de arquivo TXT (assumindo formato delimitado)"""
        try:
            # Tentar diferentes delimitadores
            delimiters = [',', ';', '\t', '|']
            
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
                    if len(df.columns) > 1:  # Se encontrou múltiplas colunas
                        return {
                            'success': True,
                            'data': df,
                            'format': 'TXT',
                            'rows': len(df),
                            'delimiter': delimiter
                        }
                except:
                    continue
            
            # Se não conseguiu com delimitadores, ler como texto simples
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            df = pd.DataFrame({'text': [line.strip() for line in lines]})
            
            return {
                'success': True,
                'data': df,
                'format': 'TXT',
                'rows': len(df),
                'note': 'Importado como texto simples'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao ler TXT: {str(e)}'
            }
    
    def process_imported_data(self, df: pd.DataFrame) -> Dict:
        """Processar e validar dados importados"""
        try:
            # Mapear colunas para formato padrão
            column_mapping = self.detect_column_mapping(df)
            
            if not column_mapping:
                return {
                    'success': False,
                    'error': 'Não foi possível mapear as colunas automaticamente',
                    'columns': list(df.columns),
                    'sample_data': df.head().to_dict('records')
                }
            
            # Aplicar mapeamento
            mapped_df = self.apply_column_mapping(df, column_mapping)
            
            # Validar dados
            validation_result = self.validate_imported_data(mapped_df)
            
            return {
                'success': True,
                'data': mapped_df,
                'column_mapping': column_mapping,
                'validation': validation_result,
                'total_rows': len(mapped_df),
                'valid_rows': validation_result['valid_count'],
                'invalid_rows': validation_result['invalid_count']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao processar dados: {str(e)}'
            }
    
    def detect_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detectar mapeamento automático de colunas"""
        mapping = {}
        columns = [col.lower().strip() for col in df.columns]
        
        # Mapeamentos possíveis
        field_patterns = {
            'data_hora': ['data', 'date', 'datetime', 'data_hora', 'timestamp'],
            'equipa_casa': ['casa', 'home', 'equipa_casa', 'team_home', 'home_team'],
            'equipa_fora': ['fora', 'away', 'equipa_fora', 'team_away', 'away_team'],
            'competicao': ['competicao', 'competition', 'liga', 'league', 'torneio'],
            'tipo_aposta': ['tipo', 'type', 'bet_type', 'tipo_aposta', 'market'],
            'odd': ['odd', 'odds', 'cotacao', 'quote'],
            'valor_apostado': ['valor', 'stake', 'amount', 'valor_apostado', 'bet_amount'],
            'resultado': ['resultado', 'result', 'outcome', 'status']
        }
        
        for field, patterns in field_patterns.items():
            for col in columns:
                for pattern in patterns:
                    if pattern in col or col in pattern:
                        original_col = df.columns[columns.index(col)]
                        mapping[field] = original_col
                        break
                if field in mapping:
                    break
        
        return mapping
    
    def apply_column_mapping(self, df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Aplicar mapeamento de colunas"""
        mapped_df = pd.DataFrame()
        
        # Campos obrigatórios
        required_fields = ['data_hora', 'equipa_casa', 'equipa_fora', 'odd', 'valor_apostado']
        
        for field in required_fields:
            if field in mapping:
                mapped_df[field] = df[mapping[field]]
            else:
                # Criar campo vazio se obrigatório não encontrado
                mapped_df[field] = ''
        
        # Campos opcionais
        optional_fields = ['competicao', 'tipo_aposta', 'resultado']
        
        for field in optional_fields:
            if field in mapping:
                mapped_df[field] = df[mapping[field]]
            else:
                # Valores padrão
                if field == 'competicao':
                    mapped_df[field] = 'Importado'
                elif field == 'tipo_aposta':
                    mapped_df[field] = 'Resultado Final'
                elif field == 'resultado':
                    mapped_df[field] = 'Pendente'
        
        return mapped_df
    
    def validate_imported_data(self, df: pd.DataFrame) -> Dict:
        """Validar dados importados"""
        validation_result = {
            'valid_count': 0,
            'invalid_count': 0,
            'errors': [],
            'warnings': []
        }
        
        for index, row in df.iterrows():
            row_errors = []
            
            # Validar data
            if not self.validator.validate_datetime(str(row['data_hora'])):
                row_errors.append(f"Linha {index + 1}: Data inválida")
            
            # Validar odd
            if not self.validator.validate_odd(str(row['odd'])):
                row_errors.append(f"Linha {index + 1}: Odd inválida")
            
            # Validar valor
            if not self.validator.validate_value(str(row['valor_apostado'])):
                row_errors.append(f"Linha {index + 1}: Valor inválido")
            
            # Validar equipas
            if not row['equipa_casa'] or not row['equipa_fora']:
                row_errors.append(f"Linha {index + 1}: Equipas não podem estar vazias")
            
            if row_errors:
                validation_result['invalid_count'] += 1
                validation_result['errors'].extend(row_errors)
            else:
                validation_result['valid_count'] += 1
        
        return validation_result
    
    def save_to_database(self, df: pd.DataFrame, overwrite: bool = False) -> Dict:
        """Salvar dados importados na base de dados"""
        try:
            saved_count = 0
            skipped_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Verificar se já existe (se não for overwrite)
                    if not overwrite:
                        if self.validator.check_duplicate_bet(
                            str(row['data_hora']),
                            str(row['equipa_casa']),
                            str(row['equipa_fora']),
                            float(row['odd']),
                            float(row['valor_apostado'])
                        ):
                            skipped_count += 1
                            continue
                    
                    # Adicionar à base de dados
                    self.db.adicionar_aposta(
                        data_hora=str(row['data_hora']),
                        equipa_casa=str(row['equipa_casa']),
                        equipa_fora=str(row['equipa_fora']),
                        competicao=str(row['competicao']),
                        tipo_aposta=str(row['tipo_aposta']),
                        odd=float(row['odd']),
                        valor_apostado=float(row['valor_apostado']),
                        resultado=str(row['resultado'])
                    )
                    
                    saved_count += 1
                    
                except Exception as e:
                    errors.append(f"Linha {index + 1}: {str(e)}")
            
            return {
                'success': True,
                'saved_count': saved_count,
                'skipped_count': skipped_count,
                'error_count': len(errors),
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao salvar na base de dados: {str(e)}'
            }

class DataExporter:
    """Classe para exportação de dados"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def export_apostas(self, file_path: str, format_type: str = 'csv', filters: Dict = None) -> Dict:
        """Exportar apostas para arquivo"""
        try:
            # Carregar dados
            conn = sqlite3.connect(self.db.db_path)
            
            query = "SELECT * FROM apostas"
            conditions = []
            params = []
            
            # Aplicar filtros se fornecidos
            if filters:
                if 'data_inicio' in filters and filters['data_inicio']:
                    conditions.append("date(data_hora, 'localtime') >= ?")
                    params.append(filters['data_inicio'])
                
                if 'data_fim' in filters and filters['data_fim']:
                    conditions.append("date(data_hora, 'localtime') <= ?")
                    params.append(filters['data_fim'])
                
                if 'competicao' in filters and filters['competicao']:
                    conditions.append("competicao = ?")
                    params.append(filters['competicao'])
                
                if 'resultado' in filters and filters['resultado']:
                    conditions.append("resultado = ?")
                    params.append(filters['resultado'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY data_hora DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if df.empty:
                return {
                    'success': False,
                    'error': 'Nenhum dado encontrado com os filtros aplicados'
                }
            
            # Exportar baseado no formato
            if format_type.lower() == 'csv':
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif format_type.lower() in ['xlsx', 'excel']:
                df.to_excel(file_path, index=False)
            elif format_type.lower() == 'json':
                df.to_json(file_path, orient='records', date_format='iso', indent=2)
            else:
                return {
                    'success': False,
                    'error': f'Formato {format_type} não suportado'
                }
            
            return {
                'success': True,
                'file_path': file_path,
                'records_exported': len(df),
                'format': format_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao exportar: {str(e)}'
            }
    
    def export_relatorio_completo(self, file_path: str) -> Dict:
        """Exportar relatório completo em Excel com múltiplas abas"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                conn = sqlite3.connect(self.db.db_path)
                
                # Aba 1: Todas as apostas
                df_apostas = pd.read_sql_query(
                    "SELECT * FROM apostas ORDER BY data_hora DESC",
                    conn
                )
                df_apostas.to_excel(writer, sheet_name='Apostas', index=False)
                
                # Aba 2: Resumo por competição
                df_competicao = pd.read_sql_query("""
                    SELECT 
                        competicao,
                        COUNT(*) as total_apostas,
                        SUM(CASE WHEN resultado = 'Ganha' THEN 1 ELSE 0 END) as ganhas,
                        SUM(CASE WHEN resultado = 'Perdida' THEN 1 ELSE 0 END) as perdidas,
                        ROUND(AVG(odd), 2) as odd_media,
                        SUM(valor_apostado) as valor_total,
                        SUM(lucro_prejuizo) as lucro_total,
                        ROUND((SUM(lucro_prejuizo) / SUM(valor_apostado)) * 100, 2) as roi
                    FROM apostas 
                    WHERE resultado IN ('Ganha', 'Perdida')
                    GROUP BY competicao
                    ORDER BY lucro_total DESC
                """, conn)
                df_competicao.to_excel(writer, sheet_name='Por Competição', index=False)
                
                # Aba 3: Resumo mensal
                df_mensal = pd.read_sql_query("""
                    SELECT 
                        strftime('%Y-%m', data_hora) as mes,
                        COUNT(*) as total_apostas,
                        SUM(CASE WHEN resultado = 'Ganha' THEN 1 ELSE 0 END) as ganhas,
                        SUM(CASE WHEN resultado = 'Perdida' THEN 1 ELSE 0 END) as perdidas,
                        SUM(valor_apostado) as valor_total,
                        SUM(lucro_prejuizo) as lucro_total,
                        ROUND((SUM(lucro_prejuizo) / SUM(valor_apostado)) * 100, 2) as roi
                    FROM apostas 
                    WHERE resultado IN ('Ganha', 'Perdida')
                    GROUP BY strftime('%Y-%m', data_hora)
                    ORDER BY mes DESC
                """, conn)
                df_mensal.to_excel(writer, sheet_name='Por Mês', index=False)
                
                # Aba 4: Histórico da banca
                df_banca = pd.read_sql_query(
                    "SELECT * FROM historico_banca ORDER BY data_hora DESC",
                    conn
                )
                df_banca.to_excel(writer, sheet_name='Histórico Banca', index=False)
                
                conn.close()
            
            return {
                'success': True,
                'file_path': file_path,
                'sheets_created': 4
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao criar relatório: {str(e)}'
            }

class ImportExportInterface(ctk.CTkFrame):
    """Interface para importação e exportação de dados"""
    
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db
        self.importer = DataImporter(db)
        self.exporter = DataExporter(db)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        # Título
        title = ctk.CTkLabel(
            self,
            text="📁 Importação e Exportação de Dados",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Notebook para separar importação e exportação
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba de Importação
        self.notebook.add("Importação")
        self.create_import_tab()
        
        # Aba de Exportação
        self.notebook.add("Exportação")
        self.create_export_tab()
    
    def create_import_tab(self):
        """Criar aba de importação"""
        import_frame = self.notebook.tab("Importação")
        
        # Instruções
        instructions = ctk.CTkLabel(
            import_frame,
            text="Selecione um arquivo para importar apostas.\nFormatos suportados: CSV, Excel, JSON, XML, TXT",
            font=ctk.CTkFont(size=14)
        )
        instructions.pack(pady=10)
        
        # Botão para selecionar arquivo
        select_btn = ctk.CTkButton(
            import_frame,
            text="📂 Selecionar Arquivo",
            command=self.select_import_file,
            width=200,
            height=40
        )
        select_btn.pack(pady=10)
        
        # Frame para preview dos dados
        self.preview_frame = ctk.CTkFrame(import_frame)
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Label para status
        self.import_status_label = ctk.CTkLabel(
            import_frame,
            text="Nenhum arquivo selecionado",
            font=ctk.CTkFont(size=12)
        )
        self.import_status_label.pack(pady=5)
    
    def create_export_tab(self):
        """Criar aba de exportação"""
        export_frame = self.notebook.tab("Exportação")
        
        # Opções de exportação
        options_frame = ctk.CTkFrame(export_frame)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            options_frame,
            text="Opções de Exportação",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Formato
        format_frame = ctk.CTkFrame(options_frame)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(format_frame, text="Formato:").pack(side="left", padx=10)
        
        self.export_format = ctk.CTkComboBox(
            format_frame,
            values=["CSV", "Excel", "JSON"],
            width=150
        )
        self.export_format.pack(side="left", padx=10)
        
        # Filtros de data
        date_frame = ctk.CTkFrame(options_frame)
        date_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(date_frame, text="Período:").pack(side="left", padx=10)
        
        self.data_inicio = ctk.CTkEntry(
            date_frame,
            placeholder_text="Data início (DD/MM/YYYY)",
            width=150
        )
        self.data_inicio.pack(side="left", padx=5)
        
        self.data_fim = ctk.CTkEntry(
            date_frame,
            placeholder_text="Data fim (DD/MM/YYYY)",
            width=150
        )
        self.data_fim.pack(side="left", padx=5)
        
        # Botões de exportação
        buttons_frame = ctk.CTkFrame(export_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        export_apostas_btn = ctk.CTkButton(
            buttons_frame,
            text="📤 Exportar Apostas",
            command=self.export_apostas,
            width=200,
            height=40
        )
        export_apostas_btn.pack(side="left", padx=10, pady=10)
        
        export_relatorio_btn = ctk.CTkButton(
            buttons_frame,
            text="📊 Relatório Completo",
            command=self.export_relatorio_completo,
            width=200,
            height=40
        )
        export_relatorio_btn.pack(side="left", padx=10, pady=10)
        
        # Status da exportação
        self.export_status_label = ctk.CTkLabel(
            export_frame,
            text="Pronto para exportar",
            font=ctk.CTkFont(size=12)
        )
        self.export_status_label.pack(pady=5)
    
    def select_import_file(self):
        """Selecionar arquivo para importação"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo para importar",
            filetypes=[
                ("Todos os suportados", "*.csv;*.xlsx;*.xls;*.json;*.xml;*.txt"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.import_status_label.configure(text="Processando arquivo...")
            self.update()
            
            # Importar arquivo
            result = self.importer.import_file(file_path)
            
            if result['success']:
                self.show_import_preview(result)
                self.import_status_label.configure(
                    text=f"Arquivo carregado: {result['total_rows']} registros encontrados"
                )
            else:
                self.import_status_label.configure(
                    text=f"Erro: {result['error']}"
                )
                messagebox.showerror("Erro de Importação", result['error'])
    
    def show_import_preview(self, import_result):
        """Mostrar preview dos dados importados"""
        # Limpar preview anterior
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Título do preview
        preview_title = ctk.CTkLabel(
            self.preview_frame,
            text="Preview dos Dados Importados",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        preview_title.pack(pady=10)
        
        # Informações de validação
        validation = import_result['validation']
        info_text = f"Total: {import_result['total_rows']} | Válidos: {validation['valid_count']} | Inválidos: {validation['invalid_count']}"
        
        info_label = ctk.CTkLabel(
            self.preview_frame,
            text=info_text,
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=5)
        
        # Mostrar erros se houver
        if validation['errors']:
            errors_frame = ctk.CTkFrame(self.preview_frame)
            errors_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                errors_frame,
                text="⚠️ Erros encontrados:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=5)
            
            errors_text = "\n".join(validation['errors'][:5])  # Mostrar apenas os primeiros 5
            if len(validation['errors']) > 5:
                errors_text += f"\n... e mais {len(validation['errors']) - 5} erros"
            
            errors_label = ctk.CTkLabel(
                errors_frame,
                text=errors_text,
                font=ctk.CTkFont(size=10),
                justify="left"
            )
            errors_label.pack(padx=10, pady=5)
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(self.preview_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        if validation['valid_count'] > 0:
            import_btn = ctk.CTkButton(
                buttons_frame,
                text=f"✅ Importar {validation['valid_count']} registros válidos",
                command=lambda: self.confirm_import(import_result),
                width=300
            )
            import_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancelar",
            command=self.cancel_import,
            width=100
        )
        cancel_btn.pack(side="right", padx=5)
    
    def confirm_import(self, import_result):
        """Confirmar e executar importação"""
        # Perguntar sobre duplicados
        overwrite = messagebox.askyesno(
            "Duplicados",
            "Deseja sobrescrever apostas duplicadas?\n\nSim = Sobrescrever\nNão = Pular duplicados"
        )
        
        self.import_status_label.configure(text="Importando dados...")
        self.update()
        
        # Salvar na base de dados
        save_result = self.importer.save_to_database(
            import_result['data'],
            overwrite=overwrite
        )
        
        if save_result['success']:
            message = f"Importação concluída!\n\n"
            message += f"Salvos: {save_result['saved_count']}\n"
            message += f"Ignorados: {save_result['skipped_count']}\n"
            message += f"Erros: {save_result['error_count']}"
            
            messagebox.showinfo("Importação Concluída", message)
            self.import_status_label.configure(text="Importação concluída com sucesso")
            
            # Limpar preview
            self.cancel_import()
        else:
            messagebox.showerror("Erro na Importação", save_result['error'])
            self.import_status_label.configure(text="Erro na importação")
    
    def cancel_import(self):
        """Cancelar importação"""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        self.import_status_label.configure(text="Nenhum arquivo selecionado")
    
    def export_apostas(self):
        """Exportar apostas"""
        # Selecionar arquivo de destino
        format_ext = {
            'CSV': '.csv',
            'Excel': '.xlsx',
            'JSON': '.json'
        }
        
        selected_format = self.export_format.get()
        extension = format_ext.get(selected_format, '.csv')
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar exportação como",
            defaultextension=extension,
            filetypes=[
                (f"{selected_format} files", f"*{extension}"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Preparar filtros
            filters = {}
            
            if self.data_inicio.get():
                try:
                    data_inicio = datetime.strptime(self.data_inicio.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
                    filters['data_inicio'] = data_inicio
                except:
                    pass
            
            if self.data_fim.get():
                try:
                    data_fim = datetime.strptime(self.data_fim.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
                    filters['data_fim'] = data_fim
                except:
                    pass
            
            self.export_status_label.configure(text="Exportando...")
            self.update()
            
            # Exportar
            result = self.exporter.export_apostas(
                file_path,
                selected_format.lower(),
                filters
            )
            
            if result['success']:
                message = f"Exportação concluída!\n\n"
                message += f"Arquivo: {result['file_path']}\n"
                message += f"Registros: {result['records_exported']}\n"
                message += f"Formato: {result['format']}"
                
                messagebox.showinfo("Exportação Concluída", message)
                self.export_status_label.configure(text="Exportação concluída")
            else:
                messagebox.showerror("Erro na Exportação", result['error'])
                self.export_status_label.configure(text="Erro na exportação")
    
    def export_relatorio_completo(self):
        """Exportar relatório completo"""
        file_path = filedialog.asksaveasfilename(
            title="Salvar relatório completo como",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.export_status_label.configure(text="Gerando relatório...")
            self.update()
            
            result = self.exporter.export_relatorio_completo(file_path)
            
            if result['success']:
                message = f"Relatório gerado com sucesso!\n\n"
                message += f"Arquivo: {result['file_path']}\n"
                message += f"Abas criadas: {result['sheets_created']}"
                
                messagebox.showinfo("Relatório Gerado", message)
                self.export_status_label.configure(text="Relatório gerado com sucesso")
            else:
                messagebox.showerror("Erro no Relatório", result['error'])
                self.export_status_label.configure(text="Erro ao gerar relatório")

# Função para integrar na aplicação principal
def create_import_export_tab(parent, db: DatabaseManager):
    """Criar aba de importação/exportação na aplicação principal"""
    return ImportExportInterface(parent, db)