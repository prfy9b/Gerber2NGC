from STL import *
import matplotlib.pyplot as plt
import numpy
import mpl_toolkits.mplot3d.axes3d as p3	# new stuff from matplotlib for 3D plotting
import pylab as p

class modelslice():
		def __init__(self,layerthickness):
      
			self.layerthickness=layerthickness
			
		def SHSlice(self,model,model_bound):

			heightp=1.0/24.5;  #should be small than TPI affects the R when caculate TPI at some points, however, the TPI return is the minimal TPI, if will not affect the result
			
			print model_bound[0],model_bound[1]
			n=numpy.array([0,0,1])
			
			firstlayerheight=0.5/25.4  #firstlayerheight=0.82550882-1.0/25.4
			current_height=firstlayerheight
			shslice=[]

			i=0
			begin_point=numpy.array([model_bound[1][0],model_bound[1][1]*0.5,0])
			while (current_height<model_bound[1][2]):
				print i
				layercontour=[]
				i=i+1
				layercontour=self.slicelayer(model,current_height,n,begin_point)
				print len(layercontour)
				#for m in range(len(layercontour)):
					#print "\n\n"
					#for n in range(len(layercontour[m])):
					# print layercontour[m][n].p1
				if i>=1:
					shslice.append(numpy.array(layercontour))
				current_height=current_height+self.layerthickness

			return shslice

		def slicelayer(self,model,h,n,p0):

			p=numpy.array([0,0,h])
			S=model.slice(p,n) #slices the STL file with a plane through point P0 with normal direction n.  returns a list of line objects.
			#print len(S)
			S=self.sort(S,p0)
			#print len(S)
			#S=self.sort(S,p1)

			return S

		def plot(self,S0):
				pnts=[]
				for i in range(len(S0)):
					pnts.append(S0[i])
				pnts=numpy.array(pnts)
				plt.plot(pnts[:,0],pnts[:,1])
				plt.show()

		def plotting(self,SHSlice_layer_points,toolpath):
		#def plotting(self,SHSlice_layer_points):
			
			fig=p.figure()	# these are the two additional lines			
			ax = p3.Axes3D(fig)
			pnts=[]
			for i in range(len(SHSlice_layer_points)):
				pnts.append(SHSlice_layer_points[i].p1)		
			pnts=numpy.array(pnts)
			ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points
					
			pnts=[]
			
			for i in range(len(toolpath)):
				pnts.append(toolpath[i])
			pnts=numpy.array(pnts)
			ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'r-')	# plotting the surface points
			
			ax.set_xlabel('X')
			ax.set_ylabel('Y')
			ax.set_zlabel('Z')
			ax.set_aspect('equal')
			fig.add_axes(ax)
			p.show()

		def plotting1(self,SHSlice_layer_points):
			
			fig=p.figure()	# these are the two additional lines			
			ax = p3.Axes3D(fig)
			pnts=[]

			#print len(SHSlice_layer_points)
			for i in range(len(SHSlice_layer_points)):
				#print len(SHSlice_layer_points)
				for j in range(len(SHSlice_layer_points[i])):
					#print len(SHSlice_layer_points[i])
					pnts=[]
					for k in range(len(SHSlice_layer_points[i][j])):
						#print SHSlice_layer_points[i][j][k].p1
						pnts.append(SHSlice_layer_points[i][j][k].p1)	
					pnts.append(SHSlice_layer_points[i][j][k].p2)
					pnts=numpy.array(pnts)
					ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points	
					'''
					if j==0:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points	
					elif j==1:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points
					elif j==2:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'g-')	# plotting the surface points
					elif j==3:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'y-')	# plotting the surface points
					elif j==4: 
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'm-')	# plotting the surface points
					elif j==5: 
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'c-')	# plotting the surface points
					else : 
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'k-')	# plotting the surface points
					'''
					
			ax.set_xlabel('X')
			ax.set_ylabel('Y')
			ax.set_zlabel('Z')
			ax.set_aspect('equal')
			fig.add_axes(ax)
			p.show()

		def plotting2(self,SHSlice_layer_points,ToolPath):
			
			fig=p.figure()	# these are the two additional lines			
			ax = p3.Axes3D(fig)

			'''
			pnts=[]

			for i in range(len(SHSlice_layer_points)):		
				for j in range(len(SHSlice_layer_points[i])):
					pnts=[]
					for k in range(len(SHSlice_layer_points[i][j])):
						pnts.append(SHSlice_layer_points[i][j][k].p1)	
					pnts.append(SHSlice_layer_points[i][j][k].p2)
					pnts=numpy.array(pnts)
					ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points
					
					if j==0:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points	
					elif j==1:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'r-')	# plotting the surface points
					elif j==2:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'g-')	# plotting the surface points
					elif j==3:
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'y-')	# plotting the surface points
					elif j==4: 
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'm-')	# plotting the surface points
					elif j==5: 
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'c-')	# plotting the surface points
					else : 
						ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'k-')	# plotting the surface points
					

			'''
			pnts=[]	

			for i in range(len(ToolPath)):		
				for j in range(len(ToolPath[i])):			
					pnts=[]			
					for m in range(len(ToolPath[i][j])):
        						pnts.append(ToolPath[i][j][m])
					pnts=numpy.array(pnts)		
					ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points
	
			ax.set_xlabel('X')
			ax.set_ylabel('Y')
			ax.set_zlabel('Z')
			ax.set_aspect('equal')
			fig.add_axes(ax)
			p.show()

		def plotting3(self,SHSlice_layer_points,ToolPath):
			
			fig=p.figure()	# these are the two additional lines			
			ax = p3.Axes3D(fig)
                        f=[]
                        f=open("output\\deposition.txt","w")
                        
			pnts=[]	
                        num=0
                        num2=0
                        for i in range(len(ToolPath)):		
				for j in range(len(ToolPath[i])):			
					pnts=[]
					#print len(ToolPath[i])
					for m in range(len(ToolPath[i][j])):		
						pnts.append(ToolPath[i][j][m])
						num2=num2+1
						#print ToolPath[i][j][m][0],ToolPath[i][j][m][1],ToolPath[i][j][m][2]
						if ((m==0)&(j!=0)):
                                                        num=num+1
							f.write("%.4f "%(ToolPath[i][j][m][0])+"%.4f "%(ToolPath[i][j][m][1])+"%.4f "%(ToolPath[i][j][m][2])+"1\n")
						else:
                                                        num=num+1
							f.write("%.4f "%(ToolPath[i][j][m][0])+"%.4f "%(ToolPath[i][j][m][1])+"%.4f "%(ToolPath[i][j][m][2])+"0\n")
                                        pnts=numpy.array(pnts)
                                        if j==0:
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points	
                                        elif j==1:
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'r-')	# plotting the surface points
                                        elif j==2:
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'g-')	# plotting the surface points
                                        elif j==3:
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'y-')	# plotting the surface points
                                        elif j==4: 
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'm-')	# plotting the surface points
                                        elif j==5: 
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'c-')	# plotting the surface points
                                        else : 
                                            ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'k-')	# plotting the surface points
                        print num,num2
                        f.close()
			ax.set_xlabel('X')
			ax.set_ylabel('Y')
			ax.set_zlabel('Z')
			ax.set_aspect('equal')
			fig.add_axes(ax)
			p.show()
			
                        
		def sort(self,S,point):

				
				layercontour=[]
				k=0
				while(len(S)!=0):
					sorted=[]						
					num,place=self.min_distance2(point,S)
					if place==0:	 						
						sorted.append(S.pop(num))
					else:
						temp=S.pop(num)
						temp.reverse()
						sorted.append(temp)
							
					while len(S)!=0:
						lsb=len(S)
						for i in range(len(S)):
							if numpy.linalg.norm(sorted[-1].p2-S[i].p1)<0.0000001:
								if numpy.linalg.norm(sorted[-1].p1-S[i].p2)>0.0000001:
									sorted.append(S.pop(i))
									break
							elif numpy.linalg.norm(sorted[-1].p2-S[i].p2)<0.0000001:
								if numpy.linalg.norm(sorted[-1].p1-S[i].p1)>0.0000001:						#print "reversed!\n"
									temp=S.pop(i)
									temp.reverse()
									sorted.append(temp)
									break
						lse=len(S)
						if lse==lsb:
							break
					layercontour.append(numpy.array(sorted))
                 
				return layercontour

		def min_distance2(self,point,s):

				mindistance=0.0

				if len(s)==0:
					print "error"

				for i in range(len(s)):		

					distance1=numpy.linalg.norm(point-s[i].p1)
					distance2=numpy.linalg.norm(point-s[i].p2)					
					if distance1<distance2:
						
						if (mindistance==0):
							mindistance=distance1
							minplace=0
							minnum=i
						elif (distance1<mindistance):
							mindistance=distance1
							minplace=0
							minnum=i
					else:
						
						if (mindistance==0):
							mindistance=distance1
							minplace=1
							minnum=i
						elif (distance2<mindistance):
							mindistance=distance2
							minplace=1
							minnum=i
				return minnum,minplace
'''
if j==0:
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'b-')	# plotting the surface points	
elif j==1:
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'r-')	# plotting the surface points
elif j==2:
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'g-')	# plotting the surface points
elif j==3:
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'y-')	# plotting the surface points
elif j==4: 
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'm-')	# plotting the surface points
elif j==5: 
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'c-')	# plotting the surface points
else : 
    ax.plot3D(pnts[:,0],pnts[:,1], pnts[:,2], 'k-')	# plotting the surface points
'''
