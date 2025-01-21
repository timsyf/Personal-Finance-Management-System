import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Establish a connection to the MySQL database.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_all_recurring_transactions():
    """
    Fetch all recurring transactions from the database.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Use dictionary=True to return results as dicts

        query = "SELECT * FROM recurring_transactions"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_recurring_transaction(name, amount, recurrence, start_date):
    """
    Insert a new recurring transaction into the database.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO recurring_transactions (name, amount, recurrence, start_date)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, amount, recurrence, start_date))
        connection.commit()
        print("Transaction added successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_recurring_transaction(recurring_id):
    """
    Delete a recurring transaction by its ID.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "DELETE FROM recurring_transactions WHERE recurring_id = %s"
        cursor.execute(query, (recurring_id,))
        connection.commit()
        print(f"Recurring transaction with ID {recurring_id} deleted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
