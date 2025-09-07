#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Apostas Desportivas - Versão 2.0
Módulo: Notificações por Email
Autor: Sistema de Apostas
Data: 2025
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
from typing import Optional

class GestorNotificacoesEmail:
    """Classe para gestão de notificações por email"""
    
    def __init__(self, config_path: str = "config_email.json"):
        self.config_path = config_path
        self.config = self.carregar_configuracao()
    
    def carregar_configuracao(self) -> dict:
        """Carrega configuração de email do ficheiro"""
        config_padrao = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email_remetente": "",
            "password_remetente": "",
            "email_destino": "delaunayjulio@gmail.com",
            "ativo": True,
            "usar_tls": True
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Mesclar com configuração padrão
                    config_padrao.update(config)
            except Exception as e:
                print(f"Erro ao carregar configuração de email: {e}")
        else:
            # Criar ficheiro de configuração padrão
            self.salvar_configuracao(config_padrao)
        
        return config_padrao
    
    def salvar_configuracao(self, config: dict):
        """Salva configuração de email no ficheiro"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração de email: {e}")
    
    def configurar_email(self, smtp_server: str, smtp_port: int, 
                        email_remetente: str, password_remetente: str,
                        email_destino: str = None, usar_tls: bool = True):
        """Configura parâmetros de email"""
        self.config.update({
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "email_remetente": email_remetente,
            "password_remetente": password_remetente,
            "usar_tls": usar_tls
        })
        
        if email_destino:
            self.config["email_destino"] = email_destino
        
        self.salvar_configuracao(self.config)
    
    def ativar_notificacoes(self, ativo: bool = True):
        """Ativa ou desativa notificações por email"""
        self.config["ativo"] = ativo
        self.salvar_configuracao(self.config)
    
    def enviar_email(self, assunto: str, corpo: str, 
                    email_destino: Optional[str] = None) -> bool:
        """Envia email de notificação"""
        if not self.config.get("ativo", False):
            print("📧 Notificações por email desativadas")
            return False
        
        if not self.config.get("email_remetente") or not self.config.get("password_remetente"):
            print("❌ Configuração de email incompleta")
            return False
        
        try:
            # Configurar destinatário
            destino = email_destino or self.config.get("email_destino")
            if not destino:
                print("❌ Email de destino não configurado")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.config["email_remetente"]
            msg['To'] = destino
            msg['Subject'] = assunto
            
            # Adicionar corpo do email
            msg.attach(MIMEText(corpo, 'html', 'utf-8'))
            
            # Configurar servidor SMTP
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            
            if self.config.get("usar_tls", True):
                server.starttls()
            
            # Fazer login e enviar
            server.login(self.config["email_remetente"], self.config["password_remetente"])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email enviado com sucesso para {destino}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            return False
    
    def notificar_novo_registo(self, username: str, email_utilizador: str, 
                              tipo_utilizador: str = "utilizador") -> bool:
        """Envia notificação de novo registo"""
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        assunto = "🆕 Novo Registo - Sistema de Apostas Desportivas"
        
        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2c5aa0; text-align: center;">🎯 Sistema de Apostas Desportivas</h2>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">✅ Novo Utilizador Registado</h3>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold; width: 30%;">👤 Username:</td>
                            <td style="padding: 8px; background-color: #e9ecef; border-radius: 4px;">{username}</td>
                        </tr>
                        <tr><td colspan="2" style="height: 10px;"></td></tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">📧 Email:</td>
                            <td style="padding: 8px; background-color: #e9ecef; border-radius: 4px;">{email_utilizador}</td>
                        </tr>
                        <tr><td colspan="2" style="height: 10px;"></td></tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">🏷️ Tipo:</td>
                            <td style="padding: 8px; background-color: #e9ecef; border-radius: 4px;">{tipo_utilizador.title()}</td>
                        </tr>
                        <tr><td colspan="2" style="height: 10px;"></td></tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">📅 Data/Hora:</td>
                            <td style="padding: 8px; background-color: #e9ecef; border-radius: 4px;">{data_atual}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; font-size: 14px;">
                        <strong>ℹ️ Informação:</strong> Este email foi enviado automaticamente pelo sistema quando um novo utilizador se registou na plataforma.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #6c757d; font-size: 12px; margin: 0;">
                        Sistema de Apostas Desportivas v2.0<br>
                        Notificação automática - {data_atual}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(assunto, corpo)
    
    def testar_configuracao(self) -> bool:
        """Testa configuração de email enviando email de teste"""
        assunto = "✅ Teste - Sistema de Apostas Desportivas"
        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2c5aa0; text-align: center;">🎯 Sistema de Apostas Desportivas</h2>
                
                <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <h3 style="color: #155724; margin-top: 0;">✅ Teste de Configuração</h3>
                    <p style="margin: 0;">Se recebeu este email, a configuração de notificações está a funcionar corretamente!</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #6c757d; font-size: 12px; margin: 0;">
                        Sistema de Apostas Desportivas v2.0<br>
                        Email de teste - {datetime.now().strftime("%d/%m/%Y às %H:%M")}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(assunto, corpo)

# Instância global do gestor de notificações
gestor_notificacoes = GestorNotificacoesEmail()