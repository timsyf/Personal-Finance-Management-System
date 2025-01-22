import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

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

def get_income_records(user_id, start_date=None, end_date=None):
    """Get all income records for a user within date range"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT i.id, i.amount, i.description, i.date, s.name as source
            FROM income_tracker i
            JOIN income_sources s ON i.source_id = s.id
            WHERE i.user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND i.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND i.date <= %s"
            params.append(end_date)
            
        query += " ORDER BY i.date DESC"
        
        cursor.execute(query, tuple(params))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching income records: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_expense_records(user_id, start_date=None, end_date=None):
    """Get all expense records for a user within date range"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT id, description, amount, category, date
            FROM expenses_tracker
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
            
        query += " ORDER BY date DESC"
        
        cursor.execute(query, tuple(params))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching expense records: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_budget_data(user_id):
    """Get budget data for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get expense categories and their budgets
        query = """
            SELECT ec.name as category, et.amount as spent,
                   COUNT(et.id) as transaction_count
            FROM expenses_category ec
            LEFT JOIN expenses_tracker et 
                ON ec.name = et.category 
                AND et.user_id = ec.user_id
                AND MONTH(et.date) = MONTH(CURRENT_DATE())
                AND YEAR(et.date) = YEAR(CURRENT_DATE())
            WHERE ec.user_id = %s
            GROUP BY ec.name
        """
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching budget data: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def import_income_records(user_id, data):
    """Import income records for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        added = 0
        updated = 0
        skipped = 0
        
        for record in data:
            try:
                # Get source_id from source name
                cursor.execute(
                    "SELECT id FROM income_sources WHERE name = %s AND user_id = %s",
                    (record['source'], user_id)
                )
                source_result = cursor.fetchone()
                
                if not source_result:
                    # Create new source if it doesn't exist
                    cursor.execute(
                        "INSERT INTO income_sources (name, user_id) VALUES (%s, %s)",
                        (record['source'], user_id)
                    )
                    source_id = cursor.lastrowid
                else:
                    source_id = source_result[0]
                
                # Check if record already exists
                cursor.execute(
                    """SELECT id FROM income_tracker 
                       WHERE user_id = %s AND date = %s AND amount = %s AND description = %s""",
                    (user_id, record['date'], record['amount'], record['description'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute(
                        """UPDATE income_tracker 
                           SET source_id = %s
                           WHERE id = %s""",
                        (source_id, existing[0])
                    )
                    updated += 1
                else:
                    # Insert new record
                    cursor.execute(
                        """INSERT INTO income_tracker 
                           (user_id, amount, description, date, source_id)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (user_id, record['amount'], record['description'], 
                         record['date'], source_id)
                    )
                    added += 1
                    
            except Exception as e:
                print(f"Error processing record: {e}")
                skipped += 1
                
        connection.commit()
        return {
            'success': True,
            'added': added,
            'updated': updated,
            'skipped': skipped
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        cursor.close()
        connection.close()

def import_expense_records(user_id, data):
    """Import expense records for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        added = 0
        updated = 0
        skipped = 0
        
        for record in data:
            try:
                # Check if category exists
                cursor.execute(
                    "SELECT name FROM expenses_category WHERE name = %s AND user_id = %s",
                    (record['category'], user_id)
                )
                if not cursor.fetchone():
                    # Create new category
                    cursor.execute(
                        "INSERT INTO expenses_category (name, user_id) VALUES (%s, %s)",
                        (record['category'], user_id)
                    )
                
                # Check if record already exists
                cursor.execute(
                    """SELECT id FROM expenses_tracker 
                       WHERE user_id = %s AND date = %s AND amount = %s 
                       AND description = %s AND category = %s""",
                    (user_id, record['date'], record['amount'], 
                     record['description'], record['category'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    updated += 1
                else:
                    # Insert new record
                    cursor.execute(
                        """INSERT INTO expenses_tracker 
                           (user_id, description, amount, category, date)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (user_id, record['description'], record['amount'],
                         record['category'], record['date'])
                    )
                    added += 1
                    
            except Exception as e:
                print(f"Error processing record: {e}")
                skipped += 1
                
        connection.commit()
        return {
            'success': True,
            'added': added,
            'updated': updated,
            'skipped': skipped
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        cursor.close()
        connection.close()

def import_budget_data(user_id, data):
    """Import budget categories for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        added = 0
        updated = 0
        skipped = 0
        
        for record in data:
            try:
                # Check if category exists
                cursor.execute(
                    "SELECT name FROM expenses_category WHERE name = %s AND user_id = %s",
                    (record['category'], user_id)
                )
                if cursor.fetchone():
                    updated += 1
                else:
                    # Create new category
                    cursor.execute(
                        "INSERT INTO expenses_category (name, user_id) VALUES (%s, %s)",
                        (record['category'], user_id)
                    )
                    added += 1
                    
            except Exception as e:
                print(f"Error processing record: {e}")
                skipped += 1
                
        connection.commit()
        return {
            'success': True,
            'added': added,
            'updated': updated,
            'skipped': skipped
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        cursor.close()
        connection.close()