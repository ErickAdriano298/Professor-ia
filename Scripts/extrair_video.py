#!/usr/bin/env python3
"""
Extrator de áudio e transcrição de vídeos usando yt-dlp + Whisper.
"""

import subprocess
import os
from pathlib import Path
import sys

def extrair_audio_youtube(url_video, pasta_saida="dados/audios/"):
    """
    Baixa o áudio de um vídeo do YouTube em MP3.
    """
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
    
    # Pego o último arquivo MP3 baixado (o mais recente)
    arquivos_mp3 = list(Path(pasta_saida).glob("*.mp3"))
    if arquivos_mp3:
        return str(arquivos_mp3[-1])
    return None

def transcrever_audio(caminho_audio, pasta_saida="dados/transcricoes/"):
    """
    Transcreve o áudio usando Whisper (modelo medium para melhor precisão).
    """
    os.makedirs(pasta_saida, exist_ok=True)
    
    nome_base = Path(caminho_audio).stem
    caminho_saida = Path(pasta_saida) / f"{nome_base}.txt"
    
    # Uso a linha de comando do Whisper porque é mais simples de integrar
    cmd = [
        "whisper",
        caminho_audio,
        "--model", "medium",
        "--language", "Portuguese",
        "--output_dir", pasta_saida,
        "--output_format", "txt"
    ]
    
    print(f"🎤 Transcrevendo áudio: {caminho_audio}")
    subprocess.run(cmd, check=True)
    
    # O Whisper salva com um nome padrão; renomeio para manter consistência
    arquivo_whisper = Path(pasta_saida) / f"{nome_base}.txt"
    if arquivo_whisper.exists() and caminho_saida != arquivo_whisper:
        os.rename(arquivo_whisper, caminho_saida)
    
    print(f"✅ Transcrição salva: {caminho_saida}")
    return str(caminho_saida)

def processar_video_url(url_video, pasta_audio="dados/audios/", pasta_transcricao="dados/transcricoes/"):
    """
    Processa um vídeo do YouTube: baixa áudio e transcreve.
    """
    audio = extrair_audio_youtube(url_video, pasta_audio)
    if audio:
        return transcrever_audio(audio, pasta_transcricao)
    return None

def processar_video_local(caminho_video, pasta_saida="dados/transcricoes/"):
    """
    Processa um vídeo local: transcreve diretamente (já tenho o arquivo).
    """
    return transcrever_audio(caminho_video, pasta_saida)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        
        if entrada.startswith("http"):
            processar_video_url(entrada)  # URL do YouTube
        else:
            processar_video_local(entrada)  # Arquivo local
    else:
        print("Uso:")
        print("  python extrair_video.py https://youtube.com/watch?v=...")
        print("  python extrair_video.py video.mp4")