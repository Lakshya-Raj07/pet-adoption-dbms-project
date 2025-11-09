# backend/app.py

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os

# --- Import your generic query functions ---
try:
    from .db.queries import (
        select_all_records, 
        select_record_by_id, 
        select_records_by_criteria,
        get_all_adopter_details,
        get_all_donor_details,
        get_report_shelter_occupancy,
        get_report_employees_above_average,
        get_report_multi_adopters
    )
    from .db.update_delete import (
        update_record, 
        delete_record, 
        insert_record, 
        execute_adoption_procedure,
        execute_create_adopter,
        execute_create_donor,
    )
except ImportError:
    print("ERROR: Make sure app.py is in the 'backend' folder")
    print("And your query files are in 'backend/db/'")
    # Fallback for simple testing
    from db.queries import (
        select_all_records, 
        select_record_by_id, 
        select_records_by_criteria,
        get_all_adopter_details,
        get_all_donor_details,
        get_report_shelter_occupancy,
        get_report_employees_above_average,
        get_report_multi_adopters
    )
    from db.update_delete import (
        update_record, 
        delete_record, 
        insert_record, 
        execute_adoption_procedure,
        execute_create_adopter,
        execute_create_donor
    )

# --- Flask App Setup ---
# *** Hum Flask ko bata rahe hain ki templates folder kahan hai ***
# Path ko ../templates set kar rahe hain (ek folder upar, fir templates mein)
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

CORS(app) # Allows frontend to call this API


# --- Helper for checking query results ---
def handle_query_result(data, error, success_code=200):
    """Generates a standard API response from query results."""
    if error:
        # Check for user-defined errors (e.g., "Shelter is full")
        if "45000" in str(error): # MySQL user-defined error
            # Error message ko clean kar rahe hain
            user_error = str(error).split(":")[-1].strip().replace("'", "")
            return jsonify({"error": user_error}), 400
        
        # Check for "Not Found" errors from our query functions
        if "No record found" in str(error):
            return jsonify({"error": str(error)}), 404

        # Baki sab errors 500 hain
        return jsonify({"error": f"Internal Server Error: {error}"}), 500
    
    # Agar data list hai aur khaali hai
    if isinstance(data, list) and not data:
        return jsonify([]), 200 # Empty list is valid JSON, not an error

    # Agar data None hai (jo nahi hona chahiye agar error None hai, but just in case)
    if data is None:
        return jsonify({"error": "No data found"}), 404

    # On success
    return jsonify(data), success_code

# ===============================================
#  *** ROUTE TO SERVE FRONTEND ***
# ===============================================
# Yeh route '/' (homepage) par index.html file ko serve karega
@app.route('/', methods=['GET'])
def serve_index():
    """Serves the main index.html file from the templates folder."""
    return render_template('index.html')

#
# 'Manage Animals' page
@app.route('/animals', methods=['GET'])
def serve_animals_page():
    """Serves the animals.html management page."""
    return render_template('animals.html')

@app.route('/adopters', methods=['GET'])
def serve_adopters_page():
    return render_template('adopters.html')


@app.route('/shelters', methods=['GET'])
def serve_shelters_page():
    return render_template('shelters.html')


@app.route('/donors', methods=['GET'])
def serve_donors_page():
    """Serves the donors.html management page."""
    return render_template('donors.html')


@app.route('/employees', methods=['GET']) 
def serve_employees_page():
    return render_template('employees.html')


@app.route('/reports', methods=['GET'])
def serve_reports_page():
    """Serves the reports.html page."""
    return render_template('reports.html')

# ===============================================
#  *** API ROUTES  ***
# ===============================================

# --- Shelter Routes ---
@app.route('/api/shelters', methods=['GET'])
def get_shelters():
    data, error = select_all_records(table_name="Shelter")
    return handle_query_result(data, error)

@app.route('/api/shelters/<int:shelter_id>', methods=['GET'])
def get_shelter_by_id(shelter_id):
    data, error = select_record_by_id(table_name="Shelter", id_column="shelter_id", id_value=shelter_id)
    return handle_query_result(data, error)

@app.route('/api/shelters', methods=['POST'])
def add_new_shelter():
    shelter_data = request.json
    try:
        # Hum sirf teen zaroori columns insert karenge
        insert_data = {
            'name': shelter_data['name'],
            'address': shelter_data['address'], # <-- KEY MATCHES SCHEMA (address)
            'capacity': shelter_data['capacity']
        }
    except KeyError:
        return jsonify({"error": "Missing name, address, or capacity"}), 400
        
    data, error = insert_record(table_name="Shelter", insert_data=insert_data)
    return handle_query_result({"new_shelter_id": data}, error, success_code=201)

