from math import *
from copy import deepcopy
from Objects import Gerber


def getBoundsGKO(gerbersList, offset):
    bounds = []
    gerber = None

    for line in gerbersList:
        if line.find('%FSLA') != -1:
            gerber = Gerber(int(line[6]), int(line[7]))

        if line.find('%MOIN') != -1:
            gerber.unit = "IN"
            gerber.unitScale = 25.4

        if line.find('D01') != -1:
            # Section of line needed changes based on whether new DCode is supplied
            if line.find('D') == -1:
                draw_to_y = round(gerber.unitScale * int(line[line.find('Y') + 1:line.find('*')]) / 10 ** gerber.decNum + offset[1], 3)
            elif line.find('Y') == -1:
                draw_to_y = start[1]
            else:
                draw_to_y = round(gerber.unitScale * int(line[line.find('Y') + 1:line.find('D01*')]) / 10 ** gerber.decNum + offset[1], 3)
            if line.find('X') == -1:
                draw_to_x = start[0]
            else:
                if(line.find('Y') == -1):
                    draw_to_x = round(gerber.unitScale * int(line[line.find('X') + 1:line.find('D01*')]) / 10 ** gerber.decNum + offset[0], 3)
                else:
                    draw_to_x = round(gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0],3)

            bounds.append([])
            bounds[len(bounds) - 1].append(draw_to_x)
            bounds[len(bounds) - 1].append(draw_to_y)
            start = [draw_to_x, draw_to_y]

        # Checks for nozzle relocation
        elif line.find('D02') != -1:
            if line.find('Y') == -1:
                start_pnt_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('D02*')]) / 10 ** gerber.decNum + offset[0]
                start_pnt_y = start[1]
            elif line.find('X') == -1:
                start_pnt_x = start[0]
            else:
                start_pnt_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                start_pnt_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D02*')]) / 10 ** gerber.decNum + offset[1]
            start_pnt_x = round(start_pnt_x, 3)
            start_pnt_y = round(start_pnt_y, 3)
            bounds.append([])
            bounds[len(bounds) - 1].append(start_pnt_x)
            bounds[len(bounds) - 1].append(start_pnt_y)
            start = [start_pnt_x, start_pnt_y]

    return bounds

# Returns coordinates (x,y) after being rotated around the point rotateCenter
def rotateCoords(x, y, radAngle, rotateCenter):
    coords = []
    coords.append(round(float(rotateCenter[0] + cos(radAngle) * (x - rotateCenter[0]) - sin(radAngle) * (y - rotateCenter[1])), 3))
    coords.append(round(float(rotateCenter[1] + sin(radAngle) * (x - rotateCenter[0]) + cos(radAngle) * (y - rotateCenter[1])), 3))
    return coords


# Raises or lowers nozzle between relocations, to prevent material/nozzle collision
def moveNoz(draw_trace, stop_lift):
    if(stop_lift > 0):
        message = "Lifting Nozzle"
        startSpacing = '\n'
        endSpacing = ''
    else:
        message = "Lowering Nozzle"
        startSpacing = ''
        endSpacing = '\n'
    draw_trace.append(startSpacing + 'G91\n')
    draw_trace.append('G0 Z' + str(stop_lift) + message + '\n')
    draw_trace.append('G90\n' + endSpacing)


def raster(segments, lineThickness):
    # Gets lists of segment starting and ending X positions
    xStarts = [item[0] for item in segments]
    xEnds = [item[1] for item in segments]

    # Finds smallest and largest of all X positions
    xMin = min(min(xStarts), min(xEnds))
    xMax = max(max(xStarts), max(xEnds))

    # Starts at leftmost point
    x = xMin + lineThickness
    rastList = []

    # Creates raster list, in order of increasing X
    while x <= xMax - lineThickness:
        for segment in segments:

            # If part of segment falls on current X, add point to list of points
            if min(segment[0], segment[1]) <= x <= max(segment[0], segment[1]):
                rastList.append([])
                rastList[len(rastList) - 1].append(round(x, 3))
                rastList[len(rastList) - 1].append(round(((segment[3] - segment[2]) * x + (segment[2] * segment[1]) - segment[3] * segment[0]) / (segment[1] - segment[0]), 3))

                # If segment is part of Via, add Via hole ID number to point
                if len(segment) == 5:
                    rastList[len(rastList) - 1].append(segment[4])
        x += lineThickness

    count = 0
    # Sorts points with same X values by Y
    while count < len(rastList):
        xNum = 1  # How many points with this x value there are

        # Checks number of points that have the same x value as the current point
        while xNum + count < len(rastList) and rastList[count][0] == rastList[count + xNum][0]:
            xNum += 1

        # Sorts all points with same X by Y
        rastList[count:count + xNum] = sorted(rastList[count:count + xNum], key=lambda lam: lam[1])
        count = count + xNum

    count = 0
    currViaNum = -1
    # Deletes any Via points that are not on the edges
    while count < len(rastList) - 1:
        if len(rastList[count]) == 3:
            if currViaNum != rastList[count][2]:
                currViaNum = rastList[count][2]
                # Delete point if next one is not from same via (1 point is not enough for raster)
                if len(rastList[count + 1]) != 3 or rastList[count + 1][2] != currViaNum:
                    del rastList[count]
                    count -= 1
            # Delete point if next one is from same via (3 points are too many for raster)
            elif len(rastList[count + 1]) == 3 and rastList[count + 1][2] == currViaNum:
                del rastList[count]
                count -= 1
        else:
            currViaNum = -1
        count += 1
    finalList = []
    tempList = deepcopy(rastList)




    # Orders points by how they will be printed
    while len(rastList) > 0:
        count = 0
        #Adds pairs of points to list
        while count < len(rastList) - 1:
            finalList.append(deepcopy(rastList[count]))
            finalList.append(deepcopy(rastList[count + 1]))
            tempList[count] = [0, 'None']
            tempList[count + 1] = [0, 'None']
            # Skips any points that have same X value as current pair
            while (count < len(rastList) - 1 and rastList[count][0] == rastList[count + 1][0]):
                count += 1
            count += 1
        rastList.clear()
        # Fills rastList with all remaining point pairs
        for obj in tempList:
            if obj[1] != 'None':
                rastList.append(deepcopy(obj))
        tempList = deepcopy(rastList)

    count = 0
    while count < len(finalList) - 1:
        # Swap every other pair of points to follow raster path
        if count / 2 % 2 == 0:
            temp = finalList[count]
            finalList[count] = finalList[count + 1]
            finalList[count + 1] = temp

        # Move higher point down and lower point up to account for thickness
        if finalList[count][1] > finalList[count+1][1]:
            finalList[count][1] -= lineThickness
            finalList[count + 1][1] += lineThickness
        else:
            finalList[count][1] += lineThickness
            finalList[count + 1][1] -= lineThickness
        count += 2

    return finalList

def fillVias(draw_trace, vias, noz2Offset, noz2coeff, stop_lift):

    for via in vias:
        fillTime = pi * via.radius * via.radius * noz2coeff
        moveNoz(draw_trace, float(stop_lift))
        draw_trace.append('G0 X' + str(via.xPos + noz2Offset[0]) + ' Y' + str(via.yPos + noz2Offset[1]) + '\n')
        moveNoz(draw_trace, -float(stop_lift))
        draw_trace.append("M121; Start Fill Via\n")
        draw_trace.append("G4 P" + str(fillTime) + "; Start dwell\n")
        draw_trace.append("M120; Stop Fill Via\n")
