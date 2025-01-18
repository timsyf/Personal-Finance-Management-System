import tkinter as tk
from tkinter import ttk
from pages.home.database import add_transaction, get_all_transactions, update_transaction, delete_transaction

def create_home_tab(notebook):
    tab_frame = ttk.Frame(notebook)
    
    tk.Label(tab_frame, text="Description").grid(row=0, column=0)
    entry_description = tk.Entry(tab_frame)
    entry_description.grid(row=0, column=1)

    tk.Label(tab_frame, text="Amount").grid(row=1, column=0)
    entry_amount = tk.Entry(tab_frame)
    entry_amount.grid(row=1, column=1)

    tk.Label(tab_frame, text="Date (YYYY-MM-DD)").grid(row=2, column=0)
    entry_date = tk.Entry(tab_frame)
    entry_date.grid(row=2, column=1)

    tk.Button(tab_frame, text="Add Transaction", command=lambda: add(entry_description, entry_amount, entry_date, listbox)).grid(row=3, column=0, columnspan=2)
    tk.Button(tab_frame, text="Update Transaction", command=lambda: update(entry_description, entry_amount, entry_date, listbox)).grid(row=4, column=0, columnspan=2)
    tk.Button(tab_frame, text="Delete Transaction", command=lambda: delete(entry_description, entry_amount, entry_date, listbox)).grid(row=5, column=0, columnspan=2)

    listbox = tk.Listbox(tab_frame, width=50, height=10)
    listbox.grid(row=6, column=0, columnspan=2)

    view_transactions(listbox)
    
    notebook.add(tab_frame, text="Home")

def add(entry_description, entry_amount, entry_date, listbox):
    description = entry_description.get()
    amount = entry_amount.get()
    date = entry_date.get()

    if description and amount and date:
        add_transaction(description, amount, date)
        entry_description.delete(0, tk.END)
        entry_amount.delete(0, tk.END)
        entry_date.delete(0, tk.END)
        view_transactions(listbox)
    else:
        print("Please fill in all fields.")

def update(entry_description, entry_amount, entry_date, listbox):
    selected = listbox.curselection()
    if selected:
        transaction_id = listbox.get(selected[0]).split(" | ")[0]
        description = entry_description.get()
        amount = entry_amount.get()
        date = entry_date.get()

        if description and amount and date:
            update_transaction(transaction_id, description, amount, date)
            entry_description.delete(0, tk.END)
            entry_amount.delete(0, tk.END)
            entry_date.delete(0, tk.END)
            view_transactions(listbox)
        else:
            print("Please fill in all fields.")
    else:
        print("No transaction selected for update.")

def view_transactions(listbox):
    rows = get_all_transactions()
    listbox.delete(0, tk.END)
    for row in rows:
        listbox.insert(tk.END, f"{row[0]} | {row[1]} | ${row[2]} | {row[3]}")

def delete(entry_description, entry_amount, entry_date, listbox):
    selected = listbox.curselection()
    if selected:
        transaction_id = listbox.get(selected[0]).split(" | ")[0]
        delete_transaction(transaction_id)
        view_transactions(listbox)
    else:
        print("No transaction selected for deletion.")