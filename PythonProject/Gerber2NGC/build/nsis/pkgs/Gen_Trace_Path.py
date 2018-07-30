from sys import platform as sys_pf
from sys import float_info
from Objects import *
from sympy import *
from Helper_Functions import *
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


def gen_trace_path_layer(filename, gerberList, offset, h, stop_lift, angle, rotateCenter, lineThickness, bounds, exuderDelay):
    gerber = None
    gerberLeft = []
    draw_trace = []
    radAngle = angle * 2 * pi / 360
    current_Dcode = ''
    region = False
    pads = []
    start = [0, 0]  # Start point of current trace
    draw_trace.append('G0 Z' + h + '\n')
    keepLine = False

    # First pass, initializes variables and memorizes pads
    for i, line in enumerate(gerberList):
        keepLine = False

        # Checks for initialization line
        if line.find('%FSLA') != -1:
            gerber = Gerber(int(line[6]), int(line[7]))
            continue

        # Checks for unit specification line, defaults to millimeters
        if line.find('%MOIN') != -1:
            gerber.unit = "IN"
            gerber.unitScale = 25.4
            continue

        # Checks for aperture definition line
        if line.find('ADD') != -1:
            gerber.apertures[line[3:6]] = Aperture(line, gerber)
            continue

        # Checks for aperture/DCode selection line
        if line[0] == 'D' and int(line[1:3]) > 9:
            current_aperture = gerber.apertures[line[0:3]]
            keepLine = True
        elif line[len(line) - 5] == 'D':
            current_Dcode = line[len(line) - 5: len(line) - 2]
            keepLine = True


        if line.find("D03") != -1 or (line.find('D') == -1 and current_Dcode == 'D03' and (line.find('X') != -1 or line.find('Y') != -1)): # if D03 found
            keepLine = True
            # Draw outline of rectangle
            if line.find('Y') == -1:
                flash_center_y = start[1]
            else:
                flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                flash_center_x = start[0]
            else:
                flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum  # + offset[0]
            pads.append(Pad(flash_center_x, flash_center_y, current_aperture))

        if line.find('X') != -1:
            keepLine = True
            if line.find('Y') != -1:
                start[0] = round(gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum, 3)
            else:
                start[0] = round(gerber.unitScale * int(line[line.find('X') + 1: line.find('D')]) / 10 ** gerber.decNum,3)
        if line.find('Y') != -1:
            keepLine = True
            start[1] = round(gerber.unitScale * int(line[line.find('Y') + 1: line.find('D')]) / 10 ** gerber.decNum, 3)

        if keepLine:
            gerberLeft.append(line)

    #Second pass, draws everything
    for line in gerberLeft:

        # Checks for aperture/DCode selection line
        if line[0] == 'D' and int(line[1:3]) > 9:
            current_aperture = gerber.apertures[line[0:3]]
        elif line[len(line) - 5] == 'D':
            current_Dcode = line[len(line) - 5: len(line) - 2]

        # Checks for Traces
        if line.find('D01') != -1 or (line.find('D') == -1 and current_Dcode == 'D01' and (line.find('X') != -1 or line.find('Y') != -1)):
            vertical = False
            # Section of line needed changes based on whether new DCode is supplied
            xVal = line[line.find('X') + 1: line.find('Y')]
            yVal = line[line.find('Y') + 1: line.find('D01*')]
            if (line.find('D') == -1):
                yVal = line[line.find('Y') + 1: line.find('*')]
            if line.find('Y') == -1:
                draw_to_y = start[1]
                xVal = line[line.find('X') + 1: line.find('D01*')]
            else:
                draw_to_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                draw_to_x = start[0]
            else:
                draw_to_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum  # + offset[0]

            # If ends of trace have same X value, treat as vertical line. Else, define slope of line
            if draw_to_x - start[0] == 0:
                vertical = True
            else:
                slope = (draw_to_y - start[1]) / (draw_to_x - start[0])

            isBound = False
            for bound in bounds:
                if bound == [start[0], draw_to_x, start[1], draw_to_y]:
                    isBound = True
                    break
            # Move trace to edges of any colliding pads
            for pad in pads:
                # If trace end intersects pad
                if abs(pad.xPos - draw_to_x) < pad.aperture.xLength / 2 and abs(pad.yPos - draw_to_y) < pad.aperture.yLength / 2:
                    currX = start[0]
                    currY = start[1]
                    direction = 1 # Specifies x direction of movement, or y direction if vertical
                    if start[0] > draw_to_x or (vertical and start[1] > draw_to_y):
                        direction = -1
                    # Move across line until edge of pad is hit
                    while abs(pad.xPos - currX) >= pad.aperture.xLength / 2 or abs(pad.yPos - currY) >= pad.aperture.yLength / 2:
                        if vertical:
                            currY += .1 * direction
                            if (draw_to_y - currY) * direction < .1:
                                break
                        else:
                            currX += .1 * direction
                            currY += .1 * slope * direction
                            if (draw_to_x - currX) * direction < .1:
                                break
                    # Move backwards 1 step to prevent collisions
                    if vertical:
                        draw_to_y = currY - .1 * direction
                    else:
                        draw_to_x = currX - .1 * direction
                        draw_to_y = currY - .1 * slope * direction
                # If trace start intersects pad, same as previous code in opposite direction
                if abs(pad.xPos - start[0]) < pad.aperture.xLength / 2 and abs(pad.yPos - start[1]) < pad.aperture.yLength / 2:
                    currX = draw_to_x
                    currY = draw_to_y
                    direction = -1
                    if start[0] > draw_to_x or (vertical and start[1] > draw_to_y):
                        direction = 1
                    while abs(pad.xPos - currX) >= pad.aperture.xLength / 2 or abs(pad.yPos - currY) >= pad.aperture.yLength / 2:
                        if (vertical):
                            currY += .1 * direction
                            if (start[1] - currY) * direction < .1:
                                break
                        else:
                            currX += .1 * direction
                            currY += .1 * slope * direction
                            if (start[0] - currX) * direction < .1:
                                break
                    if vertical:
                        currY -= .1 * direction
                    else:
                        currX -= .1 * direction
                        currY -= .1 * slope * direction
                    start = [currX, currY]

                    moveNoz(draw_trace, float(stop_lift))
                    draw_trace.append('G0 X' + str(start[0]) + ' Y' + str(start[1]) + '\n')
                    moveNoz(draw_trace, -float(stop_lift))
            # Do not print trace if it is a bound, or too small to matter (Testing skip of unnecessary traces)
            if not isBound and (draw_to_x - start[0] >= .2 or draw_to_y - start[1] >= .2):
                draw_trace.append('T1; Layer Trace\n')
                draw_trace.append('M111\n')
                draw_trace.append("G4 P" + str(exuderDelay) + "; Start dwell\n")
                draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' E1 F1200\n')
                draw_trace.append('M110\n')

            start = [draw_to_x, draw_to_y]

        # Checks for nozzle relocation
        elif line.find('D02') != -1 or (line.find('D') == -1 and current_Dcode == 'D02'):  # if D02 found
            xVal = line[line.find('X') + 1: line.find('Y')]
            yVal = line[line.find('Y') + 1: line.find('D02*')]
            if line.find('D') == -1:
                yVal = line[line.find('Y') + 1: line.find('*')]
            if line.find('Y') == -1:
                xVal = line[line.find('X') + 1: line.find('D02*')]
                start_pnt_y = start[1]
            else:
                start_pnt_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                start_pnt_x = start[0]
            else:
                start_pnt_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum  # + offset[0]
            start_pnt_x = round(start_pnt_x, 3)
            start_pnt_y = round(start_pnt_y, 3)
            moveNoz(draw_trace, float(stop_lift))
            draw_trace.append('G0 X' + str(start_pnt_x) + ' Y' + str(start_pnt_y) + ' ;aperture ' + current_aperture.code + ' moving\n')
            moveNoz(draw_trace, -float(stop_lift))
            start = [start_pnt_x, start_pnt_y]

        # Checks for Rectangular flashes (Circular should be in VIAS file)
        elif line.find("D03") != -1 or (line.find('D') == -1 and current_Dcode == 'D03' and (line.find('X') != -1 or line.find('Y') != -1)): # if D03 found
            # Draw outline of rectangle
            if line.find('Y') == -1:
                flash_center_y = start[1]
            else:
                flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                flash_center_x = start[0]
            else:
                flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum  # + offset[0]
            xMax = flash_center_x + current_aperture.xLength / 2 - lineThickness
            xMin = xMax - current_aperture.xLength + lineThickness
            yMax = flash_center_y + current_aperture.yLength / 2 - lineThickness
            yMin = yMax - current_aperture.yLength + lineThickness

            # Temporarily rotated coordinates for rectangle
            bottom_left = rotateCoords(xMin, yMin, radAngle, rotateCenter)
            bottom_right = rotateCoords(xMax, yMin, radAngle, rotateCenter)
            top_right = rotateCoords(xMax, yMax, radAngle, rotateCenter)
            top_left = rotateCoords(xMin, yMax, radAngle, rotateCenter)

            draw_trace.append('T4; Pad Outline\n')
            moveNoz(draw_trace, float(stop_lift))
            draw_trace.append('G0 X' + str(xMin) + ' Y' + str(yMin) + ' ;aperture ' + current_aperture.code + ' moving to flash pos\n')
            moveNoz(draw_trace, -float(stop_lift))
            draw_trace.append('M111\n')
            draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
            draw_trace.append('G1 X' + str(xMin) + ' Y' + str(yMax) + ' E1 F1200\n')
            draw_trace.append('G1 X' + str(xMax) + ' Y' + str(yMax) + ' E1 F1200\n')
            draw_trace.append('G1 X' + str(xMax) + ' Y' + str(yMin) + ' E1 F1200\n')
            draw_trace.append('G1 X' + str(xMin) + ' Y' + str(yMin) + ' E1 F1200\n')
            draw_trace.append('M110\n')
            start = [round(flash_center_x, 3), round(flash_center_y, 3)]

            # Create rotated segments
            segments = []
            segments.append([])
            segments.append([])
            segments.append([])
            segments.append([])
            segments[0] = [bottom_left[0], bottom_right[0], bottom_left[1], bottom_right[1]]
            segments[1] = [bottom_right[0], top_right[0], bottom_right[1], top_right[1]]
            segments[2] = [top_right[0], top_left[0], top_right[1], top_left[1]]
            segments[3] = [top_left[0], bottom_left[0], top_left[1], bottom_left[1]]

            # Make list of raster lines out of rotated segments
            finalList = raster(segments, lineThickness)

            # Unrotate and print lines in order
            draw_trace.append('T3; Pad Filling\n')
            moveNoz(draw_trace, float(stop_lift))
            finalList[0] = rotateCoords(finalList[0][0], finalList[0][1], -radAngle, rotateCenter)
            draw_trace.append('G0 X' + str(round(finalList[0][0], 3)) + ' Y' + str(round(finalList[0][1], 3)) + '\n')
            moveNoz(draw_trace, -float(stop_lift))
            count = 1
            draw_trace.append('M111\n')
            draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
            while count < len(finalList) - 2:
                temp = deepcopy(finalList[count])
                finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(
                    round(finalList[count][1], 3)) + ' E1 F1000\n')

                if (count == len(finalList) - 1):
                    break
                distX = abs(finalList[count + 1][0] - temp[0])
                distY = abs(finalList[count + 1][1] - temp[1])
                if sqrt(distX * distX + distY * distY) > lineThickness * 3:
                    count += 1
                    moveNoz(draw_trace, float(stop_lift))
                    finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                    draw_trace.append('M110\n')
                    draw_trace.append(
                        'G0 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + '\n')
                    draw_trace.append('M111\n')
                    draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                    moveNoz(draw_trace, -float(stop_lift))
                else:
                    count += 1
                    finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                    draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(
                        round(finalList[count][1], 3)) + ' E1 F1000\n')

                count += 1

            draw_trace.append('M110\n')

    return draw_trace


