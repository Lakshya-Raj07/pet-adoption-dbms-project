document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // Form elements
    const addAdopterForm = document.getElementById('add-adopter-form');
    const formResult = document.getElementById('form-result');

    // Table elements
    const loadAdoptersBtn = document.getElementById('loadAdoptersBtn');
    const adopterTableContainer = document.getElementById('adopter-table-container');

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

    // --- 1. Load All Adopters ---
    async function loadAdopters() {
        adopterTableContainer.innerHTML = '<p>Loading adopters...</p>';
        
        try {
            // Humara API route
            const response = await fetch(`${API_BASE_URL}/adopters/details`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            const adopters = await response.json();
            
            if (adopters && adopters.length > 0) {
                // Table create karo
                let tableHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Adopter ID</th>
                                <th>Customer ID</th>
                                <th>First Name</th>
                                <th>Last Name</th>
                                <th>Phone</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                // Har adopter ke liye ek row
                adopters.forEach(adopter => {
                    tableHtml += `
                        <tr>
                            <td>${adopter.adopter_id}</td>
                            <td>${adopter.customer_id}</td>
                            <td>${adopter.first_name}</td>
                            <td>${adopter.last_name}</td>
                            <td>${adopter.phone}</td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                adopterTableContainer.innerHTML = tableHtml;

            } else {
                adopterTableContainer.innerHTML = '<p>No adopters found in the database.</p>';
            }
        } catch (error) {
            console.error('Error fetching adopters:', error);
            adopterTableContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    // Button par click karke function call karo
    loadAdoptersBtn.addEventListener('click', loadAdopters);


    // --- 2. Add New Adopter (Form Submit) ---
    addAdopterForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Form ko default submit se roko

        // Form data ko object mein convert karo
        const formData = new FormData(addAdopterForm);
        const adopterData = Object.fromEntries(formData.entries());

        // API ko call karo: POST /api/adopters
        try {
            const response = await fetch(`${API_BASE_URL}/adopters`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(adopterData)
            });

            const result = await response.json();

            if (!response.ok) {
                // Agar procedure se error aaye (Transaction rollback)
                throw new Error(result.error || `Error: ${response.status}`);
            }

            // Success
            showResult(formResult, `Success! New adopter added. Customer ID: ${result.customer_id}, Adopter ID: ${result.adopter_id}`, false);
            addAdopterForm.reset(); // Form ko clear karo
            loadAdopters(); // Table ko refresh karo

        } catch (error) {
            console.error('Error adding adopter:', error);
            showResult(formResult, `Error: ${error.message}`, true);
        }
    });

    // Page load hote hi adopters ko load kar lo
    loadAdopters();
});