import pandas as pd
import json

# --- CONFIGURAÇÕES ---
# O nome do seu ficheiro CSV. Garanta que ele esteja na mesma pasta que este script.
NOME_FICHEIRO_CSV = 'Relação de Campos RD e BotConversa.xlsx - Planilha1.csv'

# Os nomes exatos das colunas na sua planilha.
# ATENÇÃO: Se os nomes na sua planilha forem diferentes, ajuste-os aqui.
COLUNA_NOME_BC = 'CAMPO REFERENTE NO BOTCONVERSA'
COLUNA_ID_RD = ' ID DO CAMPO NO RD STATION'

# O nome do ficheiro JSON que será gerado.
NOME_FICHEIRO_JSON = 'mapa_sincronizacao.json'
# --------------------

def criar_mapa_de_sincronizacao():
    """
    Lê o ficheiro CSV com a relação de campos e gera um
    ficheiro JSON de mapeamento para a sincronização.
    """
    print(f"Lendo o ficheiro de mapeamento: '{NOME_FICHEIRO_CSV}'...")
    
    try:
        df = pd.read_csv(NOME_FICHEIRO_CSV, encoding='latin-1', sep=';')
        
        df = df.dropna(subset=[COLUNA_NOME_BC, COLUNA_ID_RD])

        mapa_final = {}
        
        for index, row in df.iterrows():
            nome_campo_bc = str(row[COLUNA_NOME_BC]).strip()
            id_campo_rd = str(row[COLUNA_ID_RD]).strip()
            
            # --- CORREÇÃO AQUI ---
            # Adiciona a relação ao nosso mapa, IGNORANDO a chave "N/A"
            if nome_campo_bc and id_campo_rd and nome_campo_bc.upper() != 'N/A':
                mapa_final[nome_campo_bc] = id_campo_rd

        with open(NOME_FICHEIRO_JSON, 'w', encoding='utf-8') as f:
            json.dump(mapa_final, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Sucesso! O mapa de sincronização foi criado com {len(mapa_final)} regras.")
        print(f"O ficheiro '{NOME_FICHEIRO_JSON}' foi gerado na sua pasta.")

    except FileNotFoundError:
        print(f"\nERRO: O ficheiro '{NOME_FICHEIRO_CSV}' não foi encontrado.")
        print("Por favor, garanta que ele está na mesma pasta que este script.")
    except KeyError as e:
        print(f"\nERRO: A coluna {e} não foi encontrada no seu ficheiro CSV.")
        print("Por favor, verifique os nomes das colunas na sua planilha e ajuste no script.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    criar_mapa_de_sincronizacao()