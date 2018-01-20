import numpy as np

def convert_candle(candles, outcandleperiod):
    outcandles=[]
    initcandleperiod=int(candles[1,0]-candles[0,0]) #seconds
    period=outcandleperiod/initcandleperiod
    
    for i in range(len(candles)/period):
        period_candles=candles[(period*i):(period*(i+1)),:]
        candle_timestamp=period_candles[0,0] # Timestamp is the initial timestamp
        candle_open=period_candles[0,1] # The open value is the open from the initial timestamp
        candle_high=period_candles[:,2].max() # The high value is the maximum of the highs 
        candle_low=period_candles[:,3].min() # The low value is the minimum of the lows
        candle_close=period_candles[-1,4] # The close value is the close of the last timestamp
        candle_volume=period_candles[:,5].sum() # The volume is the sum of the volumes
        outcandles.append([candle_timestamp, candle_open, candle_high, candle_low, candle_close, candle_volume])
    
    outcandles=np.array(outcandles)
    return outcandles