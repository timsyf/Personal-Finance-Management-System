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