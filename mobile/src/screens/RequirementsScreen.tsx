import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { spacing, typography, colors } from '@theme/index';
import { apiClient } from '@api/client';
import { useAppStore } from '@store/index';
import { RequirementCard } from '@components/RequirementCard';
import { SearchBar } from '@components/SearchBar';
import { Requirement, PaginatedResponse } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

type FilterStatus = 'All' | 'Active' | 'Filled' | 'Closed';

const RequirementsScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('All');
  const [refreshing, setRefreshing] = useState(false);

  const filters = {
    status:
      filterStatus === 'All'
        ? undefined
        : filterStatus.toLowerCase(),
  };

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['requirements', searchQuery, filterStatus],
    queryFn: async ({ pageParam = 1 }) => {
      const response = await apiClient.requirements.list(pageParam, 20, filters);
      return response.data as PaginatedResponse<Requirement>;
    },
    getNextPageParam: (lastPage) =>
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
    staleTime: 5 * 60 * 1000,
  });

  const handleSearch = async (query: string) => {
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
      RNHapticFeedback.trigger('selection', {
        enableVibrateFallback: true,
        ignoreAndroidSystemSettings: false,
      });
      fetchNextPage();
    }
  };

  const requirements = data?.pages.flatMap((page) => page.data) || [];

  const filterButtons: FilterStatus[] = ['All', 'Active', 'Filled', 'Closed'];

  return (
    <SafeAreaView style={styles.container}>
      <SearchBar
        placeholder="Search requirements..."
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      <View style={styles.filterContainer}>
        {filterButtons.map((button) => (
          <View
            key={button}
            style={[
              styles.filterButton,
              filterStatus === button && styles.filterButtonActive,
            ]}
          >
            <Text
              onPress={() => {
                setFilterStatus(button);
                RNHapticFeedback.trigger('selection', {
                  enableVibrateFallback: true,
                  ignoreAndroidSystemSettings: false,
                });
              }}
              style={[
                styles.filterButtonText,
                filterStatus === button && styles.filterButtonTextActive,
              ]}
            >
              {button}
            </Text>
          </View>
        ))}
      </View>

      {isLoading && !requirements.length ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      ) : requirements.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyTitle}>No Requirements Found</Text>
          <Text style={styles.emptyText}>
            {searchQuery ? 'Try a different search' : 'Create a new requirement to get started'}
          </Text>
        </View>
      ) : (
        <FlatList
          data={requirements}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={({ item }) => <RequirementCard requirement={item} />}
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
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    gap: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  filterButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  filterButtonActive: {
    backgroundColor: '#2563EB',
    borderColor: '#2563EB',
  },
  filterButtonText: {
    ...typography.caption,
    color: colors.text.secondary,
    fontWeight: '600',
  },
  filterButtonTextActive: {
    color: '#FFFFFF',
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
  loadingMore: {
    paddingVertical: spacing.lg,
    alignItems: 'center',
  },
});

export default RequirementsScreen;
