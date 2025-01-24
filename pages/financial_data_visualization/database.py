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

def get_total_expenses_by_category(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses_tracker
            WHERE user_id = %s
            GROUP BY category
            ORDER BY total_amount DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_income_by_source(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT i.name, SUM(t.amount) AS total_income
            FROM income_tracker t
            JOIN income_sources i ON t.source_id = i.id
            WHERE t.user_id = %s
            GROUP BY i.name
            ORDER BY total_income DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_recurring_transactions_by_category(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT category, COUNT(*) AS total_count, SUM(amount) AS total_amount
            FROM recurring_transactions
            WHERE user_id = %s
            GROUP BY category
            ORDER BY total_amount DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_budget_utilization(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT b.category, b.amount AS budgeted_amount, 
                COALESCE(SUM(e.amount), 0) AS spent_amount, 
                b.amount - COALESCE(SUM(e.amount), 0) AS remaining_amount
            FROM budgets b
            LEFT JOIN expenses_tracker e 
            ON b.category = e.category AND b.user_id = e.user_id
            WHERE b.user_id = %s
            GROUP BY b.category, b.amount
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_top_expense_categories(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses_tracker
            WHERE user_id = %s
            GROUP BY category
            ORDER BY total_amount DESC
            LIMIT 5
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_top_expense_categories(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses_tracker
            WHERE user_id = %s
            GROUP BY category
            ORDER BY total_amount DESC
            LIMIT 5
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_daily_expense_trends(user_id, start_date, end_date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT date, SUM(amount) AS total_amount
            FROM expenses_tracker
            WHERE user_id = %s AND date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date ASC
        """
        cursor.execute(query, (user_id, start_date, end_date))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_income_vs_expenses(user_id, start_date, end_date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                (SELECT SUM(amount) FROM income_tracker WHERE user_id = %s AND date BETWEEN %s AND %s) AS total_income,
                (SELECT SUM(amount) FROM expenses_tracker WHERE user_id = %s AND date BETWEEN %s AND %s) AS total_expenses
        """
        cursor.execute(query, (user_id, start_date, end_date, user_id, start_date, end_date))
        row = cursor.fetchone()
        return row
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_income_breakdown_by_year(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT YEAR(date) AS year, i.name AS source, SUM(t.amount) AS total_income
            FROM income_tracker t
            JOIN income_sources i ON t.source_id = i.id
            WHERE t.user_id = %s
            GROUP BY year, i.name
            ORDER BY year ASC, total_income DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()






