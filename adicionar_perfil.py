import sqlite3

conn = sqlite3.connect("banco_mizu_final.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN perfil TEXT DEFAULT 'FUNCIONÁRIO'")
    conn.commit()
    print("✅ Sucesso: Coluna 'perfil' adicionada!")
except Exception as e:
    print(f"⚠️ Aviso: A coluna já deve existir ou houve um erro: {e}")

cursor.execute("UPDATE usuarios SET perfil = 'ADMINISTRADOR' WHERE email LIKE '%julia%' OR nome LIKE '%julia%'")
conn.commit()
conn.close()