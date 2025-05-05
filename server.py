import sys
import os
import socket
import sqlite3
import threading
import json
from multiprocessing import Process, freeze_support
from PyQt5 import QtCore, QtWidgets

# Caminho fixo para o banco de dados
DB_PATH = r"C:\Users\LucasZGallert\Documents\Cod\Gersu\basecpf.db"

# Dependências externas esperadas
from response import Response
from user import User


class Server:
    def __init__(self, server_socket):
        self.server_socket = server_socket

    def database_access(self, data_received):
        print("[THREAD] Database Access PID:", os.getpid())
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()

        if data_received[0].isdigit():
            cursor.execute("SELECT * FROM cpf WHERE cpf = ?", (data_received,))
        else:
            cursor.execute("SELECT * FROM cpf WHERE nome = ?", (data_received,))

        rows = cursor.fetchall()
        conn.close()

        users = [User(*row) for row in rows]

        response_json = Response(users).toJson()
        print("[THREAD] JSON →", response_json)
        return response_json

    def handle_request(self, client_socket, message):
        json_payload = self.database_access(message)
        try:
            client_socket.sendall((json_payload + "\n").encode("utf-8"))
        except Exception as e:
            print("[SERVER] Error sending response:", e)

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
            except Exception as e:
                print("[MAIN] Error accepting connection:", e)
                break


class Ui_Janela(object):
    def setupUi(self, Janela):
        Janela.setObjectName("Janela")
        Janela.resize(331, 212)
        self.centralwidget = QtWidgets.QWidget(Janela)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 0, 291, 91))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(2)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setText("IP do Servidor:")
        self.verticalLayout_2.addWidget(self.label_2)
        self.lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.verticalLayout_2.addWidget(self.lineEdit)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.verticalLayout_2.addWidget(self.label)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setText("Porta:")
        self.verticalLayout_2.addWidget(self.label_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.verticalLayout_2.addWidget(self.lineEdit_2)

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(40, 90, 251, 41))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushButton.setText("Iniciar/Parar Servidor")
        self.verticalLayout_3.addWidget(self.pushButton)

        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(110, 130, 111, 41))
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
        if self.server_thread:
            self.label_4.setText("Parado")
            print("[GUI] Servidor encerrado.")
            # Not safe to close socket here forcibly if thread is still using it
            return
        try:
            host = self.lineEdit.text() or "0.0.0.0"
            port = int(self.lineEdit_2.text() or 12345)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen(1000)
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            self.label_4.setText("Rodando")
            print(f"[GUI] Servidor iniciado em {host}:{port}")
        except Exception as e:
            print(f"[GUI] Erro ao iniciar servidor: {e}")
            self.label_4.setText("Erro")

    def run_server(self):
        freeze_support()
        server = Server(self.server_socket)
        server.connection()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Janela = QtWidgets.QMainWindow()
    ui = Ui_Janela()
    ui.setupUi(Janela)
    Janela.show()
    sys.exit(app.exec_())
