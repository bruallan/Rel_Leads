import random
import time
from config_sync import LIMITE_DE_LEADS_PARA_SINC
from api_handler import (
    carregar_mapa_sincronizacao,
    encontrar_leads_integrados,
    buscar_deal_rdstation,
    atualizar_deal_rdstation,
    atualizar_subscriber_botconversa,
)

def gerar_relatorio_comparativo(titulo, lead_bc, deal_rd, mapa):
    """Imprime uma tabela comparativa dos dados do lead."""
    print("\n" + "="*80)
    print(f"  {titulo.upper()}")
    print("="*80)
    tabela = []
    variaveis_bc = lead_bc.get('variables', {})
    mapa_campos_rd = {campo['custom_field_id']: campo['value'] for campo in deal_rd.get('deal_custom_fields', [])}
    for campo_bc, id_campo_rd in mapa.items():
        valor_bc = variaveis_bc.get(campo_bc)
        valor_rd = mapa_campos_rd.get(id_campo_rd)
        valor_bc_str = str(valor_bc or '').strip()
        valor_rd_str = str(valor_rd or '').strip()
        equivalente = "Sim ✅" if valor_bc_str == valor_rd_str else "Não ❌"
        tabela.append([campo_bc, valor_bc, valor_rd, equivalente])
    if not tabela:
        print("\nNenhum campo mapeado encontrado para comparar.")
        return

    # Lógica para formatação da tabela...
    try:
        max_campo = max(len(row[0]) for row in tabela)
        max_bc = max(len(str(row[1])) for row in tabela)
        max_rd = max(len(str(row[2])) for row in tabela)
    except ValueError:
        max_campo, max_bc, max_rd = 15, 20, 20

    print(f"\n{'CAMPO':<{max_campo}} | {'VALOR NO BOTCONVERSA':<{max_bc}} | {'VALOR NO RD STATION':<{max_rd}} | ESTÁ EQUIVALENTE?")
    print(f"{'-'*max_campo}-|-{'-'*max_bc}-|-{'-'*max_rd}-|------------------")
    for row in tabela:
        print(f"{row[0]:<{max_campo}} | {str(row[1]):<{max_bc}} | {str(row[2]):<{max_rd}} | {row[3]}")

if __name__ == "__main__":
    mapa_sinc = carregar_mapa_sincronizacao()
    if not mapa_sinc: exit()

    todos_leads_integrados = encontrar_leads_integrados()
    if not todos_leads_integrados: exit()

    limite = min(LIMITE_DE_LEADS_PARA_SINC, len(todos_leads_integrados))
    leads_sorteados = random.sample(todos_leads_integrados, limite)
    print(f"\nSorteando {limite} leads para a sincronização...")

    for i, lead_bc_antes in enumerate(leads_sorteados):
        print("\n" + "#"*80)
        print(f"#  PROCESSANDO LEAD {i+1}/{limite}: {lead_bc_antes.get('full_name')}")
        print("#"*80)

        id_rd = lead_bc_antes.get('variables', {}).get('RD-IDNegociacao')
        deal_rd_antes = buscar_deal_rdstation(id_rd)
        if not deal_rd_antes:
            print(f"Não foi possível buscar a negociação ID {id_rd}. Pulando para o próximo.")
            continue

        gerar_relatorio_comparativo(f"RELATÓRIO ANTES DA SINCRONIZAÇÃO - {lead_bc_antes.get('full_name')}", lead_bc_antes, deal_rd_antes, mapa_sinc)

        updates_para_rd = {}
        updates_para_bc = {}
        variaveis_bc_antes = lead_bc_antes.get('variables', {})
        mapa_campos_rd_antes = {campo['custom_field_id']: campo['value'] for campo in deal_rd_antes.get('deal_custom_fields', [])}

        for campo_bc, id_campo_rd in mapa_sinc.items():
            valor_bc = variaveis_bc_antes.get(campo_bc)
            valor_rd = mapa_campos_rd_antes.get(id_campo_rd)
            valor_bc_str = str(valor_bc or '').strip()
            valor_rd_str = str(valor_rd or '').strip()

            if valor_bc_str != valor_rd_str:
                if valor_bc_str and not valor_rd_str:
                    updates_para_rd[id_campo_rd] = valor_bc
                else: # RD é o mestre se ambos tiverem valor ou se BC estiver vazio
                    updates_para_bc[campo_bc] = valor_rd
        
        if not updates_para_rd and not updates_para_bc:
            print("\nNenhuma atualização necessária para este lead.")
            continue

        if updates_para_rd:
            atualizar_deal_rdstation(id_rd, updates_para_rd)
        if updates_para_bc:
            atualizar_subscriber_botconversa(lead_bc_antes['id'], variaveis_bc_antes, updates_para_bc)

        print("\nAguardando 5 segundos para as APIs processarem...")
        time.sleep(5)
        
        lead_bc_depois = lead_bc_antes # Para o relatório, assumimos a atualização
        deal_rd_depois = buscar_deal_rdstation(id_rd)
        if deal_rd_depois:
            # Para o relatório 'depois', atualizamos as variáveis do BC com o que foi enviado
            lead_bc_depois.get('variables', {}).update(updates_para_bc)
            gerar_relatorio_comparativo(f"RELATÓRIO DEPOIS DA SINCRONIZAÇÃO - {lead_bc_antes.get('full_name')}", lead_bc_depois, deal_rd_depois, mapa_sinc)

    print("\n\n--- Sincronização em lote concluída ---")