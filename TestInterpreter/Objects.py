
class Aperture:
    def __init__(self, line):
        line = line[3:len(line - 1):]  # Removes AM and surrounding %'s
        self.code = line[:3]
        self.shape = line[3:4]
        self.xLength = -1
        self.yLength = -1
        self.diameter = -1
        if self.shape == 'C':
            self.diameter = int(line[line.find(",") + 1:line.find("*")])
        elif self.shape == 'R':
            self.xLength = int(line[line.find(",") + 1:line.find("X")])
            self.yLength = int(line[line.find("X") + 1:line.find("*")])
        # If we want, add code for Obrounds and Polygon

class Gerber:
    def __init(self, resolution):
        self.resolution = resolution #Tuple, (integers, decimals)
        self.unit = "MM"
        self.unitScale = 1
        self.apertures = {}


