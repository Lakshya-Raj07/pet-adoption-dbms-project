document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    const addEmployeeForm = document.getElementById('add-employee-form');
    const formResult = document.getElementById('form-result');
    const employeeTableContainer = document.getElementById('employee-table-container');

    function showResult(element, message, isError = false) {
        element.textContent = message;
        element.className = isError ? 'result-message error-message' : 'result-message success-message';
        setTimeout(() => {
            element.textContent = '';
            element.className = 'result-message';
        }, 5000);
    }

    // --- 1. Load All Employees ---
    async function loadEmployees() {
        employeeTableContainer.innerHTML = '<p>Loading employees...</p>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/employees`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! Status: ${response.status}`);
            }

            if (data && data.length > 0) {
                let tableHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Role</th>
                                <th>Salary</th>
                                <th>Shelter ID</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                data.forEach(employee => {
                    const salary = parseFloat(employee.salary).toFixed(2);
                    tableHtml += `
                        <tr data-id="${employee.employee_id}">
                            <td>${employee.employee_id}</td>
                            <td>${employee.name}</td>
                            <td>${employee.role}</td>
                            <td>$${salary}</td>
                            <td>${employee.shelter_id}</td>
                            <td class="actions">
                                <button class="btn-update-salary" data-id="${employee.employee_id}" data-name="${employee.name}" data-current-salary="${salary}">Update Salary</button>
                            </td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                employeeTableContainer.innerHTML = tableHtml;

            } else {
                employeeTableContainer.innerHTML = '<p>No employees found. Add one above!</p>';
            }
        } catch (error) {
            console.error('Error fetching employees:', error);
            employeeTableContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    // --- 2. Add New Employee (Form Submit) ---
    addEmployeeForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(addEmployeeForm);
        const employeeData = Object.fromEntries(formData.entries());
        
        employeeData.salary = parseFloat(employeeData.salary);
        employeeData.shelter_id = parseInt(employeeData.shelter_id);

        try {
            const response = await fetch(`${API_BASE_URL}/employees`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(employeeData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `Error: ${response.status}`);
            }

            showResult(formResult, `Success! New employee added with ID: ${result.new_employee_id}`, false);
            addEmployeeForm.reset();
            loadEmployees();

        } catch (error) {
            console.error('Error adding employee:', error);
            showResult(formResult, `Error: ${error.message}`, true);
        }
    });


    // --- 3. Update Salary (TESTS TRIGGER) ---
    employeeTableContainer.addEventListener('click', async (event) => {
        
        const target = event.target;
        const employeeId = target.dataset.id;
        const employeeName = target.dataset.name;
        const currentSalary = target.dataset.currentSalary;

        if (target.classList.contains('btn-update-salary')) {
            
            const newSalaryInput = prompt(`Enter new salary for ${employeeName} (Current: $${currentSalary}):`);
            
            if (!newSalaryInput || newSalaryInput.trim() === '') {
                return;
            }

            const newSalary = parseFloat(newSalaryInput);

            if (isNaN(newSalary) || newSalary <= 0) {
                alert("Invalid salary amount.");
                return;
            }

            const updateData = { salary: newSalary };

            try {
                const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/salary`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updateData)
                });
                
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Salary update failed');
                }
                
                alert(`Salary updated successfully! This change was logged in the SalaryChangeLog table.`);
                loadEmployees(); // Table refresh karo

            } catch (error) {
                console.error('Error updating salary:', error);
                alert(`Error updating salary: ${error.message}`);
            }
        }
    });

    // Page load hote hi employees ko load kar lo
    loadEmployees();
});