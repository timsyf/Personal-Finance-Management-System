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
        
        # Create users table 
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

        # Create income sources table first (since it's referenced by income_tracker)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_sources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                user_id INT NOT NULL,
                UNIQUE KEY unique_source_per_user (name, user_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create income_tracker table after income_sources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_tracker (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                source_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (source_id) REFERENCES income_sources(id)
            )
        """)
        
        # Create recurring income table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_income (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description VARCHAR(255) NOT NULL,
                source_id INT NOT NULL,
                frequency VARCHAR(50) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                next_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (source_id) REFERENCES income_sources(id)
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
                end_date DATE NOT NULL,
                next_due_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                
            )
        """)

        # create budgets table
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category VARCHAR(50),
                amount DECIMAL(10,2) NOT NULL,
                frequency ENUM('Monthly', 'Yearly') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # create alert table
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                budget_id INT,
                category VARCHAR(50),
                alert_message VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (budget_id) REFERENCES budgets(id)
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
        
        # Create expenses_category table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fixed_queries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                query_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
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
            
        # Delete user's data from all tables in correct order (foreign key constraints)
        cursor.execute("DELETE FROM recurring_income WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM income_tracker WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM income_sources WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM recurring_transactions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM expenses_tracker WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM expenses_category WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM budgets WHERE user_id = %s", (user_id,))
        
        # Finally delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        return True, "User and all associated data deleted successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

def update_user(user_id, username=None, email=None, is_admin=None, admin_id=None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify the admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (admin_id,))
        admin = cursor.fetchone()
        if not admin or not admin[0]:
            return False, "Not authorized"
            
        # Build update query dynamically based on provided fields
        update_parts = []
        params = []
        
        if username is not None:
            update_parts.append("username = %s")
            params.append(username)
            
        if email is not None:
            update_parts.append("email = %s")
            params.append(email)
            
        if is_admin is not None:
            update_parts.append("is_admin = %s")
            params.append(is_admin)
            
        if not update_parts:
            return False, "No fields to update"
            
        query = f"UPDATE users SET {', '.join(update_parts)} WHERE id = %s"
        params.append(user_id)
        
        cursor.execute(query, tuple(params))
        connection.commit()
        
        return True, "User updated successfully"
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error
            return False, "Username or email already exists"
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