import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { spacing, typography, colors } from '@theme/index';
import { PipelineData } from '@types/index';

interface PipelineStageProps {
  stage: PipelineData;
  maxCount: number;
}

export const PipelineStage: React.FC<PipelineStageProps> = ({
  stage,
  maxCount,
}) => {
  const barWidth = (stage.count / maxCount) * 100;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>{stage.stage}</Text>
        <Text style={styles.count}>{stage.count}</Text>
      </View>

      <View style={styles.barContainer}>
        <View
          style={[
            styles.bar,
            {
              width: `${barWidth}%`,
              backgroundColor: getStageColor(stage.stage),
            },
          ]}
        />
      </View>

      <Text style={styles.percentage}>{stage.percentage}%</Text>
    </View>
  );
};

const getStageColor = (stage: string): string => {
  switch (stage.toLowerCase()) {
    case 'submitted':
      return '#3B82F6';
    case 'screening':
      return '#F59E0B';
    case 'interview':
      return '#8B5CF6';
    case 'offer':
      return '#10B981';
    case 'hired':
      return '#34D399';
    default:
      return '#6B7280';
  }
};

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  label: {
    ...typography.bodySmall,
    color: colors.text.primary,
    fontWeight: '600',
  },
  count: {
    ...typography.bodySmall,
    color: colors.text.secondary,
  },
  barContainer: {
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  bar: {
    height: '100%',
    borderRadius: 4,
  },
  percentage: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
});
