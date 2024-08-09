async function getRecommendations() {
    const movieInput = document.getElementById('movieInput').value;
    const recommendationsDiv = document.getElementById('recommendations');
    
    recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';

    try {
        const response = await fetch('http://127.0.0.1:5000/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ movie_name: movieInput })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const recommendations = await response.json();
        
        if (recommendations.length === 0) {
            recommendationsDiv.innerHTML = "<p>No recommendations found</p>";
            return;
        }

        const recommendationsHtml = recommendations.map(movie => `
            <div class="movie">
                <img src="https://image.tmdb.org/t/p/w500${movie.poster_path}" alt="${movie.title}" class="poster">
                <div class="movie-content">
                    <h3>${movie.title}</h3>
                    <p><strong>Release Date:</strong> ${movie.release_date}</p>
                    <p><strong>Overview:</strong> ${movie.overview}</p>
                    <p><strong>Cast:</strong> ${movie.cast.join(', ')}</p>
                </div>
            </div>
        `).join('');

        recommendationsDiv.innerHTML = recommendationsHtml;
    } catch (error) {
        console.error('Error:', error);
        recommendationsDiv.innerHTML = "<p>An error occurred while fetching recommendations</p>";
    }
}

// Add event listener for Enter key press
document.getElementById('movieInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        getRecommendations();
    }
});