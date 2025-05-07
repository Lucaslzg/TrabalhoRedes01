import sys
import socket
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import json

class TestClient(QtCore.QObject):
    received = QtCore.pyqtSignal(str)
    connected = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.lock = threading.Lock()
        self.running = False

    def connect_to_server(self, host, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, int(port)))
            self.running = True
            self.connected.emit(True)
            return True
        except Exception as e:
            self.connected.emit(False)
            return False

    def disconnect(self):
        self.running = False
        try:
            self.client_socket.sendall(b"END\n")
            self.client_socket.close()
        except Exception:
            pass
        self.connected.emit(False)

    def send_message(self, message):
        if not self.running or not message.strip():
            return
        try:
            # Empacotar a consulta (CPF ou Nome) em um JSON
            message_dict = {"query": message.strip()}  # A chave "query" contém o valor enviado
            message_json = json.dumps(message_dict)  # Converte o dicionário para JSON

            with self.lock:
                # Envia o JSON no formato UTF-8
                self.client_socket.sendall((message_json + "\n").encode("utf-8"))

            threading.Thread(target=self.receive_response, daemon=True).start()
        except Exception as e:
            self.received.emit(f"Erro ao enviar: {e}")
            self.running = False
            self.connected.emit(False)

    def receive_response(self):
        try:
            buffer = ""
            while self.running:
                data = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    break
                buffer += data
                if '\n' in buffer:
                    break
            self.received.emit(buffer.strip())
        except Exception as e:
            self.received.emit(f"Erro ao receber: {e}")
            self.running = False
            self.connected.emit(False)


class Ui_Janela(object):
    def setupUi(self, Janela):
        Janela.setObjectName("Janela")
        Janela.resize(732, 361)
        self.centralwidget = QtWidgets.QWidget(Janela)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 711, 321))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setText("")
        self.verticalLayout_2.addWidget(self.lineEdit)
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setText("")
        self.verticalLayout_2.addWidget(self.lineEdit_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.label_4 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.label_5 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout_2.addWidget(self.lineEdit_3)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.text_resultado = QtWidgets.QTextEdit(self.horizontalLayoutWidget_2)
        self.text_resultado.setReadOnly(True)
        self.text_resultado.setObjectName("text_resultado")
        self.horizontalLayout_2.addWidget(self.text_resultado)
        Janela.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Janela)
        self.statusbar.setObjectName("statusbar")
        Janela.setStatusBar(self.statusbar)

        self.retranslateUi(Janela)
        QtCore.QMetaObject.connectSlotsByName(Janela)

        # Logic integration
        self.client = TestClient()
        self.client.received.connect(self.display_response)
        self.client.connected.connect(self.set_connection_status)

        self.pushButton_2.clicked.connect(self.connect_client)
        self.pushButton.clicked.connect(self.send_query)

    def connect_client(self):
        ip = self.lineEdit.text()
        port = self.lineEdit_2.text()
        self.client.connect_to_server(ip, port)

    def send_query(self):
        text = self.lineEdit_3.text().strip()
        if text:
            self.text_resultado.append(f"[CLIENT] Enviando: {text}")
            self.client.send_message(text)

    def display_response(self, message):
        self.text_resultado.append(f"[SERVER] {message}")

    def set_connection_status(self, status):
        if status:
            self.label_4.setText("Conectado")
        else:
            self.label_4.setText("Desconectado")


    def retranslateUi(self, Janela):
        _translate = QtCore.QCoreApplication.translate
        Janela.setWindowTitle(_translate("Janela", "Client"))
        self.label_2.setText(_translate("Janela", "IP do Servidor:"))
        self.label_3.setText(_translate("Janela", "Porta:"))
        self.pushButton_2.setText(_translate("Janela", "Connectar"))
        self.label_4.setText(_translate("Janela", "Desconectado"))
        self.label_5.setText(_translate("Janela", "CPF ou Nome a ser Consultado:"))
        self.pushButton.setText(_translate("Janela", "Consultar"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Janela = QtWidgets.QMainWindow()
    ui = Ui_Janela()
    ui.setupUi(Janela)
    Janela.show()
    sys.exit(app.exec_())