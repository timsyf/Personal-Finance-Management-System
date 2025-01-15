import tkinter as tk
from tkinter import ttk

def create_reports_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Reports Tab").pack()
    notebook.add(tab_frame, text="Reports")