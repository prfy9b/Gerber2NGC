# -*- coding: utf-8 -*-
"""
Created on Mon May 05 16:53:38 2014

@author: Renwei
"""
import csv
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3    # new stuff from matplotlib for 3D plotting
import pylab as plt
#read csv file 
def read_points(filename):
    points=[]
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            points.append([float(row[0])*25.4-104.459786 ,float(row[1])*25.4+366.63249,float(row[2])])
    return points   

def plot(points):
    fig=plt.figure()    # these are the two additional lines            
    ax = p3.Axes3D(fig)
    pnts=[]
    for i in range(len(points)):
#        print points[i]
        if(points[i][1]>20.37) & (points[i][1]<60.37):
            if points[i][0]<20:
                pnts.append(points[i])
    pnts=np.array(sorted(pnts, key=lambda a_entry: a_entry[1]))
    pnts=np.array(pnts)
    print pnts
    print min(pnts[:,0]),max(pnts[:,0])
    print min(pnts[:,1]),max(pnts[:,1])
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'ro')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim3d(0,150)
    ax.set_zlim3d(-100,100)
    fig.add_axes(ax)
    plt.show()
    np.save('points',points)
        
if __name__ == '__main__':
    points=read_points('wuzemei.txt')
    plot(points)