import os
from enum import Enum
import tkinter as tk
from tkinter import messagebox

def info_dialogue(window, msg: str = "", title = "Info"):
    messagebox.showinfo(title, msg, parent=window)

def warn_dialogue(window, msg: str, title = "Warning"):
    messagebox.showwarning(title, msg, parent=window)

def err_dialogue(window, msg: str, title = "Error"):
    messagebox.showerror(title, msg, parent=window)

def ask_yes_no(window, msg: str, title = "CrystalPass") -> bool:
    response = messagebox.askyesno(title, msg, parent=window)
    return response

def window_launch():
    window = tk.Tk()
    window.unbind_all("<Tab>")
    window.unbind_all("<<PrevWindow>>")
    window.unbind_all("<<NextWindow>>")
    window.unbind_all("<Return>")
    window.geometry('800x400+0+0')
    window.title("CrystalPass")

    input_pattern = tk.StringVar()
    generated_password = tk.StringVar()

    # Frame for main interactions
    fr_main = tk.Frame(master=window, width=500, height=300, bg="white")
    fr_main.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    # Frame for quick guide
    fr_guide = tk.Frame(master=window, width=300, height=300, borderwidth=10, bg="lightblue")
    fr_guide.pack(fill=tk.Y, side=tk.LEFT, expand=False)

    # UI feedback for password strength
    txt_guide = tk.Text(master=fr_guide, width=35, height=10, borderwidth=3, relief=tk.FLAT, bg="lightblue", state='disabled')
    txt_guide.pack(fill=tk.BOTH, side=tk.TOP, padx=4, pady=4, expand=True)

    # frame to hold guide buttons
    fr_guide_buttons = tk.Frame(master=fr_guide, bg="lightblue")
    fr_guide_buttons.pack(fill=tk.NONE, side=tk.TOP, expand=False)

    # Button to open manual
    btn_manual = tk.Button(master=fr_guide_buttons, text="Manual", height=2, width=15, relief=tk.RAISED, borderwidth=3) # , command=manual
    btn_manual.pack(padx=4, pady=4)

    # frame to center the entry things
    fr_entry = tk.Frame(master=fr_main, borderwidth=10, bg="white")
    fr_entry.pack(fill=tk.X, anchor=tk.CENTER, expand=True)

    # frame to hold the input and wizard
    fr_input = tk.Frame(master=fr_entry, bg="white")
    fr_input.pack(fill=tk.X, side=tk.TOP, expand=True)

    # Entry for password pattern
    ent_pattern_input = tk.Entry(master=fr_input, textvariable=input_pattern, relief=tk.RIDGE, borderwidth=3, bg="white")
    ent_pattern_input.pack(fill=tk.X, side=tk.LEFT, anchor=tk.CENTER, padx=4, pady=4, expand=True)

    # wizard button
    btn_generate = tk.Button(master=fr_input, text="Wizard", height=1, width=10, relief=tk.RAISED, borderwidth=3) # , command=wizard
    btn_generate.pack(side=tk.RIGHT, padx=4, pady=4, expand=False)

    # labelframe for the meter
    lf_meter = tk.LabelFrame(master=fr_entry, text="Password Strength", bg="white")
    lf_meter.pack(fill=tk.NONE, side=tk.TOP, padx=4, pady=20, expand=False)

    # UI feedback for password strength
    lbl_meter = tk.Label(master=lf_meter, width=40, text="Meter", bg="red")
    lbl_meter.pack(fill=tk.NONE, side=tk.TOP, padx=4, pady=4, expand=False)

    # frame to hold the input and wizard
    fr_output = tk.Frame(master=fr_entry, bg="white")
    fr_output.pack(fill=tk.X, side=tk.TOP, expand=True)

    # Entry for outputting the user password
    ent_password_output = tk.Entry(master=fr_output, textvariable=generated_password, state='disabled', relief=tk.RIDGE, borderwidth=3, bg="white")
    ent_password_output.pack(fill=tk.X, side=tk.LEFT, padx=4, pady=4, expand=True)

    # clipboard button
    btn_clipboard = tk.Button(master=fr_output, text="clipboard", height=1, width=10, relief=tk.RAISED, borderwidth=3) # , command=clipboard
    btn_clipboard.pack(side=tk.RIGHT, padx=4, pady=4, expand=False)

    # run or rerun the results
    btn_generate = tk.Button(master=fr_entry, text="Generate", height=2, width=20, relief=tk.RAISED, borderwidth=3) # , command=generate
    btn_generate.pack(side=tk.TOP, padx=4, pady=20, expand=False)

    window.mainloop()

if __name__ == "__main__":
    window_launch()