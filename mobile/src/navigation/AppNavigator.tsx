import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { useAppStore, selectIsAuthenticated } from '@store/index';

// Screens
import LoginScreen from '@screens/LoginScreen';
import DashboardScreen from '@screens/DashboardScreen';
import RequirementsScreen from '@screens/RequirementsScreen';
import CandidatesScreen from '@screens/CandidatesScreen';
import SubmissionsScreen from '@screens/SubmissionsScreen';
import ChatScreen from '@screens/ChatScreen';
import ContractsScreen from '@screens/ContractsScreen';
import NotificationsScreen from '@screens/NotificationsScreen';
import ProfileScreen from '@screens/ProfileScreen';
import SettingsScreen from '@screens/SettingsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const screenOptions = {
  headerShown: true,
  headerStyle: {
    backgroundColor: '#FFFFFF',
  },
  headerTitleStyle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  headerTintColor: '#2563EB',
  headerShadowVisible: true,
};

const DashboardStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="DashboardHome"
        component={DashboardScreen}
        options={{ headerTitle: 'Dashboard' }}
      />
    </Stack.Navigator>
  );
};

const RequirementsStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="RequirementsHome"
        component={RequirementsScreen}
        options={{ headerTitle: 'Requirements' }}
      />
    </Stack.Navigator>
  );
};

const CandidatesStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="CandidatesHome"
        component={CandidatesScreen}
        options={{ headerTitle: 'Candidates' }}
      />
    </Stack.Navigator>
  );
};

const SubmissionsStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="SubmissionsHome"
        component={SubmissionsScreen}
        options={{ headerTitle: 'Submissions' }}
      />
    </Stack.Navigator>
  );
};

const ChatStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="ChatHome"
        component={ChatScreen}
        options={{ headerTitle: 'AI Copilot' }}
      />
    </Stack.Navigator>
  );
};

const ContractsStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="ContractsHome"
        component={ContractsScreen}
        options={{ headerTitle: 'Contracts' }}
      />
    </Stack.Navigator>
  );
};

const NotificationsStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="NotificationsHome"
        component={NotificationsScreen}
        options={{ headerTitle: 'Notifications' }}
      />
    </Stack.Navigator>
  );
};

const MoreStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="ProfileHome"
        component={ProfileScreen}
        options={{ headerTitle: 'Profile' }}
      />
      <Stack.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ headerTitle: 'Settings' }}
      />
    </Stack.Navigator>
  );
};

const TabNavigator = () => {
  const unreadCount = useAppStore((state) => state.unreadNotifications);

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#E5E7EB',
          borderTopWidth: 1,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          marginTop: 4,
        },
        tabBarActiveTintColor: '#2563EB',
        tabBarInactiveTintColor: '#9CA3AF',
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="dashboard" size={size} color={color} />
          ),
        }}
      />

      <Tab.Screen
        name="Requirements"
        component={RequirementsStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="assignment" size={size} color={color} />
          ),
        }}
      />

      <Tab.Screen
        name="Candidates"
        component={CandidatesStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="people" size={size} color={color} />
          ),
        }}
      />

      <Tab.Screen
        name="Submissions"
        component={SubmissionsStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="send" size={size} color={color} />
          ),
        }}
      />

      <Tab.Screen
        name="Chat"
        component={ChatStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="chat" size={size} color={color} />
          ),
        }}
      />

      <Tab.Screen
        name="Contracts"
        component={ContractsStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="description" size={size} color={color} />
          ),
        }}
      />

      <Tab.Screen
        name="Notifications"
        component={NotificationsStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="notifications" size={size} color={color} />
          ),
          tabBarBadge: unreadCount > 0 ? unreadCount : null,
        }}
      />

      <Tab.Screen
        name="More"
        component={MoreStack}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="more-horiz" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

export const AppNavigator: React.FC = () => {
  const isAuthenticated = useAppStore(selectIsAuthenticated);

  return (
    <NavigationContainer
      linking={{
        prefixes: ['hrplatform://', 'https://app.hrplatform.com'],
        config: {
          screens: {
            Dashboard: 'dashboard',
            Requirements: 'requirements/:id',
            Candidates: 'candidates/:id',
            Submissions: 'submissions/:id',
            Chat: 'chat',
            Contracts: 'contracts/:id',
            Notifications: 'notifications',
            Profile: 'profile',
            Settings: 'settings',
            Login: 'login',
          },
        },
      }}
    >
      {isAuthenticated ? (
        <TabNavigator />
      ) : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
};

export default AppNavigator;
