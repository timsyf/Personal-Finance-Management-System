import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta, date
from .database import (
    add_income, get_income, update_income, delete_income,
    get_monthly_income, get_total_income, get_income_sources,
    add_income_source, update_income_source, delete_income_source,
    add_recurring_income, get_recurring_income, update_recurring_income,
    delete_recurring_income, get_income_date_range
)

class IncomeTrackingTab:
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.selected_income_id = None
        self.selected_source_id = None
        self.sources = {}  # Dictionary to store source_id -> source_name mapping
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)
        
        # Create frames for each tab
        self.records_frame = ttk.Frame(self.notebook)
        self.recurring_frame = ttk.Frame(self.notebook)
        self.sources_frame = ttk.Frame(self.notebook)
        
        # Setup all tabs first
        self.setup_sources_tab()  # Setup sources first since other tabs depend on it
        self.setup_records_tab()
        self.setup_recurring_tab()
        
        # Add tabs to notebook after setup
        self.notebook.add(self.records_frame, text="Income Records")
        self.notebook.add(self.recurring_frame, text="Recurring Income")
        self.notebook.add(self.sources_frame, text="Manage Sources")
        
        # Load initial data
        self.load_sources()
        self.update_source_combo()
        self.load_income_data()
        self.load_recurring_income()
        
    def setup_records_tab(self):
        # Left Frame - Income List
        self.list_frame = ttk.LabelFrame(self.records_frame, text="Income Records", padding="10")
        self.list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Add Filter Frame
        filter_frame = ttk.LabelFrame(self.list_frame, text="Filters", padding="5")
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # Date Range Filter
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="From:").pack(side="left", padx=5)
        self.date_from = DateEntry(date_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2)
        self.date_from.pack(side="left", padx=5)
        
        ttk.Label(date_frame, text="To:").pack(side="left", padx=5)
        self.date_to = DateEntry(date_frame, width=12, background='darkblue',
                               foreground='white', borderwidth=2)
        self.date_to.pack(side="left", padx=5)
        
        # Set date range based on existing records
        start_date, end_date = get_income_date_range(self.user_id)
        self.date_from.set_date(start_date)
        self.date_to.set_date(end_date)
        
        # Quick Date Filters
        quick_filter_frame = ttk.Frame(filter_frame)
        quick_filter_frame.pack(fill="x", pady=5)
        
        ttk.Button(quick_filter_frame, text="This Month", 
                  command=lambda: self.apply_quick_filter("this_month")).pack(side="left", padx=2)
        ttk.Button(quick_filter_frame, text="Last Month", 
                  command=lambda: self.apply_quick_filter("last_month")).pack(side="left", padx=2)
        ttk.Button(quick_filter_frame, text="This Year", 
                  command=lambda: self.apply_quick_filter("this_year")).pack(side="left", padx=2)
        ttk.Button(quick_filter_frame, text="Last Year", 
                  command=lambda: self.apply_quick_filter("last_year")).pack(side="left", padx=2)
        
        # Source Filter
        source_frame = ttk.Frame(filter_frame)
        source_frame.pack(fill="x", pady=5)
        
        ttk.Label(source_frame, text="Source:").pack(side="left", padx=5)
        self.filter_source_var = tk.StringVar()
        self.filter_source_combo = ttk.Combobox(source_frame, textvariable=self.filter_source_var)
        self.filter_source_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Search by Description
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill="x", pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=5, fill="x", expand=True)
        
        # Apply/Clear Filters
        btn_frame = ttk.Frame(filter_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Apply Filters", 
                  command=self.apply_filters).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Filters", 
                  command=self.clear_filters).pack(side="left", padx=5)
        
        # Create Treeview below filters
        self.setup_income_tree()
        
        # Right Frame - Add/Edit Income
        self.form_frame = ttk.LabelFrame(self.records_frame, text="Add/Edit Income", padding="10")
        self.form_frame.pack(side="right", fill="both", padx=(10, 0))
        
        self.setup_form()
        
    def setup_recurring_tab(self):
        # Setup recurring income tab
        self.setup_recurring_form()
        
    def setup_sources_tab(self):
        # Left Frame - Sources List
        sources_list_frame = ttk.LabelFrame(self.sources_frame, text="Income Sources", padding="10")
        sources_list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(sources_list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview for sources
        columns = ("ID", "Name", "Description")
        self.sources_tree = ttk.Treeview(sources_list_frame, columns=columns, show="headings", 
                                       yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.sources_tree.yview)
        
        # Configure columns
        self.sources_tree.heading("ID", text="ID")
        self.sources_tree.heading("Name", text="Name")
        self.sources_tree.heading("Description", text="Description")
        
        self.sources_tree.column("ID", width=50)
        self.sources_tree.column("Name", width=150)
        self.sources_tree.column("Description", width=200)
        
        self.sources_tree.pack(fill="both", expand=True)
        
        # Bind select event
        self.sources_tree.bind("<<TreeviewSelect>>", self.on_select_source)
        
        # Right Frame - Add/Edit Source
        source_form_frame = ttk.LabelFrame(self.sources_frame, text="Add/Edit Source", padding="10")
        source_form_frame.pack(side="right", fill="both", padx=(10, 0))
        
        # Source Name
        ttk.Label(source_form_frame, text="Source Name:").pack(pady=5)
        self.source_name_var = tk.StringVar()
        self.source_name_entry = ttk.Entry(source_form_frame, textvariable=self.source_name_var)
        self.source_name_entry.pack(pady=5, fill="x")
        
        # Source Description
        ttk.Label(source_form_frame, text="Description:").pack(pady=5)
        self.source_desc_var = tk.StringVar()
        self.source_desc_entry = ttk.Entry(source_form_frame, textvariable=self.source_desc_var)
        self.source_desc_entry.pack(pady=5, fill="x")
        
        # Buttons
        btn_frame = ttk.Frame(source_form_frame)
        btn_frame.pack(pady=20, fill="x")
        
        ttk.Button(btn_frame, text="Add Source", 
                  command=self.add_source).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Source", 
                  command=self.update_source).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Source", 
                  command=self.delete_source).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", 
                  command=self.clear_source_form).pack(side="left", padx=5)
        
    def setup_income_tree(self):
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview
        columns = ("ID", "Date", "Description", "Amount", "Source")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", 
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Source", text="Source")
        
        self.tree.column("ID", width=50)
        self.tree.column("Date", width=100)
        self.tree.column("Description", width=200)
        self.tree.column("Amount", width=100)
        self.tree.column("Source", width=100)
        
        self.tree.pack(fill="both", expand=True)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_select_income)
        
    def setup_form(self):
        # Create notebook for form tabs
        form_notebook = ttk.Notebook(self.form_frame)
        form_notebook.pack(fill="both", expand=True)
        
        # Regular Income Tab
        regular_frame = ttk.Frame(form_notebook)
        form_notebook.add(regular_frame, text="One-time Income")
        
        # Setup regular form
        self.setup_regular_form(regular_frame)
        
        # Initialize total income variable
        self.total_income_var = tk.StringVar()
        ttk.Label(self.form_frame, textvariable=self.total_income_var).pack(pady=10)
        self.total_income_var.set("Total Income: $0.00")
        
    def setup_regular_form(self, parent):
        # Amount
        ttk.Label(parent, text="Amount:").pack(pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(parent, textvariable=self.amount_var)
        self.amount_entry.pack(pady=5, fill="x")
        
        # Description
        ttk.Label(parent, text="Description:").pack(pady=5)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(parent, textvariable=self.description_var)
        self.description_entry.pack(pady=5, fill="x")
        
        # Date
        ttk.Label(parent, text="Date:").pack(pady=5)
        self.date_entry = DateEntry(parent, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_entry.pack(pady=5)
        
        # Source
        ttk.Label(parent, text="Source:").pack(pady=5)
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(parent, textvariable=self.source_var)
        self.source_combo.pack(pady=5, fill="x")
        self.update_source_combo()
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=20, fill="x")
        
        ttk.Button(btn_frame, text="Add Income", 
                  command=self.add_income_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", 
                  command=self.update_income_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", 
                  command=self.delete_income_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", 
                  command=self.clear_form).pack(side="left", padx=5)
        
    def setup_recurring_form(self):
        # Split frame for list and form
        list_frame = ttk.Frame(self.recurring_frame)
        list_frame.pack(side="left", fill="both", expand=True)
        
        form_frame = ttk.Frame(self.recurring_frame)
        form_frame.pack(side="right", fill="y", padx=10)
        
        # Recurring income list
        columns = ("id", "description", "amount", "frequency", "next_date", "source")
        self.recurring_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configure columns
        self.recurring_tree.heading("id", text="ID")
        self.recurring_tree.heading("description", text="Description")
        self.recurring_tree.heading("amount", text="Amount")
        self.recurring_tree.heading("frequency", text="Frequency")
        self.recurring_tree.heading("next_date", text="Next Date")
        self.recurring_tree.heading("source", text="Source")
        
        self.recurring_tree.column("id", width=50)
        self.recurring_tree.column("description", width=200)
        self.recurring_tree.column("amount", width=100)
        self.recurring_tree.column("frequency", width=100)
        self.recurring_tree.column("next_date", width=100)
        self.recurring_tree.column("source", width=150)
        
        self.recurring_tree.pack(fill="both", expand=True)
        self.recurring_tree.bind("<<TreeviewSelect>>", self.on_recurring_select)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.recurring_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.recurring_tree.configure(yscrollcommand=scrollbar.set)
        
        # Recurring income form
        ttk.Label(form_frame, text="Add/Edit Recurring Income", font=("", 10, "bold")).pack(pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").pack(pady=2)
        self.recurring_description = ttk.Entry(form_frame, width=30)
        self.recurring_description.pack(pady=2)
        
        # Amount
        ttk.Label(form_frame, text="Amount:").pack(pady=2)
        self.recurring_amount = ttk.Entry(form_frame, width=30)
        self.recurring_amount.pack(pady=2)
        
        # Source
        ttk.Label(form_frame, text="Source:").pack(pady=2)
        self.recurring_source = ttk.Combobox(form_frame, width=27, state="readonly")
        self.recurring_source.pack(pady=2)
        
        # Frequency
        ttk.Label(form_frame, text="Frequency:").pack(pady=2)
        self.recurring_frequency = ttk.Combobox(form_frame, width=27, state="readonly")
        self.recurring_frequency["values"] = ("Monthly", "Bi-monthly", "Quarterly", 
                                            "Semi-annually", "Annually")
        self.recurring_frequency.set("Monthly")
        self.recurring_frequency.pack(pady=2)
        
        # Start Date
        ttk.Label(form_frame, text="Start Date:").pack(pady=2)
        self.recurring_start_date = DateEntry(form_frame, width=27, date_pattern="yyyy-mm-dd")
        self.recurring_start_date.pack(pady=2)
        
        # End Date (Optional)
        ttk.Label(form_frame, text="End Date (Optional):").pack(pady=2)
        self.recurring_end_date = DateEntry(form_frame, width=27, date_pattern="yyyy-mm-dd")
        self.recurring_end_date.pack(pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self.add_recurring).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_recurring).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_recurring).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_recurring_form).pack(side="left", padx=5)
        
    def add_recurring(self):
        try:
            amount = float(self.recurring_amount.get())
            description = self.recurring_description.get().strip()
            source_name = self.recurring_source.get()
            frequency = self.recurring_frequency.get()
            start_date = self.recurring_start_date.get_date()
            end_date = self.recurring_end_date.get_date()
            
            if not description or not source_name:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
                
            source_id = self.get_source_id_by_name(source_name)
            if not source_id:
                messagebox.showerror("Error", "Please select a valid source")
                return
            
            success, message = add_recurring_income(
                self.user_id, amount, description, source_id, frequency, 
                start_date, end_date
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_recurring_form()
                self.load_recurring_income()
                self.load_income_data()  # Refresh regular income list
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            
    def update_recurring(self):
        selection = self.recurring_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a recurring income to update")
            return
        
        try:
            recurring_id = self.recurring_tree.item(selection[0])["values"][0]
            amount = float(self.recurring_amount.get())
            description = self.recurring_description.get().strip()
            source_name = self.recurring_source.get()
            frequency = self.recurring_frequency.get()
            start_date = self.recurring_start_date.get_date()
            end_date = self.recurring_end_date.get_date()
            
            if not description or not source_name:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
                
            source_id = self.get_source_id_by_name(source_name)
            if not source_id:
                messagebox.showerror("Error", "Please select a valid source")
                return
            
            success, message = update_recurring_income(
                recurring_id, self.user_id, amount, description, source_id,
                frequency, start_date, end_date
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_recurring_form()
                self.load_recurring_income()
                self.load_income_data()  # Refresh regular income list
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            
    def delete_recurring(self):
        selection = self.recurring_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a recurring income to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Do you want to delete future transactions as well?"):
            recurring_id = self.recurring_tree.item(selection[0])["values"][0]
            success, message = delete_recurring_income(recurring_id, self.user_id, True)
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_recurring_form()
                self.load_recurring_income()
                self.load_income_data()  # Refresh regular income list
            else:
                messagebox.showerror("Error", message)
            
    def clear_recurring_form(self):
        self.recurring_description.delete(0, "end")
        self.recurring_amount.delete(0, "end")
        self.recurring_source.set("")
        self.recurring_frequency.set("Monthly")
        self.recurring_start_date.set_date(date.today())
        self.recurring_end_date.set_date(date.today())
        self.recurring_tree.selection_remove(*self.recurring_tree.selection())
        
    def on_recurring_select(self, event):
        selection = self.recurring_tree.selection()
        if selection:
            values = self.recurring_tree.item(selection[0])["values"]
            self.recurring_description.delete(0, "end")
            self.recurring_description.insert(0, values[1])
            self.recurring_amount.delete(0, "end")
            self.recurring_amount.insert(0, values[2])
            self.recurring_source.set(values[5])
            self.recurring_frequency.set(values[3])
            self.recurring_start_date.set_date(datetime.strptime(values[4], "%Y-%m-%d").date())
        
    def load_recurring_income(self):
        # Clear existing items
        for item in self.recurring_tree.get_children():
            self.recurring_tree.delete(item)
        
        # Load recurring income records
        records = get_recurring_income(self.user_id)
        for record in records:
            self.recurring_tree.insert("", "end", values=(
                record["id"],
                record["description"],
                record["amount"],
                record["frequency"],
                record["next_date"].strftime("%Y-%m-%d"),
                record["source"]
            ))
    
    def update_source_combo(self):
        """Update source comboboxes with current sources"""
        sources = get_income_sources(self.user_id)
        print(f"Retrieved sources: {sources}")  # Debug print
        
        self.sources = {source['id']: source['name'] for source in sources}
        print(f"Sources mapping: {self.sources}")  # Debug print
        
        source_names = list(self.sources.values())
        
        # Update source combo for adding income
        self.source_combo['values'] = source_names
        self.source_combo.set('')
        
        # Update filter source combo
        filter_sources = ['All Sources'] + source_names
        self.filter_source_combo['values'] = filter_sources
        self.filter_source_combo.set('All Sources')
        
        # Update recurring income source combo if it exists
        if hasattr(self, 'recurring_source'):
            self.recurring_source['values'] = source_names
            
    def get_source_id_by_name(self, source_name):
        """Get source ID from source name"""
        print(f"Looking for source name: '{source_name}' in {self.sources}")  # Debug print
        for source_id, name in self.sources.items():
            if name == source_name:
                print(f"Found source_id: {source_id}")  # Debug print
                return source_id
        print("Source not found")  # Debug print
        return None
        
    def get_source_name_by_id(self, source_id):
        """Get source name from source ID"""
        return self.sources.get(source_id, '')
        
    def load_sources(self):
        """Load sources into the sources treeview"""
        for item in self.sources_tree.get_children():
            self.sources_tree.delete(item)
        
        sources = get_income_sources(self.user_id)
        for source in sources:
            self.sources_tree.insert("", "end", values=(
                source["id"],
                source["name"],
                source["description"]
            ))
    
    def on_select_source(self, event):
        """Handle source selection"""
        selected_items = self.sources_tree.selection()
        if not selected_items:
            return
        
        item = self.sources_tree.item(selected_items[0])
        values = item["values"]
        
        self.selected_source_id = values[0]
        self.source_name_var.set(values[1])
        self.source_desc_var.set(values[2])
    
    def add_source(self):
        """Add a new income source"""
        name = self.source_name_var.get().strip()
        description = self.source_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a source name")
            return
        
        success, message = add_income_source(self.user_id, name, description)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_source_form()
            self.load_sources()
            self.update_source_combo()
        else:
            messagebox.showerror("Error", message)
    
    def update_source(self):
        """Update selected income source"""
        if not self.selected_source_id:
            messagebox.showerror("Error", "Please select a source to update")
            return
        
        name = self.source_name_var.get().strip()
        description = self.source_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a source name")
            return
        
        success, message = update_income_source(
            self.selected_source_id, self.user_id, name, description
        )
        if success:
            messagebox.showinfo("Success", message)
            self.clear_source_form()
            self.load_sources()
            self.update_source_combo()
        else:
            messagebox.showerror("Error", message)
    
    def delete_source(self):
        """Delete selected income source"""
        if not self.selected_source_id:
            messagebox.showerror("Error", "Please select a source to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this source?"):
            success, message = delete_income_source(self.selected_source_id, self.user_id)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_source_form()
                self.load_sources()
                self.update_source_combo()
            else:
                messagebox.showerror("Error", message)
    
    def clear_source_form(self):
        """Clear the source form"""
        self.selected_source_id = None
        self.source_name_var.set("")
        self.source_desc_var.set("")
    
    def load_income_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load income records
        records = get_income(self.user_id)
        for record in records:
            self.tree.insert("", "end", values=(
                record["id"],
                record["date"].strftime("%Y-%m-%d"),
                record["description"],
                f"${record['amount']:.2f}",
                record["source_name"]
            ))
        
        # Update summary
        total = get_total_income(self.user_id)
        self.total_income_var.set(f"Total Income: ${total:.2f}")
        
    def on_select_income(self, event):
        """Handle income record selection"""
        selection = self.tree.selection()
        if not selection:
            return
            
        # Get selected item values
        values = self.tree.item(selection[0])['values']
        if not values:
            return
            
        # Update form with selected values
        self.selected_income_id = values[0]
        self.amount_var.set(values[3].replace('$', ''))
        self.description_var.set(values[2])
        # Convert string date to datetime object
        try:
            date_obj = datetime.strptime(values[1], "%Y-%m-%d").date()
            self.date_entry.set_date(date_obj)
        except ValueError:
            print(f"Invalid date format: {values[1]}")
        self.source_var.set(values[4])  # source name
        
    def add_income_record(self):
        """Add a new income record"""
        try:
            amount = float(self.amount_var.get())
            description = self.description_var.get()
            date = self.date_entry.get_date()
            source_name = self.source_var.get()
            
            if not all([amount, description, date, source_name]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            source_id = self.get_source_id_by_name(source_name)
            if not source_id:
                messagebox.showerror("Error", "Please select a valid source")
                return
                
            success, message = add_income(
                self.user_id, amount, description, date, source_id
            )
            
            if success:
                self.clear_form()
                self.apply_filters()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            
    def update_income_record(self):
        """Update the selected income record"""
        if not self.selected_income_id:
            messagebox.showerror("Error", "Please select an income record to update")
            return
            
        try:
            amount = float(self.amount_var.get())
            description = self.description_var.get()
            date = self.date_entry.get_date()
            source_name = self.source_var.get()
            
            if not all([amount, description, date, source_name]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            source_id = self.get_source_id_by_name(source_name)
            if not source_id:
                messagebox.showerror("Error", "Please select a valid source")
                return
                
            success, message = update_income(
                self.selected_income_id, self.user_id,
                amount, description, date, source_id
            )
            
            if success:
                self.clear_form()
                self.apply_filters()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            
    def delete_income_record(self):
        if not self.selected_income_id:
            messagebox.showerror("Error", "Please select an income record to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this income record?"):
            success, message = delete_income(self.selected_income_id, self.user_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_income_data()
            else:
                messagebox.showerror("Error", message)
                
    def clear_form(self):
        """Clear the income form"""
        self.selected_income_id = None
        self.amount_var.set('')
        self.description_var.set('')
        self.date_entry.set_date(date.today())
        self.source_var.set('')
        
    def apply_quick_filter(self, filter_type):
        """Apply quick date filters"""
        today = datetime.now()
        if filter_type == "this_month":
            self.date_from.set_date(today.replace(day=1))
            self.date_to.set_date(today)
        elif filter_type == "last_month":
            last_month = today.replace(day=1)
            if last_month.month == 1:
                last_month = last_month.replace(year=last_month.year-1, month=12)
            else:
                last_month = last_month.replace(month=last_month.month-1)
            self.date_from.set_date(last_month)
            self.date_to.set_date(today.replace(day=1) - timedelta(days=1))
        elif filter_type == "this_year":
            self.date_from.set_date(today.replace(month=1, day=1))
            self.date_to.set_date(today)
        elif filter_type == "last_year":
            self.date_from.set_date(today.replace(year=today.year-1, month=1, day=1))
            self.date_to.set_date(today.replace(year=today.year-1, month=12, day=31))
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters to the income records"""
        # Get filter values
        start_date = self.date_from.get_date()
        end_date = self.date_to.get_date()
        selected_source = self.filter_source_var.get()
        search_text = self.search_var.get().lower()
        
        # Get income records
        records = get_income(self.user_id, start_date, end_date)
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_income = 0
        for record in records:
            # Debug print for source comparison
            print(f"Comparing - Selected: '{selected_source}' with Record: '{record['source_name']}'")
            
            # Apply source filter
            if selected_source != 'All Sources':
                if record['source_name'].strip() != selected_source.strip():
                    print(f"Source mismatch - skipping record")
                    continue
                
            # Apply search filter
            if search_text and search_text not in record['description'].lower():
                continue
                
            # Add matching record to tree
            self.tree.insert('', 'end', values=(
                record['id'],
                record['date'],
                record['description'],
                f"${record['amount']:.2f}",
                record['source_name']
            ))
            total_income += float(record['amount'])
            
        # Update total income display
        self.total_income_var.set(f"Total Income: ${total_income:.2f}")
        
        # Debug print total records
        print(f"Total records displayed: {len(self.tree.get_children())}")
    
    def clear_filters(self):
        """Clear all filters"""
        # Get the earliest and latest dates from income records
        start_date, end_date = get_income_date_range(self.user_id)
        self.date_from.set_date(start_date)
        self.date_to.set_date(end_date)
        self.filter_source_var.set("All Sources")
        self.search_var.set("")
        self.load_income_data()  # Reset to show all records

def create_income_tracking_tab(notebook, user_id):
    """Create and return the income tracking tab"""
    frame = ttk.Frame(notebook)
    income_tab = IncomeTrackingTab(frame, user_id)
    notebook.add(frame, text="Income Tracking")
    return frame