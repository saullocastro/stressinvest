def backtest_calc(candles, outcandles, decision_table):
    initial_currency=1000 # usd
    trader_fee=0.1 #trader fee, in %
    
    # Starts sold
    currency_1=[initial_currency]
    currency_2=[0]
    transactions=[]
    for i in range(len(decision_table)):
        if decision_table[i]=="buy":
            if currency_1>0: # if it is not bought, buys
                transaction.add(["buy", ])
    
    # Ends sold