from socket import *
from threading import Thread

host = gethostname()  # #
#host = '10.129.5.203'
port = 5555

s = socket(AF_INET, SOCK_STREAM)

try:
    s.connect((host, port))
    s.setblocking(False)
except error:
    print("COULDN'T REACH THE SERVER")
    exit(1)


def from_server():
    while True:
        try:
            data = s.recv(1024).decode()
            print(": ", data)

            if data == "EXIT":
                s.close()
                exit(0)
        except error:
            pass


Thread(target=from_server).start()


while True:
    try:
         s.send(input().encode())
    except OSError:
        exit(0)
