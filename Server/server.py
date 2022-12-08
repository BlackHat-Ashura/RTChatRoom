from threading import Thread

from server_manager import ServerManager


try:
    s = ServerManager("Admin", "0.0.0.0", 4444)
    s.start_server()
    t = Thread(target=s.server_accept)
    t.start()
    input()
except KeyboardInterrupt:
    print("[-] Stopping Server...")
    s.stop_server()
