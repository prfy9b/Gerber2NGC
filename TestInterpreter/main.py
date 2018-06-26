from Objects import *
import tkinter as tk
from tkinter import filedialog
from Load_PCB_files import read_gerbers

filenames, gerbersList = read_gerbers()
file = gerbersList[filenames[0]]
unitScale = 1
gerber = None

for count, line in enumerate(file):
    # Extended Commands
    if line[0] == '%' and line[len(line) - 1] == '%':
        if line[1:5] == "FSLA":
            if line[6:8] == line[9:11]:
                gerber = Gerber((line[6], line[7]))
            else:
                print("X and Y resolutions do not match.")
                exit(1)
        elif line[1:3] == "MO":
            if line[3:5] == "IN":
                gerber.unit = "IN"
                gerber.unitScale = 25.4
            elif line[3:5] != "MM":
                print("Measurement unit not valid.")
                exit(1)
        elif line[1:3] == "AD":
            gerber.apertures[line[3:6]] = Aperture(line)
        elif line[1:3] == "LN":
            continue
