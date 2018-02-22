from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
from strategy import strategy
import threading
import sys
import time
import sqlite3
import math
import numpy as np
import datetime

#------------------------------------------------------------------------------
def ticker(msg):
    # global variables
    global b_warmedup
    global b_trade
    global market_status
    global db_table
    global db_name
    
    # ticker
    #id, start, open, high, low, close, , vwp, volume, trades
    s_start=msg['k']['t']/1000 #s
    s_open=msg['k']['o']
    s_high=msg['k']['h']
    s_low=msg['k']['l']
    s_close=msg['k']['c']
    s_vwp=msg['k']['c'] #average weighted price - will assume close price
    s_volume=msg['k']['v']
    s_trades=msg['k']['t']
    final_bar=msg['k']['x'] # if it is the final bar, insert in the database
    if final_bar: # candle has formed
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        cmd="INSERT INTO candles_USDT_BTC (start, open, high, low, close, vwp, volume, trades) VALUES ("
        cmd+=str(s_start)
        cmd+=","+str(s_open)
        cmd+=","+str(s_high)
        cmd+=","+str(s_low)
        cmd+=","+str(s_close)
        cmd+=","+str(s_vwp)
        cmd+=","+str(s_volume)
        cmd+=","+str(s_trades)
        cmd+=");"
        cursor.execute(cmd)
        db.commit()
        db.close()
    # call strategy
    if b_warmedup:
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        
        t1=time.time()
        t1-=t1%60-60 # last full minute candle
        t0=t1-120*60*60 #maximum number of data used - 120hr
        
        aux_str='SELECT * FROM '
        aux_str+=db_table
        aux_str+=' WHERE start BETWEEN %s AND %s' %(str(t0), str(t1))
        
        cursor.execute(aux_str)
        db_candles=cursor.fetchall()
        db_candles.sort(key=lambda tup: tup[1]) # Order the results by timestamp
        db_candles=np.array(db_candles)
        decision=strategy(db_candles, market_status, "ema", [60])
        # call trade
        trade(decision)
#------------------------------------------------------------------------------
def warmup(exchange, currency, warmupperiod):
    global b_warmedup
    global db_table
    global db_name
    t1=time.time()
    t1-=t1%60-60 # last full minute candle
    t0=t1-warmupperiod
    # Import DB results

    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    aux_str='SELECT * FROM '
    aux_str+=db_table
    aux_str+=' WHERE start BETWEEN %s AND %s' %(str(t0), str(t1))
    
    cursor.execute(aux_str)
    db_candles=cursor.fetchall()
    db_candles.sort(key=lambda tup: tup[1]) # Order the results by timestamp
    db_candles=np.array(db_candles)
    #print(db_candles)
    
    # Scan the imported results to find gaps
    v_gaps=[]
    for i, candle in enumerate(db_candles):
        if i==0: # check first candle
            if candle[1]-t0>60: # there is a gap
                v_gaps.append([t0,candle[1]])        
        if i>0: # check the others
            if candle[1]-db_candles[i-1][1]>60: # there is a gap
                v_gaps.append([candle[1],db_candles[i-1][1]])
    # check last candle
    if t1-candle[1]>60: # there is a gap
        v_gaps.append([candle[1],t1])   
    
    v_candles=[]
    for gap in v_gaps:
        # check if the gap is above 500 candles
        startTime=gap[0]
        endTime=gap[1]
        v_aux=[]
        if (endTime-startTime)/60>500:
            aux_endTime=startTime
            for i in range(int(math.floor((endTime-startTime)/60/500))):
                aux_startTime=aux_endTime
                aux_endTime=aux_startTime+500*60
                if aux_endTime>endTime:
                    aux_endTime=endTime
                v_aux.append([aux_startTime, aux_endTime])
        else:
            v_aux.append([startTime, endTime])
        # Get the candles
        for aux in v_aux: 
            startTime=int(aux[0])*1000 #binance uses ms
            endTime=int(aux[1])*1000 #binance uses ms
            candles = client.get_klines(symbol=currency, interval=Client.KLINE_INTERVAL_1MINUTE, limit=500, startTime=startTime, endTime=endTime)
            v_candles.append(candles)
            
    # add candles to the database
    for list_candle in v_candles:
        for candle in list_candle:
            s_start=candle[0]/1000 #s
            s_open=candle[1]
            s_high=candle[2]
            s_low=candle[3]
            s_close=candle[4]
            s_vwp=candle[4] #average weighted price - will assume close price
            s_volume=candle[5]
            s_trades=candle[8]
            cmd="INSERT INTO "+str(db_table)+" (start, open, high, low, close, vwp, volume, trades) VALUES ("
            cmd+=str(s_start)
            cmd+=","+str(s_open)
            cmd+=","+str(s_high)
            cmd+=","+str(s_low)
            cmd+=","+str(s_close)
            cmd+=","+str(s_vwp)
            cmd+=","+str(s_volume)
            cmd+=","+str(s_trades)
            cmd+=");"
            cursor.execute(cmd)
    db.commit()
    # Delete duplicate timestamp
    cmd="DELETE FROM "+db_table+" WHERE rowid NOT IN (SELECT MAX(rowid) FROM "+db_table+" GROUP BY start);"
    cursor.execute(cmd)
    db.commit()
    db.close()
    b_warmedup=True
