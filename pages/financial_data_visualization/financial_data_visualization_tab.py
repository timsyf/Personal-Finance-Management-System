import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pages.home.database import get_all_transactions

def create_financial_data_visualization_tab(notebook):
    main_tab_frame = ttk.Frame(notebook)
    
    sub_notebook = ttk.Notebook(main_tab_frame)
    
    sub_tab_1_frame = ttk.Frame(sub_notebook)
    create_transaction_summary_subtab(sub_tab_1_frame)
    sub_notebook.add(sub_tab_1_frame, text="Transaction Summary")
    
    sub_tab_2_frame = ttk.Frame(sub_notebook)
    create_pie_chart_subtab(sub_tab_2_frame)
    sub_notebook.add(sub_tab_2_frame, text="Pie Chart")
    
    sub_notebook.pack(fill="both", expand=True)

    notebook.add(main_tab_frame, text="Financial Data Visualization")

def create_transaction_summary_subtab(sub_tab_frame):
    transactions = get_all_transactions()

    if not transactions:
        tk.Label(sub_tab_frame, text="No data available").pack()
    else:
        categories = {}
        for transaction in transactions:
            category = transaction[0]
            amount = transaction[1]
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

        fig, ax = plt.subplots()
        ax.bar(categories.keys(), categories.values())

        ax.set_xlabel('Categories')
        ax.set_ylabel('Total Amount')
        ax.set_title('Transaction Summary by Category')

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

def create_pie_chart_subtab(sub_tab_frame):
    transactions = get_all_transactions()

    if not transactions:
        tk.Label(sub_tab_frame, text="No data available").pack()
    else:
        categories = {}
        for transaction in transactions:
            category = transaction[0]
            amount = transaction[1]
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

        fig, ax = plt.subplots()
        ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()