@app.route('/api/shelters/<int:shelter_id>', methods=['DELETE'])
def delete_shelter_route(shelter_id):
    data, error = delete_record(table_name="Shelter", id_column="shelter_id", id_value=shelter_id)
    return handle_query_result({"rows_affected": data}, error)

# --- Animal Routes ---
@app.route('/api/animals', methods=['GET'])
def get_animals():
    # Example: /api/animals?status=Available
    status = request.args.get('status')
    if status:
        criteria = {"status": status}
        data, error = select_records_by_criteria(table_name="Animal", criteria=criteria)
    else:
        data, error = select_all_records(table_name="Animal")
    return handle_query_result(data, error)

@app.route('/api/animals', methods=['POST'])
def add_new_animal():
    new_animal_data = request.json
    # Yeh aapke 'check_shelter_capacity' trigger ko test karega
    data, error = insert_record(table_name="Animal", insert_data=new_animal_data)
    # 201 = Created (aur hum naya 'data' (new_id) bhej rahe hain)
    return handle_query_result({"new_animal_id": data}, error, success_code=201)

@app.route('/api/animals/<int:animal_id>', methods=['GET'])
def get_animal_by_id(animal_id):
    data, error = select_record_by_id(table_name="Animal", id_column="animal_id", id_value=animal_id)
    return handle_query_result(data, error)

@app.route('/api/animals/<int:animal_id>', methods=['PUT'])
def update_animal(animal_id):
    update_data = request.json
    data, error = update_record(table_name="Animal", id_column="animal_id", id_value=animal_id, update_data=update_data)
    return handle_query_result({"rows_affected": data}, error)

@app.route('/api/animals/<int:animal_id>', methods=['DELETE'])
def delete_animal_route(animal_id):
    data, error = delete_record(table_name="Animal", id_column="animal_id", id_value=animal_id)
    return handle_query_result({"rows_affected": data}, error)

# --- Employee Routes ---
@app.route('/api/employees', methods=['GET'])
def get_employees():
    data, error = select_all_records(table_name="Employee")
    return handle_query_result(data, error)

@app.route('/api/employees', methods=['POST'])
def add_employee():
    new_employee_data = request.json
    data, error = insert_record(table_name="Employee", insert_data=new_employee_data)
    return handle_query_result({"new_employee_id": data}, error, success_code=201)

@app.route('/api/employees/<int:employee_id>/salary', methods=['PUT'])
def update_employee_salary(employee_id):
    # Yeh aapke 'log_salary_change' trigger ko test karega
    salary_data = request.json # e.g., {"salary": 60000}
    if 'salary' not in salary_data:
        return jsonify({"error": "Missing 'salary' in request body"}), 400
        
    data, error = update_record(table_name="Employee", id_column="employee_id", id_value=employee_id, update_data=salary_data)
    return handle_query_result({"rows_affected": data}, error)

# --- Adopter/Donor (Customer) Routes ---
@app.route('/api/customers', methods=['GET'])
def get_customers():
    data, error = select_all_records(table_name="Customer")
    return handle_query_result(data, error)

@app.route('/api/adopters/details', methods=['GET'])
def get_adopter_details():
    """
    Returns a JOINed list of Adopters and their Customer details.
    """
    data, error = get_all_adopter_details()
    return handle_query_result(data, error)


@app.route('/api/adopters', methods=['POST'])
def create_new_adopter():
    """
    Creates a new Adopter using the Stored Procedure.
    Expects JSON: {"first_name": "...", "last_name": "...", "phone": "..."}
    """
    adopter_data = request.json
    try:
        first_name = adopter_data['first_name']
        last_name = adopter_data['last_name']
        phone = adopter_data['phone']
    except KeyError:
        return jsonify({"error": "Missing first_name, last_name, or phone"}), 400

    # Stored Procedure ko call karo (jo transaction handle karega)
    data, error = execute_create_adopter(first_name, last_name, phone)
    
    # 201 = Created
    return handle_query_result(data, error, success_code=201)

@app.route('/api/adopters', methods=['GET'])
def get_adopters():
    data, error = select_all_records(table_name="Adopter")
    return handle_query_result(data, error)

# --- Donor Routes  ---
@app.route('/api/donors/details', methods=['GET'])
def get_donor_details():
    """
    Returns a JOINed list of Donors and their Customer details.
    """
    data, error = get_all_donor_details()
    return handle_query_result(data, error)

