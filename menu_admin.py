import sqlite3
from datetime import datetime, timedelta

def conectar():
    return sqlite3.connect("banco_mizu_final.db")

def fazer_login():
    print("\n" + "="*35)
    print("      SISTEMA MIZU - LOGIN")
    print("="*35)
    user = input("ID do Colaborador: ").lower()
    senha = input("Senha/Chave: ")
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM usuarios WHERE usuario = ? AND senha = ?", (user, senha))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return user, resultado[0]
    else:
        print("\n❌ Login ou senha incorretos!")
        return None, None

def ver_estoque():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nome, status FROM itens")
    print("\n--- CONSULTA DE ESTOQUE ---")
    for i in cursor.fetchall():
        print(f"[{i[2]}] {i[0]} - {i[1]}")
    conn.close()

def verificar_atrasos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT usuario, item_codigo, prazo_devolucao 
        FROM movimentacoes 
        WHERE data_devolucao_real IS NULL AND acao = 'Empréstimo'
    """)
    pendentes = cursor.fetchall()
    conn.close()

    hoje = datetime.now()
    print("\n" + "!"*40)
    print("   RELATÓRIO DE ATRASOS (ADMIN)")
    print("!"*40)

    encontrou_atraso = False
    for p in pendentes:
        u, cod, prazo_str = p
        prazo_dt = datetime.strptime(prazo_str, "%d/%m/%Y")
        if hoje > prazo_dt:
            print(f"🚨 ATRASO: {u.upper()} está com o item {cod} (Venceu em {prazo_str})")
            encontrou_atraso = True
    
    if not encontrou_atraso: 
        print("✅ Tudo em ordem ou nenhum item atrasado no momento.")

def reservar_ferramenta():
    print("\n--- RESERVAR / BLOQUEAR ITEM ---")
    codigo = input("Código da ferramenta: ")
    try:
        dias = int(input("Bloquear por quantos dias? "))
        prazo = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE itens SET status = 'RESERVADO', reservado_ate = ? WHERE codigo = ?", (prazo, codigo))
        conn.commit()
        conn.close()
        print(f"✅ Item {codigo} reservado até {prazo}.")
    except: 
        print("❌ Erro na reserva.")

def excluir_item():
    print("\n--- EXCLUIR ITEM DO SISTEMA ---")
    codigo = input("Digite o Código do item para REMOVER: ")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itens WHERE codigo = ?", (codigo,))
    conn.commit()
    conn.close()
    print(f"⚠️ Item {codigo} removido.")

def cadastrar_item():
    print("\n--- CADASTRAR NOVO ITEM ---")
    nome = input("Nome da ferramenta: ")
    codigo = input("Código/TAG: ")
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO itens (codigo, nome, status) VALUES (?, ?, 'Disponível')", (codigo, nome))
        conn.commit()
        print(f"✅ Item {nome} cadastrado!")
    except: 
        print("❌ Erro: Código já existe.")
    conn.close()

def gerenciar_usuarios():
    print("\n--- CADASTRO DE COLABORADOR ---")
    nome = input("Novo ID: ").lower()
    senha = input("Senha: ")
    tipo = input("Tipo (admin/operador): ").lower()
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)", (nome, senha, tipo))
        conn.commit()
        print(f"✅ Usuário {nome} criado.")
    except: 
        print("❌ Erro ao criar usuário.")
    conn.close()

def registrar_saida():
    print("\n" + "="*30)
    print("      REGISTRAR EMPRÉSTIMO")
    print("="*30)
    
    codigo = input("ID da Ferramenta: ")
    funcionario = input("Quem está pegando? (Nome do Funcionário): ")
    
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome, status FROM itens WHERE codigo = ?", (codigo,))
    item = cursor.fetchone()

    if item and item[1] == 'Disponível':
        try:
            dias = int(input("Prazo para devolução (em quantos dias?): "))
            data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            data_prazo = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")

            cursor.execute("UPDATE itens SET status = 'Em Uso' WHERE codigo = ?", (codigo,))
            cursor.execute("""
                INSERT INTO movimentacoes (usuario, item_codigo, acao, data_saida, prazo_devolucao, data_devolucao_real) 
                VALUES (?, ?, 'Empréstimo', ?, ?, NULL)
            """, (funcionario, codigo, data_hoje, data_prazo))
            
            conn.commit()
            print(f"\n✅ SUCESSO! {item[0]} entregue a {funcionario}.")
            print(f"📅 Deve ser devolvido até: {data_prazo}")
        except ValueError:
            print("❌ Erro: Digite apenas números para os dias.")
    else:
        print(f"❌ Erro: Item {codigo} não encontrado ou já está em uso!")
    conn.close()

def registrar_entrada():
    print("\n--- REGISTRAR DEVOLUÇÃO ---")
    codigo = input("ID da Ferramenta que está voltando: ")
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE itens SET status = 'Disponível' WHERE codigo = ?", (codigo,))
    cursor.execute("""
        UPDATE movimentacoes 
        SET data_devolucao_real = ?, acao = 'Devolvido' 
        WHERE item_codigo = ? AND data_devolucao_real IS NULL
    """, (data_agora, codigo))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Devolução do item {codigo} registrada com sucesso!")
    else:
        print("⚠️ Aviso: Não encontrei nenhum empréstimo pendente para este código.")
    conn.close()

# --- 5. MENU PRINCIPAL ---
def exibir_menu(usuario, nivel):
    while True:
        print(f"\nOPERADOR: {usuario.upper()}")
        print("="*40)
        print("1. Consultar Estoque")
        print("2. Cadastrar Novo Item")
        print("3. Gerenciar Usuários")
        print("4. Retirar Ferramenta (Baixa)")
        print("5. Devolver Ferramenta")
        
        if nivel == 'admin':
            print("6. Verificar Atrasos")
            print("7. Reservar Item")
            print("8. Excluir Item")
            
        print("0. Sair")
        op = input("\nOperação: ")

        if op == "1": ver_estoque()
        elif op == "2": cadastrar_item()
        elif op == "3": gerenciar_usuarios()
        elif op == "4": registrar_saida()
        elif op == "5": registrar_entrada()
        elif op == "6" and nivel == 'admin': verificar_atrasos()
        elif op == "7" and nivel == 'admin': reservar_ferramenta()
        elif op == "8" and nivel == 'admin': excluir_item()
        elif op == "0": break

if __name__ == "__main__":
    conn = conectar()
    c = conn.cursor()
    
    c.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT, tipo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS itens (codigo TEXT PRIMARY KEY, nome TEXT, status TEXT, reservado_ate TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, item_codigo TEXT, 
                 acao TEXT, data_saida TEXT, prazo_devolucao TEXT, data_devolucao_real TEXT)""")
    
    try:
        c.execute("ALTER TABLE itens ADD COLUMN reservado_ate TEXT")
    except sqlite3.OperationalError: pass 
        
    conn.commit()
    conn.close()

    user, nivel = fazer_login()
    if user: 
        exibir_menu(user, nivel)
        