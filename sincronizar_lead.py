import requests
from dotenv import load_dotenv
import os
import json
import time
import re

# --- Carrega as configurações do arquivo .env ---
load_dotenv()
RDSTATION_TOKEN = os.getenv('RDSTATION_CRM_TOKEN')
BOTCONVERSA_TOKEN = os.getenv('BOTCONVERSA_API_TOKEN')

RDSTATION_BASE_URL = "https://crm.rdstation.com/api/v1"
BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1"

# --- Funções ---

def carregar_mapa_sincronizacao():
    """Carrega o mapa de campos do ficheiro JSON."""
    try:
        with open('mapa_sincronizacao.json', 'r', encoding='utf-8') as f:
            print("Mapa de sincronização carregado com sucesso.")
            return json.load(f)
    except FileNotFoundError:
        print("ERRO: O ficheiro 'mapa_sincronizacao.json' não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print("ERRO: O ficheiro 'mapa_sincronizacao.json' parece estar corrompido ou vazio.")
        return None

def mapear_campos_botconversa():
    """Busca todos os campos do BotConversa e cria um mapa de Nome -> ID."""
    print("Mapeando IDs dos campos do BotConversa...")
    mapa_ids = {}
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    # Apenas 'custom_fields' são atualizáveis por usuário.
    endpoint = "/webhook/custom_fields/"
    try:
        response = requests.get(f"{BOTCONVERSA_BASE_URL}{endpoint}", headers=headers, timeout=10)
        response.raise_for_status()
        for campo in response.json():
            nome = campo.get('key')
            campo_id = campo.get('id')
            if nome and campo_id:
                mapa_ids[nome] = campo_id
        print(f"-> Mapeamento concluído: {len(mapa_ids)} campos do BotConversa encontrados.")
        return mapa_ids
    except Exception as e:
        print(f"-> AVISO: Não foi possível mapear os campos do BotConversa: {e}")
        return {}

def encontrar_lead_para_sincronizar():
    """Busca no BotConversa o primeiro lead que tem o campo 'RD-IDNegociacao' preenchido."""
    print("Iniciando busca por um lead integrado...")
    url = f"{BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    pagina = 1
    while url:
        try:
            print(f"-> Verificando página {pagina}...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            for inscrito in response.json().get('results', []):
                variaveis = inscrito.get('variables', {})
                if variaveis.get('RD-IDNegociacao'):
                    print(f"\nLead integrado para teste encontrado! Nome: {inscrito.get('full_name')}")
                    return inscrito
            url = response.json().get('next')
            pagina += 1
        except requests.exceptions.RequestException as e:
            print(f"ERRO ao buscar contatos do BotConversa: {e}")
            return None
    print("\nNenhum lead com 'RD-IDNegociacao' preenchido foi encontrado para o teste.")
    return None

def buscar_deal_rdstation(deal_id):
    """Busca os dados de uma negociação no RD Station pelo seu ID."""
    if not deal_id: return None
    print(f"Buscando negociação ID {deal_id} no RD Station...")
    params = {'token': RDSTATION_TOKEN}
    url = f"{RDSTATION_BASE_URL}/deals/{deal_id}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"ERRO ao buscar detalhes no RD Station: {e}")
        return None

def atualizar_deal_rdstation(deal_id, updates_rd):
    """Atualiza campos personalizados de uma negociação no RD Station."""
    print(f"\n-> Sincronizando {len(updates_rd)} campo(s) para o RD Station...")
    if not deal_id or not updates_rd: return
    url = f"{RDSTATION_BASE_URL}/deals/{deal_id}?token={RDSTATION_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload_fields = [{'custom_field_id': field_id, 'value': value} for field_id, value in updates_rd.items()]
    payload = {"deal": {"deal_custom_fields": payload_fields}}
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        print("-> Sucesso na atualização do RD Station!")
    except Exception as e:
        print(f"-> FALHA ao atualizar RD Station: {e}")

def atualizar_subscriber_botconversa(subscriber_id, updates_bc, mapa_ids_bc):
    """
    VERSÃO FINAL: Atualiza cada campo do BotConversa individualmente,
    usando a URL e o método corretos (POST).
    """
    print(f"\n-> Sincronizando {len(updates_bc)} campo(s) para o BotConversa...")
    if not subscriber_id or not updates_bc: return

    headers = {"API-KEY": BOTCONVERSA_TOKEN, "Content-Type": "application/json"}
    
    for campo_nome, campo_valor in updates_bc.items():
        custom_field_id = mapa_ids_bc.get(campo_nome)
        if not custom_field_id:
            print(f"-> AVISO: Campo '{campo_nome}' não é um campo personalizado atualizável. Atualização ignorada.")
            continue

        # --- CORREÇÃO FINAL DA URL ---
        # Adicionado o segmento /webhook/ que estava faltando.
        url = f"{BOTCONVERSA_BASE_URL}/webhook/subscriber/{subscriber_id}/custom_fields/{custom_field_id}/"
        # ---------------------------
        
        payload = {"value": str(campo_valor)}

        try:
            print(f"   - Atualizando campo '{campo_nome}'...")
            # O método POST está correto conforme a documentação.
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"   -> FALHA ao atualizar campo '{campo_nome}': {e}")
            
    print("-> Sincronização com o BotConversa concluída.")

def gerar_relatorio_comparativo(titulo, lead_bc, deal_rd, mapa):
    """Imprime uma tabela comparativa dos dados do lead."""
    print("\n" + "="*80)
    print(f"  {titulo.upper()}")
    print("="*80)

    tabela = []
    variaveis_bc = lead_bc.get('variables', {})
    mapa_campos_rd = {campo['custom_field_id']: campo['value'] for campo in deal_rd.get('deal_custom_fields', [])}

    for campo_bc, id_campo_rd in mapa.items():
        valor_bc = variaveis_bc.get(campo_bc)
        valor_rd = mapa_campos_rd.get(id_campo_rd)
        valor_bc_str = str(valor_bc or '').strip()
        valor_rd_str = str(valor_rd or '').strip()
        equivalente = "Sim ✅" if valor_bc_str == valor_rd_str else "Não ❌"
        tabela.append([campo_bc, valor_bc, valor_rd, equivalente])

    if not tabela:
        print("\nNenhum campo mapeado encontrado para comparar.")
        return

    max_campo = max(len(row[0]) for row in tabela)
    max_bc = max(len(str(row[1])) for row in tabela)
    max_rd = max(len(str(row[2])) for row in tabela)

    print(f"\n{'CAMPO':<{max_campo}} | {'VALOR NO BOTCONVERSA':<{max_bc}} | {'VALOR NO RD STATION':<{max_rd}} | ESTÁ EQUIVALENTE?")
    print(f"{'-'*max_campo}-|-{'-'*max_bc}-|-{'-'*max_rd}-|------------------")
    for row in tabela:
        print(f"{row[0]:<{max_campo}} | {str(row[1]):<{max_bc}} | {str(row[2]):<{max_rd}} | {row[3]}")


# --- Rotina Principal ---
if __name__ == "__main__":
    mapa_sinc = carregar_mapa_sincronizacao()
    if not mapa_sinc:
        exit()

    mapa_ids_botconversa = mapear_campos_botconversa()
    if not mapa_ids_botconversa:
        print("Não foi possível mapear os campos do BotConversa. Encerrando.")
        exit()

    lead_bc_antes = encontrar_lead_para_sincronizar()
    if not lead_bc_antes:
        exit()

    id_rd = lead_bc_antes.get('variables', {}).get('RD-IDNegociacao')
    deal_rd_antes = buscar_deal_rdstation(id_rd)
    if not deal_rd_antes:
        exit()

    gerar_relatorio_comparativo("RELATÓRIO ANTES DA SINCRONIZAÇÃO", lead_bc_antes, deal_rd_antes, mapa_sinc)

    updates_para_rd = {}
    updates_para_bc = {}
    variaveis_bc_antes = lead_bc_antes.get('variables', {})
    mapa_campos_rd_antes = {campo['custom_field_id']: campo['value'] for campo in deal_rd_antes.get('deal_custom_fields', [])}

    for campo_bc, id_campo_rd in mapa_sinc.items():
        valor_bc = variaveis_bc_antes.get(campo_bc)
        valor_rd = mapa_campos_rd_antes.get(id_campo_rd)
        valor_bc_str = str(valor_bc or '').strip()
        valor_rd_str = str(valor_rd or '').strip()

        if valor_bc_str != valor_rd_str:
            if valor_bc_str and not valor_rd_str:
                updates_para_rd[id_campo_rd] = valor_bc
            elif not valor_bc_str and valor_rd_str:
                updates_para_bc[campo_bc] = valor_rd
            else:
                updates_para_bc[campo_bc] = valor_rd
    
    if updates_para_rd:
        atualizar_deal_rdstation(id_rd, updates_para_rd)
    if updates_para_bc:
        atualizar_subscriber_botconversa(lead_bc_antes['id'], updates_para_bc, mapa_ids_botconversa)

    if updates_para_rd or updates_para_bc:
        print("\nAguardando 5 segundos para as APIs processarem as atualizações...")
        time.sleep(5)
        # Busca os dados novamente para o relatório "Depois"
        lead_bc_depois = encontrar_lead_para_sincronizar() 
        deal_rd_depois = buscar_deal_rdstation(id_rd)
        gerar_relatorio_comparativo("RELATÓRIO DEPOIS DA SINCRONIZAÇÃO", lead_bc_depois, deal_rd_depois, mapa_sinc)
    else:
        print("\nNenhuma atualização necessária. Os dados já estão sincronizados.")

    print("\n--- Sincronização de lead individual concluída ---")