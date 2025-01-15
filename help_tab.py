import tkinter as tk
from tkinter import ttk

def create_help_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Help Tab").pack()
    notebook.add(tab_frame, text="Help")