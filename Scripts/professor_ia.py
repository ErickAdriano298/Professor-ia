"""
Professor IA - Integra Vector DB (FAISS) com Qwen3.5 4B via Ollama.
"""

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import ollama
import sys
from pathlib import Path

# ===== CONFIGURAÇÕES =====
PASTA_VECTOR_DB = "dados/vector_db/"
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODELO_LLM = "qwen3.5:4b"  # Testado e funcionando no meu notebook

# ===== FUNÇÕES =====
def carregar_vector_db():
    """Carrega o banco de dados vetorial."""
    print("📚 Carregando Vector DB...")
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)
    db = FAISS.load_local(
        PASTA_VECTOR_DB,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("✅ Vector DB carregado.")
    return db

def buscar_contexto(db, pergunta, k=3):
    """Busca os trechos mais relevantes no Vector DB."""
    docs = db.similarity_search(pergunta, k=k)
    contexto = "\n\n".join([doc.page_content for doc in docs])
    return contexto, docs

def gerar_resposta(pergunta, contexto):
    """Envia pergunta + contexto para o Qwen3.5 4B via Ollama."""
    prompt = f"""Você é um professor especialista. Use o contexto abaixo para responder à pergunta do aluno.

Contexto:
{contexto}

Pergunta do aluno: {pergunta}

Resposta (seja didático, dê exemplos e aponte se a pergunta não estiver no contexto):"""
    
    resposta = ollama.chat(
        model=MODELO_LLM,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return resposta["message"]["content"]

# ===== MAIN =====
def main():
    print("🤖 Professor IA - Qwen3.5 4B")
    db = carregar_vector_db()
    print("\n✅ Pronto para perguntas! Digite 'sair' para encerrar.\n")
    
    while True:
        pergunta = input("🧑‍🎓 Você: ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("👋 Até logo!")
            break
        
        print("🔍 Buscando contexto...")
        contexto, docs = buscar_contexto(db, pergunta)
        print(f"📚 {len(docs)} trechos relevantes encontrados.")
        
        print("🧠 Gerando resposta...")
        resposta = gerar_resposta(pergunta, contexto)
        print(f"\n👨‍🏫 Professor: {resposta}\n")

if __name__ == "__main__":
    main()