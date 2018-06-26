from parameter import *
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3    # new stuff from matplotlib for 3D plotting
import pylab as p
from math import *

from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

def py_ang(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'    """
    cosang = np.dot(v1, v2)
    sinang = np.linalg.norm(np.cross(v1, v2))
    return np.arctan2(sinang, cosang)

class toolpath():

        def __init__(self,sliceresult,parameter):

            self.para=parameter
            self.interval=self.para.diameter-self.para.overlap
            self.sliceresult=sliceresult

        def sections(self,n1,n2):

            sections=self.sectionofcontour(n1,n2)
            return sections
        def toolpath(self,n1,n2):

            sections=self.sections(n1,n2)
            toolpath=self.generatetoolpath(sections,n1,n2)

            return toolpath

        def layerbound(self,layer):

            points=[]
            for contour in layer:
                for line in contour:
                    points.append([line.p1[0],line.p1[1],line.p1[2]])

            points=np.array(points)
            bound=[]
            bound.append([min(points[:,0]),max(points[:,0])])
            bound.append([min(points[:,1]),max(points[:,1])])

            return bound

        def sortsection(self,singlesection,n):

            sortline=[]
            for i in range(len(singlesection)-1):
                for j in range(len(singlesection)-i-1):
                    p1=np.dot(singlesection[i][0:3],n)
                    p2=np.dot(singlesection[i+j+1][0:3],n)
                    if p1>p2 :
                        temp=[singlesection[i][0],singlesection[i][1],singlesection[i][2],singlesection[i][3]]
                        singlesection[i]=singlesection[i+j+1]
                        singlesection[i+j+1]=temp
            for k in range(len(singlesection)/2):
                sortline.append([singlesection[2*k],singlesection[2*k+1]])
            return sortline

        def sectionofcontour(self,n1,n2):

            sections=[]
            num=0

            for layer in self.sliceresult:
                finallayersection=[]
                if num%2==0:
                    finallayersection=self.section(layer,n1,n2,-1)
                else:
                    finallayersection=self.section(layer,n2,n1,-1)
                num=num+1
                sections.append(finallayersection)
            return sections
        def offset_section(self,singlesection):
            singlesection=np.array(singlesection)
            new_singlesection=[]
            for i in range(len(singlesection)):
                p0=np.array([singlesection[i][0][0],singlesection[i][0][1],singlesection[i][0][2]])
                p1=np.array([singlesection[i][1][0],singlesection[i][1][1],singlesection[i][1][2]])
                u=p1-p0
                if np.linalg.norm(u)>2*self.para.offset:
                    u=u/np.linalg.norm(u)
                    p0=p0+self.para.offset*u
                    p1=p1-self.para.offset*u
                    singlesection[i][0]=np.array([p0[0],p0[1],p0[2],singlesection[i][0][3]])
                    singlesection[i][1]=np.array([p1[0],p1[1],p1[2],singlesection[i][1][3]])
                    new_singlesection.append([singlesection[i][0],singlesection[i][1]])
            return new_singlesection
        def section(self,layer,n1,n2,layer_n):
            layersection=[]
            singlesection=[]
            bound=self.layerbound(layer)
            n1=n1/np.linalg.norm(n1)
            n2=n2/np.linalg.norm(n2)
            x_center=(bound[0][1]+bound[0][0])/2.0
            y_center=(bound[1][1]+bound[1][0])/2.0
            cp=np.array([x_center,y_center,0])
            n=0
            while(1):
                if n==0:
                    point=cp
                elif n%2==0:
                    point=cp+(n/2)*self.interval*(layer_n*n1)
                elif n%2==1:
                    point=cp+(n/2+1)*self.interval*(-layer_n*n1)
                singlesection=self.slice(layer,point,n1)
                if len(singlesection)>=2:
                    singlesection=self.sortsection(singlesection,n2)
                    singlesection=self.offset_section(singlesection)
                    if len(singlesection)>0:
                        if n%2==0:
                            layersection.insert(0,singlesection)
                        else:
                            layersection.insert(len(layersection),singlesection)
                    flag=0
                else:
                    flag=flag+1
                n=n+1
#                print n,np.shape(layersection)
                if flag==2:
                    break
            finallayersection=[]
            for i in range(len(layersection)):
                for j in range(len(layersection[i])):
                    finallayersection.append(layersection[i][j])
            return finallayersection
        def min_start(self,last_p,start_s):
            last_p=np.array([last_p[0],last_p[1],last_p[2]])
            p0=np.array([start_s[0][0],start_s[0][1],start_s[0][2]])
            p1=np.array([start_s[1][0],start_s[1][1],start_s[1][2]])
            if np.linalg.norm(p0-last_p)<= np.linalg.norm(p1-last_p):
                return 0
            else:
                return 1
        def find_min(self,last_p,s_candidate):
            last_p=np.array([last_p[0],last_p[1],last_p[2]])
            min_d=10000
            i=0
            for s in s_candidate:
                cc=np.array(s[0][0][0:3]+s[0][1][0:3])/2.0
                if np.linalg.norm(last_p-cc)<min_d:
                    min_s=s[0]
                    min_i=s[1]
                    min_d=np.linalg.norm(last_p-cc)
            return min_s,min_i
        def generatetoolpath(self,sections,n1,n2):

            toolpath=[]
            num=0
            n=[]
            n.append(n1)
            n.append(n2)
            return_p=np.array([sections[0][0][0][0],sections[0][0][0][1],sections[-1][0][0][2]])
            print return_p
            for layersection,layer in zip(sections,self.sliceresult):
                con_i=0
                for contour in layer:
                    for line in contour:
                        toolpath.append([line.p1[0],line.p1[1],line.p1[2],con_i,1])
                    toolpath.append([contour[0].p1[0],contour[0].p1[1],contour[0].p1[2],con_i,0])
                    con_i=con_i+1
                while len(layersection)!=0:
#                    head=self.min_start(toolpath[-1],layersection[0])
                    head=0
                    toolpath.append([layersection[0][head][0],layersection[0][head][1],layersection[0][head][2],layersection[0][head][3],1])
                    toolpath.append([layersection[0][1-head][0],layersection[0][1-head][1],layersection[0][1-head][2],layersection[0][1-head][3],0])
                    layersection.pop(0)
                    while len(layersection)!=0:
                        i=0
                        s_candidate=[]
                        for s in layersection:
                            cp=(np.array(toolpath[-1][0:3])+np.array(toolpath[-2][0:3]))/2.0
                            cc=np.array(s[0][0:3]+s[1][0:3])/2.0
                            v=abs(np.dot(cp,n[num%2])-np.dot(cc,n[num%2]))
                            if (v<1.01*self.interval):
                                s_candidate.append([s,i])
                            i=i+1
                        if len(s_candidate)>0:
#                            print len(s_candidate)
                            s,min_i=self.find_min(toolpath[-1],s_candidate)
                            if head==0:
#                                if (toolpath[-1][3]==s[1][3]):
                                        #print 'a'
                                        toolpath.append([s[1][0],s[1][1],s[1][2],s[1][3],1])
                                        toolpath.append([s[0][0],s[0][1],s[0][2],s[0][3],0])
                                        layersection.pop(min_i)
                                        head=1
                            else:
#                                if (toolpath[-1][3]==s[0][3]):
                                        #print 'b'
                                        toolpath.append([s[0][0],s[0][1],s[0][2],s[0][3],1])
                                        toolpath.append([s[1][0],s[1][1],s[1][2],s[1][3],0])
                                        layersection.pop(min_i)
                                        head=0
                        else:
                            break
#
#                for contour in layer:
#                    for line in contour:
#                        toolpath.append([line.p1[0],line.p1[1],line.p1[2],con_i,1])
#                    toolpath.append([contour[0].p1[0],contour[0].p1[1],contour[0].p1[2],con_i,0])
#                    con_i=con_i+1

                num=num+1
            toolpath.append([return_p[0],return_p[1],return_p[2],0,0])
            return toolpath

        def slice(self,layer,point,direction):

            points=[]

            for i in range(len(layer)):
                for lines in layer[i]:
                    temp=lines.intersection(point,direction)
                    if temp is not None:
                        points.append([temp[0],temp[1],temp[2]])

                    else:
                        points.append(temp)
                    if points[-1] is None:
                        points.pop(-1)
                    else:
                        points[-1].append(i)

            return points
        def plotting2(self,points_cloud,SHSlice_layer_points):

            fig=p.figure()    # these are the two additional lines
            ax = p3.Axes3D(fig)
            pnts=[]
            for point in points_cloud:
                if point[2]<=-0.4:
                    pnts.append(point)
            pnts=np.array(pnts)
            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'g.')

            pnts=[]
            for layer in SHSlice_layer_points:
                for contour in layer:
                    pnts=[]
                    for line in contour:
                        pnts.append(line.p1)
                    pnts.append(line.p2)
                    pnts=np.array(pnts)
                    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'ro',linewidth=2)    # plotting the surface points

            '''
            for i in range(len(ToolPath)):
                for j in range(len(ToolPath[i])):
                    pnts=[]
                    for m in range(len(ToolPath[i][j])):
                        pnts.append(ToolPath[i][j][m])
                    pnts=np.array(pnts)
                    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')    # plotting the surface points
            '''
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_aspect('equal')
            MAX = 10
            for direction in (0, 1):
                for point in np.diag(direction * MAX * np.array([1,1,1])):
                    ax.plot([point[0]], [point[1]], [point[2]], 'w')
            ax.axis('off')
            ax.grid(b=False)
            ax.set_axis_bgcolor('white')
            ax.patch.set_facecolor('white')
            ax.margins(0,0,0)
            maxv=max(np.max(pnts[:,0]),np.max(pnts[:,1]))

            print maxv
            '''
            ax.set_xlim3d(-maxv/4.,3*maxv/4.)
            ax.set_ylim3d(0,maxv)
            '''
