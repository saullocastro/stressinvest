import time

import numpy as np

from cryptocompare import get_histo, EXCHANGES

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
    return MA_short, MA_long, MA_histogram, MA_who_is_up, MA_trigger, MA_action

LIMIT = 120
CANDLE_WIDTH = 4
SHORT_SIZE = 10
LONG_SIZE = 20

def write_func(out, num, e):
    title = 'BTC, %s, Candle Width %d min, Short Avg %d, Long Avg %d' % (e, CANDLE_WIDTH, SHORT_SIZE, LONG_SIZE)
    print('Fetching data for: %s' % title)
    timestamp = []
    candles = []
    volume = []
    q = get_histo('minute', 'BTC', LIMIT, CANDLE_WIDTH, e)
    for d in q['Data']:
        timestamp.append(d['time'])
        volume.append(d['volumeto'])
        candles.append([d['low'], d['open'], d['close'], d['high']])
    timestamp = np.asarray(timestamp)

    def tostr(t):
        return time.strftime("%m-%d %H:%M:%S", time.localtime(t))

    candles = np.asarray(candles)
    vclose = candles[:, 2]
    MA_short, MA_long, MA_histogram, MA_who_is_up, MA_trigger, MA_action = MA(vclose, SHORT_SIZE, LONG_SIZE)

    # Table for HTML
    th = ''
    pts1 = [0.] + MA_short
    pts2 = [0.] + MA_long
    a1s = [''] + MA_action
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
    for newline in newlines:
        out.write(newline)


out = open('index.html', 'w')
out.write('''
<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
''')

for num, e in enumerate(EXCHANGES):
    out.write('      google.charts.setOnLoadCallback(drawVisualization%02d);\n' % num)
    write_func(out, num, e)

out.write('''
    </script>
  </head>
  <body>
    <div id="intro" style="height: 200px;">
        <br>
        <h2>Graphs are shown below</h2>
        <h2><a href='table.html'> Decision table </a></h2>
    </div>
''')

for num, e in enumerate(EXCHANGES):
    out.write('    <div id="chart_div%02d" style="height: 700px;"></div>\n' % num)

out.write('''
  </body>
</html>
''')
out.close()
