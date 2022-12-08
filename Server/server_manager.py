import socket
from threading import Thread, Lock
import time

from client_manager import ClientManager


class ServerManager:
    def __init__(self, real_admin, ip, port):
        self.__real_admin = real_admin
        self.__current_admin = None

        self.__clients = list()
        self.__clients_lock = Lock()

        self.__ip = ip
        self.__port = port
        self.__s_socket = None

    def start_server(self):
        self.__s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s_socket.bind((self.__ip, self.__port))
        self.__s_socket.listen()

    def server_accept(self):
        try:
            while True:
                c, addr = self.__s_socket.accept()
                client = ClientManager(c, addr)
                with self.__clients_lock:
                    self.__clients.append(client)
                    time.sleep(1)
                self.__update_clients_with_clients_list()
                self.__update_admin(client)
                t = Thread(target=self.__client_handler, args=(client,))
                t.start()
        except Exception:
            pass
    
    def stop_server(self):
        self.__disconnect_clients()
        self.__s_socket.close()

    def __update_clients_with_clients_list(self):
        with self.__clients_lock:
            message = "<[UPDATE CLIENTS]> <[" + "]> <[".join([client.name for client in self.__clients]) + "]>"
            time.sleep(1)
        self.__transfer_message(message)

    def __update_admin(self, client=None):
        if not client:
            # To handle when Current Admin leaves the chat
            with self.__clients_lock:
                if len(self.__clients) == 0:
                    self.__current_admin = None
                    return
                client = self.__clients[0]
                self.__current_admin = client.name
                client.is_admin = True
                time.sleep(1)
        
        if not self.__current_admin:
            # To handle First Admin
            self.__current_admin = client.name
            client.is_admin = True

        if self.__current_admin != self.__real_admin and client.name == self.__real_admin:
            # To handle when Real Admin joins
            current_admin_client = self.__get_client_manager(self.__current_admin)
            current_admin_client.is_admin = False
            self.__current_admin = client.name
            client.is_admin = True

        message = f"<[UPDATE ADMIN]> <[{self.__current_admin}]>"
        self.__transfer_message(message)

    def __client_handler(self, client):
        try:
            while True:
                message_list = client.receive_data()
                self.__process_message(client, message_list)
        except:
            self.__disconnect_clients(client)

    def __process_message(self, client, message_list):
        if message_list[0] == "<[MESSAGE]>":
            self.__transfer_message(message_list[1], client)
        if message_list[0] == "<[PRIVATE]>":
            client2_name = message_list[1]
            if message_list[2] == "<[MESSAGE]>":
                self.__transfer_message(message_list[3], client, client2_name)
            elif message_list[2] == "<[FILE]>":
                pass
        elif message_list[0] == "<[DISCONNECT]>":
            raise

    def __transfer_message(self, message, client1=None, client2_name=None):
        if client2_name:
            client2 = self.__get_client_manager(client2_name)
            message = f"<[PRIVATE]> <[MESSAGE]> <[{client1.name}]> <[{message}]>"
            client1.send_data(message)
            client2.send_data(message)
        else:
            if client1:
                message = f"<[MESSAGE]> <[{client1.name}]> <[{message}]>"
            with self.__clients_lock:
                for client in self.__clients:
                    client.send_data(message)
                time.sleep(1)

    def __get_client_manager(self, name):
        with self.__clients_lock:
            for client in self.__clients:
                if client.name == name:
                    return client

    def __send_filename(self, client, client_name=None):
        pass

    def __send_file(self, client, client_name=None):
        pass

    def __disconnect_clients(self, client=None):
        try:
            if client:
                client.disconnect()
                name = client.name
                with self.__clients_lock:
                    self.__clients.remove(client)
                    time.sleep(1)
                self.__transfer_message(f"<[LEFT]> <[{name}]>")
                self.__update_clients_with_clients_list()
                if name == self.__current_admin:
                    self.__update_admin()
            else:
                with self.__clients_lock:
                    for client in self.__clients:
                        client.disconnect()
                        self.__clients.remove(client)
                    time.sleep(1)
        except:
            pass