#            ax.set_zlim3d(-2,0)

            fig.add_axes(ax)
            p.show()
        def smooth(self,p0,p1,n0,n1):

            n0=np.array([n0[0],n0[1],n0[2]])
            n1=np.array([n1[0],n1[1],n1[2]])
            u=n0/np.linalg.norm(n0)
            v=n1/np.linalg.norm(n1)
            t=np.arange(0,0.5+0.01,0.01)
            points=[]
            r=1
#            points.append([p0[0],p0[1],p0[2],0])
#            points.append([p1[0],p1[1],p1[2],1])
            for j in t:
                ft=sin(pi*j)
                gt=1-cos(pi*j)
                wt=(1-cos(2*pi*j))/2.0
                s=p0+r*ft*u+r*gt*v+wt*(p1-p0-r*u-r*v)
                points.append([s[0],s[1],s[2],0])
            points[-1][3]=1
            return points

        def plotting3(self,points_cloud,SHSlice_layer_points,ToolPath):

            fig=p.figure()    # these are the two additional lines
            ax = p3.Axes3D(fig)
            f=[]
            points=[]
            f=open("deposition_toolpath.txt","w")
            power_deposition=255
            pnts=[]

            for i in range(len(ToolPath)-2):
                pnts=[]
                pnts.append(ToolPath[i])
                pnts.append(ToolPath[i+1])
                pnts=np.array(pnts)

                if ToolPath[i][4]==1:
                    curr_dir=pnts[1][0:3]-pnts[0][0:3]
                    if (i!=0):
                        if (abs(py_ang(curr_dir,pre_dir))>pi/5.0):
                            smooth_points=self.smooth(pnts[0][0:3],pnts[0][0:3],pre_dir,curr_dir)
                            pnts_connection=np.array(smooth_points)
                            ax.plot3D(pnts_connection[:,0],pnts_connection[:,1], pnts_connection[:,2], 'r-',linewidth=2.5)    # plotting the surface points
                            for pc in pnts_connection:
                                f.write("%.3f, "%(pc[0])+"%.3f, "%(pc[1])+"%.3f, "%(pc[2])+"%d\n"%(pc[3]*power_deposition))
                        else:
                            f.write("%.3f, "%(ToolPath[i][0])+"%.3f, "%(ToolPath[i][1])+"%.3f, "%(ToolPath[i][2])+"%d\n"%(ToolPath[i][4]*power_deposition))
                    else:
                        f.write("%.3f, "%(ToolPath[i][0])+"%.3f, "%(ToolPath[i][1])+"%.3f, "%(ToolPath[i][2])+"%d\n"%(ToolPath[i][4]*power_deposition))
                    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-',linewidth=2.5)
