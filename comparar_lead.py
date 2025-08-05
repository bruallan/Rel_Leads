import requests
from dotenv import load_dotenv
import os
import re
import random
import json

# --- Carrega as configurações do arquivo .env ---
load_dotenv()
RDSTATION_TOKEN = os.getenv('RDSTATION_CRM_TOKEN')
BOTCONVERSA_TOKEN = os.getenv('BOTCONVERSA_API_TOKEN')

RDSTATION_BASE_URL = "https://crm.rdstation.com/api/v1"
BOTCONVERSA_BASE_URL = "https://backend.botconversa.com.br/api/v1"

def carregar_mapa_sincronizacao():
    """Carrega o mapa de campos do ficheiro JSON."""
    try:
        with open('mapa_sincronizacao.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERRO: O ficheiro 'mapa_sincronizacao.json' não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print("ERRO: O ficheiro 'mapa_sincronizacao.json' parece estar corrompido ou vazio.")
        return None

def encontrar_lead_para_comparar():
    """Busca no BotConversa um lead que já foi integrado e tenha dados preenchidos."""
    print("Iniciando busca por um lead integrado com dados para comparar...")
    url = f"{BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    pagina = 1

    while url:
        try:
            print(f"-> Verificando página {pagina} de contatos do BotConversa...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            dados = response.json()

            for inscrito in dados.get('results', []):
                variaveis = inscrito.get('variables', {})
                id_negociacao_rd = variaveis.get('RD-IDNegociacao')

                if id_negociacao_rd and len(variaveis) > 5:
                    print(f"\nLead para comparação encontrado! Nome: {inscrito.get('full_name')}")
                    return inscrito
            
            url = dados.get('next')
            pagina += 1
        except requests.exceptions.RequestException as e:
            print(f"ERRO ao buscar contatos do BotConversa: {e}")
            return None
            
    print("\nNão foi possível encontrar um lead adequado para a comparação.")
    return None

def buscar_deal_rdstation(deal_id):
    """Busca os dados de uma negociação no RD Station pelo seu ID."""
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

if __name__ == "__main__":
    mapa = carregar_mapa_sincronizacao()
    if not mapa:
        exit()

    lead_bc = encontrar_lead_para_comparar()
    if not lead_bc:
        exit()

    id_rd = lead_bc.get('variables', {}).get('RD-IDNegociacao')
    deal_rd = buscar_deal_rdstation(id_rd)

    if not deal_rd:
        print("Não foi possível buscar os dados da negociação correspondente no RD Station.")
        exit()
        
    # --- COMPARAÇÃO E PREPARAÇÃO DA TABELA COMPLETA ---
    print("\n" + "="*80)
    print(f"  COMPARANDO DADOS PARA O LEAD: {lead_bc.get('full_name')}")
    print("="*80)

    tabela_comparativa = []
    variaveis_bc = lead_bc.get('variables', {})
    campos_rd = deal_rd.get('deal_custom_fields', [])
    mapa_campos_rd = {campo['custom_field_id']: campo['value'] for campo in campos_rd}

    for campo_bc, id_campo_rd in mapa.items():
        valor_bc = variaveis_bc.get(campo_bc)
        valor_rd = mapa_campos_rd.get(id_campo_rd)
        
        valor_bc_str = str(valor_bc or '').strip()
        valor_rd_str = str(valor_rd or '').strip()

        equivalente = "Sim ✅" if valor_bc_str == valor_rd_str else "Não ❌"

        tabela_comparativa.append({
            "campo": campo_bc,
            "valor_botconversa": valor_bc,
            "valor_rdstation": valor_rd,
            "equivalente": equivalente
        })

    # Imprime a tabela de comparação completa
    if not tabela_comparativa:
        print("\nNenhum campo mapeado encontrado para comparar.")
    else:
        # Calcula a largura das colunas para alinhamento
        max_campo = max(len(d['campo']) for d in tabela_comparativa)
        max_bc = max(len(str(d['valor_botconversa'])) for d in tabela_comparativa)
        max_rd = max(len(str(d['valor_rdstation'])) for d in tabela_comparativa)

        # Cabeçalho da Tabela
        print(f"\n{'CAMPO':<{max_campo}} | {'VALOR NO BOTCONVERSA':<{max_bc}} | {'VALOR NO RD STATION':<{max_rd}} | ESTÁ EQUIVALENTE?")
        print(f"{'-'*max_campo}-|-{'-'*max_bc}-|-{'-'*max_rd}-|------------------")
        
        for item in tabela_comparativa:
            print(f"{item['campo']:<{max_campo}} | {str(item['valor_botconversa']):<{max_bc}} | {str(item['valor_rdstation']):<{max_rd}} | {item['equivalente']}")

    print("\n--- Comparação concluída ---")