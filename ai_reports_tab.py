import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
from dotenv import load_dotenv
from database import get_all_transactions

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

def create_ai_reports_tab(notebook):
    tab_frame = ttk.Frame(notebook)

    tk.Label(tab_frame, text="AI Reports", font=("Arial", 16)).pack(pady=10)
    tk.Label(tab_frame, text="Enter your query").pack(pady=5)
    user_input = tk.Text(tab_frame, height=4, width=50)
    user_input.pack(pady=5)
    response_text = tk.Text(tab_frame, height=6, width=50, wrap="word")
    response_text.pack(pady=5)
    response_text.config(state=tk.DISABLED)
    loading_label = tk.Label(tab_frame, text="", fg="blue")
    loading_label.pack()

    def get_openai_response():
        query = user_input.get("1.0", tk.END).strip()
        if not query:
            query = "Provide a summary of all transactions."

        loading_label.config(text="Loading... please wait.")
        response_text.config(state=tk.NORMAL)

        transactions = get_all_transactions()

        if not transactions:
            messagebox.showerror("Database Error", "No transactions found in the database.")
            return

        transactions_data = "Transactions:\n"
        for tx in transactions:
            transactions_data += f"ID: {tx[0]}, Description: {tx[1]}, Amount: ${tx[2]}, Date: {tx[3]}\n"

        prompt = f"Here is a list of financial transactions:\n{transactions_data}\n\nUser Query: {query}"

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            }
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful financial assistant."},
                    {"role": "user", "content": prompt},
                ],
            }
            response = requests.post(API_URL, headers=headers, json=data)
            response_data = response.json()

            if "choices" in response_data and len(response_data["choices"]) > 0:
                result = response_data["choices"][0]["message"]["content"]
            else:
                result = "No valid response received."

        except Exception as e:
            result = f"Error occurred: {e}"

        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, result)
        response_text.config(state=tk.DISABLED)
        loading_label.config(text="")

    submit_button = ttk.Button(tab_frame, text="Submit", command=get_openai_response)
    submit_button.pack(pady=10)

    notebook.add(tab_frame, text="AI Reports")