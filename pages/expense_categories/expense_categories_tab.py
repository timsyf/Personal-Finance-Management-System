import tkinter as tk
from tkinter import ttk

def create_expense_categories_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Expense Categories Tab").pack()
    notebook.add(tab_frame, text="Expense Categories")