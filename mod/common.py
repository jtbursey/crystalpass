from typing import List
import tkinter as tk
from tkinter import font

def clipboard(str : str):
    cp = tk.Tk()
    cp.withdraw()
    cp.clipboard_clear()
    cp.clipboard_append(str)
    cp.update()
    cp.destroy()

def set_font(size = 12):
    fonts = font.families()

    if "Courier New" in fonts:
        return ("Courier New", size)
    elif "Courier" in fonts:
        return ("Courier", size)
    return font.nametofont("TkDefaultFont").actual()

def read_file_lines(file : str):
    infile = open(file, 'r')
    lines = infile.readlines()
    infile.close()
    return lines

def find_first_of(s : str, l : List[str]) -> int:
    return next((i for i, c in enumerate(s) if c in l),None)
