import os
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- Configurações Meta Ads ---
META_ADS_ACCESS_TOKEN = os.getenv('META_ADS_ACCESS_TOKEN')
META_AD_ACCOUNTS = {
    'bella_serra': os.getenv('META_AD_ACCOUNT_ID_BELLA_SERRA'),
    'vista_bella': os.getenv('META_AD_ACCOUNT_ID_VISTA_BELLA')
}
# O nome exato da ação de conversão de lead que funciona para você
META_LEAD_ACTION_TYPE = 'onsite_conversion.messaging_conversation_started_7d'

# --- Configurações BotConversa ---
BOTCONVERSA_TOKEN = os.getenv('BOTCONVERSA_API_TOKEN')
BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1"

# --- Configurações RD Station ---
RDSTATION_TOKEN = os.getenv('RDSTATION_CRM_TOKEN')
RDSTATION_BASE_URL = "https://crm.rdstation.com/api/v1"
RD_RESPONSAVEIS = {
    'Reinaldo': '67f667359b9f1c001f3156d0',
    'Letícia': '680777cb2455f800240ea6e1',
    'Lucas': '67ae25c4bc39410014dd6f82',
    'Bruno': '67af917534509600242cf93a',
    'Diogo': '67af902330fafb001c8ef7da'
}
RD_FUNIL_PADRAO_ID = '67ae261cab5a8e00178ea85f'

# --- Configurações de Contatos ---
CONTATOS_GRUPO_1 = os.getenv('CONTATOS_GRUPO_1', '').split(',') if os.getenv('CONTATOS_GRUPO_1') else []
CONTATOS_GRUPO_2 = os.getenv('CONTATOS_GRUPO_2', '').split(',') if os.getenv('CONTATOS_GRUPO_2') else []