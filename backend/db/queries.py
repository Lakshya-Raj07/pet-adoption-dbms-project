import mysql.connector
from mysql.connector import Error
import os

# --- IMPORT from your existing connection file ---
# We get the DB_NAME from the .env file as well
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
    # Fallback for testing, but .env is preferred
    DB_NAME = 'pet_adoption_db'






# --- GENERIC SELECT ALL FUNCTION ---
def select_all_records(table_name):
    """
    Fetches all records from a table.
    Returns:
        (list, None) on success
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor(dictionary=True)
    results = None
    
    try:
        # Use backticks for table names in case they are keywords
        query = f"SELECT * FROM `{table_name}`"
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully fetched {len(results)} records from {table_name}.")
        return (results, None) # SUCCESS
        
    except Error as e:
        print(f"Error while fetching records: {e}")
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()







# --- GENERIC SELECT BY ID FUNCTION ---
def select_record_by_id(table_name, id_column, id_value):
    """
    Fetches a single record by its ID.
    Returns:
        (dict, None) on success
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor(dictionary=True)
    result = None
    
    try:
        # Use backticks for table and column names
        query = f"SELECT * FROM `{table_name}` WHERE `{id_column}` = %s"
        cursor.execute(query, (id_value,))
        result = cursor.fetchone()
        
        if result:
            print(f"Successfully fetched record {id_value} from {table_name}.")
            return (result, None) # SUCCESS
        else:
            print(f"No record found with ID {id_value} in {table_name}.")
            # This is not a DB error, but a "not found" error
            return (None, f"No record found with ID {id_value} in {table_name}.") # FAILURE (Not found)
            
    except Error as e:
        print(f"Error while fetching record: {e}")
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()





# --- GENERIC SELECT BY CRITERIA ---
def select_records_by_criteria(table_name, criteria):
    """
    Fetches records based on a dictionary of criteria.
    Returns:
        (list, None) on success
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor(dictionary=True)
    results = None
    
    try:
        # Build the WHERE clause dynamically
        where_parts = [f"`{column}` = %s" for column in criteria.keys()]
        where_clause = " AND ".join(where_parts)
        values = list(criteria.values())
        
        query = f"SELECT * FROM `{table_name}` WHERE {where_clause}"
        
        cursor.execute(query, tuple(values))
        results = cursor.fetchall()
        print(f"Successfully fetched {len(results)} records from {table_name} matching criteria.")
        return (results, None) # SUCCESS
        
    except Error as e:
        print(f"Error while fetching records: {e}")
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()






def get_all_adopter_details():
    """
    Fetches all adopters by joining Customer and Adopter tables.
    Returns:
        (list, None) on success
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor(dictionary=True)
    results = None
    
    try:
        # Yeh JOIN query hai jo DBMS project ke liye important hai
        query = """
            SELECT 
                a.adopter_id,
                c.customer_id,
                c.first_name,
                c.last_name,
                c.phone
            FROM Customer c
            JOIN Adopter a ON c.customer_id = a.customer_id
            ORDER BY c.first_name;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully fetched {len(results)} adopter detail records.")
        return (results, None) # SUCCESS
        
    except Error as e:
        print(f"Error fetching adopter details: {e}")
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()






# --- *** NEW FUNCTION *** ---
def get_all_donor_details():
    """
    Fetches all donors by joining Customer and Donor tables.
    Returns:
        (list, None) on success
        (None, str) on error
    """
    connection = get_db_connection(DB_NAME)
    if connection is None:
        return (None, "Failed to connect to database.")

    cursor = connection.cursor(dictionary=True)
    results = None
    
    try:
        # Yeh JOIN query hai
        query = """
            SELECT 
                d.donor_id,
                c.customer_id,
                c.first_name,
                c.last_name,
                c.phone,
                d.amount
            FROM Customer c
            JOIN Donor d ON c.customer_id = d.customer_id
            ORDER BY c.first_name;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully fetched {len(results)} donor detail records.")
        return (results, None) # SUCCESS
        
    except Error as e:
        print(f"Error fetching donor details: {e}")
        return (None, str(e)) # FAILURE
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()




