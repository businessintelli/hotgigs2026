import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { spacing, typography, colors, shadows } from '@theme/index';
import { apiClient } from '@api/client';
import { useAppStore } from '@store/index';
import { KPICard } from '@components/KPICard';
import { PipelineStage } from '@components/PipelineStage';
import { DashboardStats } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

const DashboardScreen: React.FC = () => {
  const user = useAppStore((state) => state.auth.user);
  const [refreshing, setRefreshing] = useState(false);

  const {
    data: stats,
    isLoading,
    refetch,
  } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.dashboard.getStats();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    await refetch();
    setRefreshing(false);
  };

  const maxPipelineCount = stats?.pipeline
    ? Math.max(...stats.pipeline.map((s) => s.count))
    : 0;

  if (isLoading && !stats) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>
              Good {new Date().getHours() < 12 ? 'Morning' : 'Afternoon'},
            </Text>
            <Text style={styles.userName}>{user?.name || 'User'}</Text>
          </View>
          <View style={styles.headerIcon}>
            <MaterialIcons name="waving-hand" size={32} color="#FCD34D" />
          </View>
        </View>

        {/* KPI Cards - 2x2 Grid */}
        <View style={styles.kpiGrid}>
          <View style={styles.kpiColumn}>
            <KPICard
              title="Open Requirements"
              value={stats?.open_requirements || 0}
              icon="assignment"
              color="#3B82F6"
              change={5}
              trend="up"
            />
            <KPICard
              title="Pending Submissions"
              value={stats?.pending_submissions || 0}
              icon="send"
              color="#8B5CF6"
              change={-2}
              trend="down"
            />
          </View>

          <View style={styles.kpiColumn}>
            <KPICard
              title="Active Candidates"
              value={stats?.active_candidates || 0}
              icon="people"
              color="#10B981"
              change={12}
              trend="up"
            />
            <KPICard
              title="Offers Pending"
              value={stats?.offers_pending || 0}
              icon="card-giftcard"
              color="#F59E0B"
              change={8}
              trend="up"
            />
          </View>
        </View>

        {/* Key Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Key Metrics</Text>

          <View style={[styles.metricCard, shadows.sm]}>
            <View style={styles.metricRow}>
              <View style={styles.metricLeft}>
                <Text style={styles.metricLabel}>Hire Rate</Text>
                <Text style={styles.metricValue}>
                  {stats?.hire_rate.toFixed(1) || 0}%
                </Text>
              </View>
              <View style={styles.metricChart}>
                <View
                  style={[
                    styles.metricBar,
                    {
                      width: `${stats?.hire_rate || 0}%`,
                      backgroundColor: '#10B981',
                    },
                  ]}
                />
              </View>
            </View>
          </View>

          <View style={[styles.metricCard, shadows.sm]}>
            <View style={styles.metricRow}>
              <View style={styles.metricLeft}>
                <Text style={styles.metricLabel}>Avg Time to Hire</Text>
                <Text style={styles.metricValue}>
                  {stats?.avg_time_to_hire || 0} days
                </Text>
              </View>
              <MaterialIcons
                name="timer"
                size={32}
                color="#F59E0B"
              />
            </View>
          </View>
        </View>

        {/* Pipeline */}
        {stats?.pipeline && stats.pipeline.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Hiring Pipeline</Text>
            <View style={styles.pipelineContainer}>
              {stats.pipeline.map((stage, index) => (
                <PipelineStage
                  key={index}
                  stage={stage}
                  maxCount={maxPipelineCount}
                />
              ))}
            </View>
          </View>
        )}

        {/* Recent Activity */}
        {stats?.recent_activity && stats.recent_activity.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Recent Activity</Text>
              <TouchableOpacity>
                <Text style={styles.viewAll}>View All</Text>
              </TouchableOpacity>
            </View>

            {stats.recent_activity.slice(0, 5).map((activity, index) => (
              <View
                key={index}
                style={[
                  styles.activityItem,
                  index < stats.recent_activity.length - 1 &&
                    styles.activityItemBorder,
                ]}
              >
                <View style={styles.activityIcon}>
                  <MaterialIcons
                    name="circle"
                    size={8}
                    color="#2563EB"
                  />
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityAction}>{activity.action}</Text>
                  {activity.candidate && (
                    <Text style={styles.activityMeta}>
                      Candidate: {activity.candidate}
                    </Text>
                  )}
                  {activity.requirement && (
                    <Text style={styles.activityMeta}>
                      Role: {activity.requirement}
                    </Text>
                  )}
                </View>
                <Text style={styles.activityTime}>
                  {new Date(activity.timestamp).toLocaleDateString()}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>

          <TouchableOpacity style={[styles.actionButton, shadows.sm]}>
            <MaterialIcons name="add-circle" size={24} color="#2563EB" />
            <View style={styles.actionContent}>
              <Text style={styles.actionTitle}>New Requirement</Text>
              <Text style={styles.actionSubtitle}>Create a new job requirement</Text>
            </View>
            <MaterialIcons name="chevron-right" size={24} color="#9CA3AF" />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.actionButton, shadows.sm]}>
            <MaterialIcons name="search" size={24} color="#2563EB" />
            <View style={styles.actionContent}>
              <Text style={styles.actionTitle}>Search Candidates</Text>
              <Text style={styles.actionSubtitle}>Find matching candidates</Text>
            </View>
            <MaterialIcons name="chevron-right" size={24} color="#9CA3AF" />
          </TouchableOpacity>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },
  greeting: {
    ...typography.bodySmall,
    color: colors.text.secondary,
  },
  userName: {
    ...typography.heading2,
    color: colors.text.primary,
    marginTop: spacing.xs,
  },
  headerIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  kpiGrid: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  kpiColumn: {
    flex: 1,
  },
  section: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    ...typography.heading3,
    color: colors.text.primary,
    marginBottom: spacing.md,
  },
  viewAll: {
    ...typography.bodySmall,
    color: '#2563EB',
    fontWeight: '600',
  },
  metricCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metricLeft: {
    flex: 1,
  },
  metricLabel: {
    ...typography.bodySmall,
    color: colors.text.secondary,
    marginBottom: spacing.sm,
  },
  metricValue: {
    ...typography.heading2,
    color: colors.text.primary,
  },
  metricChart: {
    flex: 1,
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    marginLeft: spacing.lg,
    overflow: 'hidden',
  },
  metricBar: {
    height: '100%',
    borderRadius: 4,
  },
  pipelineContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
  },
  activityItem: {
    flexDirection: 'row',
    paddingVertical: spacing.md,
    gap: spacing.md,
  },
  activityItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  activityIcon: {
    justifyContent: 'center',
    alignItems: 'center',
    width: 24,
  },
  activityContent: {
    flex: 1,
  },
  activityAction: {
    ...typography.bodySmall,
    color: colors.text.primary,
    fontWeight: '600',
  },
  activityMeta: {
    ...typography.caption,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  activityTime: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
  actionButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.lg,
    marginBottom: spacing.md,
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    ...typography.button,
    color: colors.text.primary,
  },
  actionSubtitle: {
    ...typography.caption,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
});

export default DashboardScreen;