@app.route('/api/donors', methods=['POST'])
def create_new_donor():
    """
    Creates a new Donor using the Stored Procedure.
    Expects JSON: {"first_name": "...", "last_name": "...", "phone": "...", "amount": ...}
    """
    donor_data = request.json
    try:
        first_name = donor_data['first_name']
        last_name = donor_data['last_name']
        phone = donor_data['phone']
        amount = donor_data['amount']
    except KeyError:
        return jsonify({"error": "Missing first_name, last_name, phone, or amount"}), 400

    # Stored Procedure ko call karo (jo transaction handle karega)
    data, error = execute_create_donor(first_name, last_name, phone, amount)
    
    # 201 = Created
    return handle_query_result(data, error, success_code=201)

@app.route('/api/donors', methods=['GET'])
def get_donors():
    data, error = select_all_records(table_name="Donor")
    return handle_query_result(data, error)

# --- Adoption & Donation Routes ---
@app.route('/api/adoptions', methods=['GET'])
def get_adoptions():
    data, error = select_all_records(table_name="Adoption")
    return handle_query_result(data, error)

@app.route('/api/donations', methods=['GET'])
def get_donations():
    data, error = select_all_records(table_name="Donation")
    return handle_query_result(data, error)

# --- THE MOST IMPORTANT ROUTE ---
# This route runs the procedure that fires all your triggers!
@app.route('/api/adopt', methods=['POST'])
def create_adoption():
    adoption_data = request.json
    try:
        animal_id = adoption_data['animal_id']
        adopter_id = adoption_data['adopter_id']
        employee_id = adoption_data['employee_id']
    except KeyError:
        return jsonify({"error": "Request body must include 'animal_id', 'adopter_id', and 'employee_id'"}), 400

    # This will test:
    # 1. Stored Procedure 'CreateAdoption'
    # 2. 'after_animal_update' trigger (sets status to 'Adopted')
    # 3. 'after_adoption_insert' trigger (updates shelter occupancy)
    data, error = execute_adoption_procedure(animal_id, adopter_id, employee_id)
    
    if error:
         return handle_query_result(None, error) # handle_query_result error ko check karega
        
    return jsonify({"message": "Adoption successful!", "adoption_details": data}), 201



# THIS CODE HAS BEEN MOVED UP DEKHLENA SAB
# --- Shelter Routes (CRUD) ---
# @app.route('/api/shelters', methods=['POST'])
# def add_new_shelter():
#     shelter_data = request.json
#     try:
#         # Hum sirf teen zaroori columns insert karenge
#         insert_data = {
#             'name': shelter_data['name'],
#             'address': shelter_data['address'], # Address, location nahi
#             'capacity': shelter_data['capacity']
#         }
#     except KeyError:
#         return jsonify({"error": "Missing name, address, or capacity"}), 400
        
#     # insert_record automatically current_occupancy = 0 set kar dega
#     data, error = insert_record(table_name="Shelter", insert_data=insert_data)
#     return handle_query_result({"new_shelter_id": data}, error, success_code=201)

# @app.route('/api/shelters/<int:shelter_id>', methods=['DELETE'])
# def delete_shelter_route(shelter_id):
#     # Yeh aapke 'before_shelter_delete' trigger ko test karega
#     data, error = delete_record(table_name="Shelter", id_column="shelter_id", id_value=shelter_id)
#     return handle_query_result({"rows_affected": data}, error)





@app.route('/api/reports/shelter-occupancy', methods=['GET'])
def get_shelter_occupancy_report():
    """API route for Report 1"""
    data, error = get_report_shelter_occupancy()
    return handle_query_result(data, error)

@app.route('/api/reports/employees-above-average', methods=['GET'])
def get_employees_above_average_report():
    """API route for Report 2"""
    data, error = get_report_employees_above_average()
    return handle_query_result(data, error)

@app.route('/api/reports/multi-adopters', methods=['GET'])
def get_multi_adopters_report():
    """API route for Report 3"""
    data, error = get_report_multi_adopters()
    return handle_query_result(data, error)


# --- Main entry point ---
if __name__ == '__main__':
    # Isse run karne ke liye:
    # 1. .env file 'backend' folder mein honi chahiye
    # 2. Terminal ko 'backend' folder ke UPAR waale folder mein kholo
    # 3. Command chalao: python -m backend.app
    #    (ya agar aap 'backend' folder ke andar ho, toh: python app.py)
    print("Starting Flask server at http://127.0.0.1:5000 ...")
    app.run(debug=True)