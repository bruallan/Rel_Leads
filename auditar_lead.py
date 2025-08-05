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

def mapear_campos_botconversa():
    """Busca todos os campos do BotConversa e cria um mapa de Nome -> ID."""
    print("Mapeando campos do BotConversa...")
    mapa_ids = {}
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    endpoints = ["/webhook/bot_fields/", "/webhook/custom_fields/"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BOTCONVERSA_BASE_URL}{endpoint}", headers=headers, timeout=10)
            response.raise_for_status()
            for campo in response.json():
                nome = campo.get('key')
                campo_id = campo.get('id')
                if nome and campo_id:
                    mapa_ids[nome] = campo_id
        except Exception:
            pass # Ignora erros se um dos endpoints falhar
            
    print(f"-> Mapeamento concluído. {len(mapa_ids)} campos do BotConversa encontrados.")
    return mapa_ids

def encontrar_lead_integrado_no_botconversa():
    """Busca no BotConversa o primeiro contato que tem o campo 'RD-IDNegociacao' preenchido."""
    print("Iniciando busca por um lead já integrado no BotConversa...")
    url = f"{BOTCONVERSA_BASE_URL}/webhook/subscribers/"
    headers = {"API-KEY": BOTCONVERSA_TOKEN}
    pagina = 1

    while url:
        try:
            print(f"-> Verificando página {pagina} de contatos...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            dados = response.json()
            for inscrito in dados.get('results', []):
                variaveis = inscrito.get('variables', {})
                id_negociacao_rd = variaveis.get('RD-IDNegociacao') or variaveis.get('rd-idnegociacao')
                if id_negociacao_rd:
                    print(f"\nLead integrado encontrado! Nome: {inscrito.get('full_name')}")
                    return inscrito
            url = dados.get('next')
            pagina += 1
        except requests.exceptions.RequestException as e:
            print(f"ERRO ao buscar contatos do BotConversa: {e}")
            return None
    print("\nNenhum lead com 'RD-IDNegociacao' preenchido foi encontrado.")
    return None

def buscar_detalhes_rdstation_por_id(deal_id):
    """Busca os dados completos de uma negociação no RD Station pelo seu ID."""
    print(f"Buscando detalhes da negociação ID {deal_id} no RD Station...")
    params = {'token': RDSTATION_TOKEN}
    url = f"{RDSTATION_BASE_URL}/deals/{deal_id}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"ERRO ao buscar detalhes no RD Station: {e}")
    return None

def imprimir_tabela(titulo, dados):
    """Imprime uma lista de dados no formato de tabela."""
    print("\n" + titulo)
    print("-" * (len(titulo) + 5))
    
    # Encontra o tamanho máximo de cada coluna para alinhar
    max_len_nome = max(len(str(row[0])) for row in dados) if dados else 10
    max_len_id = max(len(str(row[1])) for row in dados) if dados else 10

    # Imprime o cabeçalho
    print(f"{'NOME DO CAMPO':<{max_len_nome}} | {'ID DO CAMPO':<{max_len_id}} | CONTEÚDO DO CAMPO")
    print(f"{'-'*max_len_nome}-|-{'-'*max_len_id}-|------------------")

    for nome, campo_id, conteudo in dados:
        print(f"{str(nome):<{max_len_nome}} | {str(campo_id):<{max_len_id}} | {str(conteudo)}")

if __name__ == "__main__":
    mapa_ids_botconversa = mapear_campos_botconversa()
    lead_botconversa = encontrar_lead_integrado_no_botconversa()
    
    if lead_botconversa:
        # Extrai o ID da negociação do campo personalizado
        id_negociacao_rd = lead_botconversa.get('variables', {}).get('RD-IDNegociacao')
        
        # Busca os dados no RD usando o ID que encontramos
        dados_rd = buscar_detalhes_rdstation_por_id(id_negociacao_rd)
        
        # --- PREPARA OS DADOS PARA EXIBIÇÃO ---
        
        # Nome principal do Lead
        nome_lead = lead_botconversa.get('full_name', 'Lead Sem Nome')
        print("\n\n" + "="*50)
        print(f"  AUDITORIA DO LEAD: {nome_lead.upper()}")
        print("="*50)
        
        # Tabela RD Station
        tabela_rd = []
        if dados_rd:
            tabela_rd.append(("Nome da Negociação", "N/A", dados_rd.get("name")))
            tabela_rd.append(("ID da Negociação", "N/A", dados_rd.get("id")))
            tabela_rd.append(("Data de Criação", "N/A", dados_rd.get("created_at")))
            if dados_rd.get('contacts'):
                tabela_rd.append(("Nome do Contato", "N/A", dados_rd['contacts'][0].get("name")))
                if dados_rd['contacts'][0].get('phones'):
                    tabela_rd.append(("Telefone do Contato", "N/A", dados_rd['contacts'][0]['phones'][0].get("phone")))
            for campo in dados_rd.get('deal_custom_fields', []):
                tabela_rd.append((
                    campo['custom_field'].get('label', 'N/A'),
                    campo.get('custom_field_id', 'N/A'),
                    campo.get('value', 'N/A')
                ))
        imprimir_tabela("RD Station:", tabela_rd)

        # Tabela BotConversa
        tabela_bc = []
        tabela_bc.append(("Nome Completo", "N/A", lead_botconversa.get("full_name")))
        tabela_bc.append(("ID do Inscrito", "N/A", lead_botconversa.get("id")))
        tabela_bc.append(("Telefone", "N/A", lead_botconversa.get("phone")))
        for nome_campo, conteudo_campo in lead_botconversa.get("variables", {}).items():
            id_do_campo = mapa_ids_botconversa.get(nome_campo, 'N/A')
            tabela_bc.append((nome_campo, id_do_campo, conteudo_campo))
        
        imprimir_tabela("BotConversa:", tabela_bc)

    print("\n--- Auditoria de lead individual concluída ---")