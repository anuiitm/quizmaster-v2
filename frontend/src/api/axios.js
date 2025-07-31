import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5001',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('csrf_token');
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('is_logged_in');
      localStorage.removeItem('is_admin');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
