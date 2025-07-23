import axios from 'axios';

// API configuration for Django backend
const api = axios.create({
    baseURL: process.env.NODE_ENV === 'production' 
        ? '/api/' 
        : 'http://localhost:8000/api/',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Token ${token}`;
        }
        
        // Don't override Content-Type for FormData (file uploads)
        if (config.data instanceof FormData) {
            // Let browser set Content-Type automatically for multipart/form-data
            delete config.headers['Content-Type'];
        }
        
        // Add CSRF token if available
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken.value;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for better error handling
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Handle authentication errors
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        
        return Promise.reject(error);
    }
);

export default api; 