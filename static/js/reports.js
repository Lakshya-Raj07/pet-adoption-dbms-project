document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // Report containers
    const report1Container = document.getElementById('report1-container');
    const report2Container = document.getElementById('report2-container');
    const report3Container = document.getElementById('report3-container');

    /**
     * Helper function to fetch data and build a table
     * @param {string} url - The API endpoint to fetch
     * @param {HTMLElement} container - The container to inject the table into
     * @param {string[]} headers - Array of header names (e.g., ['Name', 'Count'])
     * @param {string[]} keys - Array of keys from the JSON object (e.g., ['name', 'animal_count'])
     */
    async function loadReport(url, container, headers, keys) {
        container.innerHTML = '<p>Loading...</p>';
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            if (data && data.length > 0) {
                // Table create karo
                let tableHtml = '<table class="data-table"><thead><tr>';
                headers.forEach(header => {
                    tableHtml += `<th>${header}</th>`;
                });
                tableHtml += '</tr></thead><tbody>';

                // Har item ke liye ek row
                data.forEach(item => {
                    tableHtml += '<tr>';
                    keys.forEach(key => {
                        // Agar key 'salary' ya 'amount' hai, toh usse format karo
                        if (key === 'salary' || key === 'amount') {
                            tableHtml += `<td>${parseFloat(item[key]).toFixed(2)}</td>`;
                        } else {
                            tableHtml += `<td>${item[key]}</td>`;
                        }
                    });
                    tableHtml += '</tr>';
                });

                tableHtml += '</tbody></table>';
                container.innerHTML = tableHtml;

            } else {
                container.innerHTML = '<p>No data found for this report.</p>';
            }
        } catch (error) {
            console.error(`Error fetching report from ${url}:`, error);
            container.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
        }
    }

    // --- Saare reports ko page load par call karo ---
    
    // Report 1: Shelter Occupancy
    loadReport(
        `${API_BASE_URL}/reports/shelter-occupancy`,
        report1Container,
        ['Shelter Name', 'Capacity', 'Occupancy (Trigger)', 'Calculated Count (Available)'],
        ['name', 'capacity', 'current_occupancy', 'calculated_animal_count']
    );

    // Report 2: Employees Above Average
    loadReport(
        `${API_BASE_URL}/reports/employees-above-average`,
        report2Container,
        ['Employee Name', 'Role', 'Salary'],
        ['name', 'role', 'salary']
    );

    // Report 3: Multi-Adopters
    loadReport(
        `${API_BASE_URL}/reports/multi-adopters`,
        report3Container,
        ['First Name', 'Last Name', 'Phone', 'Total Adoptions'],
        ['first_name', 'last_name', 'phone', 'total_adoptions']
    );
});