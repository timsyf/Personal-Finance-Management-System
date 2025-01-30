import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests
import pyttsx3
import os
import threading
from dotenv import load_dotenv
from pages.ai_insights.database import (
    get_income_tracker,
    get_expenses_tracker,
    get_income_sources,
    get_recurring_income,
    get_recurring_transactions,
    get_expenses_category,
)
from pages.ai_insights.database import get_fixed_queries, add_fixed_query, delete_fixed_query

tts_thread = None
stop_reading_flag = False

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

tts_engine = pyttsx3.init()

def create_ai_insights_tab(notebook, user_id):
    tab_frame = ttk.Frame(notebook)
    notebook.add(tab_frame, text="AI Insights")

    main_frame = ttk.Frame(tab_frame)
    main_frame.pack(fill="x", padx=20, pady=10)

    query_frame = ttk.LabelFrame(main_frame, text="Query Input", padding=10)
    query_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    query_label = ttk.Label(query_frame, text="Enter your query:")
    query_label.grid(row=0, column=0, sticky="w", pady=5)
    user_input = tk.Text(query_frame, height=8, width=40)
    user_input.grid(row=1, column=0, pady=5)

    fixed_queries_frame = ttk.LabelFrame(main_frame, text="Fixed Queries", padding=10)
    fixed_queries_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    queries = []

    def load_fixed_queries():
        fixed_queries_tree.delete(*fixed_queries_tree.get_children())
        queries = get_fixed_queries(user_id)
        for query in queries:
            fixed_queries_tree.insert("", "end", values=(query[1], query[0]))

    def add_query():
        """Add a new query to the user's saved queries."""
        new_query = user_input.get("1.0", tk.END).strip()
        if new_query:
            add_fixed_query(user_id, new_query)
            load_fixed_queries()

    add_button = ttk.Button(fixed_queries_frame, text="Add Query", command=add_query)
    add_button.pack(pady=5)

    def remove_query():
        """Remove the selected fixed query from the database."""
        selected_item = fixed_queries_tree.selection()
        if selected_item:
            query_id = fixed_queries_tree.item(selected_item, "values")[1]  # Get the query ID
            delete_fixed_query(query_id, user_id)
            load_fixed_queries()

    remove_button = ttk.Button(fixed_queries_frame, text="Remove Query", command=remove_query)
    remove_button.pack(pady=5)

    def populate_query(event):
        """Populate the user_input Text widget with the selected query."""
        selected_item = fixed_queries_tree.selection()
        if selected_item:
            query = fixed_queries_tree.item(selected_item, "values")[0]
            user_input.delete("1.0", tk.END)
            user_input.insert("1.0", query)

    fixed_queries_tree = ttk.Treeview(fixed_queries_frame, columns=("Query"), show="headings", height=8)
    fixed_queries_tree.heading("Query", text="Select a Query")
    fixed_queries_tree.column("Query", anchor="w", width=300)

    for query in queries:
        fixed_queries_tree.insert("", "end", values=(query,))
    fixed_queries_tree.pack(fill="both", expand=True, pady=5)
    fixed_queries_tree.bind("<<TreeviewSelect>>", populate_query)

    date_range_frame = ttk.LabelFrame(main_frame, text="Date Range", padding=10)
    date_range_frame.pack(side="left", fill="both", expand=True)

    ttk.Label(date_range_frame, text="Start Date:").grid(row=0, column=0, pady=5, sticky="w")
    start_date = DateEntry(date_range_frame, width=15)
    start_date.grid(row=1, column=0, pady=5, sticky="w")

    ttk.Label(date_range_frame, text="End Date:").grid(row=0, column=1, pady=5, sticky="w")
    end_date = DateEntry(date_range_frame, width=15)
    end_date.grid(row=1, column=1, pady=5, sticky="w")

    def update_query_with_dates():
        """Update the query text box with the selected date range."""
        start = start_date.get_date()
        end = end_date.get_date()
        query = user_input.get("1.0", tk.END).strip()

        query = "\n".join(
            line for line in query.split("\n") if not line.startswith("Date Range:")
        )
        query += f"\nDate Range: {start} to {end}"
        user_input.delete("1.0", tk.END)
        user_input.insert("1.0", query.strip())

    def update_query_with_predefined_range(range_name):
        """Update the query text box with a predefined range."""
        query = user_input.get("1.0", tk.END).strip()

        query = "\n".join(
            line for line in query.split("\n") if not line.startswith("Date Range:")
        )
        query += f"\nDate Range: {range_name}"
        user_input.delete("1.0", tk.END)
        user_input.insert("1.0", query.strip())

    ttk.Button(date_range_frame, text="Set Date Range", command=update_query_with_dates).grid(row=2, column=0, columnspan=2, pady=5)

    predefined_ranges_frame = ttk.Frame(date_range_frame)
    predefined_ranges_frame.grid(row=3, column=0, columnspan=2, pady=10)

    ttk.Button(predefined_ranges_frame, text="This Month", command=lambda: update_query_with_predefined_range("This Month")).pack(side="left", padx=5)
    ttk.Button(predefined_ranges_frame, text="Last Month", command=lambda: update_query_with_predefined_range("Last Month")).pack(side="left", padx=5)
    ttk.Button(predefined_ranges_frame, text="This Year", command=lambda: update_query_with_predefined_range("This Year")).pack(side="left", padx=5)
    ttk.Button(predefined_ranges_frame, text="Last Year", command=lambda: update_query_with_predefined_range("Last Year")).pack(side="left", padx=5)
    ttk.Button(predefined_ranges_frame, text="All", command=lambda: update_query_with_predefined_range("All")).pack(side="left", padx=5)

    response_frame = ttk.LabelFrame(tab_frame, text="AI Response", padding=10)
    response_frame.pack(fill="both", expand=True, padx=20, pady=10)

    response_text = tk.Text(response_frame, height=15, wrap="word")
    response_text.pack(fill="both", expand=True, pady=5)
    response_text.config(state=tk.DISABLED)

    loading_label = ttk.Label(tab_frame, text="", foreground="blue")
    loading_label.pack(pady=5)

    load_fixed_queries()

    def fetch_database_data():
        """Fetch all relevant data from the database."""
        try:
            income = get_income_tracker(user_id)
            expenses = get_expenses_tracker(user_id)
            income_sources = get_income_sources(user_id)
            recurring_income = get_recurring_income(user_id)
            recurring_transactions = get_recurring_transactions(user_id)
            expense_categories = get_expenses_category(user_id)

            return {
                "income": income,
                "expenses": expenses,
                "income_sources": income_sources,
                "recurring_income": recurring_income,
                "recurring_transactions": recurring_transactions,
                "expense_categories": expense_categories,
            }
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching data: {e}")
            return None

    def get_openai_response():
        query = user_input.get("1.0", tk.END).strip()

        loading_label.config(text="Loading... please wait.")
        response_text.config(state=tk.NORMAL)

        data = fetch_database_data()
        if not data:
            return

        prompt = f"User Query: {query}\n\nHere is the user's financial data:\n"

        if data["income"]:
            prompt += "Income Records:\n" + "\n".join(
                [f"ID: {i[0]}, Amount: {i[2]}, Description: {i[3]}, Date: {i[4]}" for i in data["income"]]
            ) + "\n\n"

        if data["expenses"]:
            prompt += "Expense Records:\n" + "\n".join(
                [f"ID: {e[0]}, Amount: {e[2]}, Description: {e[1]}, Date: {e[4]}" for e in data["expenses"]]
            ) + "\n\n"

        if data["income_sources"]:
            prompt += "Income Sources:\n" + "\n".join(
                [f"ID: {s[0]}, Name: {s[1]}, Description: {s[2]}" for s in data["income_sources"]]
            ) + "\n\n"

        if data["recurring_income"]:
            prompt += "Recurring Income:\n" + "\n".join(
                [
                    f"ID: {r[0]}, Amount: {r[2]}, Description: {r[3]}, Frequency: {r[4]}, Next Date: {r[7]}"
                    for r in data["recurring_income"]
                ]
            ) + "\n\n"

        if data["recurring_transactions"]:
            prompt += "Recurring Transactions:\n" + "\n".join(
                [
                    f"ID: {rt[0]}, Amount: {rt[2]}, Name: {rt[3]}, Category: {rt[4]}, Recurrence: {rt[5]}, Next Due Date: {rt[7]}"
                    for rt in data["recurring_transactions"]
                ]
            ) + "\n\n"

        if data["expense_categories"]:
            prompt += "Expense Categories:\n" + "\n".join(
                [f"ID: {ec[0]}, Name: {ec[2]}" for ec in data["expense_categories"]]
            ) + "\n\n"

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            }
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful financial assistant."},
                    {"role": "user", "content": prompt},
                ],
            }
            response = requests.post(API_URL, headers=headers, json=payload)
            response_data = response.json()

            if "choices" in response_data and len(response_data["choices"]) > 0:
                result = response_data["choices"][0]["message"]["content"]
            else:
                result = "No valid response received from OpenAI."

        except Exception as e:
            result = f"Error occurred: {e}"

        response_text.delete("1.0", tk.END)
        response_text.insert("1.0", result)
        response_text.config(state=tk.DISABLED)
        loading_label.config(text="")

    def read_aloud():
        """Read the response text aloud in a separate thread."""
        global tts_thread, stop_reading_flag

        if tts_thread and tts_thread.is_alive():
            messagebox.showinfo("Info", "Already reading aloud!")
            return

        stop_reading_flag = False

        def tts_worker():
            """Worker function to read text in a separate thread."""
            text = response_text.get("1.0", tk.END).strip()
            if text:
                tts_engine.say(text)
                tts_engine.runAndWait()

        tts_thread = threading.Thread(target=tts_worker, daemon=True)
        tts_thread.start()

        threading.Thread(target=tts_worker, daemon=True).start()
        read_aloud_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)

    def stop_reading():
        """Stop reading the response text."""
        global stop_reading_flag
        stop_reading_flag = True
        tts_engine.stop()
        read_aloud_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)

    button_frame = ttk.Frame(tab_frame)
    button_frame.pack(pady=10)

    submit_button = ttk.Button(button_frame, text="Submit", command=get_openai_response)
    submit_button.pack(side="left", padx=5)

    read_aloud_button = ttk.Button(button_frame, text="Read Aloud", command=read_aloud)
    read_aloud_button.pack(side="left", padx=5)

    stop_button = ttk.Button(button_frame, text="Stop Reading", command=stop_reading)
    stop_button.pack(side="left", padx=5)
    stop_button.config(state=tk.DISABLED)