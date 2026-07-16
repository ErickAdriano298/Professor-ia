#!/usr/bin/env python3
"""
Extrator de texto de PDFs usando pypdf (sucessor do PyPDF2)
"""

from pypdf import PdfReader
import os
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para importar config.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import TRANSCRICOES_PASTA, PDFS_PASTA

# ===== MODO DEBUG =====
DEBUG = "--debug" in sys.argv

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
            Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write(texto_completo)
            print(f"✅ PDF extraído: {caminho_saida}")

        return texto_completo

    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao extrair {caminho_pdf}: {e}")
        return ""

def extrair_pdfs_da_pasta(pasta_entrada, pasta_saida):
    """
    Processa todos os PDFs de uma pasta e subpastas recursivamente.
    """
    try:
        pasta_entrada = Path(pasta_entrada)
        pasta_saida = Path(pasta_saida)
        pasta_saida.mkdir(parents=True, exist_ok=True)

        # 🔧 AGORA BUSCA RECURSIVAMENTE EM TODAS AS SUBPASTAS
        arquivos = list(pasta_entrada.rglob("*.pdf"))
        if not arquivos:
            print(f"ℹ️ Nenhum PDF encontrado em: {pasta_entrada}")
            return 0

        total = 0
        for pdf in arquivos:
            # Mantém a estrutura de subpastas no nome do arquivo de saída?
            # Opção: usar apenas o nome do arquivo (como antes)
            nome_saida = pasta_saida / f"{pdf.stem}.txt"
            extrair_pdf(str(pdf), str(nome_saida))
            total += 1

        print(f"\n📊 Total de PDFs extraídos: {total}")
        return total

    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao processar pasta {pasta_entrada}: {e}")
        return 0

if __name__ == "__main__":
    try:
        if len(sys.argv) >= 2:
            entrada = sys.argv[1]
            saida = sys.argv[2] if len(sys.argv) >= 3 else TRANSCRICOES_PASTA

            if os.path.isdir(entrada):
                extrair_pdfs_da_pasta(entrada, saida)
            else:
                nome_base = Path(entrada).stem
                saida_arquivo = Path(saida) / f"{nome_base}.txt"
                extrair_pdf(entrada, str(saida_arquivo))
        else:
            # Executa com valores padrão (pasta de PDFs e transcrições)
            print("Uso:")
            print(f"  python extrair_pdf.py pasta_com_pdfs/ [pasta_saida]")
            print(f"  python extrair_pdf.py arquivo.pdf [pasta_saida]")
            print("")
            print("Dica: execute com --debug para ver erros detalhados.")
            print("")
            print("Valores padrão (definidos em config.py):")
            print(f"  Pasta de entrada (PDFs): {PDFS_PASTA}")
            print(f"  Pasta de saída: {TRANSCRICOES_PASTA}")
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro na execução principal: {e}")
        sys.exit(1)