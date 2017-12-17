from datetime import datetime
import time
import sqlite3

import numpy as np

from dbinfo import DB_TABLE_ORDER

db = sqlite3.connect('/var/stressinvest/StressInvest.db')
cursor = db.cursor()
coin = 'BTC'
columns = ['TIMESTAMP', 'PRICE']
t1 = time.mktime(datetime(2017, 12, 17, 16, 8, 4, 0).timetuple())
t2 = time.mktime(datetime(2017, 12, 17, 18, 8, 4, 0).timetuple())
out = []
for entry in cursor.execute('SELECT * FROM %s WHERE TIMESTAMP BETWEEN %s AND %s' %
        (coin, str(t1), str(t2))):
    row = []
    for col in columns:
        if col not in DB_TABLE_ORDER:
            raise ValueError('Invalid column "%s"' % col)
        row.append(entry[DB_TABLE_ORDER.index(col)])
    out.append(row)
out = np.array(out)

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

date_fmt = '%H:%M:%S'
ax = plt.gca()
x = out[:, 0]
y = out[:, 1]
ax.plot(x, y)
ax.set_ylabel(coin + ' (USD)')
plt.gcf().autofmt_xdate()
ax.xaxis.set_major_locator(mtick.FixedLocator(np.linspace(x.min(), x.max(), 10)))
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda pos,_: time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(pos))))
plt.tight_layout()
plt.show()
