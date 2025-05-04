import socket
import threading
from response import Response

class TestClient:
    def __init__(self, host="localhost", port=12345):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()

    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))
        print(f"[CLIENT] Connected to {self.server_host}:{self.server_port}")

    def start(self):
        while True:
            message = input("[CLIENT] Enter CPF or Name (or type END to quit): ").strip()
            if not message:
                continue
            if message.upper() == "END":
                self.client_socket.sendall(b"END\n")
                print("[CLIENT] Disconnected from server.")
                break

            try:
                with self.lock:
                    self.client_socket.sendall((message + "\n").encode("utf-8"))
                threading.Thread(target=self.receive_response).start()
            except Exception as e:
                print(f"[CLIENT] Error sending data: {e}")
                break

        self.client_socket.close()

    def receive_response(self):
        try:
            buffer = ""
            while True:

                data = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    break
                buffer += data
                if '\n' in buffer:
                    break
            print(f"\n[CLIENT] Response: {buffer.strip()}")
        except Exception as e:
            print(f"[CLIENT] Error receiving data: {e}")

if __name__ == '__main__':
    client = TestClient()
    client.connect()
    client.start()
