import sqlite3
import datetime

conn = sqlite3.connect('bitfinex_0.1.db')

cursor = conn.cursor()

# Comando para verificar quais tabelas existem 
cursor.execute("""
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
""")

for tabela in cursor.fetchall():
    print("%s" % (tabela))
    if tabela[0]<>"sqlite_sequence":
        # Comando para verificar as colunas
        cursor.execute('PRAGMA table_info({})'.format(tabela[0]))
        print cursor.fetchall()
#        colunas = [tupla[1] for tupla in cursor.fetchall()]
#        print('Colunas:', colunas)    
#        
#        #Escreve formato normal
#        with open(tabela[0]+'.csv','w') as f:
#            for col in colunas:
#                f.write(col)
#                f.write(",")
#            f.write("\n")
#            aux_str='SELECT * FROM '
#            aux_str+=tabela[0]+';'
#            cursor.execute(aux_str)
#            #cursor.execute("""
#            #SELECT * FROM " +tabela+";
#            #""")
#        
#            for linha in cursor.fetchall():
#                for i in range(len(linha)):
#                    col=linha[i]
#                    if i==1:
#                        f.write(datetime.datetime.fromtimestamp(float(col)).strftime('%m/%d/%Y %H:%M,'))
#                    else:
#                        f.write(str(col)+",")
#                f.write("\n")
#        #Escreve formato metastock
#        with open(tabela[0]+'meta.csv','w') as f:       
#            cursor.execute(aux_str)
#            for linha in cursor.fetchall():
#                name=tabela[0].split("_")[2]+"_"+tabela[0].split("_")[1]
#                f.write(name+",") #Name
#                f.write("I,") # Period
#                f.write(datetime.datetime.fromtimestamp(linha[1]).strftime('%m/%d/%Y,%H:%M,')) # Time
#                f.write(str(linha[2])+",") # Open
#                f.write(str(linha[3])+",") # High
#                f.write(str(linha[4])+",") # Low
#                f.write(str(linha[5])+",") # Close
#                f.write(str(linha[7])+",") # Volume
#                f.write("0") # Open-int
#                f.write("\n")        
        
conn.close()