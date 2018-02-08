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

table="candles_USD_BCH"
#table="candles_USD_BCH"
# Command to write columns

#cursor.execute('PRAGMA table_info({})'.format(table))
#
#colunas = [tupla[1] for tupla in cursor.fetchall()]
#print('Colunas:', colunas)  

t1 = time.mktime(datetime.datetime(2017, 12, 1, 7, 0, 0, 0).timetuple())
t2 = time.mktime(datetime.datetime(2018, 2, 5, 21, 19, 0, 0).timetuple())


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
outdecision_table=[]
for i in range(len(outcandles)):
    outdecision_table.append("")
    for j in range(len(decision_table)):
        if candles[j,0]>outcandles[i,0]:
            outdecision_table[i]=decision_table[j]
            break

# Backtest - Calculate transactions
backtest_results=backtest_calc(candles, candles, decision_table)

# Post-processing
# Select timestamp to plot
t1 = time.mktime(datetime.datetime(2018, 1, 6, 0, 0, 0, 0).timetuple())
t2 = time.mktime(datetime.datetime(2018, 1, 23, 21, 0, 0, 0).timetuple())

# Calculate Indicators - EMA, DMI, Stoch
#short_ema=talib.EMA(outcandles[:,3], timeperiod=9)
#long_ema=talib.EMA(outcandles[:,3], timeperiod=20)
#long_ema=talib.SMA(outcandles[:,3], timeperiod=100)

leadsine, sine, trendline, trending=trendmode(outcandles)
smoothprice=talib.WMA(outcandles[:,3], timeperiod=4)

plus_di=talib.PLUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) # PLUS_DI(high, low, close, timeperiod=14)
minus_di=talib.MINUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) #MINUS_DI(high, low, close, timeperiod=14)

# Write Graph
html_path="teste.html"

# Convert indicators
ooutcandles=[]
ooutdecision_table=[]
osmoothprice=[]
otrendline=[]
oplus_di=[]
ominus_di=[]
otrending=[]
oleadsine=[]
osine=[]
for i in range(len(outcandles)):
    if outcandles[i,0]>=t1 and outcandles[i,0]<=t2:
        ooutcandles.append(outcandles[i,:])
        ooutdecision_table.append(outdecision_table[i])
        osmoothprice.append(smoothprice[i])
        otrendline.append(trendline[i])
        oplus_di.append(plus_di[i])
        ominus_di.append(minus_di[i])
        otrending.append(trending[i])
        oleadsine.append(leadsine[i])
        osine.append(sine[i])

ooutcandles=np.array(ooutcandles)
ooutdecision_table=np.array(ooutdecision_table)
osmoothprice=np.array(osmoothprice)
otrendline=np.array(otrendline)
oplus_di=np.array(oplus_di)
ominus_di=np.array(ominus_di)
otrending=np.array(otrending)     
oleadsine=np.array(oleadsine)
osine=np.array(osine)
# Generate html
generate_buy_sell_html(ooutcandles,
        ooutdecision_table,
        oplus_di,
        ominus_di,
        [[oplus_di, ominus_di,'Plus DI', 'Minus DI']],
        html_path,otrending)

# Write Backtest Results - Buy N HOld, profit for each transaction 

#for transaction in backtest_results:
for i in backtest_results:
    print(i)
buynhold=outcandles[-1,3]/outcandles[warmup,3]
strategyratio=backtest_results[-1][1]/1000 #1000 is the initial investment
print("Backtest Results: \n")
print("Buy and Hold: %s \n"%(buynhold))
print("Strategy Profit: %s"%(strategyratio))
print("Profit/Buy 'n Hold: %s"%str(strategyratio/buynhold))
backtest_results=np.array(backtest_results)
print("Maximum Cash: %s"%str(max(backtest_results[:,1].astype(float))))
