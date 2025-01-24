import tkinter as tk
from tkinter import ttk, messagebox
from .database import get_all_users, change_user_password, delete_user, create_user_by_admin, update_user

class AdminPanel:
    def __init__(self, admin_id):
        self.admin_id = admin_id
        self.window = tk.Toplevel()
        self.window.title("Admin Control Panel")
        self.window.geometry("800x600")
        
        def on_closing():
            """Handle admin panel window closing"""
            if messagebox.askyesno("Close Admin Panel", "Are you sure you want to close the admin panel?"):
                self.window.destroy()
        
        self.window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Top frame for title and logout
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Welcome label on the left
        ttk.Label(
            top_frame, 
            text="Admin Control Panel", 
            font=("Arial", 16, "bold")
        ).pack(side="left")
        
        # Logout button on the right
        ttk.Button(
            top_frame,
            text="Logout",
            command=self.logout
        ).pack(side="right", padx=5)
        
        # Create notebook for different admin functions
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Users List Tab
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Users Management")
        self.setup_users_list()
        
        # Create User Tab
        self.create_user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.create_user_frame, text="Create New User")
        self.setup_create_user()
    
    def setup_users_list(self):
        # Create main container
        container = ttk.Frame(self.users_frame, padding="20")
        container.pack(expand=True, fill="both")
        
        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(container)
        tree_frame.pack(expand=True, fill="both")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview
        columns = ("ID", "Username", "Email", "Is Admin", "Created At")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Set column headings and widths
        column_widths = {
            "ID": 50,
            "Username": 150,
            "Email": 200,
            "Is Admin": 100,
            "Created At": 150
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])
        
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Buttons Frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=10)
        
        # Center the buttons
        buttons_container = ttk.Frame(btn_frame)
        buttons_container.pack(expand=True)
        
        ttk.Button(buttons_container, text="Refresh", 
                  command=self.refresh_users).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Update User", 
                  command=self.update_user_dialog).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Change Password", 
                  command=self.change_password_dialog).pack(side="left", padx=5)
        ttk.Button(buttons_container, text="Delete User", 
                  command=self.delete_user_dialog).pack(side="left", padx=5)
        
        self.refresh_users()
    
    def setup_create_user(self):
        # Create main container
        container = ttk.Frame(self.create_user_frame, padding="20")
        container.pack(expand=True, fill="both")
        
        # Center the form
        form_frame = ttk.Frame(container)
        form_frame.pack(expand=True, pady=(50, 0))
        
        # Username
        ttk.Label(form_frame, text="Username:").pack(pady=5)
        self.new_username = ttk.Entry(form_frame, width=30)
        self.new_username.pack(pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").pack(pady=5)
        self.new_email = ttk.Entry(form_frame, width=30)
        self.new_email.pack(pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password:").pack(pady=5)
        self.new_password = ttk.Entry(form_frame, width=30, show="*")
        self.new_password.pack(pady=5)
        
        # Is Admin
        self.is_admin_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Is Admin", variable=self.is_admin_var).pack(pady=5)
        
        # Create Button
        ttk.Button(form_frame, text="Create User", command=self.create_user).pack(pady=20)
    
    def refresh_users(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch and insert users
        users = get_all_users()
        for user in users:
            self.tree.insert("", "end", values=(
                user["id"],
                user["username"],
                user["email"],
                "Yes" if user["is_admin"] else "No",
                user["created_at"]
            ))
    
    def change_password_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user")
            return
        
        user_id = self.tree.item(selected[0])["values"][0]
        
        # Create dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Change Password")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="New Password:").pack(pady=5)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.pack(pady=5)
        
        def change():
            success, message = change_user_password(user_id, password_entry.get(), self.admin_id)
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        ttk.Button(dialog, text="Change", command=change).pack(pady=20)
    
    def delete_user_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user")
            return
        
        user_id = self.tree.item(selected[0])["values"][0]
        username = self.tree.item(selected[0])["values"][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {username}?"):
            success, message = delete_user(user_id, self.admin_id)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_users()
            else:
                messagebox.showerror("Error", message)
    
    def create_user(self):
        username = self.new_username.get()
        email = self.new_email.get()
        password = self.new_password.get()
        is_admin = self.is_admin_var.get()
        
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        success, message = create_user_by_admin(username, password, email, is_admin, self.admin_id)
        if success:
            messagebox.showinfo("Success", message)
            self.new_username.delete(0, tk.END)
            self.new_email.delete(0, tk.END)
            self.new_password.delete(0, tk.END)
            self.is_admin_var.set(False)
            self.refresh_users()
        else:
            messagebox.showerror("Error", message)

    def update_user_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user")
            return
        
        user_id = self.tree.item(selected[0])["values"][0]
        current_username = self.tree.item(selected[0])["values"][1]
        current_email = self.tree.item(selected[0])["values"][2]
        current_is_admin = self.tree.item(selected[0])["values"][3] == "Yes"
        
        # Create dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Update User")
        dialog.geometry("400x300")
        
        # Center the form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(expand=True, fill="both")
        
        # Username
        ttk.Label(form_frame, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.insert(0, current_username)
        username_entry.pack(pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.insert(0, current_email)
        email_entry.pack(pady=5)
        
        # Is Admin
        is_admin_var = tk.BooleanVar(value=current_is_admin)
        ttk.Checkbutton(form_frame, text="Is Admin", variable=is_admin_var).pack(pady=5)
        
        def update():
            success, message = update_user(
                user_id,
                username=username_entry.get(),
                email=email_entry.get(),
                is_admin=is_admin_var.get(),
                admin_id=self.admin_id
            )
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.refresh_users()
            else:
                messagebox.showerror("Error", message)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Update", command=update).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def logout(self):
        """Handle logout and return to login page"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            # Create new login window first
            from pages.auth.auth_window import AuthWindow
            auth_window = AuthWindow()
            
            # Then destroy windows in correct order
            if hasattr(self.window, 'master') and self.window.master:
                self.window.master.destroy()
            else:
                # Destroy all child windows first
                for widget in self.window.winfo_children():
                    if isinstance(widget, tk.Toplevel):
                        widget.destroy()
                self.window.destroy()
            
            # Finally run the new login window
            auth_window.run() 