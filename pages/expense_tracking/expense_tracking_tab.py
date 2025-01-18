import tkinter as tk
from tkinter import ttk

def create_expense_tracking_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Expense Tracking Tab").pack()
    notebook.add(tab_frame, text="Expense Tracking")