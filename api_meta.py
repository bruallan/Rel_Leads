from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import config

def obter_dados_meta_ads(data_alvo):
    print("Buscando dados do Meta Ads...")
    # Estrutura de retorno padrão em caso de erro ou falta de token
    retorno_padrao = {'total': {'leads': 0, 'spend': 0.0}, 'bella_serra': {'leads': 0, 'spend': 0.0}, 'vista_bella': {'leads': 0, 'spend': 0.0}}

    if not config.META_ADS_ACCESS_TOKEN:
        print("-> ERRO: Token de acesso do Meta Ads não configurado.")
        return retorno_padrao

    try:
        FacebookAdsApi.init(access_token=config.META_ADS_ACCESS_TOKEN)
        # A estrutura agora guarda tanto leads quanto o custo (spend)
        resultados = {'total': {'leads': 0, 'spend': 0.0}}
        data_formatada = data_alvo.strftime('%Y-%m-%d')
        
        # ATUALIZAÇÃO: Adicionamos 'spend' aos campos solicitados
        params = {
            'time_range': {'since': data_formatada, 'until': data_formatada},
            'fields': ['actions', 'spend'], 
            'level': 'account'
        }
        
        for nome, account_id in config.META_AD_ACCOUNTS.items():
            if not account_id: continue
            
            account = AdAccount(account_id)
            insights = account.get_insights(params=params)
            
            count = 0
            # ATUALIZAÇÃO: Capturamos o valor gasto e convertemos para float
            spend = 0.0
            if insights:
                spend = float(insights[0].get('spend', '0'))
                for action in insights[0].get('actions', []):
                    if action['action_type'] == config.META_LEAD_ACTION_TYPE:
                        count = int(action['value'])
                        break
            
            # ATUALIZAÇÃO: Armazenamos leads e spend para cada conta
            resultados[nome] = {'leads': count, 'spend': spend}
            resultados['total']['leads'] += count
            resultados['total']['spend'] += spend
            
        print(f"-> Sucesso! Encontrados {resultados['total']['leads']} leads no Meta Ads.")
        return resultados
    except Exception as e:
        print(f"-> FALHA ao buscar dados do Meta Ads: {e}")
        return retorno_padrao
