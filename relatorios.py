# relatorios.py (VERSÃO SIMPLIFICADA)

def montar_mensagem_resumo(meta, data_relatorio):
    """
    Cria a mensagem de resumo de captação do Meta Ads.
    Esta função permanece a mesma.
    """
    data_formatada = data_relatorio.strftime('%d/%m/%Y')

    # Extrai os dados para Bella Serra e calcula o CPL
    dados_bs = meta.get('bella_serra', {'leads': 0, 'spend': 0.0})
    leads_bs = dados_bs.get('leads', 0)
    spend_bs = dados_bs.get('spend', 0.0)
    cpl_bs_texto = ""
    if leads_bs > 0:
        cpl_bs = spend_bs / leads_bs
        cpl_bs_texto = f"\n(CPL de R$ {cpl_bs:.2f})"

    # Extrai os dados para Vista Bella e calcula o CPL
    dados_vb = meta.get('vista_bella', {'leads': 0, 'spend': 0.0})
    leads_vb = dados_vb.get('leads', 0)
    spend_vb = dados_vb.get('spend', 0.0)
    cpl_vb_texto = ""
    if leads_vb > 0:
        cpl_vb = spend_vb / leads_vb
        cpl_vb_texto = f"\n(CPL de R$ {cpl_vb:.2f})"
    
    total_leads_meta = meta.get('total', {}).get('leads', 0)

    # Note que os parâmetros `bc_count` e `rd` foram removidos da chamada da função
    # pois não eram utilizados aqui.
    return f"""*Relatório de Leads de ontem ({data_formatada})*

*1. Captação (Meta Ads):* {total_leads_meta}
- Bella Serra: 
{leads_bs}{cpl_bs_texto}

- Vista Bella: 
{leads_vb}{cpl_vb_texto}
"""

def montar_mensagem_responsaveis(contagem_responsaveis):
    """
    NOVA FUNÇÃO: Cria APENAS a mensagem com a contagem de leads por responsável.
    """
    texto_responsaveis = "*Leads 'Em Andamento' por Responsável:*\n"
    
    if not contagem_responsaveis:
        texto_responsaveis += "_Nenhuma contagem encontrada._\n"
    else:
        # Ordena os responsáveis por nome para um relatório mais organizado
        for nome, total in sorted(contagem_responsaveis.items()):
            texto_responsaveis += f"- {nome}: {total}\n"
            
    return texto_responsaveis

# As funções `analisar_e_auditar_dados` e `montar_mensagem_analise` foram removidas.
