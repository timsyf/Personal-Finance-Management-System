import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_income_tracker(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM income_tracker WHERE user_id = %s ORDER BY date DESC"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_expenses_tracker(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM expenses_tracker WHERE user_id = %s ORDER BY date DESC"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_income_sources(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM income_sources WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_recurring_income(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM recurring_income WHERE user_id = %s ORDER BY next_date ASC"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_recurring_transactions(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM recurring_transactions WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_expenses_category(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM expenses_category WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def add_expense(user_id, amount, category, description):
    """Insert a new expense record into the expenses_tracker table."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO expenses_tracker (user_id, amount, category, description, date)
            VALUES (%s, %s, %s, %s, CURDATE())
        """
        cursor.execute(query, (user_id, amount, category, description))
        connection.commit()

        return True  # Indicate success
    except mysql.connector.Error as err:
        print(f"Error inserting expense: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_fixed_queries(user_id):
    """Fetch all fixed queries for the logged-in user."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT id, query_text FROM fixed_queries WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def add_fixed_query(user_id, query_text):
    """Add a new fixed query for the logged-in user."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO fixed_queries (user_id, query_text) VALUES (%s, %s)"
        cursor.execute(query, (user_id, query_text))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

def delete_fixed_query(query_id, user_id):
    """Delete a fixed query by its ID (only if it belongs to the logged-in user)."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "DELETE FROM fixed_queries WHERE id = %s AND user_id = %s"
        cursor.execute(query, (query_id, user_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()