import requests
import re
import time
from datetime import datetime
import config

def normalizar_telefone(numero):
    """
    Versão aprimorada: Limpa e padroniza o número de telefone, focando nos últimos 9 dígitos
    para evitar problemas com DDD, 55 e o 9º dígito.
    """
    if not numero: return None
    apenas_digitos = re.sub(r'\D', '', str(numero))
    
    # Pega os últimos 9 dígitos, que representam o número de celular
    if len(apenas_digitos) >= 9:
        return apenas_digitos[-9:]
    return apenas_digitos # Retorna o que for possível se for um número curto/inválido


def processar_contatos_botconversa(data_alvo):
    print("Processando contatos do BotConversa...")
    if not config.BOTCONVERSA_TOKEN: return [], {}
    
    url = f"{config.BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": config.BOTCONVERSA_TOKEN}
    leads_do_dia_alvo = []
    mapa_telefone_id = {}
    pagina = 1

    while url:
        try:
            print(f"-> Lendo página {pagina} de contatos do BotConversa...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            dados = response.json()

            for inscrito in dados.get('results', []):
                telefone_normalizado = normalizar_telefone(inscrito.get('phone'))
                subscriber_id = inscrito.get('id')
                if telefone_normalizado and subscriber_id:
                    mapa_telefone_id[telefone_normalizado] = subscriber_id

                created_at_str = inscrito.get('created_at')
                if created_at_str:
                    data_inscrito = datetime.fromisoformat(created_at_str.replace('Z', '')).date()
                    if data_inscrito == data_alvo:
                        variaveis = inscrito.get('variables', {})
                        leads_do_dia_alvo.append({
                            "nome": inscrito.get('full_name', 'N/A'),
                            "telefone": telefone_normalizado,
                            "empreendimento_bc": variaveis.get('Empreendimento', 'N/A')
                        })
            url = dados.get('next')
            pagina += 1
        except requests.exceptions.RequestException as e:
            print(f"-> FALHA ao processar contatos do BotConversa: {e}")
            return [], {}

    print(f"-> Processamento concluído: {len(leads_do_dia_alvo)} novos contatos encontrados no BotConversa.")
    return leads_do_dia_alvo, mapa_telefone_id

def enviar_mensagem_pelo_botconversa(mensagem, contatos, mapa_telefone_id):
    print(f"\nIniciando envio para grupo de {len(contatos)} contato(s)...")
    if not config.BOTCONVERSA_TOKEN: return
    headers = {"API-KEY": config.BOTCONVERSA_TOKEN}
    for numero in contatos:
        numero_normalizado = normalizar_telefone(numero)
        if not numero_normalizado: continue
        subscriber_id = mapa_telefone_id.get(numero_normalizado)
        if subscriber_id:
            print(f"-> Enviando para {numero_normalizado} (ID: {subscriber_id})...")
            try:
                send_url = f"{config.BOTCONVERSA_BASE_URL}/webhook/subscriber/{subscriber_id}/send_message/"
                payload = {"type": "text", "value": mensagem}
                response_send = requests.post(send_url, headers=headers, json=payload, timeout=10)
                response_send.raise_for_status()
                print(f"-> Sucesso!")
            except requests.exceptions.RequestException as e:
                print(f"-> FALHA no envio para {numero_normalizado}: {e}")
        else:
            print(f"-> ERRO: O número {numero_normalizado} não foi encontrado no mapa de contatos do BotConversa.")
        time.sleep(2)