class Player:
    def __init__(self, name):
        self.name = name
        # [nazwa, ilość]
        self.stock = [["GOLD", 0], ["SILVER", 0], ["COPPER", 0]]
        self.money = 3000
        self.messages = []

    def print(self):
        result = "\n"
        result += (" MONEY:  " + str(self.money) + " ").center(100, "*") + "\n"
        result += "*" * 100 + "\n"
        result += "*" + "STOCK".ljust(48) + "*" + "QUANTITY".center(49) + "*\n"
        result += "*" * 100 + "\n"

        for stock in self.stock:
            result += "*" + str(stock[0]).ljust(48) + "*" + str(stock[1]).center(49) + "*\n"
            result += "*" * 100 + "\n"

        result += "\n"

        return result

    def get_stock(self, stock_name):
        for stock in self.stock:
            if stock[0] == stock_name:
                print("YES:  " + stock[0])
                return stock
        print("NOOO:  " + stock_name)

    def get_stock_quantity(self, stock_name):
        return self.get_stock(stock_name)[1]

    def has_enough_stock(self, product_id, amount):
        return self.stock[product_id][1] >= amount

    def add_stock(self, stock_name, quantity):
        self.get_stock(stock_name)[1] += quantity

    def reduce_stock(self, stock_name, quantity):
        self.get_stock(stock_name)[1] -= quantity

    def has_enough_money(self, price):
        return self.money >= price

    def add_money(self, money):
        self.money += money

    def reduce_money(self, money):
        self.money -= money

    def add_message(self, message):
        self.messages.append(message)
