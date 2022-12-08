import socket
from threading import Thread

BUFFER = 10


class Client:
    def __init__(self, name, ip, port):
        self.__name = name
        self.__ip = ip
        self.__port = port

        self.__running = False
        self.__s_socket = None
        self.__participants = list()

    def start_client(self):
        self.__s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s_socket.connect((self.__ip, self.__port))
        self.__s_socket.send(self.__name.encode())
        self.__running = True

        send_thread = Thread(target=self.__send_data)
        send_thread.start()
        receive_thread = Thread(target=self.__receive_data)
        receive_thread.start()

    def disconnect(self):
        self.__running = False
        self.__s_socket.send("<[DISCONNECT]>".encode())
        print("Disconnecting...")
        self.__s_socket.close()

    def __send_data(self):
        try:
            while self.__running:
                message = self.__parse_outgoing_data()
                if not message:
                    continue
                if len(message)%BUFFER == 0:
                    message += "\x00"
                self.__s_socket.send(message.encode())
        except Exception as e:
            print(e)
            self.disconnect()
    
    def __parse_outgoing_data(self):
        replacer = lambda x : x.replace("\\", "\\\\").replace("<", "\\<").replace(">", "\\>").replace("[", "\\[").replace("]", "\\]")
        user_input = input()
        data = None
        if user_input[:4] == "/msg":
            data = "<[MESSAGE]> <[" + replacer(user_input[5:]) + "]>"
        elif user_input[:8] == "/privmsg":
            if username_msg_idx := self.__get_private_username_and_msg_idx(user_input[9:]):
                username, msg_idx = username_msg_idx
                msg_idx += 9
                data = "<[PRIVATE]> <[" + replacer(username) + "]> <[MESSAGE]> <[" + replacer(user_input[msg_idx:]) + "]>"
        else:
            pass

        if data:
            return data
        else:
            return

    def __get_private_username_and_msg_idx(self, string):
        if string[0] == "\"":
            idx = 1;
            while True:
                if string[idx] == "\"":
                    break
                if idx >= len(string)-2:
                    print("[-] No username or message specified.")
                    return None
                idx += 1
            username = string[1:idx]
            #if username in self.__participants:
            #    msg_idx = idx + 2
            #    return username, msg_idx
            msg_idx = idx + 2
            return username, msg_idx
            print("[-] Not a valid username")
        print("[-] No username specified.")
        return None


    def __receive_data(self):
        try:
            while self.__running:
                data = self.__receive()
                #data = self.__filter_incoming_data(data)
                print(data)
        except:
            self.disconnect()

    def __receive(self):
        data = ""
        while True:
            tmp = self.__s_socket.recv(BUFFER).decode()
            data += tmp
            if len(tmp) < BUFFER:
                break
        return data.strip("\x00")

    def __filter_incoming_data(self, data):
        pass


if __name__ == "__main__":
    login_name = input("[+] Enter Login Name : ")
    c = Client(login_name, "127.0.0.1", 4444)
    c.start_client()

