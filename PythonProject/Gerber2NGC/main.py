from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog
from sympy import *

from Load_PCB_files import read_gerbers
from Gen_Trace_Path import *

Noz2_offset = [125, 60]
layerthickness = 5
stop_lift = 0.3
angle = 60 #Angle flashes are filled with, in degrees\
rotateCenter = (50, 50)
lineThickness = .1
filenames, gerbersList = read_gerbers()
draw_trace = []
hasVia = False
for i in range(0, len(filenames)):
    if(i == 0 or filenames[i-1][0:5] == 'LAYER'):
        curren_z = (i+1) * layerthickness
    if(filenames[i][0:5] == "LAYER"):
        draw_trace.append(gen_trace_path_layer(filenames[i], gerbersList[i], Noz2_offset, str(curren_z), str(stop_lift), angle, rotateCenter, lineThickness, hasVia))
        hasVia = False
    else:
        draw_trace.append(gen_trace_path_via(filenames[i], gerbersList[i], Noz2_offset, str(curren_z), str(stop_lift), angle, rotateCenter, lineThickness))
        hasVia = True

root = tk.Tk()
root.withdraw()
root.call('wm', 'attributes', '.', '-topmost', True)
newfilename = filedialog.asksaveasfilename(initialfile='gcode for trace.gcode', parent=root)

fhand = open(newfilename, 'w')
for i in range(0, len(filenames)):
    fhand.writelines(draw_trace[i])
    print(len(draw_trace[i]))

fhand.close
print('gcode for trace saved')