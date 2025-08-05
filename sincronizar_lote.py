import requests
from dotenv import load_dotenv
import os
import json
import time
import random

from sincronizar_lead import encontrar_lead_para_sincronizar

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
            return json.load(f)
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar o 'mapa_sincronizacao.json'. {e}")
        return None

def mapear_campos_botconversa():
    """Busca apenas os Campos Personalizados do BotConversa e cria um mapa de Nome -> ID."""
    print("Mapeando IDs dos Campos Personalizados do BotConversa...")
    mapa_ids = {}
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    endpoint = "/webhook/custom_fields/"
    try:
        response = requests.get(f"{BOTCONVERSA_BASE_URL}{endpoint}", headers=headers, timeout=10)
        response.raise_for_status()
        for campo in response.json():
            mapa_ids[campo.get('key')] = campo.get('id')
        print(f"-> Mapeamento concluído: {len(mapa_ids)} campos personalizados encontrados.")
        return mapa_ids
    except Exception as e:
        print(f"-> FALHA CRÍTICA ao mapear os campos do BotConversa: {e}")
        return {}

def encontrar_leads_integrados():
    """Busca no BotConversa TODOS os contatos que têm o campo 'RD-IDNegociacao' preenchido."""
    print("Iniciando busca por TODOS os leads integrados. Isso pode demorar vários minutos...")
    url = f"{BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    pagina = 1
    leads_integrados = []
    while url:
        try:
            print(f"-> Verificando página {pagina} de contatos...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            for inscrito in response.json().get('results', []):
                if inscrito.get('variables', {}).get('RD-IDNegociacao'):
                    leads_integrados.append(inscrito)
            url = response.json().get('next')
            pagina += 1
        except requests.exceptions.RequestException as e:
            print(f"ERRO ao buscar contatos do BotConversa: {e}")
            return []
    print(f"\nBusca concluída! {len(leads_integrados)} leads integrados encontrados.")
    return leads_integrados

def buscar_deal_rdstation(deal_id):
    if not deal_id: return None
    params = {'token': RDSTATION_TOKEN}
    url = f"{RDSTATION_BASE_URL}/deals/{deal_id}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception: return None

def atualizar_deal_rdstation(deal_id, updates_rd):
    """Atualiza campos personalizados de uma negociação no RD Station."""
    print(f"-> Sincronizando {len(updates_rd)} campo(s) para o RD Station...")
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
    """VERSÃO FINAL: Atualiza cada campo usando o método comprovadamente correto."""
    print(f"-> Sincronizando {len(updates_bc)} campo(s) para o BotConversa...")
    if not subscriber_id or not updates_bc: return

    headers = {"API-KEY": BOTCONVERSA_TOKEN, "Content-Type": "application/json"}
    
    for campo_nome, campo_valor in updates_bc.items():
        custom_field_id = mapa_ids_bc.get(campo_nome)
        if not custom_field_id:
            print(f"-> AVISO: Campo '{campo_nome}' não é um campo personalizado atualizável. Ignorando.")
            continue

        url = f"{BOTCONVERSA_BASE_URL}/webhook/subscriber/{subscriber_id}/custom_fields/{custom_field_id}/"
        payload = {"value": str(campo_valor)}
        try:
            print(f"   - Atualizando campo '{campo_nome}'...")
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            print(f"     -> Sucesso!")
        except Exception as e:
            print(f"     -> FALHA na requisição: {e}")
            
    print("-> Sincronização com o BotConversa concluída.")

def gerar_relatorio_comparativo(titulo, lead_bc, deal_rd, mapa):
    """Imprime uma tabela comparativa dos dados do lead."""
    print("\n" + "="*80)
    print(f"  {titulo.upper()}")
    print("="*80)
    # ... (O corpo desta função está correto e pode ser copiado da resposta anterior)
    pass

# --- Rotina Principal ---
if __name__ == "__main__":
    # Cole aqui o corpo COMPLETO da função 'gerar_relatorio_comparativo' da resposta anterior
    # ---------------------------------------------------------------------------------
    def gerar_relatorio_comparativo(titulo, lead_bc, deal_rd, mapa):
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
        max_campo = max(len(row[0]) for row in tabela) if tabela else 10
        max_bc = max(len(str(row[1])) for row in tabela) if tabela else 10
        max_rd = max(len(str(row[2])) for row in tabela) if tabela else 10
        print(f"\n{'CAMPO':<{max_campo}} | {'VALOR NO BOTCONVERSA':<{max_bc}} | {'VALOR NO RD STATION':<{max_rd}} | ESTÁ EQUIVALENTE?")
        print(f"{'-'*max_campo}-|-{'-'*max_bc}-|-{'-'*max_rd}-|------------------")
        for row in tabela:
            print(f"{row[0]:<{max_campo}} | {str(row[1]):<{max_bc}} | {str(row[2]):<{max_rd}} | {row[3]}")
    # ---------------------------------------------------------------------------------

    mapa_sinc = carregar_mapa_sincronizacao()
    if not mapa_sinc: exit()

    mapa_ids_botconversa = mapear_campos_botconversa()
    if not mapa_ids_botconversa: exit()

    todos_leads_integrados = encontrar_leads_integrados()
    if not todos_leads_integrados: exit()

    limite = min(25, len(todos_leads_integrados))
    leads_sorteados = random.sample(todos_leads_integrados, limite)
    print(f"\nSorteando {limite} leads para a sincronização...")

    for i, lead_bc_antes in enumerate(leads_sorteados):
        print("\n" + "#"*80)
        print(f"#  PROCESSANDO LEAD {i+1}/{limite}: {lead_bc_antes.get('full_name')}")
        print("#"*80)

        id_rd = lead_bc_antes.get('variables', {}).get('RD-IDNegociacao')
        deal_rd_antes = buscar_deal_rdstation(id_rd)
        if not deal_rd_antes:
            print(f"Não foi possível buscar a negociação ID {id_rd}. Pulando para o próximo.")
            continue

        gerar_relatorio_comparativo(f"RELATÓRIO ANTES DA SINCRONIZAÇÃO - {lead_bc_antes.get('full_name')}", lead_bc_antes, deal_rd_antes, mapa_sinc)

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
        
        if not updates_para_rd and not updates_para_bc:
            print("\nNenhuma atualização necessária para este lead.")
            continue

        if updates_para_rd:
            atualizar_deal_rdstation(id_rd, updates_para_rd)
        if updates_para_bc:
            atualizar_subscriber_botconversa(lead_bc_antes['id'], updates_para_bc, mapa_ids_botconversa)

        print("\nAguardando 5 segundos para as APIs processarem...")
        time.sleep(5)
        
        lead_bc_depois = encontrar_lead_para_sincronizar() # Busca o lead novamente para ter os dados atualizados
        deal_rd_depois = buscar_deal_rdstation(id_rd)
        if lead_bc_depois and deal_rd_depois:
            gerar_relatorio_comparativo(f"RELATÓRIO DEPOIS DA SINCRONIZAÇÃO - {lead_bc_antes.get('full_name')}", lead_bc_depois, deal_rd_depois, mapa_sinc)

    print("\n\n--- Sincronização em lote concluída ---")