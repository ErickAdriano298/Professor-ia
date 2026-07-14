"""
Cria um banco de dados vetorial (FAISS) a partir dos textos limpos.
"""

import pickle
from pathlib import Path

# Ainda uso langchain-community para carregadores locais, pois é o que funciona
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def criar_vector_db(
    pasta_textos: str = "dados/processados/",
    pasta_saida: str = "dados/vector_db/",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> FAISS:
    """
    Carrega os textos, gera embeddings e salva o índice FAISS.
    """
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
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("💾 Criando índice FAISS...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    Path(pasta_saida).mkdir(parents=True, exist_ok=True)
    vector_db.save_local(pasta_saida)

    # Salvo metadados para consulta futura (total de documentos, chunks, etc.)
    with open(Path(pasta_saida) / "metadados.pkl", "wb") as f:
        pickle.dump({
            "total_documentos": len(documentos),
            "total_chunks": len(chunks),
            "modelo_embeddings": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }, f)

    print(f"✅ Vector DB salvo em: {pasta_saida}")
    return vector_db

if __name__ == "__main__":
    criar_vector_db()