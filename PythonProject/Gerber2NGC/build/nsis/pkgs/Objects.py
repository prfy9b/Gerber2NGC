
class Aperture:
    def __init__(self, line, gerber):
        line = line[3:len(line)-1]  # Removes AM and surrounding %'s
        self.code = line[:3]
        self.type = line[3:4]
        self.xLength = -1
        self.yLength = -1
        self.diameter = -1
        self.isPad = False
        if self.type == 'C':
            self.diameter = float(line[line.find(",") + 1:line.find("*")]) * gerber.unitScale
        elif self.type == 'R':
            self.xLength = float(line[line.find(",") + 1:line.find("X")]) * gerber.unitScale
            self.yLength = float(line[line.find("X") + 1:line.find("*")]) * gerber.unitScale
        # If we want, add code for Obrounds and Polygon
        if self.diameter > .4 / gerber.unitScale or self.xLength > .4 / gerber.unitScale or self.yLength > .4 / gerber.unitScale:
            self.isPad = True


class Gerber:
    def __init__(self, intNum, decNum):
        self.intNum = intNum
        self.decNum = decNum
        self.unit = "MM"
        self.unitScale = 1
        self.apertures = {}
        self.polarity = 'D'
        self.xPos = 0
        self.yPos = 0
        self.zPos = 0

class Pad:
    def __init__(self, xPos, yPos, aperture):
        self.aperture = aperture
        self.xPos = xPos
        self.yPos = yPos
        self.xMax = self.xPos + self.aperture.xLength / 2
        self.xMin = self.xPos - self.aperture.xLength / 2
        self.yMax = self.yPos + self.aperture.yLength / 2
        self.yMin = self.yPos - self.aperture.yLength / 2

class Via:
    def __init__(self, xPos, yPos, radius):
        self.xPos = xPos
        self.yPos = yPos
        self.radius = radius



