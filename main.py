from datetime import datetime, timedelta
import config
from api_meta import obter_dados_meta_ads
from api_botconversa import processar_contatos_botconversa, enviar_mensagem_pelo_botconversa
from api_rdstation import obter_dados_rdstation, obter_contagem_por_responsavel_rd
from relatorios import analisar_e_auditar_dados, montar_mensagem_resumo, montar_mensagem_analise

def trabalho_diario():
    data_alvo = datetime.now().date() - timedelta(days=1)
    print(f"--- INICIANDO ROTINA DIÁRIA PARA DADOS DE: {data_alvo.strftime('%d/%m/%Y')} ---")
    
    # Coleta de Todos os Dados
    dados_meta = obter_dados_meta_ads(data_alvo)
    leads_bc, mapa_contatos_bc = processar_contatos_botconversa(data_alvo)
    dados_leads_rd = obter_dados_rdstation(data_alvo)
    contagem_responsaveis = obter_contagem_por_responsavel_rd()
    
    # ATUALIZAÇÃO: Passando o objeto completo 'dados_leads_rd' para a análise
    texto_analise = analisar_e_auditar_dados(leads_bc, dados_leads_rd, data_alvo)
    
    mensagem_resumo = montar_mensagem_resumo(dados_meta, len(leads_bc), dados_leads_rd, data_alvo)
    mensagem_analise = montar_mensagem_analise(texto_analise, contagem_responsaveis)
    
    alertas = []
    if dados_meta.get('total', 0) == 0:
        alertas.append("ALERTA: A busca no Meta Ads não retornou leads.")
    if not leads_bc:
        alertas.append("ALERTA: A busca no BotConversa não retornou interações.")
    if dados_leads_rd.get('total', 0) == 0:
        alertas.append("ALERTA: A busca no RD Station não retornou cadastros.")
        
    if alertas:
        mensagem_analise += "\n\n" + "\n".join(alertas)

    # Envio dos Relatórios
    print("\n--- [GRUPO 1] ENVIANDO MENSAGEM DE RESUMO ---")
    print(mensagem_resumo)
    enviar_mensagem_pelo_botconversa(mensagem_resumo, config.CONTATOS_GRUPO_1, mapa_contatos_bc)

    print("\n--- [GRUPO 2] ENVIANDO MENSAGEM DE ANÁLISE ---")
    print(mensagem_analise)
    enviar_mensagem_pelo_botconversa(mensagem_analise, config.CONTATOS_GRUPO_2, mapa_contatos_bc)
    
    print(f"--- ROTINA DIÁRIA CONCLUÍDA ---\n")

if __name__ == "__main__":
    print("--- INICIANDO SCRIPT ---")
    trabalho_diario()
    print("--- FIM DO SCRIPT ---")