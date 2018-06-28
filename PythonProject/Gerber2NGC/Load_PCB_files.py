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
    count = 0
    root.update()
    filenames = list(filenames)
    while(count < len(filenames)):
        if(filenames[count] == 'LAYER' + count):


    gerbersDict = {}

    for i in range(0, len(filenames)):
        fhand = open(filenames[i], 'r')
        while filenames[i].find('/') != -1:
            filenames[i] = filenames[i][filenames[i].find('/') + 1:len(filenames[i])]
        gerbersDict[filenames[i]] = fhand.readlines()
        fhand.close

    return filenames, gerbersDict
