import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pages.financial_data_visualization.database import (
    get_total_expenses_by_category,
    get_income_by_source,
    get_budget_utilization,
    get_top_expense_categories,
    get_daily_expense_trends,
    get_income_vs_expenses,
    get_income_breakdown_by_year,
)

def create_financial_data_visualization_tab(notebook, user_id):
    main_tab_frame = ttk.Frame(notebook)

    sub_notebook = ttk.Notebook(main_tab_frame)

    sub_tab_1_frame = ttk.Frame(sub_notebook)
    create_transaction_summary_subtab(sub_tab_1_frame, user_id)
    sub_notebook.add(sub_tab_1_frame, text="Transaction Summary")

    sub_tab_2_frame = ttk.Frame(sub_notebook)
    create_top_expense_categories_subtab(sub_tab_2_frame, user_id)
    sub_notebook.add(sub_tab_2_frame, text="Top Expense Categories")

    sub_tab_3_frame = ttk.Frame(sub_notebook)
    create_income_distribution_subtab(sub_tab_3_frame, user_id)
    sub_notebook.add(sub_tab_3_frame, text="Income Distribution")

    sub_tab_4_frame = ttk.Frame(sub_notebook)
    create_budget_utilization_subtab(sub_tab_4_frame, user_id)
    sub_notebook.add(sub_tab_4_frame, text="Budget Utilization")

    sub_tab_5_frame = ttk.Frame(sub_notebook)
    create_daily_expense_trends_subtab(sub_tab_5_frame, user_id)
    sub_notebook.add(sub_tab_5_frame, text="Daily Expense Trends")

    sub_tab_6_frame = ttk.Frame(sub_notebook)
    create_income_vs_expenses_subtab(sub_tab_6_frame, user_id)
    sub_notebook.add(sub_tab_6_frame, text="Income vs Expenses")

    sub_tab_7_frame = ttk.Frame(sub_notebook)
    create_income_breakdown_by_year_subtab(sub_tab_7_frame, user_id)
    sub_notebook.add(sub_tab_7_frame, text="Income Breakdown by Year")

    sub_notebook.pack(fill="both", expand=True)

    notebook.add(main_tab_frame, text="Financial Data Visualization")

def create_transaction_summary_subtab(sub_tab_frame, user_id):
    transactions = get_total_expenses_by_category(user_id)

    if transactions:
        categories, amounts = zip(*transactions)

        fig, ax = plt.subplots()
        ax.bar(categories, amounts)

        ax.set_xlabel('Categories')
        ax.set_ylabel('Total Amount')
        ax.set_title('Total Expenses by Category')

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        tk.Label(sub_tab_frame, text="No data available for Transaction Summary").pack()

def create_income_distribution_subtab(sub_tab_frame, user_id):
    income_sources = get_income_by_source(user_id)

    if income_sources:
        sources, amounts = zip(*income_sources)

        fig, ax = plt.subplots()
        ax.pie(amounts, labels=sources, autopct='%1.1f%%', startangle=90)
        ax.set_title('Income Distribution by Source')
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        tk.Label(sub_tab_frame, text="No data available for Income Distribution").pack()

def create_budget_utilization_subtab(sub_tab_frame, user_id):
    budgets = get_budget_utilization(user_id)

    if budgets:
        categories, budgeted_amounts, spent_amounts, remaining_amounts = zip(*budgets)

        fig, ax = plt.subplots()
        bar_width = 0.35
        index = range(len(categories))

        ax.bar(index, budgeted_amounts, bar_width, label='Budgeted')
        ax.bar([i + bar_width for i in index], spent_amounts, bar_width, label='Spent')

        ax.set_xlabel('Categories')
        ax.set_ylabel('Amount')
        ax.set_title('Budget Utilization')
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(categories)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        tk.Label(sub_tab_frame, text="No data available for Budget Utilization").pack()
        
