"""
Interface web para o Professor IA usando Streamlit.
Reaproveita as funções de professor_ia.py, extrator_unificado.py,
limpar_texto.py e criar_vector_db.py.
"""

import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# ===== CONFIGURAÇÃO DE PATH =====
ROOT_DIR = Path(__file__).parent
SCRIPTS_DIR = ROOT_DIR / "Scripts"
if not SCRIPTS_DIR.exists():
    SCRIPTS_DIR = ROOT_DIR / "scripts"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

# ===== IMPORTS =====
import streamlit as st
import ollama

try:
    from professor_ia import carregar_vector_db, buscar_contexto, gerar_resposta
    from extrator_unificado import processar_arquivo as extrair_arquivo
    from extrair_video import processar_video_url
    from limpar_texto import processar_pasta as limpar_pasta
    from criar_vector_db import criar_vector_db
    from config import (
        PDFS_PASTA, IMAGENS_PASTA, VIDEOS_PASTA, AUDIOS_PASTA,
        TRANSCRICOES_PASTA, PROCESSADOS_PASTA
    )
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos do projeto: {e}")
    st.info("Certifique-se de que a pasta 'Scripts/' e o 'config.py' existem na raiz.")
    st.stop()

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Professor IA",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

EXTENSOES_SUPORTADAS = {
    ".pdf": PDFS_PASTA,
    ".jpg": IMAGENS_PASTA, ".jpeg": IMAGENS_PASTA, ".png": IMAGENS_PASTA,
    ".bmp": IMAGENS_PASTA, ".tiff": IMAGENS_PASTA,
    ".mp4": VIDEOS_PASTA, ".avi": VIDEOS_PASTA, ".mkv": VIDEOS_PASTA, ".mov": VIDEOS_PASTA,
}


# ===== STATUS (CACHEADOS COM TTL CURTO) =====
@st.cache_data(ttl=30)
def verificar_ollama() -> bool:
    """Verifica se o Ollama está rodando. Cacheado por 30s para não bater
    na rede a cada rerun do Streamlit."""
    try:
        ollama.list()
        return True
    except Exception:
        return False


@st.cache_resource
def get_vector_db():
    """Carrega o Vector DB uma única vez por sessão de servidor."""
    return carregar_vector_db()


# ===== FUNÇÕES DE CHAT =====
def extrair_fontes(docs: List[Any], max_trecho: int = 300) -> List[Dict[str, str]]:
    """Converte documentos em dicts com nome do arquivo e trecho."""
    fontes = []
    for doc in docs:
        caminho = doc.metadata.get("source", "Fonte desconhecida")
        nome_arquivo = Path(caminho).name if caminho != "Fonte desconhecida" else caminho
        fontes.append({
            "arquivo": nome_arquivo,
            "caminho": caminho,
            "trecho": doc.page_content[:max_trecho] + ("..." if len(doc.page_content) > max_trecho else "")
        })
    return fontes


def render_fontes(fontes: List[Dict[str, str]], expanded: bool = False):
    """Renderiza a lista de fontes consultadas."""
    if not fontes:
        return
    with st.expander(f"📚 Fontes consultadas ({len(fontes)})", expanded=expanded):
        for fonte in fontes:
            st.caption(f"**Arquivo:** `{fonte['arquivo']}`")
            st.text(fonte["trecho"])


def gerar_markdown_conversa(historico: List[Dict[str, Any]]) -> str:
    """Monta o markdown de exportação a partir do histórico."""
    conteudo = "# Conversa com Professor IA\n\n"
    for item in historico:
        conteudo += f"## Pergunta\n{item['pergunta']}\n\n"
        conteudo += f"## Resposta\n{item['resposta']}\n\n"
        if item["fontes"]:
            conteudo += "### Fontes\n"
            for fonte in item["fontes"]:
                conteudo += f"- {fonte['arquivo']}\n"
            conteudo += "\n"
    return conteudo


