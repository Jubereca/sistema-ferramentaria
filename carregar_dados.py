import sqlite3
import pandas as pd
NOME_BANCO = 'banco_mizu_final.db'
ARQUIVO_EXCEL = 'tb_saldos_localizacoes 2.xlsx'

def carregar_tudo_do_zero():
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        
        cursor.execute(f"DROP TABLE IF EXISTS itens") 
        cursor.execute("""
            CREATE TABLE itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT,
                nome TEXT,
                status TEXT,
                quantidade INTEGER
            )
        """)

        # 3. LÊ A PLANILHA
        print(f"🔄 Lendo: {ARQUIVO_EXCEL}")
        df = pd.read_excel(ARQUIVO_EXCEL, sheet_name='FERRAMENTARIA')

        for index, row in df.iterrows():
            c = str(row['COD']) if pd.notna(row['COD']) else f"S/C-{index}"
            n = str(row['DESC']) if pd.notna(row['DESC']) else "Sem Descrição"
            
            cursor.execute("INSERT INTO itens (codigo, nome, status, quantidade) VALUES (?, ?, ?, ?)", 
                           (c, n, "Disponível", 0))

        conn.commit()
        conn.close()
        print(f"\n✅ VITÓRIA! {len(df)} itens carregados em: {NOME_BANCO}")

    except Exception as e:
        print(f"\n❌ ERRO REAL: {e}")

if __name__ == "__main__":
    carregar_tudo_do_zero()
    