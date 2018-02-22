from math import cos, sin, exp
def dominant_cycle(candles):
    close = candles[:,5]
    
    # Using autocorrelation technique
    AvgLength = 3 # length over which the averaging is to be done, if 0, averaging length is equal to each lag
    
    # Variable initialization
    MaxPwr=0
    
    # List initialization
    HP=[]
    Filt=[]
    Corr=[]
    CosinePart=[]
    SinePart=[]
    SqSum=[]
    R=[]
    Pwr=[]
    DominantCycle=[] # Output
    
    for i in range(len(candles)):
        # Initialization
        HP.append(0.)
        Filt.append(0.)
        DominantCycle.append(48.)
        
        # Highpass filter cyclic components whose periods are shorter than 48 bars
        if i>2:
            alpha1 = (cos(.707*360/48)+sin(.707*360/48)-1)/(cos(.707*360/48))
            HP[i] = (1-alpha1/2)*(1-alpha1/2)*(close[i] - 2*close[i-1]+close[i-2])
            HP[i] += 2*(1-alpha1)*HP[i-1]-(1-alpha1)*(1-alpha1)*HP[i-2]
        
        # Smooth with a Super Smoother Filter from equation 3-3
        if i>2+2:
            a1 = exp(-1.414*3.14159/10)
            b1 = 2*a1*cos(1.414*180/10)
            c2 = b1
            c3 = -a1*a1
            c1 = 1-c2-c3
            Filt[i] = c1*(HP[i]+HP[i-1])/2+c2*Filt[i-1]+c3*Filt[i-2]
        
        # Pearson correlation for each value of lag
        if i>2+2+48:
            Corr=[0.]*48
            CosinePart=[0.]*48
            SinePart=[0.]*48
            SqSum=[0.]*48
            R=[[0.,0.]]*48
            Pwr=[0.]*48
            
            for Lag in range(1,49):
                # Set the averaging length as M
                M = AvgLength
                if AvgLength==0:
                    M=Lag
                Sx = 0
                Sy = 0
                Sxx = 0
                Syy = 0
                Sxy = 0
                for count in range(M):
                    X = Filt[i-count]
                    Y = Filt[i - Lag - count]
                    Sx += X
                    Sy += Y
                    Sxx += X*X
                    Syy += Y*Y
                    Sxy += X*Y
                if (M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy) > 0:
                    Corr[-Lag] = (M*Sxy - Sx*Sy)/((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy))**0.5
                    
            for Period in range(10,49):
                CosinePart[-Period] = 0
                SinePart[-Period] = 0
                for N in range(3,49):
                    CosinePart[-Period] += Corr[-N]*cos(360*N/Period)
                    SinePart[-Period] += Corr[-N]*sin(360*N/Period)
                SqSum[-Period] = CosinePart[-Period]**2. + SinePart[-Period]**2.
        
            for Period in range(10,49):
                R[-Period, 1] = R[-Period, 0]
                R[-Period, 0] = .2*SqSum[-Period]**2. + .8*R[-Period, 1]
        
                    
            # Find Maximum Power Level for Normalization
            MaxPwr = .995*MaxPwr
                
            for Period in range(10,49):
                if R[-Period, 0] > MaxPwr:
                    MaxPwr = R[-Period,0]            
        
            for Period in range(3,49):
                Pwr[-Period] = R[-Period, 0] / MaxPwr            
                    
            # Compute the dominant cycle using the CG of the spectrum
            Spx = 0
            Sp = 0
            
            for Period in range (10, 49):
                if Pwr[-Period] >= .5:
                    Spx += Period*Pwr[-Period]
                    Sp += Pwr[-Period]
            
            if Sp != 0.:
                DominantCycle[i] = Spx / Sp
            
            if DominantCycle[i] < 10:
                DominantCycle[i] = 10