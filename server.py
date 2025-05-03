import os
import socket
import sqlite3
import threading
from multiprocessing import Process, freeze_support

DB_PATH = "C:/Redes/basecpf.db"


class Server:
    def __init__(self, server_socket):
        self.server_socket = server_socket

    def database_access(self, data_received):
        print("[THREAD] Database Access")
        print('PID ATUAL (Processo):', os.getpid())

        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        if data_received[0].isdigit():
            query = "SELECT * FROM cpf WHERE cpf = ?"
        else:
            query = "SELECT * FROM cpf WHERE nome = ?"
        cursor.execute(query, (data_received,))
        result = cursor.fetchall()
        conn.close()
        return result

    def handle_request(self, client_socket, message):
        result = self.database_access(message)
        try:
            response = str(result) + '\n'
            client_socket.sendall(response.encode('utf-8'))
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


if __name__ == "__main__":
    freeze_support()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(1000)
    server = Server(server_socket)
    server.connection()
