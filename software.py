import sqlite3
from datetime import datetime

def criar_tabela():
    conexao = sqlite3.connect("portaria.db")
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT NOT NULL,
            matricula TEXT NOT NULL,
            empresa TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

def registrar_movimentacao(cpf, matricula, empresa, tipo):
    conexao = sqlite3.connect("portaria.db")
    cursor = conexao.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO registros (cpf, matricula, empresa, data_hora, tipo) VALUES (?, ?, ?, ?, ?)",
                   (cpf, matricula, empresa, data_hora, tipo))
    conexao.commit()
    conexao.close()
    print(f"{tipo} registrada com sucesso para {cpf} às {data_hora}.")

def listar_registros():
    conexao = sqlite3.connect("portaria.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM registros")
    registros = cursor.fetchall()
    conexao.close()
    
    print("\nRegistros de Movimentação:")
    for reg in registros:
        print(f"ID: {reg[0]} | CPF: {reg[1]} | Matrícula: {reg[2]} | Empresa: {reg[3]} | Data/Hora: {reg[4]} | Tipo: {reg[5]}")

def menu():
    criar_tabela()
    while True:
        print("\n===== Sistema de Controle de Portaria =====")
        print("1. Registrar Entrada")
        print("2. Registrar Saída")
        print("3. Listar Registros")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cpf = input("Informe o CPF: ")
            matricula = input("Informe a Matrícula: ")
            empresa = input("Informe a Empresa: ")
            registrar_movimentacao(cpf, matricula, empresa, "Entrada")
        elif opcao == "2":
            cpf = input("Informe o CPF: ")
            matricula = input("Informe a Matrícula: ")
            empresa = input("Informe a Empresa: ")
            registrar_movimentacao(cpf, matricula, empresa, "Saída")
        elif opcao == "3":
            listar_registros()
        elif opcao == "4":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu()
