import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { useAppStore } from '@store/index';
import { spacing, typography, colors, shadows } from '@theme/index';

const ProfileScreen: React.FC = () => {
  const user = useAppStore((state) => state.auth.user);

  const profileItems = [
    {
      icon: 'email',
      label: 'Email',
      value: user?.email || 'N/A',
    },
    {
      icon: 'phone',
      label: 'Phone',
      value: user?.phone || 'Not provided',
    },
    {
      icon: 'work',
      label: 'Department',
      value: user?.department || 'N/A',
    },
    {
      icon: 'admin-panel-settings',
      label: 'Role',
      value: user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1) || 'User',
    },
    {
      icon: 'calendar-today',
      label: 'Joined',
      value: user?.joinedDate
        ? new Date(user.joinedDate).toLocaleDateString()
        : 'N/A',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <View style={[styles.profileHeader, shadows.md]}>
          {user?.avatar ? (
            <Image
              source={{ uri: user.avatar }}
              style={styles.profileImage}
            />
          ) : (
            <View style={styles.profileImagePlaceholder}>
              <Text style={styles.profileImageText}>
                {user?.name
                  ?.split(' ')
                  .map((n) => n[0])
                  .join('') || 'U'}
              </Text>
            </View>
          )}

          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{user?.name || 'User'}</Text>
            <Text style={styles.profileRole}>
              {user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1) || 'User'}
            </Text>
          </View>

          <TouchableOpacity style={styles.editButton}>
            <MaterialIcons name="edit" size={20} color="#2563EB" />
          </TouchableOpacity>
        </View>

        {/* Profile Details */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Profile Information</Text>

          {profileItems.map((item, index) => (
            <View
              key={index}
              style={[
                styles.profileItem,
                index < profileItems.length - 1 && styles.profileItemBorder,
              ]}
            >
              <MaterialIcons
                name={item.icon as any}
                size={20}
                color="#2563EB"
              />
              <View style={styles.profileItemContent}>
                <Text style={styles.profileItemLabel}>{item.label}</Text>
                <Text style={styles.profileItemValue}>{item.value}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Preferences */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>

          <TouchableOpacity style={[styles.preferenceItem, shadows.sm]}>
            <View style={styles.preferenceIcon}>
              <MaterialIcons
                name="language"
                size={20}
                color="#2563EB"
              />
            </View>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>Language</Text>
              <Text style={styles.preferenceValue}>English</Text>
            </View>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.preferenceItem, shadows.sm]}>
            <View style={styles.preferenceIcon}>
              <MaterialIcons
                name="public"
                size={20}
                color="#2563EB"
              />
            </View>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>Timezone</Text>
              <Text style={styles.preferenceValue}>UTC</Text>
            </View>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>
        </View>

        {/* Connected Apps */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Connected Integrations</Text>

          <View style={[styles.integrationItem, shadows.sm]}>
            <View style={styles.integrationIcon}>
              <Text style={styles.integrationIconText}>GH</Text>
            </View>
            <View style={styles.integrationContent}>
              <Text style={styles.integrationName}>GitHub</Text>
              <Text style={styles.integrationStatus}>Connected</Text>
            </View>
            <View style={styles.connectedBadge}>
              <MaterialIcons
                name="check-circle"
                size={20}
                color={colors.status.success}
              />
            </View>
          </View>

          <View style={[styles.integrationItem, shadows.sm]}>
            <View style={styles.integrationIcon}>
              <Text style={styles.integrationIconText}>LI</Text>
            </View>
            <View style={styles.integrationContent}>
              <Text style={styles.integrationName}>LinkedIn</Text>
              <Text style={styles.integrationStatus}>Not connected</Text>
            </View>
            <TouchableOpacity>
              <Text style={styles.connectLink}>Connect</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Account Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>

          <TouchableOpacity style={[styles.actionItem, shadows.sm]}>
            <MaterialIcons
              name="security"
              size={20}
              color="#2563EB"
            />
            <Text style={styles.actionItemText}>Change Password</Text>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.actionItem, shadows.sm]}>
            <MaterialIcons
              name="download"
              size={20}
              color="#2563EB"
            />
            <Text style={styles.actionItemText}>Download My Data</Text>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color={colors.text.tertiary}
            />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.actionItem, styles.deleteAction, shadows.sm]}>
            <MaterialIcons
              name="delete-forever"
              size={20}
              color="#DC2626"
            />
            <Text style={[styles.actionItemText, styles.deleteActionText]}>
              Delete Account
            </Text>
            <MaterialIcons
              name="chevron-right"
              size={24}
              color="#DC2626"
            />
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={styles.versionText}>Version 1.0.0</Text>
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
  profileHeader: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    margin: spacing.lg,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.lg,
  },
  profileImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  profileImagePlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#E5E7EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileImageText: {
    ...typography.heading2,
    color: colors.text.primary,
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  profileRole: {
    ...typography.bodySmall,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  editButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
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
  profileItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: spacing.md,
    gap: spacing.md,
  },
  profileItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  profileItemContent: {
    flex: 1,
  },
  profileItemLabel: {
    ...typography.caption,
    color: colors.text.secondary,
    fontWeight: '600',
  },
  profileItemValue: {
    ...typography.body,
    color: colors.text.primary,
    marginTop: spacing.xs,
  },
  preferenceItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  preferenceIcon: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  preferenceContent: {
    flex: 1,
  },
  preferenceName: {
    ...typography.button,
    color: colors.text.primary,
  },
  preferenceValue: {
    ...typography.caption,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  integrationItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  integrationIcon: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: '#E5E7EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  integrationIconText: {
    ...typography.button,
    color: colors.text.primary,
    fontWeight: '700',
  },
  integrationContent: {
    flex: 1,
  },
  integrationName: {
    ...typography.button,
    color: colors.text.primary,
  },
  integrationStatus: {
    ...typography.caption,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  connectedBadge: {
    marginRight: spacing.md,
  },
  connectLink: {
    ...typography.bodySmall,
    color: '#2563EB',
    fontWeight: '600',
  },
  actionItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  deleteAction: {
    backgroundColor: '#FEF2F2',
  },
  actionItemText: {
    flex: 1,
    ...typography.button,
    color: colors.text.primary,
  },
  deleteActionText: {
    color: '#DC2626',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: spacing.lg,
  },
  versionText: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
});

export default ProfileScreen;
