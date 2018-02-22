import os
import sys
import time
import getpass
import math
import sqlite3
import datetime
from functools import partial

import numpy as np
from binance.client import Client
from binance.websockets import BinanceSocketManager

sys.path.append('.')
from strategy import strategy


class TradeData(object):
    def __init__(self):
        self.b_realtrade = True
        self.b_warmedup = False
        self.warmupperiod = 120*60*60 #60 hours - in seconds - depends on strategy
        self.b_trade = False
        self.market_status = None
        self.exchange = "BINANCE" # To be Implemented Additional Exchanges
        self.currency = "BTCUSDT"
        self.asset1 = "BTC"
        self.asset2 = "USDT"
        self.precisionasset1 = 6 #depends on the asset
        self.precisionasset2 = 6 #depends on the asset
        self.trader_fee = 0.05 # in % obs, changes over time, how to get automatically?
        self.db_name = "binance.db"
        self.db_table = "candles_USDT_BTC"
        self.candle_size = 1*60*60

#------------------------------------------------------------------------------
def ticker(msg, td):
    # ticker
    #print(msg)
    #id, start, open, high, low, close, , vwp, volume, trades
    s_start = msg['k']['t']/1000 #s
    s_open = msg['k']['o']
    s_high = msg['k']['h']
    s_low = msg['k']['l']
    s_close = msg['k']['c']
    s_vwp = msg['k']['c'] #average weighted price - will assume close price
    s_volume = msg['k']['v']
    s_trades = msg['k']['t']
    final_bar = msg['k']['x'] # if it is the final bar, insert in the database
    if final_bar: # candle has formed
        db = sqlite3.connect(td.db_name)
        cursor = db.cursor()
        cmd = "INSERT INTO candles_USDT_BTC (start, open, high, low, close, vwp, volume, trades) VALUES ("
        cmd += str(s_start)
        cmd += "," + str(s_open)
        cmd += "," + str(s_high)
        cmd += "," + str(s_low)
        cmd += "," + str(s_close)
        cmd += "," + str(s_vwp)
        cmd += "," + str(s_volume)
        cmd += "," + str(s_trades)
        cmd += ");"
        cursor.execute(cmd)
        db.commit()
        db.close()
    # call strategy
    if td.b_warmedup:
        db = sqlite3.connect(td.db_name)
        cursor = db.cursor()

        t1=time.time()
        t1-=t1%60-60 # last full minute candle
        t0=t1-120*60*60 #maximum number of data used - 120hr

        aux_str = 'SELECT * FROM '
        aux_str += td.db_table
        aux_str += ' WHERE start BETWEEN %s AND %s' %(str(t0), str(t1))

        cursor.execute(aux_str)
        db_candles = cursor.fetchall()
        db_candles.sort(key=lambda tup: tup[1]) # Order the results by timestamp
        db_candles = np.array(db_candles)
        decision = strategy(db_candles, "ema", td)
        # call trade
        try:
            trade(decision)
        except:
            pass
#------------------------------------------------------------------------------
def warmup(td):
    t1 = time.time()
    t1 -= t1 % 60-60 # last full minute candle
    t0 = t1-td.warmupperiod

    if not os.path.isfile(td.db_name):
        print('Creating database...')
        db = sqlite3.connect(td.db_name)
        cursor = db.cursor()
        #id, start, open, high, low, close, , vwp, volume, trades
        cmd = ("""CREATE TABLE %s (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start INTEGER,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            vwp REAL NOT NULL,
            volume REAL NOT NULL,
            trades INTEGER NOT NULL
            )""" % td.db_table)
        cursor.execute(cmd)
        db.commit()
        db.close()

    # Import DB results
    db = sqlite3.connect(td.db_name)
    cursor = db.cursor()
    aux_str = 'SELECT * FROM '
    aux_str += td.db_table
    aux_str += ' WHERE start BETWEEN %s AND %s' %(str(t0), str(t1))

    cursor.execute(aux_str)
    db_candles = cursor.fetchall()
    db_candles.sort(key=lambda tup: tup[1]) # Order the results by timestamp
    db_candles = np.array(db_candles)

    # Scan the imported results to find gaps
    v_gaps = []
    candle = None
    for i, candle in enumerate(db_candles):
        if i == 0: # check first candle
            if candle[1]-t0 > 60: # there is a gap
                v_gaps.append([t0, candle[1]])
        if i > 0: # check the others
            if candle[1]-db_candles[i-1][1] > 60: # there is a gap
                v_gaps.append([candle[1], db_candles[i-1][1]])

    if candle is not None:
        # check last candle
        if t1 - candle[1] > 60: # there is a gap
            v_gaps.append([candle[1], t1])

    v_candles = []
    for gap in v_gaps:
        # check if the gap is above 500 candles
        startTime = gap[0]
        endTime = gap[1]
        v_aux = []
        if (endTime-startTime)/60>500:
            aux_endTime = startTime
            for i in range(int(math.floor((endTime-startTime)/60/500))):
                aux_startTime = aux_endTime
                aux_endTime = aux_startTime+500*60
                if aux_endTime > endTime:
                    aux_endTime = endTime
                v_aux.append([aux_startTime, aux_endTime])
        else:
            v_aux.append([startTime, endTime])
        # Get the candles
        for aux in v_aux:
            startTime = int(aux[0])*1000 #binance uses ms
            endTime = int(aux[1])*1000 #binance uses ms
            candles = client.get_klines(symbol=td.currency, interval=Client.KLINE_INTERVAL_1MINUTE, limit=500, startTime=startTime, endTime=endTime)
            v_candles.append(candles)

    # add candles to the database
    for list_candle in v_candles:
        for candle in list_candle:
            s_start = candle[0]/1000 #s
            s_open = candle[1]
            s_high = candle[2]
            s_low = candle[3]
            s_close = candle[4]
            s_vwp = candle[4] #average weighted price - will assume close price
            s_volume = candle[5]
            s_trades = candle[8]
            cmd = "INSERT INTO " + str(td.db_table)+" (start, open, high, low, close, vwp, volume, trades) VALUES ("
            cmd += str(s_start)
            cmd += ","+str(s_open)
            cmd += ","+str(s_high)
            cmd += ","+str(s_low)
            cmd += ","+str(s_close)
            cmd += ","+str(s_vwp)
            cmd += ","+str(s_volume)
            cmd += ","+str(s_trades)
            cmd += ");"
            cursor.execute(cmd)
    db.commit()
    # Delete duplicate timestamp
    cmd = "DELETE FROM " + td.db_table + " WHERE rowid NOT IN (SELECT MAX(rowid) FROM " + td.db_table + " GROUP BY start);"
    cursor.execute(cmd)
    db.commit()
    db.close()
    td.b_warmedup = True
