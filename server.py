import socket
import sys
import threading
import queue
import math
import random
from time import sleep
from timeit import default_timer as timer
from Query import *
from Stock import *

host = socket.gethostbyname(socket.gethostname())
port = 6666
print(host)

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

s.listen(8)


def print_rules():
    return "RULES:\n" \
           "THERE ARE " + str(rounds_total) + " ROUNDS, EACH LASTS " + str(round_time) +\
           " SECONDS. BETWEEN EACH ROUND THERE IS A BREAK WHICH LASTS " + str(break_time*2) +\
           " SECONDS. THE PRICE OF EACH OF THE RESOURCES CHANGES BETWEEN THE ROUNDS BASED ON HOW MUCH OF IT\n" \
           "IS THERE AVAILABLE (COMPARED TO THE INITIAL AMOUNT), WHICH IS THEN MULTIPLIED BY A MARKET FLUCTUATION\n" \
           "(100% + RANDOM PERCENTAGE BETWEEN -20 AND 20)" \
           "\nYOU CAN USE THE FOLLOWING COMMANDS (ASSUMING YOU HAVE ENOUGH MONEY, RESOURCES ETC):\n\n" \
           "BUY \"RESOURCE\" \"AMOUNT\" [\"ADDITIONAL PERCENTAGE\"] - BUY THE AMOUNT OF A RESOURCE. IF YOU DON'T WANT" \
           " ANYONE ELSE TO BUY IT BEFORE YOU,\nYOU CAN SPECIFY HOW MUCH MORE " \
           "ARE YOU WILLING TO PAY (IN PERCENTAGES). " \
           "BUY ORDERS OF ALL THE PLAYERS ARE SORTED IN THE DESCENDING ORDER \n" \
           "FIRST BY THE [\"ADDITIONAL PERCENTAGE\"] - DEFAULTS TO 0 - AND THEN BY THE " \
           "SPECIFIED AMOUNT\n\n" \
           "SELL \"RESOURCE\" \"QUANTITY\" - SELL THE AMOUNT OF A RESOURCE (FOR THE MARKET PRICE)\n\n" \
           "FLOG \"RESOURCE\" \"QUANTITY\" - SAME AS \"SELL\" BUT THE RESOURCE DOESN'T GO BACK TO THE MARKET - " \
           "AT THE COST OF GETTING ONLY 85% OF THE MARKET PRICE\n\n" \
           "...YOU CAN ALSO USE ABILITIES (EACH ONE HAS AN ATTACHED COST) SUCH AS:\n\n" \
           "FUTURE - SEE THE FLUCTUATIONS OF RESOURCE PRICES THAT WILL TAKE PLACE AFTER THE NEXT ROUND -" \
           "COST: 200\n\n" \
           "SPY - SEE POSSESSIONS AND MONEY OF ALL OTHER PLAYERS. THEY GET A NOTIFICATION THAT SOMEONE HAS SPIED ON THEM - COST: 400 \n\n" \
           "SHORTEN - SHORTEN THE NEXT ROUND BY 75% (CAN ONLY BE SHORTENED ONCE) - COST: 600\n\n" \
           "DESTROY - DESTROY 25% OF ALL RESOURCES OF ALL THE PLAYERS (INCLUDING YOURS). THEY GET A NOTIFICATION - " \
           "COST: 1000\n\n" \
           "ALL COMMANDS ARE EXECUTED BETWEEN THIS ROUND AND THE NEXT ONE IN THIS ORDER: \n" \
           "BUY -> SELL | FLOG -> ABILITIES. YOU CAN ALSO IMMEDIATLY VIEW THE RULES BY TYPING \"RULES\". \n" \
           "PLAYERS THAT HAVE THE MOST MONEY ON THEM (NORMAL MONEY + THE SUM OF ALL THEIR RESOURCES SOLD AT THE" \
           "CURRENT PRICE) WIN."


def calculate_percentages():
    result = []
    for i in range(len(stock.stock)):
        result.append(random.randint(-20, 21))

    return result


