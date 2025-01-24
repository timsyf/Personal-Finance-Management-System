import mysql.connector
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_expenses_and_categories(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch expenses grouped by category
        query = """
            SELECT category, SUM(amount) AS total_expense
            FROM expenses_tracker
            WHERE user_id = %s
            GROUP BY category
        """
        cursor.execute(query, (user_id,))
        expenses = cursor.fetchall()

        # Fetch all categories
        query = """
            SELECT name
            FROM expenses_category
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        categories = cursor.fetchall()

        return expenses, categories
    except mysql.connector.Error as err:
        print(f"Error fetching expenses and categories: {err}")
        return [], []
    finally:
        cursor.close()
        connection.close()

def create_chart(income, expenses):
    # Extract categories for expenses and sources for income
    expense_categories = [item['category'] for item in expenses]
    income_sources = [item['source_name'] for item in income]
    unique_categories = list(set(expense_categories + income_sources))  # Combine and deduplicate

    # Map income and expenses to the unique categories
    income_dict = {item['source_name']: item['total_income'] for item in income}
    expense_dict = {item['category']: item['total_expense'] for item in expenses}

    income_values = [income_dict.get(cat, 0) for cat in unique_categories]
    expense_values = [expense_dict.get(cat, 0) for cat in unique_categories]

    # Create a bar chart
    plt.figure(figsize=(6, 4))  # Reduced size
    bar_width = 0.35
    index = range(len(unique_categories))

    plt.bar(index, income_values, bar_width, label="Income", color="green")
    plt.bar([i + bar_width for i in index], expense_values, bar_width, label="Expenses", color="red")

    plt.xlabel("Categories")
    plt.ylabel("Amount ($)")
    plt.title("Monthly Income vs. Expenses by Category")
    plt.xticks([i + bar_width / 2 for i in index], unique_categories, rotation=45)
    plt.legend()

    # Save the plot to a buffer
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer

def get_monthly_data(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch monthly expenses grouped by category
        query_expenses = """
            SELECT category, SUM(amount) AS total_expense
            FROM expenses_tracker
            WHERE user_id = %s AND MONTH(date) = MONTH(CURRENT_DATE())
            AND YEAR(date) = YEAR(CURRENT_DATE())
            GROUP BY category
        """
        cursor.execute(query_expenses, (user_id,))
        expenses = cursor.fetchall()

        # Fetch monthly income grouped by source and map source_id to source_name
        query_income = """
            SELECT s.name AS source_name, SUM(i.amount) AS total_income
            FROM income_tracker i
            JOIN income_sources s ON i.source_id = s.id
            WHERE i.user_id = %s AND MONTH(i.date) = MONTH(CURRENT_DATE())
            AND YEAR(i.date) = YEAR(CURRENT_DATE())
            GROUP BY i.source_id
        """
        cursor.execute(query_income, (user_id,))
        income = cursor.fetchall()

        return income, expenses
    except mysql.connector.Error as err:
        print(f"Error fetching monthly data: {err}")
        return [], []
    finally:
        cursor.close()
        connection.close()

def create_dashboard_tab(notebook, user_id):
    # Create a new tab frame for the dashboard
    tab_frame = ttk.Frame(notebook)

    def refresh_dashboard():
        # Clear the current contents of the tab frame
        for widget in tab_frame.winfo_children():
            widget.destroy()

        # Add a title
        tk.Label(tab_frame, text="Dashboard", font=("Arial", 16)).pack(pady=10)

        # Fetch monthly data
        income, expenses = get_monthly_data(user_id)
        print("Income Data:", income)
        print("Expenses Data:", expenses)

        # Display financial metrics
        total_income = sum(item['total_income'] for item in income)
        total_expenses = sum(item['total_expense'] for item in expenses)
        net_savings = total_income - total_expenses

        tk.Label(tab_frame, text="Financial Metrics", font=("Arial", 14)).pack(anchor="w", padx=10, pady=10)
        tk.Label(tab_frame, text=f"Total Income: ${total_income:.2f}", font=("Arial", 12)).pack(anchor="w", padx=20)
        tk.Label(tab_frame, text=f"Total Expenses: ${total_expenses:.2f}", font=("Arial", 12)).pack(anchor="w", padx=20)
        tk.Label(tab_frame, text=f"Net Savings: ${net_savings:.2f}", font=("Arial", 12)).pack(anchor="w", padx=20)

        # Generate the chart
        buffer = create_chart(income, expenses)
        chart_image = Image.open(buffer)
        chart_photo = ImageTk.PhotoImage(chart_image)
        chart_label = tk.Label(tab_frame, image=chart_photo)
        chart_label.image = chart_photo
        chart_label.pack(pady=10)

        # Add a reload button
        reload_button = tk.Button(tab_frame, text="Reload Dashboard", command=refresh_dashboard, bg="blue", fg="white")
        reload_button.pack(pady=10)

    # Add the tab to the notebook
    notebook.add(tab_frame, text="Dashboard")

    # Initial load of the dashboard
    refresh_dashboard()
