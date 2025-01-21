import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from pages.expense_tracking.database import add_expenses_tracker, get_filtered_expenses, get_expenses_categories, add_expense_category

def create_expense_tracking_tab(notebook, user_id):
    main_tab_frame = ttk.Frame(notebook)
    
    sub_notebook = ttk.Notebook(main_tab_frame)
    
    sub_tab_1_frame = ttk.Frame(sub_notebook)
    create_add_expense_subtab(sub_tab_1_frame, user_id)
    sub_notebook.add(sub_tab_1_frame, text="Add Expense")
    
    sub_tab_2_frame = ttk.Frame(sub_notebook)
    create_view_expenses_subtab(sub_tab_2_frame, user_id)
    sub_notebook.add(sub_tab_2_frame, text="View Expenses")
    
    sub_notebook.pack(fill="both", expand=True)

    notebook.add(main_tab_frame, text="Expense Tracking")

def create_add_expense_subtab(sub_tab_frame, user_id):
    def add_expense():
        description = description_entry.get()
        amount = amount_entry.get()
        category = category_combobox.get()
        expense_date = date_picker.get_date()

        if not description or not amount or not category:
            messagebox.showerror("Input Error", "All fields are required.")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a valid number.")
            return

        try:
            add_expenses_tracker(description, amount, category, expense_date, user_id)
            messagebox.showinfo("Success", "Expense added successfully!")
            description_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            category_combobox.set("")
            date_picker.set_date(date.today())
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving expense: {e}")

    def add_category():
        category_name = new_category_entry.get().strip()
        if not category_name:
            messagebox.showerror("Input Error", "Category name is required.")
            return
        
        try:
            existing_categories = get_expenses_categories(user_id)
            if category_name in existing_categories:
                messagebox.showerror("Duplicate Error", "Category already exists.")
                return
            
            add_expense_category(category_name, user_id)
            messagebox.showinfo("Success", "Category added successfully!")
            new_category_entry.delete(0, tk.END)
            load_categories()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding category: {e}")

    def load_categories():
        try:
            categories = get_expenses_categories(user_id)
            category_combobox['values'] = categories
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    tk.Label(sub_tab_frame, text="Add Expense", font=("Arial", 16)).pack(pady=10)

    form_frame = ttk.Frame(sub_tab_frame)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    description_entry = ttk.Entry(form_frame, width=30)
    description_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    amount_entry = ttk.Entry(form_frame, width=30)
    amount_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    category_combobox = ttk.Combobox(form_frame, width=28, state="readonly")
    category_combobox.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Date:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    date_picker = DateEntry(form_frame, width=28, background="darkblue", foreground="white", state="readonly")
    date_picker.set_date(date.today())
    date_picker.grid(row=3, column=1, padx=5, pady=5)

    add_button = ttk.Button(form_frame, text="Add Expense", command=add_expense)
    add_button.grid(row=4, columnspan=2, pady=10)

    add_category_frame = ttk.Frame(sub_tab_frame)
    add_category_frame.pack(pady=10)

    tk.Label(add_category_frame, text="New Category:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    new_category_entry = ttk.Entry(add_category_frame, width=30)
    new_category_entry.grid(row=0, column=1, padx=5, pady=5)

    add_category_button = ttk.Button(add_category_frame, text="Add Category", command=add_category)
    add_category_button.grid(row=1, columnspan=2, pady=10)

    load_categories()

def create_view_expenses_subtab(sub_tab_frame, user_id):
    def view_expenses():
        start_date = start_date_picker.get_date()
        end_date = end_date_picker.get_date()
        category = category_filter_combobox.get()
        min_amount = min_amount_entry.get()
        max_amount = max_amount_entry.get()
        description = description_search_entry.get()

        try:
            min_amount = float(min_amount) if min_amount else None
            max_amount = float(max_amount) if max_amount else None
        except ValueError:
            min_amount = max_amount = None
            messagebox.showerror("Input Error", "Amount filters must be valid numbers.")
            return
        
        try:
            expenses = get_filtered_expenses(user_id, start_date, end_date, category, min_amount, max_amount, description)
            update_expenses_table(expenses)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching expenses: {e}")

    def update_expenses_table(expenses):
        for row in expenses_tree.get_children():
            expenses_tree.delete(row)
        
        for expense in expenses:
            expenses_tree.insert("", "end", values=(expense["description"], expense["amount"], expense["category"], expense["date"]))

    tk.Label(sub_tab_frame, text="View Expenses", font=("Arial", 16)).pack(pady=10)

    filter_frame = ttk.Frame(sub_tab_frame)
    filter_frame.pack(pady=10)

    tk.Label(filter_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    start_date_picker = DateEntry(filter_frame, width=28, background="darkblue", foreground="white", state="readonly")
    start_date_picker.set_date(date.today())
    start_date_picker.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text="End Date:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    end_date_picker = DateEntry(filter_frame, width=28, background="darkblue", foreground="white", state="readonly")
    end_date_picker.set_date(date.today())
    end_date_picker.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    category_filter_combobox = ttk.Combobox(filter_frame, width=28, state="readonly")
    category_filter_combobox.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text="Min Amount:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    min_amount_entry = ttk.Entry(filter_frame, width=28)
    min_amount_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text="Max Amount:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    max_amount_entry = ttk.Entry(filter_frame, width=28)
    max_amount_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text="Search Description:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    description_search_entry = ttk.Entry(filter_frame, width=28)
    description_search_entry.grid(row=5, column=1, padx=5, pady=5)

    filter_button = ttk.Button(filter_frame, text="Search", command=view_expenses)
    filter_button.grid(row=6, columnspan=2, pady=10)

    expenses_table_frame = ttk.Frame(sub_tab_frame)
    expenses_table_frame.pack(pady=10)

    columns = ("Description", "Amount", "Category", "Date")
    expenses_tree = ttk.Treeview(expenses_table_frame, columns=columns, show="headings")
    for col in columns:
        expenses_tree.heading(col, text=col)
        expenses_tree.column(col, width=150)
    expenses_tree.pack(fill="both", expand=True)
