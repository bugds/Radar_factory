import pandas

df = pandas.read_csv('merged_DEMO.csv')
df = df.merge(pandas.read_csv('merged_CBC.csv'), on = 'SEQN')
df = df.merge(pandas.read_csv('merged_CHEM.csv'), on = 'SEQN')
with open('columns.txt', 'r') as inpObj:
    lines = inpObj.readlines()

for l in lines:
    columns_dict[l.split(':')[0]] = l.split(':')[1].replace('\n', '')

df.rename(columns=columns_dict, inplace=True)
df = df.drop(columns = [c for c in df.columns if c.endswith('*')])
df = df.set_index('Respondent')
df.to_csv('NHANES_full.csv')
