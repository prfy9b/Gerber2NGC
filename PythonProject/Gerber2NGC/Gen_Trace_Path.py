from sys import platform as sys_pf
from math import *
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from Objects import *
from sympy import *

def rotateCoords(x, y, radAngle, rotateCenter):
    rotateX = rotateCenter[0] + cos(radAngle) * (x - rotateCenter[0]) - sin(radAngle) * (y - rotateCenter[1])
    rotateY = rotateCenter[1] + sin(radAngle) * (x - rotateCenter[0]) + cos(radAngle) * (y - rotateCenter[1])
    return rotateX, rotateY

def gen_trace_path_layer(filename, gerberList, offset, h, stop_lift, angle, rotateCenter, lineThickness, hasVia):
    gerber = None
    draw_trace = []
    radAngle = angle * 2 * pi / 360
    current_Dcode = 'D01'
    region = False
    draw_trace.append('G0 Z' + h + '\n')

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
            if line.find('D01') != -1:  # if D01 found
                draw_to_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                draw_to_x = round(draw_to_x, 3)
                draw_to_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D01*')]) / 10 ** gerber.decNum + offset[1]
                draw_to_y = round(draw_to_y, 3)
                coords = rotateCoords(draw_to_x, draw_to_y, radAngle, rotateCenter)
                draw_trace.append('G1 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' E1 F1200 ;aperture ' + current_aperture.code + ' drawing\n')
            elif line.find('D02') != -1:  # if D02 found
                start_pnt_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                start_pnt_x = round(start_pnt_x, 3)
                start_pnt_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D02*')]) / 10 ** gerber.decNum + offset[1]
                start_pnt_y = round(start_pnt_y, 3)
                coords = rotateCoords(start_pnt_x, start_pnt_y, radAngle, rotateCenter)
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z' + stop_lift + '\n')
                draw_trace.append('G90\n')
                draw_trace.append('G0 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' ;aperture ' + current_aperture.code + ' moving\n')
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z-' + stop_lift + '\n')
                draw_trace.append('G90\n')
            elif line.find("D03") != -1 and current_aperture.type == 'R': # if D03 found
                #Draw outline of rectangle
                flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
                xMax = flash_center_x + current_aperture.xLength / 2 - lineThickness
                xMin = xMax - current_aperture.xLength + lineThickness
                yMax = flash_center_y + current_aperture.yLength / 2 - lineThickness
                yMin = yMax - current_aperture.yLength + lineThickness
                bottom_left = rotateCoords(xMin, yMin, radAngle, rotateCenter)
                bottom_right = rotateCoords(xMax, yMin, radAngle, rotateCenter)
                top_left = rotateCoords(xMin, yMax, radAngle, rotateCenter)
                top_right = rotateCoords(xMax, yMax, radAngle, rotateCenter)
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z' + stop_lift + '\n')
                draw_trace.append('G90\n')
                draw_trace.append('G0 X' + str(bottom_left[0]) + ' Y' + str(bottom_left[1]) + ' ;aperture ' + current_aperture.code + ' moving to flash pos\n')
                draw_trace.append('G1 X' + str(top_left[0]) + ' Y' + str(top_left[1]) + ' E1 F1200\n')
                draw_trace.append('G1 X' + str(top_right[0]) + ' Y' + str(top_right[1]) + ' E1 F1200\n')
                draw_trace.append('G1 X' + str(bottom_right[0]) + ' Y' + str(bottom_right[1]) + ' E1 F1200\n')
                draw_trace.append('G1 X' + str(bottom_left[0]) + ' Y' + str(bottom_left[1]) + ' E1 F1200\n')
                #Fill in rectangle using raster
                pos_1 = [xMin, yMin]
                pos_2 = [xMin, yMin]
                start_pos = pos_1
                end_pos = pos_2
                while pos_1[0] < xMax or pos_1[1] < yMax:
                    if(radAngle == 0):
                        pos_1[1] += lineThickness
                        pos_2[1] += lineThickness
                    elif(radAngle == pi/2):
                        pos_1[0] += lineThickness
                        pos_2[0] += lineThickness
                    else:
                        if pos_1[0] >= xMax:
                            pos_1[1] += lineThickness * tan(radAngle)
                        else:
                            pos_1[0] += lineThickness * (1/tan(radAngle))
                        if pos_2[1] >= yMax:
                            pos_2[0] += lineThickness * (1/tan(radAngle))
                        else:
                            pos_2[1] += lineThickness * tan(radAngle)
                    if pos_1[0] > xMax:
                        pos_1[0] = xMax
                    if pos_1[1] > xMax:
                        pos_1[1] = xMax
                    if pos_2[0] > xMax:
                        pos_2[0] = xMax
                    if pos_2[1] > xMax:
                        pos_2[1] = xMax
                    if(start_pos == pos_1):
                        start_pos = pos_2
                        end_pos = pos_1
                    else:
                        start_pos = pos_1
                        end_pos = pos_2
                    start_pos = rotateCoords(start_pos[0], start_pos[1], radAngle, rotateCenter)
                    end_pos = rotateCoords(end_pos[0], end_pos[1], radAngle, rotateCenter)
                    draw_trace.append('G1 X' + str(start_pos[0]) + ' Y' + str(start_pos[1]) + ' E1 F1200\n')
                    draw_trace.append('G1 X' + str(end_pos[0]) + ' Y' + str(end_pos[1]) + ' E1 F1200\n')

                draw_trace.append('G91\n')
                draw_trace.append('G0 Z-' + stop_lift + '\n')
                draw_trace.append('G90\n')


    return draw_trace

def gen_trace_path_via(filename, gerberList, offset, h, stop_lift, angle, rotateCenter, lineThickness):
    gerber = None
    draw_trace = []
    current_Dcode = 'D01'
    region = False
    traceCount = 0
    radAngle = angle * 2 * pi / 360
    x_traces = []
    y_traces = []
    draw_trace.append('G0 Z' + h + '\n')

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
            if line.find('D01') != -1 or (line.find('D') == -1 and current_Dcode == 'D01'):  # if D01 found
                xVal = line[line.find('X') + 1: line.find('Y')]
                yVal = line[line.find('Y') + 1: line.find('D01*')]
                if(line.find('D') == -1):
                    yVal = line[line.find('Y') + 1: line.find('*')]
                draw_to_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum + offset[0]
                draw_to_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum + offset[1]
                coords = rotateCoords(draw_to_x, draw_to_y, radAngle, rotateCenter)
                draw_to_y = round(draw_to_y, 3)
                draw_to_x = round(draw_to_x, 3)
                draw_trace.append('G1 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' E1 F1200 ;aperture ' + current_aperture.code + ' drawing\n')
                x_traces.append(draw_to_x)
                y_traces.append(draw_to_y)
            elif line.find('D02') != -1 or (line.find('D') == -1 and current_Dcode == 'D02'):  # if D02 found
                xVal = line[line.find('X') + 1: line.find('Y')]
                yVal = line[line.find('Y') + 1: line.find('D02*')]
                if line.find('D') == -1:
                    yVal = line[line.find('Y') + 1: line.find('*')]
                start_pnt_x = gerber.unitScale * int(xVal) / 10 ** gerber.decNum + offset[0]
                start_pnt_y = gerber.unitScale * int(yVal) / 10 ** gerber.decNum + offset[1]
                coords = rotateCoords(start_pnt_x, start_pnt_y, radAngle, rotateCenter)
                start_pnt_x = round(start_pnt_x, 3)
                start_pnt_y = round(start_pnt_y, 3)
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z' + stop_lift + '\n')
                draw_trace.append('G90\n')
                draw_trace.append('G0 X' + str(coords[0]) + ' Y' + str(coords[1]) + ' ;aperture ' + current_aperture.code + ' moving\n')
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z-' + stop_lift + '\n')
                draw_trace.append('G90\n')
            elif line.find("D03") != -1 or (line.find('D') == -1 and current_Dcode == 'D03'):  # if D03 found
                if current_aperture.type == 'C':
                    radius = current_aperture.diameter / 2
                    flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                    flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
                    bottom = rotateCoords(flash_center_x, flash_center_y - radius, radAngle, rotateCenter)
                    top = rotateCoords(flash_center_x, flash_center_y + radius, radAngle, rotateCenter)
                    center = rotateCoords(flash_center_x, flash_center_y, radAngle, rotateCenter)
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                    draw_trace.append('G0 X' + str(top[0]) + ' Y' + str(top[1]) + ' ;aperture ' + current_aperture.code + ' moving to flash pos\n')
                    draw_trace.append('G2 X' + str(bottom[0]) + ' Y' + str(bottom[1]) + ' I0' + ' J' + str(-radius) + ' E1 F1200\n')
                    draw_trace.append('G2 X' + str(top[0]) + ' Y' + str(top[1]) + ' I0' + ' J' + str(radius) + ' E1 F1200\n')
                    draw_trace.append('G0 X' + str(center[0]) + ' Y' + str(center[1]) + '\n')
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z-' + stop_lift + '\n')
                    draw_trace.append('G90\n')
        #Once all vias are drawn, fill space
        """
        if line.find('M02') != -1:
            xMax = max(x_traces)
            xMin = min(x_traces)
            yMax = max(y_traces)
            yMin = min(y_traces)
            draw_trace.append('G0 X' + str(xMin) + ' Y' + str(yMin) + '\n')
            # Fill in rectangle using raster
            pos_1 = [xMin, yMin]
            pos_2 = [xMin, yMin]
            start_pos = pos_1
            end_pos = pos_2
            while pos_1[0] < xMax or pos_1[1] < yMax:
                if pos_1[0] >= xMax:
                    pos_1[1] += lineThickness * tan(radAngle, rotateCenter)
                else:
                    pos_1[0] += lineThickness * (1 / tan(radAngle, rotateCenter))
                if pos_2[1] >= yMax:
                    pos_2[0] += lineThickness * (1 / tan(radAngle, rotateCenter))
                else:
                    pos_2[1] += lineThickness * tan(radAngle, rotateCenter)
                if pos_1[0] > xMax:
                    pos_1[0] = xMax
                if pos_1[1] > xMax:
                    pos_1[1] = xMax
                if pos_2[0] > xMax:
                    pos_2[0] = xMax
                if pos_2[1] > xMax:
                    pos_2[1] = xMax
                if (start_pos == pos_1):
                    start_pos = pos_2
                    end_pos = pos_1
                else:
                    start_pos = pos_1
                    end_pos = pos_2
                draw_trace.append('G1 X' + str(start_pos[0]) + ' Y' + str(start_pos[1]) + ' E1 F1000\n')
                draw_trace.append('G1 X' + str(end_pos[0]) + ' Y' + str(end_pos[1]) + ' E1 F1000\n')
        """
    return draw_trace