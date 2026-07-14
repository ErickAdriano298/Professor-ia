"""
Limpeza de textos extraídos para uso no Professor IA.
"""

import re
import unicodedata
from pathlib import Path
import sys

def limpar_texto(texto):
    """
    Aplica as regras de limpeza: remove ruídos, junta linhas quebradas, normaliza espaços e pontuação.
    """
    if not texto:
        return ""

    # Remove caracteres não imprimíveis (exceto quebras e tabs)
    texto = ''.join(ch for ch in texto if ch.isprintable() or ch in '\n\t')

    # Normaliza Unicode para remover variações invisíveis
    texto = unicodedata.normalize('NFKC', texto)

    # Remove cabeçalhos/rodapés comuns de páginas
    texto = re.sub(r'(?i)(página|page)\s+\d+\s+(de|of|/)\s+\d+', '', texto)
    texto = re.sub(r'-\s*\d+\s*-', '', texto)

    # Remove linhas com apenas números (numeração de página isolada)
    texto = re.sub(r'^\s*\d+\s*$', '', texto, flags=re.MULTILINE)

    # Junta linhas quebradas indevidamente (comum em PDFs)
    linhas = texto.split('\n')
    linhas_unidas = []
    for i, linha in enumerate(linhas):
        linha = linha.strip()
        if not linha:
            continue
        if i < len(linhas) - 1:
            proxima = linhas[i+1].strip()
            # Se a linha não termina com pontuação final e a próxima não começa com maiúscula
            if proxima and not re.search(r'[.!?;:]\s*$', linha) and not re.match(r'^[A-ZÇÃÕÁÉÍÓÚÂÊÔÀÈÌÒ]', proxima):
                linha += ' ' + proxima
                linhas[i+1] = ''  # Marca a próxima como já processada
        linhas_unidas.append(linha)

    texto = '\n'.join(linhas_unidas)

    # Remove espaços duplicados e ajusta pontuação
    texto = re.sub(r' +', ' ', texto)
    texto = re.sub(r' ([,.;:!?])', r'\1', texto)
    texto = re.sub(r'([,.;:!?])([^\s])', r'\1 \2', texto)

    # Remove quebras de linha excessivas e espaços nas bordas
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = texto.strip()

    return texto

def processar_arquivo(entrada, saida=None):
    """
    Lê um arquivo, limpa e salva o resultado.
    """
    try:
        with open(entrada, 'r', encoding='utf-8') as f:
            texto_bruto = f.read()

        texto_limpo = limpar_texto(texto_bruto)

        if saida is None:
            nome_base = Path(entrada).stem
            saida = Path(entrada).parent / f"{nome_base}_limpo.txt"
        else:
            saida = Path(saida)

        saida.parent.mkdir(parents=True, exist_ok=True)
        with open(saida, 'w', encoding='utf-8') as f:
            f.write(texto_limpo)

        print(f"✅ Texto limpo salvo: {saida}")
        return texto_limpo

    except Exception as e:
        print(f"❌ Erro ao processar {entrada}: {e}")
        return ""

def processar_pasta(entrada, saida="dados/processados/"):
    """
    Processa todos os arquivos .txt de uma pasta.
    """
    entrada = Path(entrada)
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)

    arquivos = list(entrada.glob("*.txt"))
    if not arquivos:
        print(f"ℹ️ Nenhum arquivo .txt encontrado em: {entrada}")
        return 0

    total = 0
    for arquivo in arquivos:
        nome_saida = saida / f"{arquivo.stem}_limpo.txt"
        processar_arquivo(str(arquivo), str(nome_saida))
        total += 1

    print(f"\n📊 Total de arquivos processados: {total}")
    return total

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        saida = sys.argv[2] if len(sys.argv) >= 3 else "dados/processados/"

        if Path(entrada).is_dir():
            processar_pasta(entrada, saida)
        else:
            processar_arquivo(entrada, saida)
    else:
        print("Uso:")
        print("  python limpar_texto.py pasta_com_textos/ pasta_saida/")
        print("  python limpar_texto.py arquivo.txt pasta_saida/")