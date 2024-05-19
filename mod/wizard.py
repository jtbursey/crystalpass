import tkinter as tk
from typing import List
import string

import mod.dialogue as dialogue
import mod.common as common
from mod.environment import Environment as env

class Wizard:
    window : tk.Tk
    font : str
    fr_mst : tk.Frame
    fr_argin : tk.Frame
    
    menu : tk.OptionMenu
    menu_choice : tk.StringVar

    max_args = 4
    ent_list : List[tk.Entry]
    lbl_list : List[tk.Label]
    var_list : List[tk.StringVar]

    button : tk.Button

    exp_types = ["None", "Word", "Digit", "Letter", "Symbol", "Character", "Named", "Literal"]

    def set_ent(i : int, label : str, default : str, state : str):
        Wizard.ent_list[i].configure(state="normal")
        Wizard.var_list[i].set(default)
        Wizard.lbl_list[i].configure(text=label)
        Wizard.ent_list[i].configure(state=state)

    def menu_reset():
        for i in range(Wizard.max_args):
            Wizard.set_ent(i, "Unused:", "", "disabled")

    def menu_selected(sel):
        match sel:
            case "Word":
                Wizard.set_ent(0, "Length:", "Any", "normal")
                Wizard.set_ent(1, "Caps:", "False", "normal")
                Wizard.set_ent(2, "Subs:", "False", "normal")
                Wizard.set_ent(3, "Name:", "", "normal")
            case "Digit":
                Wizard.set_ent(0, "Length:", "1", "normal")
                Wizard.set_ent(1, "Range/Set:", "0-9", "normal")
                Wizard.set_ent(2, "Unused:", "", "disabled")
                Wizard.set_ent(3, "Name:", "", "normal")
            case "Letter":
                Wizard.set_ent(0, "Length:", "1", "normal")
                Wizard.set_ent(1, "Range/Set:", "a-z", "normal")
                Wizard.set_ent(2, "Caps:", "False", "normal")
                Wizard.set_ent(3, "Name:", "", "normal")
            case "Symbol":
                Wizard.set_ent(0, "Length:", "1", "normal")
                Wizard.set_ent(1, "Range/Set:", env.symbolSet, "normal")
                Wizard.set_ent(2, "Unused:", "", "disabled")
                Wizard.set_ent(3, "Name:", "", "normal")
            case "Character":
                Wizard.set_ent(0, "Length:", "1", "normal")
                Wizard.set_ent(1, "Range/Set:", env.symbolSet + string.ascii_letters + string.digits, "normal")
                Wizard.set_ent(2, "Unused:", "", "disabled")
                Wizard.set_ent(3, "Name:", "", "normal")
            case "Named":
                Wizard.set_ent(0, "Name:", "", "normal")
                Wizard.set_ent(1, "Reverse:", "False", "normal")
                Wizard.set_ent(2, "Regen:", "False", "normal")
                Wizard.set_ent(3, "Unused:", "", "disabled")
            case "Literal":
                Wizard.set_ent(0, "Literal:", "", "normal")
                Wizard.set_ent(1, "Unused:", "", "disabled")
                Wizard.set_ent(2, "Unused:", "", "disabled")
                Wizard.set_ent(3, "Unused:", "", "disabled")
            case _ :
                Wizard.menu_reset()

    def read(sel) -> str:
        output = ""
        count = 0
        match sel:
            case "Word":
                output = "\\w["
                l = Wizard.var_list[0].get()
                if l != "Any" and l != "":
                    count += 1
                    output += "l="+l
                c = Wizard.var_list[1].get()
                if "true".startswith(c.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "c=t"
                elif "begin".startswith(c.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "c=b"
                elif "end".startswith(c.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "c=e"
                elif not "false".startswith(c.lower()):
                    dialogue.warn(title="Invalid", msg="Invalid caps value!")
                    return ""
                s = Wizard.var_list[2].get()
                if "true".startswith(s.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "s=t"
                elif not "false".startswith(s.lower()):
                    dialogue.warn(title="Invalid", msg="Invalid subs value!")
                    return ""
            case "Digit":
                output = "\\d["
                l = Wizard.var_list[0].get()
                if l != "1" and l != "" and all(x in string.digits + "-" for x in l):
                    count += 1
                    output += "l="+l
                elif not all(x in string.digits + "-" for x in l):
                    dialogue.warn(title="Invalid", msg="Invalid length!")
                    return ""
                s = Wizard.var_list[1].get()
                if s != "0-9" and all(x in string.digits + "-" for x in s):
                    if count > 0:
                        output += ","
                    count += 1
                    if all(x in string.digits for x in s):
                        output += '"' + s + '"'
                    else:
                        output += s
                elif not all(x in string.digits + "-" for x in s):
                    dialogue.warn(title="Invalid", msg="Invalid digit set!")
                    return ""
            case "Letter":
                output = "\\l["
                l = Wizard.var_list[0].get()
                if l != "1" and l != "" and all(x in string.digits + "-" for x in l):
                    count += 1
                    output += "l="+l
                elif not all(x in string.digits + "-" for x in l):
                    dialogue.warn(title="Invalid", msg="Invalid length!")
                    return ""
                s = Wizard.var_list[1].get()
                if s != "a-z" and all(x in string.ascii_letters + "-" for x in s):
                    if count > 0:
                        output += ","
                    count += 1
                    if all(x in string.ascii_letters for x in s):
                        output += '"' + s.lower() + '"'
                    else:
                        output += s.lower()
                elif not all(x in string.ascii_letters + "-" for x in s):
                    dialogue.warn(title="Invalid", msg="Invalid letter set!")
                    return ""
                c = Wizard.var_list[2].get()
                if "true".startswith(c.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "c=t"
                elif not "false".startswith(c.lower()):
                    dialogue.warn(title="Invalid", msg="Invalid caps value!")
                    return ""
            case "Symbol":
                output = "\\s["
                l = Wizard.var_list[0].get()
                if l != "1" and l != "" and all(x in string.digits + "-" for x in l):
                    count += 1
                    output += "l="+l
                elif not all(x in string.digits + "-" for x in l):
                    dialogue.warn(title="Invalid", msg="Invalid length!")
                    return ""
                s = Wizard.var_list[1].get()
                if s != string.punctuation and all(x in string.punctuation for x in s):
                    if count > 0:
                        output += ","
                    count += 1
                    output += '"' + s + '"'
                elif not all(x in string.punctuation for x in s):
                    dialogue.warn(title="Invalid", msg="Invalid symbol set!")
                    return ""
            case "Character":
                output = "\\c["
                l = Wizard.var_list[0].get()
                if l != "1" and l != "" and all(x in string.digits + "-" for x in l):
                    count += 1
                    output += "l="+l
                elif not all(x in string.digits + "-" for x in l):
                    dialogue.warn(title="Invalid", msg="Invalid length!")
                    return ""
                s = Wizard.var_list[1].get()
                if s != env.symbolSet + string.ascii_letters + string.digits and all(x in string.punctuation + string.ascii_letters + string.digits for x in s):
                    if count > 0:
                        output += ","
                    count += 1
                    output += '"' + s + '"'
                elif not all(x in string.punctuation + string.ascii_letters + string.digits for x in s):
                    dialogue.warn(title="Invalid", msg="Invalid character set!")
                    return ""
            case "Named":
                output = "\\n["
                n = Wizard.var_list[0].get()
                if n != "" and all(x in string.ascii_letters + string.digits for x in n):
                    count += 1
                    output += "n="+n
                elif not all(x in string.ascii_letters + string.digits for x in n):
                    dialogue.warn(title="Invalid", msg="Invalid name value!")
                    return ""
                rev = Wizard.var_list[1].get()
                if "true".startswith(rev.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "rev=t"
                elif not "false".startswith(rev.lower()):
                    dialogue.warn(title="Invalid", msg="Invalid reverse value!")
                    return ""
                reg = Wizard.var_list[2].get()
                if "true".startswith(reg.lower()):
                    if count > 0:
                        output += ","
                    count += 1
                    output += "reg=t"
                elif not "false".startswith(reg.lower()):
                    dialogue.warn(title="Invalid", msg="Invalid regen value!")
                    return ""
            case "Literal":
                output = Wizard.var_list[0].get()
            case _ :
                return ""
        name = Wizard.var_list[-1].get()
        if name != "" and all(x in string.ascii_letters + string.digits for x in name):
            if count > 0:
                output += ","
            count += 1
            output += "n="+name
        elif not all(x in string.ascii_letters + string.digits for x in name):
            dialogue.warn(title="Invalid", msg="Invalid name value!")
            return ""
        output += "]"
        return output

    def close():
        Wizard.window.destroy()

    def run(parent : tk.Tk) -> str:
        Wizard.var_list = []
        for i in range(Wizard.max_args):
            Wizard.var_list.append(tk.StringVar())

        Wizard.font = common.set_font()

        Wizard.window = tk.Toplevel(parent)
        Wizard.window.wm_title("Wizard")
        Wizard.window.attributes('-topmost', 'true')
        Wizard.window.resizable(width=False, height=False)
        
        Wizard.fr_mst = tk.Frame(master=Wizard.window, borderwidth=3, bg="white")
        Wizard.fr_mst.pack(fill=tk.BOTH, expand=True)

        Wizard.menu_choice = tk.StringVar()
        Wizard.menu_choice.set(Wizard.exp_types[0])
        Wizard.menu = tk.OptionMenu(Wizard.fr_mst, Wizard.menu_choice, *Wizard.exp_types, command=Wizard.menu_selected)
        Wizard.menu.configure(anchor='w', font=Wizard.font)
        Wizard.menu.pack(fill=tk.X, side=tk.TOP, padx=4, pady=4, expand=False)

        Wizard.fr_argin = tk.Frame(master=Wizard.fr_mst, height=4, borderwidth=3, bg="white")
        Wizard.fr_argin.pack(fill=tk.X, side=tk.TOP, padx=4, pady=4, expand=False)

        Wizard.ent_list = []
        Wizard.lbl_list = []
        for i in range(Wizard.max_args):
            Wizard.lbl_list.append(tk.Label(master=Wizard.fr_argin, font=Wizard.font, text="Unused:", bg="white"))
            Wizard.ent_list.append(tk.Entry(master=Wizard.fr_argin, textvariable=Wizard.var_list[i], relief=tk.RIDGE, borderwidth=3, bg="white", state="disabled"))
            Wizard.ent_list[-1].configure(font=Wizard.font)
            Wizard.lbl_list[-1].grid(row=i+1, column=0, sticky="e")
            Wizard.ent_list[-1].grid(row=i+1, column=1, pady=4)

        Wizard.button = tk.Button(master=Wizard.fr_mst, text="Make it!", height=1, width = 15, relief=tk.RAISED, borderwidth=3, command=Wizard.close)
        Wizard.button.pack(side=tk.TOP, padx=4, pady=4, expand=False)

        Wizard.window.wait_window()
        return Wizard.read(Wizard.menu_choice.get())

