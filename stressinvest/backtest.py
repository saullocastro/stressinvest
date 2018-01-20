# Backtest
# Modules
import numpy as np
import sqlite3
import datetime
import talib
import math

from strategy import strategy_ema
from aux_functions import convert_candle

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

# Command to write columns

#cursor.execute('PRAGMA table_info({})'.format(table))
#
#colunas = [tupla[1] for tupla in cursor.fetchall()]
#print('Colunas:', colunas)  

# Command to read database        
aux_str='SELECT * FROM '
aux_str+=table+';'
cursor.execute(aux_str)

candles=np.array(cursor.fetchall()) #id, start, open, high, low, close, , vwp, volume, trades
#candles=candles[:, [1,2,3,4,5,7]]# simplify to timestamp, open, high, low, close, volume
candles=candles[:, [1,4,2,5,3,7]]# simplify to timestamp, low, open, close, high, volume

# Pass Database to strategy - will return buy/sell points
outperiod=30*60 #seconds

decision_table=strategy_ema(candles, outperiod)

# Backtest - Calculate transactions


# Post-processing

# Convert Candles
outcandles=convert_candle(candles,30*60)

# Calculate Indicators - EMA, DMI, Stoch
short_ema=talib.EMA(outcandles[:,3], timeperiod=9)
long_ema=talib.EMA(outcandles[:,3], timeperiod=20)

plus_di=talib.PLUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) # PLUS_DI(high, low, close, timeperiod=14)
minus_di=talib.MINUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) #MINUS_DI(high, low, close, timeperiod=14)

slowk, slowd = talib.STOCH(outcandles[:,4], outcandles[:,1], outcandles[:,3], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
# Write Graph

# Write Backtest Results - Buy N HOld, profit for each transaction 