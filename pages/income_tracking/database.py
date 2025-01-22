import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ..auth.database import get_db_connection

load_dotenv()

def get_all_transactions():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM transactions"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def add_income(user_id, amount, description, date, source_id):
    """Add a new income record"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Debug print
        print(f"Adding income with source_id: {source_id}")
        
        query = """
            INSERT INTO income_tracker (user_id, amount, description, date, source_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, amount, description, date, source_id))
        
        # Debug print
        print(f"Rows affected: {cursor.rowcount}")
        
        connection.commit()
        return True, "Income added successfully"
    except mysql.connector.Error as err:
        print(f"Error adding income: {err}")
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def get_income(user_id, start_date=None, end_date=None):
    """Get all income records for a user within date range"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT i.id, i.amount, i.description, i.date, s.name as source_name, s.id as source_id
            FROM income_tracker i
            JOIN income_sources s ON i.source_id = s.id
            WHERE i.user_id = %s
        """
        params = [user_id]
        
        if start_date and end_date:
            query += " AND i.date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        query += " ORDER BY i.date DESC"
        
        # Debug print
        print(f"Executing query: {query}")
        print(f"With params: {params}")
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Debug print
        print(f"Query results: {results}")
        
        return results
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def update_income(income_id, user_id, amount, description, date, source_id):
    """Update an income record"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            UPDATE income_tracker
            SET amount = %s, description = %s, date = %s, source_id = %s
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(query, (amount, description, date, source_id, income_id, user_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            return True, "Income updated successfully"
        return False, "Income record not found or unauthorized"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def delete_income(income_id, user_id):
    """Delete an income record"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            DELETE FROM income_tracker
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(query, (income_id, user_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            return True, "Income deleted successfully"
        return False, "Income record not found or unauthorized"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def get_monthly_income(user_id, month, year):
    """Get monthly income summary"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT SUM(i.amount) as total_income, 
                   COUNT(*) as transaction_count,
                   s.name as source_name,
                   DATE_FORMAT(i.date, '%Y-%m') as month
            FROM income_tracker i
            JOIN income_sources s ON i.source_id = s.id
            WHERE i.user_id = %s 
            AND MONTH(i.date) = %s
            AND YEAR(i.date) = %s
            GROUP BY s.name, DATE_FORMAT(i.date, '%Y-%m')
        """
        cursor.execute(query, (user_id, month, year))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_income_by_source(user_id, source_id, start_date=None, end_date=None):
    """Get income records filtered by source"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT i.id, i.amount, i.description, i.date, s.name as source_name
            FROM income_tracker i
            JOIN income_sources s ON i.source_id = s.id
            WHERE i.user_id = %s AND i.source_id = %s
        """
        params = [user_id, source_id]
        
        if start_date and end_date:
            query += " AND i.date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        query += " ORDER BY i.date DESC"
        cursor.execute(query, params)
        
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_total_income(user_id, start_date=None, end_date=None):
    """Get total income for a period"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT SUM(amount) as total
            FROM income_tracker
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date and end_date:
            query += " AND date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result[0] else 0
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return 0
    finally:
        cursor.close()
        connection.close()

def get_income_sources(user_id):
    """Get all income sources for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT id, name, description
            FROM income_sources
            WHERE user_id = %s
            ORDER BY name
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def add_income_source(user_id, name, description=""):
    """Add a new income source"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO income_sources (name, description, user_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (name, description, user_id))
        connection.commit()
        return True, "Income source added successfully"
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error
            return False, "This source name already exists"
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def update_income_source(source_id, user_id, name, description=""):
    """Update an existing income source"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            UPDATE income_sources
            SET name = %s, description = %s
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(query, (name, description, source_id, user_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            return True, "Income source updated successfully"
        return False, "Income source not found or unauthorized"
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error
            return False, "This source name already exists"
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def delete_income_source(source_id, user_id):
    """Delete an income source"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if source is in use
        cursor.execute("""
            SELECT COUNT(*) FROM income_tracker 
            WHERE source_id = %s
        """, (source_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return False, "Cannot delete source that is in use by income records"
        
        query = """
            DELETE FROM income_sources
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(query, (source_id, user_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            return True, "Income source deleted successfully"
        return False, "Income source not found or unauthorized"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def add_recurring_income(user_id, amount, description, source_id, frequency, start_date, end_date=None):
    """Add a recurring income schedule and immediately create past records if start_date is in the past"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        print(f"Adding recurring income: {description}, Amount: {amount}, Frequency: {frequency}")
        print(f"Start Date: {start_date}, End Date: {end_date}")
        
        current_date = datetime.now().date()
        
        # Add to recurring_income table with next_date
        # If start_date is in the past, set next_date to tomorrow to avoid duplicate entries
        next_date = max(start_date, current_date + timedelta(days=1))
        
        query = """
            INSERT INTO recurring_income 
            (user_id, amount, description, source_id, frequency, start_date, end_date, next_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, amount, description, source_id, frequency, 
                             start_date, end_date, next_date))
        recurring_id = cursor.lastrowid
        print(f"Created recurring income record with ID: {recurring_id}")
        
        # If start_date is in the past, create all past records immediately
        if start_date < current_date:
            current = start_date
            while current <= current_date:
                # Skip if we've passed the end date
                if end_date and current > end_date:
                    break
                    
                # Add income record for this date
                add_query = """
                    INSERT INTO income_tracker 
                    (user_id, amount, description, date, source_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(add_query, (
                    user_id, amount, description, current, source_id
                ))
                
                # Move to next date based on frequency
                if frequency == "Daily":
                    current = current + timedelta(days=1)
                elif frequency == "Monthly":
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
                elif frequency == "Bi-monthly":
                    if current.month >= 11:
                        current = current.replace(year=current.year + 1, month=(current.month + 2) % 12)
                    else:
                        current = current.replace(month=current.month + 2)
                elif frequency == "Quarterly":
                    if current.month > 9:
                        current = current.replace(year=current.year + 1, month=(current.month + 3) % 12)
                    else:
                        current = current.replace(month=current.month + 3)
                elif frequency == "Semi-annually":
                    if current.month > 6:
                        current = current.replace(year=current.year + 1, month=(current.month + 6) % 12)
                    else:
                        current = current.replace(month=current.month + 6)
                elif frequency == "Annually":
                    current = current.replace(year=current.year + 1)
        
        connection.commit()
        return True, "Recurring income schedule added successfully"
    except mysql.connector.Error as err:
        print(f"Error in add_recurring_income: {err}")
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def process_recurring_income():
    """Process all recurring income schedules and create transactions for due dates"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get current date
        current_date = datetime.now().date()
        
        # Get all recurring incomes that are due
        query = """
            SELECT id, user_id, amount, description, source_id, frequency, 
                   start_date, end_date, next_date
            FROM recurring_income
            WHERE next_date <= %s
            AND (end_date IS NULL OR end_date >= %s)
        """
        cursor.execute(query, (current_date, current_date))
        due_incomes = cursor.fetchall()
        
        for income in due_incomes:
            # Add the income record
            add_query = """
                INSERT INTO income_tracker 
                (user_id, amount, description, date, source_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(add_query, (
                income['user_id'], 
                income['amount'], 
                income['description'], 
                income['next_date'],
                income['source_id']
            ))
            
            # Calculate next date based on frequency
            next_date = income['next_date']
            if income['frequency'] == "Daily":
                next_date = next_date + timedelta(days=1)
            elif income['frequency'] == "Monthly":
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
            elif income['frequency'] == "Bi-monthly":
                if next_date.month >= 11:
                    next_date = next_date.replace(year=next_date.year + 1, month=(next_date.month + 2) % 12)
                else:
                    next_date = next_date.replace(month=next_date.month + 2)
            elif income['frequency'] == "Quarterly":
                if next_date.month > 9:
                    next_date = next_date.replace(year=next_date.year + 1, month=(next_date.month + 3) % 12)
                else:
                    next_date = next_date.replace(month=next_date.month + 3)
            elif income['frequency'] == "Semi-annually":
                if next_date.month > 6:
                    next_date = next_date.replace(year=next_date.year + 1, month=(next_date.month + 6) % 12)
                else:
                    next_date = next_date.replace(month=next_date.month + 6)
            elif income['frequency'] == "Annually":
                next_date = next_date.replace(year=next_date.year + 1)
            
            # Update next_date in recurring_income
            update_query = """
                UPDATE recurring_income
                SET next_date = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (next_date, income['id']))
        
        connection.commit()
        return True, f"Processed {len(due_incomes)} recurring incomes"
    except mysql.connector.Error as err:
        print(f"Error processing recurring income: {err}")
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def update_recurring_income(recurring_id, user_id, amount, description, source_id, 
                          frequency, start_date, end_date=None):
    """Update a recurring income schedule without affecting past records"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        print(f"Updating recurring income {recurring_id}")
        print(f"New values - Amount: {amount}, Description: {description}, Frequency: {frequency}")
        print(f"Start Date: {start_date}, End Date: {end_date}")
        
        # Get current date
        current_date = datetime.now().date()
        
        # Update the recurring income record, but only set next_date to start_date
        # if the current next_date hasn't occurred yet
        query = """
            UPDATE recurring_income
            SET amount = %s, 
                description = %s, 
                source_id = %s, 
                frequency = %s, 
                start_date = %s, 
                end_date = %s,
                next_date = CASE 
                    WHEN next_date >= %s THEN %s 
                    ELSE next_date 
                END
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(query, (
            amount, description, source_id, frequency, 
            start_date, end_date, current_date, start_date,
            recurring_id, user_id
        ))
        
        if cursor.rowcount > 0:
            print("Recurring income record updated successfully")
            connection.commit()
            return True, "Recurring income updated successfully"
        return False, "Recurring income not found or unauthorized"
    except mysql.connector.Error as err:
        print(f"Error in update_recurring_income: {err}")
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def delete_recurring_income(recurring_id, user_id):
    """Delete a recurring income schedule without affecting past records"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Simply delete the recurring schedule
        # Past records in income_tracker will remain unchanged
        cursor.execute("""
            DELETE FROM recurring_income
            WHERE id = %s AND user_id = %s
        """, (recurring_id, user_id))
        
        if cursor.rowcount > 0:
            connection.commit()
            return True, "Recurring income schedule deleted successfully"
        return False, "Recurring income not found or unauthorized"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def get_income_date_range(user_id):
    """Get the earliest and latest dates from income records"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT MIN(date) as earliest_date, MAX(date) as latest_date
            FROM income_tracker
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        # If no records exist, return today's date for both
        if not result or not result['earliest_date']:
            today = datetime.now().date()
            return today, today
            
        return result['earliest_date'], result['latest_date']
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        today = datetime.now().date()
        return today, today
    finally:
        cursor.close()
        connection.close()

def get_recurring_income(user_id):
    """Get all recurring income records for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT r.id, r.amount, r.description, s.name as source_name, s.id as source_id,
                   r.frequency, r.start_date, r.end_date, r.next_date
            FROM recurring_income r
            JOIN income_sources s ON r.source_id = s.id
            WHERE r.user_id = %s
            ORDER BY r.next_date
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error in get_recurring_income: {err}")
        return []
    finally:
        cursor.close()
        connection.close()