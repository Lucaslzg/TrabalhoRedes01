import socket
import threading

def handle_client(client_socket, addr):
    print(f"Client connected from {addr}")

    while True:
        data = client_socket.recv(1024)
        if not data or data.decode('utf-8') == 'END':
            break

        print(f"Received from {addr}: {data.decode('utf-8')}")
        try:
            client_socket.send(b'Hey client')
        except:
            print(f"Connection with {addr} closed by the client")
            break

    client_socket.close()
    print(f"Connection with {addr} closed")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(5)
    print("Server is running and waiting for connections...")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()



