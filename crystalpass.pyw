import tkinter as tk
from tkinter import font
import os
from typing import List

import mod.common as common
import mod.dialogue as dialogue
import mod.expression as exp
import mod.wordlist as wordlist
from mod.environment import Environment as env
from manual.quick_guide import Quick_Guide as qg
from mod.wizard import Wizard

class Window:
    master : tk.Tk
    font : font
    input : tk.StringVar
    password : tk.StringVar
    fr_main : tk.Frame
    fr_guide : tk.Frame
    txt_guide : tk.Text
    fr_guide_buttons : tk.Frame
    btn_manual : tk.Button
    fr_entry : tk.Frame
    lf_input : tk.LabelFrame
    ent_pattern_input: tk.Entry
    btn_wizard : tk.Button
    lf_meter : tk.LabelFrame
    lbl_meter : tk.Label
    fr_output : tk.Frame
    ent_password_output : tk.Entry
    btn_clipboard : tk.Button
    fr_entry_buttons : tk.Frame
    btn_generate : tk.Button
    btn_explain : tk.Button
    btn_options : tk.Button

    wizard_open = False

def write_txt(lines : List[str], txt : tk.Text):
    txt.configure(state='normal')
    txt.delete(0.0, tk.END)
    for l in lines:
        txt.insert(tk.END, l + '\n')
    txt.configure(state='disabled')

def init():
    # get where we expect to be
    selfpath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(selfpath))
    # Setup environment
    env.addlist = common.read_file_lines(env.addlist_file)
    env.blocklist = common.read_file_lines(env.blocklist_file)
    words = common.read_file_lines(env.wordlist_file)

    env.wordlists = wordlist.split_words(words, env.addlist, env.blocklist)
    # set initial manual text
    write_txt(qg.default, Window.txt_guide)

# =============================
# Action Functions
# =============================

def generate_password():
    pattern = Window.input.get()
    if pattern == "":
        return
    err, password = exp.generate(pattern)
    if int(err) < 0:
        exp.handle_err(err, password)
        Window.password.set("")
        return
    Window.password.set(password)

def run_wizard():
    if not Window.wizard_open:
        Window.wizard_open = True
        output = Wizard.run(parent=Window.master)
        Window.wizard_open = False
        app = Window.input.get()
        Window.input.set(app + output)
    else:
        dialogue.info("The wizard is already open.")

def update_guide():
    pass

def open_manual():
    dialogue.info(msg="This will open the manual")

def copy_to_clipboard():
    gen_pwd = Window.password.get()
    if gen_pwd != "":
        common.clipboard(gen_pwd)

def explain_pattern():
    pattern = Window.input.get()
    if pattern == "":
        return

    err, exprs = exp.parse(pattern)
    if err < 0:
        exp.handle_err(err, exprs)
        return

    lines = exp.get_explanation(exprs)
    explain = tk.Toplevel(Window.master)
    explain.wm_title("Explanation")
    txt = tk.Text(master=explain, width=75, height=35, borderwidth=3, relief=tk.FLAT, bg="white", state='disabled')
    txt.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
    write_txt(lines, txt)

def open_advanced_options():
    dialogue.info(msg="This will open the advanced options")

# =============================
# Window Loop
# =============================

