import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from tkcalendar import DateEntry
import csv
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from .database import (
    get_income_records,
    get_expense_records,
    import_income_records,
    import_expense_records,
)
import openpyxl

def create_data_export_and_import_tab(notebook, user_id):
    tab_frame = ttk.Frame(notebook)
    
    # Create main sections
    export_frame = ttk.LabelFrame(tab_frame, text="Export Data", padding="10")
    export_frame.pack(fill="x", padx=10, pady=5)
    
    import_frame = ttk.LabelFrame(tab_frame, text="Import Data", padding="10")
    import_frame.pack(fill="x", padx=10, pady=5)
    
    def create_pdf(filename, data, data_type):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        title = Paragraph(f"{data_type} Report - {datetime.now().strftime('%Y-%m-%d')}", title_style)
        elements.append(title)
        
        # Convert data to table format
        if data:
            # Get column headers from first record
            headers = list(data[0].keys())
            table_data = [headers]  # First row is headers
            
            # Add data rows
            for record in data:
                row = [str(record[col]) for col in headers]
                table_data.append(row)
            
            # Create table
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            elements.append(table)
            
            # Add summary section if applicable
            if data_type in ["Income", "Expenses"]:
                elements.append(Spacer(1, 30))
                total = sum(float(record['amount']) for record in data)
                summary_style = ParagraphStyle(
                    'Summary',
                    parent=styles['Normal'],
                    fontSize=14,
                    textColor=colors.black
                )
                summary = Paragraph(f"Total {data_type}: ${total:,.2f}", summary_style)
                elements.append(summary)
        
        # Build PDF
        doc.build(elements)
    
    # Export Section
    def export_data():
        data_type = export_type_var.get()
        file_format = format_var.get()
        
        if not data_type or not file_format:
            messagebox.showerror("Error", "Please select both data type and file format")
            return
        
        # Get dates from calendar widgets
        start_date = start_date_cal.get_date() if start_date_cal.get() else None
        end_date = end_date_cal.get_date() if end_date_cal.get() else None
            
        if start_date and end_date and start_date > end_date:
            messagebox.showerror("Error", "Start date cannot be later than end date")
            return
            
        # Get current date for filename
        current_date = datetime.now().strftime("%Y%m%d")
        
        if file_format == "CSV":
            filetypes = [("CSV files", "*.csv")]
            default_ext = ".csv"
        elif file_format == "Excel":
            filetypes = [("Excel files", "*.xlsx")]
            default_ext = ".xlsx"
        elif file_format == "PDF":
            filetypes = [("PDF files", "*.pdf")]
            default_ext = ".pdf"
            
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=f"{data_type.lower()}_{current_date}{default_ext}"
        )
        
        if filename:
            try:
                if data_type == "Income":
                    data = get_income_records(user_id, start_date, end_date)
                elif data_type == "Expenses":
                    data = get_expense_records(user_id, start_date, end_date)
                    
                if not data:
                    messagebox.showinfo("Info", "No data to export for the selected date range")
                    return
                    
                if file_format == "CSV":
                    pd.DataFrame(data).to_csv(filename, index=False)
                elif file_format == "Excel":
                    pd.DataFrame(data).to_excel(filename, index=False)
                elif file_format == "PDF":
                    create_pdf(filename, data, data_type)
                    
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    # Export Options
    export_options = ttk.Frame(export_frame)
    export_options.pack(fill="x", padx=5, pady=5)
    
    # Data Type Selection
    type_frame = ttk.Frame(export_options)
    type_frame.pack(fill="x", pady=5)
    
    ttk.Label(type_frame, text="Data Type:").pack(side="left", padx=5)
    export_type_var = tk.StringVar()
    export_type = ttk.Combobox(type_frame, textvariable=export_type_var, 
                              values=["Income", "Expenses"], 
                              state="readonly", width=15)
    export_type.pack(side="left", padx=5)
    
    ttk.Label(type_frame, text="Format:").pack(side="left", padx=5)
    format_var = tk.StringVar()
    format_combo = ttk.Combobox(type_frame, textvariable=format_var,
                               values=["CSV", "Excel", "PDF"],
                               state="readonly", width=15)
    format_combo.pack(side="left", padx=5)
    
    # Date Range Selection with Calendar
    date_frame = ttk.Frame(export_options)
    date_frame.pack(fill="x", pady=5)
    
    ttk.Label(date_frame, text="Start Date:").pack(side="left", padx=5)
    start_date_cal = DateEntry(date_frame, width=12, background='darkblue',
                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    start_date_cal.pack(side="left", padx=5)
    start_date_cal.delete(0, 'end')  # Clear the default date
    
    ttk.Label(date_frame, text="End Date:").pack(side="left", padx=5)
    end_date_cal = DateEntry(date_frame, width=12, background='darkblue',
                           foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    end_date_cal.pack(side="left", padx=5)
    end_date_cal.delete(0, 'end')  # Clear the default date
    
    # Export Button Frame
    button_frame = ttk.Frame(export_options)
    button_frame.pack(fill="x", pady=5)
    
    ttk.Button(button_frame, text="Export", command=export_data).pack(side="left", padx=5)
    
    # Import Section
    def import_data():
        # Check if data type is selected first
        data_type = import_type_var.get()
        if not data_type:
            messagebox.showerror("Error", "Please select a data type first")
            return
            
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if not file_path:
            return
            
        try:
            # Read the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Convert date column to datetime and then to string in YYYY-MM-DD format
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # Convert data to list of dictionaries
            records = df.to_dict('records')
            
            result = {'success': False, 'message': 'No data type selected'}
            
            if data_type == "Income":
                result = import_income_records(user_id, records)
            elif data_type == "Expenses":
                result = import_expense_records(user_id, records)
                
            if result['success']:
                messagebox.showinfo("Success", 
                    f"Import completed:\n"
                    f"Added: {result['added']}\n"
                    f"Updated: {result['updated']}\n"
                    f"Skipped: {result['skipped']}\n\n"
                    f"Please go to the Income Tracking tab to see your updated data."
                )
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {str(e)}")
    
    # Import Options
    import_options = ttk.Frame(import_frame)
    import_options.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(import_options, text="Data Type:").pack(side="left", padx=5)
    import_type_var = tk.StringVar()
    import_type = ttk.Combobox(import_options, textvariable=import_type_var,
                              values=["Income", "Expenses"],
                              state="readonly", width=15)
    import_type.pack(side="left", padx=5)
    
    def download_template():
        data_type = import_type_var.get()
        if not data_type:
            messagebox.showerror("Error", "Please select a data type first")
            return
            
        filetypes = [
            ("Excel files", "*.xlsx"),
            ("CSV files", "*.csv")
        ]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=filetypes,
            initialfile=f"{data_type.lower()}_template"
        )
        
        if filename:
            try:
                # Create template based on data type
                if data_type == "Income":
                    template_data = {
                        'date': ['YYYY-MM-DD'],
                        'amount': ['0.00'],
                        'description': ['Description here'],
                        'source': ['Source name']
                    }
                else:  # Expenses
                    template_data = {
                        'date': ['YYYY-MM-DD'],
                        'amount': ['0.00'],
                        'description': ['Description here'],
                        'category': ['Category name']
                    }
                
                df = pd.DataFrame(template_data)
                
                if filename.endswith('.xlsx'):
                    # Create Excel writer with formatting
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Template')
                        worksheet = writer.sheets['Template']
                        
                        # Format headers
                        for col in range(len(df.columns)):
                            cell = worksheet.cell(row=1, column=col+1)
                            cell.font = openpyxl.styles.Font(bold=True)
                            cell.fill = openpyxl.styles.PatternFill(
                                start_color='CCCCCC',
                                end_color='CCCCCC',
                                fill_type='solid'
                            )
                        
                        # Adjust column widths
                        for col in worksheet.columns:
                            max_length = 0
                            column = col[0].column_letter
                            for cell in col:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = (max_length + 2)
                            worksheet.column_dimensions[column].width = adjusted_width
                else:  # CSV
                    df.to_csv(filename, index=False)
                
                messagebox.showinfo("Success", "Template downloaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download template: {str(e)}")
    
    ttk.Button(import_options, text="Download Template", command=download_template).pack(side="left", padx=5)
    ttk.Button(import_options, text="Import", command=import_data).pack(side="left", padx=5)
    
    # Add help text
    help_frame = ttk.LabelFrame(tab_frame, text="Help", padding="10")
    help_frame.pack(fill="x", padx=10, pady=5)
    
    help_text = """
    Export Data:
    1. Select the type of data to export (Income or Expenses)
    2. Choose the export format (CSV, Excel, or PDF)
    3. Click 'Export' and choose where to save the file
    
    Import Data:
    1. Select the type of data to import
    2. Download the template using 'Download Template' button
    3. Fill in your data following the template format
    4. Click 'Import' and select your filled template file
    
    Note: For importing, your file must match the template format exactly.
    The date format should be YYYY-MM-DD (e.g., 2024-01-31)
    """
    
    ttk.Label(help_frame, text=help_text, justify="left").pack(padx=5, pady=5)
    
    notebook.add(tab_frame, text="Data Export and Import")
    return tab_frame