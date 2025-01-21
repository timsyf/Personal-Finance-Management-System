import mysql.connector
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def create_tables():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create users table with is_admin flag
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(64) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create default admin user if not exists
        admin_password = hash_password("admin123")  # Default admin password
        try:
            cursor.execute("""
                INSERT INTO users (username, password, email, is_admin)
                VALUES ('admin', %s, 'admin@system.com', TRUE)
            """, (admin_password,))
            connection.commit()
            print("Admin user created successfully")
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry error
                print("Admin user already exists")
            else:
                raise err
        
        # Create transactions table with user_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                date DATE NOT NULL,
                type ENUM('income', 'expense') NOT NULL,
                category VARCHAR(50),
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create budget table with user_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create expense categories table with user_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                budget_limit DECIMAL(10,2),
                user_id INT NOT NULL,
                UNIQUE KEY unique_category_per_user (name, user_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create recurring transactions table with user_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                recurring_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                name VARCHAR(255),
                category VARCHAR(50) NOT NULL,
                recurrence ENUM('Daily', 'Weekly', 'Monthly', 'Yearly') NOT NULL,
                start_date DATE NOT NULL,
                next_due_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                
            )
        """)
        
        # Create daily expenses table with user_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses_tracker (
                id INT AUTO_INCREMENT PRIMARY KEY,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                user_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create expenses_category table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses_category (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL
            )
        """)
        
        connection.commit()
        print("Tables verified successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, email):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Hash the password before storing
        hashed_password = hash_password(password)
        
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, hashed_password, email))
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

def verify_user(username, password):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Hash the password for comparison
        hashed_password = hash_password(password)
        
        # Fetch is_admin status
        query = "SELECT id, is_admin FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        return {"id": user[0], "is_admin": user[1]} if user else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

def username_exists(username):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        exists = cursor.fetchone() is not None
        return exists
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

def email_exists(email):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        exists = cursor.fetchone() is not None
        return exists
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

# Admin Functions
def get_all_users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT id, username, email, is_admin, created_at FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        return users
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def change_user_password(user_id, new_password, admin_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify the admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (admin_id,))
        admin = cursor.fetchone()
        if not admin or not admin[0]:
            return False, "Not authorized"
            
        # Change password
        hashed_password = hash_password(new_password)
        query = "UPDATE users SET password = %s WHERE id = %s"
        cursor.execute(query, (hashed_password, user_id))
        connection.commit()
        return True, "Password updated successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def delete_user(user_id, admin_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify the admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (admin_id,))
        admin = cursor.fetchone()
        if not admin or not admin[0]:
            return False, "Not authorized"
            
        # Check if trying to delete an admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user and user[0]:
            return False, "Cannot delete admin users"
            
        # Delete user's data first 
        cursor.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM budgets WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM expense_categories WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM recurring_transactions WHERE user_id = %s", (user_id,))
        
        # Delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        return True, "User deleted successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def create_user_by_admin(username, password, email, is_admin, admin_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify the admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (admin_id,))
        admin = cursor.fetchone()
        if not admin or not admin[0]:
            return False, "Not authorized"
            
        # Create new user
        hashed_password = hash_password(password)
        query = "INSERT INTO users (username, password, email, is_admin) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, hashed_password, email, is_admin))
        connection.commit()
        return True, "User created successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close() 