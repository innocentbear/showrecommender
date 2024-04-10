document.addEventListener('DOMContentLoaded', function() {
    const favoritesForm = document.getElementById('favorites-form');
    const favoritesContainer = document.getElementById('favorites-container');
    const addMoreBtn = document.getElementById('add-more-btn');
    const generateBtn = document.getElementById('generate-btn');
    const recommendationsDiv = document.getElementById('recommendations');
    const loadingDiv = document.getElementById('loadingDiv');

    // Event listener for "Add More" button
    addMoreBtn.addEventListener('click', function() {
        const newInput = document.createElement('input');
        newInput.type = 'text';
        newInput.name = 'favorite';
        newInput.placeholder = 'Favorite Movie/Series';
        favoritesContainer.appendChild(newInput);
    });

    // Event listener for form submission
    favoritesForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const favorites = Array.from(favoritesForm.elements['favorite']).map(input => input.value.trim()).filter(Boolean);
        if (favorites.length === 0) {
            alert('Please enter at least one favorite movie/series.');
            return;
        }
        generateRecommendations(favorites);
    });

    // Function to generate recommendations
    function generateRecommendations(favorites) {
        const requestBody = { favorites };

        // Show loading symbol before making the fetch request
        loadingDiv.style.display = 'block';

        // Make API call to backend server
        fetch('http://localhost:5000/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading symbol after getting the response
            loadingDiv.style.display = 'none';
        
            // Replace markdown syntax with HTML
            const boldReplaced = data.recommendations[0].replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");
            const linkReplaced = boldReplaced.replace(/\[(.*?)\]\((.*?)\)/g, "<a href='$2' target='_blank'>$1</a>");
            const recommendations = linkReplaced.replace(/\n/g, "<br>");
            // Set HTML of `recommendationsDiv`
            recommendationsDiv.innerHTML = '<h2>Recommended Movies/Series:</h2>' + recommendations;
        })
        .catch(error => {
            // Hide loading symbol if an error occurs
            loadingDiv.style.display = 'none';
            
            console.error('Error fetching recommendations:', error);
            recommendationsDiv.innerHTML = '<p>Failed to fetch recommendations. Please try again later.</p>';
        });
    }
});
