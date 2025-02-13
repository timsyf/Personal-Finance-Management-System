import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, date
from pages.alerts_and_reminder.database import check_budget_exceeded

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Function to add daily expense
def add_expenses_tracker(description, amount, category, date, user_id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO expenses_tracker (description, amount, category, date, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (description, amount, category, date, user_id))
                connection.commit()

        # Use a new connection for checking budget exceedance
        check_budget_exceeded(user_id)

    except Exception as e:
        raise Exception(f"Error saving expense: {e}")


# Function to fetch all daily expenses for a user
def get_expenses_tracker(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT id, description, amount, category, date
            FROM expenses_tracker
            WHERE user_id = %s
            ORDER BY date DESC
        """
        cursor.execute(query, (user_id,))
        expenses = cursor.fetchall()
        cursor.close()
        return expenses
    except Exception as e:
        raise Exception(f"Error fetching expenses: {e}")
    
# Function to fetch filtered daily expenses for a user with various filters
def get_filtered_expenses(user_id, start_date=None, end_date=None, category=None, min_amount=None, max_amount=None, description=None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT id, description, amount, category, date
            FROM expenses_tracker
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        if category:
            query += " AND category = %s"
            params.append(category)
        if min_amount:
            query += " AND amount >= %s"
            params.append(min_amount)
        if max_amount:
            query += " AND amount <= %s"
            params.append(max_amount)
        if description:
            query += " AND description LIKE %s"
            params.append(f"%{description}%")
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, tuple(params))
        expenses = cursor.fetchall()
        cursor.close()
        return expenses
    except Exception as e:
        raise Exception(f"Error fetching filtered expenses: {e}")

# Function to get all expense categories for a specific user
def get_expenses_categories(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT name
            FROM expenses_category
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        categories = cursor.fetchall()
        cursor.close()
        
        category_names = [category["name"] for category in categories]
        return category_names
    except Exception as e:
        raise Exception(f"Error fetching expense categories: {e}")

# Function to add a new expense category for a specific user
def add_expense_category(name, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO expenses_category (name, user_id)
            VALUES (%s, %s)
        """
        cursor.execute(query, (name, user_id))
        connection.commit()
        cursor.close()
    except Exception as e:
        raise Exception(f"Error adding expense category: {e}")

# Function to delete an expense by ID
def delete_expense_by_id(expense_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            DELETE FROM expenses_tracker
            WHERE id = %s
        """
        cursor.execute(query, (expense_id,))
        connection.commit()
        cursor.close()
    except Exception as e:
        raise Exception(f"Error deleting expense: {e}")

# Function to update an expense by ID
def update_expense_by_id(expense_id, description, amount, category, date, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            UPDATE expenses_tracker
            SET description = %s, amount = %s, category = %s, date = %s
            WHERE id = %s
        """
        cursor.execute(query, (description, amount, category, date, expense_id))
        connection.commit()
        cursor.close()

        check_budget_exceeded(user_id)
    except Exception as e:
        raise Exception(f"Error updating expense: {e}")
    finally:
        if connection:
            connection.close()

# Function to delete an expense category by name
def delete_expense_category_by_name(name, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            DELETE FROM expenses_category
            WHERE name = %s AND user_id = %s
        """
        cursor.execute(query, (name, user_id))
        connection.commit()
        cursor.close()
    except Exception as e:
        raise Exception(f"Error deleting expense category: {e}")


def get_expense_stats_by_category(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                category, 
                COUNT(*) as count, 
                SUM(amount) as total, 
                MIN(amount) as min, 
                MAX(amount) as max, 
                AVG(amount) as avg
            FROM expenses_tracker
            WHERE user_id = %s
            GROUP BY category
        """
        cursor.execute(query, (user_id,))
        stats = cursor.fetchall()
        cursor.close()
        return {item['category']: {
            'count': item['count'],
            'total': item['total'],
            'min': item['min'],
            'max': item['max'],
            'avg': item['avg']
        } for item in stats}
    except Exception as e:
        raise Exception(f"Error fetching expense stats: {e}")




# Delete all expenses linked to the category
def delete_category_and_expenses(category_name, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        
        cursor.execute("""
            DELETE FROM expenses_tracker WHERE category = %s AND user_id = %s
        """, (category_name, user_id))

        cursor.execute("""
            DELETE FROM expenses_category WHERE name = %s AND user_id = %s
        """, (category_name, user_id))

        connection.commit()
        cursor.close()
    except Exception as e:
        raise Exception(f"Error deleting category and its linked expenses: {e}")