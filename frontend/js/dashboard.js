// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    checkAuthStatus();
    
    // Load dashboard data
    loadDashboardData();
    
    // Event listeners
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('view-watchlist-btn').addEventListener('click', showWatchlistModal);
    document.getElementById('upgrade-btn').addEventListener('click', showPremiumUpgrade);
    document.getElementById('premium-cta').addEventListener('click', showPremiumUpgrade);
    
    // Modal functionality
    setupModalHandlers();
});

function checkAuthStatus() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = '/';
        return;
    }
    
    document.getElementById('dashboard-username').textContent = user.username;
    document.getElementById('username-display').textContent = user.username;
    
    if (user.is_premium) {
        document.getElementById('premium-status').textContent = 'Premium';
        document.getElementById('upgrade-btn').style.display = 'none';
    }
}

async function loadDashboardData() {
    try {
        // Load watchlist count
        const watchlistResponse = await fetch(`${baseUrl}/api/watchlist`, {
            credentials: 'include'
        });
        
        if (watchlistResponse.ok) {
            const watchlistData = await watchlistResponse.json();
            document.getElementById('watchlist-count').textContent = watchlistData.watchlist.length;
            
            // Display recent watchlist items
            displayRecentWatchlist(watchlistData.watchlist.slice(0, 6));
        }
        
        // Load recommendations count (would need a new API endpoint)
        document.getElementById('recommendations-count').textContent = '0'; // Placeholder
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function displayRecentWatchlist(items) {
    const container = document.getElementById('recent-watchlist');
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = '<p class="empty-state">No items in your watchlist yet. <a href="/">Get recommendations</a> to start building your list!</p>';
        return;
    }
    
    items.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'watchlist-item';
        itemElement.innerHTML = `
            <img src="${item.poster_url || 'https://via.placeholder.com/200x300?text=No+Image'}" alt="${item.title}">
            <div class="watchlist-item-content">
                <h4>${item.title}</h4>
                <p>${item.type}</p>
                <button class="remove-watchlist-btn" onclick="removeFromWatchlist(${item.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        container.appendChild(itemElement);
    });
}

async function showWatchlistModal() {
    try {
        const response = await fetch(`${baseUrl}/api/watchlist`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            displayFullWatchlist(data.watchlist);
            document.getElementById('watchlist-modal').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading watchlist:', error);
        showNotification('Error loading watchlist', 'error');
    }
}

function displayFullWatchlist(items) {
    const container = document.getElementById('watchlist-content');
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = '<p class="empty-state">Your watchlist is empty. Start adding movies and shows!</p>';
        return;
    }
    
    items.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'watchlist-item';
        itemElement.innerHTML = `
            <img src="${item.poster_url || 'https://via.placeholder.com/200x300?text=No+Image'}" alt="${item.title}">
            <div class="watchlist-item-content">
                <h4>${item.title}</h4>
                <p>${item.type}</p>
                <p class="added-date">Added: ${new Date(item.added_at).toLocaleDateString()}</p>
                <button class="remove-watchlist-btn" onclick="removeFromWatchlist(${item.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        container.appendChild(itemElement);
    });
}

async function removeFromWatchlist(itemId) {
    try {
        const response = await fetch(`${baseUrl}/api/watchlist/${itemId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            showNotification('Removed from watchlist', 'success');
            loadDashboardData(); // Refresh dashboard
            showWatchlistModal(); // Refresh modal if open
        } else {
            showNotification('Error removing item', 'error');
        }
    } catch (error) {
        console.error('Error removing from watchlist:', error);
        showNotification('Error removing item', 'error');
    }
}

function showPremiumUpgrade() {
    // This would integrate with a payment processor
    alert('Premium upgrade feature coming soon! Get unlimited recommendations, ad-free experience, and more for just $4.99/month.');
}

async function handleLogout() {
    try {
        const response = await fetch(`${baseUrl}/api/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            localStorage.removeItem('currentUser');
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

function setupModalHandlers() {
    // Close modal handlers
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // Click outside modal to close
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

function getCurrentUser() {
    return JSON.parse(localStorage.getItem('currentUser') || 'null');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}