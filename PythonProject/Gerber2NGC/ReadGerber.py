from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog



# read Gerber file
def ReadGerber():
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    filename = filedialog.askopenfilenames(filetypes=(("Gerber PHO files","*.PHO"),("all files","*.*")), parent = root)
    fhand = open(filename,'r')
    gerberList = fhand.readlines()
    fhand.close

    while filename.find('/') != -1: # '/'
        filename = filename[filename.find('/')+1:len(filename)]

    return  filename, gerberList