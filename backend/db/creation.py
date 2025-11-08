# backend/db/creation.py
# FINAL FIX (Har function apna connection khud banayega)

import mysql.connector
from mysql.connector import Error
from connection import get_db_connection
import os
import re

def execute_sql_file(db_name, file_path):
    """
    Ek .sql file ko execute karta hai.
    Yeh apna connection khud banata aur band karta hai.
    """
    print(f"Executing SQL file: {file_path}")
    
    connection = None # Connection abhi nahi bana
    try:
        # Step 1: File ko padho
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print(f"Error: SQL file not found at {file_path}")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    try:
        # Step 2: Naya connection banao
        connection = get_db_connection(db_name)
        if connection is None:
            print(f"Error: Could not connect to DB '{db_name}' for executing file.")
            return False
            
        cursor = connection.cursor()
        
        # Step 3: Script execute karo (DELIMITER logic)
        current_delimiter = ';'
        command_buffer = ''
        
        for line in sql_script.split('\n'):
            line = line.strip()
            
            if not line or line.startswith('--'):
                continue 

            if line.upper().startswith('DELIMITER '):
                current_delimiter = line.split(' ')[1]
                continue
                
            command_buffer += line + ' '
            
            if command_buffer.endswith(current_delimiter + ' '):
                command = command_buffer[:-len(current_delimiter + ' ')].strip()
                
                if command:
                    try:
                        cursor.execute(command)
                    except Error as e:
                        print(f"\n--- ERROR ---")
                        print(f"Error executing command: {e}")
                        print(f"Failed Command: {command}")
                        print(f"--- END ERROR ---")
                        connection.rollback()
                        return False
                
                command_buffer = '' # Buffer ko reset karo
                
        if command_buffer.strip():
            try:
                cursor.execute(command_buffer.strip())
            except Error as e:
                print(f"Error executing final command: {e}")
                connection.rollback()
                return False

        connection.commit()
        print(f"Successfully executed SQL file: {file_path}")
        return True

    except Error as e:
        print(f"Error during SQL execution: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        # Step 4: Connection ko band karo (chahe pass ho ya fail)
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            # print(f"Connection for {file_path} closed.")


def main():
    # .env file 'backend' folder mein honi chahiye
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=dotenv_path)

    db_name = os.environ.get('DB_NAME', 'pet_adoption_db')
    
    # 1. Server se connect karo (sirf DB banane ke liye)
    conn_server = get_db_connection()
    if not conn_server:
        print("Could not connect to MySQL server. Exiting.")
        return

    cursor = conn_server.cursor()
    
    # 2. Database banao
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()
        conn_server.close()
    
    # 3. Ab, har SQL file ko execute karo
    # Har function apna connection khud banayega/band karega
    
    base_dir = os.path.dirname(__file__)
    schema_file = os.path.join(base_dir, 'schema.sql')
    triggers_file = os.path.join(base_dir, 'triggers.sql')
    procedures_file = os.path.join(base_dir, 'procedures.sql')

    print("\n--- STEP 1: EXECUTING SCHEMA ---")
    if not execute_sql_file(db_name, schema_file):
        print("Failed to create schema. Aborting.")
        return

    print("\n--- STEP 2: EXECUTING TRIGGERS ---")
    if not execute_sql_file(db_name, triggers_file):
        print("Failed to create triggers. Aborting.")
        return

    print("\n--- STEP 3: EXECUTING PROCEDURES ---")
    if not execute_sql_file(db_name, procedures_file):
        print("Failed to create procedures. Aborting.")
        return

    print("\nDatabase setup complete. All tables, triggers, and procedures are created.")
    print("You can now run 'insertion.py' to add sample data.")

if __name__ == "__main__":
    main()