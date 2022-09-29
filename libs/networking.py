import socket, select, json
_print = print

def print(*args):
    _print("[Network]",*args)

class Server:
    def __init__(self) -> None:
        self.host, self.port = "localhost", 5757
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.window = None
        print("Connected")
        self.queue = []

    def send(
        self,
        data
    ):
        self.queue.insert(0, data)

    def cycle(
        self
    ):
        while True:
            ready = select.select([self.sock], [], [], 0.1)

            if self.queue:
                try:
                    self.sock.sendall(str(self.queue[0]).encode("UTF-8"))
                except BrokenPipeError:
                    print("Oi, we fell off, stop trying!!!")
                print(f"sent {self.queue[0]}")
                del self.queue[0]
            if ready[0]:
                got = self.sock.recv(1024).decode("UTF-8")
                j: dict = None
                try:
                    j = json.loads(got)
                except:
                    # Failed to load :(((
                    if got:
                        print(got)
                        print("Connection fell off")
                if j is not None:
                    self.window.update(j)