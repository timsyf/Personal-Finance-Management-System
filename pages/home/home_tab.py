import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pages.home.database import get_all_transactions, change_password
from pages.auth.auth_window import AuthWindow
from .database import (
    get_monthly_summary,
    get_budget_status,
    get_upcoming_transactions,
    get_user_info,
    update_user_profile
)

class HomeTab:
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Welcome section
        self.setup_welcome_section()
        
        # Financial Overview section
        self.setup_financial_overview()
        
        # Budget Status section
        self.setup_budget_status()
        
        # Upcoming Transactions section
        self.setup_upcoming_transactions()
        
        # Profile section
        self.setup_profile_section()
        
        # Button frame for refresh and logout
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)
        
        # Refresh button
        refresh_btn = ttk.Button(
            button_frame, 
            text="Refresh Dashboard",
            command=self.refresh_all
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Logout button
        logout_btn = ttk.Button(
            button_frame,
            text="Logout",
            command=self.logout
        )
        logout_btn.pack(side=tk.LEFT, padx=5)
        
        # Initial data load
        self.refresh_all()
        
    def setup_welcome_section(self):
        welcome_frame = ttk.LabelFrame(self.frame, text="Welcome")
        welcome_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.welcome_label = ttk.Label(
            welcome_frame,
            text="Welcome back!",
            font=("Helvetica", 12)
        )
        self.welcome_label.pack(pady=10)
        
    def setup_financial_overview(self):
        finance_frame = ttk.LabelFrame(self.frame, text="Financial Overview")
        finance_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create and pack labels for financial data
        self.income_label = ttk.Label(finance_frame, text="Monthly Income: $0")
        self.income_label.pack(pady=5)
        
        self.expenses_label = ttk.Label(finance_frame, text="Monthly Expenses: $0")
        self.expenses_label.pack(pady=5)
        
        self.net_label = ttk.Label(finance_frame, text="Net Amount: $0")
        self.net_label.pack(pady=5)
        
    def setup_budget_status(self):
        budget_frame = ttk.LabelFrame(self.frame, text="Budget Status")
        budget_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.within_budget_label = ttk.Label(
            budget_frame,
            text="Categories Within Budget: 0"
        )
        self.within_budget_label.pack(pady=5)
        
        self.exceeding_budget_label = ttk.Label(
            budget_frame,
            text="Categories Exceeding Budget: 0"
        )
        self.exceeding_budget_label.pack(pady=5)
        
    def setup_upcoming_transactions(self):
        upcoming_frame = ttk.LabelFrame(self.frame, text="Upcoming Transactions")
        upcoming_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.recurring_income_label = ttk.Label(
            upcoming_frame,
            text="Upcoming Recurring Income: 0"
        )
        self.recurring_income_label.pack(pady=5)
        
        self.recurring_expenses_label = ttk.Label(
            upcoming_frame,
            text="Upcoming Recurring Expenses: 0"
        )
        self.recurring_expenses_label.pack(pady=5)
        
    def setup_profile_section(self):
        profile_frame = ttk.LabelFrame(self.frame, text="Profile")
        profile_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Username
        username_frame = ttk.Frame(profile_frame)
        username_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            username_frame,
            textvariable=self.username_var
        )
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        # Email
        email_frame = ttk.Frame(profile_frame)
        email_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(email_frame, text="Email:").pack(side=tk.LEFT)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(
            email_frame,
            textvariable=self.email_var
        )
        self.email_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(profile_frame)
        buttons_frame.pack(pady=5)
        
        # Update Profile button
        update_btn = ttk.Button(
            buttons_frame,
            text="Update Profile",
            command=self.save_profile
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Change Password button
        change_pwd_btn = ttk.Button(
            buttons_frame,
            text="Change Password",
            command=self.show_password_dialog
        )
        change_pwd_btn.pack(side=tk.LEFT, padx=5)
        
    def show_password_dialog(self):
        # Create a new top-level window
        dialog = tk.Toplevel(self.frame)
        dialog.title("Change Password")
        dialog.geometry("300x250")  
        dialog.transient(self.frame) 
        dialog.grab_set()  
        
        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add password fields
        ttk.Label(main_frame, text="Current Password:").pack(pady=(0,5))
        current_pwd = ttk.Entry(main_frame, show="*")
        current_pwd.pack(fill=tk.X, pady=(0,10))
        
        ttk.Label(main_frame, text="New Password:").pack(pady=(0,5))
        new_pwd = ttk.Entry(main_frame, show="*")
        new_pwd.pack(fill=tk.X, pady=(0,10))
        
        ttk.Label(main_frame, text="Confirm New Password:").pack(pady=(0,5))
        confirm_pwd = ttk.Entry(main_frame, show="*")
        confirm_pwd.pack(fill=tk.X, pady=(0,10))
        
        def update_password():
            if new_pwd.get() != confirm_pwd.get():
                messagebox.showerror("Error", "New passwords do not match!")
                return
                
            if len(new_pwd.get()) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long!")
                return
                
            success, message = change_password(
                self.user_id,
                current_pwd.get(),
                new_pwd.get()
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10,0))
        
        # Add update and cancel buttons
        ttk.Button(
            button_frame,
            text="Update Password",
            command=update_password
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        current_pwd.focus()
        
    def refresh_all(self):
        """Refresh all sections of the dashboard"""
        # Update welcome message with username
        user_info = get_user_info(self.user_id)
        if user_info:
            self.welcome_label.config(
                text=f"Welcome back, {user_info['username']}!"
            )
            self.username_var.set(user_info['username'])
            self.email_var.set(user_info['email'])
            
        # Update financial overview
        summary = get_monthly_summary(self.user_id)
        self.income_label.config(
            text=f"Monthly Income: ${summary['income']:,.2f}"
        )
        self.expenses_label.config(
            text=f"Monthly Expenses: ${summary['expenses']:,.2f}"
        )
        self.net_label.config(
            text=f"Net Amount: ${summary['net']:,.2f}"
        )
        
        # Update budget status
        budget = get_budget_status(self.user_id)
        self.within_budget_label.config(
            text=f"Categories Within Budget: {budget['within_budget']}"
        )
        self.exceeding_budget_label.config(
            text=f"Categories Exceeding Budget: {budget['exceeding_budget']}"
        )
        
        # Update upcoming transactions
        upcoming = get_upcoming_transactions(self.user_id)
        self.recurring_income_label.config(
            text=f"Upcoming Recurring Income: {upcoming['recurring_income']}"
        )
        self.recurring_expenses_label.config(
            text=f"Upcoming Recurring Expenses: {upcoming['recurring_expenses']}"
        )
        
    def save_profile(self):
        """Save updated profile information"""
        success, message = update_user_profile(
            self.user_id,
            username=self.username_var.get(),
            email=self.email_var.get()
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_all()
        else:
            messagebox.showerror("Error", message)

    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            # Clear all tabs from notebook
            for tab in self.parent.tabs():
                self.parent.forget(tab)
            
            # Close the main window and show login window
            self.parent.master.destroy()
            auth_window = AuthWindow()
            auth_window.run()

def create_home_tab(notebook, user_id):
    """Create and return the home tab"""
    home_tab = HomeTab(notebook, user_id)
    notebook.add(home_tab.frame, text="Home")
    return home_tab

def view_transactions(listbox, user_id):
    rows = get_all_transactions(user_id)
    listbox.delete(0, tk.END)
    for row in rows:
        listbox.insert(tk.END, f"{row[0]} | {row[1]} | ${row[2]} | {row[3]}")

