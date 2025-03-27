from datetime import datetime
import hashlib
import getpass
import re
import json
import os

registros = []
usuarios = {}
ARQUIVO_REGISTROS = "registros_mprj_csi.json"

# Carregar registros salvos ao iniciar
if os.path.exists(ARQUIVO_REGISTROS):
    with open(ARQUIVO_REGISTROS, "r") as f:
        registros = json.load(f)


def validar_cpf(cpf):
    # Remove caracteres não numéricos e verifica se tem 11 dígitos
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()


def cadastrar_usuario():
    usuario = input("Informe um nome de usuário: ").strip()
    if usuario in usuarios:
        print("Usuário já existe!")
        return

    cpf = input("Informe o CPF (somente números): ")
    if not validar_cpf(cpf):
        print("CPF inválido! Deve conter 11 dígitos numéricos.")
        return

    nome = input("Informe o nome completo: ").strip()
    cargo = input("Informe o cargo (ex.: Analista, Técnico): ").strip()
    nivel_acesso = input("Nível de acesso (admin/usuario): ").lower()
    if nivel_acesso not in ["admin", "usuario"]:
        print("Nível de acesso inválido! Use 'admin' ou 'usuario'.")
        return

    senha = getpass.getpass("Informe uma senha: ")
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    usuarios[usuario] = {
        "senha": senha_hash,
        "cpf": cpf,
        "nome": nome,
        "cargo": cargo,
        "empresa": "MPRJ",
        "nivel_acesso": nivel_acesso
    }
    print("Usuário cadastrado com sucesso!")


def autenticar_usuario():
    usuario = input("Informe seu usuário: ").strip()
    senha = getpass.getpass("Informe sua senha: ")
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    if usuario in usuarios and usuarios[usuario]["senha"] == senha_hash:
        print(f"Autenticação bem-sucedida! Bem-vindo(a), {usuarios[usuario]['nome']}.")
        return usuario
    else:
        print("Usuário ou senha incorretos!")
        return None


def registrar_movimentacao(usuario, matricula, passagem_policia, pcd, tipo):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = {
        "cpf": usuarios[usuario]["cpf"],
        "nome": usuarios[usuario]["nome"],
        "matricula": matricula,
        "empresa": "MPRJ",
        "passagem_policia": passagem_policia,
        "pcd": pcd,
        "data_hora": data_hora,
        "tipo": tipo,
        "registrado_por": usuario
    }
    registros.append(registro)
    with open(ARQUIVO_REGISTROS, "w") as f:
        json.dump(registros, f, indent=4)
    print(f"{tipo} registrada com sucesso para {registro['nome']} às {data_hora}.")


def listar_registros():
    if not registros:
        print("Nenhum registro encontrado.")
        return
    print("\nRegistros de Movimentação (MPRJ CSI):")
    for reg in registros:
        print(f"Nome: {reg['nome']} | CPF: {reg['cpf']} | Matrícula: {reg['matricula']} | "
              f"Passagem pela Polícia: {reg['passagem_policia']} | PCD: {reg['pcd']} | "
              f"Data/Hora: {reg['data_hora']} | Tipo: {reg['tipo']} | Registrado por: {reg['registrado_por']}")


def buscar_registro_por_cpf():
    cpf = input("Informe o CPF para busca: ")
    encontrados = [reg for reg in registros if reg["cpf"] == cpf]
    if not encontrados:
        print("Nenhum registro encontrado para este CPF.")
    else:
        print(f"\nRegistros encontrados para CPF {cpf}:")
        for reg in encontrados:
            print(f"Nome: {reg['nome']} | Matrícula: {reg['matricula']} | Tipo: {reg['tipo']} | "
                  f"Data/Hora: {reg['data_hora']}")


def menu():
    while True:
        print("\n===== Sistema de Controle de Portaria - MPRJ CSI =====")
        print("1. Cadastrar Usuário")
        print("2. Registrar Entrada")
        print("3. Registrar Saída")
        print("4. Listar Todos os Registros")
        print("5. Buscar Registro por CPF")
        print("6. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            usuario = autenticar_usuario()
            if usuario and usuarios[usuario]["nivel_acesso"] == "admin":
                cadastrar_usuario()
            elif usuario:
                print("Acesso negado! Apenas administradores podem cadastrar usuários.")
            else:
                print("Autenticação necessária!")

        elif opcao in ["2", "3"]:
            usuario = autenticar_usuario()
            if usuario:
                matricula = input("Informe a Matrícula: ").strip()
                passagem_policia = input("Já teve passagem pela polícia? (Sim/Não): ").capitalize()
                pcd = input("É PCD? (Sim/Não): ").capitalize()
                tipo = "Entrada" if opcao == "2" else "Saída"
                registrar_movimentacao(usuario, matricula, passagem_policia, pcd, tipo)

        elif opcao == "4":
            usuario = autenticar_usuario()
            if usuario:
                listar_registros()

        elif opcao == "5":
            usuario = autenticar_usuario()
            if usuario:
                buscar_registro_por_cpf()

        elif opcao == "6":
            print("Encerrando o sistema...")
            break

        else:
            print("Opção inválida! Tente novamente.")


if __name__ == "__main__":
    menu()
