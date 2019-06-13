from Player import *
import math


class Stock:

    def __init__(self, players_number):
        self.players = []
        # [nazwa,aktualna ilość,aktualna cena, początkowa ilość, początkowa cena]
        # początkowe wartości są używane tylko do policzenia zmian ceny
        self.stock = [["GOLD", 10*players_number, 300, 10*players_number, 300],
                      ["SILVER", 20*players_number, 120, 20*players_number, 120],
                      ["COPPER", 30*players_number, 60, 30*players_number, 60]]

    def stock_exists(self, stock_name):
        for stock in self.stock:
            if stock[0] == stock_name:
                return True
        return False

    def get_stock(self, stock_name):
        for stock in self.stock:
            if stock[0] == stock_name:
                return stock

    def get_stock_price(self, stock_name):
        return self.get_stock(stock_name)[2]

    def get_stock_quantity(self, stock_name):
        return self.get_stock(stock_name)[1]

    def stock_available(self, stock_name, quantity):
        return self.get_stock(stock_name)[1] >= quantity

    def stock_buyable(self, stock_name, quantity, player_money, over_percentage=0):
        return self.get_stock(stock_name)[2]*quantity*(1+over_percentage/10) <= player_money

    def add_player(self, player):
        self.players.append(player)

    def add_stock(self, stock_name, quantity):
        self.get_stock(stock_name)[1] += quantity

    def reduce_stock(self, stock_name, quantity):
        self.get_stock(stock_name)[1] -= quantity

    def calculate_new_prices(self, percentages):
        i = 0
        for stock in self.stock:
            if stock[1] <= stock[3]:
                stock[2] = math.floor((stock[4] + ((stock[1] - stock[3]) * (stock[1] - stock[3])) * 0.01) *
                                      (1 + percentages[i]/100))
            else:
                stock[2] = math.floor((stock[4] - ((stock[1] - stock[3]) * (stock[1] - stock[3])) * 0.01) *
                                      (1 + percentages[i]/100))

            i += 1

    def calculate_winner(self):
        current_max = 0
        winners = []

        for player in self.players:
            sum_stock_value = player.money
            for stock in player.stock:
                sum_stock_value += stock[1] * self.get_stock_price(stock[0])

            if sum_stock_value > current_max:
                current_max = sum_stock_value
                del winners[:]
                winners.append(player.name)
            elif sum_stock_value == current_max:
                winners.append(player.name)

        return winners

    def print(self):
        result = "\n"
        result += " STOCK EXCHANGE ".center(100, "*") + " \n"
        result += "*" * 100 + " \n"
        result += "*" + "STOCK".ljust(32) + "*" + "PRICE".center(32) + "*" + "QUANTITY".center(32) + "* \n"
        result += "*" * 100 + " \n"

        for stock in self.stock:
            result += "*" + str(stock[0]).ljust(32) + "*" + str(stock[2]).center(32) + "*" + str(stock[1]).center(32) +\
                      "* \n"
            result += "*" * 100 + " \n"

        result += " \n"

        return result
