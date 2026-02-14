import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAppStore } from '@store/index';

const API_BASE_URL = process.env.API_URL || 'https://api.hrplatform.com';

let client: AxiosInstance;

export const initializeApiClient = () => {
  client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  });

  // Add token to request headers
  client.interceptors.request.use(
    async (config) => {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Handle response errors
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Token expired or invalid
        await AsyncStorage.removeItem('auth_token');
        useAppStore.getState().logout();
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const getApiClient = (): AxiosInstance => {
  if (!client) {
    initializeApiClient();
  }
  return client;
};

// API Methods
export const apiClient = {
  // Auth
  auth: {
    login: (email: string, password: string) =>
      getApiClient().post('/auth/login', { email, password }),
    loginBiometric: (userId: string, biometricData: string) =>
      getApiClient().post('/auth/biometric-login', { userId, biometricData }),
    logout: () => getApiClient().post('/auth/logout'),
    refreshToken: () => getApiClient().post('/auth/refresh'),
    validateToken: () => getApiClient().get('/auth/validate'),
  },

  // User Profile
  user: {
    getProfile: () => getApiClient().get('/users/profile'),
    updateProfile: (data: any) =>
      getApiClient().put('/users/profile', data),
    getNotifications: (page: number = 1, limit: number = 20) =>
      getApiClient().get(`/users/notifications?page=${page}&limit=${limit}`),
    markNotificationAsRead: (notificationId: string) =>
      getApiClient().put(`/notifications/${notificationId}/read`),
    markAllNotificationsAsRead: () =>
      getApiClient().put('/notifications/read-all'),
  },

  // Dashboard
  dashboard: {
    getStats: () => getApiClient().get('/dashboard/stats'),
    getActivity: (limit: number = 10) =>
      getApiClient().get(`/dashboard/activity?limit=${limit}`),
  },

  // Requirements
  requirements: {
    list: (
      page: number = 1,
      limit: number = 20,
      filters?: any
    ) => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...filters,
      });
      return getApiClient().get(`/requirements?${params.toString()}`);
    },
    get: (id: string) => getApiClient().get(`/requirements/${id}`),
    search: (query: string) =>
      getApiClient().get(`/requirements/search?q=${query}`),
    getApplications: (requirementId: string) =>
      getApiClient().get(`/requirements/${requirementId}/applications`),
  },

  // Candidates
  candidates: {
    list: (
      page: number = 1,
      limit: number = 20,
      filters?: any
    ) => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...filters,
      });
      return getApiClient().get(`/candidates?${params.toString()}`);
    },
    get: (id: string) => getApiClient().get(`/candidates/${id}`),
    search: (query: string) =>
      getApiClient().get(`/candidates/search?q=${query}`),
    updateRating: (id: string, rating: number) =>
      getApiClient().put(`/candidates/${id}/rating`, { rating }),
    sendMessage: (id: string, message: string) =>
      getApiClient().post(`/candidates/${id}/message`, { message }),
  },

  // Submissions
  submissions: {
    list: (
      page: number = 1,
      limit: number = 20,
      filters?: any
    ) => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...filters,
      });
      return getApiClient().get(`/submissions?${params.toString()}`);
    },
    get: (id: string) => getApiClient().get(`/submissions/${id}`),
    updateStatus: (id: string, status: string) =>
      getApiClient().put(`/submissions/${id}/status`, { status }),
    addNote: (id: string, note: string) =>
      getApiClient().post(`/submissions/${id}/notes`, { note }),
    scheduleInterview: (
      id: string,
      date: string,
      time: string
    ) =>
      getApiClient().post(`/submissions/${id}/interview`, { date, time }),
  },

  // Chat / AI Copilot
  chat: {
    sendMessage: (message: string, context?: any) =>
      getApiClient().post('/copilot/chat', { message, context }),
    getHistory: (limit: number = 50) =>
      getApiClient().get(`/copilot/history?limit=${limit}`),
    clearHistory: () => getApiClient().post('/copilot/history/clear'),
  },

  // Contracts
  contracts: {
    list: (page: number = 1, limit: number = 20) =>
      getApiClient().get(`/contracts?page=${page}&limit=${limit}`),
    get: (id: string) => getApiClient().get(`/contracts/${id}`),
    uploadSignature: (id: string, signature: string) =>
      getApiClient().post(`/contracts/${id}/sign`, { signature }),
    getSigningStatus: (id: string) =>
      getApiClient().get(`/contracts/${id}/status`),
  },

  // Settings
  settings: {
    updateNotifications: (settings: any) =>
      getApiClient().put('/settings/notifications', settings),
    updateBiometrics: (enabled: boolean) =>
      getApiClient().put('/settings/biometrics', { enabled }),
    updateLanguage: (language: string) =>
      getApiClient().put('/settings/language', { language }),
  },
};

export default apiClient;
