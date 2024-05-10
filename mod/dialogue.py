from tkinter import messagebox

def info(msg: str = "", title = "Info"):
    messagebox.showinfo(title, msg)

def warn(msg: str, title = "Warning"):
    messagebox.showwarning(title, msg)

def err(msg: str, title = "Error"):
    messagebox.showerror(title, msg)

def ask_yes_no(msg: str, title = "CrystalPass") -> bool:
    response = messagebox.askyesno(title, msg)
    return response
