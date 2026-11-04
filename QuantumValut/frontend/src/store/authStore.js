import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isInitialized: false,
  
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  clearUser: () => set({ user: null, isAuthenticated: false }),
  setLoading: (isLoading) => set({ isLoading }),
  initialize: () => set({ isInitialized: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));
