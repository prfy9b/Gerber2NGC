from sys import platform as sys_pf
from Objects import *
from sympy import *
from Helper_Functions import *
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


def gen_trace_path_layer(filename, gerberList, offset, h, stop_lift, angle, rotateCenter, lineThickness, bounds, exuderDelay):
    gerber = None
    draw_trace = []
    radAngle = angle * 2 * pi / 360
    current_Dcode = 'D01'
    region = False
    pads = []
    start = []  # Start point of current trace
    draw_trace.append('G0 Z' + h + '\n')

    for line in gerberList:

        # Checks for initialization line
        if line.find('%FSLA') != -1:
            gerber = Gerber(int(line[6]), int(line[7]))

        # Checks for unit specification line, defaults to millimeters
        if line.find('%MOIN') != -1:
            gerber.unit = "IN"
            gerber.unitScale = 25.4

        # Checks for aperture definition line
        if line.find('ADD') != -1:
            gerber.apertures[line[3:6]] = Aperture(line, gerber)

        # Checks for region start (regions are ignored at this point)
        if line[0:3] == "G36":
            region = True

        # Checks for region end
        if line[0:3] == "G37":
            region = False

        # Checks for aperture/DCode selection line
        if line[0] == 'D' and int(line[1:3]) > 9:
            current_aperture = gerber.apertures[line[0:3]]
        elif line[len(line) - 5] == 'D':
            current_Dcode = line[len(line) - 5: len(line) - 2]

        # Checks for any kind of movement
        if not region and line.find('G01') != -1:
            # Checks for Traces
            if line.find('D01') != -1 or (line.find('D') == -1 and current_Dcode == 'D01'):
                vertical = False
                draw_to_x = round(gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0], 3)
                # Section of line needed changes based on whether new DCode is supplied
                if line.find('D') == -1:
                    draw_to_y = round(gerber.unitScale * int(line[line.find('Y') + 1:line.find('*')]) / 10 ** gerber.decNum + offset[1], 3)
                else:
                    draw_to_y = round(gerber.unitScale * int(line[line.find('Y') + 1:line.find('D01*')]) / 10 ** gerber.decNum + offset[1], 3)

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

                # Do not print trace if it is a bound, since those are covered by Via file
                if not isBound:
                    draw_trace.append('T1; Layer Trace\n')
                    draw_trace.append('M111')
                    draw_trace.append("G4 P" + str(exuderDelay) + "; Start dwell\n")
                    draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' E1 F1200\n')
                    draw_trace.append('M110')

                start = [draw_to_x, draw_to_y]

            # Checks for nozzle relocation
            elif line.find('D02') != -1:  # if D02 found
                start_pnt_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                start_pnt_x = round(start_pnt_x, 3)
                start_pnt_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D02*')]) / 10 ** gerber.decNum + offset[1]
                start_pnt_y = round(start_pnt_y, 3)
                moveNoz(draw_trace, float(stop_lift))
                draw_trace.append('G0 X' + str(start_pnt_x) + ' Y' + str(start_pnt_y) + ' ;aperture ' + current_aperture.code + ' moving\n')
                moveNoz(draw_trace, -float(stop_lift))
                start = [start_pnt_x, start_pnt_y]

            # Checks for Rectangular flashes (Circular should be in VIAS file)
            elif line.find("D03") != -1 and current_aperture.type == 'R': # if D03 found
                # Draw outline of rectangle
                flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
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
                draw_trace.append('M111')
                draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                draw_trace.append('G1 X' + str(xMin) + ' Y' + str(yMax) + ' E1 F1200\n')
                draw_trace.append('G1 X' + str(xMax) + ' Y' + str(yMax) + ' E1 F1200\n')
                draw_trace.append('G1 X' + str(xMax) + ' Y' + str(yMin) + ' E1 F1200\n')
                draw_trace.append('G1 X' + str(xMin) + ' Y' + str(yMin) + ' E1 F1200\n')
                draw_trace.append('M110')
                start = [round(flash_center_x, 3), round(flash_center_y, 3)]
                pads.append(Pad(flash_center_x, flash_center_y, current_aperture))

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
                draw_trace.append('M111')
                draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                while count < len(finalList) - 2:
                    if abs(finalList[count + 1][0] - finalList[count][0]) > lineThickness:
                        finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                        draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + ' E1 F1000\n')
                        count += 1
                        moveNoz(draw_trace, float(stop_lift))
                        finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                        draw_trace.append('M110')
                        draw_trace.append('G0 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + '\n')
                        draw_trace.append('M111')
                        draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                        moveNoz(draw_trace, -float(stop_lift))
                    else:
                        finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle,rotateCenter)
                        draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + ' E1 F1000\n')
                    count += 1
                draw_trace.append('M110')

    return draw_trace


