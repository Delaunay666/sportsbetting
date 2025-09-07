#!/usr/bin/env python3
"""
Script para criar um ícone ICO baseado no design do SVG
"""

import os
from PIL import Image, ImageDraw

def criar_icone_apostas():
    """
    Cria um ícone ICO baseado no tema de apostas desportivas
    """
    try:
        ico_path = "icon.ico"
        
        print(f"Criando ícone de apostas desportivas: {ico_path}...")
        
        # Criar múltiplos tamanhos para o ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        images = []
        
        for size in sizes:
            # Criar imagem com fundo transparente
            img = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            w, h = size
            
            # Calcular dimensões proporcionais
            margin = max(2, w // 16)
            
            # Fundo com gradiente simulado (azul para verde)
            for y in range(margin, h - margin):
                # Gradiente de azul (#0088ff) para verde (#00ff88)
                ratio = (y - margin) / (h - 2 * margin)
                r = int(0 * (1 - ratio) + 0 * ratio)
                g = int(136 * (1 - ratio) + 255 * ratio)
                b = int(255 * (1 - ratio) + 136 * ratio)
                
                draw.rectangle([
                    margin, y, 
                    w - margin, y + 1
                ], fill=(r, g, b, 255))
            
            # Fundo branco interno
            inner_margin = margin + max(1, w // 32)
            draw.rounded_rectangle([
                inner_margin, inner_margin,
                w - inner_margin, h - inner_margin
            ], radius=max(1, w // 16), fill=(255, 255, 255, 255))
            
            # Desenhar símbolo de apostas (bola de futebol estilizada)
            center_x, center_y = w // 2, h // 2
            ball_radius = max(2, w // 8)
            
            # Círculo principal (bola)
            draw.ellipse([
                center_x - ball_radius, center_y - ball_radius,
                center_x + ball_radius, center_y + ball_radius
            ], fill=(0, 136, 255, 255), outline=(0, 100, 200, 255), width=max(1, w // 64))
            
            # Padrão da bola (linhas)
            if w >= 32:
                line_width = max(1, w // 128)
                # Linha horizontal
                draw.line([
                    center_x - ball_radius // 2, center_y,
                    center_x + ball_radius // 2, center_y
                ], fill=(255, 255, 255, 255), width=line_width)
                
                # Linha vertical
                draw.line([
                    center_x, center_y - ball_radius // 2,
                    center_x, center_y + ball_radius // 2
                ], fill=(255, 255, 255, 255), width=line_width)
            
            # Adicionar símbolo de dinheiro ($) pequeno
            if w >= 48:
                dollar_x = center_x + ball_radius + max(2, w // 32)
                dollar_y = center_y - max(2, w // 32)
                font_size = max(2, w // 16)
                
                # Desenhar $ simplificado
                draw.text(
                    (dollar_x, dollar_y), "$", 
                    fill=(0, 200, 100, 255), 
                    anchor="mm"
                )
            
            images.append(img)
        
        # Salvar como ICO
        images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images])
        
        print(f"✅ Ícone criado com sucesso: {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar ícone: {e}")
        return False

if __name__ == "__main__":
    criar_icone_apostas()