#                    a=Arrow3D([ToolPath[i][0],ToolPath[i+1][0]],[ToolPath[i][1],ToolPath[i+1][1]],[ToolPath[i][2],ToolPath[i+1][2]], mutation_scale=20, lw=1, arrowstyle="-|>", color="b")
#                    ax.add_artist(a)
                else:
                    curr_dir=np.array(ToolPath[i+2])[0:3]-np.array(ToolPath[i+1])[0:3]
                    smooth_points=self.smooth(pnts[0][0:3],pnts[1][0:3],pre_dir,curr_dir)
                    pnts_connection=np.array(smooth_points)
                    ax.plot3D(pnts_connection[:,0],pnts_connection[:,1], pnts_connection[:,2], 'r-',linewidth=2.5)    # plotting the surface points
                    smooth_points.pop(-1)
                    pnts_connection=np.array(smooth_points)
                    for pc in pnts_connection:
                        f.write("%.3f, "%(pc[0])+"%.3f, "%(pc[1])+"%.3f, "%(pc[2])+"%d\n"%(pc[3]*power_deposition))

                pre_dir=curr_dir
            f.write("%.3f, "%(ToolPath[-2][0])+"%.3f, "%(ToolPath[-2][1])+"%.3f, "%(ToolPath[-2][2])+"%d\n"%(ToolPath[-1][4]*power_deposition))
            f.write("%.3f, "%(ToolPath[-1][0])+"%.3f, "%(ToolPath[-1][1])+"%.3f, "%(ToolPath[-1][2])+"%d\n"%(ToolPath[-1][4]*power_deposition))
            f.close()
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_aspect('equal')
            ax.axis('off')
#            MAX = 5
#            for direction in (0, 1):
#                for point in np.diag(direction * MAX * np.array([1,1,1])):
#                    ax.plot([point[0]], [point[1]], [point[2]], 'w')
            ax.grid(b=False)
            ax.set_axis_bgcolor('white')
            ax.patch.set_facecolor('white')
            ax.margins(0,0,0)
#            ax.set_xlim(-500,500)
#            ax.set_ylim(-1800,-1000)
#            ax.set_zlim(-500,500)
            fig.add_axes(ax)
            p.show()








