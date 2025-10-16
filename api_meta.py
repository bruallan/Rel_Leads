# ficheiro: api_meta.py

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import config

def obter_dados_meta_ads(data_alvo):
    """
    Função atualizada para buscar leads, gastos (spend) e o saldo (balance)
    de cada conta de anúncios.
    """
    print("Buscando dados do Meta Ads (incluindo saldo)...")
    # Estrutura de retorno padrão, agora com o campo 'balance'
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
        data_formatada = data_alvo.strftime('%Y-%m-%d')
        
        # Parâmetros para buscar os insights (leads e gastos)
        params_insights = {
            'time_range': {'since': data_formatada, 'until': data_formatada},
            'fields': ['actions', 'spend'], 
            'level': 'account'
        }
        
        for nome, account_id in config.META_AD_ACCOUNTS.items():
            if not account_id: continue
            
            account = AdAccount(account_id)
            
            # --- NOVA LÓGICA PARA BUSCAR O SALDO ---
            # Pedimos à API os detalhes da conta, especificamente o campo 'balance'
            account_details = account.api_get(fields=['balance'])
            # A API retorna o saldo como string (ex: '12345'), dividimos por 100 para ter o valor real
            saldo_str = account_details.get('balance', '0')
            saldo_float = float(saldo_str) / 100
            # --- FIM DA NOVA LÓGICA ---
            
            # Busca de insights (como já existia)
            insights = account.get_insights(params=params_insights)
            
            count = 0
            spend = 0.0
            if insights:
                spend = float(insights[0].get('spend', '0'))
                for action in insights[0].get('actions', []):
                    if action['action_type'] == config.META_LEAD_ACTION_TYPE:
                        count = int(action['value'])
                        break
            
            # Armazenamos leads, gastos e o novo saldo
            resultados[nome] = {'leads': count, 'spend': spend, 'balance': saldo_float}
            resultados['total']['leads'] += count
            resultados['total']['spend'] += spend
            
        print(f"-> Sucesso! Encontrados {resultados['total']['leads']} leads no Meta Ads e saldos atualizados.")
        return resultados
    except Exception as e:
        print(f"-> FALHA ao buscar dados do Meta Ads: {e}")
        # Em caso de falha, usamos a estrutura padrão com saldo zerado
        return retorno_padrao