# ===== FUNÇÕES DE INGESTÃO DE MATERIAL =====
def salvar_upload(arquivo_upload) -> Path:
    """Salva um arquivo enviado pela interface na pasta correta de config.py,
    de acordo com a extensão (livro/pdf, imagem, vídeo)."""
    extensao = Path(arquivo_upload.name).suffix.lower()
    pasta_destino = EXTENSOES_SUPORTADAS.get(extensao)
    if pasta_destino is None:
        raise ValueError(f"Extensão não suportada: {extensao}")

    Path(pasta_destino).mkdir(parents=True, exist_ok=True)
    caminho_destino = Path(pasta_destino) / arquivo_upload.name
    with open(caminho_destino, "wb") as f:
        f.write(arquivo_upload.getbuffer())
    return caminho_destino


def processar_material(
    arquivos_upload: List[Any],
    links_youtube: List[str],
    progresso
) -> Dict[str, int]:
    """Processa arquivos enviados + links do YouTube: extrai texto,
    limpa e reconstrói o Vector DB. Retorna um resumo do que foi feito."""
    resumo = {"processados": 0, "falhas": 0}
    total_passos = len(arquivos_upload) + len(links_youtube) + 2  # +2: limpeza e reindexação
    passo_atual = 0

    def avancar(msg):
        nonlocal passo_atual
        passo_atual += 1
        progresso.progress(min(passo_atual / total_passos, 1.0), text=msg)

    # 1. Salva e extrai texto dos arquivos enviados
    for arquivo_upload in arquivos_upload:
        try:
            caminho = salvar_upload(arquivo_upload)
            avancar(f"📄 Extraindo texto de {arquivo_upload.name}...")
            extrair_arquivo(str(caminho), TRANSCRICOES_PASTA)
            resumo["processados"] += 1
        except Exception as e:
            resumo["falhas"] += 1
            st.warning(f"⚠️ Falha ao processar {arquivo_upload.name}: {e}")

    # 2. Processa links do YouTube
    for link in links_youtube:
        link = link.strip()
        if not link:
            continue
        try:
            avancar(f"🎬 Transcrevendo vídeo: {link}...")
            processar_video_url(link, AUDIOS_PASTA, TRANSCRICOES_PASTA)
            resumo["processados"] += 1
        except Exception as e:
            resumo["falhas"] += 1
            st.warning(f"⚠️ Falha ao processar {link}: {e}")

    # 3. Limpa os textos extraídos
    avancar("🧹 Limpando textos extraídos...")
    limpar_pasta(TRANSCRICOES_PASTA, PROCESSADOS_PASTA)

    # 4. Reconstrói o Vector DB com todo o material (antigo + novo)
    avancar("🧠 Reindexando Vector DB...")
    criar_vector_db()

    progresso.progress(1.0, text="✅ Concluído!")
    return resumo


# ===== ESTADO DO DB =====
db = None
db_erro = None
try:
    db = get_vector_db()
except Exception as e:
    db_erro = str(e)

ollama_ok = verificar_ollama()

