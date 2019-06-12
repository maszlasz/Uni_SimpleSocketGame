from player import Player

class Stock:

    def __init__(self):
         self.players = []
          #[nazwa,aktualna ilość,aktualna cena, początkowa ilość, początkowa cena]
          #początkowe wartości są używane tylko do policzenia zmian ceny
         self.stock = [["gold", 200, 150.0, 200, 150.0], ["silver", 200, 120.0, 200, 120.0], ["copper", 200, 80.0, 200, 80.0]]

    def add_player(self,name):
         self.players.append(Player(name))

    def print_state(self): #w tej chwili printuje też posiadłości graczy, zamiast tego powinien to wysyłać do client.py(?)
        #for p in self.players:
        #    print(p.to_string())
        print("Available stock:")
        for s in self.stock:
            print("Product: " + s[0] + " Available: " + str(s[1]) + " Price: " + str(s[2]))

    def player_state(self,player_ip):
        for p in self.players:
            if p.ip == player_ip:
                return p.to_string()


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
        

        return "Transcation succesful."
        
    def calculate_new_prices(self):
        for s in self.stock:
            if s[1] <= s[3]:
                s[2] = s[4] + ((s[1] - s[3])*(s[1] - s[3]))*0.01
            if s[1] > s[3]:
                s[2] = s[4] - ((s[1] - s[3])*(s[1] - s[3]))*0.01

    def show_results(self):
        results = []
        for p in self.players:
            score = p.money
            for i in range(len(self.stock)):
                score += self.stock[i][2] * p.possesions[i][1]
            results.append((p.name, score))
        results.sort(key = lambda x: x[1], reverse = True)
        print("\n\n\t\tRESULTS:")
        for r in results:
            print("\n\t" + str(r[0]) + "   score: " + str(r[1]) )

 