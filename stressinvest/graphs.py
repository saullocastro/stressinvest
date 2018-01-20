import time
import os
import inspect

import numpy as np

THIS_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))

LIMIT = 60
CANDLE_WIDTH = 4
SHORT_SIZE = 5
LONG_SIZE = 21

def tostr(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

def create_graph_candle(num, candle_array, avg_short, avg_long, decision_array):
    try:
        title = 'Title'
        print('Fetching data for: %s' % title)
        timestamp = candle_array[:, 0]
        candles = candle_array[:, 1:5]
        volume = candle_array[:, 5]
        # Table for HTML
        th = ''
        dummy_array = ['' for _ in avg_long]
        barsty = 'fill-color: #2E8B57; fill-opacity: 0.4'
        def treat_val(val):
            if val == '':
                return 'null'
            if not isinstance(val, str):
                if np.isnan(val):
                    return 'null'
            else:
                return "'%s'" % val
            return '%f' % val
        for timeval, c, pt1, a1, pt2, a2, vol in zip(timestamp, candles,
                avg_short, decision_array, avg_long, dummy_array, volume):
            a1 = treat_val(a1)
            a2 = treat_val(a2)
            pt1 = treat_val(pt1)
            pt2 = treat_val(pt2)
            th += ("                ['%s', %f, %f, %f, %f, %s, %s, %s, %s, %f, '%s'],\n"
                    % (tostr(timeval), c[0], c[1], c[2], c[3], pt1, a1, pt2, a2, vol, barsty))
        template = os.path.join(THIS_DIR, 'graph_candle_template.html')
        lines = open(template, 'r').readlines()
        newlines = []
        for line in lines:
            newline = line.replace('%TABLE_HTML%', th)
            newline = newline.replace('%Y1TITLE%', 'Coin value in USD')
            newline = newline.replace('%Y2TITLE%', 'Candle volume in USD')
            newline = newline.replace('%TITLE%', title)
            newline = newline.replace('%NUM%', '%02d' % num)
            newline = newline.replace('%LABELLINE1%', 'Avg %d' % SHORT_SIZE)
            newline = newline.replace('%LABELLINE2%', 'Avg %d' % LONG_SIZE)
            newline = newline.replace('%LABELVOLUME%', 'Candle volume')
            newlines.append(newline)
    except:
        raise
        return ''
    out = '      google.charts.setOnLoadCallback(drawGraphCandle%02d);\n' % num
    for newline in newlines:
        out += newline
    return out


def create_graph_indicator(num, candle_array, plus_di, minus_di, slow_k, slow_d):
    try:
        timestamp = candle_array[:, 0]
        # Table for HTML
        th = ''
        for timeval, pt1, pt2, pt3, pt4 in zip(timestamp, plus_di, minus_di, slow_k, slow_d):
            def treat_pt(pt):
                if np.isnan(pt):
                    pt = 'null'
                else:
                    pt = '%f' % pt
                return pt
            pt1 = treat_pt(pt1)
            pt2 = treat_pt(pt2)
            pt3 = treat_pt(pt3)
            pt4 = treat_pt(pt4)
            th += ("                ['%s', %f, %f, %f, %f],\n"
                    % (tostr(timeval), pt1, pt2, pt3, pt4))
        template = os.path.join(THIS_DIR, 'graph_indicator_template.html')
        lines = open(template, 'r').readlines()
        newlines = []
        for line in lines:
            newline = line.replace('%TABLE_HTML%', th)
            newline = newline.replace('%NUM%', '%02d' % num)
            newline = newline.replace('%LABELLINE1%', 'Plus DI')
            newline = newline.replace('%LABELLINE2%', 'Minus DI')
            newline = newline.replace('%LABELLINE3%', 'Slow K')
            newline = newline.replace('%LABELLINE4%', 'Slow D')
            newlines.append(newline)
    except:
        return ''
    out = '      google.charts.setOnLoadCallback(drawGraphIndicator%02d);\n' % num
    for newline in newlines:
        out += newline
    return out
