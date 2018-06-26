# Rotation functions
import numpy

def __init__(self):

	a=1

def RX(theta):
	R=numpy.matrix([[1,0,0],[0,numpy.cos(theta),-numpy.sin(theta)],[0,numpy.sin(theta),numpy.cos(theta)]])
	return R

def RY(theta):
	R=numpy.matrix([[numpy.cos(theta),0,numpy.sin(theta)],[0,1,0],[-numpy.sin(theta),0,numpy.cos(theta)]])
	return R

def RZ(theta):
	R=numpy.matrix([[numpy.cos(theta),-numpy.sin(theta),0],[numpy.sin(theta),numpy.cos(theta),0],[0,0,1],])
	return R

def RXYZ(theta_x,theta_y,theta_z,point):
	P=numpy.array([[point[0]],[point[1]],[point[2]]])
	newP=RX(theta_x)*RY(theta_y)*RZ(theta_z)*P
	return numpy.array(newP.reshape(1,3)[0])[0]