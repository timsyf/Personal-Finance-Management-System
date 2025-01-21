import tkinter as tk
from tkinter import ttk

def create_dashboard_tab(notebook, user_id):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Dashboard Tab").pack()
    notebook.add(tab_frame, text="Dashboard")