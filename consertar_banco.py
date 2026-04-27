import sqlite3

conn = sqlite3.connect("banco_mizu_final.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE itens ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)")
    # Adiciona também as colunas de controle que vamos usar na tabela de uso
    cursor.execute("ALTER TABLE itens ADD COLUMN quantidade_em_uso INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE itens ADD COLUMN data_saida TEXT")
    cursor.execute("ALTER TABLE itens ADD COLUMN prazo_devolucao TEXT")
    conn.commit()
    print("Banco atualizado com sucesso! Agora o erro vai sumir.")
except Exception as e:
    print(f"Aviso: {e}") 
finally:
    conn.close()