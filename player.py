class Player:

    def __init__(self,name):
        self.name = name
        #[nazwa, ilość]
        self.possesions = [["gold", 0],["silver", 0]]
        self.money = 3000
    
    def to_string(self):
        string = "Name: " + self.name + "\nMoney: " + str(self.money) + "\nPossesions: "
        for p in self.possesions:
            string = string + "\n " + p[0] + " " + str(p[1])
        string = string + "\n"
        return string

    def has_enough_possesions(self,product_id,amount):
        return self.possesions[product_id][1] >= amount
    
    def add_possesions(self,product_id,amount):
        self.possesions[product_id][1] += amount
        
    
    def reduce_possesions(self,product_id,amount):
        self.possesions[product_id][1] -= amount
        

    def has_enough_money(self,price):
         return self.money >= price

    def add_money(self,price):
        self.money += price
        
    
    def reduce_money(self,price):
        self.money -= price
        

    

    

    
    


    

