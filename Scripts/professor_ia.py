"""
Professor IA - Integra Vector DB (FAISS) com Qwen3.5 4B via Ollama.
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para importar config.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    VECTOR_DB_PASTA,
    MODELO_EMBEDDINGS,
    MODELO_LLM,
    K_BUSCA
)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import ollama

# ===== MODO DEBUG =====
DEBUG = "--debug" in sys.argv

# ===== FUNÇÕES =====
def carregar_vector_db():
    """
    Carrega o banco de dados vetorial.
    """
    try:
        if not Path(VECTOR_DB_PASTA).exists():
            print(f"❌ Vector DB não encontrado em {VECTOR_DB_PASTA}")
            print("   Execute primeiro: python scripts/criar_vector_db.py")
            sys.exit(1)
        print("📚 Carregando Vector DB...")
        embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)

        # A flag allow_dangerous_deserialization=True é necessária para carregar
        # o índice FAISS salvo localmente. Como o índice é gerado pelo próprio
        # projeto, o risco de dados maliciosos é controlado.
        db = FAISS.load_local(
            VECTOR_DB_PASTA,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Vector DB carregado.")
        return db
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao carregar Vector DB: {e}")
        sys.exit(1)

def buscar_contexto(db, pergunta, k=K_BUSCA):
    """
    Busca os trechos mais relevantes no Vector DB.
    """
    try:
        docs = db.similarity_search(pergunta, k=k)
        contexto = "\n\n".join([doc.page_content for doc in docs])
        return contexto, docs
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro na busca de contexto: {e}")
        return "", []

def gerar_resposta(pergunta, contexto):
    """
    Envia pergunta + contexto para o Qwen3.5 4B via Ollama.
    """
    try:
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
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao gerar resposta: {e}")
        return "Desculpe, ocorreu um erro ao gerar a resposta."

# ===== MAIN =====
def main():
    print("🤖 Professor IA - Qwen3.5 4B")
    db = carregar_vector_db()
    print("\n✅ Pronto para perguntas! Digite 'sair' para encerrar.\n")

    while True:
        try:
            pergunta = input("🧑‍🎓 Você: ")
            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("👋 Até logo!")
                break

            print("🔍 Buscando contexto...")
            contexto, docs = buscar_contexto(db, pergunta)
            if not contexto:
                print("ℹ️ Nenhum trecho relevante encontrado.")
                continue
            print(f"📚 {len(docs)} trechos relevantes encontrados.")

            print("🧠 Gerando resposta...")
            resposta = gerar_resposta(pergunta, contexto)
            print(f"\n👨‍🏫 Professor: {resposta}\n")

        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            if DEBUG:
                import traceback
                traceback.print_exc()
            else:
                print(f"❌ Erro inesperado: {e}")
                print("   Tente novamente ou execute com --debug para mais detalhes.")

if __name__ == "__main__":
    main()