import mysql.connector
import os
from datetime import datetime, date
from dotenv import load_dotenv
import hashlib

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_monthly_summary(user_id):
    """Get total income and expenses for the current month"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get current month's first and last day
        today = date.today()
        first_day = date(today.year, today.month, 1)
        
        # Get monthly income
        income_query = """
            SELECT COALESCE(SUM(amount), 0) as total_income 
            FROM income_tracker 
            WHERE user_id = %s AND date >= %s AND date <= %s
        """
        cursor.execute(income_query, (user_id, first_day, today))
        monthly_income = cursor.fetchone()['total_income']
        
        # Get monthly expenses
        expense_query = """
            SELECT COALESCE(SUM(amount), 0) as total_expenses 
            FROM expenses_tracker 
            WHERE user_id = %s AND date >= %s AND date <= %s
        """
        cursor.execute(expense_query, (user_id, first_day, today))
        monthly_expenses = cursor.fetchone()['total_expenses']
        
        return {
            'income': float(monthly_income),
            'expenses': float(monthly_expenses),
            'net': float(monthly_income - monthly_expenses)
        }
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {'income': 0, 'expenses': 0, 'net': 0}
    finally:
        cursor.close()
        connection.close()

def get_budget_status(user_id):
    """Get count of categories within and exceeding budget"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get current month's first and last day
        today = date.today()
        first_day = date(today.year, today.month, 1)
        
        # Get monthly budgets and actual expenses
        query = """
            SELECT b.category, b.amount as budget,
                   COALESCE(SUM(e.amount), 0) as spent
            FROM budgets b
            LEFT JOIN expenses_tracker e ON b.category = e.category 
                AND e.user_id = b.user_id 
                AND e.date >= %s AND e.date <= %s
            WHERE b.user_id = %s AND b.frequency = 'Monthly'
            GROUP BY b.category, b.amount
        """
        cursor.execute(query, (first_day, today, user_id))
        results = cursor.fetchall()
        
        within_budget = 0
        exceeding_budget = 0
        for result in results:
            if float(result['spent']) <= float(result['budget']):
                within_budget += 1
            else:
                exceeding_budget += 1
                
        return {
            'within_budget': within_budget,
            'exceeding_budget': exceeding_budget
        }
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {'within_budget': 0, 'exceeding_budget': 0}
    finally:
        cursor.close()
        connection.close()

def get_upcoming_transactions(user_id):
    """Get count of upcoming recurring transactions"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        today = date.today()
        
        # Get upcoming recurring income count
        income_query = """
            SELECT COUNT(*) as count 
            FROM recurring_income 
            WHERE user_id = %s AND next_date >= %s
        """
        cursor.execute(income_query, (user_id, today))
        recurring_income = cursor.fetchone()['count']
        
        # Get upcoming recurring expenses count
        expense_query = """
            SELECT COUNT(*) as count 
            FROM recurring_transactions 
            WHERE user_id = %s AND next_date >= %s
        """
        cursor.execute(expense_query, (user_id, today))
        recurring_expenses = cursor.fetchone()['count']
        
        return {
            'recurring_income': recurring_income,
            'recurring_expenses': recurring_expenses
        }
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {'recurring_income': 0, 'recurring_expenses': 0}
    finally:
        cursor.close()
        connection.close()

def get_user_info(user_id):
    """Get user's profile information"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT username, email 
            FROM users 
            WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

def update_user_profile(user_id, username=None, email=None):
    """Update user's profile information"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if username:
            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        if email:
            cursor.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
            
        connection.commit()
        return True, "Profile updated successfully"
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error
            return False, "Username or email already exists"
        return False, f"Error updating profile: {err}"
    finally:
        cursor.close()
        connection.close()

def change_password(user_id, current_password, new_password):
    """Change user's password"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Hash passwords using SHA-256
        hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
        hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
        
        # First verify current password
        verify_query = """
            SELECT password 
            FROM users 
            WHERE id = %s
        """
        cursor.execute(verify_query, (user_id,))
        result = cursor.fetchone()
        
        if not result or result[0] != hashed_current:
            return False, "Current password is incorrect"
        
        # Update to new password
        update_query = """
            UPDATE users 
            SET password = %s 
            WHERE id = %s
        """
        cursor.execute(update_query, (hashed_new, user_id))
        connection.commit()
        
        return True, "Password updated successfully"
    except mysql.connector.Error as err:
        return False, f"Error changing password: {err}"
    finally:
        cursor.close()
        connection.close()


