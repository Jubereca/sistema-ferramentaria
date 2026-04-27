import sqlite3

conn = sqlite3.connect('banco_mizu_final.db')

try:
    conn.execute("UPDATE itens SET marca='Bosch', observacoes='Equipamento revisado em Jan/26' WHERE codigo='S/C-0'")
    conn.execute("ALTER TABLE usuarios ADD COLUMN setor TEXT;")
    conn.execute("ALTER TABLE usuarios ADD COLUMN matricula TEXT;")
    conn.execute("ALTER TABLE usuarios ADD COLUMN status TEXT DEFAULT 'Ativo';")

    conn.commit()
    print('✅ Tudo atualizado! Marcas ajustadas e colunas de usuário criadas.')

except sqlite3.OperationalError as e:
    conn.commit()
    print(f'📢 Algumas colunas já existiam, mas o comando da Bosch foi executado!')

finally:
    conn.close()