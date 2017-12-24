import numpy as np
import matplotlib.pyplot as plt

from dbinfo import OPERATORS
from cryptocompare import query_cryptocompare

def sinal(x):
    if x[0]*1 >= 0:
        return +1
    else:
        return -1

def EMA(samples, interval_close, previous_ema):
    return (interval_close * (2 / (samples + 1)) + previous_ema * (1 - (2 / (samples + 1))))

def MA(close, MA_short_size, MA_long_size):
    MA_short = [0]
    MA_long = [0]
    pos = 0
    avg_short = 0
    avg_long = 0
    pos = 0
    for x in close:
        if pos >= MA_short_size-1:
            temp_short = pos-(MA_short_size-1)
            while temp_short <= pos:
                avg_short+= close[temp_short]
                temp_short+= 1
            avg_short = avg_short/MA_short_size
            MA_short.append(avg_short)
            avg_short = 0
        if pos>0 and pos  < MA_short_size-1:
            MA_short.append(0)

        if pos >= MA_long_size-1:
            temp_long = pos-(MA_long_size-1)
            while temp_long <= pos:
                avg_long+= close[temp_long]
                temp_long+= 1
            avg_long = avg_long/MA_long_size
            MA_long.append(avg_long)
            avg_long = 0

        if  pos>0 and pos  < MA_long_size-1:
            MA_long.append(0)

        pos += 1


    pos = 0
    for x in MA_long:
        if pos == 0:
            MA_histogram  = [MA_short[0]-MA_long[0]]
            if MA_short[0] > MA_long[0]:
                MA_who_is_up = ['short']
            else:
                MA_who_is_up = ['long']
        else:
            if MA_long[pos] == 0:
                MA_histogram.append(  0 )
                if MA_short[pos] > MA_long[pos]:
                    MA_who_is_up.append( 'short')
                else:
                    MA_who_is_up.append('long')
            else:
                MA_histogram.append(   [MA_short[pos]-MA_long[pos]] )
                if MA_short[pos] > MA_long[pos]:
                    MA_who_is_up.append('short')
                else:
                    MA_who_is_up.append('long')
        pos += 1

    pos = 0
    MA_trigger=['']
    MA_action=['']
    for x in MA_histogram:
        if pos>0:
            if MA_histogram[pos-1] != 0 :
                if sinal(MA_histogram[pos])*sinal(MA_histogram[pos-1]) < 0:
                    MA_trigger.append('cross')
                else:
                    MA_trigger.append('')
            else:
                MA_trigger.append('')
            if MA_trigger[pos] == 'cross' and MA_who_is_up[pos] == 'short':
                MA_action.append('buy')
            elif MA_trigger[pos] == 'cross' and MA_who_is_up[pos] == 'long':
                MA_action.append('sell')
            else:
                MA_action.append('')
        pos += 1
    return np.asarray(MA_short), np.asarray(MA_long), MA_histogram, MA_who_is_up, MA_trigger, MA_action

limit = 60
candle_width = 3

fig = plt.gcf()
ax = plt.gca()
for operator in OPERATORS:
    fig.clear()
    timestamp = []
    close = []
    url = 'https://min-api.cryptocompare.com/data/histohour?fsym=BTC&tsym=USD&limit={limit}&aggregate={candle_width}&e={operator}'.format(
            limit=limit,
            candle_width=candle_width,
            operator=operator,
            )
    q = query_cryptocompare(url, errorCheck=False)
    for d in q['Data']:
        timestamp.append(d['time'])
        close.append(d['close'])
    timestamp = np.asarray(timestamp)
    close = np.asarray(close)

    MA_short, MA_long, MA_histogram, MA_who_is_up, MA_trigger, MA_action = MA(close, 9, 21)
    ax.plot(timestamp[MA_short != 0], MA_short[MA_short != 0])
    ax.plot(timestamp[MA_long != 0], MA_long[MA_long != 0])
    for i, action in enumerate(MA_action):
        if action == 'buy':
            plt.annotate('buy', (timestamp[i], MA_short[i]), (timestamp[i], MA_short[i]))
        if action == 'sell':
            plt.annotate('sell', (timestamp[i], MA_short[i]), (timestamp[i], MA_short[i]))
    fig.savefig('coin_%s_operator_%s.png' % ('BTC', operator))

