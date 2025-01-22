import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from .database import insert_budget, get_budgets, delete_budget
from pages.expense_tracking.database import get_expenses_tracker, get_expenses_categories

def filter_expense_stats(expenses, date_filter):

    filtered_stats = {}
    for expense in expenses:
        expense_date = expense['date']
        if date_filter(expense_date):
            category = expense['category']
            if category not in filtered_stats:
                filtered_stats[category] = {
                    'count': 0,
                    'total': 0,
                    'min': float('inf'),
                    'max': float('-inf'),
                    'avg': 0,
                }
            filtered_stats[category]['count'] += 1
            filtered_stats[category]['total'] += expense['amount']
            filtered_stats[category]['min'] = min(filtered_stats[category]['min'], expense['amount'])
            filtered_stats[category]['max'] = max(filtered_stats[category]['max'], expense['amount'])


    for category, data in filtered_stats.items():
        data['avg'] = data['total'] / data['count'] if data['count'] > 0 else 0

    return filtered_stats

def create_budget_tool_tab(notebook, user_id):
    def load_categories():
        try:
            categories = get_expenses_categories(user_id)
            category_combobox['values'] = categories
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    def is_current_month(date_obj):
        """Check if a given date is in the current month."""
        now = datetime.now()
        return date_obj.year == now.year and date_obj.month == now.month

    def is_current_year(date_obj):
        """Check if a given date is in the current year."""
        now = datetime.now()
        return date_obj.year == now.year

    def load_progress():
        """Reloads both monthly and yearly progress, including the Overall category."""
        monthly_table.delete(*monthly_table.get_children())
        yearly_table.delete(*yearly_table.get_children())
        try:
            budgets = get_budgets(user_id)
            all_expenses = get_expenses_tracker(user_id)


            monthly_stats = filter_expense_stats(all_expenses, is_current_month)
            total_monthly_budget = 0
            total_monthly_spent = 0

            for budget in budgets:
                if budget["frequency"] != "Monthly":
                    continue

                category = budget["category"] or "All"
                spent = monthly_stats.get(category, {}).get("total", 0)
                remaining = budget["amount"] - spent
                status = "Within Budget" if remaining >= 0 else "Exceeding Budget"

                monthly_table.insert("", "end", values=(category, budget["amount"], spent, remaining, status))
                total_monthly_budget += budget["amount"]
                total_monthly_spent += spent


            monthly_table.insert(
                "", "end",
                values=(
                "Overall", total_monthly_budget, total_monthly_spent, total_monthly_budget - total_monthly_spent,
                "Within Budget" if total_monthly_budget - total_monthly_spent >= 0 else "Exceeding Budget"),
            )

            # Yearly Progress
            yearly_stats = filter_expense_stats(all_expenses, is_current_year)
            total_yearly_budget = 0
            total_yearly_spent = 0

            for budget in budgets:
                if budget["frequency"] != "Yearly":
                    continue

                category = budget["category"] or "All"
                spent = yearly_stats.get(category, {}).get("total", 0)
                remaining = budget["amount"] - spent
                status = "Within Budget" if remaining >= 0 else "Exceeding Budget"

                yearly_table.insert("", "end", values=(category, budget["amount"], spent, remaining, status))
                total_yearly_budget += budget["amount"]
                total_yearly_spent += spent

            # Add Overall row for yearly
            yearly_table.insert(
                "", "end",
                values=("Overall", total_yearly_budget, total_yearly_spent, total_yearly_budget - total_yearly_spent,
                        "Within Budget" if total_yearly_budget - total_yearly_spent >= 0 else "Exceeding Budget"),
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load progress: {e}")

    # main Tab Frame
    tab_frame = ttk.Frame(notebook)
    tab_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(tab_frame, text="Budget Tool", font=("Arial", 16)).pack(pady=10)

    # frame for Adding Budget
    add_budget_frame = ttk.LabelFrame(tab_frame, text="Add Budget")
    add_budget_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(add_budget_frame, text="Budget Amount:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    budget_amount_entry = ttk.Entry(add_budget_frame, width=25)
    budget_amount_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(add_budget_frame, text="Frequency:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    frequency_combobox = ttk.Combobox(add_budget_frame, values=["Monthly", "Yearly"], state="readonly", width=23)
    frequency_combobox.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(add_budget_frame, text="Category :").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    category_combobox = ttk.Combobox(add_budget_frame, width=25)
    category_combobox.grid(row=2, column=1, padx=5, pady=5)

    load_categories()


    # add Budget button
    def add_budget():
        try:
            budget_amount = float(budget_amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Budget amount must be a valid number.")
            return

        frequency = frequency_combobox.get()
        category = category_combobox.get()

        if not frequency:
            messagebox.showerror("Error", "Frequency is required!")
            return

        try:
            insert_budget(user_id, category or None, budget_amount, frequency)
            messagebox.showinfo("Success", "Budget added successfully!")
            load_progress()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add budget: {e}")

    ttk.Button(add_budget_frame, text="Add Budget", command=add_budget).grid(row=3, column=1, pady=10, sticky=tk.E)

    # delete budget button
    def delete_budget_action():
        # Get the selected item from the monthly or yearly table
        selected_item = None
        for table in [monthly_table, yearly_table]:
            selected = table.selection()
            if selected:
                selected_item = selected
                break

        if not selected_item:
            messagebox.showwarning("Warning", "Please select a budget to delete.")
            return


        item_values = table.item(selected_item, "values")
        category = item_values[0]  # Assuming the first column is the category

        try:
            if category == "All" or category == "Overall":
                delete_budget(user_id)
            else:
                delete_budget(user_id, category)

            messagebox.showinfo("Success", f"Budget for '{category}' deleted successfully!")
            load_progress()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete budget: {e}")

    ttk.Button(add_budget_frame, text="Delete Budget", command=delete_budget_action).grid(row=3, column=0, pady=10, sticky=tk.W)


    # Frame for Checking Progress
    check_progress_frame = ttk.LabelFrame(tab_frame, text="Check Progress")
    check_progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    progress_notebook = ttk.Notebook(check_progress_frame)
    progress_notebook.pack(fill=tk.BOTH, expand=True)

    # Monthly Progress Tab
    monthly_progress_frame = ttk.Frame(progress_notebook)
    monthly_progress_frame.pack(fill=tk.BOTH, expand=True)

    monthly_columns = ("Category", "Budget Amount", "Spent", "Remaining", "Status")
    monthly_table = ttk.Treeview(monthly_progress_frame, columns=monthly_columns, show="headings", height=10)
    monthly_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for col in monthly_columns:
        monthly_table.heading(col, text=col)
        monthly_table.column(col, width=150, anchor=tk.CENTER)

    # yearly Progress Tab
    yearly_progress_frame = ttk.Frame(progress_notebook)
    yearly_progress_frame.pack(fill=tk.BOTH, expand=True)

    yearly_columns = ("Category", "Budget Amount", "Spent", "Remaining", "Status")
    yearly_table = ttk.Treeview(yearly_progress_frame, columns=yearly_columns, show="headings", height=10)
    yearly_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for col in yearly_columns:
        yearly_table.heading(col, text=col)
        yearly_table.column(col, width=150, anchor=tk.CENTER)


    progress_notebook.add(monthly_progress_frame, text="Monthly Progress")
    progress_notebook.add(yearly_progress_frame, text="Yearly Progress")
    ttk.Button(add_budget_frame, text="Reload Progress", command=load_progress).grid(row=4, column=0, pady=10,
                                                                                     sticky=tk.W)
    load_progress()  # Load progress initially
    notebook.add(tab_frame, text="Budget Tool")
