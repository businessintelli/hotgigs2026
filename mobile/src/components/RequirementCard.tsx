import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, shadows, colors } from '@theme/index';
import { Requirement } from '@types/index';
import { StatusBadge } from './StatusBadge';

interface RequirementCardProps {
  requirement: Requirement;
  onPress?: (requirement: Requirement) => void;
}

export const RequirementCard: React.FC<RequirementCardProps> = ({
  requirement,
  onPress,
}) => {
  return (
    <TouchableOpacity
      style={[styles.card, shadows.sm]}
      onPress={() => onPress?.(requirement)}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={styles.title}>{requirement.title}</Text>
          <StatusBadge status={requirement.status} size="sm" />
        </View>
        {requirement.priority === 'urgent' && (
          <MaterialIcons name="priority-high" size={20} color="#DC2626" />
        )}
      </View>

      <View style={styles.detailsContainer}>
        <View style={styles.detailRow}>
          <MaterialIcons name="domain" size={16} color={colors.text.secondary} />
          <Text style={styles.detailText}>{requirement.department}</Text>
        </View>

        <View style={styles.detailRow}>
          <MaterialIcons name="location-on" size={16} color={colors.text.secondary} />
          <Text style={styles.detailText}>{requirement.location}</Text>
        </View>

        <View style={styles.detailRow}>
          <MaterialIcons name="trending-up" size={16} color={colors.text.secondary} />
          <Text style={styles.detailText}>
            {requirement.experience_level} level
          </Text>
        </View>

        <View style={styles.salaryRow}>
          <MaterialIcons name="paid" size={16} color={colors.text.secondary} />
          <Text style={styles.detailText}>
            {requirement.salary_range.currency} {requirement.salary_range.min / 1000}k -
            {requirement.salary_range.max / 1000}k
          </Text>
        </View>
      </View>

      {requirement.required_skills.length > 0 && (
        <View style={styles.skillsContainer}>
          {requirement.required_skills.slice(0, 4).map((skill, index) => (
            <View key={index} style={styles.skillTag}>
              <Text style={styles.skillText}>{skill}</Text>
            </View>
          ))}
          {requirement.required_skills.length > 4 && (
            <Text style={styles.moreSkills}>
              +{requirement.required_skills.length - 4}
            </Text>
          )}
        </View>
      )}

      <View style={styles.statsContainer}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{requirement.candidate_count}</Text>
          <Text style={styles.statLabel}>Candidates</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.stat}>
          <Text style={styles.statValue}>{requirement.applications_count}</Text>
          <Text style={styles.statLabel}>Applications</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.stat}>
          <Text style={styles.statValue}>
            {requirement.deadline
              ? Math.ceil(
                  (new Date(requirement.deadline).getTime() -
                    Date.now()) /
                    (1000 * 60 * 60 * 24)
                )
              : '—'}
          </Text>
          <Text style={styles.statLabel}>Days Left</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  titleContainer: {
    flex: 1,
    gap: spacing.sm,
  },
  title: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  detailsContainer: {
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  salaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  detailText: {
    ...typography.bodySmall,
    color: colors.text.secondary,
  },
  skillsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  skillTag: {
    backgroundColor: '#F0F4FF',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
  },
  skillText: {
    ...typography.caption,
    color: '#2563EB',
  },
  moreSkills: {
    ...typography.caption,
    color: colors.text.secondary,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  statsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  stat: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    ...typography.heading2,
    color: colors.text.primary,
  },
  statLabel: {
    ...typography.caption,
    color: colors.text.tertiary,
    marginTop: spacing.xs,
  },
  divider: {
    width: 1,
    height: 24,
    backgroundColor: '#E5E7EB',
  },
});
