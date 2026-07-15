"""
Orquestrador do Professor IA – executa todos os passos em sequência.
"""

import subprocess
import sys
from pathlib import Path

# Importa configurações
from config import DADOS_PASTA, TRANSCRICOES_PASTA, PROCESSADOS_PASTA

def run_script(script, args=[]):
    """Executa um script Python e verifica se foi bem-sucedido."""
    cmd = ["python", f"scripts/{script}"] + args
    print(f"\n▶️ Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Erro em {script} (código {result.returncode})")
        sys.exit(1)
    print(f"✅ {script} concluído com sucesso!")

def main():
    print("🚀 Iniciando pipeline do Professor IA...")
    print(f"📁 Pasta de dados: {DADOS_PASTA}")
    print(f"📁 Pasta de transcrições: {TRANSCRICOES_PASTA}")
    print(f"📁 Pasta de textos processados: {PROCESSADOS_PASTA}")
    
    # 1. Extrair textos de todos os arquivos
    run_script("extrator_unificado.py", [DADOS_PASTA, TRANSCRICOES_PASTA])
    
    # 2. Limpar os textos extraídos
    run_script("limpar_texto.py", [TRANSCRICOES_PASTA, PROCESSADOS_PASTA])
    
    # 3. Criar o banco de dados vetorial
    run_script("criar_vector_db.py")
    
    # 4. Iniciar o Professor IA (modo interativo)
    print("\n✅ Pipeline concluído! Iniciando o Professor IA...")
    run_script("professor_ia.py")

if __name__ == "__main__":
    main()