#------------------------------------------------------------------------------
def trade(decision):
    global b_realtrade
    global market_status
    global asset1
    global asset2
    global precisionasset1
    global precisionasset2
    global currency
    
    if b_realtrade:
        if decision=="buy":
            # get asset 2 balance to buy everything
            balance = client.get_asset_balance(asset=asset2)
            amt_str=math.floor(float(balance["free"]) * 10**precisionasset2) / 10**precisionasset2
            amt_str = "{:0.0{}f}".format(amt_str, precisionasset2)
            # read asset1 balance
            balance_t0 = client.get_asset_balance(asset=asset1)
            balance_t0 = float(balance_t0["free"])
            order = client.order_market_buy(symbol=currency, quantity=amt_str)
            # read asset1 balance and calculate the price
            balance_t1 = client.get_asset_balance(asset=asset1)
            balance_t1=float(balance_t1["free"])
            price=float(amt_str)/(balance_t1-balance_t0)/(1.-trader_fee/100.)  
            fee=float(amt_str)*trader_fee/100.
        if decision=="sell":
            # get asset 1 balance to sell everything
            balance = client.get_asset_balance(asset=asset1) 
            amt_str=math.floor(float(balance["free"]) * 10**precisionasset1) / 10**precisionasset1
            amt_str = "{:0.0{}f}".format(amt_str, precisionasset1) #amount to be sold
            # read asset2 balance to calculate the price
            balance_t0 = client.get_asset_balance(asset=asset2)
            balance_t0 = float(balance_t0["free"])
            # Market Order - TODO - EXCEPTION HANDLING if fails
            order = client.order_market_sell(symbol=currency, quantity=amt_str) # if order["status"]=="FILLED" order is finished
            # read asset2 balance and calculate the price
            balance_t1 = client.get_asset_balance(asset=asset2)
            balance_t1=float(balance_t1["free"])
            price=(balance_t1-balance_t0)/(1.-trader_fee/100.)/float(amt_str)
            fee=amt_str*price*trader_fee/100. # fee always in asset2
        # Log Trade
        #['Action','Balance Asset 1','Balance Asset 2','Paid Fee','Price','Date']
        balance_1=client.get_asset_balance(asset=asset1)["free"]
        balance_2=client.get_asset_balance(asset=asset2)["free"]
        if decision!="":
            with f as open("log.txt", a):
                aux=decision
                aux+=", "+balance_1
                aux+=", "+balance_2
                aux+=", "+str(fee)
                when=order["transactTime"]
                when=datetime.datetime.fromtimestamp(float(when)).strftime('%m/%d/%Y %H:%M:%S')
                f.write(aux)
    else:
        if decision!="":
            print("decision")
    
#------------------------------------------------------------------------------
# Main Program
# Get API Keys
api_key=""
api_secret=""

# Define exchance and currency
exchange="BINANCE" # To be Implemented Additional Exchanges
currency="BTCUSDT"
asset1="BTC"
asset2="USDT"
precisionasset1=6 #depends on the asset
precisionasset2=6 #depends on the asset
trader_fee=0.05 # in % obs, changes over time, how to get automatically?
db_name="binance.db"
db_table="candles_USDT_BTC"

# Start Client
client = Client(api_key, api_secret)
bm = BinanceSocketManager(client)
#conn_key = bm.start_kline_socket(currency, ticker, interval=client.KLINE_INTERVAL_1MINUTE)
#bm.start() # Start ticker socket

# Check Warmup Period
b_warmedup=False
warmupperiod= 120*60*60 #60 hours - in seconds - depends on strategy
#warmup(exchange, currency, warmupperiod)
# Check bought/sold status
balance = client.get_asset_balance(asset='USDT')
if float(balance["free"])<1.0: # this value depends for each asset - logic using USDT
    market_status="bought"
else:
    market_status="sold"

balance = client.get_asset_balance(asset='BTC')
precision=6
amt_str=math.floor(float(balance["free"]) * 10**precision) / 10**precision
amt_str = "{:0.0{}f}".format(amt_str, precision)
# read asset2 balance
balance_t0 = client.get_asset_balance(asset='USDT')
balance_t0 = float(balance_t0["free"])
order = client.order_market_sell(symbol='BTCUSDT', quantity=amt_str)
# read asset2 balance and calculate the price
balance_t1 = client.get_asset_balance(asset='USDT')
balance_t1=float(balance_t1["free"])
price=(balance_t1-balance_t0)/(1-trader_fee/100)/float(amt_str)
# Buy or sell according to strategy
b_realtrade=False
#db.close()
#reactor.stop()

# TO DO
# HANDLE ERROR WHEN SELLING - BinanceAPIException: APIError(code=-1013): Filter failure: LOT_SIZE
# ripple only allows integers
# BinanceAPIException: APIError(code=-2010): Account has insufficient balance for requested action.
# ReadTimeout: HTTPSConnectionPool(host='api.binance.com', port=443): Read timed out. (read timeout=10)
