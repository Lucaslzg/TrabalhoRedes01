import sys
import os
import socket
import sqlite3
import threading
import json
from multiprocessing import Process, freeze_support
from PyQt5 import QtCore, QtWidgets

# Caminho padrão
DB_PATH = r"C:/Redes/basecpf.db"

from response import Response
from user import User


class Server:
    def __init__(self, server_socket, db_path):
        self.server_socket = server_socket
        self.db_path = db_path
        self.conn = None  # Armazena a conexão com o banco de dados

    def database_access(self, data_received):
        print("[THREAD] Database Access PID:", os.getpid())
        conn = sqlite3.connect(self.db_path, check_same_thread=False)  # Usa self.db_path
        cursor = conn.cursor()

        if data_received[0].isdigit():
            cursor.execute("SELECT * FROM cpf WHERE cpf = ?", (data_received,))
        else:
            cursor.execute("SELECT * FROM cpf WHERE nome LIKE ? LIMIT 1000", ('%' + data_received.upper() + '%',))

        rows = cursor.fetchall()
        conn.close()

        users = [User(*row) for row in rows]
        response_json = Response(users).toJson()
        print("[THREAD] JSON →", response_json)
        return response_json

    def handle_request(self, client_socket, message):
        try:
            # Converte a mensagem recebida de JSON para dicionário
            message_dict = json.loads(message.strip())  # Converte o JSON em um dicionário
            query = message_dict.get("query", "").strip()  # Obtém o valor da chave "query"

            if query:
                # Chama o metodo de acesso ao banco para buscar o CPF ou Nome
                json_payload = self.database_access(query)
                client_socket.sendall((json_payload + "\n").encode("utf-8"))
            else:
                client_socket.sendall(b"Erro: Nenhuma consulta fornecida.\n")
        except Exception as e:
            print(f"[SERVER] Erro ao processar a requisição: {e}")
            client_socket.sendall(b"Erro ao processar a requisicao.\n")

    def handle_client(self, client_socket, addr):
        print(f"[PROCESS] Handling client from {addr} (PID: {os.getpid()})")
        buffer = ""

        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data

                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.strip().upper() == "END":
                        print(f"[PROCESS] Client {addr} disconnected.")
                        client_socket.close()
                        return
                    p = Process(target=self.handle_request, args=(client_socket, message.strip()))
                    p.start()
            except Exception as e:
                print(f"[PROCESS] Error with {addr}: {e}")
                break
        client_socket.close()

    def connection(self):
        print("[MAIN] Server is running and waiting for connections...")
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
            except OSError as e:
                print("[MAIN] Socket encerrado. Encerrando conexão.")
                break
            except Exception as e:
                print("[MAIN] Error accepting connection:", e)
                break

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("[SERVER] Conexão com o banco de dados fechada.")


class Ui_Janela(object):
    def setupUi(self, Janela):
        Janela.setObjectName("Janela")
        Janela.resize(331, 260)  # Aumentado para acomodar novo campo
        self.centralwidget = QtWidgets.QWidget(Janela)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 0, 291, 131))  # Ajustado
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(2)

        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setText("IP do Servidor:")
        self.verticalLayout_2.addWidget(self.label_2)
        self.lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.verticalLayout_2.addWidget(self.lineEdit)

        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setText("Porta:")
        self.verticalLayout_2.addWidget(self.label_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.verticalLayout_2.addWidget(self.lineEdit_2)

        # NOVO: Campo para o caminho do banco de dados
        self.label_db = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_db.setText("Caminho do Banco de Dados:")
        self.verticalLayout_2.addWidget(self.label_db)
        self.lineEdit_db_path = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_db_path.setText(DB_PATH)  # seta o caminho do banco de dados padrão
        self.verticalLayout_2.addWidget(self.lineEdit_db_path)

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(40, 135, 251, 41))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushButton.setText("Iniciar/Parar Servidor")
        self.verticalLayout_3.addWidget(self.pushButton)

        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(110, 180, 111, 41))
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setText("Parado")
        self.verticalLayout_4.addWidget(self.label_4)

        Janela.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Janela)
        Janela.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Janela)
        Janela.setStatusBar(self.statusbar)

        self.pushButton.clicked.connect(self.toggle_server)
        self.server_socket = None
        self.server_thread = None

    def toggle_server(self):
        global DB_PATH

        # Se o servidor estiver rodando, encerra
        if self.server_thread and self.server_thread.is_alive():
            self.label_4.setText("Parado")
            print("[GUI] Servidor encerrado.")
            try:
                # Fechar o socket e a conexão com o banco de dados
                if self.server_socket:
                    self.server_socket.close()
                if self.server:
                    self.server.close_connection()  # Se você tiver uma função para fechar a conexão do banco de dados
            except Exception as e:
                print(f"[GUI] Erro ao fechar o socket ou a conexão: {e}")
            self.server_socket = None
            self.server_thread = None
            return

        try:
            db_path_input = self.lineEdit_db_path.text()
            if db_path_input:
                DB_PATH = db_path_input  # Atualiza o DB_PATH com o valor do campo de texto

            host = self.lineEdit.text() or "0.0.0.0"
            port = int(self.lineEdit_2.text() or 12345)

            # Recriar o socket e reconfigurar a porta
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(1000)

            self.server_thread = threading.Thread(target=self.run_server, args=(DB_PATH,), daemon=True)
            self.server_thread.start()

            self.label_4.setText("Rodando")
            print(f"[GUI] Servidor iniciado em {host}:{port}")
            print(f"[GUI] Usando banco de dados em: {DB_PATH}")
        except Exception as e:
            print(f"[GUI] Erro ao iniciar servidor: {e}")
            self.label_4.setText("Erro")

    def run_server(self, db_path):
        freeze_support()
        self.server = Server(self.server_socket, db_path)  # Passando db_path como parâmetro para o servidor
        self.server.connection()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Janela = QtWidgets.QMainWindow()
    ui = Ui_Janela()
    ui.setupUi(Janela)
    Janela.show()
    sys.exit(app.exec_())
