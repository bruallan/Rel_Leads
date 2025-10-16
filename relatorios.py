# ficheiro: relatorios.py

def montar_mensagem_resumo(meta, data_relatorio):
    """
    Cria a mensagem de resumo de captação do Meta Ads.
    Esta função permanece a mesma.
    """
    data_formatada = data_relatorio.strftime('%d/%m/%Y')

    dados_bs = meta.get('bella_serra', {'leads': 0, 'spend': 0.0})
    leads_bs = dados_bs.get('leads', 0)
    spend_bs = dados_bs.get('spend', 0.0)
    cpl_bs_texto = ""
    if leads_bs > 0:
        cpl_bs = spend_bs / leads_bs
        cpl_bs_texto = f"\n(CPL de R$ {cpl_bs:.2f})"

    dados_vb = meta.get('vista_bella', {'leads': 0, 'spend': 0.0})
    leads_vb = dados_vb.get('leads', 0)
    spend_vb = dados_vb.get('spend', 0.0)
    cpl_vb_texto = ""
    if leads_vb > 0:
        cpl_vb = spend_vb / leads_vb
        cpl_vb_texto = f"\n(CPL de R$ {cpl_vb:.2f})"
    
    total_leads_meta = meta.get('total', {}).get('leads', 0)

    return f"""*Relatório de Leads de ontem ({data_formatada})*

*1. Captação (Meta Ads):* {total_leads_meta}
- Bella Serra: 
{leads_bs}{cpl_bs_texto}

- Vista Bella: 
{leads_vb}{cpl_vb_texto}
"""

def montar_mensagem_saldo_meta(dados_meta):
    """
    --- NOVA FUNÇÃO ---
    Cria uma mensagem separada exibindo o saldo de cada conta de anúncios.
    """
    texto_saldo = "*Saldo das Contas de Anúncios (Meta Ads)*\n\n"
    
    # Itera sobre as contas para pegar o saldo de cada uma
    for nome_conta, dados_conta in dados_meta.items():
        # Ignora a chave 'total' que não representa uma conta
        if nome_conta == 'total':
            continue
        
        # Formata o nome da conta (ex: 'bella_serra' vira 'Bella Serra')
        nome_formatado = nome_conta.replace('_', ' ').title()
        saldo = dados_conta.get('balance', 0.0)
        
        texto_saldo += f"- {nome_formatado}: *R$ {saldo:.2f}*\n"
        
    return texto_saldo.strip()


def montar_mensagem_responsaveis(contagem_responsaveis):
    """
    Cria a mensagem com a contagem de leads por responsável.
    Esta função permanece a mesma.
    """
    texto_responsaveis = "*Leads 'Em Andamento' por Responsável:*\n"
    
    if not contagem_responsaveis:
        texto_responsaveis += "_Nenhuma contagem encontrada._\n"
    else:
        for nome, total in sorted(contagem_responsaveis.items()):
            texto_responsaveis += f"- {nome}: {total}\n"
            
    return texto_responsaveis
