// Utility functions for API calls and notifications
const API_BASE = ''; // Update this if your API is hosted elsewhere

async function fetchJson(endpoint, options = {}) {
    const url = API_BASE + endpoint;
    
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    
    const config = {
        method: options.method || 'GET',
        headers,
        ...(options.body ? { body: JSON.stringify(options.body) } : {})
    };
    
    const response = await fetch(url, config);
    
    if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        error.status = response.status;
        throw error;
    }
    
    // For DELETE requests that might not return content
    if (response.status === 204) {
        return null;
    }
    
    return await response.json();
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

// Make these functions available globally
window.fetchJson = fetchJson;
window.showSuccess = showSuccess;
window.showError = showError;
