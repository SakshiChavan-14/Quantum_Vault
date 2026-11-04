import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import { authService } from '../services/authService';
import { authApi } from '../api/authApi';
import { useEffect } from 'react';

export const useAuth = () => {
  const queryClient = useQueryClient();
  const { user, isAuthenticated, isLoading, isInitialized, setUser, clearUser, setLoading, initialize } = useAuthStore();

  const { data: queryUser, isFetching, error } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authApi.getCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });

  useEffect(() => {
    if (!isInitialized && !isFetching) {
      if (queryUser) {
        setUser(queryUser);
      } else if (error) {
        clearUser();
      }
      initialize();
    }
  }, [queryUser, error, isFetching, isInitialized, setUser, clearUser, initialize]);

  const login = async (credentials) => {
    setLoading(true);
    const result = await authService.login(credentials);
    if (result.success) {
      await queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
      setUser(result.user);
    }
    setLoading(false);
    return result;
  };

  const register = async (userData) => {
    setLoading(true);
    const result = await authService.register(userData);
    setLoading(false);
    return result;
  };

  const logout = async () => {
    setLoading(true);
    const result = await authService.logout();
    if (result.success) {
      clearUser();
      queryClient.removeQueries({ queryKey: ['auth', 'me'] });
    }
    setLoading(false);
    return result;
  };
  
  const refresh = async () => {
    return await authApi.refresh();
  }

  const getCurrentUser = async () => {
    return await authApi.getCurrentUser();
  }

  return {
    login,
    register,
    logout,
    refresh,
    getCurrentUser,
    loading: isLoading || (isFetching && !isInitialized),
    user,
    isAuthenticated,
    isInitialized
  };
};
