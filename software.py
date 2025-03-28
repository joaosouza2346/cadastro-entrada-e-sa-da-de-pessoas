
     from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QTableWidget, \
    QTableWidgetItem, QFormLayout, QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt
from datetime import datetime
import hashlib
import getpass
import re
import json
import os


class SistemaPortariaApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema de Controle de Portaria - MPRJ CSI")
        self.setGeometry(300, 300, 600, 400)

        # Carregar registros salvos ao iniciar
        self.registros = []
        self.usuarios = {}
        self.ARQUIVO_REGISTROS = "registros_mprj_csi.json"
        if os.path.exists(self.ARQUIVO_REGISTROS):
            with open(self.ARQUIVO_REGISTROS, "r") as f:
                self.registros = json.load(f)

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Exibir as opções
        self.menu()

    def menu(self):
        self.clear_layout()

        # Caixa de Botões
        self.layout.addWidget(QPushButton("Cadastrar Usuário", clicked=self.cadastrar_usuario))
        self.layout.addWidget(QPushButton("Registrar Entrada", clicked=self.registrar_entrada))
        self.layout.addWidget(QPushButton("Registrar Saída", clicked=self.registrar_saida))
        self.layout.addWidget(QPushButton("Listar Todos os Registros", clicked=self.listar_registros))
        self.layout.addWidget(QPushButton("Buscar Registro por CPF", clicked=self.buscar_registro_por_cpf))
        self.layout.addWidget(QPushButton("Sair", clicked=self.close))

    def clear_layout(self):
        # Limpar todos os widgets da tela
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def validar_cpf(self, cpf):
        cpf = re.sub(r'\D', '', cpf)
        return len(cpf) == 11 and cpf.isdigit()

    def cadastrar_usuario(self):
        self.clear_layout()

        # Caixa para cadastrar o usuário
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.usuario_input = QLineEdit()
        self.form_layout.addRow("Nome de Usuário:", self.usuario_input)

        self.cpf_input = QLineEdit()
        self.form_layout.addRow("CPF (somente números):", self.cpf_input)

        self.nome_input = QLineEdit()
        self.form_layout.addRow("Nome Completo:", self.nome_input)

        self.cargo_input = QLineEdit()
        self.form_layout.addRow("Cargo:", self.cargo_input)

        self.nivel_acesso_input = QComboBox()
        self.nivel_acesso_input.addItems(["admin", "usuario"])
        self.form_layout.addRow("Nível de Acesso:", self.nivel_acesso_input)

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("Senha:", self.senha_input)

        self.salvar_button = QPushButton("Cadastrar")
        self.salvar_button.clicked.connect(self.salvar_usuario)
        self.layout.addWidget(self.salvar_button)

        self.voltar_button = QPushButton("Voltar")
        self.voltar_button.clicked.connect(self.menu)
        self.layout.addWidget(self.voltar_button)

    def salvar_usuario(self):
        usuario = self.usuario_input.text().strip()
        if usuario in self.usuarios:
            self.exibir_mensagem("Usuário já existe!")
            return

        cpf = self.cpf_input.text().strip()
        if not self.validar_cpf(cpf):
            self.exibir_mensagem("CPF inválido! Deve conter 11 dígitos numéricos.")
            return

        nome = self.nome_input.text().strip()
        cargo = self.cargo_input.text().strip()
        nivel_acesso = self.nivel_acesso_input.currentText()
        senha = self.senha_input.text().strip()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        self.usuarios[usuario] = {
            "senha": senha_hash,
            "cpf": cpf,
            "nome": nome,
            "cargo": cargo,
            "empresa": "MPRJ",
            "nivel_acesso": nivel_acesso
        }
        self.exibir_mensagem(f"Usuário {usuario} cadastrado com sucesso!")

    def exibir_mensagem(self, mensagem):
        # Caixa de mensagem de erro
        dialog = QDialog(self)
        dialog.setWindowTitle("Mensagem")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(mensagem))
        dialog.setLayout(layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(button_box)
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def autenticar_usuario(self):
        usuario, ok = QInputDialog.getText(self, "Autenticação", "Usuário:")
        if not ok:
            return None

        senha, ok = QInputDialog.getText(self, "Autenticação", "Senha:", QLineEdit.Password)
        if not ok:
            return None

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        if usuario in self.usuarios and self.usuarios[usuario]["senha"] == senha_hash:
            return usuario
        else:
            self.exibir_mensagem("Usuário ou senha incorretos!")
            return None

    def registrar_entrada(self):
        usuario = self.autenticar_usuario()
        if usuario:
            matricula, _ = QInputDialog.getText(self, "Registro de Entrada", "Informe a Matrícula:")
            passagem_policia, _ = QInputDialog.getItem(self, "Registro de Entrada", "Já teve passagem pela polícia?",
                                                       ["Sim", "Não"], 0, False)
            pcd, _ = QInputDialog.getItem(self, "Registro de Entrada", "É PCD?", ["Sim", "Não"], 0, False)

            tipo = "Entrada"
            self.registrar_movimentacao(usuario, matricula, passagem_policia, pcd, tipo)

    def registrar_saida(self):
        usuario = self.autenticar_usuario()
        if usuario:
            matricula, _ = QInputDialog.getText(self, "Registro de Saída", "Informe a Matrícula:")
            passagem_policia, _ = QInputDialog.getItem(self, "Registro de Saída", "Já teve passagem pela polícia?",
                                                       ["Sim", "Não"], 0, False)
            pcd, _ = QInputDialog.getItem(self, "Registro de Saída", "É PCD?", ["Sim", "Não"], 0, False)

            tipo = "Saída"
            self.registrar_movimentacao(usuario, matricula, passagem_policia, pcd, tipo)

    def registrar_movimentacao(self, usuario, matricula, passagem_policia, pcd, tipo):
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registro = {
            "cpf": self.usuarios[usuario]["cpf"],
            "nome": self.usuarios[usuario]["nome"],
            "matricula": matricula,
            "empresa": "MPRJ",
            "passagem_policia": passagem_policia,
            "pcd": pcd,
            "data_hora": data_hora,
            "tipo": tipo,
            "registrado_por": usuario
        }
        self.registros.append(registro)
        with open(self.ARQUIVO_REGISTROS, "w") as f:
            json.dump(self.registros, f, indent=4)
        self.exibir_mensagem(f"{tipo} registrada com sucesso para {registro['nome']} às {data_hora}.")

    def listar_registros(self):
        self.clear_layout()

        if not self.registros:
            self.exibir_mensagem("Nenhum registro encontrado.")
            return

        table = QTableWidget(len(self.registros), 7)
        table.setHorizontalHeaderLabels(["Nome", "CPF", "Matrícula", "Passagem Polícia", "PCD", "Data/Hora", "Tipo"])
        self.layout.addWidget(table)

        for row, reg in enumerate(self.registros):
            table.setItem(row, 0, QTableWidgetItem(reg['nome']))
            table.setItem(row, 1, QTableWidgetItem(reg['cpf']))
            table.setItem(row, 2, QTableWidgetItem(reg['matricula']))
            table.setItem(row, 3, QTableWidgetItem(reg['passagem_policia']))
            table.setItem(row, 4, QTableWidgetItem(reg['pcd']))
            table.setItem(row, 5, QTableWidgetItem(reg['data_hora']))
            table.setItem(row, 6, QTableWidgetItem(reg['tipo']))

    def buscar_registro_por_cpf(self):
        cpf, _ = QInputDialog.getText(self, "Buscar Registro por CPF", "Informe o CPF:")
        encontrados = [reg for reg in self.registros if reg["cpf"] == cpf]
        if not encontrados:
            self.exibir_mensagem("Nenhum registro encontrado para este CPF.")
        else:
            self.clear_layout()
            table = QTableWidget(len(encontrados), 4)
            table.setHorizontalHeaderLabels(["Nome", "Matrícula", "Tipo", "Data/Hora"])
            self.layout.addWidget(table)

            for row, reg in enumerate(encontrados):
                table.setItem(row, 0, QTableWidgetItem(reg['nome']))
                table.setItem(row, 1, QTableWidgetItem(reg['matricula']))
                table.setItem(row, 2, QTableWidgetItem(reg['tipo']))
                table.setItem(row, 3, QTableWidgetItem(reg['data_hora']))


if __name__ == "__main__":
    app = QApplication([])
    window = SistemaPortariaApp()
    window.show()
    app.exec_()
