# -*- coding: utf-8 -*-
"""
Created on Wed Jan 06 16:55:07 2016

@author: xinchang
"""

from MAPS import *
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from numpy import pi
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
filename="deposition_toolpath.txt"
A=load_MAPS_file(filename)
p0 = list(A[:,0])
p1 = list(A[:,1])
p2 = list(A[:,2])
p0_use=[]
p1_use=[]
p2_use=[]
for i in range(len(p0)):
    p0_use.append(p0[i]-p0[0])
    p1_use.append(p1[i]-p1[0])
    p2_use.append(p2[i]-p2[0])
outfname="tool_path_45.ngc"
outfile=open(outfname,'w')
outfile.writelines(['M102 P30 Q1'])
outfile.close()

for i in range(len(p0)):
    outfile=open(outfname,'a')
    outfile.writelines(['\n'+'G1'+' '+'y'+str(p0_use[i])+' '+'x'+str(p1_use[i])+' '+'z'+str(p2_use[i])+' '+'F220'])
outfile.close()
outfile=open(outfname,'a')
outfile.writelines(['\n'+'M02'])
outfile.close()
ax = p3.Axes3D(fig)
ax.plot3D(p1_use,p0_use,p2_use,'r')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
fig.add_axes(ax)
plt.show()
print "File created successfully!!!"
