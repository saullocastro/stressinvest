# Backtest
# Modules
import numpy as np
import sqlite3
import datetime
import time
import talib
import math
from generate_buy_sell_html import generate_buy_sell_html
from strategy import strategy_ema
from strategy import strategy_stoch
from strategy import strategy_hilbert, strategy_mult_hilbert
from aux_functions import convert_candle, trendmode
from backtest_calc import backtest_calc

# Read Database
conn = sqlite3.connect('bitfinex_0.1.db')

cursor = conn.cursor()

# Command to check which databases are available

#cursor.execute("""
#SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
#""")
#
#for tabela in cursor.fetchall():
#    print("%s" % (tabela))

table="candles_USD_BTC"
#table="candles_USD_BCH"
# Command to write columns

#cursor.execute('PRAGMA table_info({})'.format(table))
#
#colunas = [tupla[1] for tupla in cursor.fetchall()]
#print('Colunas:', colunas)  

t1 = time.mktime(datetime.datetime(2017, 12, 1, 7, 0, 0, 0).timetuple())
#t2 = time.mktime(datetime.datetime(2017, 12, 20, 17, 0, 0, 0).timetuple())

#t1 = time.mktime(datetime.datetime(2018, 1, 6, 0, 0, 0, 0).timetuple())
#t1 = time.mktime(datetime.datetime(2018, 1, 06, 0, 0, 0, 0).timetuple())

t2 = time.mktime(datetime.datetime(2018, 1, 23, 21, 19, 0, 0).timetuple())


# Command to read database        
aux_str='SELECT * FROM '
aux_str+=table
aux_str+=' WHERE start BETWEEN %s AND %s' %(str(t1), str(t2))
cursor.execute(aux_str)

candles=np.array(cursor.fetchall()) #id, start, open, high, low, close, , vwp, volume, trades
#candles=candles[:, [1,2,3,4,5,7]]# simplify to timestamp, open, high, low, close, volume
candles=candles[:, [1,4,2,5,3,7]]# simplify to timestamp, low, open, close, high, volume

#Warmup Period
warmup=63
# Select timestamp
initial_time=1
final_time=1


# Pass Database to strategy - will return buy/sell points
outperiod=1*60*60 #seconds

decision_table=strategy_hilbert(candles, outperiod)
decision_table=strategy_mult_hilbert(candles, outperiod, outperiod)

#decision_table=strategy_ema(candles, outperiod)
#decision_table=strategy_stoch(candles, outperiod)
# Convert Candles
outcandles=convert_candle(candles,outperiod)
    
# Backtest - Calculate transactions
backtest_results=backtest_calc(candles, candles, decision_table)

# Post-processing

# Calculate Indicators - EMA, DMI, Stoch
short_ema=talib.EMA(outcandles[:,3], timeperiod=9)
long_ema=talib.EMA(outcandles[:,3], timeperiod=20)
long_ema=talib.SMA(outcandles[:,3], timeperiod=100)

leadsine, sine, trendline, trending=trendmode(outcandles)
#short_ema=leadsine
#long_ema=trendline
#short_ema=talib.WMA(outcandles[:,3], timeperiod=4)
#long_ema=talib.HT_TRENDLINE(outcandles[:,3])

plus_di=talib.PLUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) # PLUS_DI(high, low, close, timeperiod=14)
minus_di=talib.MINUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) #MINUS_DI(high, low, close, timeperiod=14)

slowk, slowd = talib.STOCH(outcandles[:,4], outcandles[:,1], outcandles[:,3], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
#slowk, slowd=  talib.HT_SINE(outcandles[:,3])
#plus_di=talib.HT_DCPHASE(outcandles[:,3])
#short_ema=plus_di
#long_ema=minus_di
#slowk, slowd = talib.STOCHRSI(outcandles[:,3], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
# Write Graph
html_path="teste.html"
#trending=talib.HT_TRENDMODE(outcandles[:,3])

generate_buy_sell_html(outcandles,
        decision_table,
        short_ema,
        long_ema,
        [[plus_di, minus_di,'Plus DI', 'Minus DI'],
        [slowk, slowd,'Slow K', 'Slow D']],
        html_path,trending)
# Write Backtest Results - Buy N HOld, profit for each transaction 

#for transaction in backtest_results:
for i in backtest_results:
    print(i)
#print(outcandles[0,3])
#print(outcandles[-1,3])
#print(outcandles[-1,3]/outcandles[0,3])   
buynhold=outcandles[-1,3]/outcandles[warmup,3]
strategyratio=backtest_results[-1][1]/1000 #1000 is the initial investment
print("Backtest Results: \n")
print("Buy and Hold: %s \n"%(buynhold))
print("Strategy Profit: %s"%(strategyratio))
#
#    print i
#print(trending[-1])
#print(vec_trendmode[-1])
print("Profit/Buy 'n Hold: %s"%str(strategyratio/buynhold))
backtest_results=np.array(backtest_results)
print("Maximum Cash: %s"%str(max(backtest_results[:,1].astype(float))))