# Like layer function, but rasters bounds at end of file, and supports circular via flashes rather than rectangular
def gen_trace_path_via(filename, gerberList, offset, h, stop_lift, angle, rotateCenter, lineThickness, outputCoeff, exuderDelay):
    gerber = None
    draw_trace = []
    current_Dcode = 'D01'
    segments = [] #xStart, xEnd, yStart, yEnd
    bounds = []
    region = False
    radAngle = angle * 2 * pi / 360
    start = []
    viaNum = 0

    moveNoz(draw_trace, float(stop_lift))
    draw_trace.append('G0 Z' + h + '\n')
    moveNoz(draw_trace, -float(stop_lift))

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

        if not region and line.find('G01') != -1:
            if line.find('D01') != -1 or (line.find('D') == -1 and current_Dcode == 'D01'):
                xVal = line[line.find('X') + 1: line.find('Y')]
                yVal = line[line.find('Y') + 1: line.find('D01*')]
                if(line.find('D') == -1):
                    yVal = line[line.find('Y') + 1: line.find('*')]
                draw_to_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum + offset[0]
                draw_to_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum + offset[1]
                tempCoords = rotateCoords(draw_to_x, draw_to_y, radAngle, rotateCenter)
                tempStart = rotateCoords(start[0], start[1], radAngle, rotateCenter)
                coords = [round(float(draw_to_x), 3), round(float(draw_to_y), 3)]
                draw_trace.append('T4; Layer Border\n')
                draw_trace.append('M111')
                draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                draw_trace.append('G1 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' E1 F1200 ;aperture ' + current_aperture.code + ' drawing\n')
                draw_trace.append('M110')
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
                start_pnt_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum + offset[0]
                start_pnt_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum + offset[1]
                coords = [start_pnt_x, start_pnt_y]
                tempCoords = rotateCoords(start_pnt_x, start_pnt_y, radAngle, rotateCenter)
                coords[0] = round(float(start_pnt_x), 3)
                coords[1] = round(float(start_pnt_y), 3)
                moveNoz(draw_trace, float(stop_lift))
                draw_trace.append('G0 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' ;aperture ' + current_aperture.code + ' moving\n')
                moveNoz(draw_trace, -float(stop_lift))
                start = coords

            #Checks for circular flashes
            elif line.find("D03") != -1 or (line.find('D') == -1 and current_Dcode == 'D03') and current_aperture.type == 'C':  # if D03 found
                radius = current_aperture.diameter / 2
                flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
                center = [flash_center_x, flash_center_y]
                right = [center[0] + radius, center[1]]
                right[0] = round(float(right[0]), 3)
                right[1] = round(float(right[1]), 3)
                center[0] = round(float(center[0]), 3)
                center[1] = round(float(center[1]), 3)

                segNum = 50 #Number of segments in circle, smoothness
                segRads = 2 * pi / segNum
                currRads = 0
                volume = pi * radius * radius
                fillTime = round(volume * outputCoeff, 3)

                moveNoz(draw_trace, float(stop_lift))
                draw_trace.append('G0 X' + str(right[0]) + ' Y' + str(right[1]) + ' ;aperture ' + current_aperture.code + ' moving to start pos\n')
                moveNoz(draw_trace, -float(stop_lift))
                start = right
                draw_trace.append('T5; Via Outline\n')
                draw_trace.append('M111')
                draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                while currRads < 2 * pi:
                    x = round(float(center[0] + (cos(currRads) * radius)), 3)
                    y = round(float(center[1] + (sin(currRads) * radius)), 3)
                    # Only outputs for first circle, then continues moving to use up extra material
                    tempStart = rotateCoords(start[0] + lineThickness * cos(currRads - segRads),start[1] + lineThickness * sin(currRads - segRads), radAngle,rotateCenter)
                    tempEnd = rotateCoords(x + lineThickness * cos(currRads), y + lineThickness * sin(currRads),radAngle, rotateCenter)
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
                moveNoz(draw_trace, float(stop_lift))
                draw_trace.append('G0 X' + str(center[0]) + ' Y' + str(center[1]) + '\n')
                moveNoz(draw_trace, -float(stop_lift))
                draw_trace.append("M121; Start Fill Via\n")
                draw_trace.append("G4 P" + str(fillTime) + "; Start dwell\n")
                draw_trace.append("M120; Stop Fill Via\n")
                start = [center[0], center[1]]

        if line.find('M02') != -1:
            finalList = raster(segments, lineThickness)
            moveNoz(draw_trace, float(stop_lift))
            finalList[0] = rotateCoords(finalList[0][0], finalList[0][1], -radAngle, rotateCenter)
            draw_trace.append('T2; Layer Filling\n')
            draw_trace.append('G0 X' + str(round(finalList[0][0],3)) + ' Y' + str(round(finalList[0][1],3)) + '\n')
            moveNoz(draw_trace, -float(stop_lift))
            count = 1
            draw_trace.append('M111')
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
                    draw_trace.append('M110')
                    draw_trace.append('G0 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + '\n')
                    draw_trace.append('M111')
                    draw_trace.append('G4 P' + str(exuderDelay) + '; Start dwell\n')
                    moveNoz(draw_trace, -float(stop_lift))
                else:
                    count += 1
                    finalList[count] = rotateCoords(finalList[count][0], finalList[count][1], -radAngle, rotateCenter)
                    draw_trace.append('G1 X' + str(round(finalList[count][0], 3)) + ' Y' + str(round(finalList[count][1], 3)) + ' E1 F1000\n')
                count += 1
            draw_trace.append('M110')

    return draw_trace, bounds
