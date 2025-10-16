# ficheiro: api_meta.py (VERSÃO CORRIGIDA E FINAL)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import config
import re # Importamos a biblioteca de expressões regulares para extrair o saldo

def extrair_saldo_disponivel(display_string):
    """
    Função auxiliar para extrair o valor numérico do saldo a partir
    de um texto como "Saldo disponível (R$336,21 BRL)".
    """
    if not display_string:
        return 0.0
    
    # Usa uma expressão regular para encontrar números com vírgula (formato brasileiro)
    match = re.search(r'R\$\s*([\d\.,]+)', display_string)
    if match:
        try:
            # Pega o valor encontrado (ex: "336,21"), remove pontos e troca vírgula por ponto
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            return float(valor_str)
        except (ValueError, IndexError):
            # Se algo der errado na conversão, retorna 0
            return 0.0
    return 0.0


def obter_dados_meta_ads(data_alvo):
    """
    Função corrigida para buscar o saldo disponível real do campo 'funding_source_details'.
    """
    print("Buscando dados do Meta Ads (com saldo correto)...")
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
        
        for nome, account_id in config.META_AD_ACCOUNTS.items():
            if not account_id: continue
            
            account = AdAccount(account_id)
            
            # --- LÓGICA CORRIGIDA PARA BUSCAR O SALDO ---
            # Pedimos à API os detalhes da fonte de financiamento
            account_details = account.api_get(fields=['funding_source_details'])
            
            # Extraímos o texto que contém o saldo
            funding_details = account_details.get('funding_source_details', {})
            display_text = funding_details.get('display_string', '')
            
            # Usamos nossa nova função para extrair o valor numérico
            saldo_final = extrair_saldo_disponivel(display_text)
            # --- FIM DA LÓGICA CORRIGIDA ---

            # Lógica para buscar leads e gastos (permanece igual)
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
            
            # Armazenamos os dados corretos
            resultados[nome] = {'leads': count, 'spend': spend, 'balance': saldo_final}
            resultados['total']['leads'] += count
            resultados['total']['spend'] += spend
            
        print(f"-> Sucesso! Encontrados {resultados['total']['leads']} leads no Meta Ads e saldos corrigidos.")
        return resultados
    except Exception as e:
        print(f"-> FALHA ao buscar dados do Meta Ads: {e}")
        return retorno_padrao
