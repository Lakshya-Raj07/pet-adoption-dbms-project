import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load .env file from the 'backend' folder (one level up)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

def get_db_connection(db_name=None):
    """
    Creates a connection to the MySQL server.
    Forces 'use_pure=True' to avoid C-extension errors.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD'),
            database=db_name,
            use_pure=True  
        )
        # print("MySQL (Pure Python) connection successful")
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        print("Error: MySQL se connect nahi ho pa raha. Check karo ki .env file 'backend' folder mein hai aur password sahi hai.")
        exit(1)
        
    return connection

# --- Test function (sirf is file ko run karne ke liye) ---
if __name__ == "__main__":
    print("Testing connection.py directly...")
    
    # 1. Server se connection (bina database ke)
    conn_server = get_db_connection()
    if conn_server:
        print("Server connection (db_name=None) SUCCESSFUL.")
        conn_server.close()
    else:
        print("Server connection (db_name=None) FAILED.")

    # 2. Database se connection (db_name ke saath)
    DB_NAME_TEST = os.environ.get('DB_NAME')
    if DB_NAME_TEST:
        conn_db = get_db_connection(DB_NAME_TEST)
        if conn_db:
            print(f"Database connection (db_name={DB_NAME_TEST}) SUCCESSFUL.")
            conn_db.close()
        else:
            print(f"Database connection (db_name={DB_NAME_TEST}) FAILED.")
    else:
        print("Skipping DB connection test (DB_NAME not in .env).")