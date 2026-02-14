import React, { useEffect } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'react-native';
import messaging from '@react-native-firebase/messaging';
import { initializeApiClient } from '@api/client';
import { AppNavigator } from '@navigation/AppNavigator';
import { useAppStore } from '@store/index';
import { lightTheme, darkTheme } from '@theme/index';

// Initialize API client
initializeApiClient();

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Request push notification permission
const requestUserPermission = async () => {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    console.log('Authorization status:', authStatus);
    const token = await messaging().getToken();
    console.log('FCM Token:', token);
  }
};

// Handle notification messages
const handleNotificationMessage = (message: any) => {
  const { title, body, data } = message.notification || {};
  const { unreadNotifications, setUnreadNotifications } = useAppStore.getState();

  if (title && body) {
    // Show notification to user
    console.log('Notification:', { title, body, data });

    // Update unread count
    setUnreadNotifications(unreadNotifications + 1);
  }
};

const App: React.FC = () => {
  const isDarkMode = useAppStore((state) => state.isDarkMode);
  const theme = isDarkMode ? darkTheme : lightTheme;

  useEffect(() => {
    // Request push notification permission
    requestUserPermission();

    // Handle notification when app is in foreground
    const unsubscribe = messaging().onMessage(async (remoteMessage) => {
      handleNotificationMessage(remoteMessage);
    });

    // Handle notification when app is opened from notification
    messaging()
      .getInitialNotification()
      .then((remoteMessage) => {
        if (remoteMessage) {
          handleNotificationMessage(remoteMessage);
        }
      });

    // Handle notification when app is in background
    messaging().onNotificationOpenedApp((remoteMessage) => {
      if (remoteMessage) {
        handleNotificationMessage(remoteMessage);
      }
    });

    return unsubscribe;
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <StatusBar
            barStyle={isDarkMode ? 'light-content' : 'dark-content'}
            backgroundColor={theme.background}
            translucent={false}
          />
          <AppNavigator />
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
};

export default App;