# Like layer function, but rasters bounds at end of file, and supports circular via flashes rather than rectangular
def gen_trace_path_via(filename, gerberList, offset, h, stop_lift, angle, rotateCenter, lineThickness, outputCoeff, exuderDelay, bounds = []):
    gerber = None
    draw_trace = []
    current_Dcode = ''
    segments = [] #xStart, xEnd, yStart, yEnd
    region = False
    radAngle = angle * 2 * pi / 360
    start = []
    viaNum = 0
    vias = []

    draw_trace.append('G0 Z' + h + '\n')

    if bounds != []:
        # Remove identical bounds
        i = 0
        while i < len(bounds) - 1:
            j = i + 1
            while j < len(bounds):
                if bounds[i] == bounds[j]:
                    del bounds[j]
                else:
                    j += 1
            i += 1

        moveNoz(draw_trace, float(stop_lift))
        draw_trace.append('G0 X' + str(bounds[0][0]) + ' Y' + str(bounds[0][1]) + '\n')
        moveNoz(draw_trace, -float(stop_lift))
        draw_trace.append('T4; Layer Border\n')
        draw_trace.append('M111\n')

        count = 1
        while count < len(bounds):
            startCoords = rotateCoords(bounds[count-1][0], bounds[count-1][1], radAngle, rotateCenter)
            endCoords = rotateCoords(bounds[count][0], bounds[count][1], radAngle, rotateCenter)
            segments.append([])
            segments[len(segments) - 1].append(startCoords[0])
            segments[len(segments) - 1].append(endCoords[0])
            segments[len(segments) - 1].append(startCoords[1])
            segments[len(segments) - 1].append(endCoords[1])
            draw_trace.append('G1 X' + str(bounds[count][0]) + ' Y' + str(bounds[count][1]) + ' E1 F1200 ;\n')
            count += 1

        startCoords = rotateCoords(bounds[count - 1][0], bounds[count - 1][1], radAngle, rotateCenter)
        endCoords = rotateCoords(bounds[0][0], bounds[0][1], radAngle, rotateCenter)
        segments.append([])
        segments[len(segments) - 1].append(startCoords[0])
        segments[len(segments) - 1].append(endCoords[0])
        segments[len(segments) - 1].append(startCoords[1])
        segments[len(segments) - 1].append(endCoords[1])
        draw_trace.append('G1 X' + str(bounds[0][0]) + ' Y' + str(bounds[0][1]) + ' E1 F1200 ;\n')

        draw_trace.append('M110\n')


    for i, line in enumerate(gerberList):
        if gerberList[i].find('%FSLA') != -1:
            gerber = Gerber(int(gerberList[i][6]), int(gerberList[i][7]))

        if gerberList[i].find('%MOIN') != -1:
            gerber.unit = "IN"
            gerber.unitScale = 25.4

        if line.find('ADD') != -1:
            gerber.apertures[line[3:6]] = Aperture(line, gerber)

        if line[0:3] == "G36":
            region = True

        if line[0:3] == "G37":
            region = False

        if line[0] == 'D' and int(line[1:3]) > 9:
            current_aperture = gerber.apertures[line[0:3]]
        elif line[len(line) - 5] == 'D':
            current_Dcode = line[len(line) - 5: len(line) - 2]

        if line.find('D01') != -1 or (line.find('D') == -1 and current_Dcode == 'D01'):
            xVal = line[line.find('X') + 1: line.find('Y')]
            yVal = line[line.find('Y') + 1: line.find('D01*')]
            if(line.find('D') == -1):
                yVal = line[line.find('Y') + 1: line.find('*')]
            if line.find('Y') == -1:
                draw_to_y = start[1]
                xVal = line[line.find('X') + 1: line.find('D01*')]
            else:
                draw_to_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                draw_to_x = start[0]
            else:
                draw_to_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum  # + offset[0]

            tempCoords = rotateCoords(draw_to_x, draw_to_y, radAngle, rotateCenter)
            tempStart = rotateCoords(start[0], start[1], radAngle, rotateCenter)
            coords = [round(float(draw_to_x), 3), round(float(draw_to_y), 3)]
            draw_trace.append('T4; Layer Border\n')
            draw_trace.append('M111\n')
            draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
            draw_trace.append('G1 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' E1 F1200 ;aperture ' + current_aperture.code + ' drawing\n')
            draw_trace.append('M110\n')
            # Segments are created by all traces, rather than a flash
            segments.append([])
            segments[len(segments) - 1].append(tempStart[0])
            segments[len(segments) - 1].append(tempCoords[0])
            segments[len(segments) - 1].append(tempStart[1])
            segments[len(segments) - 1].append(tempCoords[1])

            bounds.append([])
            bounds[len(bounds) - 1].append(start[0])
            bounds[len(bounds) - 1].append(coords[0])
            bounds[len(bounds) - 1].append(start[1])
            bounds[len(bounds) - 1].append(coords[1])
            start = coords
        elif line.find('D02') != -1 or (line.find('D') == -1 and current_Dcode == 'D02'):  # if D02 found
            xVal = line[line.find('X') + 1: line.find('Y')]
            yVal = line[line.find('Y') + 1: line.find('D02*')]
            if line.find('D') == -1:
                yVal = line[line.find('Y') + 1: line.find('*')]
            if line.find('Y') == -1:
                xVal = line[line.find('X') + 1: line.find('D02*')]
                start_pnt_y = start[1]
            else:
                start_pnt_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                start_pnt_x = start[0]
            else:
                start_pnt_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum  # + offset[0]
            coords = [start_pnt_x, start_pnt_y]
            coords[0] = round(float(start_pnt_x), 3)
            coords[1] = round(float(start_pnt_y), 3)
            moveNoz(draw_trace, float(stop_lift))
            draw_trace.append('G0 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' ;Moving nozzle\n')
            moveNoz(draw_trace, -float(stop_lift))
            start = coords

        #Checks for circular flashes
        elif line.find("D03") != -1 or (line.find('D') == -1 and current_Dcode == 'D03' and (line.find('X') != -1 or line.find('Y') != -1)):  # if D03 found
            radius = current_aperture.diameter / 2
            if line.find('Y') == -1:
                flash_center_y = start[1]
            else:
                flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum  # + offset[1]
            if line.find('X') == -1:
                flash_center_x = start[0]
            else:
                flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum  # + offset[0]
            center = [flash_center_x, flash_center_y]
            right = [center[0] + radius, center[1]]
            right[0] = round(float(right[0]), 3)
            right[1] = round(float(right[1]), 3)
            center[0] = round(float(center[0]), 3)
            center[1] = round(float(center[1]), 3)
            vias.append(Via(center[0], center[1], radius))

            segNum = 50 #Number of segments in circle, smoothness
            segRads = 2 * pi / segNum
            currRads = 0
            volume = pi * radius * radius
            fillTime = round(volume * outputCoeff, 3)

            moveNoz(draw_trace, float(stop_lift))
            draw_trace.append('G0 X' + str(right[0]) + ' Y' + str(right[1]) + ' ;Moving nozzle to start pos\n')
            moveNoz(draw_trace, -float(stop_lift))
            start = right
            draw_trace.append('T5; Via Outline\n')
            draw_trace.append('M111\n')
            draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
            while currRads < 2 * pi:
                x = round(float(center[0] + (cos(currRads) * radius)), 3)
                y = round(float(center[1] + (sin(currRads) * radius)), 3)
                # Rotates points of segment to lengthen, to prevent raster not colliding
                tempStart = rotateCoords(start[0] + lineThickness * cos(currRads - segRads) / 1.5, start[1] + lineThickness * sin(currRads - segRads), -pi / 20, center)
                tempStart = rotateCoords(tempStart[0], tempStart[1], radAngle, rotateCenter)
                tempEnd = rotateCoords(x + lineThickness * cos(currRads) / 1.5, y + lineThickness * sin(currRads) / 2, pi / 20, center)
                tempEnd = rotateCoords(tempEnd[0], tempEnd[1],radAngle, rotateCenter)
                segments.append([])
                segments[len(segments) - 1].append(tempStart[0])
                segments[len(segments) - 1].append(tempEnd[0])
                segments[len(segments) - 1].append(tempStart[1])
                segments[len(segments) - 1].append(tempEnd[1])
                segments[len(segments) - 1].append(viaNum)
                draw_trace.append('G1 X' + str(x) + ' Y' + str(y) + ' E1 F1200\n')
                start = [x, y]
                currRads = round(currRads + segRads, 3)

            draw_trace.append("M110\n")
            draw_trace.append('T3; Via Outline Surplus\n')
            currRads = 0

            while currRads < 4 * pi / 5:
                x = round(float(center[0] + (cos(currRads) * radius)), 3)
                y = round(float(center[1] + (sin(currRads) * radius)), 3)
                draw_trace.append('G1 X' + str(x) + ' Y' + str(y) + ' E1 F1200\n')
                currRads = round(currRads + segRads, 3)

            viaNum += 1
            start = [center[0], center[1]]

        if line.find('M02') != -1:
            finalList = raster(segments, lineThickness)
            moveNoz(draw_trace, float(stop_lift))
            finalList[0] = rotateCoords(finalList[0][0], finalList[0][1], -radAngle, rotateCenter)
            draw_trace.append('T2; Layer Filling\n')
            draw_trace.append('G0 X' + str(round(finalList[0][0],3)) + ' Y' + str(round(finalList[0][1],3)) + '\n')
            moveNoz(draw_trace, -float(stop_lift))
            count = 1
            draw_trace.append('M111\n')
            draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
            while count < len(finalList):
                temp = deepcopy(finalList[count])
                finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + ' E1 F1000\n')

                if(count == len(finalList) - 1):
                    break
                distX = abs(finalList[count + 1][0] - temp[0])
                distY = abs(finalList[count + 1][1] - temp[1])
                if sqrt(distX * distX + distY * distY) > lineThickness * 3:
                    count += 1
                    moveNoz(draw_trace, float(stop_lift))
                    finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                    draw_trace.append('M110\n')
                    draw_trace.append('G0 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + '\n')
                    draw_trace.append('M111\n')
                    draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                    moveNoz(draw_trace, -float(stop_lift))
                else:
                    count += 1
                    finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                    draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + ' E1 F1000\n')

                count += 1
            draw_trace.append('M110\n')

            fillVias(draw_trace, vias, offset, outputCoeff, stop_lift)

    return draw_trace, bounds
