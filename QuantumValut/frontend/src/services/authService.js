import toast from 'react-hot-toast';
import { authApi } from '../api/authApi';

const getErrorMessage = (error) => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  switch (error.response?.status) {
    case 400: return 'Invalid request data';
    case 401: return 'Invalid credentials';
    case 404: return 'User not found';
    case 422: return 'Validation error';
    case 500: return 'Unexpected server error';
    default: return 'Network error or server is unreachable';
  }
};

export const authService = {
  login: async (credentials) => {
    try {
      const user = await authApi.login(credentials);
      toast.success('Welcome back');
      return { success: true, user };
    } catch (error) {
      toast.error(getErrorMessage(error));
      return { success: false, error };
    }
  },

  register: async (userData) => {
    try {
      await authApi.register(userData);
      toast.success('Registration successful');
      return { success: true };
    } catch (error) {
      toast.error(getErrorMessage(error));
      return { success: false, error };
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
      toast.success('Logged out successfully');
      return { success: true };
    } catch (error) {
      toast.error(getErrorMessage(error));
      return { success: false, error };
    }
  }
};