def window_launch():
    Window.master = tk.Tk()
    Window.master.unbind_all("<Tab>")
    Window.master.unbind_all("<<PrevWindow>>")
    Window.master.unbind_all("<<NextWindow>>")
    Window.master.unbind_all("<Return>")
    # TODO: Get screen resolution and scale to that, also middle of screen
    Window.master.geometry('1200x450')
    Window.master.title("CrystalPass")

    Window.font = common.set_font()

    Window.input = tk.StringVar()
    Window.password = tk.StringVar()

    # Frame for main interactions
    Window.fr_main = tk.Frame(master=Window.master, width=500, height=300, bg="white")
    Window.fr_main.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    # Frame for quick guide
    Window.fr_guide = tk.Frame(master=Window.master, borderwidth=10, bg="lightblue")
    Window.fr_guide.pack(fill=tk.Y, side=tk.LEFT, expand=False)

    # UI feedback for password strength
    Window.txt_guide = tk.Text(master=Window.fr_guide, width=35, height=17, borderwidth=3, relief=tk.FLAT, bg="lightblue", state='disabled')
    Window.txt_guide.configure(font=Window.font, cursor="")
    Window.txt_guide.pack(fill=tk.BOTH, side=tk.TOP, padx=4, pady=4, expand=True)

    # frame to hold guide buttons
    Window.fr_guide_buttons = tk.Frame(master=Window.fr_guide, bg="lightblue")
    Window.fr_guide_buttons.pack(fill=tk.NONE, side=tk.TOP, expand=False)

    # Button to open manual
    Window.btn_manual = tk.Button(master=Window.fr_guide_buttons, text="Manual", height=2, width=15, relief=tk.RAISED, borderwidth=3, command=open_manual)
    Window.btn_manual.pack(padx=4, pady=4)

    # frame to center the entry things
    Window.fr_entry = tk.Frame(master=Window.fr_main, borderwidth=10, bg="white")
    Window.fr_entry.pack(fill=tk.X, anchor=tk.CENTER, expand=True)

    # frame to hold the input and wizard
    Window.lf_input = tk.LabelFrame(master=Window.fr_entry, text="Password Pattern", bg="white")
    Window.lf_input.pack(fill=tk.X, side=tk.TOP, expand=True)

    # Entry for password pattern
    Window.ent_pattern_input = tk.Entry(master=Window.lf_input, textvariable=Window.input, relief=tk.RIDGE, borderwidth=3, bg="white")
    Window.ent_pattern_input.configure(font=Window.font)
    Window.ent_pattern_input.pack(fill=tk.X, side=tk.LEFT, anchor=tk.CENTER, padx=4, pady=4, expand=True)
    Window.ent_pattern_input.bind("<Return>", (lambda event: generate_password()))

    # wizard button
    Window.btn_wizard = tk.Button(master=Window.lf_input, text="Wizard", height=1, width=10, relief=tk.RAISED, borderwidth=3, command=run_wizard)
    Window.btn_wizard.pack(side=tk.RIGHT, padx=4, pady=4, expand=False)

    # labelframe for the meter
    Window.lf_meter = tk.LabelFrame(master=Window.fr_entry, text="Password Strength", bg="white")
    Window.lf_meter.pack(fill=tk.NONE, side=tk.TOP, padx=4, pady=20, expand=False)

    # UI feedback for password strength
    Window.lbl_meter = tk.Label(master=Window.lf_meter, width=40, text="Meter", bg="red")
    Window.lbl_meter.pack(fill=tk.NONE, side=tk.TOP, padx=4, pady=4, expand=False)

    # frame to hold the input and wizard
    Window.fr_output = tk.Frame(master=Window.fr_entry, bg="white")
    Window.fr_output.pack(fill=tk.X, side=tk.TOP, expand=True)

    # Entry for outputting the user password
    Window.ent_password_output = tk.Entry(master=Window.fr_output, textvariable=Window.password, state='readonly', relief=tk.RIDGE, borderwidth=3, bg="white")
    Window.ent_password_output.configure(font=Window.font)
    Window.ent_password_output.pack(fill=tk.X, side=tk.LEFT, padx=4, pady=4, expand=True)

    # clipboard button
    Window.btn_clipboard = tk.Button(master=Window.fr_output, text="clipboard", height=1, width=10, relief=tk.RAISED, borderwidth=3, command=copy_to_clipboard)
    Window.btn_clipboard.pack(side=tk.RIGHT, padx=4, pady=4, expand=False)

    # frame for entry buttons
    Window.fr_entry_buttons = tk.Frame(master=Window.fr_entry, bg="white")
    Window.fr_entry_buttons.pack(fill=tk.NONE, side=tk.TOP, expand=True)

    # run or rerun the results
    Window.btn_generate = tk.Button(master=Window.fr_entry_buttons, text="Generate", height=2, width=20, relief=tk.RAISED, borderwidth=3, command=generate_password)
    Window.btn_generate.pack(side=tk.LEFT, padx=10, pady=20, expand=False)

    # run or rerun the results
    Window.btn_explain = tk.Button(master=Window.fr_entry_buttons, text="Explain", height=2, width=20, relief=tk.RAISED, borderwidth=3, command=explain_pattern)
    Window.btn_explain.pack(side=tk.LEFT, padx=10, pady=20, expand=False)

    # button to open the advanced options
    Window.btn_options = tk.Button(master=Window.fr_entry_buttons, text="Adv. Options", height=2, width=20, relief=tk.RAISED, borderwidth=3, command=open_advanced_options)
    Window.btn_options.pack(side=tk.LEFT, padx=10, pady=20, expand=False)

    init()

    Window.master.mainloop()

if __name__ == "__main__":
    window_launch()
