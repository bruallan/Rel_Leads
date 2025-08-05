import re
import requests
import json
import time
import config # Importa as configurações do nosso novo arquivo

def carregar_mapa_sincronizacao():
    """Carrega o mapa de campos do ficheiro JSON."""
    try:
        with open('mapa_sincronizacao.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar o 'mapa_sincronizacao.json'. {e}")
        return None

def encontrar_leads_integrados():
    """Busca no BotConversa TODOS os contatos que têm o campo 'RD-IDNegociacao' preenchido."""
    print("Iniciando busca por TODOS os leads integrados. Isso pode demorar...")
    url = f"{config.BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": config.BOTCONVERSA_TOKEN}
    pagina = 1
    leads_integrados = []
    while url:
        try:
            print(f"-> Verificando página {pagina} de contatos...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            dados = response.json()
            for inscrito in dados.get('results', []):
                if inscrito.get('variables', {}).get('RD-IDNegociacao'):
                    leads_integrados.append(inscrito)
            url = dados.get('next')
            pagina += 1
        except requests.exceptions.RequestException as e:
            print(f"ERRO ao buscar contatos do BotConversa: {e}")
            return []
    print(f"\nBusca concluída! {len(leads_integrados)} leads integrados encontrados.")
    return leads_integrados

def buscar_deal_rdstation(deal_id):
    """Busca os dados de uma negociação no RD Station pelo seu ID."""
    if not deal_id: return None
    params = {'token': config.RDSTATION_TOKEN}
    url = f"{config.RDSTATION_BASE_URL}/deals/{deal_id}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def atualizar_deal_rdstation(deal_id, updates_rd):
    """Atualiza campos personalizados de uma negociação no RD Station."""
    print(f"-> Sincronizando {len(updates_rd)} campo(s) para o RD Station...")
    if not deal_id or not updates_rd: return False
    url = f"{config.RDSTATION_BASE_URL}/deals/{deal_id}?token={config.RDSTATION_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload_fields = [{'custom_field_id': field_id, 'value': value} for field_id, value in updates_rd.items()]
    payload = {"deal": {"deal_custom_fields": payload_fields}}
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        print("-> Sucesso na atualização do RD Station!")
        return True
    except Exception as e:
        print(f"-> FALHA ao atualizar RD Station: {e}")
        return False

def atualizar_subscriber_botconversa(subscriber_id, variaveis_atuais_bc, updates_bc):
    """
    VERSÃO DEFINITIVA: Usa o método PUT para atualizar o objeto de variáveis
    de um subscriber de uma só vez.
    """
    print(f"-> Sincronizando {len(updates_bc)} campo(s) para o BotConversa...")
    if not subscriber_id or not updates_bc: return False

    url = f"{config.BOTCONVERSA_BASE_URL}/webhook/subscriber/{subscriber_id}/"
    headers = {"API-KEY": config.BOTCONVERSA_TOKEN, "Content-Type": "application/json"}
    
    # Preserva as variáveis existentes e apenas atualiza as necessárias
    variaveis_finais = variaveis_atuais_bc.copy()
    variaveis_finais.update(updates_bc)
    
    payload = {"variables": variaveis_finais}

    try:
        response = requests.put(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        print("-> Sucesso na atualização do BotConversa!")
        return True
    except Exception as e:
        print(f"-> FALHA ao atualizar BotConversa: {e}")
        return False
    
# --- NOVA FUNÇÃO PARA VERIFICAÇÃO RÁPIDA ---
def buscar_subscriber_bc_por_telefone(telefone):
    """Busca um contato específico no BotConversa pelo telefone para verificação."""
    if not telefone: return None
    numero_para_busca = re.sub(r'\D', '', str(telefone)) # Limpa o número
    url = f"{config.BOTCONVERSA_BASE_URL}/webhook/subscribers/?search={numero_para_busca}"
    headers = {"API-KEY": config.BOTCONVERSA_TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        resultados = response.json().get('results', [])
        if resultados:
            # Retorna o primeiro resultado da busca
            return resultados[0]
    except Exception:
        return None
    return None    