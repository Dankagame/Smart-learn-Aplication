/**
 * SmartLearn - API Client Helper (Vanilla JavaScript)
 * Fully compliant with Issue 13 and backend REST API specifications.
 * Endpoints: /auth/login, /auth/register, /auth/me, /courses, /quizzes, /health
 */

(function (window) {
  'use strict';

  // Backend base configuration
  const DEFAULT_BACKEND_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : '';

  const API_CONFIG = {
    BASE_URL: window.__API_BASE_URL__ || DEFAULT_BACKEND_URL,
    PREFIX: '', // Backend routes have no /api prefix
    STORAGE_KEYS: {
      TOKEN: 'smartlearn_token',
      USER: 'smartlearn_user'
    },
    TIMEOUT_MS: 8000
  };

  /**
   * Helper function for fetch() calls with timeout
   */
  async function fetchWithTimeout(resource, options = {}) {
    const { timeout = API_CONFIG.TIMEOUT_MS } = options;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(resource, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(id);
      return response;
    } catch (err) {
      clearTimeout(id);
      throw err;
    }
  }

  /**
   * Main fetch helper: apiRequest
   * @param {string} endpoint - API path (e.g. '/auth/login' or '/courses')
   * @param {object} options - Fetch options (method, headers, body)
   */
  async function apiRequest(endpoint, options = {}) {
    const base = API_CONFIG.BASE_URL;
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${base}${cleanEndpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(options.headers || {})
    };

    const token = localStorage.getItem(API_CONFIG.STORAGE_KEYS.TOKEN);
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetchWithTimeout(url, {
        ...options,
        headers
      });

      let data = {};
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        data = { message: text };
      }

      if (!response.ok) {
        let message = `HTTP error ${response.status}`;
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else if (Array.isArray(data.detail) && data.detail.length > 0) {
          message = data.detail.map(d => d.msg || d.message).join(', ');
        } else if (data.message) {
          message = data.message;
        }
        return {
          success: false,
          status: response.status,
          error: message,
          data
        };
      }

      return {
        success: true,
        status: response.status,
        data
      };
    } catch (err) {
      const isAbort = err.name === 'AbortError';
      const errorMessage = isAbort 
        ? 'Connection timed out. Backend is not reachable.'
        : (err.message || 'Network error');

      return {
        success: false,
        error: errorMessage,
        isNetworkError: true
      };
    }
  }

  // HTTP Verb helpers
  const http = {
    get: (endpoint, options = {}) => apiRequest(endpoint, { method: 'GET', ...options }),
    post: (endpoint, body, options = {}) => apiRequest(endpoint, {
      method: 'POST',
      body: typeof body === 'string' ? body : JSON.stringify(body),
      ...options
    }),
    put: (endpoint, body, options = {}) => apiRequest(endpoint, {
      method: 'PUT',
      body: typeof body === 'string' ? body : JSON.stringify(body),
      ...options
    }),
    delete: (endpoint, options = {}) => apiRequest(endpoint, { method: 'DELETE', ...options })
  };

  /**
   * Check backend health / status
   */
  async function checkBackendHealth() {
    try {
      const res = await fetchWithTimeout(`${API_CONFIG.BASE_URL}/health`, { method: 'GET', timeout: 3000 });
      return res.ok;
    } catch {
      return false;
    }
  }

  /**
   * Authentication endpoints
   */
  const auth = {
    async login(email, password) {
      const res = await http.post('/auth/login', { email, password });
      if (res.success && res.data && res.data.access_token) {
        localStorage.setItem(API_CONFIG.STORAGE_KEYS.TOKEN, res.data.access_token);
        localStorage.setItem(API_CONFIG.STORAGE_KEYS.USER, JSON.stringify(res.data.user || { email }));
      }
      return res;
    },

    async register(userData) {
      // Backend expects: full_name, email, password, role
      return http.post('/auth/register', userData);
    },

    async getProfile() {
      return http.get('/auth/me');
    },

    getCurrentUser() {
      const raw = localStorage.getItem(API_CONFIG.STORAGE_KEYS.USER);
      try {
        return raw ? JSON.parse(raw) : null;
      } catch {
        return null;
      }
    },

    getToken() {
      return localStorage.getItem(API_CONFIG.STORAGE_KEYS.TOKEN);
    },

    isAuthenticated() {
      return !!localStorage.getItem(API_CONFIG.STORAGE_KEYS.TOKEN);
    },

    logout() {
      localStorage.removeItem(API_CONFIG.STORAGE_KEYS.TOKEN);
      localStorage.removeItem(API_CONFIG.STORAGE_KEYS.USER);
      const isPagesDir = window.location.pathname.includes('/pages/');
      window.location.href = isPagesDir ? 'login.html' : 'pages/login.html';
    }
  };

  /**
   * Courses endpoints
   */
  const courses = {
    list: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return http.get(query ? `/courses?${query}` : '/courses');
    },
    getById: (id) => http.get(`/courses/${id}`),
    getMaterials: (courseId) => http.get(`/courses/${courseId}/materials`),
    create: (courseData) => http.post('/courses', courseData)
  };

  /**
   * Quizzes endpoints
   */
  const quizzes = {
    getByCourse: (courseId) => http.get(`/courses/${courseId}/quizzes`),
    getById: (quizId) => http.get(`/quizzes/${quizId}`),
    submit: (quizId, answers) => http.post(`/quizzes/${quizId}/submit`, { answers })
  };

  // Expose to window for global access
  window.SmartLearnAPI = {
    config: API_CONFIG,
    request: apiRequest,
    http,
    auth,
    courses,
    quizzes,
    checkBackendHealth
  };

  window.apiRequest = apiRequest;
  window.API = window.SmartLearnAPI;

})(window);
