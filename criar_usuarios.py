import sqlite3

conn = sqlite3.connect("banco_mizu_final.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    setor_cargo TEXT NOT NULL,
    status TEXT DEFAULT 'Pendente'
)
""")

cursor.execute("INSERT INTO usuarios (nome, email, setor_cargo, status) VALUES (?, ?, ?, ?)", 
               ('lara clarisse da silva oliveira', 'lara.oliveira@mizu.com.br', 'formare', 'Aprovado'))

conn.commit()
conn.close()
print("Tabela criada com sucesso!")