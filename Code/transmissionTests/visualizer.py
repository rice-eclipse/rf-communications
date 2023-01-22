from mpl_toolkits import mplot3d
import numpy
import matplotlib.pyplot as plt
import yaml

# Referneces:
# https://jakevdp.github.io/PythonDataScienceHandbook/04.12-three-dimensional-plotting.html
# https://jakevdp.github.io/PythonDataScienceHandbook/04.02-simple-scatter-plots.html

with open("log.yaml", 'r') as logfile:
    data = yaml.safe_load(logfile)


"""
Variables that would be good to plot:
ping_time
bandwidth
spreading
tx_power
orig_rssi
orig_snr
rssi
snr

Variables that would not be good to plot:
send_time
test_num
"""
disp = {"x":"bandwidth", "y":"spreading", "z":"tx_power", "color":"rssi"}


fig = plt.figure()
ax = plt.axes(projection='3d')


x = []
y = []
z = []
col = []

for point in data:
    x.append(point[disp["x"]])
    y.append(point[disp["y"]])
    z.append(point[disp["z"]])
    col.append(point[disp["col"]])

assert len(x) == len(y) == len(z) == len(col)

ax.scatter3D(numpy.array(x), numpy.array(y), numpy.array(z), c=numpy.array(col), alpha=1, cmap='Reds')

ax.set_xlabel(disp["x"])
ax.set_ylabel(disp["y"])
ax.set_zlabel(disp["z"])

plt.show()