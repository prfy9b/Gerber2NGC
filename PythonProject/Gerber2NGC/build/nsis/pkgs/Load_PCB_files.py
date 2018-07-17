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
    filenames = filedialog.askopenfilenames(filetypes=[("Gerber PHO files", "*.G*"), ("all files", "*.*")], parent=root)
    orderedNames = []
    count = 0
    fileType = 'BL'
    root.update()
    filenames = list(filenames)

    while(len(filenames) > 1):
        try:
            if count == 0 or len(filenames) == 3:
                checkVal = fileType
                fileType = 'TL'
            else:
                checkVal = str(count)
            for i, name in enumerate(filenames):
                if '-vias' + '.G' + checkVal in name:
                    orderedNames.append(filenames[i])
                    del filenames[i]
                    break
            for i, name in enumerate(filenames):
                if '-films' + '.G' + checkVal in name:
                    orderedNames.append(filenames[i])
                    del filenames[i]
                    break
            count += 1
        except(ValueError):
            print("ALERT: MAKE SURE ALL FILE NAMES ARE .G#, .GBL, .GTL, or .GKO, AND FILENAMES END WITH -films or -vias")
            for name in filenames:
                print(name)
            exit(1)

    if('.GKO' in filenames[0]):
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