def print_percentages():
    result = ""
    i = 0
    for percentage in percentages:
        if percentage > 0:
            result += stock.stock[i][0] + ": +" + str(percentage) + "%\n"
        elif percentage == 0:
            result += stock.stock[i][0] + ": NO CHANGE\n"
        else:
            result += stock.stock[i][0] + ": " + str(percentage) + "%\n"
        i += 1
    result += "\n"

    return result


def process_queries():
    global percentages
    global round_shortened

    while not queue_buy.empty():
        query = queue_buy.get()

        if stock.stock_available(query.stock_name, int(query.quantity)):
            if stock.stock_buyable(query.stock_name, query.quantity, query.player.money, query.over_percentage):

                query.player.add_stock(query.stock_name, query.quantity)
                query.player.reduce_money(math.floor(stock.get_stock_price(query.stock_name) *
                                          query.quantity * (1 + query.over_percentage / 100)))
                stock.reduce_stock(query.stock_name, query.quantity)

                query.player.messages.append("-> BOUGHT " + str(query.quantity) + " OF " + str(query.stock_name))
            else:
                tmp_quantity = math.floor(query.player.money /
                                          (query.get_stock_price(query.stock_name) * (1 + query.over_percentage)))
                if tmp_quantity:
                    query.player.add_stock(query.stock_name, tmp_quantity)
                    query.player.reduce_money(math.floor(stock.get_stock_price(query.stock_name) *
                                              tmp_quantity * (1 + query.over_percentage / 100)))
                    stock.reduce_stock(query.stock_name, tmp_quantity)

                    query.player.messages.append("-> BOUGHT ONLY " + str(tmp_quantity) + " OF " + str(query.stock_name) +
                                                 " (YOU DIDN'T HAVE ENOUGH MONEY FOR MORE)")
                else:
                    query.player.messages.append("-> YOU DIDN'T HAVE ENOUGH MONEY TO BUY EVEN A SINGLE PIECE OF "
                                                 + str(query.stock_name))

        elif stock.get_stock_quantity(query.stock_name):
            if stock.stock_buyable(query.stock_name, stock.get_stock_quantity(query.stock_name),
                                   query.player.money, query.over_percentage):

                tmp_quantity = stock.get_stock_quantity(query.stock_name)

                query.player.add_stock(query.stock_name, stock.get_stock_quantity(query.stock_name))
                query.player.reduce_money(math.floor(stock.get_stock_price(query.stock_name) *
                                          stock.get_stock_quantity(query.stock_name) * (1 + query.over_percentage / 100)))
                stock.reduce_stock(query.stock_name, stock.get_stock_quantity(query.stock_name))

                query.player.messages.append("-> BOUGHT ONLY " + str(tmp_quantity) + " OF " + str(query.stock_name))
            else:
                tmp_quantity = math.floor(query.player.money /
                                          (query.get_stock_price(query.stock_name) * (1 + query.over_percentage)))
                if tmp_quantity:
                    query.player.add_stock(query.stock_name, tmp_quantity)
                    query.player.reduce_money(math.floor(stock.get_stock_price(query.stock_name) *
                                              tmp_quantity * (1 + query.over_percentage / 100)))
                    stock.reduce_stock(query.stock_name, tmp_quantity)

                    query.player.messages.append("-> BOUGHT ONLY " + str(tmp_quantity) + " OF " + str(query.stock_name) +
                                                 " (YOU DIDN'T HAVE ENOUGH MONEY FOR MORE)")
                else:
                    query.player.messages.append("-> YOU DIDN'T HAVE ENOUGH MONEY TO BUY EVEN A SINGLE PIECE OF "
                                                 + str(query.stock_name))

        else:
            query.player.messages.append("-> " + str(query.stock_name) + " ISN'T AVAILABLE ANYMORE. SORRY")

    while not queue_sell.empty():
        query = queue_sell.get()

        if query.flogged:
            if 0 < query.quantity <= query.player.get_stock_quantity(query.stock_name):
                query.player.reduce_stock(query.stock_name, query.quantity)
                query.player.add_money(math.floor(stock.get_stock_price(query.stock_name) * query.quantity))
                stock.add_stock(query.stock_name, query.quantity)

                query.player.messages.append("-> SOLD " + str(query.quantity) + " OF " + str(query.stock_name))

            elif query.quantity > query.player.get_stock_quantity(query.stock_name):
                query.player.reduce_stock(query.stock_name, query.player.get_stock_quantity(query.stock_name))
                query.player.add_money(math.floor(stock.get_stock_price(query.stock_name) *
                                       query.player.get_stock_quantity(query.stock_name)))
                stock.add_stock(query.stock_name, query.player.get_stock_quantity(query.stock_name))

                query.player.messages.append("-> SOLD ONLY " + str(query.player.get_stock_quantity(query.stock_name)) +
                                             " OF " + str(query.stock_name))
            else:
                query.player.messages.append("-> YOU DIDN'T HAVE ENOUGH OF " + str(query.stock_name) +
                                             " TO SELL EVEN A SINGLE PIECE OF IT")

        else:
            if 0 < query.quantity <= query.player.get_stock_quantity(query.stock_name):
                query.player.reduce_stock(query.stock_name, query.quantity)
                query.player.add_money(math.floor(stock.get_stock_price(query.stock_name) * query.quantity * 0.85))

                query.player.messages.append("-> FLOGGED " + str(query.quantity) + " OF " + str(query.stock_name))

            elif query.quantity > query.player.get_stock_quantity(query.stock_name):
                query.player.reduce_stock(query.stock_name, query.player.get_stock_quantity(query.stock_name))
                query.player.add_money(math.floor(stock.get_stock_price(query.stock_name) *
                                       query.player.get_stock_quantity(query.stock_name) * 0.85))

                query.player.messages.append("-> FLOGGED ONLY " +
                                             str(query.player.get_stock_quantity(query.stock_name)) + " OF " +
                                             str(query.stock_name))
            else:
                query.player.messages.append("-> YOU DIDN'T HAVE ENOUGH OF " + str(query.stock_name) +
                                             " TO FLOG EVEN A SINGLE PIECE OF IT")

    stock.calculate_new_prices(percentages)
    percentages = calculate_percentages()

    while not queue_ability.empty():
        query = queue_ability.get()
        if query.kind == "FUTURE":
            if query.player.money >= 200:
                query.player.reduce_money(200)
                query.player.messages.append(print_percentages())
            else:
                query.player.messages.append("YOU DIDN'T HAVE ENOUGH MONEY FOR ABILITY: FUTURE")

        elif query.kind == "SPY":
            if query.player.money >= 400:
                query.player.reduce_money(400)

                query.player.messages.append("SPY RESULTS:")

                for player in stock.players:
                    if player != query.player:
                        query.player.messages.append("PLAYER " + str(player.name) + ":\n" + player.print())
                        player.messages.append("SOMEONE SPIED ON YOU")

            else:
                query.player.messages.append("YOU DIDN'T HAVE ENOUGH MONEY FOR ABILITY: SPY")

        elif query.kind == "DESTROY":
            if query.player.money >= 1000:
                query.player.reduce_money(1000)

                for player in stock.players:
                    if player != query.player:
                        player.messages.append("SOMEONE USED ABILITY: DESTROY")
                    for stock_player in player.stock:
                        player.reduce_stock(stock_player[0], math.floor(stock_player[1]/4))

            else:
                query.player.messages.append("YOU DIDN'T HAVE ENOUGH MONEY FOR ABILITY: DESTROY")

        elif query.kind == "SHORTEN":
            if query.player.money >= 600:
                query.player.reduce_money(600)

                round_shortened = True

            else:
                query.player.messages.append("YOU DIDN'T HAVE ENOUGH MONEY FOR ABILITY: SHORTEN")


