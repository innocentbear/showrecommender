document.addEventListener('DOMContentLoaded', function() {
    const favoritesForm = document.getElementById('favorites-form');
    const favoritesContainer = document.getElementById('favorites-container');
    const addMoreBtn = document.getElementById('add-more-btn');
    const generateBtn = document.getElementById('generate-btn');
    const loadingDiv = document.getElementById('loadingDiv');
    const recommendationsDiv = document.getElementById('recommendations');

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
        generateBtn.disabled = true;  // Disable button
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
            generateBtn.disabled = false;
            
            // Parse response string into JSON
            const dataJson = JSON.parse(data.recommendations[0]);

            // Generate HTML for movies and TV series recommendations
            let html = `<h2>Movies</h2>${generateHtmlForCategory(dataJson.movies)}<br>
                        <h2>TV Series</h2>${generateHtmlForCategory(dataJson.tvSeries)}`;

            // Set HTML of `recommendationsDiv`
            recommendationsDiv.innerHTML = html;
        })
        .catch(error => {
            // Hide loading symbol if an error occurs
            loadingDiv.style.display = 'none';
            generateBtn.disabled = false;

            console.error('Error fetching recommendations:', error);
            recommendationsDiv.innerHTML = '<p>Failed to fetch recommendations. Please try again later.</p>';
        });
    }

    // Function to generate HTML for a category of recommendations
    function generateHtmlForCategory(items) {
        let html = "";
        items.forEach((item, index) => {
            html += `<p>${index+1}. <a href="${item.imdb}" target="_blank">${item.title}</a> - ${item.description}</p>`;
        });
        return html;
    }
});
