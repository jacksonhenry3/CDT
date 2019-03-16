import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import pylab as pl
import scipy as sp
import numpy as np

ax = a3.Axes3D(pl.figure())
for i in range(10):
    vtx = np.array([[0, 0, 0], [0, 2, 0], [0, 2, 2]])
    tri = a3.art3d.Poly3DCollection([vtx])
    tri.set_color(colors.rgb2hex(sp.rand(3)))
    tri.set_edgecolor('k')
    ax.add_collection3d(tri)
pl.show()
