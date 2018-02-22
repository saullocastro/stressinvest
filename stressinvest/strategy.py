from aux_functions import convert_candle_db
import talib
#import math
#import numpy as np

def strategy(candles, market_status, strategy_type, args):
    if strategy_type=="ema":
        decision=strategy_ema(candles, market_status, args[0])
    return decision

def strategy_ema(candles, market_status, outperiod): 
    # Convert candles to period
    outcandles=convert_candle_db(candles,outperiod)
    
    # Calculate indicators - EMA, DMI
    short_ema=talib.EMA(outcandles[:,5], timeperiod=9)
    long_ema=talib.EMA(outcandles[:,5], timeperiod=20)
    ema_diff=short_ema-long_ema
    
    # Analyze indicator and take a decision
    decision=""
    if ema_diff[-1]>0 and ema_diff[-2]<0 and market_status=="sold": # if crossed from below, buys
        decision="buy"
    elif ema_diff[-1]<0 and ema_diff[-2]>0 and market_status=="bought": #if cross from above, sells
        decision="sell" 
    return decision