from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('banco_mizu_final.db')
conn.row_factory = sqlite3.Row

usuarios = conn.execute("SELECT id, senha FROM usuarios").fetchall()

for u in usuarios:
    senha_atual = u['senha']
    if senha_atual and not senha_atual.startswith('scrypt:'):
        senha_hash = generate_password_hash(senha_atual)
        conn.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, u['id']))
        print(f"Senha do usuário {u['id']} convertida.")

conn.commit()
conn.close()
print("Concluído!")