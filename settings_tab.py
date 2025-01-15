import tkinter as tk
from tkinter import ttk

def create_settings_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Settings Tab").pack()
    notebook.add(tab_frame, text="Settings")