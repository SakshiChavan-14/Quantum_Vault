import { dashboardApi } from '../api/dashboardApi';

class DashboardService {
  async getOverview() {
    try {
      return await dashboardApi.getOverview();
    } catch (error) {
      console.error('Error fetching dashboard overview:', error);
      throw error;
    }
  }

  async getStorage() {
    try {
      return await dashboardApi.getStorage();
    } catch (error) {
      console.error('Error fetching storage summary:', error);
      throw error;
    }
  }

  async getRecentFiles() {
    try {
      return await dashboardApi.getRecentFiles();
    } catch (error) {
      console.error('Error fetching recent files:', error);
      throw error;
    }
  }

  async getActivity() {
    try {
      return await dashboardApi.getActivity();
    } catch (error) {
      console.error('Error fetching activity:', error);
      throw error;
    }
  }
}

export const dashboardService = new DashboardService();
