markdown
# 🧑‍🏫 Professor IA – Assistente de Estudos Local via Linha de Comando

![Python](https://img.shields.io/badge/Python-3.14-blue)
![LangChain](https://img.shields.io/badge/LangChain-1.0+-blue)
![Ollama](https://img.shields.io/badge/Ollama-Qwen3.5:4B-green)

> Assistente de estudos totalmente offline que utiliza RAG (Retrieval-Augmented Generation) com modelo local Qwen3.5 4B para responder perguntas com base em seus materiais (PDFs, imagens, vídeos).

---

## 🚀 Funcionalidades

- **Extração automática** de texto de PDFs, imagens (OCR com Tesseract) e vídeos (Whisper).
- **Limpeza e padronização** dos textos extraídos.
- **Criação de banco de dados vetorial** (FAISS) para busca semântica.
- **Respostas contextualizadas** usando Qwen3.5 4B via Ollama.
- **Privacidade total** – tudo roda localmente, sem dependência de nuvem.
- **Interface via terminal** – simples, direta e eficiente.

---

## 🧰 Tecnologias Utilizadas

- **Python 3.14**
- **LangChain** (FAISS, embeddings)
- **Ollama** (Qwen3.5 4B)
- **Tesseract OCR** (imagens)
- **Whisper** (áudio/vídeo)
- **PyPDF** (PDFs)
- **FAISS** (busca vetorial)

---

## 📦 Como Executar

### Pré-requisitos

Antes de começar, instale:
- [Python 3.14+](https://python.org)
- [Ollama](https://ollama.com)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- [FFmpeg](https://ffmpeg.org/download.html)

### Passos

1. **Clone o repositório**
   ```bash
   git clone https://github.com/ErickAdriano298/Professor-ia.git
   cd Professor-ia
Crie e ative um ambiente virtual

bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
Instale as dependências

bash
pip install -r requirements.txt
Baixe o modelo de linguagem

bash
ollama pull qwen3.5:4b
Coloque seus materiais de estudo nas pastas:

dados/pdfs/

dados/imagens/

dados/videos/

Extraia, limpe e crie o banco vetorial (tudo de uma vez):

bash
python scripts/extrator_unificado.py dados/ dados/transcricoes/
python scripts/limpar_texto.py dados/transcricoes/ dados/processados/
python scripts/criar_vector_db.py
Inicie o Professor IA

bash
python scripts/professor_ia.py
Faça perguntas no terminal. Digite sair para encerrar.

🗂️ Estrutura do Projeto
text
Professor-ia/
├── scripts/                 # Módulos principais
│   ├── professor_ia.py      # Lógica de perguntas e respostas
│   ├── criar_vector_db.py   # Criação do FAISS
│   ├── limpar_texto.py      # Limpeza de textos
│   ├── extrair_*.py         # Extratores (PDF, imagem, vídeo)
│   └── extrator_unificado.py
├── dados/                   # (ignorado pelo Git) seus materiais
├── requirements.txt
├── README.md
└── .gitignore
🧠 Exemplo de Uso
bash
🧑‍🎓 Você: O que é uma derivada?
🔍 Buscando contexto...
📚 3 trechos relevantes encontrados.
🧠 Gerando resposta com Qwen3.5 4B...

👨‍🏫 Professor: Segundo seu material, derivada é a taxa de variação instantânea. A derivada de f(x) = x² é 2x...
👨‍💻 Autor
Erick Adriano

https://img.shields.io/badge/GitHub-ErickAdriano298-181717?style=flat&logo=github
https://img.shields.io/badge/LinkedIn-Erick_Adriano-0A66C2?style=flat&logo=linkedin

⭐ Agradecimentos
LangChain

Ollama

Tesseract

Whisper

text