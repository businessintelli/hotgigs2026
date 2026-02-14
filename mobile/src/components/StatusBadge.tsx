import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { spacing, typography, colors } from '@theme/index';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'filled' | 'outlined';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  variant = 'filled',
}) => {
  const getStatusColor = () => {
    switch (status.toLowerCase()) {
      case 'open':
        return { bg: '#DBEAFE', text: '#0369A1' };
      case 'filled':
        return { bg: '#D1FAE5', text: '#047857' };
      case 'closed':
        return { bg: '#F3E8FF', text: '#7E22CE' };
      case 'urgent':
        return { bg: '#FEE2E2', text: '#DC2626' };
      case 'active':
        return { bg: '#D1FAE5', text: '#047857' };
      case 'pending':
        return { bg: '#FEF3C7', text: '#92400E' };
      case 'submitted':
        return { bg: '#DBEAFE', text: '#0369A1' };
      case 'screening':
        return { bg: '#FCD34D', text: '#78350F' };
      case 'interview':
        return { bg: '#DBEAFE', text: '#0369A1' };
      case 'offer':
        return { bg: '#D1FAE5', text: '#047857' };
      case 'hired':
        return { bg: '#D1FAE5', text: '#047857' };
      case 'rejected':
        return { bg: '#FEE2E2', text: '#DC2626' };
      default:
        return { bg: '#E5E7EB', text: '#6B7280' };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return { paddingVertical: spacing.xs, paddingHorizontal: spacing.sm };
      case 'lg':
        return { paddingVertical: spacing.md, paddingHorizontal: spacing.lg };
      case 'md':
      default:
        return { paddingVertical: spacing.sm, paddingHorizontal: spacing.md };
    }
  };

  const statusColor = getStatusColor();
  const sizeStyles = getSizeStyles();

  return (
    <View
      style={[
        styles.badge,
        variant === 'filled'
          ? { backgroundColor: statusColor.bg }
          : {
              backgroundColor: 'transparent',
              borderWidth: 1,
              borderColor: statusColor.text,
            },
        sizeStyles,
      ]}
    >
      <Text style={[styles.text, { color: statusColor.text }]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  text: {
    ...typography.caption,
    fontWeight: '600',
  },
});
