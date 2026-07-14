#!/usr/bin/env python3
"""
Extrator unificado: processa PDFs, vídeos e imagens automaticamente.
"""

import os
from pathlib import Path
import sys
import subprocess

from extrair_pdf import extrair_pdfs_da_pasta
from extrair_video import processar_video_url, processar_video_local
from extrair_imagem import extrair_imagens_da_pasta

def processar_arquivo(arquivo, pasta_saida="dados/transcricoes/"):
    """
    Identifica o tipo do arquivo pela extensão e chama o extrator certo.
    """
    extensao = Path(arquivo).suffix.lower()
    
    if extensao == ".pdf":
        from extrair_pdf import extrair_pdf
        nome_base = Path(arquivo).stem
        saida = Path(pasta_saida) / f"{nome_base}.txt"
        return extrair_pdf(arquivo, saida)
    
    elif extensao in [".mp4", ".avi", ".mkv", ".mov"]:
        from extrair_video import processar_video_local
        return processar_video_local(arquivo, pasta_saida)
    
    elif extensao in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        from extrair_imagem import extrair_imagem
        nome_base = Path(arquivo).stem
        saida = Path(pasta_saida) / f"{nome_base}.txt"
        return extrair_imagem(arquivo, saida)
    
    elif arquivo.startswith("http"):
        from extrair_video import processar_video_url
        return processar_video_url(arquivo, "dados/audios/", pasta_saida)
    
    else:
        print(f"⚠️ Extensão não suportada: {extensao}")
        return None

def processar_pasta(pasta_entrada, pasta_saida="dados/transcricoes/"):
    """
    Varre a pasta e processa todos os arquivos suportados de uma vez.
    """
    os.makedirs(pasta_saida, exist_ok=True)
    
    print("\n📄 Processando PDFs...")
    extrair_pdfs_da_pasta(Path(pasta_entrada), pasta_saida)
    
    print("\n🖼️ Processando imagens...")
    extrair_imagens_da_pasta(Path(pasta_entrada), pasta_saida)
    
    print("\n🎬 Processando vídeos locais...")
    for ext in [".mp4", ".avi", ".mkv", ".mov"]:
        for video in Path(pasta_entrada).glob(f"*{ext}"):
            processar_video_local(video, pasta_saida)
    
    print("\n✅ Todos os arquivos processados!")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        saida = sys.argv[2] if len(sys.argv) >= 3 else "dados/transcricoes/"
        
        if os.path.isdir(entrada):
            processar_pasta(entrada, saida)
        else:
            processar_arquivo(entrada, saida)
    else:
        print("Uso:")
        print("  python extrator_unificado.py pasta_com_tudo/ pasta_saida/")
        print("  python extrator_unificado.py arquivo.pdf pasta_saida/")
        print("  python extrator_unificado.py video.mp4 pasta_saida/")
        print("  python extrator_unificado.py https://youtube.com/watch?v=...")