import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, shadows, colors } from '@theme/index';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon: string;
  color: string;
  onPress?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
  color,
  onPress,
}) => {
  const getTrendColor = () => {
    if (trend === 'up') return colors.status.success;
    if (trend === 'down') return colors.status.error;
    return colors.text.tertiary;
  };

  const getTrendIcon = () => {
    if (trend === 'up') return 'trending-up';
    if (trend === 'down') return 'trending-down';
    return 'remove';
  };

  return (
    <TouchableOpacity
      style={[styles.card, shadows.md]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={[styles.iconContainer, { backgroundColor: color }]}>
          <MaterialIcons name={icon} size={24} color="#FFFFFF" />
        </View>
        {change !== undefined && (
          <View style={styles.trendContainer}>
            <MaterialIcons
              name={getTrendIcon()}
              size={16}
              color={getTrendColor()}
            />
            <Text style={[styles.trendText, { color: getTrendColor() }]}>
              {change > 0 ? '+' : ''}{change}%
            </Text>
          </View>
        )}
      </View>

      <View style={styles.content}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.value}>{value}</Text>
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
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  trendText: {
    fontSize: 12,
    fontWeight: '600',
  },
  content: {
    gap: spacing.sm,
  },
  title: {
    ...typography.caption,
    color: colors.text.secondary,
  },
  value: {
    ...typography.heading2,
    color: colors.text.primary,
  },
});
