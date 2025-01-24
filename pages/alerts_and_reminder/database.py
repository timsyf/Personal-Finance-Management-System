import mysql.connector
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox

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

def log_alert(user_id, budget_id, category, alert_message):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO alerts (user_id, budget_id, category, alert_message)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user_id, budget_id, category, alert_message))
                connection.commit()
                messagebox.showwarning("Budget Alert", alert_message)
    except mysql.connector.Error as err:
        print(f"Error logging alert: {err}")



def check_budget_exceeded(user_id):
    try:
        # Step 1: Fetch all budgets
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT b.id AS budget_id, b.category, b.amount AS budget_limit, b.frequency,
                           COALESCE(SUM(e.amount), 0) AS total_expense
                    FROM budgets b
                    LEFT JOIN expenses_tracker e
                    ON b.category = e.category AND b.user_id = e.user_id
                    WHERE b.user_id = %s
                    AND (
                        (b.frequency = 'Monthly' AND (e.date IS NULL OR MONTH(e.date) = MONTH(CURRENT_DATE())))
                        OR (b.frequency = 'Yearly' AND (e.date IS NULL OR YEAR(e.date) = YEAR(CURRENT_DATE())))
                    )
                    GROUP BY b.id
                """
                cursor.execute(query, (user_id,))
                budgets = cursor.fetchall()  # Fetch all budgets into memory
                print("Budgets fetched:", budgets)

        # Step 2: Process each budget using a new connection
        for budget in budgets:
            with get_db_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # Check if an alert already exists
                    check_alert_query = """
                        SELECT id
                        FROM alerts
                        WHERE user_id = %s AND budget_id = %s
                    """
                    cursor.execute(check_alert_query, (user_id, budget['budget_id']))
                    existing_alert = cursor.fetchone()

                    if existing_alert:
                        print(f"Alert already exists for budget ID {budget['budget_id']}. Skipping...")
                        continue

                    # Log a new alert if the budget is exceeded
                    if budget['total_expense'] > budget['budget_limit']:
                        alert_message = (
                            f"Budget exceeded for category '{budget['category']}' "
                            f"({budget['frequency']} budget). "
                            f"Limit: {budget['budget_limit']}, Spent: {budget['total_expense']}"
                        )
                        log_alert(user_id, budget['budget_id'], budget['category'], alert_message)

    except mysql.connector.Error as err:
        print(f"Error checking budget: {err}")




def fetch_alerts(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT alert_message, created_at FROM alerts WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching alerts: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
