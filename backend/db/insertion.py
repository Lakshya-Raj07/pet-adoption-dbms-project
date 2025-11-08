# backend/db/insertion.py
# FINAL INSERTION SCRIPT (FIXED "Unread result found" ERROR)

import mysql.connector
from mysql.connector import Error
from connection import get_db_connection
import os
from datetime import date

def insert_data(connection):
    """
    Inserts expanded sample data (10+ entries) for Design 2.
    This data is designed to make all reports work.
    """
    cursor = connection.cursor()
    
    try:
        print("Inserting data into Shelter (6 entries)...")
        # (Shelter data insertion... )
        shelter_data = [
            (1, 'Hope Shelter', '123 Green St, Delhi', 50, 0), (2, 'Safe Haven', '456 Oak Ave, Mumbai', 30, 0),
            (3, 'Paws Place', '789 Palm Rd, Bangalore', 40, 0), (4, 'Animal Friends', '101 Maple Dr, Chennai', 25, 0),
            (5, 'Rescue Roots', '202 Pine Ln, Kolkata', 20, 0), (6, 'Kind Hearts', '303 Cedar Blvd, Pune', 35, 0)
        ]
        cursor.executemany("INSERT INTO Shelter (shelter_id, name, address, capacity, current_occupancy) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name), address=VALUES(address), capacity=VALUES(capacity), current_occupancy=VALUES(current_occupancy)", shelter_data)

        print("Inserting data into Employee (8 entries)...")
        # (Employee data insertion... )
        employee_data = [
            (1, 1, 'Amit Sharma', 'Manager', 60000.00), (2, 1, 'Priya Singh', 'Vet', 75000.00),
            (3, 2, 'Rahul Verma', 'Coordinator', 50000.00), (4, 3, 'Sunita Rao', 'Vet', 80000.00),
            (5, 4, 'Vikram Mehta', 'Manager', 62000.00), (6, 1, 'Anjali Joshi', 'Volunteer', 45000.00),
            (7, 2, 'Suresh Kumar', 'Cleaner', 30000.00), (8, 3, 'Deepa Nair', 'Coordinator', 52000.00)
        ]
        cursor.executemany("INSERT INTO Employee (employee_id, shelter_id, name, role, salary) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE shelter_id=VALUES(shelter_id), name=VALUES(name), role=VALUES(role), salary=VALUES(salary)", employee_data)

        print("Inserting data into Customer (10 entries)...")
        # (Customer data insertion... )
        customer_data = [
            (1, 'John', 'Doe', '555-1111'), (2, 'Jane', 'Smith', '555-2222'), (3, 'Raj', 'Patel', '555-3333'),
            (4, 'Anita', 'Gupta', '555-4444'), (5, 'Michael', 'Brown', '555-5555'), (6, 'Sarah', 'Lee', '555-6666'),
            (7, 'David', 'Chen', '555-7777'), (8, 'Emily', 'White', '555-8888'), (9, 'Chris', 'Taylor', '555-9999'),
            (10, 'Maria', 'Garcia', '555-0000')
        ]
        cursor.executemany("INSERT INTO Customer (customer_id, first_name, last_name, phone) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE first_name=VALUES(first_name), last_name=VALUES(last_name), phone=VALUES(phone)", customer_data)

        print("Inserting data into Adopter (5 entries)...")
        # (Adopter data insertion... )
        adopter_data = [(1, 1), (2, 2), (3, 5), (4, 7), (5, 8)]
        cursor.executemany("INSERT INTO Adopter (adopter_id, customer_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE customer_id=VALUES(customer_id)", adopter_data)

        print("Inserting data into Donor (5 entries)...")
        # (Donor data insertion... )
        donor_data = [(1, 3, 500.00), (2, 4, 1000.00), (3, 6, 250.00), (4, 9, 100.00), (5, 10, 750.00)]
        cursor.executemany("INSERT INTO Donor (donor_id, customer_id, amount) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE customer_id=VALUES(customer_id), amount=VALUES(amount)", donor_data)

        print("Inserting data into Animal (10 entries)...")
        # (Animal data insertion... )
        animal_data = [
            (1, 1, 'Buddy', 'Dog', 'Labrador', 3, 'M', date(2022, 1, 15), 'Available'), (2, 1, 'Whiskers', 'Cat', 'Siamese', 1, 'F', date(2024, 3, 10), 'Available'),
            (3, 2, 'Charlie', 'Dog', 'Golden Retriever', 2, 'M', date(2023, 5, 20), 'Available'), (4, 2, 'Luna', 'Cat', 'Persian', 4, 'F', date(2021, 7, 1), 'Available'),
            (5, 3, 'Max', 'Dog', 'German Shepherd', 5, 'M', date(2020, 4, 25), 'Available'), (6, 1, 'Milo', 'Rabbit', 'Dwarf', 1, 'M', date(2024, 1, 5), 'Available'),
            (7, 3, 'Goldie', 'Bird', 'Canary', 2, 'F', date(2023, 2, 1), 'Available'), (8, 4, 'Rocky', 'Dog', 'Boxer', 6, 'M', date(2019, 8, 30), 'Available'),
            (9, 1, 'Smokey', 'Cat', 'Domestic', 3, 'M', date(2022, 6, 10), 'Available'), (10, 2, 'Daisy', 'Dog', 'Beagle', 1, 'F', date(2024, 1, 20), 'Available')
        ]
        cursor.executemany("INSERT INTO Animal (animal_id, shelter_id, name, species, breed, age, gender, dob, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE shelter_id=VALUES(shelter_id), name=VALUES(name), species=VALUES(species), breed=VALUES(breed), age=VALUES(age), gender=VALUES(gender), dob=VALUES(dob), status=VALUES(status)", animal_data)
        
        
        # --- DATA FOR REPORTS 
        print("Inserting sample adoptions for reports...")
        
        # Adopter 1 (John Doe) adopts Animal 1 (Buddy)
        cursor.callproc('CreateAdoption', [1, 1, 1])
        
        for res in cursor.stored_results():
            res.fetchall() 
        

        # Adopter 1 (John Doe) adopts Animal 2 (Whiskers)
        cursor.callproc('CreateAdoption', [2, 1, 2])
        
        for res in cursor.stored_results():
            res.fetchall()
        
        
        # Adopter 2 (Jane Smith) adopts Animal 3 (Charlie)
        cursor.callproc('CreateAdoption', [3, 2, 3])
        
        for res in cursor.stored_results():
            res.fetchall()
        
        
        print("Sample adoptions added. 'Multi-Adopter' report will now work.")

        connection.commit()
        print("All sample data inserted successfully (10+ entries).")

    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=dotenv_path)

    db_name = os.environ.get('DB_NAME', 'pet_adoption_db')
    
    # Database se connect karo
    conn_db = get_db_connection(db_name)
    if not conn_db:
        print(f"Could not connect to database '{db_name}'. Exiting.")
        return
        
    # Data insert karo
    insert_data(conn_db)

    conn_db.close()
    print("Data insertion complete.")

if __name__ == "__main__":
    main()