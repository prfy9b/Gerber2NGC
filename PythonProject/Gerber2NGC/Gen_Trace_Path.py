from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from Objects import *
from sympy import *


def gen_trace_path(filename, gerberList, offset, h, stop_lift):
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
                draw_trace.append('G1 X' + str(start_pnt_x) + ' Y' + str(start_pnt_y) + ' E1 F2400 ;aperture ' + current_aperture.code + ' moving\n')
                draw_trace.append('G91\n')
                draw_trace.append('G0 Z-' + stop_lift + '\n')
                draw_trace.append('G90\n')
            elif line.find("D03") != -1: # if D03 found
                if current_aperture.type == 'C':
                    radius = current_aperture.diameter / 2
                    print ("radius: " + str(radius))
                    flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                    flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[1]
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                    draw_trace.append('G1 X' + str(flash_center_x) + ' Y' + str(flash_center_y + radius) + ' E1 F2400 ;aperture ' + current_aperture.code + ' moving to flash pos\n')
                    draw_trace.append('G2 X' + str(flash_center_x) + ' Y' + str(flash_center_y - radius) + ' I0' + ' J' + str(-radius) + ' E1 F1200\n')
                    draw_trace.append('G2 X' + str(flash_center_x) + ' Y' + str(flash_center_y + radius) + ' I0' + ' J' + str(radius) + ' E1 F1200\n')
                    draw_trace.append('G1 X' + str(flash_center_x) + ' Y' + str(flash_center_y) + ' E1 F2400\n')
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z-' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                elif current_aperture.type == 'R':
                    flash_center_x = gerber.unitScale * int(line[line.find('X') + 1: line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                    flash_center_y = gerber.unitScale * int(line[line.find('Y') + 1: line.find('D03')]) / 10 ** gerber.decNum + offset[0]
                    draw_trace.append('G91\n')
                    draw_trace.append('G0 Z' + stop_lift + '\n')
                    draw_trace.append('G90\n')
                    draw_trace.append('G1 X' + str(flash_center_x - current_aperture.xLength / 2) + ' Y' + str(
                        flash_center_y - current_aperture.yLength / 2) + ' E1 F2400 ;aperture ' + current_aperture.code + ' moving to flash pos\n')
                    draw_trace.append('G1 X' + str(flash_center_x - current_aperture.xLength / 2) + ' Y' + str(
                        flash_center_y + current_aperture.yLength / 2) + ' E1 F2400\n')
                    draw_trace.append('G1 X' + str(flash_center_x + current_aperture.xLength / 2) + ' Y' + str(
                        flash_center_y + current_aperture.yLength / 2) + ' E1 F2400\n')
                    draw_trace.append('G1 X' + str(flash_center_x + current_aperture.xLength / 2) + ' Y' + str(
                        flash_center_y - current_aperture.yLength / 2) + ' E1 F2400\n')
                    draw_trace.append('G1 X' + str(flash_center_x - current_aperture.xLength / 2) + ' Y' + str(
                        flash_center_y - current_aperture.yLength / 2) + ' E1 F2400\n')
                    draw_trace.append('G1 X' + str(flash_center_x) + ' Y' + str(flash_center_y) + ' E1 F2400\n')
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