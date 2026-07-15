"""
Configurações centralizadas do Professor IA.
Altere os valores aqui para personalizar o comportamento do sistema.
"""

from pathlib import Path

# ===== PASTAS =====
DADOS_PASTA = "dados/"
TRANSCRICOES_PASTA = f"{DADOS_PASTA}transcricoes/"
PROCESSADOS_PASTA = f"{DADOS_PASTA}processados/"
VECTOR_DB_PASTA = f"{DADOS_PASTA}vector_db/"
AUDIOS_PASTA = f"{DADOS_PASTA}audios/"
PDFS_PASTA = f"{DADOS_PASTA}pdfs/"
IMAGENS_PASTA = f"{DADOS_PASTA}imagens/"
VIDEOS_PASTA = f"{DADOS_PASTA}videos/"

# ===== MODELO DE EMBEDDINGS (para o Vector DB) =====
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ===== MODELO DE LINGUAGEM (Ollama) =====
MODELO_LLM = "qwen3.5:4b"

# ===== VECTOR DB =====
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
K_BUSCA = 3

# ===== PARÂMETROS DO TESSERACT (OCR) =====
TESSERACT_LANG = "por"
TESSERACT_METODO = "otsu"

# ===== PARÂMETROS DO WHISPER =====
WHISPER_MODELO = "medium"
WHISPER_IDIOMA = "Portuguese"