import tkinter as tk
from tkinter import ttk

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

def main():
    root = tk.Tk()
    root.title("Personal Finance Management System")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    create_home_tab(notebook)
    create_dashboard_tab(notebook)
    create_income_tracking_tab(notebook)
    create_expense_tracking_tab(notebook)
    create_budget_tool_tab(notebook)
    create_expense_categories_tab(notebook)
    create_financial_data_visualization_tab(notebook)
    create_recurring_transactions_tab(notebook)
    create_alerts_and_reminder_tab(notebook)
    create_data_export_and_import_tab(notebook)
    create_ai_insights_tab(notebook)
    

    root.mainloop()

if __name__ == "__main__":
    main()