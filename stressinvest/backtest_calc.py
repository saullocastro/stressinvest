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
                price=outcandles[i,3] # close price
                currency_2=currency_1/price*(1-trader_fee/100) # applies fees
                fee=currency_1*(trader_fee/100)
                currency_1=0
                transaction.append(["buy",currency_1, currency_2, fee])
        if decision_table[i]=="sell":
            if currency_2>0: # if it is not sold, sells
                price=outcandles[i,3] # close price
                currency_1=currency_2/price*(1-trader_fee/100) # applies fees
                currency_2=0
                fee=currency_2*price*(trader_fee/100)
                transaction.append(["buy",currency_1, currency_2, fee])    
    # Ends sold