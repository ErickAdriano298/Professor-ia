#!/usr/bin/env python3
"""
Extrator de texto de PDFs usando pypdf (sucessor do PyPDF2)
"""

from pypdf import PdfReader
import os
from pathlib import Path
import sys

def extrair_pdf(caminho_pdf, caminho_saida=None):
    """
    Extrai o texto de um PDF e salva em .txt se informado.
    """
    try:
        reader = PdfReader(caminho_pdf)
        texto_completo = ""
        
        for pagina_num, pagina in enumerate(reader.pages, 1):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo += f"\n--- PÁGINA {pagina_num} ---\n"
                texto_completo += texto_pagina
        
        if caminho_saida:
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write(texto_completo)
            print(f"✅ PDF extraído: {caminho_saida}")
        
        return texto_completo
    
    except Exception as e:
        print(f"❌ Erro ao extrair {caminho_pdf}: {e}")
        return ""

def extrair_pdfs_da_pasta(pasta_entrada, pasta_saida):
    """
    Processa todos os PDFs de uma pasta de uma vez.
    """
    arquivos = Path(pasta_entrada).glob("*.pdf")
    total = 0
    
    for pdf in arquivos:
        nome_saida = Path(pasta_saida) / f"{pdf.stem}.txt"
        extrair_pdf(pdf, nome_saida)
        total += 1
    
    print(f"\n📊 Total de PDFs extraídos: {total}")
    return total

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        saida = sys.argv[2] if len(sys.argv) >= 3 else "dados/transcricoes/"
        
        if os.path.isdir(entrada):
            extrair_pdfs_da_pasta(entrada, saida)
        else:
            nome_base = Path(entrada).stem
            saida_arquivo = Path(saida) / f"{nome_base}.txt"
            extrair_pdf(entrada, saida_arquivo)
    else:
        print("Uso:")
        print("  python extrair_pdf.py pasta_com_pdfs/ pasta_saida/")
        print("  python extrair_pdf.py arquivo.pdf pasta_saida/")