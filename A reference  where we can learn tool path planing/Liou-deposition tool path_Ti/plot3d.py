from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d.axes3d import get_test_data

def plot3ddata(points,step_size):
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1, projection='3d')
	w,h=np.shape(points)
	tx=(h-1)*step_size
	ty=w*step_size
	print tx
	X = np.arange(0, 40.1, 0.1)
	print X
	Y = np.arange(0, 10, 0.1)
	X, Y = np.meshgrid(X, Y)
	Z = points
	
	print np.shape(X)
	print np.shape(Y)
	print np.shape(Z)
	surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
	        linewidth=0, antialiased=False)
	longer=max(w*step_size,h*step_size)
	ax.set_ylim3d(-longer/4.,3*longer/4.)
	ax.set_xlim3d(0,longer)
	ax.set_zlim3d(-longer/2.,longer/2.)
	fig.colorbar(surf, shrink=0.5, aspect=10)
	plt.show()

points=np.load('points_cloud.npy')
points=points[:,2]
print np.shape(points)
points=np.reshape(points,(100,401))
print np.shape(points)
print points
plot3ddata(np.array(points),0.1)