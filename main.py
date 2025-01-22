import tkinter as tk
from tkinter import ttk
from datetime import datetime


from pages.income_tracking.income_tracking_tab import create_income_tracking_tab
from pages.expense_tracking.expense_tracking_tab import create_expense_tracking_tab
from pages.budget_tool.budget_tool_tab import create_budget_tool_tab
from pages.expense_categories.expense_categories_tab import create_expense_categories_tab
from pages.financial_data_visualization.financial_data_visualization_tab import create_financial_data_visualization_tab
from pages.recurring_transactions.recurring_transactions_tab import create_recurring_transactions_tab
from pages.alerts_and_reminder.alerts_and_reminder_tab import create_alerts_and_reminder_tab
from pages.data_export_and_import.data_export_and_import_tab import create_data_export_and_import_tab
from pages.dashboard.dashboard_tab import create_dashboard_tab
from pages.home.home_tab import create_home_tab
from pages.ai_insights.ai_insights_tab import create_ai_insights_tab
from pages.auth.auth_window import AuthWindow
from pages.income_tracking.database import process_recurring_income
from pages.currency_exchange.currency_exchange_tab import create_currency_exchange_tab
import threading
import time


def main(user_id=None):
    if user_id is None:
        print("No user logged in")
        return

    root = tk.Tk()
    root.title(f"Personal Finance Management System - User ID: {user_id}")

    # Create a flag to control the processor thread
    stop_processor = False

    def on_closing():
        """Handle application closing"""
        nonlocal stop_processor
        stop_processor = True
        root.destroy()

    def recurring_income_processor():
        """Process recurring incomes while the application is running"""
        print(f"[{datetime.now()}] Starting recurring income processor...")

        while not stop_processor:
            try:
                success, message = process_recurring_income()
                if success:
                    print(f"[{datetime.now()}] {message}")
                else:
                    print(f"[{datetime.now()}] Warning: {message}")
            except Exception as e:
                print(f"[{datetime.now()}] Error in recurring income processor: {e}")

            # Sleep for 1 hour before next check
            for _ in range(360):  # Check stop_processor every 10 seconds
                if stop_processor:
                    break
                time.sleep(10)

    # Start the recurring income processor in a daemon thread
    processor_thread = threading.Thread(target=recurring_income_processor)
    processor_thread.daemon = True
    processor_thread.start()
    print(f"[{datetime.now()}] Recurring income processor thread started")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Pass user_id to all tab creation functions
    create_home_tab(notebook, user_id)
    create_dashboard_tab(notebook, user_id)
    create_income_tracking_tab(notebook, user_id)
    create_expense_tracking_tab(notebook, user_id)
    create_budget_tool_tab(notebook, user_id)
    create_expense_categories_tab(notebook, user_id)
    create_financial_data_visualization_tab(notebook, user_id)
    create_recurring_transactions_tab(notebook, user_id)
    create_alerts_and_reminder_tab(notebook, user_id)
    create_data_export_and_import_tab(notebook, user_id)
    create_ai_insights_tab(notebook, user_id)
    create_currency_exchange_tab(notebook)


    # Set up clean shutdown
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    auth_window = AuthWindow()
    auth_window.run()