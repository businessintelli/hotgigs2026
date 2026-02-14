import client, { setStoredToken, setStoredRefreshToken } from './client';
import type { AuthResponse, User } from '@/types';

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await client.post<AuthResponse>('/auth/login', {
    email,
    password,
  });

  const { access_token, refresh_token, user } = response.data;
  setStoredToken(access_token);
  setStoredRefreshToken(refresh_token);
  localStorage.setItem('user', JSON.stringify(user));

  return response.data;
};

export const logout = async (): Promise<void> => {
  try {
    await client.post('/auth/logout');
  } catch {
    // Logout endpoint may fail, but we still want to clear local data
  }

  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

export const getCurrentUser = (): User | null => {
  try {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
};

export const updateProfile = async (data: Partial<User>): Promise<User> => {
  const response = await client.put<User>('/auth/profile', data);
  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};

export const changePassword = async (
  currentPassword: string,
  newPassword: string
): Promise<void> => {
  await client.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
};

export const requestPasswordReset = async (email: string): Promise<void> => {
  await client.post('/auth/request-password-reset', { email });
};

export const resetPassword = async (token: string, newPassword: string): Promise<void> => {
  await client.post('/auth/reset-password', {
    token,
    new_password: newPassword,
  });
};

export const verifyToken = async (): Promise<User> => {
  const response = await client.get<User>('/auth/me');
  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};
