import socket
import threading


class Client:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def sendrequest(self, payload):
        self.client_socket.send(payload.encode('utf-8'))

    def receiverequest(self):
        while True:
            data = self.client_socket.recv(1024)
            print(str(data))
            more = input('Want to send more data to the server? (y/n) ')
            if more.lower() == 'y':
                payload = input('Enter Payload: ')
                send_thread = threading.Thread(target=self.sendrequest, args=(payload,))
                send_thread.start()
            else:
                break


if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    client = Client(client_socket)
    initial_payload = 'Hey Server'
    thread = threading.Thread(target=client.sendrequest, args=(initial_payload,))
    thread.start()
    client.receiverequest()

    client_socket.close()


# import socket
# import multiprocessing
# import threading
#
#
# class Client:
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def sendrequest(client_socket, payload):
#         client_socket.send(payload.encode('utf-8'))
#
#     @staticmethod
#     def receiverequest(client_socket):
#         while True:
#             data = client_socket.recv(1024)
#             print(str(data))
#             more = input('Want to send more data to the server? (y/n) ')
#             if more.lower() == 'y':
#                 payload = input('Enter Payload: ')
#                 send_thread = threading.Thread(target=Client.sendrequest, args=(client_socket, payload))
#                 send_thread.start()
#             else:
#                 break
#
#
# if __name__ == '__main__':
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect(('127.0.0.1', 12345))
#     payload = 'Hey Server'
#     thread = threading.Thread(target=Client.sendrequest, args=(client_socket, payload), )
#     thread.start()
#     Client.receiverequest(client_socket)
#
#     client_socket.close()
#
#
