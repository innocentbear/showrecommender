// Blog JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize authentication for blog
    initializeAuth();
    
    // Setup blog-specific functionality
    setupBlogFeatures();
});

function setupBlogFeatures() {
    // Blog post click handlers
    document.querySelectorAll('.blog-post, .featured-article').forEach(post => {
        post.addEventListener('click', function() {
            // In a real application, this would navigate to the full article
            showNotification('Full article feature coming soon!', 'info');
        });
    });
    
    // Category click handlers
    document.querySelectorAll('.category-list a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.textContent.trim();
            showNotification(`Showing ${category} posts...`, 'info');
        });
    });
    
    // Popular post click handlers
    document.querySelectorAll('.popular-post').forEach(post => {
        post.addEventListener('click', function() {
            showNotification('Opening article...', 'info');
        });
    });
    
    // Read more button
    const readMoreBtn = document.querySelector('.read-more-btn');
    if (readMoreBtn) {
        readMoreBtn.addEventListener('click', function() {
            showNotification('Full article feature coming soon!', 'info');
        });
    }
}

// Placeholder function that would normally fetch articles from an API
async function loadBlogArticles(category = 'all') {
    // This would fetch articles from your backend
    console.log(`Loading articles for category: ${category}`);
}