def get_report_shelter_occupancy():
    """
    REPORT 1 (LEFT JOIN + GROUP BY):
    Fetches animal count per shelter, including empty shelters.
    """
    connection = get_db_connection(DB_NAME)
    if connection is None: return (None, "Failed to connect to database.")
    cursor = connection.cursor(dictionary=True)
    try:
        # LEFT JOIN zaroori hai taaki '0' count waale shelters bhi aayein
        query = """
            SELECT 
                s.shelter_id,
                s.name,
                s.capacity,
                s.current_occupancy,
                COUNT(a.animal_id) AS calculated_animal_count
            FROM Shelter s
            LEFT JOIN Animal a ON s.shelter_id = a.shelter_id AND a.status = 'Available'
            GROUP BY s.shelter_id, s.name, s.capacity, s.current_occupancy
            ORDER BY s.name;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully fetched shelter occupancy report.")
        return (results, None)
    except Error as e:
        print(f"Error fetching shelter occupancy report: {e}")
        return (None, str(e))
    finally:
        if connection.is_connected(): cursor.close(); connection.close()


def get_report_employees_above_average():
    """
    REPORT 2 (Subquery):
    Fetches employees earning more than the average salary.
    """
    connection = get_db_connection(DB_NAME)
    if connection is None: return (None, "Failed to connect to database.")
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                employee_id, 
                name, 
                role, 
                salary
            FROM Employee
            WHERE salary > (SELECT AVG(salary) FROM Employee)
            ORDER BY salary DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully fetched above-average employees report.")
        return (results, None)
    except Error as e:
        print(f"Error fetching above-average employees report: {e}")
        return (None, str(e))
    finally:
        if connection.is_connected(): cursor.close(); connection.close()


def get_report_multi_adopters():
    """
    REPORT 3 (Multi-JOIN + GROUP BY + HAVING):
    Fetches adopters who have adopted more than one animal.
    """
    connection = get_db_connection(DB_NAME)
    if connection is None: return (None, "Failed to connect to database.")
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.phone,
                COUNT(a.adoption_id) AS total_adoptions
            FROM Adoption a
            JOIN Adopter ad ON a.adopter_id = ad.adopter_id
            JOIN Customer c ON ad.customer_id = c.customer_id
            GROUP BY c.customer_id, c.first_name, c.last_name, c.phone
            HAVING total_adoptions > 1
            ORDER BY total_adoptions DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully fetched multi-adopters report.")
        return (results, None)
    except Error as e:
        print(f"Error fetching multi-adopters report: {e}")
        return (None, str(e))
    finally:
        if connection.is_connected(): cursor.close(); connection.close()




# --- Example of how to use these functions  ---
if __name__ == "__main__":
    



    # Example 1: Get ALL animals
    print("\n--- Example 1: Selecting all animals ---")
    all_animals, error = select_all_records(table_name="Animal")
    if error:
        print(f"Error fetching animals: {error}")
    elif all_animals:
        for animal in all_animals:
            print(f"  - ID: {animal['animal_id']}, Name: {animal['name']}, Species: {animal['species']}")
    else:
        print("  - No animals found.")
            
            



    # Example 2: Get ONE employee
    print("\n--- Example 2: Selecting one employee ---")
    employee, error = select_record_by_id(table_name="Employee", id_column="employee_id", id_value=2)
    if error:
        print(f"Error fetching employee: {error}")
    elif employee:
        print(f"  Found employee: {employee['name']}, Role: {employee['role']}")
    else:
        print("  - Employee not found.")





    # Example 3: Get all 'Dog'
    print("\n--- Example 3: Selecting all dogs ---")
    dog_criteria = {"species": "Dog"}
    all_dogs, error = select_records_by_criteria(table_name="Animal", criteria=dog_criteria)
    if error:
        print(f"Error fetching dogs: {error}")
    elif all_dogs:
        for dog in all_dogs:
            print(f"  - Found dog: {dog['name']} (ID: {dog['animal_id']})")
    else:
        print("  - No dogs found.")




    # Example 4: Get a record that doesn't exist
    print("\n--- Example 4: Selecting non-existent animal ---")
    animal, error = select_record_by_id(table_name="Animal", id_column="animal_id", id_value=999)
    if error:
        print(f"  Successfully caught error: {error}")
    else:
        print(f"  Found animal: {animal}") # This shouldn't run
    




    print("\n--- Example 5: Selecting all Adopter Details (JOIN) ---")
    adopters, error = get_all_adopter_details()
    if error:
        print(f"  Error fetching adopters: {error}")
    elif adopters:
        for adopter in adopters:
            print(f"  - Adopter ID: {adopter['adopter_id']}, Name: {adopter['first_name']} {adopter['last_name']}")
    else:
        print("  - No adopters found.")




    print("\n--- Example 6: Selecting all Donor Details (JOIN) ---")
    donors, error = get_all_donor_details()
    if error:
        print(f"  Error fetching donors: {error}")
    elif donors:
        for donor in donors:
            print(f"  - Donor ID: {donor['donor_id']}, Name: {donor['first_name']}, Amount: {donor['amount']}")
    else:
        print("  - No donors found.")





    print("\n--- REPORT 1: Shelter Occupancy ---")
    report1, error = get_report_shelter_occupancy()
    if error:
        print(f"  Error: {error}")
    elif report1:
        for item in report1:
            print(f"  - {item['name']}: {item['calculated_animal_count']} animals (Trigger value: {item['current_occupancy']})")
    



    print("\n--- REPORT 2: Employees Above Average ---")
    report2, error = get_report_employees_above_average()
    if error:
        print(f"  Error: {error}")
    elif report2:
        for item in report2:
            print(f"  - {item['name']}: ${item['salary']}")




    print("\n--- REPORT 3: Multi-Adopters ---")
    report3, error = get_report_multi_adopters()
    if error:
        print(f"  Error: {error}")
    elif report3:
        for item in report3:
            print(f"  - {item['first_name']} {item['last_name']}: {item['total_adoptions']} adoptions")
    else:
        print("  - No adopters with multiple adoptions found (yeh theek hai agar data naya hai).")

