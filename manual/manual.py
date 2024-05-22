import tkinter as tk
from tkinter import font

class Manual:
    master : tk.Tk

    font : str

    def run(parent : tk.Tk):
        Manual.master = tk.Toplevel(parent)
        Manual.master.wm_title("Manual")
        Manual.master.attributes('-topmost', 'true')
        Manual.master.resizable(width=False, height=False)

        Manual.master.wait_window()
