import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, AppSettings, AuthState } from '@types/index';

interface AppState {
  // Auth
  auth: AuthState;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setAuthLoading: (loading: boolean) => void;
  setAuthError: (error: string | null) => void;
  logout: () => void;

  // Settings
  settings: AppSettings;
  updateSettings: (settings: Partial<AppSettings>) => void;

  // App
  selectedTabIndex: number;
  setSelectedTabIndex: (index: number) => void;
  isDarkMode: boolean;
  toggleTheme: () => void;
  unreadNotifications: number;
  setUnreadNotifications: (count: number) => void;

  // Cache
  lastSyncTime: number;
  setLastSyncTime: (time: number) => void;
  isSyncing: boolean;
  setIsSyncing: (syncing: boolean) => void;
}

const defaultSettings: AppSettings = {
  theme: 'light',
  notifications_enabled: true,
  push_notifications: true,
  email_notifications: true,
  biometric_auth: false,
  remember_me: false,
  language: 'en',
  timezone: 'UTC',
};

const defaultAuthState: AuthState = {
  user: null,
  token: null,
  isLoading: false,
  error: null,
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Auth state
      auth: defaultAuthState,
      setUser: (user) =>
        set((state) => ({
          auth: { ...state.auth, user },
        })),
      setToken: (token) =>
        set((state) => ({
          auth: { ...state.auth, token },
        })),
      setAuthLoading: (isLoading) =>
        set((state) => ({
          auth: { ...state.auth, isLoading },
        })),
      setAuthError: (error) =>
        set((state) => ({
          auth: { ...state.auth, error },
        })),
      logout: () =>
        set({
          auth: defaultAuthState,
          selectedTabIndex: 0,
        }),

      // Settings
      settings: defaultSettings,
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),

      // App state
      selectedTabIndex: 0,
      setSelectedTabIndex: (index) =>
        set(() => ({
          selectedTabIndex: index,
        })),
      isDarkMode: false,
      toggleTheme: () =>
        set((state) => ({
          isDarkMode: !state.isDarkMode,
          settings: {
            ...state.settings,
            theme: state.isDarkMode ? 'light' : 'dark',
          },
        })),
      unreadNotifications: 0,
      setUnreadNotifications: (count) =>
        set(() => ({
          unreadNotifications: count,
        })),

      // Cache
      lastSyncTime: 0,
      setLastSyncTime: (time) =>
        set(() => ({
          lastSyncTime: time,
        })),
      isSyncing: false,
      setIsSyncing: (syncing) =>
        set(() => ({
          isSyncing: syncing,
        })),
    }),
    {
      name: 'hr-platform-store',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        settings: state.settings,
        auth: state.auth,
        isDarkMode: state.isDarkMode,
      }),
    }
  )
);

// Selectors
export const selectUser = (state: AppState) => state.auth.user;
export const selectToken = (state: AppState) => state.auth.token;
export const selectSettings = (state: AppState) => state.settings;
export const selectIsAuthenticated = (state: AppState) =>
  !!state.auth.user && !!state.auth.token;
export const selectTheme = (state: AppState) =>
  state.settings.theme === 'dark' ? 'dark' : 'light';
