import requests
from datetime import datetime
import config
from api_botconversa import normalizar_telefone

def obter_dados_rdstation(data_alvo):
    print("Buscando dados do RD Station...")
    if not config.RDSTATION_TOKEN: return {}

    endpoint = "/deals"
    url = f"{config.RDSTATION_BASE_URL}{endpoint}"
    data_formatada = data_alvo.strftime('%Y-%m-%d')
    
    # Dicionário para guardar os resultados
    leads_rd = {
        'total': 0, 'bella_serra': 0, 'vista_bella': 0, 'nao_atribuido': 0, 
        'lista_detalhada': [], 'lista_nao_atribuidos': [] 
    }
    
    # --- INÍCIO DA LÓGICA DE PAGINAÇÃO ---
    all_deals_do_dia = []
    page = 1
    has_more = True
    print(f"-> Buscando negociações do dia {data_formatada} no RD Station (com paginação)...")

    try:
        while has_more:
            params = {
                'token': config.RDSTATION_TOKEN,
                'created_at_gte': f"{data_formatada}T00:00:00-03:00",
                'created_at_lte': f"{data_formatada}T23:59:59-03:00",
                'page': page,
                'limit': 200 # Pede o máximo de itens por página
            }
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            dados = response.json()
            
            deals_da_pagina = dados.get('deals', [])
            all_deals_do_dia.extend(deals_da_pagina)
            
            # A API do RD Station pode não ter o 'has_more', então verificamos se a página veio vazia
            if not deals_da_pagina:
                has_more = False
            else:
                page += 1
        # --- FIM DA LÓGICA DE PAGINAÇÃO ---

        # Agora processamos a lista completa de deals que coletamos
        for deal in all_deals_do_dia:
            contato_lista = deal.get('contacts', [])
            telefone_normalizado = None
            nome = deal.get('name', 'NEGOCIAÇÃO SEM CONTATO')
            if contato_lista:
                contato = contato_lista[0]
                nome = contato.get('name', nome)
                if contato.get('phones'):
                    telefone_normalizado = normalizar_telefone(contato['phones'][0].get('phone'))

            produto = "N/A"
            if deal.get('deal_products'):
                produto = deal['deal_products'][0].get('name', 'N/A').strip()

            lead_detalhado = {'nome': nome, 'telefone': telefone_normalizado, 'empreendimento_rd': produto}
            leads_rd['lista_detalhada'].append(lead_detalhado)
            
            deal_info_str = f"{nome} {produto}"
            if 'Bella Serra' in deal_info_str:
                leads_rd['bella_serra'] += 1
            elif 'Vista Bella' in deal_info_str:
                leads_rd['vista_bella'] += 1
            else:
                leads_rd['nao_atribuido'] += 1
                leads_rd['lista_nao_atribuidos'].append(lead_detalhado)
        
        leads_rd['total'] = len(leads_rd['lista_detalhada'])
        print(f"-> Processamento concluído: {leads_rd['total']} novos leads encontrados no RD Station.")
        return leads_rd
        
    except requests.exceptions.RequestException as e:
        print(f"-> FALHA ao buscar dados do RD Station: {e}")
        return {}


def obter_contagem_por_responsavel_rd():
    print("Buscando contagem de leads 'Em Andamento' por responsável no RD Station...")
    if not config.RDSTATION_TOKEN: return {}
    
    resultados = {}
    try:
        for nome, user_id in config.RD_RESPONSAVEIS.items():
            all_deals = []
            page = 1
            has_more = True
            while has_more:
                params = {
                    'token': config.RDSTATION_TOKEN, 'user_id': user_id,
                    'deal_pipeline_id': config.RD_FUNIL_PADRAO_ID, 'page': page, 'limit': 200
                }
                response = requests.get(f"{config.RDSTATION_BASE_URL}/deals", params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                all_deals.extend(data.get('deals', []))
                has_more = data.get('has_more', False)
                page += 1
            
            contagem_em_andamento = 0
            for deal in all_deals:
                if deal.get('win') is None:
                    contagem_em_andamento += 1
            
            resultados[nome] = contagem_em_andamento
            
        print("-> Sucesso! Contagem por responsável obtida.")
        return resultados
    except Exception as e:
        print(f"-> FALHA ao obter contagem por responsável: {e}")

        return {}
