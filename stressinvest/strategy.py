from aux_functions import convert_candle, trendmode
import talib
import math
import numpy as np

def strategy_ema(candles, outperiod):
    # Define the decision period - in minutes
    decision_period=outperiod
    
    # Convert candles to decision period
    outcandles=convert_candle(candles,decision_period)
    
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
                #if dm_diff[i]>0: # confirm with directional movement
                decision_table[i]="buy"
            elif ema_diff[i]<0 and ema_diff[i-1]>0: #if cross from above, sells
                #if dm_diff[i]<0: # confirm with directional movement
                decision_table[i]="sell"
                
        # Check if it has crossed the ema_diff
        
    
    return decision_table

def strategy_stoch(candles, outperiod):
    # Define the decision period - in minutes
    decision_period=outperiod
    
    # Convert candles to decision period
    outcandles=convert_candle(candles,decision_period)
    
    # Calculate indicators - Stochastic
    slowk, slowd = talib.STOCH(outcandles[:,4], outcandles[:,1], outcandles[:,3], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    #slowk, slowd=talib.STOCHRSI(outcandles[:,3], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
    upperbound=80
    lowerbound=20
    # Iterate over the candles and determine buy/sell
    decision_table=[]

    for i in range(len(outcandles)):
        if math.isnan(slowk[i]):
            decision_table.append("") # do nothing
        else:
            decision_table.append("")
            if slowk[i]>lowerbound and slowk[i-1]<lowerbound: # if crossed from below, buys
                #if dm_diff[i]>0: # confirm with directional movement
                decision_table[i]="buy"
            elif slowk[i]<upperbound and slowk[i-1]>upperbound: #if cross from above, sells
                #if dm_diff[i]<0: # confirm with directional movement
                decision_table[i]="sell"
            #elif slowk[i]<lowerbound and slowk[i-1]>lowerbound: # if crossed from above the lowerbound, sells
                #if dm_diff[i]>0: # confirm with directional movement
            #    decision_table[i]="sell"
            #elif slowk[i]<upperbound and slowk[i-1]>upperbound: #if cross from below the upperbound, buys
                #if dm_diff[i]<0: # confirm with directional movement
            #    decision_table[i]="buy"                
        # Check if it has crossed the ema_diff
        
    
    return decision_table


def strategy_hilbert(candles, outperiod):
    # Define the decision period - in minutes
    decision_period=outperiod

    # Convert candles to decision period
    outcandles=convert_candle(candles, decision_period)
    
    # Calculate indicators - SmoothedPrice
    smoothprice=talib.WMA(outcandles[:,3], timeperiod=4)
    leadsine, sine, trendline, trending=trendmode(outcandles)

    #trendline=talib.HT_TRENDLINE(outcandles[:,3])

    trenddiff=smoothprice-trendline
    
#    short_ema=talib.EMA(outcandles[:,3], timeperiod=5)
#    long_ema=talib.EMA(outcandles[:,3], timeperiod=20)
#    trenddiff=smoothprice-long_ema
    
    #sine, leadsine = talib.HT_SINE(outcandles[:,3])
    sinediff=leadsine-sine   

    # Iterate over the candles and determine buy/sell
    decision_table=[]
    for i in range(len(outcandles)):
        if math.isnan(smoothprice[i]) or math.isnan(trendline[i]) or math.isnan(sine[i]):
            decision_table.append("") # do nothing
        else:
            decision_table.append("")

            if trending[i]:
#            if True:
                if trending[i-1]==0: # if the previous mode was Cycle
                    if smoothprice[i]>=trendline[i]: # Buy if the price is higher
                        decision_table[i]="buy"
                    else: #Sell if the price is lower
                        decision_table[i]="sell"
                if trenddiff[i]>0 and trenddiff[i-1]<=0: # If price crosses over trendline - buys
                    decision_table[i]="buy"
                elif trenddiff[i]<0 and trenddiff[i-1]>=0: # If price crosses down trendline - sells
                    decision_table[i]="sell"   
#            else:
#                if sinediff[i]>0 and sinediff[i-1]<=0: # If price crosses over trendline - buys
#                    decision_table[i]="buy"
#                elif sinediff[i]<0 and sinediff[i-1]>=0: # If price crosses down trendline - sells
#                    decision_table[i]="sell"              
        # Check if it has crossed the ema_diff
        
    
    return decision_table

def strategy_mult_hilbert(candles, long_period, short_period):
    
    # Convert candles to decision period
    shortcandles=convert_candle(candles, short_period)
    longcandles=convert_candle(candles, long_period)
    
    # Calculate indicators for long period - SmoothedPrice
    longsmoothprice=talib.WMA(longcandles[:,3], timeperiod=4)
    
    longleadsine, longsine, longtrendline, longtrending=trendmode(longcandles)

    longtrenddiff=longsmoothprice-longtrendline
    longsinediff=longleadsine-longsine
    
    longsma=talib.SMA(longcandles[:,3], timeperiod=50) #used to determine the trending direction
    # Calculate indicators for short period
    shortsmoothprice=talib.WMA(shortcandles[:,3], timeperiod=4)
    shortleadsine, shortsine, shorttrendline, shorttrending=trendmode(shortcandles)

    shorttrenddiff=shortsmoothprice-shorttrendline
    shortsinediff=shortleadsine-shortsine
    
#    short_ema=talib.EMA(outcandles[:,3], timeperiod=5)
#    long_ema=talib.EMA(outcandles[:,3], timeperiod=20)
#    trenddiff=smoothprice-long_ema    

    # Iterate over the candles and determine buy/sell
    decision_table=[]
    
    # Status variables
    advise=""
    moneystatus="sold" # starts sold
    trendingdirection=""
    for i in range(len(candles)):
        # Wait warmup period
        if i<long_period/60*63:
            decision_table.append("") # do nothing
        else:
            decision_table.append("")
            # Determine current long period
            lindex=0
            while longcandles[lindex,0]<candles[i,0]:
                lindex+=1
                if lindex==len(longcandles)-1:
                    break
            lindex-=1 #only the previous candle has been formed
            
            # Determine current short period
            sindex=0
            while shortcandles[sindex,0]<candles[i,0]:
                sindex+=1
                if sindex==len(shortcandles)-1:
                    break
            sindex-=1 #only the previous candle has been formed

            # check trend by the long period
            trend=longtrending[lindex]
            if lindex>0:
                if (longsma[lindex]-longsma[lindex-1])/longsma[lindex-1]<0.01:
                    trendingdirection="down"
                else:
                    trendingdirection="up"
            if trend:
#            if True:
                if lindex>0:
                    if longtrending[lindex-1]==0: # if the previous mode was Cycle
                        if longsmoothprice[lindex]>=longtrendline[lindex] and moneystatus=="sold": # Buy if the price is higher
                            decision_table[i]="buy"
                            moneystatus="bought"
                        elif longsmoothprice[lindex]<longtrendline[lindex] and moneystatus=="bought": #Sell if the price is lower
                            decision_table[i]="sell"
                            moneystatus="sold"
                    if longtrenddiff[lindex]>0 and longtrenddiff[lindex-1]<=0 and moneystatus=="sold": # If price crosses over trendline - buys
                        decision_table[i]="buy"
                        moneystatus="bought"
                    elif longtrenddiff[lindex]<0 and longtrenddiff[lindex-1]>=0 and moneystatus=="bought": # If price crosses down trendline - sells
                        decision_table[i]="sell"   
                        moneystatus="sold"
            else:
                if shortsinediff[sindex]>0 and shortsinediff[sindex-1]<=0 and moneystatus=="sold": # If price crosses over trendline - buys
                    decision_table[i]="buy"
                    moneystatus="bought"
                elif shortsinediff[sindex]<0 and shortsinediff[sindex-1]>=0  and moneystatus=="bought": # If price crosses down trendline - sells
                    decision_table[i]="sell"
                    moneystatus="sold"        
    
    return decision_table