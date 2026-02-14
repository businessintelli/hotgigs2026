import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useInfiniteQuery } from '@tanstack/react-query';
import { spacing, typography, colors } from '@theme/index';
import { apiClient } from '@api/client';
import { CandidateCard } from '@components/CandidateCard';
import { SearchBar } from '@components/SearchBar';
import { Candidate, PaginatedResponse } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

const CandidatesScreen: React.FC = () => {
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
    queryKey: ['candidates', searchQuery],
    queryFn: async ({ pageParam = 1 }) => {
      if (searchQuery) {
        const response = await apiClient.candidates.search(searchQuery);
        return {
          data: response.data,
          total: response.data.length,
          page: 1,
          page_size: 20,
          total_pages: 1,
        } as PaginatedResponse<Candidate>;
      }

      const response = await apiClient.candidates.list(pageParam, 20);
      return response.data as PaginatedResponse<Candidate>;
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

  const handleCall = (candidate: Candidate) => {
    RNHapticFeedback.trigger('impactMedium', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    Linking.openURL(`tel:${candidate.phone}`);
  };

  const handleEmail = (candidate: Candidate) => {
    RNHapticFeedback.trigger('impactMedium', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    Linking.openURL(`mailto:${candidate.email}`);
  };

  const handleSubmit = (candidate: Candidate) => {
    RNHapticFeedback.trigger('impactMedium', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    // Navigate to submission screen or show selection modal
  };

  const candidates = data?.pages.flatMap((page) => page.data) || [];

  return (
    <SafeAreaView style={styles.container}>
      <SearchBar
        placeholder="Search candidates..."
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      {isLoading && !candidates.length ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      ) : candidates.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyTitle}>No Candidates Found</Text>
          <Text style={styles.emptyText}>
            {searchQuery ? 'Try a different search' : 'Start searching for candidates'}
          </Text>
        </View>
      ) : (
        <FlatList
          data={candidates}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={({ item }) => (
            <CandidateCard
              candidate={item}
              onCall={handleCall}
              onEmail={handleEmail}
              onSubmit={handleSubmit}
            />
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
  loadingMore: {
    paddingVertical: spacing.lg,
    alignItems: 'center',
  },
});

export default CandidatesScreen;
