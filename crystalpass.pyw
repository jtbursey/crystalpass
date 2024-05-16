import tkinter as tk

import mod.common as common
import mod.dialogue as dialogue
import mod.regex as regex

# =============================
# Action Functions
# =============================

def init():
    # Setup all to options and config
    # set initial manual text
    pass

def generate_password(pattern_entry : tk.StringVar, pwd_entry : tk.StringVar):
    pattern = pattern_entry.get()
    if pattern == "":
        return
    res = regex.generate(pattern)
    if int(res[0]) < 0:
        dialogue.err(msg="Invalid expression: "+res[1])
        return
    pwd_entry.set(res[1])

def run_wizard():
    dialogue.info(msg="This is where the wizard will be")

def open_manual():
    dialogue.info(msg="This will open the manual")

def copy_to_clipboard(pwd_entry : tk.StringVar):
    gen_pwd = pwd_entry.get()
    if gen_pwd != "":
        common.clipboard(gen_pwd)

def explain_pattern():
    dialogue.info(msg="This will explain the given pattern")

def open_advanced_options():
    dialogue.info(msg="This will open the advanced options")

# =============================
# Window Loop
# =============================

def window_launch():
    window = tk.Tk()
    window.unbind_all("<Tab>")
    window.unbind_all("<<PrevWindow>>")
    window.unbind_all("<<NextWindow>>")
    window.unbind_all("<Return>")
    # TODO: Get screen resolution and scale to that, also middle of screen
    window.geometry('1000x400')
    window.title("CrystalPass")

    text_font = common.set_font()

    input_pattern = tk.StringVar()
    generated_password = tk.StringVar()

    # TODO: Explain Button

    # Frame for main interactions
    fr_main = tk.Frame(master=window, width=500, height=300, bg="white")
    fr_main.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    # Frame for quick guide
    fr_guide = tk.Frame(master=window, borderwidth=10, bg="lightblue")
    fr_guide.pack(fill=tk.Y, side=tk.LEFT, expand=False)

    # UI feedback for password strength
    txt_guide = tk.Text(master=fr_guide, width=35, height=10, borderwidth=3, relief=tk.FLAT, bg="lightblue", state='disabled')
    txt_guide.configure(font=text_font, cursor="")
    txt_guide.pack(fill=tk.BOTH, side=tk.TOP, padx=4, pady=4, expand=True)

    # frame to hold guide buttons
    fr_guide_buttons = tk.Frame(master=fr_guide, bg="lightblue")
    fr_guide_buttons.pack(fill=tk.NONE, side=tk.TOP, expand=False)

    # Button to open manual
    btn_manual = tk.Button(master=fr_guide_buttons, text="Manual", height=2, width=15, relief=tk.RAISED, borderwidth=3, command=open_manual)
    btn_manual.pack(padx=4, pady=4)

    # frame to center the entry things
    fr_entry = tk.Frame(master=fr_main, borderwidth=10, bg="white")
    fr_entry.pack(fill=tk.X, anchor=tk.CENTER, expand=True)

    # frame to hold the input and wizard
    lf_input = tk.LabelFrame(master=fr_entry, text="Password Pattern", bg="white")
    lf_input.pack(fill=tk.X, side=tk.TOP, expand=True)

    # Entry for password pattern
    ent_pattern_input = tk.Entry(master=lf_input, textvariable=input_pattern, relief=tk.RIDGE, borderwidth=3, bg="white")
    ent_pattern_input.configure(font=text_font)
    ent_pattern_input.pack(fill=tk.X, side=tk.LEFT, anchor=tk.CENTER, padx=4, pady=4, expand=True)
    ent_pattern_input.bind("<Return>", (lambda event: generate_password(input_pattern, generated_password)))

    # wizard button
    btn_generate = tk.Button(master=lf_input, text="Wizard", height=1, width=10, relief=tk.RAISED, borderwidth=3, command=run_wizard)
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
    ent_password_output.configure(font=text_font)
    ent_password_output.pack(fill=tk.X, side=tk.LEFT, padx=4, pady=4, expand=True)

    # clipboard button
    btn_clipboard = tk.Button(master=fr_output, text="clipboard", height=1, width=10, relief=tk.RAISED, borderwidth=3, command=lambda: copy_to_clipboard(generated_password))
    btn_clipboard.pack(side=tk.RIGHT, padx=4, pady=4, expand=False)

    # frame for entry buttons
    fr_entry_buttons = tk.Frame(master=fr_entry, bg="white")
    fr_entry_buttons.pack(fill=tk.NONE, side=tk.TOP, expand=True)

    # run or rerun the results
    btn_generate = tk.Button(master=fr_entry_buttons, text="Generate", height=2, width=20, relief=tk.RAISED, borderwidth=3, command=lambda: generate_password(input_pattern, generated_password))
    btn_generate.pack(side=tk.LEFT, padx=10, pady=20, expand=False)

    # button to open the advanced options
    btn_options = tk.Button(master=fr_entry_buttons, text="Adv. Options", height=2, width=20, relief=tk.RAISED, borderwidth=3, command=open_advanced_options)
    btn_options.pack(side=tk.LEFT, padx=10, pady=20, expand=False)

    init()

    window.mainloop()

if __name__ == "__main__":
    window_launch()
