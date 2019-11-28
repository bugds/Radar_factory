import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


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

        def fill_between(self, x, y1, y2=0, where=None, interpolate=False,
                     step=None, **kwargs):
            """Override fill_between so that line is closed by default"""
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


def data_recount(values, errors, minRange, maxRange):
    minVal = list()
    maxVal = list()

    for i in range(len(values)):
        # Transferring into conditional units
        difference = maxRange[i] - minRange[i]
        minVal.append((values[i]-errors[i]) / difference)
        maxVal.append((values[i]+errors[i]) / difference)
        # Gathering marks of difference for each test
        intermedMax = minRange[i] / difference + 1

        # Condition is arbitrary, could be minimum, i=1, 2 etc
        if i == 0:
            newMin = minRange[i] / difference
            newMax = intermedMax
        else:
            # newMin/1.5 is the chosen minimum displayed. Each value less
            # than newMin/1.5 will be shown in the center of diagram to
            # concentrate on the reference interval
            minVal[i] = max(minVal[i] + newMax - intermedMax, newMin/1.5)
            maxVal[i] = max(maxVal[i] + newMax - intermedMax, newMin/1.5)

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
    ax.fill_between(theta, minArray, maxArray, alpha=0.3, color=color2)


def main(name, title, cat, values, errors, minRange, maxRange):
    N = len(values)
    theta = radar_factory(N, frame='polygon')

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.85, bottom=0.05)

    # recounting
    minVal, maxVal, newMin, newMax = data_recount(values, errors, minRange, maxRange)

    plt.yticks([], [])
    ax.set_title(title,  position=(0.5, 1.1), ha='center')

    # reference
    plotting(ax, theta, [newMin]*N, [newMax]*N, color='blue')

    # case
    plotting(ax, theta, minVal, maxVal, color='orange')

    ax.set_varlabels(map('\n'.join, zip(cat, map(lambda x: str(x), values))))

    # labelling
    for i in range(N):
        plt.text(theta[i], newMin * (1+0.02), minRange[i], size=7)
        plt.text(theta[i], newMax * (1+0.02), maxRange[i], size=7)

    m, M = ax.get_ylim()
    if M > 1.5*newMax:
        M = 1.5*newMax
    plt.ylim(newMin/1.5, M + 0.5)

    plt.savefig(sys.path[0] + '/' + name)
    plt.show()

'''
# variant 1
name = 'img0'
title = 'Клинический анализ крови'
cat = ['RBC, 10^12/л', 'HGB, г/л', 'PLT, 10^9/л', 'СОЭ, мм/ч',
       'WBC, 10^9/л', 'HCT, %', 'MPV, фл', 'MCH, пг',
       'MCHC, г/л', 'MCV, фл', 'RDW, %']
values = [5, 155, 180, 1, 3.9, 45.6, 10.3, 31.0, 33.8, 91.6, 13.5]
errors = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# errors = [0.1, 10, 10, 0.5, 0.1, 1, 1, 1, 1, 5, 1]
minRange = [4.06, 125, 152, 2, 3.6, 36.7, 7.4, 23.8, 32.5, 73.0, 12.1]
maxRange = [5.63, 163, 348, 10, 10.2, 47.1, 11.4, 33.4, 36.3, 96.2, 16.2]
'''
'''
# variant 2
name = 'img1'
title = 'Клинический анализ крови'
cat = ['RBC, 10^12/л', 'HGB, г/л', 'HCT, %', 'PLT, 10^9/л',
       'СОЭ, мм/ч', 'WBC, 10^9/л', 'MPV, фл',
       'RDW, %', 'MCV, фл', 'MCH, пг', 'MCHC, г/л']
values = [3.9, 112, 34.2, 240, 8, 4.5, 9.3, 21.3, 47.0, 15.0, 31.2]
errors = [i*0.1 for i in values]
# errors = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
minRange = [4.06, 125, 36.7, 152, 2, 3.6, 7.4, 12.1, 73.0, 23.8, 32.5]
maxRange = [5.63, 163, 47.1, 348, 10, 10.2, 11.4, 16.2, 96.2, 33.4, 36.3]
'''
'''
# variant 3
name = 'img2'
title = 'Клинический анализ крови'
cat = ['RBC, 10^12/л', 'HGB, г/л', 'HCT, %', 'PLT, 10^9/л',
       'СОЭ, мм/ч', 'WBC, 10^9/л', 'MPV, фл',
       'RDW, %', 'MCV, фл', 'MCH, пг', 'MCHC, г/л']
values = [3.7, 98, 32.1, 260, 9, 4.7, 8.3, 11.3, 45.0, 13.0, 29.2]
# errors = [i*0.1 for i in values]
errors = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
minRange = [4.06, 125, 36.7, 152, 2, 3.6, 7.4, 12.1, 73.0, 23.8, 32.5]
maxRange = [5.63, 163, 47.1, 348, 10, 10.2, 11.4, 16.2, 96.2, 33.4, 36.3]
'''
'''
# variant 4
name = 'img3'
title = 'Лейкоцитарная формула'
cat = ['WBC, 10^9/л', 'Промиелоциты', 'Миелоциты', 'Метамиелоциты', 'П/я нейтрофилы', 'С/я нейтрофилы', 'Эозинофилы', 'Базофилы', 'Моноциты', 'Лимфоциты']
values = [27, 0, 0, 2, 8, 71, 3, 0, 4, 12]
# errors = [i*0.1 for i in values]
errors = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
minRange = [3, 0, 0, 0, 2, 55, 2, 0, 4, 18]
maxRange = [9, 0.1, 0.1, 0.1, 5, 67, 4, 1, 11, 37]
'''

# variant 5
name = 'img4'
title = 'Лейкоцитарная формула'
cat = ['WBC, 10^9/л', 'Промиелоциты', 'Миелоциты', 'Метамиелоциты', 'П/я нейтрофилы', 'С/я нейтрофилы', 'Эозинофилы', 'Базофилы', 'Моноциты', 'Лимфоциты']
values = [6, 0, 0, 0, 3, 60, 2, 0, 7, 28]
# errors = [i*0.1 for i in values]
errors = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
minRange = [3, -0.1, -0.1, -0.1, 2, 55, 2, 0, 4, 18]
maxRange = [9, 0.1, 0.1, 0.1, 5, 67, 4, 1, 11, 37]


main(name, title, cat, values, errors, minRange, maxRange)