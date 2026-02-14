import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  sidebarOpen: boolean;
  darkMode: boolean;
  sidebarCollapsed: boolean;
  selectedRequirement: string | null;
  selectedCandidate: string | null;
  filters: Record<string, unknown>;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleDarkMode: () => void;
  setDarkMode: (enabled: boolean) => void;
  toggleSidebarCollapsed: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSelectedRequirement: (id: string | null) => void;
  setSelectedCandidate: (id: string | null) => void;
  setFilters: (filters: Record<string, unknown>) => void;
  clearFilters: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      darkMode: false,
      sidebarCollapsed: false,
      selectedRequirement: null,
      selectedCandidate: null,
      filters: {},

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

      toggleDarkMode: () => {
        set((state) => {
          const newMode = !state.darkMode;
          if (newMode) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { darkMode: newMode };
        });
      },

      setDarkMode: (enabled: boolean) => {
        set({ darkMode: enabled });
        if (enabled) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },

      toggleSidebarCollapsed: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed: boolean) =>
        set({ sidebarCollapsed: collapsed }),

      setSelectedRequirement: (id: string | null) =>
        set({ selectedRequirement: id }),

      setSelectedCandidate: (id: string | null) =>
        set({ selectedCandidate: id }),

      setFilters: (filters: Record<string, unknown>) => set({ filters }),

      clearFilters: () => set({ filters: {} }),
    }),
    {
      name: 'ui-store',
      partialize: (state) => ({
        darkMode: state.darkMode,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
