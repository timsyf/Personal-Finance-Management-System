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

def add_transaction(description, amount, date, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO transactions (description, amount, date, user_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (description, amount, date, user_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

def get_all_transactions(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def update_transaction(transaction_id, description, amount, date, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # First verify this transaction belongs to the user
        verify_query = "SELECT id FROM transactions WHERE id = %s AND user_id = %s"
        cursor.execute(verify_query, (transaction_id, user_id))
        if not cursor.fetchone():
            print("Transaction not found or doesn't belong to user")
            return

        query = "UPDATE transactions SET description = %s, amount = %s, date = %s WHERE id = %s AND user_id = %s"
        cursor.execute(query, (description, amount, date, transaction_id, user_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

def delete_transaction(transaction_id, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # First verify this transaction belongs to the user
        verify_query = "SELECT id FROM transactions WHERE id = %s AND user_id = %s"
        cursor.execute(verify_query, (transaction_id, user_id))
        if not cursor.fetchone():
            print("Transaction not found or doesn't belong to user")
            return

        query = "DELETE FROM transactions WHERE id = %s AND user_id = %s"
        cursor.execute(query, (transaction_id, user_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()