def add_query(player, data):

    try:
        if data[0] == "BUY":
            if stock.stock_exists(data[1]) and 0 < int(data[2]):
                if stock.stock_available(data[1], int(data[2])):
                    if len(data) == 3 and stock.stock_buyable(data[1], int(data[2]), int(player.money)):
                        queue_buy.put(QueryBuy(player, data[1], int(data[2]), 0))
                    elif len(data) == 4 and stock.stock_buyable(data[1], int(data[2]), int(player.money), int(data[3])):
                        queue_buy.put(QueryBuy(player, data[1], int(data[2]), int(data[3])))
                    else:
                        return "YOU DON'T HAVE ENOUGH MONEY"
                else:
                    return "STOCK NOT AVAILABLE IN THE DESIRED QUANTITY"

            else:
                return "ERROR: STOCK MUST EXIST, QUANTITY MUST BE GT 0"
        elif data[0] == "SELL":
            if stock.stock_exists(data[1]) and 0 < int(data[2]):
                if player.get_stock_quantity(data[1]) >= int(data[2]):
                    queue_sell.put(QuerySell(player, data[1], int(data[2])))
                else:
                    return "YOU DON'T HAVE ENOUGH OF THAT TO SELL IT IN THE DESIRED QUANTITY"
            else:
                return "ERROR: STOCK MUST EXIST, QUANTITY MUST BE GT 0"

        elif data[0] == "FLOG":
            if stock.stock_exists(data[1]) and 0 < int(data[2]):
                if player.get_stock_quantity(data[1]) >= int(data[2]):
                    queue_sell.put(QuerySell(player, data[1], int(data[2])), True)
                else:
                    return "YOU DON'T HAVE ENOUGH OF THAT TO FLOG IT IN THE DESIRED QUANTITY"
            else:
                return "ERROR: STOCK MUST EXIST, QUANTITY MUST BE GT 0"

        elif len(data) == 1 and data[0] == "FUTURE":
            if player.money >= 200:
                queue_ability.put(QueryAbility(player, "FUTURE"))
            else:
                return "YOU DON'T HAVE ENOUGH MONEY FOR THAT ABILITY (" + str(200) + ")"

        elif len(data) == 1 and data[0] == "DESTROY":
            if player.money >= 1000:
                queue_ability.put(QueryAbility(player, "DESTROY"))
            else:
                return "YOU DON'T HAVE ENOUGH MONEY FOR THAT ABILITY (" + str(1000) + ")"

        elif len(data) == 1 and data[0] == "SPY":
            if player.money >= 400:
                queue_ability.put(QueryAbility(player, "SPY"))
            else:
                return "YOU DON'T HAVE ENOUGH MONEY FOR THAT ABILITY (" + str(400) + ")"

        elif len(data) == 1 and data[0] == "SHORTEN":
            if player.money >= 600:
                queue_ability.put(QueryAbility(player, "SHORTEN"))
            else:
                return "YOU DON'T HAVE ENOUGH MONEY FOR THAT ABILITY (" + str(600) + ")"

        elif len(data) == 1 and data[0] == "RULES":
            return print_rules()

        else:
            return "COMMAND NOT RECOGNISED"

    except IndexError:
        return "NOT ENOUGH ARGUMENTS"

    return "OK"


