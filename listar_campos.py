import requests
from dotenv import load_dotenv
import os

# --- Carrega as configurações do arquivo .env ---
load_dotenv()
RDSTATION_TOKEN = os.getenv('RDSTATION_CRM_TOKEN')
BOTCONVERSA_TOKEN = os.getenv('BOTCONVERSA_API_TOKEN')

RDSTATION_BASE_URL = "https://crm.rdstation.com/api/v1"
BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1"

def listar_campos_rdstation():
    """Busca e lista todos os campos personalizados de negociações (deals) no RD Station."""
    print("Buscando campos do RD Station...")
    if not RDSTATION_TOKEN:
        print("-> ERRO: Token do RD Station não encontrado no arquivo .env")
        return

    try:
        url = f"{RDSTATION_BASE_URL}/custom_fields"
        params = {'token': RDSTATION_TOKEN}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        dados = response.json()
        
        print("\n--- CAMPOS PERSONALIZADOS DO RD STATION (Negociações) ---")
        for campo in dados:
            if campo.get('for') == 'deal':
                nome_campo = campo.get('label', 'Nome não encontrado')
                id_campo = campo.get('id', 'ID não encontrado')
                print(f"{nome_campo} - {id_campo}")
        
    except requests.exceptions.RequestException as e:
        print(f"-> FALHA ao buscar campos do RD Station: {e}")

def listar_campos_botconversa():
    """Busca e lista os campos do BotConversa usando a chave correta 'key'."""
    print("\nBuscando campos do BotConversa...")
    if not BOTCONVERSA_TOKEN:
        print("-> ERRO: Token do BotConversa não encontrado no arquivo .env")
        return

    headers = {"API-KEY": BOTCONVERSA_TOKEN}

    endpoints_para_buscar = {
        "Campos do Robô (Variáveis)": "/webhook/bot_fields/",
        "Campos Personalizados (Audiência)": "/webhook/custom_fields/"
    }

    try:
        for titulo, endpoint in endpoints_para_buscar.items():
            url = f"{BOTCONVERSA_BASE_URL}{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            
            print(f"\n--- {titulo.upper()} DO BOTCONVERSA ---")
            
            for campo in dados:
                # --- CORREÇÃO FINAL AQUI ---
                # Trocamos 'name' por 'key' para ler o nome do campo corretamente
                nome_campo = campo.get('key', 'Nome não encontrado')
                # -------------------------
                id_campo = campo.get('id', 'ID não encontrado')
                print(f"{nome_campo} - {id_campo}")

    except requests.exceptions.RequestException as e:
        print(f"-> FALHA ao buscar campos do BotConversa: {e}")

if __name__ == "__main__":
    print("--- INICIANDO SCRIPT DE MAPEAMENTO DE CAMPOS ---")
    listar_campos_rdstation()
    listar_campos_botconversa()
    print("\n--- MAPEAMENTO CONCLUÍDO ---")