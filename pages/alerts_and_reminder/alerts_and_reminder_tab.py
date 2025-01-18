import tkinter as tk
from tkinter import ttk

def create_alerts_and_reminder_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    tk.Label(tab_frame, text="Alerts and Reminder Tab").pack()
    notebook.add(tab_frame, text="Alerts and Reminder")