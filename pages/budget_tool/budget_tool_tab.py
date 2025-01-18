import tkinter as tk
from tkinter import ttk

def create_budget_tool_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Budget Tool Tab").pack()
    notebook.add(tab_frame, text="Budget Tool")