import time

from graphs import create_graph_candle, create_graph_indicator


COIN_LIST = ['BTC']
EXCHANGES = ['BINANCE']

LIMIT = 60
CANDLE_WIDTH = 4
SHORT_SIZE = 5
LONG_SIZE = 21

def tostr(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

def generate_buy_sell_html(candle_array,
        decision_array,
        avg_short,
        avg_long,
        plus_di,
        minus_di,
        slow_k,
        slow_d,
        html_path):
    out = open(html_path, 'w')
    out.write('''
<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
''')
    text = ''
    num = 0
    text += create_graph_candle(num, candle_array, avg_short, avg_long,
            decision_array)
    text += create_graph_indicator(num, candle_array, plus_di, minus_di, slow_k, slow_d)
    for action in decision_array[::-1]:
        if action:
            break
    out.write(text)
    out.write('''
    </script>
  </head>
  <body>
''')
    out.write('    <div id="candle_div%02d" style="height: 700px;"></div>\n' % num)
    out.write('    <div id="indicator_div%02d" style="height: 350px;"></div>\n' % num)
    out.write('''
  </body>
</html>
''')
    out.close()

