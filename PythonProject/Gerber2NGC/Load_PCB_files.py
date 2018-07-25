from sys import platform as sys_pf

if sys_pf == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog


# read Gerber file
def read_gerbers(layerCheck, boundsCheck, viaCheck, filmCheck):
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    filenames = filedialog.askopenfilenames(filetypes=[("Gerber files", "*.*"), ("all files", "*.*")], parent=root)
    orderedNames = []
    root.update()
    filenames = list(filenames)

    for count in range(0, len(layerCheck)):
        try:
            for i, name in enumerate(filenames):
                if viaCheck in name and layerCheck[count] in name:
                    orderedNames.append(filenames[i])
                    del filenames[i]
                    break
            for i, name in enumerate(filenames):
                if filmCheck in name and layerCheck[count] in name:
                    orderedNames.append(filenames[i])
                    del filenames[i]
                    break
            count += 1
        except(ValueError):
            print("ALERT: MAKE SURE ALL FILE NAMES ARE DESIGNATED IN CONFIG FILE")
            for name in filenames:
                print(name)
            exit(1)

    if len(filenames) == 1 and boundsCheck in filenames[0]:
        orderedNames.append(filenames[0])
        del filenames[0]


    gerbersList = []

    for i in range(0, len(orderedNames)):
        fhand = open(orderedNames[i], 'r')
        while orderedNames[i].find('/') != -1:
            orderedNames[i] = orderedNames[i][orderedNames[i].find('/') + 1:len(orderedNames[i])]
        gerbersList.append(fhand.readlines())
        fhand.close
    for name in orderedNames:
        print(name)

    return orderedNames, gerbersList
