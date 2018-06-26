# Class and supporting functions for building MAPS post processors
import csv
import numpy
import math

class MAPS:
	'''Class for handling the MAPS intermediary data format.'''
	def __init__(self,filename='',units=''):
		try:
			raw_data=load_MAPS_file(filename)
		except IOError:
			print "Ooops! You must provide a valid file name!"
		self.units=units
		self.path=raw_data[:,0:3]
		self.normals=raw_data[:,3:6]
		self.height=raw_data[:,6]
		self.delta_t=raw_data[:,7]
		self.time=sum_time(self.delta_t)
		self.rotations=find_unique_rotations(self.normals)

	def position(self,t):
		'''Interpolates a position at time t from the list of positions.'''
		#find the indices where t[i]<=t<t[i+1]
		i=numpy.nonzero(self.time<=t)[0][-1]
		portion=(t-self.time[i])/self.delta_t[i+1]
		return self.path[i]+portion*(self.path[i+1]-self.path[i])

	def speed(self,t):
		'''Computes the speed at time t.'''
		#find the indices where t[i]<=t<t[i+1]
		i=numpy.nonzero(self.time<=t)[0][-1]
		distance=numpy.linalg.norm(self.position(i+1)-self.position(i))
		delta_t=self.time(i+1)-self.time(i)
		return distance/delta_t*1000

	def accurate_interpolation(self,t,delta_t):
		'''Returns a tuple containing position, normal, and speed arrays at time t from the list of positions.  It also returns any hard vertices found between time t-delta_t and time t.'''
		points=[] # initialze points container
		normals=[] # initialize normals container
		speeds=[] # initialize speed container
		i_s=numpy.nonzero(self.time<=t-delta_t)[0][-1] # find starting index of time period
		i_e=numpy.nonzero(self.time<=t)[0][-1] # find ending index of time period
		if i_s>i_e: # if the time period spans any hard points, add the data for each of those points
			for i in numpy.arange(i_s,i_e+1):
				points.append(self.path[i,:])
				normals.append(self.normals[i,:])
				speeds.append(self.speed(self.time(i)))
		points.append(self.position(t))
		normals.append(self.normal(t))
		speeds.append(self.speed(t))
		return numpy.array(points), numpy.array(normals), numpy.array(speeds)

	def normal(self,t):
		'''Interpolates a position at time t from the list of positions.'''
		#find the indices where t[i]<=t<t[i+1]
		i=numpy.nonzero(self.time<=t)[0][-1]
		portion=(t-self.time[i])/self.delta_t[i+1]
		return self.normals[i]+portion*(self.normals[i+1]-self.normals[i])

	def find_origin(self):
		return numpy.amin(self.path,axis=0)

	#def convert_units(self,new_unit):
	
def find_unique_rotations(normals):
	'''finds the indices at which each rotation begins'''
	indices=[0]
	i=0
	while i<numpy.shape(normals)[0]:
		if not(numpy.array_equal(normals[i,:],normals[indices[-1],:])):
			indices.append(i)
		i+=1
	return indices

def sum_time(dt):
	totals=[0]
	for i in range(1,numpy.shape(dt)[0]):
		totals.append(totals[-1]+dt[i])
	return numpy.array(totals)

def load_MAPS_file(filename): # loads a tab-separated csv file (not really tab or space anymore, uses the sniffer to determine the delimeter
	'''Loads the MAPS path file and converts it into a numpy array.'''
	csvfile=open(filename)
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	f=csv.reader(open(filename),dialect)
	lines=[]
	for line in f:
		current=[]
		for number in line:
        		current.append(float(number))
		lines.append(current)
	return numpy.array(lines)

def compute_length(points):#computes the tool path length
	distance=0
	for i in range(1,len(points)):
		distance+=numpy.linalg.norm(numpy.array(points[i])-numpy.array(points[i-1]))
	return distance
		
def find_start(path,offset): #compute a safe tool starting location for entering the path tangentially
	P1=path[0,:] # first point
	P2=path[1,:] # second point
	return P1-offset*(P2-P1)/numpy.linalg.norm(P2-P1)

def convert_units(path,units):
	scale=1
	if self.units=="in" and units=="mm": # assume inch to millimeter
		scale=25.4
	if self.units=="mm" and units=="in":
		scale=1/25.4 # assume millimeter to inch
	return path*scale

def fix_bound_box(P):
	return P-find_origin(P)