def create_top_expense_categories_subtab(sub_tab_frame, user_id):
    expenses = get_top_expense_categories(user_id)

    if expenses:
        categories, amounts = zip(*expenses)

        fig, ax = plt.subplots()
        ax.bar(categories, amounts)

        ax.set_xlabel('Categories')
        ax.set_ylabel('Total Amount')
        ax.set_title('Top 5 Expense Categories')

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        tk.Label(sub_tab_frame, text="No data available for Top Expense Categories").pack()

def create_daily_expense_trends_subtab(sub_tab_frame, user_id):
    input_frame = ttk.Frame(sub_tab_frame)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
    start_date_entry = DateEntry(input_frame, width=12, date_pattern="yyyy-mm-dd")
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
    end_date_entry = DateEntry(input_frame, width=12, date_pattern="yyyy-mm-dd")
    end_date_entry.grid(row=0, column=3, padx=5, pady=5)

    chart_frame = ttk.Frame(sub_tab_frame)
    chart_frame.pack(fill="both", expand=True, pady=10)

    def fetch_and_plot():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        if not start_date or not end_date:
            messagebox.showwarning("Input Error", "Please select both start and end dates.")
            return

        trends = get_daily_expense_trends(user_id, start_date, end_date)

        for widget in chart_frame.winfo_children():
            widget.destroy()

        if trends:
            dates, amounts = zip(*trends)
            formatted_dates = [date.strftime("%d-%m") for date in dates]

            fig, ax = plt.subplots()
            ax.plot(formatted_dates, amounts, marker='o')

            ax.set_xlabel('Date (DD-MM)')
            ax.set_ylabel('Total Amount')
            ax.set_title('Daily Expense Trends')
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            messagebox.showinfo("No Data", "No data available for the selected period.")

    ttk.Button(input_frame, text="View Chart", command=fetch_and_plot).grid(row=0, column=4, padx=10, pady=5)

def create_income_vs_expenses_subtab(sub_tab_frame, user_id):
    input_frame = ttk.Frame(sub_tab_frame)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
    start_date_entry = DateEntry(input_frame, width=12, date_pattern="yyyy-mm-dd")
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
    end_date_entry = DateEntry(input_frame, width=12, date_pattern="yyyy-mm-dd")
    end_date_entry.grid(row=0, column=3, padx=5, pady=5)

    chart_frame = ttk.Frame(sub_tab_frame)
    chart_frame.pack(fill="both", expand=True, pady=10)

    def fetch_and_plot():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        if not start_date or not end_date:
            messagebox.showwarning("Input Error", "Please select both start and end dates.")
            return

        data = get_income_vs_expenses(user_id, start_date, end_date)

        for widget in chart_frame.winfo_children():
            widget.destroy()

        if data and all(data):
            total_income, total_expenses = data

            fig, ax = plt.subplots()
            categories = ['Income', 'Expenses']
            amounts = [total_income, total_expenses]

            ax.bar(categories, amounts, color=['green', 'red'])

            ax.set_ylabel('Total Amount')
            ax.set_title('Income vs Expenses')

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            messagebox.showinfo("No Data", "No data available for the selected period.")

    ttk.Button(input_frame, text="View Chart", command=fetch_and_plot).grid(row=0, column=4, padx=10, pady=5)

def create_income_breakdown_by_year_subtab(sub_tab_frame, user_id):
    income_breakdown = get_income_breakdown_by_year(user_id)

    if income_breakdown:
        years = list(set(row[0] for row in income_breakdown))
        sources = list(set(row[1] for row in income_breakdown))
        breakdown = {year: {source: 0 for source in sources} for year in years}

        for year, source, amount in income_breakdown:
            breakdown[year][source] = amount

        fig, ax = plt.subplots()
        for source in sources:
            ax.bar(
                years,
                [breakdown[year].get(source, 0) for year in years],
                label=source,
            )

        ax.set_xlabel('Year')
        ax.set_ylabel('Total Income')
        ax.set_title('Income Breakdown by Year')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=sub_tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        tk.Label(sub_tab_frame, text="No data available for Income Breakdown by Year").pack()