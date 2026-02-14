import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useInfiniteQuery } from '@tanstack/react-query';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, colors, shadows } from '@theme/index';
import { apiClient } from '@api/client';
import { SearchBar } from '@components/SearchBar';
import { StatusBadge } from '@components/StatusBadge';
import { Contract, PaginatedResponse } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

const ContractsScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['contracts', searchQuery],
    queryFn: async ({ pageParam = 1 }) => {
      const response = await apiClient.contracts.list(pageParam, 20);
      return response.data as PaginatedResponse<Contract>;
    },
    getNextPageParam: (lastPage) =>
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    staleTime: 5 * 60 * 1000,
  });

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleLoadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  };

  const handleViewContract = (contract: Contract) => {
    RNHapticFeedback.trigger('impactMedium', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    Linking.openURL(contract.document_url);
  };

  const contracts = data?.pages.flatMap((page) => page.data) || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return 'schedule';
      case 'signed':
        return 'done';
      case 'executed':
        return 'verified';
      case 'expired':
        return 'error';
      default:
        return 'description';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return '#F59E0B';
      case 'signed':
        return '#3B82F6';
      case 'executed':
        return '#10B981';
      case 'expired':
        return '#DC2626';
      default:
        return '#6B7280';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <SearchBar
        placeholder="Search contracts..."
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      {isLoading && !contracts.length ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      ) : contracts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyTitle}>No Contracts</Text>
          <Text style={styles.emptyText}>
            {searchQuery ? 'Try a different search' : 'No contracts to display'}
          </Text>
        </View>
      ) : (
        <FlatList
          data={contracts}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[styles.contractCard, shadows.sm]}
              onPress={() => handleViewContract(item)}
              activeOpacity={0.7}
            >
              <View style={styles.contractHeader}>
                <View
                  style={[
                    styles.statusIcon,
                    {
                      backgroundColor: getStatusColor(item.status),
                    },
                  ]}
                >
                  <MaterialIcons
                    name={getStatusIcon(item.status)}
                    size={24}
                    color="#FFFFFF"
                  />
                </View>

                <View style={styles.contractInfo}>
                  <Text style={styles.contractTitle}>{item.title}</Text>
                  <Text style={styles.candidateName}>{item.candidate_name}</Text>
                </View>

                <StatusBadge status={item.status} size="sm" />
              </View>

              <View style={styles.contractDates}>
                <View style={styles.dateItem}>
                  <MaterialIcons
                    name="calendar-today"
                    size={14}
                    color={colors.text.tertiary}
                  />
                  <Text style={styles.dateLabel}>Created</Text>
                  <Text style={styles.dateValue}>
                    {new Date(item.created_date).toLocaleDateString()}
                  </Text>
                </View>

                {item.signature_date && (
                  <View style={styles.dateItem}>
                    <MaterialIcons
                      name="check-circle"
                      size={14}
                      color={colors.status.success}
                    />
                    <Text style={styles.dateLabel}>Signed</Text>
                    <Text style={styles.dateValue}>
                      {new Date(item.signature_date).toLocaleDateString()}
                    </Text>
                  </View>
                )}

                {item.expiry_date && (
                  <View style={styles.dateItem}>
                    <MaterialIcons
                      name="event-note"
                      size={14}
                      color={colors.text.tertiary}
                    />
                    <Text style={styles.dateLabel}>Expires</Text>
                    <Text
                      style={[
                        styles.dateValue,
                        new Date(item.expiry_date) < new Date() &&
                          styles.expiredDate,
                      ]}
                    >
                      {new Date(item.expiry_date).toLocaleDateString()}
                    </Text>
                  </View>
                )}
              </View>

              <View style={styles.contractFooter}>
                <Text style={styles.viewLink}>Tap to view contract</Text>
                <MaterialIcons
                  name="open-in-new"
                  size={16}
                  color="#2563EB"
                />
              </View>
            </TouchableOpacity>
          )}
          contentContainerStyle={styles.listContent}
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.3}
          ListFooterComponent={
            isFetchingNextPage ? (
              <View style={styles.loadingMore}>
                <ActivityIndicator size="small" color="#2563EB" />
              </View>
            ) : null
          }
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
  },
  emptyTitle: {
    ...typography.heading2,
    color: colors.text.primary,
    marginBottom: spacing.md,
  },
  emptyText: {
    ...typography.body,
    color: colors.text.secondary,
    textAlign: 'center',
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  contractCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  contractHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  statusIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  contractInfo: {
    flex: 1,
  },
  contractTitle: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  candidateName: {
    ...typography.bodySmall,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  contractDates: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.lg,
    paddingBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    paddingBottom: spacing.md,
  },
  dateItem: {
    flex: 1,
    alignItems: 'center',
    gap: spacing.xs,
  },
  dateLabel: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
  dateValue: {
    ...typography.bodySmall,
    color: colors.text.primary,
    fontWeight: '600',
  },
  expiredDate: {
    color: colors.status.error,
  },
  contractFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  viewLink: {
    ...typography.bodySmall,
    color: '#2563EB',
    fontWeight: '600',
  },
  loadingMore: {
    paddingVertical: spacing.lg,
    alignItems: 'center',
  },
});

export default ContractsScreen;
