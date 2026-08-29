import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('lm_auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect if expired
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/verify')) {
        localStorage.removeItem('lm_auth_token');
        localStorage.removeItem('lm_user_profile');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
