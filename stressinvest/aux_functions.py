import numpy as np
from math import atan, cos, sin

def convert_candle(candles, outcandleperiod):
    outcandles=[]
    initcandleperiod=int(candles[1,0]-candles[0,0]) #seconds
    period=int(outcandleperiod/initcandleperiod)
    # simplify to timestamp, low, open, close, high, volume
    for i in range(int(len(candles)/period)):
        period_candles=candles[(period*i):(period*(i+1)),:]
        candle_timestamp=period_candles[0,0] # Timestamp is the initial timestamp
        candle_open=period_candles[0,2] # The open value is the open from the initial timestamp
        candle_high=period_candles[:,4].max() # The high value is the maximum of the highs 
        candle_low=period_candles[:,1].min() # The low value is the minimum of the lows
        candle_close=period_candles[-1,3] # The close value is the close of the last timestamp
        candle_volume=period_candles[:,5].sum() # The volume is the sum of the volumes
        outcandles.append([candle_timestamp,candle_low, candle_open, candle_close, candle_high, candle_volume])
    
    outcandles=np.array(outcandles)
    return outcandles

def trendmode(candles):
    # constants
    pi=3.141516
    # vector initialization
    smooth=[]
    detrender=[]
    Q1=[]
    I1=[]
    jI=[]
    jQ=[]
    I2=[]
    Q2=[]
    Re=[]
    Im=[]
    period=[]
    smoothperiod=[]
    smoothprice=[]
    dcperiod=[]
    dcphase=[]
    itrend=[]
    trendline=[]
    sinediff=[]
    leadsine=[]
    sine=[]
    daysintrend=0
    trending=[]   # output
    price=(candles[:,1]+candles[:,4])/2. # prices =(H+L)/2
