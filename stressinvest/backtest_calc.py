import datetime

def backtest_calc(candles, outcandles, decision_table):
    initial_currency=1000 # usd
    trader_fee=0.2 #trader fee, in %
    
    # Starts sold
    currency_1=initial_currency
    currency_2=0
    time=outcandles[0,0]
    time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
    transactions=[["Initial",currency_1,currency_2, 0, "na", time]]
    for i in range(len(decision_table)):
        if decision_table[i]=="buy":
            if currency_1>0: # if it is not bought, buys
                price=outcandles[i,3] # close price
                currency_2=currency_1/price*(1-trader_fee/100) # applies fees
                fee=currency_1*(trader_fee/100)
                currency_1=0
                time=outcandles[i,0]
                time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
                transactions.append(["buy",currency_1, currency_2, fee, price,time])
        if decision_table[i]=="sell":
            if currency_2>0: # if it is not sold, sells
                price=outcandles[i,3] # close price
                currency_1=currency_2*price*(1-trader_fee/100) # applies fees
                fee=currency_2*price*(trader_fee/100)
                currency_2=0
                time=outcandles[i,0]
                time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
                transactions.append(["sell",currency_1, currency_2, fee, price,time])    
    
    # Ends sold
    if currency_2>0: # if it is not sold, sells
        price=outcandles[i,3] # close price
        currency_1=currency_2*price*(1-trader_fee/100) # applies fees
        fee=currency_2*price*(trader_fee/100)
        currency_2=0
        time=outcandles[i,0]
        time=datetime.datetime.fromtimestamp(time).strftime('%m/%d/%Y %H:%M,')
        transactions.append(["sell",currency_1, currency_2, fee, price, time])      
    return transactions