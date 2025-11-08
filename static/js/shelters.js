document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // Form elements
    const addShelterForm = document.getElementById('add-shelter-form');
    const formResult = document.getElementById('form-result');
    const shelterTableContainer = document.getElementById('shelter-table-container');

    // Helper functions
    function showResult(element, message, isError = false) {
        element.textContent = message;
        element.className = isError ? 'result-message error-message' : 'result-message success-message';
        setTimeout(() => {
            element.textContent = '';
            element.className = 'result-message';
        }, 5000);
    }

    // --- 1. Load All Shelters ---
    async function loadShelters() {
        shelterTableContainer.innerHTML = '<p>Loading shelters...</p>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/shelters`);
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
                                <th>Address</th>
                                <th>Capacity</th>
                                <th>Occupancy</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                data.forEach(shelter => {
                    const occupancyClass = (shelter.current_occupancy / shelter.capacity) > 0.8 ? 'text-warning' : '';

                    tableHtml += `
                        <tr data-id="${shelter.shelter_id}">
                            <td>${shelter.shelter_id}</td>
                            <td>${shelter.name}</td>
                            <td>${shelter.location}</td> <!-- Schema mein 'location' hai -->
                            <td>${shelter.capacity}</td>
                            <td><span class="${occupancyClass}">${shelter.current_occupancy}</span></td>
                            <td class="actions">
                                <button class="btn-delete" data-id="${shelter.shelter_id}">Delete</button>
                            </td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                shelterTableContainer.innerHTML = tableHtml;

            } else {
                shelterTableContainer.innerHTML = '<p>No shelters found. Add one above!</p>';
            }
        } catch (error) {
            console.error('Error fetching shelters:', error);
            shelterTableContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    // --- 2. Add New Shelter (Form Submit) ---
    addShelterForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(addShelterForm);
        const shelterData = Object.fromEntries(formData.entries());
        
        // Capacity ko number mein convert karo
        shelterData.capacity = parseInt(shelterData.capacity);

        try {
            const response = await fetch(`${API_BASE_URL}/shelters`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(shelterData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `Error: ${response.status}`);
            }

            showResult(formResult, `Success! New shelter added with ID: ${result.new_shelter_id}`, false);
            addShelterForm.reset();
            loadShelters(); // Table ko refresh karo

        } catch (error) {
            console.error('Error adding shelter:', error);
            showResult(formResult, `Error: ${error.message}`, true);
        }
    });


    // --- 3. Delete Shelter ---
    shelterTableContainer.addEventListener('click', async (event) => {
        
        const target = event.target;
        const shelterId = target.dataset.id;

        if (target.classList.contains('btn-delete')) { // Class name check
            
            if (!confirm(`Are you sure you want to delete Shelter ID ${shelterId}? \n\n(Note: Database will block deletion if employees/animals are still assigned - this tests the trigger.)`)) {
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/shelters/${shelterId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Delete failed');
                }

                alert(`Shelter ID ${shelterId} deleted successfully.`);
                loadShelters(); // Table refresh karo

            } catch (error) {
                console.error('Error deleting shelter:', error);
                alert(`Error: ${error.message}`);
            }
        }
    });

    // Page load hote hi shelters ko load kar lo
    loadShelters();
});