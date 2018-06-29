from sys import platform as sys_pf

if sys_pf == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog


# read Gerber file
def read_gerbers():
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    filenames = filedialog.askopenfilenames(filetypes=[("Gerber PHO files", "*.PHO"), ("all files", "*.*")], parent=root)
    orderedNames = []
    count = 1
    root.update()
    filenames = list(filenames)


    while(len(filenames) > 0):
        try:
            for i, name in enumerate(filenames):
                if 'VIAS' + str(count) + '.PHO' in name:
                    orderedNames.append(filenames[i])
                    del filenames[i]
                    break
            for i, name in enumerate(filenames):
                if 'LAYER' + str(count) + '.PHO' in name:
                    orderedNames.append(filenames[i])
                    del filenames[i]
                    break
            count += 1
        except(ValueError):
            print("ALERT: MAKE SURE ALL FILE NAMES ARE LAYER#.PHO or VIAS#.PHO")
            for name in filenames:
                print(name)
            exit(1)


    gerbersList = []

    for i in range(0, len(orderedNames)):
        fhand = open(orderedNames[i], 'r')
        while orderedNames[i].find('/') != -1:
            orderedNames[i] = orderedNames[i][orderedNames[i].find('/') + 1:len(orderedNames[i])]
        gerbersList.append(fhand.readlines())
        fhand.close

    return orderedNames, gerbersList
