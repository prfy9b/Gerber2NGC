# Toolheads:
# 1: Layer Traces
# 2: Layer Fillings
# 3: Pad Fillings / Via Outline Surplus
# 4: Layer Borders / Pad Borders
# 5: Via Outline
# 6: Via Outline Surplus
# 7: Layer Fillings


from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog

from Load_PCB_files import read_gerbers
from Gen_Trace_Path import *


def main():
    Noz2_offset = [53.5, 0]
    lineThickness = .2
    layerthickness = lineThickness / 2
    stop_lift = 0.3
    angle = [-60, -30, 0, 60, 90] #Angle flashes/layers are filled with, in degrees. One per layer/via pair, between -90 and 90 degrees
    rotateCenter = (125, 60)
    filenames, gerbersList = read_gerbers()
    draw_trace = []
    hasVia = False
    layerCount = 1
    viaCount = 1
    outputCoeff = 2.0  # Based off nozzle output speed
    bounds = []
    curren_z = 1
    exuderDelay = .2

    for i, name in enumerate(filenames):
        if '.GKO' in name:
            bounds = getBoundsGKO(gerbersList[i], Noz2_offset)
            del filenames[i]
            del gerbersList[i]
            i, j = 0, 0
            while i < len(bounds):
                while j < len(bounds):
                    if(bounds[i] == bounds[j] and not i == j):
                        del bounds[j]
                        i -= 1
                        j -= 1
                    i += 1
                    j += 1

    for i in range(0, len(filenames)):
        if filenames[i][filenames[i].find('-') + 1:filenames[i].find('.')] == "films":
            print("Writing " + filenames[i])
            draw_trace.append(gen_trace_path_layer(filenames[i], gerbersList[i], Noz2_offset, str(curren_z + lineThickness), str(stop_lift), angle[layerCount-1], rotateCenter, lineThickness, bounds, exuderDelay))
            hasVia = False
            layerCount += 1
        elif filenames[i][filenames[i].find('-') + 1:filenames[i].find('.')] == "vias":
            curren_z = (i + 1) * layerthickness + 1
            print("Writing " + filenames[i])
            result = gen_trace_path_via(filenames[i], gerbersList[i], Noz2_offset, str(curren_z), str(stop_lift), angle[layerCount-1], rotateCenter, lineThickness, outputCoeff, exuderDelay, bounds)
            draw_trace.append(result[0])
            bounds = result[1]
            hasVia = True
            viaCount += 1

    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    newfilename = filedialog.asksaveasfilename(initialfile='gcode for trace.gcode', parent=root)

    fhand = open(newfilename, 'w')
    for i in range(0, len(filenames)):
        fhand.writelines(draw_trace[i])

    fhand.close
    print('gcode for trace saved')

main()


