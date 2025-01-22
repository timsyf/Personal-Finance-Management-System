import tkinter as tk
from tkinter import ttk, messagebox
from .database import insert_recurring_transaction, get_all_recurring_transactions, delete_recurring_transaction, get_expenses_categories
from datetime import datetime
from tkcalendar import DateEntry
from datetime import date, timedelta

def create_recurring_transactions_tab(notebook, user_id):
    #load category
    def load_categories():
        try:
            categories = get_expenses_categories(user_id)
            category_combobox['values'] = categories
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    tab_frame = ttk.Frame(notebook)
    tab_frame.pack(fill=tk.BOTH, expand=True)

    # Label for the tab
    tk.Label(tab_frame, text="Recurring Expenses", font=("Arial", 16)).pack(pady=10)


    form_frame = ttk.Frame(tab_frame)
    form_frame.pack(fill=tk.X, padx=10, pady=10)

    #input fields
    ttk.Label(form_frame, text="Expense Name:").grid(row=0, column=0, padx=5, pady=5)
    expense_name_entry = ttk.Entry(form_frame, width=20)
    expense_name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
    expense_amount_entry = ttk.Entry(form_frame, width=20)
    expense_amount_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Recurrence:").grid(row=2, column=0, padx=5, pady=5)
    recurrence_combobox = ttk.Combobox(
        form_frame, values=["Daily", "Monthly", "Yearly"], state="readonly", width=18
    )
    recurrence_combobox.grid(row=2, column=1, padx=5, pady=5)

    # Start Date Picker
    ttk.Label(form_frame, text="Start Date (MM/DD/YYYY):").grid(row=3, column=0, padx=5, pady=5)
    start_date_picker = DateEntry(
        form_frame, width=20, background="darkblue", foreground="white",
        state="readonly", date_pattern="mm/dd/yyyy"
    )
    start_date_picker.set_date(date.today())
    start_date_picker.grid(row=3, column=1, padx=5, pady=5)

    # End Date Picker
    ttk.Label(form_frame, text="End Date (MM/DD/YYYY):").grid(row=4, column=0, padx=5, pady=5)
    end_date_picker = DateEntry(
        form_frame, width=20, background="darkblue", foreground="white",
        state="readonly", date_pattern="mm/dd/yyyy"
    )
    end_date_picker.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Category:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    category_combobox = ttk.Combobox(form_frame, width=28, state="readonly")
    category_combobox.grid(row=5, column=1, padx=5, pady=5)

    #  display recurring transactions
    columns = ("ID", "Name", "Amount", "Recurrence", "Start Date", "End Date", "Category")
    transaction_table = ttk.Treeview(tab_frame, columns=columns, show="headings", height=10)
    transaction_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)



    for col in columns:
        transaction_table.heading(col, text=col)
        transaction_table.column(col, width=150, anchor=tk.CENTER)

    load_categories()

    # Load existing transactions from the database
    def load_transactions():
        try:
            transactions = get_all_recurring_transactions()
            for transaction in transactions:
                transaction_table.insert("", "end", values=(
                    transaction["recurring_id"],
                    transaction["name"],
                    f"${transaction['amount']:.2f}",
                    transaction["recurrence"],
                    transaction["start_date"],
                    transaction["end_date"],
                    transaction["category"],
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {e}")

    load_transactions()


    def add_transaction():
        # Fetch input values
        name = expense_name_entry.get()
        amount = expense_amount_entry.get()
        recurrence = recurrence_combobox.get()
        start_date = start_date_picker.get()
        end_date = end_date_picker.get()
        category = category_combobox.get()

        # validate inputs
        if not name or not amount or not recurrence or not start_date:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return

        # insert to  database
        try:
            insert_recurring_transaction(name, amount, recurrence, start_date, end_date, category, user_id)  # Insert into the database
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction to the database: {e}")
            return

        # reload the table
        transaction_table.delete(*transaction_table.get_children())
        load_transactions()


        # clear input fields
        expense_name_entry.delete(0, tk.END)
        expense_amount_entry.delete(0, tk.END)
        recurrence_combobox.set("")
        start_date_picker.delete(0, tk.END)

        messagebox.showinfo("Success", "Recurring transaction added!")

    # delete function
    def delete_selected_transaction():
        selected_item = transaction_table.selection()  # Get selected row
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return


        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this transaction?")
        if confirm:

            item = transaction_table.item(selected_item)
            recurring_id = item["values"][0]  # ID is the first column


            try:
                delete_recurring_transaction(recurring_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete transaction from the database: {e}")
                return


            transaction_table.delete(*transaction_table.get_children())
            load_transactions()


            messagebox.showinfo("Success", "Transaction deleted successfully.")



    button_frame = ttk.Frame(tab_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    #  add/delete button
    ttk.Button(button_frame, text="Add Transaction", command=add_transaction).pack(side=tk.LEFT, padx=5)

    ttk.Button(button_frame, text="Delete Selected Transaction", command=delete_selected_transaction).pack(side=tk.LEFT, padx=5)

    # Add the tab to the notebook
    notebook.add(tab_frame, text="Recurring Expenses")

