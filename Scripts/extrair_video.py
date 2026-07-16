#!/usr/bin/env python3
"""
Extrator de áudio e transcrição de vídeos usando yt-dlp + Whisper.
"""

import subprocess
import os
import sys
import time
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para importar config.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    AUDIOS_PASTA,
    TRANSCRICOES_PASTA,
    WHISPER_MODELO,
    WHISPER_IDIOMA
)

# ===== MODO DEBUG =====
DEBUG = "--debug" in sys.argv

def extrair_audio_youtube(url_video, pasta_saida=AUDIOS_PASTA):
    """
    Baixa o áudio de um vídeo do YouTube em MP3.
    """
    try:
        os.makedirs(pasta_saida, exist_ok=True)

        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", f"{pasta_saida}/%(title)s.%(ext)s",
            url_video
        ]

        print(f"🎵 Baixando áudio de: {url_video}")
        subprocess.run(cmd, check=True)

        # Pega o arquivo MP3 mais recente (pela data de modificação)
        arquivos_mp3 = list(Path(pasta_saida).glob("*.mp3"))
        if arquivos_mp3:
            audio_mais_recente = max(arquivos_mp3, key=lambda p: p.stat().st_mtime)
            return str(audio_mais_recente)
        return None

    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao baixar áudio: {e}")
        return None

def transcrever_audio(caminho_audio, pasta_saida=TRANSCRICOES_PASTA):
    """
    Transcreve o áudio usando Whisper.
    """
    try:
        os.makedirs(pasta_saida, exist_ok=True)

        nome_base = Path(caminho_audio).stem
        caminho_saida = Path(pasta_saida) / f"{nome_base}.txt"

        # Uso a linha de comando do Whisper porque é mais simples de integrar
        cmd = [
            "whisper",
            caminho_audio,
            "--model", WHISPER_MODELO,
            "--language", WHISPER_IDIOMA,
            "--output_dir", pasta_saida,
            "--output_format", "txt"
        ]

        print(f"🎤 Transcrevendo áudio: {caminho_audio}")
        subprocess.run(cmd, check=True)

        # O Whisper pode salvar com nome diferente (ex: adiciona sufixo).
        # Vamos garantir que o arquivo final tenha o nome esperado.
        arquivo_whisper = Path(pasta_saida) / f"{nome_base}.txt"
        if arquivo_whisper.exists() and arquivo_whisper != caminho_saida:
            if not caminho_saida.exists():
                os.rename(arquivo_whisper, caminho_saida)
        elif not caminho_saida.exists() and arquivo_whisper.exists():
            os.rename(arquivo_whisper, caminho_saida)

        # Se ainda não existe, algo deu errado – procura por variações
        if not caminho_saida.exists():
            possiveis = list(Path(pasta_saida).glob(f"{nome_base}*.txt"))
            if possiveis:
                ultimo = max(possiveis, key=lambda p: p.stat().st_mtime)
                os.rename(ultimo, caminho_saida)

        print(f"✅ Transcrição salva: {caminho_saida}")
        return str(caminho_saida)

    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao transcrever áudio: {e}")
        return None

def processar_video_url(url_video, pasta_audio=AUDIOS_PASTA, pasta_transcricao=TRANSCRICOES_PASTA):
    """
    Processa um vídeo do YouTube: baixa áudio e transcreve.
    """
    try:
        audio = extrair_audio_youtube(url_video, pasta_audio)
        if audio:
            return transcrever_audio(audio, pasta_transcricao)
        return None
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao processar URL: {e}")
        return None

def processar_video_local(caminho_video, pasta_saida=TRANSCRICOES_PASTA):
    """
    Processa um vídeo local: transcreve diretamente (já tenho o arquivo).
    """
    try:
        return transcrever_audio(caminho_video, pasta_saida)
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao processar vídeo local: {e}")
        return None

# ===== NOVA FUNÇÃO PARA PROCESSAR PASTA RECURSIVAMENTE =====
def extrair_videos_da_pasta(pasta_entrada, pasta_saida=TRANSCRICOES_PASTA):
    """
    Processa todos os vídeos de uma pasta e subpastas recursivamente.
    """
    try:
        pasta_entrada = Path(pasta_entrada)
        pasta_saida = Path(pasta_saida)
        pasta_saida.mkdir(parents=True, exist_ok=True)

        extensoes = [".mp4", ".avi", ".mkv", ".mov", ".webm"]
        arquivos = []
        for ext in extensoes:
            arquivos.extend(pasta_entrada.rglob(f"*{ext}"))
            arquivos.extend(pasta_entrada.rglob(f"*{ext.upper()}"))

        if not arquivos:
            print(f"ℹ️ Nenhum vídeo encontrado em: {pasta_entrada}")
            return 0

        total = 0
        for video in arquivos:
            print(f"\n🎬 Processando: {video}")
            resultado = processar_video_local(str(video), str(pasta_saida))
            if resultado:
                total += 1

        print(f"\n📊 Total de vídeos processados: {total}")
        return total

    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro ao processar pasta {pasta_entrada}: {e}")
        return 0

if __name__ == "__main__":
    try:
        if len(sys.argv) >= 2:
            entrada = sys.argv[1]

            if entrada.startswith("http"):
                processar_video_url(entrada)  # URL do YouTube
            else:
                # Verifica se é uma pasta ou arquivo
                if os.path.isdir(entrada):
                    extrair_videos_da_pasta(entrada)
                else:
                    processar_video_local(entrada)  # Arquivo local
        else:
            print("Uso:")
            print("  python extrair_video.py https://youtube.com/watch?v=...")
            print("  python extrair_video.py video.mp4")
            print("  python extrair_video.py pasta_com_videos/")
            print("")
            print("Dica: execute com --debug para ver erros detalhados.")
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro na execução principal: {e}")
        sys.exit(1)