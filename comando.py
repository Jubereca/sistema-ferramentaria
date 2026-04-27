import sqlite3
conn = sqlite3.connect("banco_mizu_final.db")
cursor = conn.cursor()
cursor.execute("UPDATE usuarios SET tipo = 'admin' WHERE usuario = 'julia.silva'")
conn.commit()
conn.close()
print("Pronto! Agora o sistema vai te reconhecer como Admin.")