import sqlite3

conn = sqlite3.connect('banco_mizu_final.db')
conn.row_factory = sqlite3.Row

duplicados = conn.execute('''
    SELECT codigo FROM itens 
    GROUP BY codigo 
    HAVING COUNT(*) > 1
''').fetchall()

print(f"Consolidando {len(duplicados)} grupos de itens duplicados...")

for dup in duplicados:
    codigo = dup['codigo']
    itens = conn.execute('SELECT * FROM itens WHERE codigo = ? ORDER BY id ASC', (codigo,)).fetchall()
    
    disponiveis = sum(1 for i in itens if i['status'] == 'Disponível')
    em_uso = sum(1 for i in itens if i['status'] == 'Em Uso')
    reservados = sum(1 for i in itens if i['status'] == 'Reservado')
    total = len(itens)
    
    if em_uso > 0 and disponiveis == 0:
        status_final = 'Em Uso'
    elif reservados > 0 and disponiveis == 0:
        status_final = 'Reservado'
    elif disponiveis > 0:
        status_final = 'Disponível'
    else:
        status_final = itens[0]['status']
    
    primeiro_id = itens[0]['id']
    conn.execute('UPDATE itens SET quantidade = ?, status = ? WHERE id = ?', (total, status_final, primeiro_id))
    
    outros_ids = [i['id'] for i in itens[1:]]
    for oid in outros_ids:
        conn.execute('DELETE FROM itens WHERE id = ?', (oid,))
    
    print(f"  {codigo}: {total} itens → status: {status_final}, quantidade: {total}")

conn.commit()
total_final = conn.execute('SELECT COUNT(*) FROM itens').fetchone()[0]
print(f"\nConcluído! Total de itens agora: {total_final}")
conn.close()