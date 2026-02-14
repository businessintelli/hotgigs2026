import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  SafeAreaView,
} from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { useAppStore } from '@store/index';
import { useAuth } from '@hooks/useAuth';
import { spacing, typography, colors, shadows } from '@theme/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

const SettingsScreen: React.FC = () => {
  const {
    settings,
    updateSettings,
    isDarkMode,
    toggleTheme,
  } = useAppStore();
  const { logout, enableBiometric, disableBiometric } = useAuth();
  const user = useAppStore((state) => state.auth.user);

  const [biometricEnabled, setBiometricEnabled] = useState(
    settings.biometric_auth
  );

  const handleToggleNotifications = (value: boolean) => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    updateSettings({ notifications_enabled: value });
  };

  const handleTogglePushNotifications = (value: boolean) => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    updateSettings({ push_notifications: value });
  };

  const handleToggleEmailNotifications = (value: boolean) => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    updateSettings({ email_notifications: value });
  };

  const handleToggleBiometric = async (value: boolean) => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });

    if (value && user?.email) {
      const success = await enableBiometric(user.email);
      if (success) {
        setBiometricEnabled(true);
        updateSettings({ biometric_auth: true });
      } else {
        Alert.alert(
          'Biometric Setup Failed',
          'Could not enable biometric authentication'
        );
      }
    } else if (!value) {
      const success = await disableBiometric();
      if (success) {
        setBiometricEnabled(false);
        updateSettings({ biometric_auth: false });
      }
    }
  };

  const handleToggleRememberMe = (value: boolean) => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    updateSettings({ remember_me: value });
  };

  const handleToggleTheme = () => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    toggleTheme();
  };

  const handleLogout = () => {
    Alert.alert(
      'Confirm Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', onPress: () => {}, style: 'cancel' },
        {
          text: 'Logout',
          onPress: async () => {
            RNHapticFeedback.trigger('impactMedium', {
              enableVibrateFallback: true,
              ignoreAndroidSystemSettings: false,
            });
            await logout();
          },
          style: 'destructive',
        },
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>

          <View style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="notifications"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Enable Notifications</Text>
                <Text style={styles.settingDescription}>
                  Receive all notifications
                </Text>
              </View>
            </View>
            <Switch
              value={settings.notifications_enabled}
              onValueChange={handleToggleNotifications}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={
                settings.notifications_enabled ? '#2563EB' : '#9CA3AF'
              }
            />
          </View>

          <View style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="notifications-active"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Push Notifications</Text>
                <Text style={styles.settingDescription}>
                  Instant alerts on your device
                </Text>
              </View>
            </View>
            <Switch
              value={settings.push_notifications}
              onValueChange={handleTogglePushNotifications}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={
                settings.push_notifications ? '#2563EB' : '#9CA3AF'
              }
            />
          </View>

          <View style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="mail-outline"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Email Notifications</Text>
                <Text style={styles.settingDescription}>
                  Daily digest and important updates
                </Text>
              </View>
            </View>
            <Switch
              value={settings.email_notifications}
              onValueChange={handleToggleEmailNotifications}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={
                settings.email_notifications ? '#2563EB' : '#9CA3AF'
              }
            />
          </View>
        </View>

        {/* Security Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Security</Text>

          <View style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="fingerprint"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Biometric Login</Text>
                <Text style={styles.settingDescription}>
                  Face ID or Fingerprint
                </Text>
              </View>
            </View>
            <Switch
              value={biometricEnabled}
              onValueChange={handleToggleBiometric}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={
                biometricEnabled ? '#2563EB' : '#9CA3AF'
              }
            />
          </View>

          <View style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="memory"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Remember Me</Text>
                <Text style={styles.settingDescription}>
                  Stay logged in for 30 days
                </Text>
              </View>
            </View>
            <Switch
              value={settings.remember_me}
              onValueChange={handleToggleRememberMe}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={
                settings.remember_me ? '#2563EB' : '#9CA3AF'
              }
            />
          </View>
        </View>

        {/* Appearance Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Appearance</Text>

          <View style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name={isDarkMode ? 'dark-mode' : 'light-mode'}
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Dark Mode</Text>
                <Text style={styles.settingDescription}>
                  {isDarkMode ? 'Dark theme enabled' : 'Light theme enabled'}
                </Text>
              </View>
            </View>
            <Switch
              value={isDarkMode}
              onValueChange={handleToggleTheme}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={
                isDarkMode ? '#2563EB' : '#9CA3AF'
              }
            />
          </View>
        </View>

        {/* Preferences Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>

          <TouchableOpacity style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="language"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Language</Text>
                <Text style={styles.settingDescription}>
                  {settings.language || 'English'}
                </Text>
              </View>
            </View>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="public"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Timezone</Text>
                <Text style={styles.settingDescription}>
                  {settings.timezone || 'UTC'}
                </Text>
              </View>
            </View>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>

          <TouchableOpacity style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="info-outline"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Version</Text>
                <Text style={styles.settingDescription}>1.0.0</Text>
              </View>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="privacy-tip"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Privacy Policy</Text>
                <Text style={styles.settingDescription}>
                  View our privacy terms
                </Text>
              </View>
            </View>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.settingItem, shadows.sm]}>
            <View style={styles.settingContent}>
              <MaterialIcons
                name="description"
                size={20}
                color="#2563EB"
              />
              <View style={styles.settingText}>
                <Text style={styles.settingName}>Terms of Service</Text>
                <Text style={styles.settingDescription}>
                  View our terms
                </Text>
              </View>
            </View>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>
        </View>

        {/* Logout Section */}
        <View style={styles.section}>
          <TouchableOpacity
            style={[styles.logoutButton, shadows.sm]}
            onPress={handleLogout}
          >
            <MaterialIcons
              name="logout"
              size={20}
              color="#DC2626"
            />
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            All your data is encrypted and secure
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  section: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.heading3,
    color: colors.text.primary,
    marginBottom: spacing.md,
  },
  settingItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  settingContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    flex: 1,
  },
  settingText: {
    flex: 1,
  },
  settingName: {
    ...typography.button,
    color: colors.text.primary,
  },
  settingDescription: {
    ...typography.caption,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  logoutButton: {
    backgroundColor: '#FEF2F2',
    borderRadius: 12,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.md,
  },
  logoutButtonText: {
    ...typography.button,
    color: '#DC2626',
    fontWeight: '600',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: spacing.lg,
  },
  footerText: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
});

export default SettingsScreen;
