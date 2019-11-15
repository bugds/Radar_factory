from math import pi
import matplotlib.pyplot as plt


cat = ['HCT', 'MCV', 'MCH', 'MCHC', 'RDW']
values = [41.2, 89.3, 30.6, 342, 13.4]
errors = [1.2, 2.4, 1.0, 10, 0.5]
minRange = [36, 81, 27, 320, 11.5]
maxRange = [42, 98, 33, 360, 14.5]

N = len(cat)
angles = [n / float(N) * 2 * pi for n in range(N)]

cat += cat[:1]
values += values[:1]
errors += errors[:1]
minRange += minRange[:1]
maxRange += maxRange[:1]
angles += angles[:1]

# reValues = list()
catValues = list()
minVal = list()
maxVal = list()

for n in range(len(values)):
    minVal.append(values[n] - errors[n])
    maxVal.append(values[n] + errors[n])
    catValues.append(cat[n] + '\n' + str(values[n]))
    if minVal[n] < minRange[n]:
        minVal[n] = 5 * minVal[n] / minRange[n]
    elif minVal[n] > maxRange[n]:
        minVal[n] = 10 * minVal[n] / maxRange[n]
    else:
        minVal[n] = 5 + (5 * minVal[n] / maxRange[n])
    if maxVal[n] < minRange[n]:
        maxVal[n] = 5 * maxVal[n] / minRange[n]
    elif maxVal[n] > maxRange[n]:
        maxVal[n] = 10 * maxVal[n] / maxRange[n]
    else:
        maxVal[n] = 5 + (5 * maxVal[n] / maxRange[n])

#    if values[n] < minRange[n]:
#        reValues.append(5 * values[n] / minRange[n])
#        catValues.append(cat[n] + '\n< ' + str(values[n]))
#    elif values[n] > maxRange[n]:
#        reValues.append(10 * values[n] / maxRange[n])
#        catValues.append(cat[n] + '\n> ' + str(values[n]))
#    else:
#        reValues.append(5 + (5 * values[n] / maxRange[n]))
#        catValues.append(cat[n] + '\n' + str(values[n]))

plt.rc('axes', linewidth=0.5, edgecolor="#888888")

ax = plt.subplot(111, polar=True)

plt.xticks(angles[:-1], catValues)
gridlines = ax.yaxis.get_gridlines()
for gl in gridlines:
    gl.get_path()._interpolation_steps = 5
# plt.yticks([], [])

ax.fill_between(angles,
                minVal,
                maxVal,
                alpha=0.1,
                color='r')

ax.fill_between(angles,
                [5]*6,
                [10]*6,
                alpha=0.1,
                color='b')

ax.set_theta_offset(pi/2)

m, M = ax.get_ylim()
plt.ylim(m - 1, M + 1)

# ax.set_yticklabels([])

plt.show()