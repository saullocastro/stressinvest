from aux_functions import convert_candle
import talib
import math

def strategy_ema(candles, outperiod):
    # Define the decision period - in minutes
    decision_period=30
    
    # Convert candles to decision period
    outcandles=convert_candle(candles,decision_period*60)
    
    # Calculate indicators - EMA, DMI
    short_ema=talib.EMA(outcandles[:,3], timeperiod=9)
    long_ema=talib.EMA(outcandles[:,3], timeperiod=20)
    ema_diff=short_ema-long_ema
    
    plus_di=talib.PLUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) # PLUS_DI(high, low, close, timeperiod=14)
    minus_di=talib.MINUS_DI(outcandles[:,4], outcandles[:,1], outcandles[:,3], timeperiod=14) #MINUS_DI(high, low, close, timeperiod=14)
    dm_diff=plus_di-minus_di
    
    # Iterate over the candles and determine buy/sell
    decision_table=[]
    for i in range(len(outcandles)):
        if math.isnan(ema_diff[i]) or math.isnan(dm_diff[i]):
            decision_table.append("") # do nothing
        else:
            decision_table.append("")
            if ema_diff[i]>0 and ema_diff[i-1]<0: # if crossed from below, buys
                if dm_diff[i]>0: # confirm with directional movement
                    decision_table[i]="buy"
            elif ema_diff[i]<0 and ema_diff[i-1]>0: #if cross from above, sells
                if dm_diff[i]<0: # confirm with directional movement
                    decision_table[i]="sell"
                
        # Check if it has crossed the ema_diff
        
    
    return decision_table