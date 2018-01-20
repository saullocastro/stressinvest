def backtest_calc(candles, outcandles, decision_table):
    initial_currency=1000 # usd
    trader_fee=0.1 #trader fee, in %
    
    # Starts sold
    currency_1=initial_currency
    currency_2=0
    transactions=["Initial",currency_1,currency_2]
    for i in range(len(decision_table)):
        if decision_table[i]=="buy":
            if currency_1>0: # if it is not bought, buys
                price=outcandles[i]
                currency_2=currency_1*
                transaction.add(["buy",])
    
    # Ends sold