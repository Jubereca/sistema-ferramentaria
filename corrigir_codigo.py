import sqlite3
conn = sqlite3.connect('banco_mizu_final.db')
# Busca todos os códigos com ## no início
problemas = conn.execute("SELECT id, codigo FROM itens WHERE codigo LIKE '##%'").fetchall()
for item in problemas:
    codigo_certo = item[1].lstrip('#')  # remove todos os # do início e deixa só o código
    conn.execute("UPDATE itens SET codigo = ? WHERE id = ?", (codigo_certo, item[0]))
    print(f"Corrigido: {item[1]} → {codigo_certo}")
conn.commit()
conn.close()
print("Concluído!")