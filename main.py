from stock import Stock

s = Stock()

s.add_player("player0")
s.add_player("player1")
s.add_player("player2")

s.print_state()
print(s.sell_to_player(0,1,3))#(player_id/product_id/amount)
print(s.sell_to_player(1,1,113))
print(s.sell_to_player(1,1,13))
print(s.buy_from_player(1,1,5))
print(s.buy_from_player(0,0,8))
print(s.buy_from_player(0,0,8))
s.print_state()