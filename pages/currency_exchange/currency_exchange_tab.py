import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pyperclip
from .constants import CURRENCIES
from .api import CurrencyExchangeAPI

class CurrencyExchangeTab:
    def __init__(self, parent):
        self.parent = parent
        self.api = CurrencyExchangeAPI()
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.parent, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Currency Exchange Calculator", 
                              font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Input Section Frame
        input_frame = ttk.LabelFrame(main_frame, text="Currency Conversion", padding="10")
        input_frame.pack(fill="x", pady=5)
        
        # Grid layout for aligned inputs
        # Amount Row
        ttk.Label(input_frame, text="Amount:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # From Currency Row
        ttk.Label(input_frame, text="From Currency:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5)
        self.from_currency_var = tk.StringVar()
        self.from_currency_combo = ttk.Combobox(input_frame, 
                                              textvariable=self.from_currency_var,
                                              values=list(CURRENCIES.keys()),
                                              state="readonly",
                                              width=17)
        self.from_currency_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.from_currency_combo.set("USD")
        
        # To Currency Row
        ttk.Label(input_frame, text="To Currency:", width=15, anchor="e").grid(row=2, column=0, padx=5, pady=5)
        self.to_currency_var = tk.StringVar()
        self.to_currency_combo = ttk.Combobox(input_frame, 
                                            textvariable=self.to_currency_var,
                                            values=list(CURRENCIES.keys()),
                                            state="readonly",
                                            width=17)
        self.to_currency_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.to_currency_combo.set("SGD")
        
        # Swap Button - centered below currency inputs
        ttk.Button(input_frame, text="⇅ Swap Currencies", 
                  command=self.swap_currencies).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Rate Information Frame
        rate_frame = ttk.LabelFrame(main_frame, text="Exchange Rate Information", padding="10")
        rate_frame.pack(fill="x", pady=10)
        
        self.rate_var = tk.StringVar(value="Exchange Rate: --")
        ttk.Label(rate_frame, textvariable=self.rate_var, font=("Helvetica", 10)).pack(pady=2)
        
        self.last_updated_var = tk.StringVar(value="Last Updated: --")
        ttk.Label(rate_frame, textvariable=self.last_updated_var, font=("Helvetica", 9)).pack(pady=2)
        
        # Result Frame
        result_frame = ttk.LabelFrame(main_frame, text="Conversion Result", padding="10")
        result_frame.pack(fill="x", pady=10)
        
        self.result_var = tk.StringVar(value="Enter an amount and click Convert")
        self.result_label = ttk.Label(result_frame, textvariable=self.result_var,
                                    font=("Helvetica", 12))
        self.result_label.pack(pady=5)
        
        # Action Buttons Frame - centered
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Convert", width=15,
                  command=self.convert).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Copy Result", width=15,
                  command=self.copy_result).pack(side="left", padx=5)
        
    def swap_currencies(self):
        """Swap the from and to currencies"""
        from_curr = self.from_currency_var.get()
        to_curr = self.to_currency_var.get()
        self.from_currency_var.set(to_curr)
        self.to_currency_var.set(from_curr)
        
    def convert(self):
        """Convert the amount between currencies"""
        try:
            # Get and validate amount
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            from_curr = self.from_currency_var.get()
            to_curr = self.to_currency_var.get()
            
            # Get conversion
            result = self.api.convert_amount(amount, from_curr, to_curr)
            
            if result['success']:
                # Update rate display
                self.rate_var.set(f"Exchange Rate: 1 {from_curr} = {result['rate']:.4f} {to_curr}")
                self.last_updated_var.set(
                    f"Last Updated: {result['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Update result
                self.result_var.set(
                    f"{amount:.2f} {from_curr} = {result['amount']:.2f} {to_curr}"
                )
            else:
                messagebox.showerror("Error", result['error'])
                
        except ValueError as e:
            messagebox.showerror("Error", "Please enter a valid positive number")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def copy_result(self):
        """Copy the converted amount to clipboard"""
        result_text = self.result_var.get()
        if "=" in result_text:
            # Extract just the converted amount
            converted_amount = result_text.split("=")[1].strip().split(" ")[0]
            pyperclip.copy(converted_amount)
            messagebox.showinfo("Success", "Result copied to clipboard!")
        else:
            messagebox.showinfo("Copy", "Please convert an amount first")

def create_currency_exchange_tab(notebook):
    """Create and return the currency exchange tab"""
    tab_frame = ttk.Frame(notebook)
    CurrencyExchangeTab(tab_frame)
    notebook.add(tab_frame, text="Currency Exchange")
    return tab_frame 