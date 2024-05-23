import os
import tkinter as tk
from tkinter import font

import mod.common as common

class Manual:
    master : tk.Tk
    fr : tk.Frame
    sel : tk.Listbox
    txt : tk.Text

    font : str

    contents = [
        ("Crystalpass", os.path.join("manual", "crystalpass.txt")),
        ("Good Practices", os.path.join("manual", "good_practices.txt")),
        ("Password Feedback", os.path.join("manual", "feedback.txt")),
        ("Password Entropy", os.path.join("manual", "entropy.txt")),
        ("Usage", os.path.join("manual", "usage.txt")),
        ("Wizard", os.path.join("manual", "wizard.txt")),
        ("Expressions", os.path.join("manual", "expressions.txt")),
        ("  Word", os.path.join("manual", "word.txt")),
        ("  Digit", os.path.join("manual", "digit.txt")),
        ("  Letter", os.path.join("manual", "letter.txt")),
        ("  Symbol", os.path.join("manual", "symbol.txt")),
        ("  Character", os.path.join("manual", "character.txt")),
        ("  Named", os.path.join("manual", "named.txt")),
        ("  Literals", os.path.join("manual", "literal.txt"))
    ]

    def update():
        selected = Manual.sel.curselection()
        if len(selected) == 0:
            return
        selected = selected[0]
        lines = common.read_file_lines(Manual.contents[selected][1])
        Manual.txt.configure(state='normal')
        Manual.txt.delete(0.0, tk.END)
        for l in lines:
            Manual.txt.insert(tk.END, l.rstrip() + '\n')
        Manual.txt.configure(state='disabled')

    def run(parent : tk.Tk):
        Manual.font = common.set_font()

        Manual.master = tk.Toplevel(parent)
        Manual.master.wm_title("Manual")
        Manual.master.attributes('-topmost', 'true')
        Manual.master.resizable(width=False, height=False)

        Manual.fr = tk.Frame(master=Manual.master, width=500, height=300, bg="lightblue")
        Manual.fr.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        Manual.sel = tk.Listbox(master=Manual.fr, width=25, selectmode=tk.SINGLE)
        Manual.sel.configure(font=Manual.font, cursor="")
        Manual.sel.pack(fill=tk.BOTH, side=tk.LEFT, padx=4, pady=4, expand=False)
        Manual.sel.bind("<<ListboxSelect>>", (lambda event: Manual.update()))

        Manual.txt = tk.Text(master=Manual.fr, width=90, height=25, borderwidth=3, relief=tk.FLAT, bg="white", state='disabled')
        Manual.txt.configure(font=Manual.font, cursor="")
        Manual.txt.pack(fill=tk.BOTH, side=tk.LEFT, padx=4, pady=4, expand=True)

        for c in Manual.contents:
            Manual.sel.insert(tk.END, c[0])

        Manual.master.wait_window()
