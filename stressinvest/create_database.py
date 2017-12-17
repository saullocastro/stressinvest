from __future__ import absolute_import

import sys
import sqlite3

from dbinfo import COIN_LIST

if __name__ == '__main__':
    assert len(sys.argv) == 2
    db = sqlite3.connect(sys.argv[1])

    cursor = db.cursor()

    for coin in COIN_LIST:
        cursor.execute('''
        CREATE TABLE %s(
                TIMESTAMP INT PRIMARY KEY,
                LASTUPDATE INT,
                OPEN24HOUR REAL,
                OPENDAY REAL,
                LOWDAY REAL,
                HIGHDAY REAL,
                CHANGE24HOUR REAL,
                CHANGEPCT24HOUR REAL,
                CHANGEDAY REAL,
                MKTCAP REAL,
                CHANGEPCTDAY REAL,
                HIGH24HOUR REAL,
                VOLUMEDAY REAL,
                VOLUMEDAYTO REAL,
                TOTALVOLUME24HTO REAL,
                PRICE REAL,
                LOW24HOUR REAL,
                VOLUME24HOURTO REAL,
                VOLUME24HOUR REAL);
        ''' % coin)
    db.commit()
