# -*- coding: utf-8 -*-
"""
Created on Mon May 05 16:53:38 2014

@author: Renwei
"""
import csv
from STL import *
from modelslice import *
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3    # new stuff from matplotlib for 3D plotting
import pylab as p
from parameter import *
#points = np.random.rand(30, 2)
#read csv file
class getslice():
        def __init__(self,filename):
            self.para=parameter()
            self.filename=filename
        def read_points(self):
            points=[]
            scale=1.0
            flag=0
            i=0
            with open(self.filename, 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    i=i+1
#                    if i%4==0:
                    try:
                        p=np.array([scale*float(row[0]),scale*float(row[1]),(-scale)*float(row[2])])
#                        print p
                    except ValueError:
                        print "Oops!  There is no valid number."
                        flag=1
                    if flag==0:
                        if abs(p[2])>100:
                            points.append(points[-1])
                        else:
                            points.append(p)
                    else:
                        flag=0
                print len(points)
            minz=np.min(np.array(points)[:,2])
            maxz=np.max(np.array(points)[:,2])
            print minz,maxz
            for i in range(len(points)):
                points[i][2]=points[i][2]-maxz
            np.save('points_cloud',points)
            return points
        #get the points close to a plane
        def points_slice(self):
            points_cloud=self.read_points()
            sliceresult=[]
            layerresult=[]
            bound=[min(numpy.array(points_cloud)[:,2]),max(numpy.array(points_cloud)[:,2])]
            current_height=bound[0]
            direction=np.array([0,0,1])
            print 'points cloud boundary in z direction: %.3f '%bound[0]+'%.3f '%bound[1]
            layernum=int((abs(bound[1]-bound[0])/self.para.layerthickness))
            self.para.layerthickness=abs(bound[1]-bound[0])/layernum
            print layernum,self.para.layerthickness
            for i in range(layernum):
                current_height=bound[0]+i*self.para.layerthickness
                layerslice=[]
                contour=[]
                point=[0,0,current_height]
                layer_points,contour_points=self.findonelayer(points_cloud,point,direction)
                contour_len=len(contour_points)
                if contour_len>3:
                    contour2D= ConvexHull(contour_points[:,0:2])
                    contour=[]
                    for simplex in contour2D.simplices:
                        p1=[contour_points[simplex[0]][0],contour_points[simplex[0]][1],current_height]
                        p2=[contour_points[simplex[1]][0],contour_points[simplex[1]][1],current_height]
                        contour.append(line(np.array(p1),np.array(p2),direction))
                    minstance=modelslice(0.1)
#                    print np.shape(contour)
#                    print contour[0].p1
                    contour=minstance.sort(contour,np.array([0,0,0]))
                    sliceresult.append(numpy.array(contour))
                    layerresult.append(layer_points)
            return layerresult,sliceresult
        def findonelayer(self,points_cloud,point,direction):
            poplist=[]
            layerpoints=[]
            layerpoints_ori=[]
            for i in range(len(points_cloud)):
                p1=np.array(points_cloud[i])-np.array(point)
                l1=abs(np.dot(p1,direction))
                if l1<self.para.tolerance:
                    poplist.append(i)
                    p2=points_cloud[i]-direction*np.dot(p1,direction)
                    layerpoints.append(p2)
                    layerpoints_ori.append(points_cloud[i])
#                    print p2
#
#            for i in range(len(poplist)):
#                points_cloud.pop(poplist[i]-i)
#            if len(layerpoints)>3:
#                print point
#                print np.array(layerpoints_ori)
            return np.array(layerpoints_ori),np.array(layerpoints)
        def plotting(self,points):
            fig=p.figure()    # these are the two additional lines
            ax = p3.Axes3D(fig)
            pnts=[]
            pnts=np.array(points)
            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'ro')
            ax.set_aspect('equal')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            fig.add_axes(ax)
            p.show()
        #from scipy.spatial import ConvexHull
        #points = np.random.rand(30, 2)   # 30 random points in 2-D
        #hull = ConvexHull(points)
        #
        #import matplotlib.pyplot as plt
        #plt.plot(points[:,0], points[:,1], 'o')
        #for simplex in hull.simplices:
        #    plt.plot(points[simplex,0], points[simplex,1], 'k-')
