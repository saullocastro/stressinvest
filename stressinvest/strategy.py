from aux_functions import convert_candle
import talib


def strategy_ema(candles, outperiod):
    # Define the decision period - in minutes
    decision_period=30
    
    # Convert candles to decision period
    outcandles=convert_candle(candles,decision_period*60)
    
    
    # Calculate indicators - EMA, DMI, 
    