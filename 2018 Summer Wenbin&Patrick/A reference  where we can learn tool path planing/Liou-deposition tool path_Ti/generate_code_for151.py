import numpy
import csv

class generate_code_for151():
    def __init__(self,filename):
        laser,positions=self.read_depositepoints(filename)
        self.generate_code(laser,positions,filename)
    def read_depositepoints(self,filename):
            print filename
            points=[]
            laser=[]
            scale=1.0
            flag=0
            with open(filename, 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    try: 
                        p=numpy.array([scale*float(row[0]),scale*float(row[1]),scale*float(row[2])])
                        l=numpy.array([scale*float(row[4])])
                    except ValueError:
                        print "Oops!  There is no valid number."
                        flag=1
                    if flag==0:
                        points.append(p)
                        laser.append(l)
                    else:
                        flag=0
            return laser,points
    def generate_code(self,laser,positions,filename):
        looptimer=20e-6
        #feed_rate=1200 #mm/minute
        feed_rate=600
        filename[-3]
        outfname=filename[0:-4]+"_deposition_for151.txt"
        laser.append(0)
        positions=numpy.array(positions)
#        print positions,numpy.shape(positions)
        
        incremental=numpy.diff(positions,n=1,axis=0) # incremental mode
        stepsdata=numpy.round(incremental/0.002,0) # step space
        
        steps_per_loop=(feed_rate/60.0)/(0.002)*looptimer
        
        #populate the time column
        T=numpy.apply_along_axis(numpy.linalg.norm, 1, stepsdata)/steps_per_loop
        T[numpy.nonzero(T>2**32-1)]=2**32-1
        
        outfile=open(outfname,'w')
        for i in range(len(stepsdata)):
            outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(int(stepsdata[i,0]),int(stepsdata[i,1]),int(stepsdata[i,2]),int(T[i]),int(laser[i])))
        outfile.close()
