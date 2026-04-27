import sqlite3
import os

def conectar():
    caminho_diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_banco = os.path.join(caminho_diretorio, "banco_mizu_final.db")
    return sqlite3.connect(caminho_banco)

def menu_principal_admin():
    while True:
        print("\n" + "="*30)
        print("    GESTÃO DE FERRAMENTARIA")
        print("="*30)
        print("1. Consultar Estoque")
        print("2. Cadastrar Novo Item")
        print("3. Gerenciar Acessos")
        print("0. Sair")
        
        opcao = input("\nSelecione uma operação: ")

        if opcao == "1":
            ver_ferramentas()
        elif opcao == "2":
            cadastrar_ferramenta()
        elif opcao == "3":
            cadastrar_novo_usuario()
        elif opcao == "0":
            break
        else:
            print("Entrada inválida.")

def ver_ferramentas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nome, status FROM itens")
    itens = cursor.fetchall()
    
    print("\n--- STATUS ATUAL DO INVENTÁRIO ---")
    for item in itens:
        print(f"Cód: {item[0]} | Item: {item[1]} | Status: {item[2]}")
    
    print(f"\nTotal de itens no sistema: {len(itens)}")
    conn.close()

def cadastrar_ferramenta():
    conn = conectar() 
    cursor = conn.cursor()
    
    print("\n--- REGISTRO DE ENTRADA DE PATRIMÔNIO ---")
    cod = input("Código de identificação: ")
    nome = input("Descrição da ferramenta: ")
    status = "Disponível"

    try:
        cursor.execute("INSERT INTO itens (codigo, nome, status) VALUES (?, ?, ?)", 
                       (cod, nome, status))
        
        conn.commit()
        print(f"\n✅ Ferramenta {nome} (Cód: {cod}) cadastrada com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao salvar: {e}")
    finally:
        conn.close()

def cadastrar_novo_usuario():
    conn = conectar()
    cursor = conn.cursor()
    print("\n--- CONTROLE DE ACESSO (OPERADORES) ---")
    nome = input("ID do colaborador: ").lower()
    senha = input("Chave de acesso: ")
    
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, 'operador')", 
                       (nome, senha))
        conn.commit()
        print(f"Acesso liberado para: {nome}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    menu_principal_admin()