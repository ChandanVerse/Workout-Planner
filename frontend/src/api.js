import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (credentials) => api.post('/api/auth/login', credentials),
};

// User APIs
export const userAPI = {
  getMe: () => api.get('/api/user/me'),
};

// Workout APIs
export const workoutAPI = {
  createPlan: (planData) => api.post('/api/workout/plan', planData),
};

// Progress APIs
export const progressAPI = {
  logWorkout: (logData) => api.post('/api/progress/log', logData),
  getHistory: (days = 7) => api.get(`/api/progress/history?days=${days}`),
  getStats: () => api.get('/api/progress/stats'),
};

export default api;