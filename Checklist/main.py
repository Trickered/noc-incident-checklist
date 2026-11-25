import tkinter as tk
from tkinter import messagebox
import json

SAVE_FILE = "checklist.json"
items = []
BG = "#2A2A2A"
CHECKS = ["CPU", "MEMORY", "NETWORK", "STORAGE"]

def setup_columns(frame):
    frame.grid_columnconfigure(0, minsize=160)
    for i in range (1, len(CHECKS) + 1):
        frame.grid_columnconfigure(i, minsize=80)

def save():
    data = []
    for item in items:
        data.append({
            "text": item["text"],
            "checks": [v.get() for v in item["vars"]],
        })
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load():
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
    except FileNotFoundError:
        return
    for saved in data:
        add_item(saved["text"], saved["checks"])

def add_item(text, states=None):
    if states is None:
        states = [False] * len(CHECKS)
    
    row = tk.Frame(list_frame, bg=BG)
    row.pack(fill="x", padx=10, pady=2)
    setup_columns(row)

    address = tk.Label(row, text=text, fg="white", bg=BG, anchor="w")
    address.grid(row=0, column=0, sticky="w")

    vars_ = []
    for i in range(len(CHECKS)):
        var = tk.BooleanVar(value=states[i])
        check = tk.Checkbutton(
            row,
            variable=var,
            command=save,
            fg="white",
            bg=BG,
            selectcolor=BG,
            activebackground=BG,
            activeforeground="white",
        )
        check.grid(row=0, column=i + 1)
        vars_.append(var)

    item = {"text": text, "vars": vars_}
    items.append(item)

    def on_remove():
        answer = messagebox.askyesno("Remove", f"Remove {text}?")
        if not answer:
            return
        row.destroy()
        items.remove(item)
        save()

    remove_button = tk.Button(row, text="- Remove", command=on_remove)
    remove_button.grid(row=0, column=len(CHECKS) + 1, padx=(10, 0))


def on_add():
    add_popup = tk.Toplevel(window)
    add_popup.title("Add new Checklist")
    add_popup.configure(bg=BG)
    add_popup.geometry("400x250")

    ERROR_TEXT = "Input checklist label"

    title_label = tk.Label(
        add_popup,
        text="Insert label",
        font=("Segoe UI", 20, "bold"),
        fg="white",
        bg=BG,
    )
    title_label.pack(pady=(20, 0))

    hint_label = tk.Label(
        add_popup,
        text="e.g. VMID, IP address, hostname: one thing to check",
        font=("Segoe UI", 10),
        fg="#9A9A9A",
        bg=BG,
    )
    hint_label.pack(pady=(0, 10))

    entry = tk.Entry(add_popup, width=50, bg="#3A3A3A", fg="white", insertbackground="white")
    entry.pack(pady=10)

    def clear_error():
        if entry.winfo_exists() and entry.get() == ERROR_TEXT:
            entry.delete(0, tk.END)
            entry.config(fg="white")

    def on_confirm():
        text = entry.get()
        if text.strip() == "" or text == ERROR_TEXT:
            entry.delete(0, tk.END)
            entry.insert(0, ERROR_TEXT)
            entry.config(fg="red")
            add_popup.after(3000, clear_error)
            return
        add_item(text)
        save()
        add_popup.destroy()

    confirm_button = tk.Button(add_popup, text="Confirm", command=on_confirm)
    confirm_button.pack()

def on_clear():
    answer = messagebox.askyesno("Clear", "Clear all checkboxes?")
    if not answer:
        return
    for item in items:
        for var in item["vars"]:
            var.set(False)
    save()

window = tk.Tk()
window.title("NOC Incident Checklist")
window.geometry("620x500")
window.configure(bg=BG)

top_bar = tk.Frame(window, bg=BG)
top_bar.pack(pady=10)

add_button = tk.Button(top_bar, text="+ Add", command=on_add)
add_button.pack(side="left", padx=5)

clear_button = tk.Button(top_bar, text="* Clear", command=on_clear)
clear_button.pack(side="left", padx=5)

header = tk.Frame(window, bg=BG)
header.pack(fill="x", padx=10)
setup_columns(header)

tk.Label(header, text="IP Address", fg="white", bg=BG, anchor="w",).grid(row=0, column=0, sticky="w")
for i, name in enumerate(CHECKS, start=1):
    tk.Label(header, text=name, fg="white", bg=BG).grid(row=0, column=i)

container = tk.Frame(window, bg=BG)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

list_frame = tk.Frame(window, bg=BG)
canvas_window = canvas.create_window((0, 0), window=list_frame, anchor="nw")

def on_list_resize(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_canvas_resize(event):
    canvas.itemconfig(canvas_window, width=event.width)

list_frame.bind("<Configure>", on_list_resize)
canvas.bind("<Configure>", on_canvas_resize)

def on_mousewheel(event):
    canvas.yview_scroll(int(-event.delta / 120), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

load()
window.mainloop()