
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

class SegmentBound:
    def __init__(self, startX, startY, endX, endY):
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY

class ViaBound:
    def __init__(self, xPos, yPos, aperture):
        self.xPos = xPos
        self.yPos = yPos
        self.aperture = aperture



