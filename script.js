document.addEventListener('DOMContentLoaded', function() {
    const favoritesForm = document.getElementById('favorites-form');
    const favoritesContainer = document.getElementById('favorites-container');
    const addMoreBtn = document.getElementById('add-more-btn');
    const generateBtn = document.getElementById('generate-btn');
    const loadingDiv = document.getElementById('loadingDiv');
    const recommendationsDiv = document.getElementById('recommendations');
    const apiKey = '34f84a38';  // OMDb API key
    // Event listener for "Add More" button
    addMoreBtn.addEventListener('click', function() {
        const newInputContainer = document.createElement('div');
        newInputContainer.classList.add('input-container');
        newInputContainer.style.display = 'flex'; // Add this line

        const newInput = document.createElement('input');
        newInput.type = 'text';
        newInput.name = 'favorite';
        newInput.placeholder = 'Favorite Movie/Series';
        newInputContainer.appendChild(newInput);

        // Add remove button for the new input field
        const removeBtn = document.createElement('button');
        removeBtn.textContent = '-';
        removeBtn.classList.add('remove-btn'); // This line uses the remove-btn class
        removeBtn.addEventListener('click', function() {
            newInputContainer.remove();
        });
        newInputContainer.appendChild(removeBtn);

        favoritesContainer.appendChild(newInputContainer);

        // Bind autocomplete functionality to the new input field
        setupAutocomplete(newInput);
    });

    // Keydown event listener for "Enter" key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent form submission
            addMoreBtn.click(); // Trigger the click event of the "Add More" button
            clearAutocompleteSuggestions();

            // Move cursor to the next input field
            const inputFields = document.querySelectorAll('.input-container input');
            const lastInputField = inputFields[inputFields.length - 1];
            lastInputField.focus();
        }
    });
    // Event listener for form submission
    favoritesForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const favorites = Array.from(favoritesForm.elements['favorite']).map(input => input.value.trim()).filter(Boolean);
        if (favorites.length === 0 && favoritesForm.elements['favorite'].value.trim() === '') {
            alert('Please enter at least one favorite movie/series.');
            return;
        }
        generateBtn.disabled = true;  // Disable button
        generateRecommendations(favorites);
    });
    // Setup autocomplete for the initial existing input
    setupAutocomplete(document.getElementById('favorite'));
    // Function to generate recommendations
    function generateRecommendations(favorites) {
        const requestBody = { favorites };

        // Clear previous recommendations
        recommendationsDiv.innerHTML = '';
        
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
            let html = `<h2>🎦Movies</h2>${generateHtmlForCategory(dataJson.movies)}<br>
                        <h2>📺TV Series</h2>${generateHtmlForCategory(dataJson.tvSeries)}`;

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
        const emojis = ["🎬", "🍿", "🎥", "🎞️", "🎦"]; // Add more movie-related emojis if needed

        items.forEach((item, index) => {
            const emoji = emojis[index % emojis.length]; // Use modulo operator to cycle through emojis
            html += `<p>${emoji} <a href="${item.imdb}" target="_blank">${item.title}</a> - ${item.description}</p>`;
        });
        return html;
    }
    // Function to clear autocomplete suggestions
    function clearAutocompleteSuggestions() {
        const autocompleteContainers = document.querySelectorAll('.autocomplete-container');
        autocompleteContainers.forEach(container => container.remove());
    }

    // Function to display autocomplete suggestions
    function showAutocompleteSuggestions(input, suggestions) {
        clearAutocompleteSuggestions();
        
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'autocomplete-container';

        suggestions.forEach(suggestion => {
            const suggestionDiv = document.createElement('div');
            suggestionDiv.className = 'autocomplete-item';
            suggestionDiv.innerText = suggestion;
            suggestionDiv.addEventListener('click', () => {
                input.value = suggestion;
                clearAutocompleteSuggestions();
            });
            suggestionsContainer.appendChild(suggestionDiv);
        });
        
        // input.parentNode.appendChild(suggestionsContainer);
            // Append the suggestions container below the "Add More" button
        favoritesContainer.appendChild(suggestionsContainer);
    }

    // Function to fetch autocomplete suggestions from the OMDb API
    function fetchSuggestions(inputElement) {
        const searchTerm = inputElement.value.trim();
        if(searchTerm.length > 2) { // Only fetch if the input length is 3 or more
            fetch(`https://www.omdbapi.com/?s=${encodeURIComponent(searchTerm)}&apikey=${apiKey}`)
            .then(response => response.json())
            .then(data => {
                if(data.Search) {
                    showAutocompleteSuggestions(inputElement, data.Search.map(m => m.Title));
                }
            }).catch(error => {
                console.error(error);
                clearAutocompleteSuggestions();
            });
        } else {
            clearAutocompleteSuggestions();
        }
    }

    // Setup autocomplete for an input element
    function setupAutocomplete(inputElement) {
        inputElement.addEventListener('input', () => fetchSuggestions(inputElement));
        inputElement.addEventListener('focus', () => fetchSuggestions(inputElement));
        inputElement.addEventListener('blur', () => {
            // Delay clearing the suggestions so we can click them
            setTimeout(() => clearAutocompleteSuggestions(), 300);
        });
    }
});