#------------------------------------------------------------------------------
def trade(decision):
    if td.b_realtrade:
        if decision == "buy":
            # get asset 2 balance to buy everything
            balance = client.get_asset_balance(asset=td.asset2)
            amt_str = math.floor(float(balance["free"]) * 10**td.precisionasset2) / 10**td.precisionasset2
            amt_str = "{:0.0{}f}".format(amt_str, td.precisionasset2)
            # read asset1 balance
            balance_t0 = client.get_asset_balance(asset=td.asset1)
            balance_t0 = float(balance_t0["free"])
            order = client.order_market_buy(symbol=td.currency, quantity=amt_str)
            # read asset1 balance and calculate the price
            balance_t1 = client.get_asset_balance(asset=td.asset1)
            balance_t1 = float(balance_t1["free"])
            price = float(amt_str)/(balance_t1-balance_t0)/(1.-td.trader_fee/100.)
            fee = float(amt_str)*td.trader_fee/100.
        if decision == "sell":
            # get asset 1 balance to sell everything
            balance = client.get_asset_balance(asset=td.asset1)
            amt_str = math.floor(float(balance["free"]) * 10**td.precisionasset1) / 10**td.precisionasset1
            amt_str = "{:0.0{}f}".format(amt_str, td.precisionasset1) #amount to be sold
            # read asset2 balance to calculate the price
            balance_t0 = client.get_asset_balance(asset=td.asset2)
            balance_t0 = float(balance_t0["free"])
            # Market Order - TODO - EXCEPTION HANDLING if fails
            order = client.order_market_sell(symbol=td.currency, quantity=amt_str) # if order["status"]=="FILLED" order is finished
            # read asset2 balance and calculate the price
            balance_t1 = client.get_asset_balance(asset=td.asset2)
            balance_t1 = float(balance_t1["free"])
            price = (balance_t1-balance_t0)/(1.-td.trader_fee/100.)/float(amt_str)
            fee = amt_str*price*td.trader_fee/100. # fee always in asset2
        # Log Trade
        #['Action','Balance Asset 1','Balance Asset 2','Paid Fee','Price','Date']
        balance_1 = client.get_asset_balance(asset=td.asset1)["free"]
        balance_2 = client.get_asset_balance(asset=td.asset2)["free"]
        if decision != "":
            with open("log.txt", 'a') as f:
                aux = decision
                aux += ", "+balance_1
                aux += ", "+balance_2
                aux += ", "+str(fee)
                when = order["transactTime"]
                when = datetime.datetime.fromtimestamp(float(when)).strftime('%m/%d/%Y %H:%M:%S')
                f.write(aux)
    else:
        if decision!="":
            print("decision")

#------------------------------------------------------------------------------
# Main Program
# Get API Keys
api_key = getpass.getpass(prompt="Insert API KEY: ")
api_secret = getpass.getpass(prompt="Insert API SECRET: ")


# Start Client
client = Client(api_key, api_secret)
bm = BinanceSocketManager(client)
td = TradeData()

ticker_partial = partial(ticker, td=td)
conn_key = bm.start_kline_socket(td.currency, ticker_partial, interval=client.KLINE_INTERVAL_1MINUTE)
bm.start() # Start ticker socket

# Check Warmup Period
warmup(td)
# Check bought/sold status
balance = client.get_asset_balance(asset=td.asset2)
if float(balance["free"]) < 10.: # this value depends for each asset - logic using USDT
    td.market_status = "bought"
else:
    td.market_status = "sold"

# TO DO
# HANDLE ERROR WHEN SELLING - BinanceAPIException: APIError(code=-1013): Filter failure: LOT_SIZE
# ripple only allows integers
# BinanceAPIException: APIError(code=-2010): Account has insufficient balance for requested action.
# ReadTimeout: HTTPSConnectionPool(host='api.binance.com', port=443): Read timed out. (read timeout=10)
