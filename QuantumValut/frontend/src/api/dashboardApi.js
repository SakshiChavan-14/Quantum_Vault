import axiosInstance from './axios';

export const dashboardApi = {
  getOverview: async () => {
    const response = await axiosInstance.get('/dashboard/overview');
    return response.data;
  },
  
  getStorage: async () => {
    const response = await axiosInstance.get('/dashboard/storage');
    return response.data;
  },
  
  getRecentFiles: async () => {
    const response = await axiosInstance.get('/dashboard/recent-files');
    return response.data;
  },
  
  getActivity: async () => {
    const response = await axiosInstance.get('/dashboard/activity');
    return response.data;
  }
};
