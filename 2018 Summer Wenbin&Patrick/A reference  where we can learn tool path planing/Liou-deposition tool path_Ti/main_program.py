from parameter import *
from toolpath import *
from modelslice import *
import numpy as np
from STL import *
from getslice import *
from generate_code_for151 import *

n1=np.array([-1,1,0])
n2=np.array([1,1,0])

n1=n1/np.linalg.norm(n1)
n2=n2/np.linalg.norm(n2)

normal=np.array([0,0,1])
para=parameter()
getslice_obj=getslice('scan_data - Copy.csv')
points_cloud=getslice_obj.read_points()

layerresult,sliceresult=getslice_obj.points_slice()
#print 'total layers:'+repr(int(np.shape(sliceresult)[0]))
tp=toolpath(sliceresult,para)

toolpathresult=tp.toolpath(n1,n2)

#print np.shape(points_cloud)
tp.plotting2(points_cloud,sliceresult)

tp.plotting3(points_cloud,sliceresult,toolpathresult)
generate_code_for151('repair.txt')
generate_code_for151('preheat.txt')