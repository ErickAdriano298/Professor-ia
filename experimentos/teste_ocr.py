"""
Extrator de texto de imagens usando Tesseract OCR
"""

from PIL import Image
import pytesseract
import os
from pathlib import Path
import sys

# 🔧 Especifica o caminho do Tesseract (se necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extrair_imagem(caminho_imagem, caminho_saida=None, idioma='por'):
    """
    Extrai texto de uma imagem usando OCR
    
    Args:
        caminho_imagem (str): Caminho para o arquivo de imagem
        caminho_saida (str, opcional): Onde salvar o .txt
        idioma (str): Código do idioma (padrão: 'por')
    
    Returns:
        str: Texto extraído
    """
    try:
        # Abre a imagem
        imagem = Image.open(caminho_imagem)
        
        # Configuração para melhor precisão
        config = "--psm 6 --oem 3"
        
        # Extrai o texto
        texto = pytesseract.image_to_string(imagem, lang=idioma, config=config)
        texto = texto.strip()
        
        # Salva se caminho_saida for fornecido
        if caminho_saida:
            Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write(texto)
            print(f"✅ OCR concluído: {caminho_saida}")
        
        return texto
    
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado '{caminho_imagem}'")
        return ""
    
    except Exception as e:
        print(f"❌ Erro ao processar {caminho_imagem}: {e}")
        return ""

def extrair_imagens_da_pasta(pasta_entrada, pasta_saida):
    """
    Extrai texto de todas as imagens de uma pasta
    """
    pasta_entrada = Path(pasta_entrada)
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    # Extensões suportadas
    extensoes = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    arquivos = []
    
    for ext in extensoes:
        arquivos.extend(pasta_entrada.glob(f"*{ext}"))
        arquivos.extend(pasta_entrada.glob(f"*{ext.upper()}"))
    
    if not arquivos:
        print(f"ℹ️ Nenhuma imagem encontrada em: {pasta_entrada}")
        return 0
    
    total = 0
    for imagem in arquivos:
        nome_saida = pasta_saida / f"{imagem.stem}.txt"
        extrair_imagem(str(imagem), str(nome_saida))
        total += 1
    
    print(f"\n📊 Total de imagens processadas: {total}")
    return total

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        saida = sys.argv[2] if len(sys.argv) >= 3 else "dados/transcricoes/"
        
        if os.path.isdir(entrada):
            extrair_imagens_da_pasta(entrada, saida)
        else:
            nome_base = Path(entrada).stem
            saida_arquivo = Path(saida) / f"{nome_base}.txt"
            extrair_imagem(entrada, str(saida_arquivo))
    else:
        print("Uso:")
        print("  python extrair_imagem.py pasta_com_imagens/ pasta_saida/")
        print("  python extrair_imagem.py imagem.png pasta_saida/")