import { useQuery, useQueryClient } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';

export const useDashboard = () => {
  const queryClient = useQueryClient();

  const overviewQuery = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => dashboardService.getOverview()
  });

  const storageQuery = useQuery({
    queryKey: ['dashboard-storage'],
    queryFn: () => dashboardService.getStorage()
  });

  const recentFilesQuery = useQuery({
    queryKey: ['dashboard-recent-files'],
    queryFn: () => dashboardService.getRecentFiles()
  });

  const activityQuery = useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: () => dashboardService.getActivity()
  });

  const loading = 
    overviewQuery.isLoading || 
    storageQuery.isLoading || 
    recentFilesQuery.isLoading || 
    activityQuery.isLoading;

  const error = 
    overviewQuery.error || 
    storageQuery.error || 
    recentFilesQuery.error || 
    activityQuery.error;

  const refreshDashboard = () => {
    queryClient.invalidateQueries({ queryKey: ['dashboard-overview'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard-storage'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard-recent-files'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard-activity'] });
  };

  return {
    overview: overviewQuery.data,
    storage: storageQuery.data,
    recentFiles: recentFilesQuery.data?.files || [],
    activity: activityQuery.data?.activities || [],
    loading,
    error,
    refreshDashboard
  };
};
