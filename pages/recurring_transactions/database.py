import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_all_recurring_transactions():

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

def insert_recurring_transaction(name, amount, recurrence, start_date, end_date, category, user_id):
    """
    Insert a new recurring transaction into the database and populate expenses_tracker.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert recurring transaction
        query = """
        INSERT INTO recurring_transactions (name, amount, recurrence, start_date, end_date, category, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, amount, recurrence, start_date, end_date, category, user_id))
        connection.commit()

        # Call function to populate expenses_tracker
        insert_recurring_to_tracker(user_id, name, amount, category, start_date, end_date, recurrence)

        print("Recurring transaction and expenses tracker records added successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def delete_recurring_transaction(recurring_id):

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

def insert_recurring_to_tracker(user_id, name, amount, category, start_date, end_date, recurrence):
    """
    Inserts recurring expense records into the expenses_tracker table based on the recurrence type.
    """
    try:
        # Parse dates from MM/DD/YYYY and convert to datetime objects
        current_date = datetime.strptime(start_date, "%m/%d/%Y")
        end_date = datetime.strptime(end_date, "%m/%d/%Y")

        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Loop through the dates based on recurrence type
        while current_date <= end_date:
            # Convert date to YYYY-MM-DD format for database
            formatted_date = current_date.strftime("%Y-%m-%d")

            # Insert the current record into expenses_tracker
            query = """
                INSERT INTO expenses_tracker (description, amount, category, date, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, amount, category, formatted_date, user_id))

            # Move to the next date based on the recurrence
            if recurrence == "Daily":
                current_date += timedelta(days=1)
            elif recurrence == "Monthly":
                next_month = current_date.month + 1 if current_date.month < 12 else 1
                next_year = current_date.year + (1 if next_month == 1 else 0)
                current_date = current_date.replace(year=next_year, month=next_month)
            elif recurrence == "Yearly":
                current_date = current_date.replace(year=current_date.year + 1)

        # Commit the transaction
        connection.commit()
        print(f"Inserted records into expenses_tracker for {recurrence} recurrence.")

    except Exception as e:
        print(f"Error inserting recurring expenses into tracker: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


