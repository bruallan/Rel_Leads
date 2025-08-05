import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- Configurações Gerais ---
# O número de leads aleatórios para sincronizar em cada execução
LIMITE_DE_LEADS_PARA_SINC = 25

# --- Configurações BotConversa ---
BOTCONVERSA_TOKEN = os.getenv('BOTCONVERSA_API_TOKEN')
BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1"

# --- Configurações RD Station ---
RDSTATION_TOKEN = os.getenv('RDSTATION_CRM_TOKEN')
RDSTATION_BASE_URL = "https://crm.rdstation.com/api/v1"