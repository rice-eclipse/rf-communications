from mpl_toolkits import mplot3d
import numpy
import matplotlib.pyplot as plt
import yaml
import random

# Referneces:
# https://jakevdp.github.io/PythonDataScienceHandbook/04.12-three-dimensional-plotting.html
# https://jakevdp.github.io/PythonDataScienceHandbook/04.02-simple-scatter-plots.html


def load_data_from_file(config, datafile):
    # Datafile must be .tsv (or equivalently-formatted)

    with open(config, 'r') as c:
        config_dict = yaml.safe_load(c)
        data_order = config_dict["data_order"]

    data_order.extend(["rssi", "snr"])

    data = []
    with open(datafile, 'r') as d:
        for line in d.readlines():
            line_data = line.split("\t")
            data.append([float(p) for p in line_data])

    return data_order, data


fig = plt.figure()
ax = plt.axes(projection='3d')

data_order, data = load_data_from_file("pingtestconfig.yaml", "log.tsv")

x = []
y = []
z = []
col = []

for point in data:
    x.append(point[data_order.index("bandwidth")])
    y.append(point[data_order.index("spreading")])
    z.append(point[data_order.index("tx_power")])
    col.append(point[data_order.index("rssi")])

assert len(x) == len(y) == len(z) == len(col)
print("Assertion successful")

ax.scatter3D(numpy.log(numpy.array(x)), numpy.array(y), numpy.array(z), c=numpy.array(col), alpha=1, cmap='Reds')
# plt.colorbar()  # show color scale
# plt.colorbar is not working for some reason. Not worth fixing

# Axes labels
ax.set_xlabel('Log of Bandwidth')  # This is log to make the graph more readable. Trends should be unchanged
ax.set_ylabel('Spreading')
ax.set_zlabel('Transmission Power')

# This causes the graph to glitch out; don't use it
# ax.set_ylim3d(min(x), max(x))
# ax.set_xlim3d(min(y), max(y))
# ax.set_zlim3d(min(z), max(z))

# Example, could be removed. Helpful in case something goes wrong
# zdata = 15 * numpy.random.random(100)
# xdata = numpy.sin(zdata) + 0.1 * numpy.random.randn(100)
# ydata = numpy.cos(zdata) + 0.1 * numpy.random.randn(100)
# ax.scatter3D(xdata, ydata, zdata, c=zdata, cmap='Greens')
# plt.colorbar()

plt.show()
