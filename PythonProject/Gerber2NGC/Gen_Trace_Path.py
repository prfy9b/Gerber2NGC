from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

from Objects import *
from sympy import *


def gen_trace_path(filename, gerberList, offset, h, stop_lift):
    gerber = None
    draw_trace = []
    aptset_idx = 0
    aptset_cnt = 0
    current_Dcode = 'D01'
    draw_trace.append('G0 Z' + h + '\n')

    for i, line in enumerate(gerberList):
        if gerberList[i].find('%FSLA') != -1:
            gerber = Gerber(int(gerberList[i][6]), int(gerberList[i][7]))

        if gerberList[i].find('%MOIN') != -1:
            gerber.unit = "IN"
            gerber.unitScale = 25.4

        if line.find('ADD') != -1:
            gerber.apertures[line[3:6]] = Aperture(line, gerber)

        if line[0] == 'D':
            current_Dcode = line[0:3]
            print(current_Dcode)
            if True:#int(current_Dcode[1:]) > 9:
                current_aperture = gerber.apertures[current_Dcode]

        if line[0:3] == "G04":
            continue

        if line[0] == 'G' and line[0:3] != "G04":
            if current_aperture.xLength > 0.002 or current_aperture.diameter > 0.002:
                if line.find('G01') != -1:  # examine from line n+1, loop till a line without "G01 "
                    if line.find('D03') != -1:
                        print(current_Dcode, 'flash aperture')
                    elif line.find('D01') != -1:  # if D01 found
                        draw_to_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D01*')]) / 10 ** gerber.decNum + offset[1]
                        draw_to_y = round(draw_to_y, 3)
                        draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' F1200 ;aperture ' + current_aperture.code + ' drawing\n')
                    elif line.find('D02') != -1:  # if D01 not found, and D02 not found
                        start_pnt_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                        start_pnt_x = round(start_pnt_x, 3)
                        start_pnt_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('D02*')]) / 10 ** gerber.decNum + offset[1]
                        start_pnt_y = round(start_pnt_y, 3)
                        draw_trace.append('G91\n')
                        draw_trace.append('G0 Z' + stop_lift + '\n')
                        draw_trace.append('G90\n')
                        draw_trace.append('G1 X' + str(start_pnt_x) + ' Y' + str(start_pnt_y) + ' F2400 ;aperture ' + current_aperture.code + ' moveing\n')
                        draw_trace.append('G91\n')
                        draw_trace.append('G0 Z-' + stop_lift + '\n')
                        draw_trace.append('G90\n')
                    else:  # if D01 not found, instead, D02 found
                        draw_to_x = gerber.unitScale * int(line[line.find('X') + 1:line.find('Y')]) / 10 ** gerber.decNum + offset[0]
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_y = gerber.unitScale * int(line[line.find('Y') + 1:line.find('*')]) / 10 ** gerber.decNum + offset[1]
                        draw_to_y = round(draw_to_y, 3)
                        draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' F1200 ;aperture ' + current_aperture.code + ' drawing\n')


    return draw_trace