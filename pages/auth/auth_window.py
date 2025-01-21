import tkinter as tk
from tkinter import ttk, messagebox
from .database import create_user, verify_user, username_exists, email_exists, create_tables
from .admin_panel import AdminPanel
import re

class AuthWindow:
    def __init__(self):
        # Create necessary database tables
        create_tables()
        
        self.window = tk.Tk()
        self.window.title("Personal Finance Management System")
        self.window.geometry("400x500")
        
        # Store user_id after successful login
        self.current_user_id = None
        self.is_admin = False
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(pady=10, expand=True)
        
        # Login Frame
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        
        # Signup Frame
        self.signup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.signup_frame, text="Sign Up")
        
        self.setup_login_frame()
        self.setup_signup_frame()
    
    def setup_login_frame(self):
        # Create a main container frame
        container = ttk.Frame(self.login_frame)
        container.pack(expand=True, fill="both", padx=50, pady=20)
        
        # Username
        ttk.Label(container, text="Username:").pack(pady=5)
        self.login_username = ttk.Entry(container, width=30)
        self.login_username.pack(pady=5)
        
        # Password
        ttk.Label(container, text="Password:").pack(pady=5)
        self.login_password = ttk.Entry(container, width=30, show="*")
        self.login_password.pack(pady=5)
        
        # Login Button
        ttk.Button(container, text="Login", command=self.login).pack(pady=20)
    
    def setup_signup_frame(self):
        # Create a main container frame
        container = ttk.Frame(self.signup_frame)
        container.pack(expand=True, fill="both", padx=50, pady=20)
        
        # Username
        ttk.Label(container, text="Username:").pack(pady=5)
        self.signup_username = ttk.Entry(container, width=30)
        self.signup_username.pack(pady=5)
        
        # Email
        ttk.Label(container, text="Email:").pack(pady=5)
        self.signup_email = ttk.Entry(container, width=30)
        self.signup_email.pack(pady=5)
        
        # Password
        ttk.Label(container, text="Password:").pack(pady=5)
        self.signup_password = ttk.Entry(container, width=30, show="*")
        self.signup_password.pack(pady=5)
        
        # Confirm Password
        ttk.Label(container, text="Confirm Password:").pack(pady=5)
        self.signup_confirm_password = ttk.Entry(container, width=30, show="*")
        self.signup_confirm_password.pack(pady=5)
        
        # Sign Up Button
        ttk.Button(container, text="Sign Up", command=self.signup).pack(pady=20)
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        user = verify_user(username, password)
        if user:
            self.current_user_id = user["id"]
            self.is_admin = user["is_admin"]
            
            if self.is_admin:
                # For admin users, just show admin panel
                self.window.withdraw()  # Hide login window
                admin_panel = AdminPanel(self.current_user_id)
                admin_panel.window.protocol("WM_DELETE_WINDOW", lambda: self.on_admin_panel_close(admin_panel))
            else:
                # For regular users, proceed to main application
                self.window.destroy()
                self.start_main_application()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def on_admin_panel_close(self, admin_panel):
        """Handle admin panel closure"""
        admin_panel.window.destroy()
        self.window.destroy()  # Close the login window 
    
    def signup(self):
        username = self.signup_username.get()
        email = self.signup_email.get()
        password = self.signup_password.get()
        confirm_password = self.signup_confirm_password.get()
        
        if not username or not email or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if username_exists(username):
            messagebox.showerror("Error", "Username already exists")
            return
        
        if email_exists(email):
            messagebox.showerror("Error", "Email already exists")
            return
        
        if create_user(username, password, email):
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.notebook.select(0)  # Switch to login tab
            self.signup_username.delete(0, tk.END)
            self.signup_email.delete(0, tk.END)
            self.signup_password.delete(0, tk.END)
            self.signup_confirm_password.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Failed to create account")
    
    def start_main_application(self):
        from main import main
        main(self.current_user_id)
    
    def run(self):
        self.window.mainloop() 