import time

import numpy as np
import ipy_table

from cryptocompare import get_histo, EXCHANGES, COIN_LIST

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
        if pos > 0 and pos < MA_short_size-1:
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
            MA_histogram  = [MA_short[0] - MA_long[0]]
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
                MA_histogram.append([MA_short[pos] - MA_long[pos]])
                if MA_short[pos] > MA_long[pos]:
                    MA_who_is_up.append('short')
                else:
                    MA_who_is_up.append('long')
        pos += 1

    pos = 0
    MA_trigger = ['']
    MA_action = ['']
    for x in MA_histogram:
        if pos > 0:
            if MA_histogram[pos-1] != 0 :
                if np.sign(MA_histogram[pos])*np.sign(MA_histogram[pos-1]) < 0:
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
    MA_short = MA_short[1:]
    MA_long = MA_long[1:]
    MA_histogram = MA_histogram[1:]
    MA_trigger = MA_trigger[1:]
    MA_action = MA_action[1:]
    MA_who_is_up = MA_who_is_up[1:]
    return dict(
        short=MA_short,
        long=MA_long,
        histogram=MA_histogram,
        who_is_up=MA_who_is_up,
        trigger=MA_trigger,
        action=MA_action)

LIMIT = 60
CANDLE_WIDTH = 4
SHORT_SIZE = 5
LONG_SIZE = 21

def tostr(t):
    return time.strftime("%m-%d %H:%M:%S", time.localtime(t))

def write_func(coin, out, num, e, mhd='minute', candle_width=CANDLE_WIDTH, limit=LIMIT):
    try:
        title = '%s, %s, Candle Width %d %s, Short Avg %d, Long Avg %d' % (coin, e, candle_width, mhd, SHORT_SIZE, LONG_SIZE)
        print('Fetching data for: %s' % title)
        timestamp = []
        candles = []
        volume = []
        q = get_histo(mhd, coin, limit, candle_width, e)
        for d in q['Data']:
            timestamp.append(d['time'])
            volume.append(d['volumeto'])
            candles.append([d['low'], d['open'], d['close'], d['high']])
        timestamp = np.asarray(timestamp)
        candles = np.asarray(candles)
        vclose = candles[:, 2]
        ma = MA(vclose, SHORT_SIZE, LONG_SIZE)
        # Table for HTML
        th = ''
        pts1 = [0.] + ma['short']
        pts2 = [0.] + ma['long']
        a1s = [''] + ma['action']
        a2s = ['' for _ in pts2]
        for timeval, candle, pt1, a1, pt2, a2 in zip(timestamp, candles, pts1, a1s, pts2, a2s):
            if a1:
                a1 = "'%s'" % a1
            else:
                a1 = 'null'
            if a2:
                a2 = "'%s'" % a2
            else:
                a2 = 'null'
            if not pt1:
                pt1 = 'null'
            else:
                pt1 = '%f' % pt1
            if not pt2:
                pt2 = 'null'
            else:
                pt2 = '%f' % pt2
            th += "                ['%s', %f, %f, %f, %f, %s, %s, %s, %s],\n" % (tostr(timeval), *candle, pt1, a1, pt2, a2)
        lines = open('func_template.html', 'r').readlines()
        newlines = []
        for line in lines:
            newline = line.replace('%TABLE_HTML%', th)
            newline = newline.replace('%XTITLE%', 'USD')
            newline = newline.replace('%TITLE%', title)
            newline = newline.replace('%NUM%', '%02d' % num)
            newline = newline.replace('%LABELLINE1%', 'Avg %d' % SHORT_SIZE)
            newline = newline.replace('%LABELLINE2%', 'Avg %d' % LONG_SIZE)
            newlines.append(newline)
    except:
        return dict()
    out.write('      google.charts.setOnLoadCallback(drawVisualization%02d);\n' % num)
    for newline in newlines:
        out.write(newline)
    return ma


mhds = ['minute', 'hour', 'hour']
candles = [30, 4, 6]

out = open('index.html', 'w')
out.write('''
<html>
  <body>
    <div id="intro">
        <br>
        <h2>All data below generated using short MA 5 e long MA 21</h2>
''')

for candle, mhd in zip(candles, mhds):
    out.write("        <h2><a href='decision_table_candle_%03d_%s.html'> Decision table candle %03d %s</a></h2>\n" % (candle, mhd, candle, mhd))
for coin in COIN_LIST:
    for candle, mhd in zip(candles, mhds):
        out.write("        <h2><a href='graphs_%s_candle_%03d_%s.html'> %s, candle %03d %s</a></h2>\n" % (coin, candle, mhd, coin, candle, mhd))
out.write('''
    </div>
  </body>
</html>
''')
out.close()


for candle, mhd in zip(candles, mhds):
    all_exc = set()
    decision_table = {}
    for coin in COIN_LIST:
        decision_table[coin] = {}
        row = []
        exc = EXCHANGES.get(coin, EXCHANGES['BTC'])
        out = open('graphs_%s_candle_%03d_%s.html' % (coin, candle, mhd), 'w')
        out.write('''
<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
''')

        for num, e in enumerate(exc):
            all_exc.add(e)
            ma = write_func(coin, out, num, e, mhd, candle)
            for action in ma['action'][::-1]:
                if action:
                    break
            decision_table[coin][e] = action
        out.write('''
    </script>
  </head>
  <body>
''')

        for num, e in enumerate(exc):
            out.write('    <div id="chart_div%02d" style="height: 700px;"></div>\n' % num)
        out.write('''
  </body>
</html>
''')
        out.close()

    data = []
    buy = []
    sell = []
    data.append(['Exchange'] + COIN_LIST)
    for i, e in enumerate(sorted(list(all_exc))):
        row = [e]
        for j, coin in enumerate(COIN_LIST):
            d = decision_table[coin].get(e)
            if d == 'buy':
                buy.append([i, j])
            if d == 'sell':
                sell.append([i, j])
            row.append(d)
        data.append(row)

    table = ipy_table.make_table(data)
    for i in range(len(data)):
        for j in range(len(data[0])):
            table.set_cell_style(i, j, width=60, align='center')
    for i in range(len(data)):
        table.set_cell_style(i, 0, bold=True, align='left')
    for j in range(len(data[0])):
        table.set_cell_style(0, j, bold=True)

    for i, j in sell:
        table.set_cell_style(i+1, j+1, color='red')
    for i, j in buy:
        table.set_cell_style(i+1, j+1, color='green')

    with open('decision_table_candle_%03d_%s.html' % (candle, mhd), 'w') as out:
        out.write(table._repr_html_())
