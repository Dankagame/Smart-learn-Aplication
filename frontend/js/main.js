/**
 * SmartLearn (BrightMinds) - Main JavaScript (Vanilla JS)
 * Handles API calls, authentication states, and UI interactions.
 */

// Configuration for Backend REST API (FastAPI)
const API_CONFIG = {
  BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : '/api',
  STORAGE_KEYS: {
    TOKEN: 'smartlearn_token',
    USER: 'smartlearn_user'
  }
};

/**
 * Standard fetch wrapper that handles JSON formatting, headers,
 * and Bearer token injection.
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = localStorage.getItem(API_CONFIG.STORAGE_KEYS.TOKEN);
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMsg = data.detail || data.message || `Erreur HTTP ${response.status}`;
      throw new Error(errorMsg);
    }

    return { success: true, data };
  } catch (error) {
    console.warn(`[API] Appel vers ${endpoint} échoué:`, error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Authentication state helper
 */
const Auth = {
  getToken() {
    return localStorage.getItem(API_CONFIG.STORAGE_KEYS.TOKEN);
  },

  getUser() {
    const raw = localStorage.getItem(API_CONFIG.STORAGE_KEYS.USER);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  setUserSession(token, user) {
    localStorage.setItem(API_CONFIG.STORAGE_KEYS.TOKEN, token);
    localStorage.setItem(API_CONFIG.STORAGE_KEYS.USER, JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem(API_CONFIG.STORAGE_KEYS.TOKEN);
    localStorage.removeItem(API_CONFIG.STORAGE_KEYS.USER);
    window.location.href = 'login.html';
  }
};

/**
 * Initialize navbar state based on authentication
 */
function initNavbar() {
  const user = Auth.getUser();
  const contactBtn = document.querySelector('.btn-contact');
  const navContainer = document.querySelector('.navbar-nav');

  if (user && contactBtn) {
    // If logged in, update CTA to show Dashboard / Logout
    contactBtn.textContent = 'Dashboard';
    contactBtn.href = 'dashboard.html';

    // Add user pill to nav
    if (navContainer && !document.getElementById('nav-user-greeting')) {
      const userItem = document.createElement('li');
      userItem.className = 'nav-item d-flex align-items-center ms-lg-2';
      userItem.id = 'nav-user-greeting';
      userItem.innerHTML = `
        <span class="badge bg-purple-subtle text-dark px-3 py-2 rounded-pill">
          👤 ${user.username || user.name || 'Utilisateur'}
        </span>
      `;
      navContainer.appendChild(userItem);
    }
  }
}

// Auto-run on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
});
