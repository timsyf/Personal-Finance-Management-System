import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from pages.expense_tracking.database import add_expenses_tracker, get_filtered_expenses, get_expenses_categories, add_expense_category, delete_expense_by_id, update_expense_by_id, delete_expense_category_by_name
from datetime import datetime

def create_expense_tracking_tab(notebook, user_id):
    main_tab_frame = ttk.Frame(notebook)
    
    sub_notebook = ttk.Notebook(main_tab_frame)
    
    sub_tab_1_frame = ttk.Frame(sub_notebook)
    create_add_expense_subtab(sub_tab_1_frame, user_id)
    sub_notebook.add(sub_tab_1_frame, text="Add Expense")
    
    sub_tab_2_frame = ttk.Frame(sub_notebook)
    create_view_expenses_subtab(sub_tab_2_frame, user_id)
    sub_notebook.add(sub_tab_2_frame, text="View Expenses")
    
    sub_tab_3_frame = ttk.Frame(sub_notebook)
    create_manage_category_subtab(sub_tab_3_frame, user_id)
    sub_notebook.add(sub_tab_3_frame, text="Manage Categories")
    
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

    def load_categories():
        try:
            categories = get_expenses_categories(user_id)
            categories.sort()
            category_combobox['values'] = categories
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    form_frame = ttk.LabelFrame(sub_tab_frame, text="Add Expense", padding="10")
    form_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(form_frame, text="Description:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    description_entry = ttk.Entry(form_frame, width=50)
    description_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(form_frame, text="Amount:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    amount_entry = ttk.Entry(form_frame, width=50)
    amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(form_frame, text="Category:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    category_combobox = ttk.Combobox(form_frame, width=48, state="readonly")
    category_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(form_frame, text="Date:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    date_picker = DateEntry(form_frame, width=48, background="darkblue", foreground="white", state="readonly", date_pattern="mm/dd/yyyy")
    date_picker.set_date(date.today())
    date_picker.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    submit_button = ttk.Button(form_frame, text="Add Expense", command=add_expense)
    submit_button.grid(row=4, columnspan=2, pady=10)

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
            messagebox.showerror("Input Error", "Amount filters must be valid numbers.")
            return
        
        try:
            expenses = get_filtered_expenses(user_id, start_date, end_date, category, min_amount, max_amount, description)
            update_expenses_table(expenses)
            update_total_amount(expenses)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching expenses: {e}")

    def update_expenses_table(expenses):
        for row in expenses_tree.get_children():
            expenses_tree.delete(row)
        
        for expense in expenses:
            expenses_tree.insert("", "end", values=(expense["id"], expense["description"], expense["amount"], expense["category"], expense["date"]))

    def update_total_amount(expenses):
        total = sum(expense["amount"] for expense in expenses)
        total_label.config(text=f"Total Amount: ${total:.2f}")

    def clear_filters():
        start_date_picker.set_date(date.today())
        end_date_picker.set_date(date.today())
        category_filter_combobox.set("")
        min_amount_entry.delete(0, tk.END)
        max_amount_entry.delete(0, tk.END)
        description_search_entry.delete(0, tk.END)
        expenses_tree.delete(*expenses_tree.get_children())
        total_label.config(text="Total Amount: $0.00")

    def load_categories():
        try:
            categories = get_expenses_categories(user_id)
            categories.sort()
            category_filter_combobox['values'] = [""] + categories
            category_update_combobox['values'] = categories
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    def set_this_month():
        today = date.today()
        start_date_picker.set_date(today.replace(day=1))
        end_date_picker.set_date(today)

    def set_last_month():
        today = date.today()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date_picker.set_date(last_day_last_month.replace(day=1))
        end_date_picker.set_date(last_day_last_month)

    def set_this_year():
        today = date.today()
        start_date_picker.set_date(today.replace(month=1, day=1))
        end_date_picker.set_date(today)

    def set_last_year():
        today = date.today()
        last_year = today.year - 1
        start_date_picker.set_date(date(last_year, 1, 1))
        end_date_picker.set_date(date(last_year, 12, 31))

    def delete_expense():
        selected_item = expenses_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an expense to delete.")
            return

        expense_id = expenses_tree.item(selected_item, "values")[0]
        try:
            delete_expense_by_id(expense_id)
            expenses_tree.delete(selected_item)
            messagebox.showinfo("Success", "Expense deleted successfully.")
            view_expenses()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting expense: {e}")

    def update_expense():
        selected_item = expenses_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an expense to update.")
            return

        expense_id = expenses_tree.item(selected_item, "values")[0]
        description = description_update_entry.get().strip()
        amount = amount_update_entry.get().strip()
        category = category_update_combobox.get()
        expense_date = date_update_picker.get_date()

        if not description or not amount or not category:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a valid number.")
            return

        try:
            update_expense_by_id(expense_id, description, amount, category, expense_date)
            messagebox.showinfo("Success", "Expense updated successfully!")
            view_expenses()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating expense: {e}")

    def on_row_select(event):
        selected_item = expenses_tree.selection()
        if selected_item:
            selected_expense = expenses_tree.item(selected_item, "values")
            description_update_entry.delete(0, tk.END)
            description_update_entry.insert(0, selected_expense[1])
            amount_update_entry.delete(0, tk.END)
            amount_update_entry.insert(0, selected_expense[2])
            category_update_combobox.set(selected_expense[3])
            
            expense_date = selected_expense[4]
            formatted_date = datetime.strptime(expense_date, "%Y-%m-%d").strftime("%m/%d/%Y")
            
            date_update_picker.set_date(formatted_date)

    frame = ttk.Frame(sub_tab_frame)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    filter_update_frame = ttk.Frame(frame)
    filter_update_frame.pack(fill="both", expand=True)

    search_filter_frame = ttk.LabelFrame(filter_update_frame, text="Search Filters", padding="10")
    search_filter_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

    tk.Label(search_filter_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    start_date_picker = DateEntry(search_filter_frame, width=50, background="darkblue", foreground="white", state="readonly", date_pattern="mm/dd/yyyy")
    start_date_picker.set_date(date.today())
    start_date_picker.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(search_filter_frame, text="End Date:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    end_date_picker = DateEntry(search_filter_frame, width=50, background="darkblue", foreground="white", state="readonly", date_pattern="mm/dd/yyyy")
    end_date_picker.set_date(date.today())
    end_date_picker.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    date_buttons_frame = ttk.Frame(search_filter_frame)
    date_buttons_frame.grid(row=2, column=0, columnspan=2, pady=5)

    ttk.Button(date_buttons_frame, text="This Month", command=set_this_month).grid(row=0, column=0, padx=5)
    ttk.Button(date_buttons_frame, text="Last Month", command=set_last_month).grid(row=0, column=1, padx=5)
    ttk.Button(date_buttons_frame, text="This Year", command=set_this_year).grid(row=0, column=2, padx=5)
    ttk.Button(date_buttons_frame, text="Last Year", command=set_last_year).grid(row=0, column=3, padx=5)

    tk.Label(search_filter_frame, text="Category:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    category_filter_combobox = ttk.Combobox(search_filter_frame, width=50, state="readonly")
    category_filter_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(search_filter_frame, text="Min Amount:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    min_amount_entry = ttk.Entry(search_filter_frame, width=50)
    min_amount_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(search_filter_frame, text="Max Amount:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    max_amount_entry = ttk.Entry(search_filter_frame, width=50)
    max_amount_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(search_filter_frame, text="Search Description:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
    description_search_entry = ttk.Entry(search_filter_frame, width=50)
    description_search_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    ttk.Button(search_filter_frame, text="Search", command=view_expenses).grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    ttk.Button(search_filter_frame, text="Clear Filters", command=clear_filters).grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    update_input_frame = ttk.LabelFrame(filter_update_frame, text="Update Expense", padding="10")
    update_input_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

    tk.Label(update_input_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    description_update_entry = ttk.Entry(update_input_frame, width=50)
    description_update_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(update_input_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    amount_update_entry = ttk.Entry(update_input_frame, width=50)
    amount_update_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(update_input_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    category_update_combobox = ttk.Combobox(update_input_frame, width=50, state="readonly")
    category_update_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(update_input_frame, text="Date:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

    date_update_picker = DateEntry(update_input_frame, width=50, background="darkblue", foreground="white", state="readonly", date_pattern="mm/dd/yyyy")
    date_update_picker.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    ttk.Button(update_input_frame, text="Update", command=update_expense).grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    ttk.Button(update_input_frame, text="Delete", command=delete_expense).grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    expenses_tree_frame = ttk.Frame(frame)
    expenses_tree_frame.pack(fill="both", expand=True)

    expenses_tree = ttk.Treeview(expenses_tree_frame, columns=("ID", "Description", "Amount", "Category", "Date"), show="headings")
    expenses_tree.heading("ID", text="ID")
    expenses_tree.heading("Description", text="Description")
    expenses_tree.heading("Amount", text="Amount")
    expenses_tree.heading("Category", text="Category")
    expenses_tree.heading("Date", text="Date")
    
    expenses_tree.column("ID", anchor="center", width=50)
    expenses_tree.column("Description", anchor="center", width=150)
    expenses_tree.column("Amount", anchor="center", width=100)
    expenses_tree.column("Category", anchor="center", width=100)
    expenses_tree.column("Date", anchor="center", width=100)
    
    expenses_tree.pack(fill="both", expand=True)

    expenses_tree.bind("<<TreeviewSelect>>", on_row_select)

    total_label = ttk.Label(expenses_tree_frame, text="Total Amount: $0.00", padding="5")
    total_label.pack(side="bottom", anchor="w", padx=20)

    load_categories()
    view_expenses()
    
def create_manage_category_subtab(sub_tab_frame, user_id):
    def add_category():
        category_name = category_entry.get().strip()
        if not category_name:
            messagebox.showerror("Input Error", "Category name is required.")
            return
        
        try:
            add_expense_category(category_name, user_id)
            messagebox.showinfo("Success", "Category added successfully!")
            category_entry.delete(0, tk.END)
            load_categories()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding category: {e}")

    def delete_category():
        selected_item = categories_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
            return
        
        category_name = categories_tree.item(selected_item, "values")[0]
        try:
            delete_expense_category_by_name(category_name, user_id)
            messagebox.showinfo("Success", "Category deleted successfully!")
            load_categories()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error deleting category: {e}")

    def load_categories():
        try:
            categories = get_expenses_categories(user_id)
            for row in categories_tree.get_children():
                categories_tree.delete(row)
            for category in categories:
                categories_tree.insert("", "end", values=(category,))
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    frame = ttk.Frame(sub_tab_frame)
    frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    add_frame = ttk.LabelFrame(frame, text="Add Category", padding="10")
    add_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(add_frame, text="Category Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    category_entry = ttk.Entry(add_frame, width=40)
    category_entry.grid(row=0, column=1, padx=5, pady=5)
    
    add_button = ttk.Button(add_frame, text="Add Category", command=add_category)
    add_button.grid(row=0, column=2, padx=5, pady=5)
    
    view_frame = ttk.LabelFrame(frame, text="Existing Categories", padding="10")
    view_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    categories_tree = ttk.Treeview(view_frame, columns=("Category Name",), show="headings", height=10)
    categories_tree.heading("Category Name", text="Category Name")
    categories_tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    delete_button = ttk.Button(view_frame, text="Delete Selected Category", command=delete_category)
    delete_button.pack(pady=10)
    
    load_categories()