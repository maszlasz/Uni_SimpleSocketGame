from socket import *
from threading import *
import os

s = socket(AF_INET, SOCK_STREAM)

try:
    # s.connect((gethostbyname(gethostname()), 6666))
    s.connect(("192.168.0.191", 6666))
except error:
    exit(1)


def from_server():
    while True:
        try:
            data = s.recv(1024).decode()
            print(data)

            if data == "EXIT":
                s.close()
                exit(0)
        except error:
            pass


Thread(target=from_server).start()

while True:
    try:
        s.send(str(input()).encode())
    except OSError:
        os._exit(1)
