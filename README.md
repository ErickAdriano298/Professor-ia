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