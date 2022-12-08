import socket
import re

BUFFER = 10


class ClientManager:
    def __init__(self, c_socket, c_addr):
        self.__c_socket = c_socket
        self.__c_addr = c_addr
        self.name = self.__receive()
        self.is_admin = False

    def receive_data(self):
        data = self.__receive()
        data = self.__filter_incoming_data(data)
        return data

    def send_data(self, message):
        if len(message)%BUFFER == 0:
            message += "\x00"
        self.__c_socket.send(message.encode())

    def disconnect(self):
        self.__c_socket.close()

    def __receive(self):
        data = ""
        while True:
            tmp = self.__c_socket.recv(BUFFER).decode()
            data += tmp
            if len(tmp) < BUFFER:
                break
        return data.strip("\x00")

    def __filter_incoming_data(self, data):
        regex = re.compile(r"(\<\[.*?\]\>)")
        groups = regex.findall(data)

        replacer = lambda x : x[2:-2].replace("\\\\", "\\").replace("\\<", "<").replace("\\>", ">").replace("\\[", "[").replace("\\]", "]")
        return_data = list()

        if groups[0] == "<[MESSAGE]>":
            message = replacer(groups[1])
            return_data = [groups[0], message]
        elif groups[0] == "<[FILE]>":
            file_content = replacer(groups[1])
            return_data = [groups[0], file_content]
        elif groups[0] == "<[PRIVATE]>":
            client_name = replacer(groups[1])
            msg_or_file_content = replacer(groups[3])
            return_data = [groups[0], client_name, groups[2], msg_or_file_content]
        elif groups[0] == "<[DISCONNECT]>":
            return_data = groups

        return return_data

    def __parse_outgoing_data(self):
        pass
