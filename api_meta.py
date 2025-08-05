from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import config

def obter_dados_meta_ads(data_alvo):
    print("Buscando dados do Meta Ads...")
    if not config.META_ADS_ACCESS_TOKEN:
        print("-> ERRO: Token de acesso do Meta Ads não configurado.")
        return {'total': 0, 'bella_serra': 0, 'vista_bella': 0}

    try:
        FacebookAdsApi.init(access_token=config.META_ADS_ACCESS_TOKEN)
        resultados = {'total': 0}
        data_formatada = data_alvo.strftime('%Y-%m-%d')
        params = {
            'time_range': {'since': data_formatada, 'until': data_formatada},
            'fields': ['actions'], 'level': 'account'
        }
        
        for nome, account_id in config.META_AD_ACCOUNTS.items():
            if not account_id: continue
            account = AdAccount(account_id)
            insights = account.get_insights(params=params)
            count = 0
            if insights:
                for action in insights[0].get('actions', []):
                    if action['action_type'] == config.META_LEAD_ACTION_TYPE:
                        count = int(action['value'])
                        break
            resultados[nome] = count
            resultados['total'] += count
            
        print(f"-> Sucesso! Encontrados {resultados['total']} leads no Meta Ads.")
        return resultados
    except Exception as e:
        print(f"-> FALHA ao buscar dados do Meta Ads: {e}")
        return {'total': 0, 'bella_serra': 0, 'vista_bella': 0}