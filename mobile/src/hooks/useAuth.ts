import { useState, useCallback } from 'react';
import { useAppStore } from '@store/index';
import { apiClient, initializeApiClient } from '@api/client';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'react-native-secure-store';
import ReactNativeBiometrics, { BiometryTypes } from 'react-native-biometric-promise';
import { AxiosError } from 'axios';

interface LoginParams {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface BiometricLoginParams {
  biometricData: string;
}

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setUser, setToken, setAuthLoading, setAuthError, logout: storeLogout } =
    useAppStore();
  const auth = useAppStore((state) => state.auth);

  const handleLoginResponse = useCallback(
    async (response: any, rememberMe?: boolean) => {
      const { user, access_token } = response.data;

      // Store token
      await AsyncStorage.setItem('auth_token', access_token);
      if (rememberMe) {
        await AsyncStorage.setItem('remember_me', 'true');
        await SecureStore.setItem('user_email', user.email);
      }

      // Update store
      setUser(user);
      setToken(access_token);
      setAuthError(null);

      // Initialize API client with token
      initializeApiClient();

      return { user, token: access_token };
    },
    [setUser, setToken, setAuthError]
  );

  const login = useCallback(
    async (params: LoginParams) => {
      setIsLoading(true);
      setAuthLoading(true);
      setError(null);
      setAuthError(null);

      try {
        const response = await apiClient.auth.login(params.email, params.password);
        const result = await handleLoginResponse(response, params.rememberMe);
        setIsLoading(false);
        setAuthLoading(false);
        return result;
      } catch (err) {
        const axiosError = err as AxiosError;
        const errorMessage =
          axiosError.response?.data?.message || 'Login failed. Please try again.';
        setError(errorMessage as string);
        setAuthError(errorMessage as string);
        setIsLoading(false);
        setAuthLoading(false);
        throw err;
      }
    },
    [handleLoginResponse, setAuthLoading, setAuthError]
  );

  const loginWithBiometric = useCallback(
    async (params: BiometricLoginParams) => {
      setIsLoading(true);
      setAuthLoading(true);
      setError(null);
      setAuthError(null);

      try {
        const userEmail = await AsyncStorage.getItem('user_email');
        if (!userEmail) {
          throw new Error('No stored user email found');
        }

        const response = await apiClient.auth.loginBiometric(
          userEmail,
          params.biometricData
        );
        const result = await handleLoginResponse(response);
        setIsLoading(false);
        setAuthLoading(false);
        return result;
      } catch (err) {
        const axiosError = err as AxiosError;
        const errorMessage =
          axiosError.response?.data?.message || 'Biometric login failed.';
        setError(errorMessage as string);
        setAuthError(errorMessage as string);
        setIsLoading(false);
        setAuthLoading(false);
        throw err;
      }
    },
    [handleLoginResponse, setAuthLoading, setAuthError]
  );

  const checkBiometricAvailability = useCallback(async () => {
    try {
      const rnBiometrics = new ReactNativeBiometrics();
      const biometryType = await rnBiometrics.biometryType();
      return {
        available: biometryType !== null,
        type: biometryType as BiometryTypes | null,
      };
    } catch (err) {
      return {
        available: false,
        type: null,
      };
    }
  }, []);

  const enableBiometric = useCallback(
    async (email: string) => {
      try {
        const rnBiometrics = new ReactNativeBiometrics();

        // Check if biometrics are available
        const biometryType = await rnBiometrics.biometryType();
        if (!biometryType) {
          throw new Error('Biometrics not available on this device');
        }

        // Create biometric signature
        const { signature } = await rnBiometrics.createSignature({
          promptMessage: 'Authenticate to enable biometric login',
          payload: email,
        });

        // Store biometric email for later use
        await AsyncStorage.setItem('biometric_email', email);
        await AsyncStorage.setItem('biometric_signature', signature);
        await AsyncStorage.setItem('biometric_enabled', 'true');

        // Update settings on server
        await apiClient.settings.updateBiometrics(true);

        return true;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to enable biometric';
        setError(errorMessage);
        return false;
      }
    },
    []
  );

  const disableBiometric = useCallback(async () => {
    try {
      await AsyncStorage.removeItem('biometric_email');
      await AsyncStorage.removeItem('biometric_signature');
      await AsyncStorage.removeItem('biometric_enabled');
      await apiClient.settings.updateBiometrics(false);
      return true;
    } catch (err) {
      const errorMessage = 'Failed to disable biometric';
      setError(errorMessage);
      return false;
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiClient.auth.logout();
    } catch (err) {
      // Even if logout fails on server, clear local data
      console.error('Logout error:', err);
    }

    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('remember_me');
    await AsyncStorage.removeItem('user_email');

    storeLogout();
    setIsLoading(false);
    setError(null);
  }, [storeLogout]);

  const refreshToken = useCallback(async () => {
    try {
      const response = await apiClient.auth.refreshToken();
      const { access_token } = response.data;

      await AsyncStorage.setItem('auth_token', access_token);
      setToken(access_token);
      initializeApiClient();

      return access_token;
    } catch (err) {
      // Token refresh failed, logout user
      await logout();
      throw err;
    }
  }, [setToken, logout]);

  const validateToken = useCallback(async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (!token) {
        return false;
      }

      const response = await apiClient.auth.validateToken();
      return response.status === 200;
    } catch (err) {
      return false;
    }
  }, []);

  const isAuthenticated = !!auth.user && !!auth.token;

  return {
    // State
    user: auth.user,
    token: auth.token,
    isLoading: isLoading || auth.isLoading,
    error: error || auth.error,
    isAuthenticated,

    // Methods
    login,
    loginWithBiometric,
    logout,
    refreshToken,
    validateToken,
    checkBiometricAvailability,
    enableBiometric,
    disableBiometric,
  };
};

export default useAuth;
