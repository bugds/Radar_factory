import pandas

ref_dict = dict()
pregNum = 1 # in NHANES pregnancy defined as 1

with open('references.txt', 'r') as ref_file:
    lines = ref_file.readlines()

for l in lines:
    if not (l.startswith('_')):
        currAnalyte = l.replace('\n', '')
        ref_dict[currAnalyte] = dict()
    else:
        currGroup = l[1]
        currTopAge = l.split(':')[0].split('-')[1]
        currValues = l.replace('\n', '').split(':')[1].split('-')
        currValues = [currValues[0], currValues[1]]
        if not (currGroup in ref_dict[currAnalyte]):
            ref_dict[currAnalyte][currGroup] = dict()
        ref_dict[currAnalyte][currGroup][currTopAge] = currValues

df = pandas.read_csv('NHANES_refined.csv')

prevAge = 0

for analyte in ref_dict:
    analyte_df = pandas.DataFrame()
    for group in ref_dict[analyte]:
        for age in ref_dict[analyte][group]:
            if (group == 'm' or group == 'f'):
                if group == 'm':
                    groupN = 1
                elif group == 'f':
                    groupN = 2
                curr_df = df[(df['Gender'] == groupN) & (df['Pregnancy'] != pregNum)]
            elif group == 'p':
                curr_df = df[df['Pregnancy'] == pregNum]
            else:
                raise Exception('AAARGH!!!')
                
            curr_df = curr_df[curr_df['Age_years'].astype(int) > int(prevAge)]
            curr_df = curr_df[curr_df['Age_years'].astype(int) <= int(age)]
            
            topRange = float(ref_dict[analyte][group][age][1])
            botRange = float(ref_dict[analyte][group][age][0])
            median = (botRange + topRange)/2
            diff = topRange - botRange
            
            curr_df[analyte + '_normalized'] = (curr_df[analyte] - median)/diff
            
            analyte_df = analyte_df.append(curr_df)
            
            if age == max(ref_dict[analyte][group].keys()):
                prevAge = 0
            else:
                prevAge = age
    map_dict = analyte_df[analyte + '_normalized']
    df[analyte] = (df.index).map(map_dict)
    #for respondent in analyte_df.index:
        #df.loc[respondent, analyte] = analyte_df.loc[respondent][analyte + '_normalized']

df.to_csv('7_normalized.csv')
