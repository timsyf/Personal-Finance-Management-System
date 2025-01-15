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

def add_transaction(description, amount, date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO transactions (description, amount, date) VALUES (%s, %s, %s)"
        cursor.execute(query, (description, amount, date))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

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

def update_transaction(transaction_id, description, amount, date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "UPDATE transactions SET description = %s, amount = %s, date = %s WHERE id = %s"
        cursor.execute(query, (description, amount, date, transaction_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

def delete_transaction(transaction_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "DELETE FROM transactions WHERE id = %s"
        cursor.execute(query, (transaction_id,))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()