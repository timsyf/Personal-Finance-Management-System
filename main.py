import tkinter as tk
from tkinter import ttk
from home_tab import create_home_tab
from reports_tab import create_reports_tab
from budget_tab import create_budget_tab
from categories_tab import create_categories_tab
from settings_tab import create_settings_tab
from help_tab import create_help_tab

def main():
    root = tk.Tk()
    root.title("Personal Finance Management")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    create_home_tab(notebook)
    create_reports_tab(notebook)
    create_budget_tab(notebook)
    create_categories_tab(notebook)
    create_settings_tab(notebook)
    create_help_tab(notebook)

    root.mainloop()

if __name__ == "__main__":
    main()