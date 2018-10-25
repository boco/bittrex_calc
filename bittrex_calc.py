import getopt, sys
from os import system
import pandas as pd
from string import ascii_lowercase as abc
from decimal import Decimal

class Coin:
    def __init__(self, name):
        self.name = name
        self.total = 0.00000000
        self.purchases = []
        self.ave_price = 0.00000000

    def __str__(self):
        return "%s: %f | %s\n" % (self.name, self.total, self.purchases)

    def buy(self, amount, price):
        # add a purchase with the amount, price, and remaining.
        self.purchases.append( [amount, price, amount, 0.00000] )
        tprice = 0.0
        tcount = 0.0
        for i in self.purchases:
            tprice += i[1] * i[2]
            tcount += i[2]
        self.ave_price = tprice / tcount
            
    def sell(self, amount, price):
        fulfilled = 0.0
        for i in reversed(range(0, len(self.purchases))):
            if self.purchases[i][2] == 0:
                continue
            added = 0.0
            if self.purchases[i][2] + fulfilled > amount:
                left = amount - fulfilled
                self.purchases[i][2] -= left
                fulfilled += left
                added = left

            elif self.purchases[i][2] + fulfilled < amount:
                fulfilled += self.purchases[i][2]
                added = self.purchases[i][2]
                self.purchases[i][2] = 0
            else:
                fulfilled = amount
                added = self.purchases[i][2]                
                self.purchases[i][2] = 0
            self.purchases[i][3] = (added * price) - (added * self.purchases[i][1])
            if fulfilled > amount:
                fulfilled = amount
            if fulfilled == amount:
                break     
                
    def profit(self):
        profit = 0.0
        for i in self.purchases:
            profit += i[3]
        
        return profit

def main():
    # Load csv
    df = pd.read_csv("orders.csv") 

    coins = {}

    for i in df['Exchange']:
        if i not in coins:
            coins[i] = Coin(i)    
   
    print("Bittrex Profit Calculator\n")
    print("You've done %d trades with %d coins since %s.\n" % (len(df['Type']), len(coins), df['Closed'][0]))
        
    spent = {'BTC':0.00000000}
    wallet = {'BTC':0.00000000} #{'BTC':0.14630875}

    for i in (range(0, len(df['Type']))):
        market = df['Exchange'][i][:3]
        price = df['Price'][i]
        perunit = df['Perunit'][i]
        type = df['Type'][i][6:]
        if type == 'BUY':
            #Buy
            if wallet[market] < price:
                #Didn't have enough money so it's a loadup from outside.
                spent[market] += price
            else:
                #Had enough money so it's a buy.
                wallet[market] -= price
            coins[df['Exchange'][i]].total += df['Quantity'][i]
            coins[df['Exchange'][i]].buy(df['Quantity'][i], perunit)
        else:
            #Sell
            coins[df['Exchange'][i]].sell(df['Quantity'][i], perunit)
            coins[df['Exchange'][i]].total -= df['Quantity'][i]
            wallet[market] += price
            #Check previous buy to see if this is profitable.

    profit = {'BTC':0.00000000}
    high = None
    low = None
    print("   %-14s %-15s %-15s %s\n" % ("Coin", "Holdings", "Profit", "Average Price Per Coin"))
    i = 0
    for k, coin in coins.items():
        market = coin.name[:3]
        profit[market] += coin.profit()
        if not high:
            high = coin
        else:
            if high.profit() < coin.profit():
                high = coin
        if not low:
            low = coin
        else:
            if low.profit() > coin.profit():
                low = coin

        print("   %-14s %-15f %-15.8f %.8f on %d trades." % (k, coin.total, coin.profit(), coin.ave_price, (len(coin.purchases))))

    print("\nYou've made %8.8f BTC" % (profit['BTC']))
    print("You made the most off %s. You made the least of %s.\n" %( high.name, low.name))
    print("You have deposited into Bittrex %8.8f BTC" % (spent['BTC']))
    print("Current portfolio state is %8.8f BTC" % (spent['BTC'] + profit['BTC']))

if __name__ == "__main__":
   main()
