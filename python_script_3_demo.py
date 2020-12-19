import os
import pandas

df_list = list()
mainDir = '/home/bioinfuser/applications/Radar_factory/NHANES'
for table in os.listdir(mainDir):
    if table.endswith('DEMO.csv'):
        print(table)
        df_list.append(pandas.read_csv(mainDir + '/' + table, sep = ';'))
i = 0

flag = True
while flag:
    columns_set = set()
    for df in df_list:
        try:
            columns_set.add(sorted(list(df.columns))[i])
        except:
            flag = False
    print(columns_set)
    i += 1

columns_set = set(df_list[0].columns)
for df in df_list:
    columns_set = columns_set.intersection(set(df.columns))

#print(columns_set)

for i in range(0, len(df_list)):
    #print(set(df_list[i].columns).difference(columns_set))
    df_list[i] = df_list[i].drop(columns = set(df_list[i].columns).difference(columns_set))

#for df in df_list:
#    print(df.columns)

df = pandas.concat(df_list).set_index('SEQN').sort_index()

df = df.astype('string')
df = df.apply(lambda x: x.str.replace(',', '.'))
df.to_csv('merged_DEMO.csv')
