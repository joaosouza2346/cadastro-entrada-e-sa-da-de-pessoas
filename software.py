from datetime import datetime
import hashlib
import getpass

registros = []
usuarios = {}

def cadastrar_usuario():
    usuario = input("Informe um nome de usuário: ")
    cpf = input("Informe o CPF: ")
    empresa = input("Informe o nome da empresa: ")
    senha = getpass.getpass("Informe uma senha: ")
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    usuarios[usuario] = {"senha": senha_hash, "empresa": empresa, "cpf": cpf}
    print("Usuário cadastrado com sucesso!")

def autenticar_usuario():
    usuario = input("Informe seu usuário: ")
    senha = getpass.getpass("Informe sua senha: ")
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    if usuario in usuarios and usuarios[usuario]["senha"] == senha_hash:
        print("Autenticação bem-sucedida!")
        return usuario
    else:
        print("Usuário ou senha incorretos!")
        return None

def registrar_movimentacao(usuario, matricula, passagem_policia, pcd, tipo):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    empresa = usuarios[usuario]["empresa"]
    cpf = usuarios[usuario]["cpf"]
    registros.append({
        "cpf": cpf,
        "matricula": matricula,
        "empresa": empresa,
        "passagem_policia": passagem_policia,
        "pcd": pcd,
        "data_hora": data_hora,
        "tipo": tipo
    })
    print(f"{tipo} registrada com sucesso para {cpf} às {data_hora}.")

def listar_registros():
    print("\nRegistros de Movimentação:")
    for reg in registros:
        print(f"CPF: {reg['cpf']} | Matrícula: {reg['matricula']} | Empresa: {reg['empresa']} | Passagem pela Polícia: {reg['passagem_policia']} | PCD: {reg['pcd']} | Data/Hora: {reg['data_hora']} | Tipo: {reg['tipo']}")

def menu():
    while True:
        print("\n===== Sistema de Controle de Portaria =====")
        print("1. Cadastrar Usuário")
        print("2. Registrar Entrada")
        print("3. Registrar Saída")
        print("4. Listar Registros")
        print("5. Sair")
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_usuario()
        elif opcao in ["2", "3"]:
            usuario = autenticar_usuario()
            if usuario:
                matricula = input("Informe a Matrícula: ")
                passagem_policia = input("Já teve passagem pela polícia? (Sim/Não): ")
                pcd = input("É PCD? (Sim/Não): ")
                tipo = "Entrada" if opcao == "2" else "Saída"
                registrar_movimentacao(usuario, matricula, passagem_policia, pcd, tipo)
        elif opcao == "4":
            listar_registros()
        elif opcao == "5":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu()
