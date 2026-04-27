import sqlite3

def resetar_usuarios():
    # Conecta no seu banco de dados
    conn = sqlite3.connect("banco_mizu_final.db")
    cursor = conn.cursor()

    print("Tentando atualizar a tabela de usuários...")

    cursor.execute("DROP TABLE IF EXISTS usuarios")
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            setor_cargo TEXT,
            status TEXT DEFAULT 'Aprovado'
        )
    ''')

    cursor.execute('''
        INSERT INTO usuarios (nome, email, setor_cargo, status)
        VALUES ('Lara Clarisse', 'lara.oliveira@mizu.com.br', 'Formare', 'Aprovado')
    ''')
    conn.commit()
    conn.close()
    print("✅ SUCESSO! A coluna 'id' foi criada e a tabela resetada.")

if __name__ == "__main__":
    resetar_usuarios()