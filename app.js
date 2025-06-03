document.addEventListener('DOMContentLoaded', function() {
    // Test API button
    const testButton = document.createElement('button');
    testButton.textContent = 'Test API';
    testButton.className = 'bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600';
    testButton.onclick = testAPI;
    document.body.appendChild(testButton);

    // Display area for API results
    const resultDiv = document.createElement('div');
    resultDiv.className = 'mt-4 p-4 bg-gray-100 rounded-lg';
    document.body.appendChild(resultDiv);

    function testAPI() {
        // Test stats endpoint
        fetch('https://your-replit-username.replit.app:8081/api/stats')
            .then(response => response.json())
            .then(data => {
                resultDiv.innerHTML = `<p>Stats Response: ${JSON.stringify(data, null, 2)}</p>`;
            })
            .catch(error => {
                resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
            });

        // Test adding a quote
        const testQuote = {
            content: "Believe you can and you're halfway there. - Theodore Roosevelt",
            author: "Theodore Roosevelt"
        };

        fetch('https://your-replit-username.replit.app:8081/api/add-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testQuote)
        })
        .then(response => response.json())
        .then(data => {
            resultDiv.innerHTML += `<p>Quote Response: ${JSON.stringify(data, null, 2)}</p>`;
        })
        .catch(error => {
            resultDiv.innerHTML += `<p>Error: ${error.message}</p>`;
        });
    }
});