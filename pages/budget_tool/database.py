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

def insert_budget(user_id, category, amount, frequency):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO budgets (user_id, category, amount, frequency)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, category, amount, frequency))
        connection.commit()
    except Exception as e:
        raise Exception(f"Error adding budget: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_budgets(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT category, amount, frequency
            FROM budgets
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise Exception(f"Error fetching budgets: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_expense_stats_by_category(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                category, 
                SUM(amount) AS total
            FROM expenses_tracker
            WHERE user_id = %s
            GROUP BY category
        """
        cursor.execute(query, (user_id,))
        stats = cursor.fetchall()
        return {item['category']: {'total': item['total']} for item in stats}
    except Exception as e:
        raise Exception(f"Error fetching expense stats: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_total_expenses(user_id):
    """
    Fetch the total amount of expenses for a user regardless of category.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            SELECT SUM(amount) AS total_expenses
            FROM expenses_tracker
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0.0
    except Exception as e:
        raise Exception(f"Error fetching total expenses: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_budget(user_id, category=None):
    """
    Deletes a budget for a user. If no category is specified, delete the overall budget.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Determine the query based on whether a category is provided
        if category:
            query = """
                DELETE FROM budgets
                WHERE user_id = %s AND category = %s
            """
            cursor.execute(query, (user_id, category))
        else:
            query = """
                DELETE FROM budgets
                WHERE user_id = %s AND category IS NULL
            """
            cursor.execute(query, (user_id,))

        connection.commit()
        print(f"Budget for {'category: ' + category if category else 'overall'} deleted successfully.")
    except Exception as e:
        raise Exception(f"Error deleting budget: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def load_progress():
    """Reloads both monthly and yearly progress, including the Overall category."""
    monthly_table.delete(*monthly_table.get_children())
    yearly_table.delete(*yearly_table.get_children())
    try:
        budgets = get_budgets(user_id)
        all_expenses = get_expenses_tracker(user_id)

        # monthly Progress
        monthly_stats = filter_expense_stats(all_expenses, is_current_month)
        total_monthly_budget = 0
        total_monthly_spent = 0

        for budget in budgets:
            if budget["frequency"] != "Monthly":
                continue

            category = budget["category"] or "All"
            spent = monthly_stats.get(category, {}).get("total", 0)
            remaining = budget["amount"] - spent
            status = "Within Budget" if remaining >= 0 else "Exceeding Budget"

            monthly_table.insert("", "end", values=(category, budget["amount"], spent, remaining, status))
            total_monthly_budget += budget["amount"]
            total_monthly_spent += spent

        # add overall row for monthly
        monthly_table.insert(
            "", "end",
            values=("Overall", total_monthly_budget, total_monthly_spent, total_monthly_budget - total_monthly_spent,
                    "Within Budget" if total_monthly_budget - total_monthly_spent >= 0 else "Exceeding Budget"),
        )

        # yearly Progress
        yearly_stats = filter_expense_stats(all_expenses, is_current_year)
        total_yearly_budget = 0
        total_yearly_spent = 0

        for budget in budgets:
            if budget["frequency"] != "Yearly":
                continue

            category = budget["category"] or "All"
            spent = yearly_stats.get(category, {}).get("total", 0)
            remaining = budget["amount"] - spent
            status = "Within Budget" if remaining >= 0 else "Exceeding Budget"

            yearly_table.insert("", "end", values=(category, budget["amount"], spent, remaining, status))
            total_yearly_budget += budget["amount"]
            total_yearly_spent += spent

        # add overall row for yearly
        yearly_table.insert(
            "", "end",
            values=("Overall", total_yearly_budget, total_yearly_spent, total_yearly_budget - total_yearly_spent,
                    "Within Budget" if total_yearly_budget - total_yearly_spent >= 0 else "Exceeding Budget"),
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load progress: {e}")

