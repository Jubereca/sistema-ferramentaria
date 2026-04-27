import sqlite3

conn = sqlite3.connect("banco_mizu_final.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_item INTEGER,
    colaborador TEXT NOT NULL,
    tipo_movimentacao TEXT NOT NULL, 
    quantidade INTEGER NOT NULL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (id_item) REFERENCES itens(id)
)
""")

conn.commit()
print("✅ Banco banco_mizu_final.db estruturado com sucesso!")
conn.close()


