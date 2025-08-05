import requests
from dotenv import load_dotenv
import os
from datetime import datetime

# --- Carrega as configurações do arquivo .env ---
load_dotenv()
BOTCONVERSA_TOKEN = os.getenv('BOTCONVERSA_API_TOKEN')
BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1"

def verificar_leads_mais_recentes(limite=5):
    """Busca e exibe os 5 contatos mais recentes da conta no BotConversa."""
    print(f"Buscando os {limite} contatos mais recentes no BotConversa...")
    
    url = f"{BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    # Pede os mais recentes primeiro
    params = {'ordering': '-created_at'} 
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        dados = response.json()

        leads_recentes = dados.get('results', [])
        if not leads_recentes:
            print("A API não retornou nenhum contato.")
            return

        print(f"\n--- TOP {limite} CONTATOS MAIS RECENTES NA SUA CONTA ---")
        for i, inscrito in enumerate(leads_recentes[:limite]):
            nome = inscrito.get('full_name', 'Sem Nome')
            created_at = inscrito.get('created_at', 'Sem Data')
            print(f"{i+1}. Nome: {nome:<30} | Data de Criação: {created_at}")
        print("-------------------------------------------------")
    
    except Exception as e:
        print(f"ERRO ao buscar contatos: {e}")

if __name__ == "__main__":
    verificar_leads_mais_recentes()