from player import Player

class Stock:

    def __init__(self):
         self.players = []
          #[nazwa,aktualna ilość,aktualna cena, początkowa ilość, początkowa cena]
          #początkowe wartości są używane tylko do policzenia zmian ceny
         self.stock = [["gold", 200, 150, 200, 150], ["silver", 200, 120, 200, 120], ["copper", 200, 80, 200, 80]]

    def add_player(self,name):
         self.players.append(Player(name))

    def print_state(self): #w tej chwili printuje też posiadłości graczy, zamiast tego powinien to wysyłać do client.py(?)
        for p in self.players:
            print(p.to_string())
        print("Available stock:")
        for s in self.stock:
            print("Product: " + s[0] + " Available: " + str(s[1]) + " Price: " + str(s[2]))

    def sell_to_player(self,player_id,product_id,amount):
        price = amount * self.stock[product_id][2]
        if amount <= 0:
            return "Wrong amount."
        if not (self.players[player_id].has_enough_money(price)): 
            return "Not enough money."
        if  self.stock[product_id][1] < amount:
            return "Not enough products in stock."

        self.players[player_id].reduce_money(price)
        self.players[player_id].add_possesions(product_id,amount)
        self.stock[product_id][1] -= amount
        self.calculate_new_price(product_id) #?

        return "Transaction succesful."

    def buy_from_player(self,player_id,product_id,amount):
        price = amount * self.stock[product_id][2]
        if amount <= 0:
            return "Wrong amount."   
        if not self.players[player_id].has_enough_possesions(product_id,amount):
            return "Not enough products in possesion."
        
        self.players[player_id].add_money(price)
        self.players[player_id].reduce_possesions(product_id,amount)
        self.stock[product_id][1] += amount
        self.calculate_new_price(product_id) #?

        return "Transcation succesful."
        
    def calculate_new_price(self,product_id):
        
        product = self.stock[product_id] #dla przejrzystości
        #id: pruduct[0] = nazwa, [1] = aktualna ilość, [2] = aktualna cena,
        # [3] = początkowa ilość, [4] = początkowa cena
        if product[1] <= product[3]:
            self.stock[product_id][2] = product[4] + ((product[1] - product[3]) * (product[1] - product[3])) * 0.01 
        if product[1] > product[3]:
            self.stock[product_id][2] = product[4] - ((product[1] - product[3]) * (product[1] - product[3])) * 0.01 



 