from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog
from sympy import *

from Load_PCB_files import read_gerbers
from Gen_Trace_Path import gen_trace_path

Noz2_offset = [125, 60]
layerthickness = 5
stop_lift = 0.3

filenames, gerbersList = read_gerbers()
draw_trace = []
for i in range(0, len(filenames)):
    curren_z = (i+1) * layerthickness
    draw_trace.append(gen_trace_path(filenames[i], gerbersList[i], Noz2_offset, str(curren_z), str(stop_lift)))

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