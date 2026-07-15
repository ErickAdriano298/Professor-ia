"""
Cria um banco de dados vetorial (FAISS) a partir dos textos limpos.
"""

import pickle
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para importar config.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PROCESSADOS_PASTA,
    VECTOR_DB_PASTA,
    MODELO_EMBEDDINGS,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# Ainda uso langchain-community para carregadores locais, pois é o que funciona
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ===== MODO DEBUG =====
DEBUG = "--debug" in sys.argv

def criar_vector_db(
    pasta_textos: str = PROCESSADOS_PASTA,
    pasta_saida: str = VECTOR_DB_PASTA,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> FAISS:
    """
    Carrega os textos, gera embeddings e salva o índice FAISS.
    """
    try:
        print("📚 Carregando textos limpos...")
        loader = DirectoryLoader(
            pasta_textos,
            glob="*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documentos = loader.load()
        print(f"✅ {len(documentos)} documentos carregados.")

        print("✂️  Dividindo textos em chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len
        )
        chunks = splitter.split_documents(documentos)
        print(f"✅ {len(chunks)} chunks criados.")

        print("🧠 Gerando embeddings (pode levar alguns minutos)...")
        embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)

        print("💾 Criando índice FAISS...")
        vector_db = FAISS.from_documents(chunks, embeddings)

        Path(pasta_saida).mkdir(parents=True, exist_ok=True)
        vector_db.save_local(pasta_saida)

        # Salvo metadados para consulta futura
        with open(Path(pasta_saida) / "metadados.pkl", "wb") as f:
            pickle.dump({
                "total_documentos": len(documentos),
                "total_chunks": len(chunks),
                "modelo_embeddings": MODELO_EMBEDDINGS,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            }, f)

        print(f"✅ Vector DB salvo em: {pasta_saida}")
        return vector_db

    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao criar Vector DB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    criar_vector_db()