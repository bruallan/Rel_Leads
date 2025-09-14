def analisar_e_auditar_dados(leads_bc, dados_leads_rd, data_relatorio):
    header = f"*Auditoria de Leads ({data_relatorio.strftime('%d/%m/%Y')})*\n"
    
    mapa_leads_bc = {lead['telefone']: lead for lead in leads_bc if lead.get('telefone')}
    mapa_leads_rd = {lead['telefone']: lead for lead in dados_leads_rd.get('lista_detalhada', []) if lead.get('telefone')}
    
    telefones_bc = set(mapa_leads_bc.keys())
    telefones_rd = set(mapa_leads_rd.keys())

    # ATUALIZAÇÃO: Adicionada a nova seção de auditoria
    texto_nao_atribuidos = ""
    lista_nao_atribuidos = dados_leads_rd.get('lista_nao_atribuidos', [])
    if lista_nao_atribuidos:
        texto_nao_atribuidos += f"\n*Leads 'Não Atribuídos' no RD Station ({len(lista_nao_atribuidos)}):*\n"
        for lead in lista_nao_atribuidos:
            # Garante que o telefone seja exibido corretamente mesmo que seja None
            telefone = lead.get('telefone') if lead.get('telefone') else "Telefone não encontrado"
            texto_nao_atribuidos += f"- {lead.get('nome', 'N/A')} ({telefone})\n"

    # Auditoria de Leads no RD sem produto (caso a categorização falhe)
    texto_auditoria_produto = ""
    leads_rd_sem_produto = []
    for tel, lead_rd in mapa_leads_rd.items():
        if not lead_rd.get('empreendimento_rd') or lead_rd.get('empreendimento_rd') == 'N/A':
            if tel in mapa_leads_bc:
                empreendimento_bc = mapa_leads_bc[tel].get('empreendimento_bc', 'Não preenchido no BC')
                leads_rd_sem_produto.append(f"- {lead_rd['nome']} ({tel}): BC indica '{empreendimento_bc}'")
    
    if leads_rd_sem_produto:
        texto_auditoria_produto += f"\n*Auditoria de Produto Faltando no RD ({len(leads_rd_sem_produto)}):*\n"
        texto_auditoria_produto += "\n".join(leads_rd_sem_produto)
        texto_auditoria_produto += "\n"

    # Análise de Discrepâncias
    texto_discrepancias = f"\n*Análise de Discrepâncias:*\n"
    rd_nao_bc = telefones_rd - telefones_bc
    bc_nao_rd = telefones_bc - telefones_rd
    
    texto_discrepancias += f"\n*Leads no RD que NÃO estão no BotConversa ({len(rd_nao_bc)}):*\n"
    if not rd_nao_bc: texto_discrepancias += "_Nenhum._\n"
    for tel in sorted(list(rd_nao_bc)):
        texto_discrepancias += f"- {mapa_leads_rd[tel]['nome']} ({tel})\n"
        
    texto_discrepancias += f"\n*Leads no BotConversa que NÃO foram para o RD ({len(bc_nao_rd)}):*\n"
    if not bc_nao_rd: texto_discrepancias += "_Nenhum._\n"
    for tel in sorted(list(bc_nao_rd)):
        texto_discrepancias += f"- {mapa_leads_bc[tel]['nome']} ({tel})\n"
        
    return header + texto_nao_atribuidos + texto_auditoria_produto + texto_discrepancias

def montar_mensagem_resumo(meta, bc_count, rd, data_relatorio):
    data_formatada = data_relatorio.strftime('%d/%m/%Y')
    return f"""
*Relatório de Leads de ontem ({data_formatada})*

*1. Captação (Meta Ads):* {meta.get('total', 0)}
- Bella Serra: {meta.get('bella_serra', 0)}
- Vista Bella: {meta.get('vista_bella', 0)}

"""

def montar_mensagem_analise(analise_texto, contagem_responsaveis):
    texto_responsaveis = "\n*Leads 'Em Andamento' por Responsável:*\n"
    for nome, total in contagem_responsaveis.items():
        texto_responsaveis += f"- {nome}: {total}\n"

    return analise_texto + texto_responsaveis
