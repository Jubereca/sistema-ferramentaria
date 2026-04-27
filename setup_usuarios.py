import sqlite3

def configurar_usuarios():
    conn = sqlite3.connect("ferramentaria.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL
    )
    """)

    try:
        cursor.execute("INSERT INTO usuarios (login, senha, cargo) VALUES ('admin', '1234', 'ADM')")
        cursor.execute("INSERT INTO usuarios (login, senha, cargo) VALUES ('user', '5678', 'FUNC')")
        conn.commit()
        print("✅ Tabela de usuários criada e acessos de teste liberados!")
    except:
        print("⚠️ Usuários de teste já existem.")

    conn.close()

configurar_usuarios()
