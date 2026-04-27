import sqlite3

def ajustar():
    conn = sqlite3.connect("banco_mizu_final.db")
    cursor = conn.cursor()
    
    colunas_novas = [
        ("data_saida", "TEXT"),
        ("prazo_devolucao", "TEXT"),
        ("data_devolucao_real", "TEXT")
    ]
    
    for nome_col, tipo in colunas_novas:
        try:
            cursor.execute(f"ALTER TABLE movimentacoes ADD COLUMN {nome_col} {tipo}")
            print(f"✅ Coluna {nome_col} adicionada!")
        except sqlite3.OperationalError:
            print(f"⚠️ Coluna {nome_col} já existia.")

    conn.commit()
    conn.close()
    print("\n🚀 Banco de dados pronto para o seu sistema!")

if __name__ == "__main__":
    ajustar()