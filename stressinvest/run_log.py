import sys
import time
import sqlite3

from  dbinfo import COIN_LIST, DB_TABLE_ORDER
from cryptocompare import get_price

'''
15GB = nr de aquisicoes  X  nr de moedas  X  228.27 Bytes
nr de aquisicoes = 8819669

nr de aquisicoes = 60 dias X aquisicoes por dia
aquisicoes por dia = 146994

max aquisicoes por segundo = aquisicoes por dia / (3600 X 24)
max aquisicoes por segundo = 1.7

'''
SLEEP_TIME = 1
COMMIT_AT_EACH_NTH_CYCLE = 1


def treat_real(coin, v):
    v = v.replace(coin, u'')
    v = v.replace(u'$', u'')
    v = v.replace(u',', u'')
    return v

if __name__ == '__main__':
    assert len(sys.argv) == 2
    db = sqlite3.connect(sys.argv[1])
    cursor = db.cursor()

    cycle = 0
    while True:
        query = get_price(COIN_LIST, full=True)
        if query is not None:
            timestamp = time.time()
            tables = query['RAW']
            for coin, d in tables.items():
                cmd = "INSERT INTO %s VALUES(" % coin
                cmd += "%s," % str(timestamp)
                for key in DB_TABLE_ORDER[1:]:
                    v = d[u'USD'][key]
                    if isinstance(v, str):
                        cmd += "'%s'" % str(v)
                    else:
                        cmd += "%s" % str(v)
                    if key != DB_TABLE_ORDER[-1]:
                        cmd += ",\n"
                cmd += ");"
                cursor.execute(cmd)
            cycle += 1
            if cycle == COMMIT_AT_EACH_NTH_CYCLE:
                cycle = 0
                db.commit()
        time.sleep(SLEEP_TIME)
