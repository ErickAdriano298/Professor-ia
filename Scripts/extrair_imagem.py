"""
Extrator de texto de imagens usando Tesseract OCR
Com pré-processamento avançado (Otsu, contraste, remoção de ruído)
"""

from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import os
import re
import cv2
import numpy as np
from pathlib import Path
import sys

# Caminho do Tesseract no meu sistema (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ===== PRÉ-PROCESSAMENTO =====
def preprocessar_imagem(caminho_entrada, caminho_saida=None, 
                        metodo_binarizacao='otsu',
                        limiar=150, 
                        redimensionar=True,
                        largura_minima=1200,
                        remover_ruido=True,
                        ajustar_contraste=True,
                        preservar_espacos=True):
    """
    Aplica pré-processamento na imagem antes do OCR.
    """
    print("🔧 Pré-processando imagem...")
    
    # Abro e converto para escala de cinza (modo 'L')
    imagem = Image.open(caminho_entrada)
    if imagem.mode != 'L':
        imagem = imagem.convert('L')
    
    # Aumento o contraste para melhorar a leitura
    if ajustar_contraste:
        enhancer = ImageEnhance.Contrast(imagem)
        imagem = enhancer.enhance(1.5)
    
    # Removo ruído com filtro mediano (ajuda em imagens com fundo sujo)
    if remover_ruido:
        imagem = imagem.filter(ImageFilter.MedianFilter(size=3))
    
    # Redimensiono se a imagem for muito pequena (mínimo 1200px de largura)
    if redimensionar and imagem.width < largura_minima:
        fator_escala = largura_minima / imagem.width
        novo_tamanho = (int(imagem.width * fator_escala), 
                        int(imagem.height * fator_escala))
        imagem = imagem.resize(novo_tamanho, Image.Resampling.LANCZOS)
        print(f"🔍 Redimensionado para: {novo_tamanho}")
    
    # Binarização: converto para preto e branco
    if metodo_binarizacao == 'otsu':
        try:
            # Uso OpenCV para calcular o limiar automático (Otsu)
            array = np.array(imagem, dtype=np.uint8)
            _, limiar_otsu = cv2.threshold(array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            imagem = imagem.point(lambda p: 255 if p > limiar_otsu else 0, '1')
        except Exception as e:
            print(f"⚠️ Otsu falhou: {e}. Usando adaptativo.")
            metodo_binarizacao = 'adaptativo'
    
    if metodo_binarizacao == 'adaptativo':
        # Limiar suave para preservar espaços entre palavras
        limiar_suave = 180 if preservar_espacos else 150
        imagem = imagem.point(lambda p: 255 if p > limiar_suave else 0, '1')
    
    elif metodo_binarizacao == 'fixo':
        limiar_final = 180 if (preservar_espacos and limiar > 150) else limiar
        imagem = imagem.point(lambda p: 255 if p > limiar_final else 0, '1')
    
    # Aumento a nitidez da imagem binarizada
    imagem = imagem.filter(ImageFilter.SHARPEN)
    
    if caminho_saida:
        imagem.save(caminho_saida, dpi=(300, 300))
        print(f"✅ Imagem pré-processada salva: {caminho_saida}")
    
    return imagem

# ===== FUNÇÃO PARA CORRIGIR ESPAÇOS =====
def corrigir_espacos(texto):
    """
    Insere espaços onde o Tesseract juntou palavras indevidamente.
    """
    if not texto:
        return texto
    
    # Insere espaço antes de maiúscula que vem depois de minúscula
    texto = re.sub(r'([a-zçãõáéíóúâêôàèìò])([A-ZÇÃÕÁÉÍÓÚÂÊÔÀÈÌÒ])', r'\1 \2', texto)
    
    # Insere espaço entre letra e número (ex: "A1" → "A 1")
    texto = re.sub(r'([A-Za-z])(\d)', r'\1 \2', texto)
    texto = re.sub(r'(\d)([A-Za-z])', r'\1 \2', texto)
    
    # Remove espaços duplicados
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

# ===== EXTRAÇÃO PRINCIPAL =====
def extrair_imagem(caminho_imagem, caminho_saida=None, idioma='por', 
                   metodo_binarizacao='otsu', preservar_espacos=True):
    """
    Extrai texto de uma imagem com pré-processamento e correção de espaços.
    """
    try:
        print(f"📷 Processando: {caminho_imagem}")
        print(f"🧠 Usando modelo: {idioma}")
        print(f"⚙️  Método: {metodo_binarizacao}")
        
        imagem_processada = preprocessar_imagem(
            caminho_imagem,
            caminho_saida=None,
            metodo_binarizacao=metodo_binarizacao,
            preservar_espacos=preservar_espacos
        )
        
        # Configuração: preservo espaços e uso whitelist de caracteres em português
        config = "--psm 6 --oem 3 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789çÇãÃõÕáÁéÉíÍóÓúÚâÂêÊôÔàÀèÈìÌòÙ.,;:- "
        
        texto = pytesseract.image_to_string(imagem_processada, lang=idioma, config=config)
        texto = texto.strip()
        
        texto = corrigir_espacos(texto)
        
        if caminho_saida:
            Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write(texto)
            print(f"✅ OCR concluído: {caminho_saida}")
        
        return texto
    
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado '{caminho_imagem}'")
        return ""
    
    except pytesseract.pytesseract.TesseractError as e:
        if "por_best" in str(e):
            print("❌ Erro: Modelo 'por_best' não encontrado.")
            print(r"   Execute como administrador:")
            print(r"   Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata_best/raw/main/por.traineddata' -OutFile 'C:\Program Files\Tesseract-OCR\tessdata\por_best.traineddata' -UseBasicParsing")
        else:
            print(f"❌ Erro no Tesseract: {e}")
        return ""
    
    except Exception as e:
        print(f"❌ Erro ao processar {caminho_imagem}: {e}")
        return ""

# ===== PROCESSAR PASTA =====
def extrair_imagens_da_pasta(pasta_entrada, pasta_saida, idioma='por', 
                             metodo_binarizacao='otsu'):
    """
    Processa todas as imagens de uma pasta.
    """
    pasta_entrada = Path(pasta_entrada)
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
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
        extrair_imagem(str(imagem), str(nome_saida), idioma, metodo_binarizacao)
        total += 1
    
    print(f"\n📊 Total de imagens processadas: {total}")
    return total

# ===== MAIN =====
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        saida = sys.argv[2] if len(sys.argv) >= 3 else "dados/transcricoes/"
        idioma = sys.argv[3] if len(sys.argv) >= 4 else "por"
        metodo = sys.argv[4] if len(sys.argv) >= 5 else "otsu"
        
        if os.path.isdir(entrada):
            extrair_imagens_da_pasta(entrada, saida, idioma, metodo)
        else:
            nome_base = Path(entrada).stem
            saida_arquivo = Path(saida) / f"{nome_base}.txt"
            extrair_imagem(entrada, str(saida_arquivo), idioma, metodo)
    else:
        print("Uso:")
        print("  python extrair_imagem.py pasta_com_imagens/ pasta_saida/ [idioma] [metodo]")
        print("")
        print("Idiomas disponíveis:")
        print("  por       - Padrão (rápido)")
        print("  por_best  - Alta precisão (mais lento)")
        print("")
        print("Métodos de binarização:")
        print("  otsu       - Automático (requer OpenCV) [padrão]")
        print("  adaptativo - Limiar suave (preserva espaços)")
        print("  fixo       - Limiar fixo (use com cuidado)")