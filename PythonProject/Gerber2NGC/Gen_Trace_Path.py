from sys import platform as sys_pf
from math import *
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from Objects import *
from sympy import *


def gen_trace_path(filename, gerberList, offset, h, stop_lift, angle, lineThickness):
    gerber = None
    draw_trace = []
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
            current_Dcode = line[0:3]
            current_aperture = gerber.apertures[current_Dcode]

        if not region and line.find('G01') != -1:
            if line.find('D01') != -1:  # if D01 found
                draw_to_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                draw_to_x = round(draw_to_x, 3)
                draw_to_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D01*')]) / 10 ** gerber.decNum + offset[1]
                draw_to_y = round(draw_to_y, 3)
                draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' E1 F1200 ;aperture ' + current_aperture.code + ' drawing\n')
            elif line.find('D02') != -1:  # if D02 found
                start_pnt_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                start_pnt_x = round(start_pnt_x, 3)
                start_pnt_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D02*')]) / 10 ** gerber.decNum + offset[1]
                start_pnt_y = round(start_pnt_y, 3)
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z' + stop_lift + '\n')
                draw_trace.append('G90\n')
                draw_trace.append('G0 X' + str(start_pnt_x) + ' Y' + str(start_pnt_y) + ' ;aperture ' + current_aperture.code + ' moving\n')
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z-' + stop_lift + '\n')
                draw_trace.append('G90\n')
            elif line.find("D03") != -1: # if D03 found
                if current_aperture.type == 'C' and filename[0:4] == 'VIAS':
                    radius = current_aperture.diameter / 2
                    flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                    flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                    draw_trace.append('G0 X' + str(flash_center_x) + ' Y' + str(flash_center_y + radius) + ' ;aperture ' + current_aperture.code + ' moving to flash pos\n')
                    draw_trace.append('G2 X' + str(flash_center_x) + ' Y' + str(flash_center_y - radius) + ' I0' + ' J' + str(-radius) + ' E1 F1200\n')
                    draw_trace.append('G2 X' + str(flash_center_x) + ' Y' + str(flash_center_y + radius) + ' I0' + ' J' + str(radius) + ' E1 F1200\n')
                    draw_trace.append('G0 X' + str(flash_center_x) + ' Y' + str(flash_center_y) + '\n')
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z-' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                elif current_aperture.type == 'R':
                    #Draw outline of rectangle
                    flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                    flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
                    xMax = flash_center_x + current_aperture.xLength / 2 - lineThickness
                    xMin = xMax - current_aperture.xLength + lineThickness
                    yMax = flash_center_y + current_aperture.yLength / 2 - lineThickness
                    yMin = yMax - current_aperture.yLength + lineThickness
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                    draw_trace.append('G0 X' + str(xMin) + ' Y' + str(yMin) + ' ;aperture ' + current_aperture.code + ' moving to flash pos\n')
                    draw_trace.append('G1 X' + str(xMin) + ' Y' + str(yMax) + ' E1 F1200\n')
                    draw_trace.append('G1 X' + str(xMax) + ' Y' + str(yMax) + ' E1 F1200\n')
                    draw_trace.append('G1 X' + str(xMax) + ' Y' + str(yMin) + ' E1 F1200\n')
                    draw_trace.append('G1 X' + str(xMin) + ' Y' + str(yMin) + ' E1 F1200\n')
                    #draw_trace.append('G0 X' + str(flash_center_x) + ' Y' + str(flash_center_y) + '\n')
                    #Fill in rectangle using raster
                    radAngle = angle * 2 * pi / 360
                    pos_1 = [xMin, yMin]
                    pos_2 = [xMin, yMin]
                    start_pos = pos_1
                    end_pos = pos_2
                    while pos_1[0] < xMax or pos_1[1] < yMax:
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
                        draw_trace.append('G1 X' + str(start_pos[0]) + ' Y' + str(start_pos[1]) + ' E1 F1200\n')
                        draw_trace.append('G1 X' + str(end_pos[0]) + ' Y' + str(end_pos[1]) + ' E1 F1200\n')

                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z-' + stop_lift + '\n')
                    draw_trace.append('G90\n')

            else:
                draw_to_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                draw_to_x = round(draw_to_x, 3)
                draw_to_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('*')]) / 10 ** gerber.decNum + offset[1]
                draw_to_y = round(draw_to_y, 3)
                draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' E1 F1200 ;aperture ' + current_aperture.code + ' drawing\n')


    return draw_trace