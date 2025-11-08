// Pehle, hum 'DOMContentLoaded' event ka intezaar karenge.
// Iska matlab hai ki JavaScript, HTML load hone ke baad hi chalega.
document.addEventListener('DOMContentLoaded', () => {

    // Apne API server ka base URL (yeh wahi hai jo app.py chala raha hai)
    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // HTML elements ko select kar rahe hain
    const loadAnimalsBtn = document.getElementById('loadAnimalsBtn');
    const dataContainer = document.getElementById('data-container');
    const adoptBtn = document.getElementById('adoptBtn');
    const adoptResult = document.getElementById('adopt-result');

    // Helper function (Error message dikhane ke liye)
    function showError(element, message) {
        element.innerHTML = `<div class="error-message">${message}</div>`;
    }

    // Helper function (Success message dikhane ke liye)
    function showSuccess(element, message) {
        element.innerHTML = `<div class="success-message">${message}</div>`;
    }


    // --- 1. Load Animals Button ---
    loadAnimalsBtn.addEventListener('click', () => {
        // Data container ko clear karo aur 'Loading...' dikhao
        dataContainer.innerHTML = '<p>Loading animals...</p>';

        // API ko call karo: GET /api/animals?status=Available
        fetch(`${API_BASE_URL}/animals?status=Available`)
            .then(response => {
                // Agar response OK nahi hai, toh error throw karo
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json(); // JSON data ko parse karo
            })
            .then(data => {
                // Data container ko clear karo
                dataContainer.innerHTML = ''; 

                if (data && data.length > 0) {
                    // Har animal ke liye ek card banao
                    data.forEach(animal => {
                        const animalCard = document.createElement('div');
                        animalCard.className = 'animal-card';
                        animalCard.innerHTML = `
                            <h3>${animal.name} (ID: ${animal.animal_id})</h3>
                            <p>Species: ${animal.species} (${animal.breed})</p>
                            <p>Age: ${animal.age} | Gender: ${animal.gender}</p>
                            <p>Status: <span class="status-available">${animal.status}</span></p>
                            <p>Shelter ID: ${animal.shelter_id}</p>
                        `;
                        dataContainer.appendChild(animalCard);
                    });
                } else {
                    // Agar koi 'Available' animal nahi mila
                    dataContainer.innerHTML = '<p>No available animals found.</p>';
                }
            })
            .catch(error => {
                // Agar network ya fetch mein koi error aaye
                console.error('Error fetching animals:', error);
                showError(dataContainer, `Error fetching animals: ${error.message}`);
            });
    });


    // --- 2. Test Adopt Button ---
    adoptBtn.addEventListener('click', () => {
        adoptResult.innerHTML = '<p>Attempting adoption...</p>';

        // Yeh data humari insertion.py file ke hisaab se hai
        const adoptionData = {
            animal_id: 3,   // Animal: 'Charlie' (from insertion.py)
            adopter_id: 2,  // Adopter: 'Jane Smith' (from insertion.py)
            employee_id: 1  // Employee: 'Amit Sharma' (from insertion.py)
        };

        // API ko call karo: POST /api/adopt
        fetch(`${API_BASE_URL}/adopt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(adoptionData), // Data ko JSON string mein badlo
        })
        .then(response => response.json().then(data => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
            if (ok) {
                // Success!
                console.log('Adoption successful:', data);
                // Yeh aapke trigger ka test hai!
                // Ab 'Load Animals' button dubara click karoge toh 'Charlie (ID 3)' nahi dikhega.
                showSuccess(adoptResult, `Adoption Successful! (Log ID: ${data.adoption_details.adoption_id})`);
            } else {
                // Agar API se error aaye (jaise "Animal already adopted")
                // Yeh error aapke trigger/procedure se aa raha hai
                throw new Error(data.error || 'Adoption failed.');
            }
        })
        .catch(error => {
            // Agar network ya fetch mein koi error aaye
            console.error('Error during adoption:', error);
            showError(adoptResult, `Adoption Failed: ${error.message}`);
        });
    });

});