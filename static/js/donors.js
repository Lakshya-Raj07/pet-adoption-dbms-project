document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // Form elements
    const addDonorForm = document.getElementById('add-donor-form');
    const formResult = document.getElementById('form-result');

    // Table elements
    const loadDonorsBtn = document.getElementById('loadDonorsBtn');
    const donorTableContainer = document.getElementById('donor-table-container');

    // Helper function (Error/Success message dikhane ke liye)
    function showResult(element, message, isError = false) {
        element.textContent = message;
        element.className = isError ? 'result-message error-message' : 'result-message success-message';
        // 5 second baad message gayab
        setTimeout(() => {
            element.textContent = '';
            element.className = 'result-message';
        }, 5000);
    }

    // --- 1. Load All Donors ---
    async function loadDonors() {
        donorTableContainer.innerHTML = '<p>Loading donors...</p>';
        
        try {
            // Humara naya API route
            const response = await fetch(`${API_BASE_URL}/donors/details`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            const donors = await response.json();
            
            if (donors && donors.length > 0) {
                // Table create karo
                let tableHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Donor ID</th>
                                <th>Customer ID</th>
                                <th>First Name</th>
                                <th>Last Name</th>
                                <th>Phone</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                // Har donor ke liye ek row
                donors.forEach(donor => {
                    tableHtml += `
                        <tr>
                            <td>${donor.donor_id}</td>
                            <td>${donor.customer_id}</td>
                            <td>${donor.first_name}</td>
                            <td>${donor.last_name}</td>
                            <td>${donor.phone}</td>
                            <td>${parseFloat(donor.amount).toFixed(2)}</td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                donorTableContainer.innerHTML = tableHtml;

            } else {
                donorTableContainer.innerHTML = '<p>No donors found in the database.</p>';
            }
        } catch (error) {
            console.error('Error fetching donors:', error);
            donorTableContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    // Button par click karke function call karo
    loadDonorsBtn.addEventListener('click', loadDonors);


    // --- 2. Add New Donor (Form Submit) ---
    addDonorForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Form ko default submit se roko

        // Form data ko object mein convert karo
        const formData = new FormData(addDonorForm);
        const donorData = Object.fromEntries(formData.entries());

        // API ko call karo: POST /api/donors
        try {
            const response = await fetch(`${API_BASE_URL}/donors`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(donorData)
            });

            const result = await response.json();

            if (!response.ok) {
                // Agar procedure se error aaye (Transaction rollback)
                throw new Error(result.error || `Error: ${response.status}`);
            }

            // Success
            showResult(formResult, `Success! New donor added. Customer ID: ${result.customer_id}, Donor ID: ${result.donor_id}`, false);
            addDonorForm.reset(); // Form ko clear karo
            loadDonors(); // Table ko refresh karo

        } catch (error) {
            console.error('Error adding donor:', error);
            showResult(formResult, `Error: ${error.message}`, true);
        }
    });

    // Page load hote hi donors ko load kar lo
    loadDonors();
});