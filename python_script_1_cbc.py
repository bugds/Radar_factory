import os
import pandas

df_list = list()
mainDir = '/home/bioinfuser/applications/Radar_factory/NHANES'
for table in os.listdir(mainDir):
    if table.endswith('CBC.csv'):
        print(table)
        df_list.append(pandas.read_csv(mainDir + '/' + table, sep = ';', decimal = ','))
i = 0

flag = True
while flag:
    columns_set = set()
    for df in df_list:
        try:
            columns_set.add(df.columns[i])
        except:
            flag = False
    print(columns_set)
    i += 1

df = pandas.concat(df_list).set_index('SEQN').sort_index()

df = df.astype('string')
df = df.apply(lambda x: x.str.replace(',', '.'))
df.to_csv('merged_CBC.csv')
