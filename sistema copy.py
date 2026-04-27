import sqlite3

def conectar():
    return sqlite3.connect("ferramentaria.db")

def fazer_login():
    print("\n" + "="*30)
    print("      LOGIN - MIZU")
    print("="*30)
    user = input("Usuário: ")
    password = input("Senha: ")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (user, password))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        print("\n✅ Acesso liberado!")
        return True
    else:
        print("\n❌ Erro: Usuário ou senha incorretos.")
        return False

def cadastrar_ferramenta():
    print("\n--- NOVO CADASTRO DE FERRAMENTA ---")
    codigo = input("Código (ex: #001): ")
    nome = input("Nome da Ferramenta: ")
    status = "Disponível" 
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO itens (codigo, nome, quantidade_estoque) VALUES (?, ?, ?)", (codigo, nome, 1))
        conn.commit()
        print(f"✅ {nome} cadastrada com sucesso!")
    except Exception as e:
        print(f"❌ Erro: Este código já existe.")
    finally:
        conn.close()

def ver_inventario():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nome FROM itens")
    itens = cursor.fetchall()
    conn.close()

    print("\n" + "="*50)
    print(f"{'Cód':<10} | {'Ferramenta':<25} | {'Status'}")
    print("-" * 50)
    for i in itens:
        print(f"{i[0]:<10} | {i[1]:<25} | Disponível")
    print("="*50)

def cadastrar_movimentacao():

    pass

if fazer_login():
    while True:
        print("\n--- INVENTÁRIO GERAL - MIZU ---")
        print("1 - Registrar Movimentação")
        print("2 - Ver Histórico (Relatório)")
        print("3 - Cadastrar Nova Ferramenta (ADM)")
        print("4 - Ver Inventário Geral")
        print("0 - Sair")
        
        op = input("Escolha: ")
        if op == "1": print("Em breve...")
        elif op == "2": print("Em breve...")
        elif op == "3": cadastrar_ferramenta()
        elif op == "4": ver_inventario()
        elif op == "0": break
        import sqlite3
from datetime import datetime, timedelta

def registrar_saida():
    conn = sqlite3.connect('ferramentaria.db')
    cursor = conn.cursor()

    print("\n--- REGISTRAR SAÍDA DE FERRAMENTA ---")
    cod_item = input("Código do Item (ex: M011061014): ")
    colaborador = input("Nome do Colaborador: ").upper()
    prazo_dias = int(input("Prazo para devolução (em dias): "))

    # Cálculos de data
    data_saida = datetime.now().strftime('%d/%m/%Y')
    prazo_devolucao = (datetime.now() + timedelta(days=prazo_dias)).strftime('%d/%m/%Y')

    # Salva na tabela de movimentacoes
    cursor.execute("""
        INSERT INTO movimentacoes (codigo_item, colaborador, data_saida, prazo_devolucao, status)
        VALUES (?, ?, ?, ?, ?)
    """, (cod_item, colaborador, data_saida, prazo_devolucao, 'EM USO'))

    conn.commit()
    conn.close()
    print(f"\n✅ Saída registrada! {colaborador} deve devolver em {prazo_devolucao}.")
    
