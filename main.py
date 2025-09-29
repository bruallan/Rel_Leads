# main.py (VERSÃO ATUALIZADA)

from datetime import datetime, timedelta
import config
from api_meta import obter_dados_meta_ads
from api_botconversa import processar_contatos_botconversa, enviar_mensagem_pelo_botconversa
from api_rdstation import obter_contagem_por_responsavel_rd
# ATENÇÃO: A importação foi ajustada para as novas funções de relatório
from relatorios import montar_mensagem_resumo, montar_mensagem_responsaveis

def trabalho_diario():
    data_alvo = datetime.now().date() - timedelta(days=1)
    print(f"--- INICIANDO ROTINA DIÁRIA PARA DADOS DE: {data_alvo.strftime('%d/%m/%Y')} ---")
    
    # --- Coleta de Dados ---
    # A coleta de dados permanece a mesma, mas não usaremos todos os dados para os relatórios.
    dados_meta = obter_dados_meta_ads(data_alvo)
    _, mapa_contatos_bc = processar_contatos_botconversa(data_alvo) # O '_' ignora os leads do BC que não serão usados no relatório
    contagem_responsaveis = obter_contagem_por_responsavel_rd()
    
    # --- Montagem dos Relatórios ---
    # A chamada para `analisar_e_auditar_dados` foi REMOVIDA.

    # Relatório para o Grupo 1 (Resumo do Meta Ads)
    mensagem_resumo = montar_mensagem_resumo(dados_meta, data_alvo)
    
    # Relatório para o Grupo 2 (Apenas a contagem por responsável)
    mensagem_responsaveis = montar_mensagem_responsaveis(contagem_responsaveis)

    # --- Envio dos Relatórios ---
    print("\n--- [GRUPO 1] ENVIANDO MENSAGEM DE RESUMO ---")
    print(mensagem_resumo)
    enviar_mensagem_pelo_botconversa(mensagem_resumo, config.CONTATOS_GRUPO_1, mapa_contatos_bc)

    print("\n--- [GRUPO 2] ENVIANDO MENSAGEM DE RESPONSÁVEIS ---")
    print(mensagem_responsaveis)
    enviar_mensagem_pelo_botconversa(mensagem_responsaveis, config.CONTATOS_GRUPO_2, mapa_contatos_bc)
    
    print(f"--- ROTINA DIÁRIA CONCLUÍDA ---\n")

if __name__ == "__main__":
    print("--- INICIANDO SCRIPT ---")
    trabalho_diario()
    print("--- FIM DO SCRIPT ---")
