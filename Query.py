class QueryBuy:
    def __init__(self, player, stock_name, quantity, over_percentage=0):
        self.player = player
        self.stock_name = stock_name
        self.quantity = quantity
        self.over_percentage = over_percentage

    def __lt__(self, other): # reversed for piority_queue
        if self.over_percentage > other.over_percentage:
            return True
        elif self.over_percentage == other.over_percentage:
            if self.quantity > other.quantity:
                return True
        return False


class QuerySell:
    def __init__(self, player, stock_name, quantity, flogged=False):
        self.player = player
        self.stock_name = stock_name
        self.quantity = quantity
        self.flogged = flogged


class QueryAbility:
    def __init__(self, player, kind):
        self.player = player
        self.kind = kind
