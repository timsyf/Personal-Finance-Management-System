import tkinter as tk
from tkinter import ttk

def create_income_tracking_tab(notebook, user_id):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Income Tracking Tab").pack()
    notebook.add(tab_frame, text="Income Tracking")