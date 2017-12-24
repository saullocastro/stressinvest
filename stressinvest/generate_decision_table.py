import random

import ipy_table

from dbinfo import OPERATORS, COIN_LIST

options = {1: 'hold', 2: 'sell', 3: 'buy'}
data = [['Operator'] + COIN_LIST]
hold = []
sell = []
buy = []
for i, op in enumerate(OPERATORS):
    row = [op]
    for j, coin in enumerate(COIN_LIST):
        val = random.randint(1, 3)
        if val == 1:
            hold.append([i, j])
        elif val == 2:
            sell.append([i, j])
        elif val == 3:
            buy.append([i, j])
        row.append(options[val])
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

with open('table.html', 'wb') as out:
    out.write(table._repr_html_())
