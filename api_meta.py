# ficheiro: api_meta.py (VERSÃO DE DIAGNÓSTICO)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import config
import json # Importamos a biblioteca json para formatar a saída

def obter_dados_meta_ads(data_alvo):
    """
    Função modificada para diagnóstico.
    Ela vai buscar e imprimir TODOS os detalhes financeiros disponíveis da conta.
    """
    print("Buscando dados do Meta Ads (MODO DIAGNÓSTICO)...")
    retorno_padrao = {
        'total': {'leads': 0, 'spend': 0.0},
        'bella_serra': {'leads': 0, 'spend': 0.0, 'balance': 0.0},
        'vista_bella': {'leads': 0, 'spend': 0.0, 'balance': 0.0}
    }

    if not config.META_ADS_ACCESS_TOKEN:
        print("-> ERRO: Token de acesso do Meta Ads não configurado.")
        return retorno_padrao

    try:
        FacebookAdsApi.init(access_token=config.META_ADS_ACCESS_TOKEN)
        resultados = {'total': {'leads': 0, 'spend': 0.0}}
        
        for nome, account_id in config.META_AD_ACCOUNTS.items():
            if not account_id: continue
            
            account = AdAccount(account_id)
            
            # --- LÓGICA DE DIAGNÓSTICO ---
            # Pedimos à API vários campos financeiros para investigar
            campos_para_investigar = [
                'account_id',
                'name',
                'balance',
                'amount_spent',
                'spend_cap',
                'funding_source',
                'funding_source_details',
                'currency'
            ]
            
            print(f"\n--- [INVESTIGANDO] Tentando buscar dados da conta: {nome} ---")
            try:
                account_details = account.api_get(fields=campos_para_investigar)
                
                # Usamos json.dumps para imprimir o resultado de forma legível
                print(json.dumps(account_details.export_all_data(), indent=2))

            except Exception as e_details:
                print(f"-> FALHA ao buscar detalhes da conta: {e_details}")
            print("----------------------------------------------------------\n")
            # --- FIM DA LÓGICA DE DIAGNÓSTICO ---

            # A parte de buscar leads e spend continua igual para o relatório não falhar
            saldo_str = account_details.get('balance', '0') if 'account_details' in locals() else '0'
            saldo_float = float(saldo_str) / 100
            
            data_formatada = data_alvo.strftime('%Y-%m-%d')
            params_insights = {
                'time_range': {'since': data_formatada, 'until': data_formatada},
                'fields': ['actions', 'spend'], 'level': 'account'
            }
            insights = account.get_insights(params=params_insights)
            
            count = 0
            spend = 0.0
            if insights:
                spend = float(insights[0].get('spend', '0'))
                for action in insights[0].get('actions', []):
                    if action['action_type'] == config.META_LEAD_ACTION_TYPE:
                        count = int(action['value'])
                        break
            
            resultados[nome] = {'leads': count, 'spend': spend, 'balance': saldo_float}
            resultados['total']['leads'] += count
            resultados['total']['spend'] += spend
            
        return resultados
    except Exception as e:
        print(f"-> FALHA GERAL ao buscar dados do Meta Ads: {e}")
        return retorno_padrao
