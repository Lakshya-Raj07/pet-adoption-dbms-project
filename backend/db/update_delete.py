import mysql.connector
from mysql.connector import Error
import os

# --- IMPORT from your existing connection file ---
try:
    from .connection import get_db_connection
except ImportError:
    # This fallback helps if running the file directly
    from connection import get_db_connection

from dotenv import load_dotenv

# Load .env file from the 'backend' directory (one level up)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DB_NAME = os.environ.get('DB_NAME')
if not DB_NAME:
    print("Error: DB_NAME not found in .env file. Make sure .env is in the 'backend' folder.")
    DB_NAME = 'pet_adoption_db' # Fallback


# --- GENERIC INSERT FUNCTION ---
def insert_record(table_name, insert_data):
    """
    Inserts a new record into any table.
    Returns: (int, None) on success, (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor()
    
    try:
        columns = '`' + '`, `'.join(insert_data.keys()) + '`'
        placeholders = ', '.join(['%s'] * len(insert_data))
        values = list(insert_data.values())
        
        insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        
        cursor.execute(insert_query, tuple(values))
        connection.commit()
        
        new_record_id = cursor.lastrowid
        print(f"Record inserted successfully into {table_name} with ID: {new_record_id}")
        return (new_record_id, None) # SUCCESS

    except Error as e:
        print(f"Error while inserting record: {e}")
        connection.rollback()
        if e.errno == 1644: # MySQL error code for SIGNAL SQLSTATE '45000'
            return (None, e.msg) # Return the custom error message from the trigger
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# --- GENERIC DELETE FUNCTION ---
def delete_record(table_name, id_column, id_value):
    """
    Deletes a record from any table based on its ID.
    Returns: (int, None) on success, (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor()
    
    try:
        delete_query = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
        
        cursor.execute(delete_query, (id_value,))
        connection.commit()
        
        rows_affected = cursor.rowcount
        if rows_affected == 0:
            print(f"No record found with ID {id_value} in table {table_name}. Nothing deleted.")
            return (None, f"No record found with ID {id_value} in {table_name}.") # FAILURE (Not found)
        
        print(f"Record {id_value} deleted successfully from table {table_name}")
        return (rows_affected, None) # SUCCESS
        
    except Error as e:
        print(f"Error while deleting record: {e}")
        connection.rollback()
        if e.errno == 1644:
            return (None, e.msg)
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# --- GENERIC UPDATE FUNCTION ---
def update_record(table_name, id_column, id_value, update_data):
    """
    Updates one or more columns for a record in any table.
    Returns: (int, None) on success, (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor()
    
    try:
        set_parts = [f"`{column}` = %s" for column in update_data.keys()]
        set_clause = ", ".join(set_parts)
        values = list(update_data.values())
        values.append(id_value) # Add the ID value for the WHERE clause
        
        update_query = f"UPDATE `{table_name}` SET {set_clause} WHERE `{id_column}` = %s"
        
        cursor.execute(update_query, tuple(values))
        connection.commit()
        
        rows_affected = cursor.rowcount
        if rows_affected == 0:
            print(f"No record found with ID {id_value} in table {table_name}. Nothing updated.")
            return (0, None) # SUCCESS (but no rows changed)

        print(f"Record {id_value} in table {table_name} updated successfully. Rows: {rows_affected}")
        return (rows_affected, None) # SUCCESS
        
    except Error as e:
        print(f"Error while updating record: {e}")
        connection.rollback()
        if e.errno == 1644:
            return (None, e.msg)
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# --- SPECIFIC FUNCTION: EXECUTE ADOPTION ---
def execute_adoption_procedure(animal_id, adopter_id, employee_id):
    """
    Calls the 'CreateAdoption' stored procedure.
    Returns: (dict, None) on success, (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.callproc('CreateAdoption', [animal_id, adopter_id, employee_id])
        
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()
            
        connection.commit()
        
        if result:
            print(f"Successfully executed CreateAdoption procedure for animal {animal_id}")
            return (result, None) # SUCCESS
        else:
            return (None, "Adoption procedure ran but did not return details.")

    except Error as e:
        print(f"Error executing adoption procedure: {e}")
        connection.rollback()
        if e.errno == 1644: # Check for 'Animal already adopted' error
            return (None, e.msg)
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# --- SPECIFIC FUNCTION: EXECUTE CREATE ADOPTER ---
def execute_create_adopter(first_name, last_name, phone):
    """
    Calls the 'CreateAdopter' stored procedure.
    This will test the transaction.
    
    Returns:
        (dict, None) on success (returns new adopter details)
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Stored procedure call
        cursor.callproc('CreateAdopter', [first_name, last_name, phone])
        
        # Naya record fetch karo
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()
            
        connection.commit()
        
        if result:
            print(f"Successfully executed CreateAdopter procedure for {first_name}")
            return (result, None) # SUCCESS
        else:
            return (None, "CreateAdopter procedure ran but did not return details.")

    except Error as e:
        print(f"Error executing create adopter procedure: {e}")
        connection.rollback()
        if e.errno == 1644: # Check for our custom error
            return (None, e.msg)
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# --- SPECIFIC FUNCTION: EXECUTE CREATE DONOR ---
def execute_create_donor(first_name, last_name, phone, amount):
    """
    Calls the 'CreateDonor' stored procedure.
    This will test the transaction.
    
    Returns:
        (dict, None) on success (returns new donor details)
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Stored procedure call
        cursor.callproc('CreateDonor', [first_name, last_name, phone, amount])
        
        # Naya record fetch karo
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()
            
        connection.commit()
        
        if result:
            print(f"Successfully executed CreateDonor procedure for {first_name}")
            return (result, None) # SUCCESS
        else:
            return (None, "CreateDonor procedure ran but did not return details.")

    except Error as e:
        print(f"Error executing create donor procedure: {e}")
        connection.rollback()
        if e.errno == 1644: # Check for our custom error
            return (None, e.msg)
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# --- Example of how to use these functions (UPDATED) ---
if __name__ == "__main__":
    
    # --- INSERT EXAMPLE ---
    print("\n--- RUNNING GENERIC INSERT (Testing 'check_shelter_capacity' trigger) ---")
    new_animal = {
        "name": "Test Animal",
        "species": "Cat",
        "breed": "Domestic",
        "age": 1,
        "gender": "F",
        "status": "Available",
        "shelter_id": 1 # Assumes shelter 1 exists
    }
    new_id, error = insert_record(table_name="Animal", insert_data=new_animal)
    if error:
        print(f"  Error inserting animal: {error}")
    else:
        print(f"  Successfully inserted animal with new ID: {new_id}")

    # --- UPDATE EXAMPLE ---
    print("\n--- RUNNING GENERIC UPDATE (Testing 'log_salary_change' trigger) ---")
    emp_update = {"salary": 55000} # Give employee 1 a raise
    rows_affected, error = update_record(table_name="Employee", id_column="employee_id", id_value=1, update_data=emp_update)
    if error:
        print(f"  Error updating employee salary: {error}")
    else:
        print(f"  Successfully updated employee 1's salary. Rows affected: {rows_affected}")
        
    # --- ADOPTION EXAMPLE ---
    print("\n--- RUNNING ADOPTION PROCEDURE (Testing ALL adoption triggers) ---")
    # This will adopt Animal ID 2 (Buddy) by Adopter ID 1 (John Doe) handled by Employee ID 1
    # Assumes these IDs exist from your insertion.py script
    adoption_details, error = execute_adoption_procedure(animal_id=2, adopter_id=1, employee_id=1)
    if error:
        print(f"  Error during adoption: {error}")
    else:
        print(f"  Adoption successful! Details: {adoption_details}")
    
    # --- DELETE EXAMPLE ---
    print("\n--- RUNNING GENERIC DELETE ---")
    if new_id and not error: # If we successfully added 'Test Animal'
        print(f"  Attempting to delete the 'Test Animal' we just added (ID: {new_id})...")
        rows_deleted, error = delete_record(table_name="Animal", id_column="animal_id", id_value=new_id)
        if error:
            print(f"  Error deleting animal: {error}")
        else:
            print(f"  Successfully deleted 'Test Animal'. Rows deleted: {rows_deleted}")
    else:
        print("  Skipping delete test because insert test failed or was skipped.")

    

    # --- CREATE ADOPTER EXAMPLE ---
    print("\n--- RUNNING CREATE ADOPTER PROCEDURE (Testing Transaction) ---")
    new_adopter, error = execute_create_adopter("Test", "Adopter", "555-9876")
    if error:
        print(f"  Error creating adopter: {error}")
    else:
        print(f"  Adopter created successfully! Details: {new_adopter}")

    # --- CREATE DONOR EXAMPLE ---
    print("\n--- RUNNING CREATE DONOR PROCEDURE (Testing Transaction) ---")
    new_donor, error = execute_create_donor("Test", "Donor", "555-1111", 500.75)
    if error:
        print(f"  Error creating donor: {error}")
    else:
        print(f"  Donor created successfully! Details: {new_donor}")
