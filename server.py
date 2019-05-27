import socket
import sys
import threading
import queue
from time import sleep

host = socket.gethostname()  # #
port = 5555

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("SOCKET CREATED")
except socket.error as ex:
    print("COULD NOT CREATE SOCKET. ERROR: ", ex)
    sys.exit(0)


try:
    s.bind((host, port))
    print("SOCKET BOUND TO PORT: " + str(port))
except socket.error as ex:
    print("COULD NOT BIND SOCKET. ERROR: ", ex)
    sys.exit(0)

s.listen(7)


def client_thread(conn, lock, q):
    conn.setblocking(False)
    global clients_current

    while True:
        try:
            if conn.recv(1024).decode() == "START":
                conn.sendall("OK, WAITING FOR OTHERS".encode())

                # locking global value from other threads
                lock.acquire()
                clients_current += 1
                lock.release()

                break
            else:
                conn.sendall("NOT YET".encode())

        except socket.error:
            pass

    while q.empty():
        pass

    q.get()

    # GAME IN PROGRESS
    while True:
        conn.sendall("STARTING IN:".encode())

        for i in reversed(range(1, 6)):
            conn.sendall(str(i).encode())
            sleep(1)

        while q.empty():
            pass

        q.get()

        conn.sendall(("ROUND " + str(rounds_current) + " START").encode())

        # ROUND
        while q.empty():
            try:
                data = conn.recv(1024)
                print('RECEIVED: ' + data.decode() + ', FROM: ' + conn.getpeername()[0] + ':' +
                      str(conn.getpeername()[1]))
                reply = "->" + data.decode()
                conn.sendall(reply.encode())
            except socket.error:
                pass

        conn.sendall(("END OF ROUND " + str(rounds_current)).encode())

        # IF LAST ROUND -> DISCONNECT
        if str(q.get()) == "EXIT":
            break

        conn.sendall("WAITING FOR THE NEXT ROUND".encode())

        # BREAK
        while q.empty():
            try:
                print('RECEIVED: ' + conn.recv(1024).decode() + ', FROM: ' + conn.getpeername()[0] + ':' +
                      str(conn.getpeername()[1]))

                conn.sendall("WAIT FOR THE START OF THE NEXT ROUND".encode())
            except socket.error:
                pass

        q.get()

    conn.sendall("EXIT".encode())
    conn.close()


def connect_clients():
    is_first_client = True
    global clients_total
    global clients_left
    global threads
    global queues

    thread_lock = threading.Lock()

    while True:

        if clients_left:
            thread_conn, address = s.accept()
            print("CONNECTED TO " + address[0] + ":" + str(address[1]))

            if is_first_client:
                thread_conn.sendall("YOU'RE CONNECTED TO THE SERVER. ENTER THE NUMBER OF PLAYERS (2-8)".encode())
                while True:
                    try:
                        clients_total = int(thread_conn.recv(1024).decode())
                        clients_left = clients_total

                        if 2 <= clients_total <= 8:
                            thread_conn.sendall("OK, WAITING FOR OTHERS. TYPE 'START' WHEN YOU'RE READY".encode())
                            break

                        thread_conn.sendall("WRONG NUMBER OF PLAYERS".encode())

                    except ValueError:
                        thread_conn.sendall("THAT'S NOT A NUMBER".encode())

                is_first_client = False

            else:
                thread_conn.sendall("YOU'RE CONNECTED TO THE SERVER. TYPE 'START' WHEN YOU'RE READY".encode())

            thread_queue = queue.Queue()
            queues.append(thread_queue)
            thread = threading.Thread(target=client_thread, args=(thread_conn, thread_lock, thread_queue,))
            thread.start()
            threads.append(thread)

            clients_left -= 1
            print("WAITING FOR: " + str(clients_left) + " MORE CLIENTS")

        else:
            print("ALL CLIENTS CONNECTED")
            s.close()
            break


clients_total = 1
clients_current = 0
clients_left = 1

rounds_total = 3
rounds_current = 1

threads = []
queues = []
round_time = 5
break_time = 3

connect_clients()

# WAITING FOR CLIENTS TO CONFIRM START
while clients_total != clients_current:
    sleep(1)
    print("WAITING FOR: " + str(clients_total-clients_current) + " MORE CLIENTS")

print("\n\nALL CLIENTS READY. STARTING THE GAME")
for q in queues:
    q.put(".")

while True:
    print("\nCOUNTING DOWN")
    sleep(5)

    for q in reversed(queues):
        q.put(".")

    print("START ROUND " + str(rounds_current))
    sleep(round_time)
    print("END ROUND " + str(rounds_current))

    if rounds_current == rounds_total:
        print("TAK")
        for q in queues:
            q.put("EXIT")

        print("THE GAME HAS ENDED")
        break
    else:
        for q in queues:
            q.put(".")

    print("START BREAK")
    # TIME FOR PRICE CHANGE ETC.
    sleep(break_time)
    print("END BREAK")

    for q in queues:
        q.put(".")

    rounds_current += 1


# WAITING FOR THREADS TO END
for t in threads:
    t.join()

print("THE END")
exit(0)
