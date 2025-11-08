document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // Form elements
    const addAnimalForm = document.getElementById('add-animal-form');
    const formResult = document.getElementById('form-result');

    // Table elements
    const loadAllAnimalsBtn = document.getElementById('loadAllAnimalsBtn');
    const animalTableContainer = document.getElementById('animal-table-container');

    // Helper function (Result message dikhane ke liye)
    function showResult(element, message, isError = false) {
        element.textContent = message;
        element.className = isError ? 'result-message error-message' : 'result-message success-message';
        // 5 second baad message gayab
        setTimeout(() => {
            element.textContent = '';
            element.className = 'result-message';
        }, 5000);
    }

    // --- 1. Load All Animals ---
    async function loadAnimals() {
        animalTableContainer.innerHTML = '<p>Loading animals...</p>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/animals`);
            const data = await response.json();
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            if (data && data.length > 0) {
                // Table create karo
                let tableHtml = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Species/Breed</th>
                                <th>Age/Gender</th>
                                <th>Status</th>
                                <th>Shelter ID</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                // Har animal ke liye ek row
                data.forEach(animal => {
                    // Check ki status adopted ya available hai
                    const statusClass = animal.status.toLowerCase().includes('adopted') ? 'status-adopted' : 'status-available';
                    
                    tableHtml += `
                        <tr data-id="${animal.animal_id}">
                            <td>${animal.animal_id}</td>
                            <td>${animal.name}</td>
                            <td>${animal.species} / ${animal.breed}</td>
                            <td>${animal.age} yrs / ${animal.gender}</td>
                            <td>
                                <span class="${statusClass}">${animal.status}</span>
                            </td>
                            <td>${animal.shelter_id}</td>
                            <td class="actions">
                                <!-- Buttons ke 'class' attributes theek kiye gaye hain -->
                                <button class="btn-update" data-id="${animal.animal_id}" data-name="${animal.name}">Update</button>
                                <button class="btn-delete" data-id="${animal.animal_id}">Delete</button>
                            </td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                animalTableContainer.innerHTML = tableHtml;

            } else {
                animalTableContainer.innerHTML = '<p>No animals found in the database.</p>';
            }
        } catch (error) {
            console.error('Error fetching animals:', error);
            animalTableContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }
    
    // Button par click karke function call karo
    loadAllAnimalsBtn.addEventListener('click', loadAnimals);


    // --- 2. Add New Animal (Form Submit) ---
    addAnimalForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(addAnimalForm);
        const animalData = Object.fromEntries(formData.entries());

        // 'status' ko manually set karo for new animals
        animalData.status = 'Available';
        // Capacity ko number mein convert karo
        animalData.age = parseInt(animalData.age);
        animalData.shelter_id = parseInt(animalData.shelter_id);


        // API ko call karo: POST /api/animals
        try {
            const response = await fetch(`${API_BASE_URL}/animals`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(animalData)
            });

            const result = await response.json();

            if (!response.ok) {
                // Agar trigger se error aaye (jaise "Shelter is full")
                throw new Error(result.error || `Error: ${response.status}`);
            }

            // Success
            showResult(formResult, `Success! New animal added with ID: ${result.new_animal_id}`, false);
            addAnimalForm.reset(); // Form ko clear karo
            loadAnimals(); // Table ko refresh karo

        } catch (error) {
            console.error('Error adding animal:', error);
            showResult(formResult, `Error: ${error.message}`, true);
        }
    });


    // --- 3. Delete / Update (Event Delegation) ---
    animalTableContainer.addEventListener('click', async (event) => {
        
        const target = event.target;
        const animalId = target.dataset.id;
        const animalName = target.dataset.name;

        // --- Agar DELETE button click hua (FIXED) ---
        if (target.classList.contains('btn-delete')) {
            if (!confirm(`Are you sure you want to delete ${animalName} (ID ${animalId})?`)) {
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/animals/${animalId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Delete failed');
                }

                alert(`${animalName} (ID ${animalId}) deleted successfully.`);
                loadAnimals(); // Table refresh karo

            } catch (error) {
                console.error('Error deleting animal:', error);
                alert(`Error deleting animal: ${error.message}`);
            }
        }

        // --- Agar UPDATE button click hua (FIXED) ---
        if (target.classList.contains('btn-update')) {
            
            const newName = prompt(`Enter new name for Animal ID ${animalId}:`, animalName);
            
            if (!newName || newName.trim() === '' || newName === animalName) {
                return; // User ne cancel kar diya, ya khaali naam daala, ya naam change nahi kiya
            }

            const updateData = { name: newName };

            try {
                const response = await fetch(`${API_BASE_URL}/animals/${animalId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updateData)
                });
                
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Update failed');
                }
                
                alert(`Animal ID ${animalId} name updated to ${newName}.`);
                loadAnimals(); // Table refresh karo

            } catch (error) {
                console.error('Error updating animal:', error);
                alert(`Error updating animal: ${error.message}`);
            }
        }
    });

    // Page load hote hi animals ko load kar lo
    loadAnimals();
});