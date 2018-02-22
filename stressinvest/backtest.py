from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
from strategy import strategy
import sys
import time
import sqlite3
import math
import datetime
import numpy as np

#------------------------------------------------------------------------------
def ticker(candle):
    # global variables
    global market_status
    global db_table
    global db_name
    global candles
    
    # ticker
    # call strategy
#    db = sqlite3.connect(db_name)
#    cursor = db.cursor()
    
    t1=candle[1]
    t0=t1-120*60*60 #maximum number of data used - 120hr
    
    rows=candles[:,1]
    rows=(rows>=t0) & (rows<=t1)
    db_candles=candles[rows]
#    aux_str='SELECT * FROM '
#    aux_str+=db_table
#    aux_str+=' WHERE start BETWEEN %s AND %s' %(str(t0), str(t1))
#    
#    cursor.execute(aux_str)
#    db_candles=cursor.fetchall()
#    db.close()
#    db_candles.sort(key=lambda tup: tup[1]) # Order the results by timestamp
    
#    db_candles=np.array(db_candles)
    decision=strategy(db_candles, market_status, "ema", [1*60*60])
    # call trade
    trade(decision,candle)
#------------------------------------------------------------------------------
def trade(decision,candle):
    global currency_1
    global currency_2
    global market_status
    global transactions
    global trader_fee

    if decision=="buy" and market_status!="bought":
        #sells
        if currency_1>0: # if it is not bought, buys
            price=candle[5] # close price
            currency_2=currency_1/price*(1-trader_fee/100) # applies fees
            fee=currency_1*(trader_fee/100)
            currency_1=0 
            time=candle[1]
            time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
            transactions.append(["buy",currency_1, currency_2, fee, price,time])
            market_status="bought"
    elif decision=="sell" and market_status!="sold":
        if currency_2>0: # if it is not sold, sells
            price=candle[5] # close price
            currency_1=currency_2*price*(1-trader_fee/100) # applies fees
            fee=currency_2*price*(trader_fee/100)
            currency_2=0
            time=candle[1]
            time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
            transactions.append(["sell",currency_1, currency_2, fee, price,time])  
            market_status="sold"
    
#------------------------------------------------------------------------------
# Main Program

# Define exchance and currency
exchange="BINANCE" # To be Implemented Additional Exchanges
currency="BTCUSDT"

db_name="bitfinex_0.1.db"
db_table="candles_USD_BTC"

market_status="sold"
currency_1=1000. #ex: USD
currency_2=0.    #ex: BTC
trader_fee=0.2   #margin fee, in %

t1 = time.mktime(datetime.datetime(2018, 1, 1, 7, 0, 0, 0).timetuple())
#t1 = time.mktime(datetime.datetime(2018, 1, 18, 7, 0, 0, 0).timetuple())

t2 = time.mktime(datetime.datetime(2018, 2, 1, 7, 0, 0, 0).timetuple())

db = sqlite3.connect(db_name)
cursor = db.cursor()

aux_str='SELECT * FROM '
aux_str+=db_table
aux_str+=' WHERE start BETWEEN %s AND %s' %(str(t1), str(t2))
cursor.execute(aux_str)    
candles=np.array(cursor.fetchall()) #id, start, open, high, low, close, , vwp, volume, trades
warmupperiod= 20*60*60 #60 hours - in seconds - depends on strategy
transactions=[["Action", "Currency 1", "Currency 2", "Paid Fee", "Price", "Date"]]
transactions.append(["Initial",currency_1,currency_2, 0, "na", datetime.datetime.fromtimestamp(t1).strftime('%m/%d/%Y %H:%M,')])
for i,candle in enumerate(candles):
    if i%60==0:
        print(str(i)+" / " +str(len(candles)))
    if candle[1]>t1+warmupperiod:
        ticker(candle)
        
# Finish Sold
if currency_2>0: # if it is not sold, sells
    price=candle[5] # close price
    currency_1=currency_2*price*(1-trader_fee/100) # applies fees
    fee=currency_2*price*(trader_fee/100)
    currency_2=0
    time=candle[1]
    time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
    transactions.append(["sell",currency_1, currency_2, fee, price, time]) 

for transaction in transactions:
    print transaction
buynhold=candles[-1, 5]/candles[warmupperiod/60,5]
strategyratio=transactions[-1][1]/1000 #1000 is the initial investment
print("Backtest Results: \n")
print("Buy and Hold: %s \n"%(buynhold))
print("Strategy Profit: %s"%(strategyratio))
print("Profit/Buy 'n Hold: %s"%str(strategyratio/buynhold))
transactions=np.array(transactions)
print("Maximum Cash: %s"%str(max(transactions[1::,1].astype(float))))