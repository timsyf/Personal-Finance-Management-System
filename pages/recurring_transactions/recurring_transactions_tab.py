import tkinter as tk
from tkinter import ttk

def create_recurring_transactions_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Recurring Transactions Tab").pack()
    notebook.add(tab_frame, text="Recurring Transactions")