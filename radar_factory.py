import numpy as np
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

globalMin = 3
globalMax = 4

def radar_factory(num_vars, frame='polygon'):
    """Create a radar chart with "num_vars" axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def fill_between(self, x, y1, y2=0, closed=True, where=None, interpolate=False,
                     step=None, **kwargs):
            """Override fill_between so that line is closed by default"""
            if closed:
                x = np.concatenate((x, [x[0]]))
                y1 = np.concatenate((y1, [y1[0]]))
                y2 = np.concatenate((y2, [y2[0]]))
            return super().fill_between(x, y1, y2, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def draw(self, renderer):
            """ Draw. If frame is polygon, make gridlines polygon-shaped """
            if frame == 'polygon':
                gridlines = self.yaxis.get_gridlines()
                for gl in gridlines:
                    gl.get_path()._interpolation_steps = num_vars
            super().draw(renderer)


        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)


                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def data_recount(values, minRange, maxRange):
    minVal = list()
    maxVal = list()

    for i in range(len(values)):
        difference = maxRange[i] - minRange[i]
        # Gathering marks of difference for each test
        intermedMax = minRange[i] / difference + 1
        # Condition is arbitrary, could be minimum, i=1, 2 etc
        if i == 0:
            # newMin = minRange[i] / difference
            # newMax = intermedMax
            newMin = globalMin
            newMax = globalMax
        # Transferring into conditional units
        minVal.append(globalMin - ((minRange[i] - values[i]) / difference))
        maxVal.append(globalMin - ((minRange[i] - values[i]) / difference))

        # newMin/1.5 is the chosen minimum displayed. Each value less
        # than newMin/1.5 will be shown in the center of diagram to
        # concentrate on the reference interval
        minVal[i] = max(minVal[i], newMin/1.5)
        maxVal[i] = max(maxVal[i], newMin/1.5)
        minVal[i] = min(minVal[i], 1.5*newMax + 0.5)
        maxVal[i] = min(maxVal[i], 1.5*newMax + 0.5)

    return minVal, maxVal, newMin, newMax


def plotting(ax, theta, minArray, maxArray, color):
    if color == 'blue':
        color1 = '#1E90FF'
        color2 = '#87CEFA'

    if color == 'orange':
        color1 = '#FF4500'
        color2 = '#FF7F50'

    if color == 'green':
        color1 = '#0B6623'
        color2 = '#3BB143'

    ax.plot(theta, minArray, color=color1, alpha=0.5)
    ax.plot(theta, maxArray, color=color1, alpha=0.5)

    if color == 'blue':
        ax.fill_between(theta, minArray, maxArray, alpha=0.3, color=color2)
    else:
        plotTht = list()
        plotMin = list()
        plotMax = list()
        for i in range(0, len(values)):
            try:
                float(values[i])
                plotTht.append(theta[i])
                plotMin.append(minArray[i])
                plotMax.append(maxArray[i])
            except:
                ax.fill_between(plotTht, plotMin, plotMax, alpha=0.3, color=color2, closed = False)
                plotTht = list()
                plotMin = list()
                plotMax = list()
        try:
            float(values[0])
            float(values[-1])
            plotTht = np.concatenate(plotTht, theta[0])
            plotMin = np.concatenate(plotMin, minArray[0])
            plotMax = np.concatenate(plotMax, maxArray[0])
        except:
            if len(plotTht) > 1:
                ax.fill_between(plotTht, plotMin, plotMax, alpha=0.3, color=color2, closed = False)

class LabAnalyte():
    def __init__(self, minmaxerr):
        self.min = float(minmaxerr.split('-')[0])
        self.max = float(minmaxerr.split('-')[1])
        self.err = 0

class LabReference(dict):
    def __init__(self, refFile):
        with open(refFile, 'r') as refObj:
            lines = refObj.readlines()

        for l in lines:
            if l[0] != '_':
                analyte = l.strip()
            else:
                sex = l[1]
                if not analyte in self:
                    self[analyte] = dict()
                if not sex in self[analyte]:
                    self[analyte][sex] = dict()
                for age in range(int(l[2:].split('-')[0]), int(l.split('-')[1].split(':')[0])):
                    self[analyte][sex][age] = LabAnalyte(l.split(':')[1])

    def getList(self, attribute, age):
        if attribute == 'cat':
            return list(self.keys())

        valList = list()
        for analyte in self:
            toAdd = False
            for ageInt in self[analyte]:
                if ageInt == 'all':
                    toAdd = True
                if 'лет' in ageInt:
                    if '>' in ageInt:
                        minAgeInt = int(ageInt.split()[0].replace('>', ''))
                        maxAgeInt = 1000
                    if '<' in ageInt:
                        minAgeInt = 0
                        maxAgeInt = int(ageInt.split()[0].replace('<', ''))
                    if '-' in ageInt:
                        minAgeInt = int(ageInt.split()[0].split('-')[0])
                        maxAgeInt = int(ageInt.split()[0].split('-')[1])
                    if minAgeInt <= int(age) <= maxAgeInt:
                        toAdd = True
                if toAdd:
                    if attribute == 'min':
                        v = self[analyte][ageInt].min
                    if attribute == 'max':
                        v = self[analyte][ageInt].max
                    valList.append(float(v.replace(',', '.').replace('\n', '')))
                    break
        return valList

def main(name, title, cat, values, minRange, maxRange):
    N = len(values)
    theta = radar_factory(N, frame='polygon')

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.85, bottom=0.05)

    # recounting
    minVal, maxVal, newMin, newMax = data_recount(values, minRange, maxRange)

    plt.yticks([], [])
    plt.xticks([], [])

    # reference
    plotting(ax, theta, [newMin]*N, [newMax]*N, color='blue')

    # case
    plotting(ax, theta, minVal, maxVal, color='orange')

    _, M = ax.get_ylim()

    plt.ylim(newMin/1.5 - 0.1, 1.5*newMax + 0.6)

    # ax2 = fig.add_axes([0,0,1,1])
    # ax2.axis('equal')
    # elementsProportion = [
    #     6,7,2
    # ]
    # n = ax2.pie(
    #     elementsProportion,
    #     radius = 1.5,
    #     counterclock = False,
    #     startangle = 80
    # )
    # ax2.set_position(ax.get_position())
    # for i in range(len(n[0])):
    #     n[0][i].set_alpha(0.00)

    # ax.set_varlabels(map('\n'.join, zip(cat, map(lambda x: str(x), values))))
    # for i in range(N):
    #     plt.text(theta[i], newMin * (1+0.02), minRange[i], size=5, ha='center')
    #     plt.text(theta[i], newMax * (1+0.02), maxRange[i], size=7, ha='center')
    ax.set_axis_off()

    plt.savefig( \
        sys.path[0] \
        + '/results/' + name + '.png', bbox_inches \
        = "tight", format = 'png', dpi = 30 \
    )

title = 'анемия'

analytes = [
    'WBC','LymN','MonN','NeuN','EosN','BasN',
    'RBC','HGB','HCT','MCV','MCH','MCHC','RDW',
    'PltN','MPV'
]

df = pd.read_csv('NHANES_refined.csv', index_col=0)

df = df[df['Pregnancy'] == 2]
df = df[df['Age_years'] < 99]
df = df[df['Age_years'] > 12]

a = LabReference('references.txt')
# cat = list(a.keys())
cat = analytes

for i, r in df.iterrows():
    minRange = list()
    maxRange = list()
    values = list()
    for c in cat:
        if r['Gender'] == 1:
            sex = 'm'
        elif r['Gender'] == 2:
            sex = 'f'
        minRange.append(a[c][sex][r['Age_years']].min)
        maxRange.append(a[c][sex][r['Age_years']].max)
        values.append(r[c])
    main(str(i), title, cat, values, minRange, maxRange)
    print(df.iloc[0])

# for sample in os.listdir(sys.path[0] + '/anemia/samples/'):
#     age = int(sample[1:3])
#     name = sample + '.pdf'

#     a = LabReference('anemia', group = sample[0])
#     cat = a.getList('cat', age)
#     minRange = a.getList('min', age)
#     maxRange = a.getList('max', age)

#     sampleDict = dict()
#     with open(sys.path[0] + '/anemia/samples/' + sample, 'r') as inpObj:
#         lines = inpObj.readlines()
#     for l in lines:
#         sampleDict[l.split('\t')[0]] = l.split('\t')[1]
#     values = list()
#     for c in cat:
#         if sampleDict[c]:
#             values.append(float(sampleDict[c]))
#         else:
#             values.append('NA')
#     main(name, title, cat, values, minRange, maxRange)
