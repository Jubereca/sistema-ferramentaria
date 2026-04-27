import sqlite3

def configurar():
    conn = sqlite3.connect("ferramentaria.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', '123')")
        conn.commit()
        print("✅ Sucesso! Tabela criada e usuario 'admin' cadastrado.")
    except:
        print("⚠️ Aviso: O usuario 'admin' ja estava cadastrado.")

    conn.close()

if __name__ == "__main__":
    configurar()
    
