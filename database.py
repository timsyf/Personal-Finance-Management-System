import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def add_transaction(description, amount, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (description, amount, date) VALUES (%s, %s, %s)", (description, amount, date))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_transaction(transaction_id, new_description, new_amount, new_date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET description=%s, amount=%s, date=%s WHERE id=%s", 
                   (new_description, new_amount, new_date, transaction_id))
    conn.commit()
    conn.close()

def delete_transaction(transaction_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=%s", (transaction_id,))
    conn.commit()
    conn.close()