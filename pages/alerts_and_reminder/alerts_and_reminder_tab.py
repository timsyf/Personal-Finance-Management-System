import tkinter as tk
from tkinter import ttk
from .database import check_budget_exceeded, fetch_alerts

def create_alerts_and_reminder_tab(notebook, user_id):
    # Create a new tab frame
    tab_frame = ttk.Frame(notebook)

    # Add the tab to the notebook
    notebook.add(tab_frame, text="Alerts and Reminder")

    def refresh_alerts():
        # Clear the current contents of the tab frame
        for widget in tab_frame.winfo_children():
            widget.destroy()

        # Add a title
        tk.Label(tab_frame, text="Alerts and Reminder Tab", font=("Arial", 16)).pack(pady=10)



        # Fetch alerts from the database
        alerts = fetch_alerts(user_id)

        # Display Alerts Section
        if alerts:
            tk.Label(tab_frame, text="Alerts", font=("Arial", 14), fg="red").pack(anchor="w", padx=10, pady=5)
            for alert in alerts:
                tk.Label(tab_frame, text=f"{alert['alert_message']} (Logged at: {alert['created_at']})", fg="red").pack(anchor="w", padx=20)
        else:
            tk.Label(tab_frame, text="No alerts!", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)

        # Placeholder for future reminders section


    def on_tab_changed(event):
        # Ensure that the tab is refreshed only when it's active
        if notebook.index("current") == notebook.index(tab_frame):
            refresh_alerts()

    # Bind the tab change event after the tab is added
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    # Refresh alerts when the tab is first created
    refresh_alerts()
