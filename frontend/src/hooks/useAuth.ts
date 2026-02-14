import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

export const useAuth = () => {
  const navigate = useNavigate();
  const auth = useAuthStore();

  const handleLogin = useCallback(
    async (email: string, password: string) => {
      try {
        await auth.login(email, password);
        navigate('/dashboard');
      } catch (error) {
        throw error;
      }
    },
    [auth, navigate]
  );

  const handleLogout = useCallback(async () => {
    await auth.logout();
    navigate('/login');
  }, [auth, navigate]);

  const handleVerifyToken = useCallback(async () => {
    try {
      await auth.verifyToken();
      return true;
    } catch {
      await handleLogout();
      return false;
    }
  }, [auth, handleLogout]);

  return {
    user: auth.user,
    token: auth.token,
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    error: auth.error,
    login: handleLogin,
    logout: handleLogout,
    verifyToken: handleVerifyToken,
    clearError: auth.clearError,
    setUser: auth.setUser,
    setToken: auth.setToken,
  };
};
