import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SectionList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, colors, shadows } from '@theme/index';
import { apiClient } from '@api/client';
import { Notification } from '@types/index';
import { formatDistanceToNow } from 'date-fns';
import RNHapticFeedback from 'react-native-haptic-feedback';

interface NotificationGroup {
  title: string;
  data: Notification[];
}

const NotificationsScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);

  const { data: notifications = [], refetch, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await apiClient.user.getNotifications(1, 100);
      return response.data as Notification[];
    },
    staleTime: 2 * 60 * 1000,
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleNotificationPress = async (notification: Notification) => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });

    if (!notification.read) {
      await apiClient.user.markNotificationAsRead(notification.id);
      refetch();
    }
  };

  const groupNotifications = (notifs: Notification[]): NotificationGroup[] => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);

    const groups: Record<string, Notification[]> = {
      Today: [],
      'This Week': [],
      Older: [],
    };

    notifs.forEach((notif) => {
      const notifDate = new Date(notif.timestamp);
      const notifDateOnly = new Date(
        notifDate.getFullYear(),
        notifDate.getMonth(),
        notifDate.getDate()
      );

      if (notifDateOnly.getTime() === today.getTime()) {
        groups['Today'].push(notif);
      } else if (notifDate >= weekAgo) {
        groups['This Week'].push(notif);
      } else {
        groups['Older'].push(notif);
      }
    });

    return Object.entries(groups)
      .filter(([_, items]) => items.length > 0)
      .map(([title, data]) => ({
        title,
        data,
      }));
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return { icon: 'check-circle', color: colors.status.success };
      case 'warning':
        return { icon: 'warning', color: colors.status.warning };
      case 'error':
        return { icon: 'error', color: colors.status.error };
      case 'action':
        return { icon: 'info', color: colors.status.info };
      default:
        return { icon: 'notifications', color: colors.text.secondary };
    }
  };

  const handleMarkAllAsRead = async () => {
    RNHapticFeedback.trigger('impactMedium', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    await apiClient.user.markAllNotificationsAsRead();
    refetch();
  };

  const sections = groupNotifications(notifications);

  const renderNotificationItem = ({ item }: { item: Notification }) => {
    const { icon, color } = getNotificationIcon(item.type);

    return (
      <TouchableOpacity
        style={[
          styles.notificationItem,
          !item.read && styles.notificationItemUnread,
          shadows.sm,
        ]}
        onPress={() => handleNotificationPress(item)}
        activeOpacity={0.7}
      >
        <View style={[styles.notificationIcon, { backgroundColor: color }]}>
          <MaterialIcons name={icon as any} size={20} color="#FFFFFF" />
        </View>

        <View style={styles.notificationContent}>
          <Text style={styles.notificationTitle}>{item.title}</Text>
          <Text
            style={styles.notificationMessage}
            numberOfLines={2}
          >
            {item.message}
          </Text>
          <Text style={styles.notificationTime}>
            {formatDistanceToNow(new Date(item.timestamp), {
              addSuffix: true,
            })}
          </Text>
        </View>

        {!item.read && <View style={styles.unreadDot} />}
      </TouchableOpacity>
    );
  };

  const renderSectionHeader = ({ section: { title } }: { section: NotificationGroup }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );

  if (isLoading && !notifications.length) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      </SafeAreaView>
    );
  }

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <SafeAreaView style={styles.container}>
      {unreadCount > 0 && (
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.markAllButton}
            onPress={handleMarkAllAsRead}
          >
            <MaterialIcons
              name="done-all"
              size={18}
              color="#2563EB"
            />
            <Text style={styles.markAllButtonText}>
              Mark all as read
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {notifications.length === 0 ? (
        <View style={styles.emptyContainer}>
          <View style={styles.emptyIcon}>
            <MaterialIcons
              name="notifications-off"
              size={48}
              color={colors.text.tertiary}
            />
          </View>
          <Text style={styles.emptyTitle}>No Notifications</Text>
          <Text style={styles.emptyText}>
            You're all caught up!
          </Text>
        </View>
      ) : (
        <SectionList
          sections={sections}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={renderNotificationItem}
          renderSectionHeader={renderSectionHeader}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
            />
          }
          scrollEnabled={true}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerActions: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  markAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  markAllButtonText: {
    ...typography.bodySmall,
    color: '#2563EB',
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyIcon: {
    marginBottom: spacing.lg,
  },
  emptyTitle: {
    ...typography.heading2,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    color: colors.text.secondary,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  sectionHeader: {
    paddingVertical: spacing.md,
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  notificationItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.md,
  },
  notificationItemUnread: {
    backgroundColor: '#F0F7FF',
    borderLeftWidth: 4,
    borderLeftColor: '#2563EB',
  },
  notificationIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    flexShrink: 0,
  },
  notificationContent: {
    flex: 1,
  },
  notificationTitle: {
    ...typography.button,
    color: colors.text.primary,
  },
  notificationMessage: {
    ...typography.bodySmall,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  notificationTime: {
    ...typography.caption,
    color: colors.text.tertiary,
    marginTop: spacing.xs,
  },
  unreadDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#2563EB',
    marginTop: spacing.sm,
  },
});

export default NotificationsScreen;
