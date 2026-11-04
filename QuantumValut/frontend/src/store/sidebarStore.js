import { create } from 'zustand';

export const useSidebarStore = create((set) => ({
  isOpen: true,
  activeView: 'my-drive',
  
  setIsOpen: (isOpen) => set({ isOpen }),
  toggleSidebar: () => set((state) => ({ isOpen: !state.isOpen })),
  setActiveView: (activeView) => set({ activeView }),
}));
