import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  SectionList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, colors, shadows } from '@theme/index';
import { apiClient } from '@api/client';
import { SearchBar } from '@components/SearchBar';
import { StatusBadge } from '@components/StatusBadge';
import { Submission } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

interface SubmissionGroup {
  title: string;
  data: Submission[];
}

const SubmissionsScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: submissions = [], isLoading, refetch } = useQuery({
    queryKey: ['submissions', searchQuery],
    queryFn: async () => {
      const response = await apiClient.submissions.list(1, 100);
      return response.data.data as Submission[];
    },
    staleTime: 5 * 60 * 1000,
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
  };

  const groupSubmissions = (subs: Submission[]): SubmissionGroup[] => {
    const statuses = ['submitted', 'screening', 'interview', 'offer', 'hired', 'rejected'];
    const grouped: Record<string, Submission[]> = {};

    statuses.forEach((status) => {
      grouped[status] = subs.filter((s) => s.status === status);
    });

    return Object.entries(grouped)
      .filter(([_, items]) => items.length > 0)
      .map(([title, data]) => ({
        title: title.charAt(0).toUpperCase() + title.slice(1),
        data,
      }));
  };

  const sections = groupSubmissions(submissions);

  const renderSubmissionItem = ({ item }: { item: Submission }) => {
    const isExpanded = expandedId === item.id;

    return (
      <TouchableOpacity
        style={[styles.submissionCard, shadows.sm]}
        onPress={() => setExpandedId(isExpanded ? null : item.id)}
        activeOpacity={0.7}
      >
        <View style={styles.submissionHeader}>
          <View style={styles.submissionInfo}>
            <Text style={styles.candidateName}>
              {item.candidate.first_name} {item.candidate.last_name}
            </Text>
            <Text style={styles.requirementTitle}>
              {item.requirement.title}
            </Text>
            <Text style={styles.submissionDate}>
              Submitted {new Date(item.submitted_date).toLocaleDateString()}
            </Text>
          </View>

          <View style={styles.submissionActions}>
            <StatusBadge status={item.status} size="sm" />
            <MaterialIcons
              name={isExpanded ? 'expand-less' : 'expand-more'}
              size={24}
              color={colors.text.secondary}
            />
          </View>
        </View>

        {isExpanded && (
          <View style={styles.submissionExpanded}>
            <View style={styles.expandedContent}>
              {item.notes && (
                <View style={styles.noteSection}>
                  <Text style={styles.noteLabel}>Notes</Text>
                  <Text style={styles.noteText}>{item.notes}</Text>
                </View>
              )}

              {item.interview_scheduled && (
                <View style={styles.interviewSection}>
                  <MaterialIcons
                    name="event"
                    size={16}
                    color="#2563EB"
                  />
                  <Text style={styles.interviewText}>
                    Interview: {new Date(item.interview_scheduled).toLocaleString()}
                  </Text>
                </View>
              )}

              {item.rating && (
                <View style={styles.ratingSection}>
                  <Text style={styles.ratingLabel}>Rating</Text>
                  <View style={styles.starsContainer}>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <MaterialIcons
                        key={star}
                        name={star <= item.rating! ? 'star' : 'star-outline'}
                        size={16}
                        color="#FCD34D"
                      />
                    ))}
                  </View>
                </View>
              )}

              {item.offer_amount && (
                <View style={styles.offerSection}>
                  <Text style={styles.offerLabel}>Offer Amount</Text>
                  <Text style={styles.offerAmount}>
                    ${item.offer_amount.toLocaleString()}
                  </Text>
                </View>
              )}
            </View>

            <View style={styles.expandedActions}>
              <TouchableOpacity style={styles.actionBtn}>
                <MaterialIcons
                  name="edit"
                  size={18}
                  color="#2563EB"
                />
                <Text style={styles.actionBtnText}>Edit</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.actionBtn}>
                <MaterialIcons
                  name="message"
                  size={18}
                  color="#2563EB"
                />
                <Text style={styles.actionBtnText}>Message</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.actionBtn}>
                <MaterialIcons
                  name="schedule"
                  size={18}
                  color="#2563EB"
                />
                <Text style={styles.actionBtnText}>Schedule</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const renderSectionHeader = ({ section: { title } }: { section: SubmissionGroup }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );

  if (isLoading && !submissions.length) {
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
      <SearchBar
        placeholder="Search submissions..."
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      {submissions.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyTitle}>No Submissions</Text>
          <Text style={styles.emptyText}>
            {searchQuery ? 'Try a different search' : 'No submissions yet'}
          </Text>
        </View>
      ) : (
        <SectionList
          sections={sections}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={renderSubmissionItem}
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
  sectionHeader: {
    paddingVertical: spacing.md,
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  submissionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: spacing.md,
    overflow: 'hidden',
  },
  submissionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: spacing.lg,
  },
  submissionInfo: {
    flex: 1,
  },
  candidateName: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  requirementTitle: {
    ...typography.bodySmall,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  submissionDate: {
    ...typography.caption,
    color: colors.text.tertiary,
    marginTop: spacing.xs,
  },
  submissionActions: {
    alignItems: 'flex-end',
    gap: spacing.sm,
  },
  submissionExpanded: {
    backgroundColor: '#F9FAFB',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  expandedContent: {
    marginBottom: spacing.md,
    gap: spacing.md,
  },
  noteSection: {
    gap: spacing.sm,
  },
  noteLabel: {
    ...typography.caption,
    color: colors.text.secondary,
    fontWeight: '600',
  },
  noteText: {
    ...typography.bodySmall,
    color: colors.text.primary,
  },
  interviewSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  interviewText: {
    ...typography.bodySmall,
    color: colors.text.primary,
  },
  ratingSection: {
    gap: spacing.sm,
  },
  ratingLabel: {
    ...typography.caption,
    color: colors.text.secondary,
    fontWeight: '600',
  },
  starsContainer: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  offerSection: {
    gap: spacing.sm,
  },
  offerLabel: {
    ...typography.caption,
    color: colors.text.secondary,
    fontWeight: '600',
  },
  offerAmount: {
    ...typography.heading3,
    color: colors.status.success,
  },
  expandedActions: {
    flexDirection: 'row',
    gap: spacing.sm,
    justifyContent: 'space-between',
  },
  actionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.sm,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
    gap: spacing.xs,
  },
  actionBtnText: {
    ...typography.caption,
    color: '#2563EB',
    fontWeight: '600',
  },
});

export default SubmissionsScreen;
