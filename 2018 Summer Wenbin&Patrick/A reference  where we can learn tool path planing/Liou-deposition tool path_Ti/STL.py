import numpy
from rotate import *

class STL():
	def __init__(self,filename):
		self.faces=load_STL(filename)
		#b_max,
		b_min,b_max=self.bounds()

		pi=3.1415926
		xcenter=b_min[0]+b_max[0]
		ycenter=b_min[1]+b_max[1]
		zcenter=b_min[2]+b_max[2]
		#self.rotate(pi/2,0,0,[xcenter,ycenter,zcenter]) #for vase,cube,cylinder
		#self.rotate(0,pi/2,0,[xcenter,ycenter,zcenter]) #for for armbracket
                #self.rotate(pi,0,0,[xcenter,ycenter,zcenter]) #for blade
		#self.rotate(0,0,-pi/2,[xcenter,ycenter,zcenter]) # for mouse
		
		b_min,b_max=self.bounds()
		self.move(-b_min)

	def slice(self,point,direction):
		edges=[]
		for F in self.faces:
			if (point[2]>min(F.v1[2],F.v2[2],F.v3[2])) & (point[2]<max(F.v1[2],F.v2[2],F.v3[2])):
				edges.append(F.intersection(point,direction))
				if edges[-1]==None: # remove the result if its not a line
					edges.pop(-1)
			#else: print edges[0].p1
		return edges

	def bounds(self):
		b_max=self.faces[0].v1
		b_min=self.faces[0].v1
		pnts=[]
		for F in self.faces:
			pnts.append(F.v1)
			pnts.append(F.v2)
			pnts.append(F.v3)
		pnts=numpy.array(pnts)
		#print pnts.shape
		b_min=numpy.array([min(pnts[:,0]),min(pnts[:,1]),min(pnts[:,2])])
		b_max=numpy.array([max(pnts[:,0]),max(pnts[:,1]),max(pnts[:,2])])
		return b_min,b_max

	def move(self,delta):
		for i in range(len(self.faces)):
			self.faces[i].move(delta)
	def rotate(self,theta_x,theta_y,theta_z,origin):
		for i in range(len(self.faces)):
			self.faces[i].rotate(theta_x,theta_y,theta_z,origin)


class triangle():
	def __init__(self,v1,v2,v3,normal):          
		self.v1=v1
		self.v2=v2
		self.v3=v3
		self.l1=line(self.v1,self.v2,normal)
		self.l2=line(self.v2,self.v3,normal)
		self.l3=line(self.v3,self.v1,normal)
		self.normal=normal
	def intersection(self,point,direction):
		points=[]
		w1=self.l1.p1-point
		w2=self.l2.p1-point
		w3=self.l3.p1-point
		s1=numpy.dot(direction,w1)
		s2=numpy.dot(direction,w2)
		s3=numpy.dot(direction,w3)

		if (s1==0)&(s2==0)&(s3!=0):
			return line(self.l1.p1,self.l2.p1,self.normal)
		elif (s1==0)&(s3==0)&(s2!=0):
			return line(self.l1.p1,self.l3.p1,self.normal)
		elif (s2==0)&(s3==0)&(s1!=0):
			return line(self.l2.p1,self.l3.p1,self.normal)
		elif (s1==0)&(s2==0)&(s3==0):
			 print "triangle in the slice plane"
		else:
			points.append(self.l1.intersection(point,direction))
			if points[-1]==None:
				points.pop(-1)
			points.append(self.l2.intersection(point,direction))
			if points[-1]==None:	
				points.pop(-1)
			points.append(self.l3.intersection(point,direction))
			if points[-1]==None:
				points.pop(-1)
			if len(points)==2:
				return line(points[0],points[1],self.normal)   
		return
	def move(self,delta):
		self.v1+=delta
		self.v2+=delta
		self.v3+=delta
		self.l1=line(self.v1,self.v2,self.normal)
		self.l2=line(self.v2,self.v3,self.normal)
		self.l3=line(self.v3,self.v1,self.normal)

	def rotate(self,theta_x,theta_y,theta_z,origin):
		self.v1=(RXYZ(theta_x,theta_y,theta_z,self.v1-origin)+origin)
		self.v2=(RXYZ(theta_x,theta_y,theta_z,self.v2-origin)+origin)
		self.v3=(RXYZ(theta_x,theta_y,theta_z,self.v3-origin)+origin)		
		self.normal=RXYZ(theta_x,theta_y,theta_z,self.normal)
		self.l1=line(self.v1,self.v2,self.normal)
		self.l2=line(self.v2,self.v3,self.normal)
		self.l3=line(self.v3,self.v1,self.normal)

class line():
	def __init__(self,p1,p2,normal):
		self.p1=p1
		self.p2=p2
		self.normal=normal
	def intersection(self,point,direction):
		w=self.p1-point
		length=numpy.linalg.norm(self.p2-self.p1)
		u=(self.p2-self.p1)/length
		test=numpy.dot(direction,u)
		if abs(test)>0.0: 
			s=-numpy.dot(direction,w)/test
			if (s<=length)&(s>0):
				return self.p1+s*u
		return None

	def reverse(self):
                temp=self.p1
                self.p1=self.p2
                self.p2=temp

def load_STL(filename): # loads a tab-separated csv file (not really tab or space anymore, uses the sniffer to determine the delimeter
	zoom=1
	stlfile=open(filename)
	faces=[]
	for line in stlfile:
		line = line.lstrip()
		if line.find("facet") == 0:
			v = []
			normal = line.split()[-3:]
			n=numpy.array([float(normal[0]),float(normal[1]),float(normal[2])])

		if line.find("vertex") == 0:
			vertex = line.split()[-3:]
			v.append(numpy.array([float(vertex[0])*zoom,float(vertex[1])*zoom,float(vertex[2])*zoom]))
			if len(v)==3:
				faces.append(triangle(v[0]/24.5,v[1]/24.5,v[2]/24.5,n))

	return faces

def load_STL1(filename): # loads a tab-separated csv file (not really tab or space anymore, uses the sniffer to determine the delimeter
	zoom=1*0.5
	stlfile=open(filename)
	faces=[]

	try:
		alltext=stlfile.read()
	finally:
		stlfile.close()


	stlfile=open(filename, 'w')

	alltext.replace("outer loop"," ")
	alltext.replace("endloop"," ")
	alltext.replace("endfacet"," ")
	
	stlfile.write(alltext)
	stlfile.close()

	stlfile=open(filename)

	for line in stlfile:
		line = line.lstrip()
		if line.find("facet") == 0:
			v = []
			normal = line.split()[-3:]
			n=numpy.array([float(normal[0]),float(normal[1]),float(normal[2])])

		if line.find("vertex") == 0:
			vertex = line.split()[-3:]
			v.append(numpy.array([float(vertex[0])*zoom,float(vertex[1])*zoom,float(vertex[2])*zoom]))
			if len(v)==3:
				faces.append(triangle(v[0]/24.5,v[1]/24.5,v[2]/24.5,n))

	print "load end"
	
	return faces

