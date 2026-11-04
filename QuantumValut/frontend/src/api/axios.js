import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/refresh') {
      originalRequest._retry = true;
      
      try {
        await axios.post(
          `${axiosInstance.defaults.baseURL}/auth/refresh`, 
          {}, 
          { withCredentials: true }
        );
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().clearUser();
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;