def client_thread(player, conn, lock, q):
    conn.setblocking(False)
    global clients_current

    conn.sendall(print_rules().encode())
    while True:

        try:
            if conn.recv(1024).decode() == "START":
                conn.sendall("-> OK, WAITING FOR OTHERS".encode())

                # locking global value from other threads
                lock.acquire()
                clients_current += 1
                lock.release()

                break
            else:
                conn.sendall("-> TYPE START".encode())

        except socket.error:
            pass

    while q.empty():
        pass

    q.get()

    # GAME IN PROGRESS
    while True:
        if round_shortened:
            conn.sendall("!!! ROUND SHORTENED !!!".encode())
        conn.sendall("-> STARTING IN:".encode())

        for i in reversed(range(1, 6)):
            conn.sendall(("-> " + str(i)).encode())
            sleep(1)

        while q.empty():
            pass

        q.get()

        conn.sendall(("-> ROUND " + str(rounds_current) + " START").encode())

        # ROUND
        if rounds_current > 1:
            conn.sendall("-> MESSAGES:\n".encode())
            for message in player.messages:
                conn.sendall((message + "\n").encode())
            if not len(player.messages):
                conn.sendall("NONE".encode())
            player.messages = []

        conn.sendall(stock.print().encode())
        conn.sendall(player.print().encode())

        while q.empty():
            try:
                data = conn.recv(1024).decode()
                print('RECEIVED: ' + data + ', FROM: ' + conn.getpeername()[0] + ':' +
                      str(conn.getpeername()[1]))
                conn.sendall(("-> " + add_query(player, data.upper().split())).encode())
            except socket.error:
                pass

        conn.sendall(("-> END OF ROUND " + str(rounds_current)).encode())

        # IF LAST ROUND -> DISCONNECT
        if str(q.get()) == "EXIT":
            break

        conn.sendall("-> WAITING FOR THE NEXT ROUND".encode())

        # BREAK
        while q.empty():
            try:
                print('RECEIVED: ' + conn.recv(1024).decode() + ', FROM: ' + conn.getpeername()[0] + ':' +
                      str(conn.getpeername()[1]))

                conn.sendall("-> WAIT FOR THE START OF THE NEXT ROUND".encode())
            except socket.error:
                pass

        q.get()

    for winner in winners:
        if winner == player.name:
            conn.sendall("-> YOU WON\n".encode())
            sleep(1)
            conn.sendall("EXIT".encode())
            conn.close()
            return

    conn.sendall("-> YOU LOST\n".encode())
    sleep(1)
    conn.sendall("EXIT".encode())
    conn.close()