#    price=candles[:,3] # prices =(H+L)/2
    # Iterate over the candles and determine the trending
    for i in range(len(candles)):
        trending.append(1) # Assume trending
        
        # Initialize
        smooth.append(0)
        detrender.append(0)
        Q1.append(0)
        I1.append(0)
        jI.append(0)
        jQ.append(0)
        I2.append(0)
        Q2.append(0)
        Re.append(0)
        Im.append(0)
        period.append(6)
        smoothperiod.append(6)
        smoothprice.append(0)
        dcperiod.append(0)
        dcphase.append(0)
        itrend.append(0)
        trendline.append(0)
        sinediff.append(0)
        leadsine.append(0)
        sine.append(0)
            
        if i>4: #warmup period
            smooth[i]=((4.*price[i]+3.*price[i-1]+2.*price[i-2]+price[i-3])/10.)
        if i>4+7: #warmup period
            detrender[i]=((0.0962*smooth[i]+0.5769*smooth[i-2]-0.5769*smooth[i-4]-0.0962*smooth[i-6])*(0.075*period[i-1]+0.54))
        
        # Compute InPhase and Quadrature components
        if i>4+7+7: #warmup
            Q1[i]=((0.0962*detrender[i]+0.5769*detrender[i-2]-0.5769*detrender[i-4]-0.0962*detrender[i-6])*(0.075*period[i-1]+0.54))
            I1[i]=(detrender[i-3])

        # Advance the phase of I1 and Q1 by 90 degrees
        if i>4+7+7+7: #warmup
            jI[i]=((0.0962*I1[i]+0.5769*I1[i-2]-0.5769*I1[i-4]-0.0962*I1[i-6])*(0.075*period[i-1]+0.54))
            jQ[i]=((0.0962*Q1[i]+0.5769*Q1[i-2]-0.5769*Q1[i-4]-0.0962*Q1[i-6])*(0.075*period[i-1]+0.54))

        # Phasor addition for 3 bar averaging
        if i>4+7+7+7: #warmup
            I2[i]=(I1[i]-jQ[i])
            Q2[i]=(Q1[i]+jI[i])

        # Smooth the I and Q components before applying the discriminator
        if i>4+7+7+7+1: #warmup
            I2[i] = 0.2*I2[i]+0.8*I2[i-1]
            Q2[i] = 0.2*Q2[i]+0.8*Q2[i-1]

        # Homodyne Discriminator
        if i>4+7+7+7+1: #warmup
            Re[i]=(I2[i]*I2[i-1] + Q2[i]*Q2[i-1])
            Im[i]=(I2[i]*Q2[i-1] - Q2[i]*I2[i-1])
        if i>4+7+7+7+1+1: #warmup
            Re[i] = 0.2*Re[i] + 0.8*Re[i-1]
            Im[i] = 0.2*Im[i] + 0.8*Im[i-1]
            if Im[i] != 0 and Re[i] != 0:
                period[i]=(360./(atan(Im[i]/Re[i])*180./pi))
            period[i]=min(period[i], 1.5*period[i-1], 50.) # Limit max new period by 1.5*old period or 50
            period[i]=max(period[i], period[i-1]/1.5, 6.) # Limit min new period by old period/1.5 or 6
        if i>4+7+7+7+1+1+1: #warmup
            period[i]=0.2*period[i] + 0.8*period[i-1]
        if i>4+7+7+7+1+1+1+1: #warmup
            smoothperiod[i]=(0.33*period[i]+0.67*smoothperiod[i-1])
            
        # Compute Dominant Cycle Phase
        if i>4+7+7+7+1+1+1+1+4: #warmup
            smoothprice[i]=((4.*price[i]+3.*price[i-1]+2.*price[i-2]+price[i-3])/10.)
            dcperiod[i]=(int(smoothperiod[i]+0.5))
        
        if i>50: #warmup
            realpart=0.
            imagpart=0.
            for j in range(dcperiod[i]):
                imagpart=imagpart+cos(2.*pi*j/dcperiod[i])*smoothprice[i-j]
                realpart=realpart+sin(2.*pi*j/dcperiod[i])*smoothprice[i-j]
            
            dcphase[i]=(0)
            if abs(imagpart)>0.:
                dcphase[i]=atan(realpart/imagpart)*180./pi
            if abs(imagpart)<=0.01:
                if realpart<0.:
                    dcphase[i] -= 90.
                elif realpart>0.:
                    dcphase[i] += 90.
            dcphase[i]=dcphase[i]+90.
        
        # Compensate for one bar lag of the Weighted Moving Average
            dcphase[i]=dcphase[i]+360./smoothperiod[i]
            
            if imagpart<0.:
                dcphase[i]=dcphase[i]+180.
            if dcphase[i]>315.:
                dcphase[i]=dcphase[i]-360.
        # Compute Trendline as simple average over the measured dominant cycle period
            itrend[i]=(0.)
            factor=0.97
            intperiod=(int(factor*smoothperiod[i]+0.5))
            for j in range(intperiod):
                itrend[i]=itrend[i]+price[i-j]
            if dcperiod[i]>0:
                itrend[i]=itrend[i]/intperiod
            trendline[i]=((4.*itrend[i]+3.*itrend[i-1]+2.*itrend[i-2]+itrend[i-3])/10.)
            if i<63: #warmup
                trendline[i]=price[i]
        if i>62:
            # Check Trend Mode
            leadsine[i]=sin((dcphase[i]+45.)*pi/180.)
            sine[i]=sin(dcphase[i]*pi/180.)
            sinediff[i]=(sin(dcphase[i]*pi/180.)-sin((dcphase[i]+45.)*pi/180.))
            # Measure in trend from last crossing of the Sinewave Indicator lines
            bool1 = sine[i]>leadsine[i] and sine[i-1]<=leadsine[i-1]
            bool2 = sine[i]<leadsine[i] and sine[i-1]>=leadsine[i-1]
            if (bool1 or bool2):
                daysintrend=0
                trending[i]=0
            daysintrend+=1
            if daysintrend<0.5*smoothperiod[i]:
                trending[i]=0
            # Cycle Mode if delta phase is +/- 50% of dominant cycle change of phase
            if smoothperiod != 0. and (dcphase[i]-dcphase[i-1]>.67*360./smoothperiod[i]) and (dcphase[i]-dcphase[i-1]<1.5*360./smoothperiod[i]):
                trending[i]=0
            # Trend mode if prices are widely separated from the Trendline
            if abs((smoothprice[i]-trendline[i])/trendline[i])>=0.03:
                trending[i]=1               
    return np.array(leadsine),  np.array(sine),  np.array(trendline), trending