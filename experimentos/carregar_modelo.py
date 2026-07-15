"""
Carreguei este modelo para testar o Professor IA localmente.
Usei o Qwen2.5-1.5B porque é leve e tem bom suporte para português.
Depois migrei para o Qwen3.5:4b via Ollama, mas mantive este script como referência.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

def carregar_modelo():
    print("🧠 Carregando modelo Qwen2.5-1.5B...")
    modelo_nome = "Qwen/Qwen2.5-1.5B-Instruct"
    
    # trust_remote_code=True porque o modelo precisa de configurações específicas
    tokenizer = AutoTokenizer.from_pretrained(modelo_nome, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        modelo_nome,
        torch_dtype=torch.float16,  # Reduz uso de memória
        device_map="auto",          # Deixa o PyTorch decidir GPU/CPU
        trust_remote_code=True
    )
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.7,
        do_sample=True,
        top_p=0.95
    )
    
    print("✅ Modelo carregado com sucesso!")
    return pipe

if __name__ == "__main__":
    pipe = carregar_modelo()
    resposta = pipe("Olá! Me ensine sobre o que você sabe.")[0]['generated_text']
    print("\n🧪 Teste do modelo:")
    print(resposta)