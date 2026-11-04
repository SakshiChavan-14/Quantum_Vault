import { create } from 'zustand';

// Contains only the theme state structure as per architecture requirements
export const useThemeStore = create((set) => ({
  theme: 'light', // 'light' | 'dark'
  
  // Placeholders for future state updates
  setTheme: (theme) => set({ theme }),
  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
}));