def connect_clients():
    is_first_client = True
    global clients_total
    global clients_left
    global threads
    global queues
    global stock

    thread_lock = threading.Lock()

    while True:

        if clients_left:
            thread_conn, address = s.accept()
            print("CONNECTED TO " + address[0] + ":" + str(address[1]))

            if is_first_client:
                thread_conn.sendall("-> YOU'RE CONNECTED TO THE SERVER. ENTER THE NUMBER OF PLAYERS (2-8)".encode())
                while True:
                    try:
                        clients_total = int(thread_conn.recv(1024).decode())
                        clients_left = clients_total

                        if 2 <= clients_total <= 8:
                            stock = Stock(clients_total)
                            thread_conn.sendall("-> OK, WAITING FOR OTHERS. TYPE 'START' WHEN YOU'RE READY".encode())
                            break

                        thread_conn.sendall("-> WRONG NUMBER OF PLAYERS".encode())

                    except ValueError:
                        thread_conn.sendall("-> THAT'S NOT A NUMBER".encode())

                is_first_client = False

            else:
                thread_conn.sendall("-> YOU'RE CONNECTED TO THE SERVER. TYPE 'START' WHEN YOU'RE READY".encode())

            thread_queue = queue.Queue()
            queues.append(thread_queue)
            player = Player(clients_left)
            stock.add_player(player)
            thread = threading.Thread(target=client_thread, args=(player, thread_conn, thread_lock, thread_queue,))
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

rounds_total = 6
rounds_current = 1

threads = []
queues = []
round_time = 20
break_time = 5
round_shortened = False

queue_buy = queue.PriorityQueue()
queue_sell = queue.Queue()
queue_ability = queue.Queue()

stock = None

connect_clients()

percentages = calculate_percentages()

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
    if round_shortened:
        sleep(math.ceil(round_time*0.25))
        round_shortened = False
    else:
        sleep(round_time)
    print("END ROUND " + str(rounds_current))

    if rounds_current == rounds_total:
        winners = stock.calculate_winner()
        for q in queues:
            q.put("EXIT")

        print("THE GAME HAS ENDED")
        break
    else:
        for q in queues:
            q.put(".")

    print("START BREAK")
    # TIME FOR PRICE CHANGE ETC.
    start = timer()
    process_queries()
    sleep(break_time - (timer() - start))
    print("END BREAK")

    for q in queues:
        q.put(".")

    rounds_current += 1


# WAITING FOR THREADS TO END
for t in threads:
    t.join()

print("THE END")
exit(0)