# ===== SIDEBAR =====
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.title("🧑‍🏫 Professor IA")
    st.caption("RAG local com Qwen3.5 4B")

    st.divider()

    st.markdown("### 📊 Status")
    st.write(f"🟢 Ollama: {'✅ Conectado' if ollama_ok else '❌ Offline'}")
    st.write(f"📚 Vector DB: {'✅ Carregado' if db is not None else '❌ Não encontrado'}")
    if db_erro:
        st.info("Adicione material na aba '📥 Materiais' ou execute `python pipeline.py`.")

    st.divider()

    st.markdown("### ⚙️ Parâmetros")
    k = st.slider(
        "Número de chunks recuperados (k)",
        min_value=1,
        max_value=10,
        value=3,
        help="Quantos trechos do seu material serão usados para embasar a resposta."
    )

    st.divider()

    st.markdown("### 🛠️ Ações")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.historico = []
        st.rerun()

    if st.session_state.get("historico"):
        st.download_button(
            label="📥 Exportar conversa (Markdown)",
            data=gerar_markdown_conversa(st.session_state.historico),
            file_name=f"conversa_professor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.caption("Nenhuma conversa para exportar ainda.")

    st.divider()
    st.caption("Tudo roda localmente – seus dados não saem do seu computador.")

# ===== CABEÇALHO =====
st.title("🧑‍🏫 Professor IA")
st.caption("Seu assistente de estudos offline, com RAG e Qwen3.5 4B")

aba_chat, aba_materiais = st.tabs(["💬 Perguntas", "📥 Materiais"])

# =====================================================================
# ABA: CHAT
# =====================================================================
with aba_chat:
    if db is None:
        st.error(f"❌ Erro ao carregar Vector DB: {db_erro}")
        st.info("Vá para a aba '📥 Materiais' para adicionar seu primeiro conteúdo.")
    else:
        if "historico" not in st.session_state:
            st.session_state.historico = []

        for item in st.session_state.historico:
            with st.chat_message("user"):
                st.write(item["pergunta"])
            with st.chat_message("assistant"):
                st.write(item["resposta"])
                render_fontes(item["fontes"])

        pergunta = st.chat_input("Digite sua pergunta sobre seus materiais de estudo...")

        if pergunta:
            if not ollama_ok:
                st.error("❌ Ollama não está rodando. Inicie com `ollama serve` ou `ollama run qwen3.5:4b`.")
                st.stop()

            with st.chat_message("user"):
                st.write(pergunta)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("⏳ _Buscando contexto..._")

                inicio = time.time()
                fontes = []

                try:
                    contexto, docs = buscar_contexto(db, pergunta, k=k)
                    if not contexto:
                        resposta = "ℹ️ Nenhum trecho relevante encontrado nos seus materiais."
                    else:
                        placeholder.markdown(f"📚 _{len(docs)} trechos encontrados._\n\n⏳ _Gerando resposta..._")
                        resposta = gerar_resposta(pergunta, contexto)
                        fontes = extrair_fontes(docs)
                except Exception as e:
                    resposta = f"❌ Erro ao processar sua pergunta: {e}"

                tempo = time.time() - inicio
                placeholder.empty()

                st.write(resposta)
                render_fontes(fontes)
                st.caption(f"⏱️ Tempo de resposta: {tempo:.2f}s")

            st.session_state.historico.append({
                "pergunta": pergunta,
                "resposta": resposta,
                "fontes": fontes
            })

# =====================================================================
# ABA: ADICIONAR MATERIAL
# =====================================================================
with aba_materiais:
    st.markdown("### 📥 Adicionar novo material de estudo")
    st.caption(
        "Envie livros/PDFs, capturas de página (imagens) ou cole links de vídeos do "
        "YouTube. O material é extraído, limpo e adicionado ao Vector DB automaticamente."
    )

    col_arquivos, col_video = st.columns(2)

    with col_arquivos:
        st.markdown("#### 📄 Livros, PDFs e imagens")
        arquivos_upload = st.file_uploader(
            "Arraste ou selecione arquivos",
            type=["pdf", "jpg", "jpeg", "png", "bmp", "tiff"],
            accept_multiple_files=True,
            help="PDFs de livros/apostilas e fotos de páginas (será aplicado OCR automaticamente)."
        )

    with col_video:
        st.markdown("#### 🎬 Vídeos do YouTube")
        links_texto = st.text_area(
            "Cole um ou mais links (um por linha)",
            placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/...",
            height=150,
            help="Cada vídeo será transcrito com Whisper e adicionado ao material de estudo."
        )
        links_youtube = [l for l in links_texto.split("\n") if l.strip()]

    st.divider()

    tem_material = bool(arquivos_upload) or bool(links_youtube)
    if st.button(
        "🚀 Processar e adicionar ao Professor IA",
        type="primary",
        disabled=not tem_material,
        use_container_width=True
    ):
        progresso = st.progress(0.0, text="Iniciando processamento...")
        with st.spinner("Isso pode levar alguns minutos, dependendo do tamanho do material..."):
            resumo = processar_material(arquivos_upload or [], links_youtube, progresso)

        if resumo["processados"] > 0:
            st.success(
                f"✅ {resumo['processados']} item(ns) processado(s) e adicionado(s) ao Vector DB!"
            )
            # Invalida o cache do DB para forçar recarregar com o novo conteúdo
            get_vector_db.clear()
            db = get_vector_db()

        if resumo["falhas"] > 0:
            st.warning(f"⚠️ {resumo['falhas']} item(ns) falharam. Veja os avisos acima.")

    if not tem_material:
        st.caption("Selecione arquivos ou cole links para habilitar o processamento.")