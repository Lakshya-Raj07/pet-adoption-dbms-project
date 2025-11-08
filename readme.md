Pet Adoption Center Management System

This is a college-level project for a Database Management Systems (DBMS) course. It demonstrates a full-stack application built with Python and MySQL, with a primary focus on robust database design, complex queries, triggers, and procedures.

🐾 Project Overview

The system manages the core operations of a pet adoption center. It connects shelters, employees, animals, and customers (who can be adopters, donors, or both). The goal is to create a realistic, data-driven application that showcases deep understanding of DBMS concepts.

⚙️ Tech Stack

Backend: Python (Flask)

Database: MySQL

Core Focus: SQL, Database Design, Normalization, Triggers, Procedures, Complex Queries

Frontend: HTML / CSS / JavaScript (via Flask Templates)

📦 Database Design

Entity-Relationship (ER) Model Description

The database is designed around the following core entities and relationships:

Entities:

Shelter: Stores information about each adoption center location (e.g., name, location, capacity).

Employee: Staff members who work at a shelter.

Animal: Pets available for adoption (e.g., name, species, breed, status).

Customer: A person who interacts with the center. This is the parent table for the ISA relationship.

Adopter: A type of customer who adopts animals. (ISA relationship with Customer).

Donor: A type of customer who donates money. (ISA relationship with Customer).

Relationship Tables:

Adoption: A many-to-many (or ternary) relationship linking Animal, Adopter, and Employee.

Donation: A many-to-many relationship linking Donor and Shelter.

Relationships

1:M (One-to-Many):

Shelter (1) -> Employee (M): One shelter has many employees.

Shelter (1) -> Animal (M): One shelter houses many animals.

ISA (Specialization):

Customer is the parent entity.

Adopter (1) -> Customer (1): An adopter is a customer. This is a 1:1 relationship where the adopter_id is both a Primary Key and a Foreign Key to Customer.

Donor (1) -> Customer (1): A donor is a customer. (Same 1:1 structure).

This allows a customer to be an adopter, a donor, or both, while avoiding data redundancy.

M:N (Many-to-Many):

Adopter (M) <-> Animal (M) is resolved by the Adoption table. An adopter can adopt multiple animals, and an animal (in theory, if returned) could be adopted by multiple people over time (though our model simplifies to 1 adoption per animal). The Adoption table also links the Employee who processed it.

Donor (M) <-> Shelter (M) is resolved by the Donation table. A donor can donate to multiple shelters, and a shelter can receive donations from multiple donors.

Normalization

The schema is designed to be in 3rd Normal Form (3NF).

All tables have a primary key.

All non-key attributes are fully functionally dependent on the primary key (1NF & 2NF).

There are no transitive dependencies (3NF). For example, in Employee, shelter_id determines the shelter's details, but those details are stored in the Shelter table, not in the Employee table.

triggers Schemas (Triggers)

This database uses triggers to automatically maintain data integrity and enforce business rules:

after_animal_insert:

Event: After a new Animal is inserted.

Action: Automatically increments the current_occupancy of the animal's assigned shelter by 1.

after_adoption_insert:

Event: After a new Adoption record is created.

Action: This trigger performs two critical actions:

Updates the Animal's status from 'Available' to 'Adopted'.

Decrements the current_occupancy of the animal's original shelter by 1.

🚀 How to Run

Set up MySQL:

Ensure you have a MySQL server running.

Create a user and password.

Set Environment Variables:

This project uses environment variables to keep credentials secure. Create a .env file in the backend/ directory (or set them in your system) with:

DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=pet_adoption_db


Note: The DB_NAME is the database that will be created by the script.

Install Python Dependencies:

pip install mysql-connector-python python-dotenv


Run the Creation Script:

This will connect to MySQL, create the database, and run all the SQL files.

cd backend
python db/creation.py


Run the Insertion Script:

This will populate the new database with sample data.

python db/insertion.py


Verify:

You can now connect to your pet_adoption_db database using a tool like MySQL Workbench or DBeaver and see all the tables, data, and triggers.

Next Steps

With the database built, the next steps are:

Build the Flask backend (app.py).

Create the query module (queries.py) to execute simple and complex SQL.

Create the frontend templates (index.html, etc.) to interact with the backend.