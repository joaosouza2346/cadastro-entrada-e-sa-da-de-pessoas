from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QTableWidget, \
    QTableWidgetItem, QFormLayout, QDialog, QDialogButtonBox, QInputDialog
from PyQt5.QtCore import Qt
from datetime import datetime
import hashlib
import re
import sqlite3

class SistemaPortariaApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema de Controle de Portaria - MPRJ CSI")
        self.setGeometry(300, 300, 600, 400)

        # Conectar ao banco de dados SQLite
        self.conn = sqlite3.connect("portaria_mprj_csi.db")
        self.criar_tabelas()

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Exibir as opções
        self.menu()

    def criar_tabelas(self):
        # Criar tabelas se não existirem
        cursor = self.conn.cursor()
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                senha TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                cargo TEXT NOT NULL,
                empresa TEXT NOT NULL,
                nivel_acesso TEXT NOT NULL
            )
        ''')
        # Tabela de registros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL,
                nome TEXT NOT NULL,
                matricula TEXT NOT NULL,
                empresa TEXT NOT NULL,
                passagem_policia TEXT NOT NULL,
                pcd TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                tipo TEXT NOT NULL,
                registrado_por TEXT NOT NULL,
                FOREIGN KEY (cpf) REFERENCES usuarios(cpf)
            )
        ''')
        self.conn.commit()

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
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def validar_cpf(self, cpf):
        cpf = re.sub(r'\D', '', cpf)
        return len(cpf) == 11 and cpf.isdigit()

    def cadastrar_usuario(self):
        self.clear_layout()

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
        cpf = self.cpf_input.text().strip()
        nome = self.nome_input.text().strip()
        cargo = self.cargo_input.text().strip()
        nivel_acesso = self.nivel_acesso_input.currentText()
        senha = self.senha_input.text().strip()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        if not self.validar_cpf(cpf):
            self.exibir_mensagem("CPF inválido! Deve conter 11 dígitos numéricos.")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios (usuario, senha, cpf, nome, cargo, empresa, nivel_acesso)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (usuario, senha_hash, cpf, nome, cargo, "MPRJ", nivel_acesso))
            self.conn.commit()
            self.exibir_mensagem(f"Usuário {usuario} cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            self.exibir_mensagem("Usuário ou CPF já existe!")

    def exibir_mensagem(self, mensagem):
        dialog = QDialog(self)
        dialog.setWindowTitle("Mensagem")
        dialog.setModal(True)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(mensagem))
        dialog.setLayout(layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        dialog.exec_()

    def autenticar_usuario(self):
        usuario, ok = QInputDialog.getText(self, "Autenticação", "Usuário:")
        if not ok:
            return None

        senha, ok = QInputDialog.getText(self, "Autenticação", "Senha:", QLineEdit.Password)
        if not ok:
            return None

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        if resultado and resultado[0] == senha_hash:
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
            self.registrar_movimentacao(usuario, matricula, passagem_policia, pcd, "Entrada")

    def registrar_saida(self):
        usuario = self.autenticar_usuario()
        if usuario:
            matricula, _ = QInputDialog.getText(self, "Registro de Saída", "Informe a Matrícula:")
            passagem_policia, _ = QInputDialog.getItem(self, "Registro de Saída", "Já teve passagem pela polícia?",
                                                       ["Sim", "Não"], 0, False)
            pcd, _ = QInputDialog.getItem(self, "Registro de Saída", "É PCD?", ["Sim", "Não"], 0, False)
            self.registrar_movimentacao(usuario, matricula, passagem_policia, pcd, "Saída")

    def registrar_movimentacao(self, usuario, matricula, passagem_policia, pcd, tipo):
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute("SELECT cpf, nome FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        if resultado:
            cpf, nome = resultado
            cursor.execute('''
                INSERT INTO registros (cpf, nome, matricula, empresa, passagem_policia, pcd, data_hora, tipo, registrado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cpf, nome, matricula, "MPRJ", passagem_policia, pcd, data_hora, tipo, usuario))
            self.conn.commit()
            self.exibir_mensagem(f"{tipo} registrada com sucesso para {nome} às {data_hora}.")

    def listar_registros(self):
        self.clear_layout()
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome, cpf, matricula, passagem_policia, pcd, data_hora, tipo FROM registros")
        registros = cursor.fetchall()

        if not registros:
            self.exibir_mensagem("Nenhum registro encontrado.")
            return

        table = QTableWidget(len(registros), 7)
        table.setHorizontalHeaderLabels(["Nome", "CPF", "Matrícula", "Passagem Polícia", "PCD", "Data/Hora", "Tipo"])
        self.layout.addWidget(table)

        for row, reg in enumerate(registros):
            for col, value in enumerate(reg):
                table.setItem(row, col, QTableWidgetItem(value))

        voltar_button = QPushButton("Voltar")
        voltar_button.clicked.connect(self.menu)
        self.layout.addWidget(voltar_button)

    def buscar_registro_por_cpf(self):
        cpf, _ = QInputDialog.getText(self, "Buscar Registro por CPF", "Informe o CPF:")
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome, matricula, tipo, data_hora FROM registros WHERE cpf = ?", (cpf,))
        encontrados = cursor.fetchall()

        if not encontrados:
            self.exibir_mensagem("Nenhum registro encontrado para este CPF.")
        else:
            self.clear_layout()
            table = QTableWidget(len(encontrados), 4)
            table.setHorizontalHeaderLabels(["Nome", "Matrícula", "Tipo", "Data/Hora"])
            self.layout.addWidget(table)

            for row, reg in enumerate(encontrados):
                for col, value in enumerate(reg):
                    table.setItem(row, col, QTableWidgetItem(value))

            voltar_button = QPushButton("Voltar")
            voltar_button.clicked.connect(self.menu)
            self.layout.addWidget(voltar_button)

    def closeEvent(self, event):
        # Fecha a conexão com o banco de dados ao sair
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = SistemaPortariaApp()
    window.show()
    app.exec_()

