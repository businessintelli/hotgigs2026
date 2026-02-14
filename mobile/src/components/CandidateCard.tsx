import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, shadows, colors } from '@theme/index';
import { Candidate } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

interface CandidateCardProps {
  candidate: Candidate;
  onPress?: (candidate: Candidate) => void;
  onCall?: (candidate: Candidate) => void;
  onEmail?: (candidate: Candidate) => void;
  onSubmit?: (candidate: Candidate) => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  onPress,
  onCall,
  onEmail,
  onSubmit,
}) => {
  const handleCall = () => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    onCall?.(candidate);
  };

  const handleEmail = () => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    onEmail?.(candidate);
  };

  const handleSubmit = () => {
    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });
    onSubmit?.(candidate);
  };

  const renderStars = (rating: number) => {
    return (
      <View style={styles.starsContainer}>
        {[1, 2, 3, 4, 5].map((star) => (
          <MaterialIcons
            key={star}
            name={star <= rating ? 'star' : 'star-outline'}
            size={14}
            color={star <= rating ? '#FCD34D' : '#D1D5DB'}
          />
        ))}
      </View>
    );
  };

  return (
    <TouchableOpacity
      style={[styles.card, shadows.sm]}
      onPress={() => onPress?.(candidate)}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        {candidate.avatar ? (
          <Image
            source={{ uri: candidate.avatar }}
            style={styles.avatar}
          />
        ) : (
          <View style={[styles.avatar, styles.avatarPlaceholder]}>
            <Text style={styles.avatarText}>
              {candidate.first_name[0]}
              {candidate.last_name[0]}
            </Text>
          </View>
        )}

        <View style={styles.mainInfo}>
          <Text style={styles.name}>
            {candidate.first_name} {candidate.last_name}
          </Text>
          <Text style={styles.title}>{candidate.current_title}</Text>
          <View style={styles.ratingContainer}>
            {renderStars(candidate.ratings)}
            <Text style={styles.ratingText}>({candidate.ratings})</Text>
          </View>
        </View>
      </View>

      <View style={styles.details}>
        <View style={styles.detailRow}>
          <MaterialIcons name="location-on" size={16} color={colors.text.secondary} />
          <Text style={styles.detailText}>{candidate.location}</Text>
        </View>
        <View style={styles.detailRow}>
          <MaterialIcons name="work" size={16} color={colors.text.secondary} />
          <Text style={styles.detailText}>
            {candidate.experience_years} years experience
          </Text>
        </View>
      </View>

      {candidate.skills.length > 0 && (
        <View style={styles.skillsContainer}>
          {candidate.skills.slice(0, 3).map((skill, index) => (
            <View key={index} style={styles.skillTag}>
              <Text style={styles.skillText}>{skill}</Text>
            </View>
          ))}
          {candidate.skills.length > 3 && (
            <Text style={styles.moreSkills}>
              +{candidate.skills.length - 3} more
            </Text>
          )}
        </View>
      )}

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionBtn} onPress={handleCall}>
          <MaterialIcons name="call" size={18} color="#2563EB" />
          <Text style={styles.actionText}>Call</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionBtn} onPress={handleEmail}>
          <MaterialIcons name="email" size={18} color="#2563EB" />
          <Text style={styles.actionText}>Email</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionBtn, styles.submitBtn]}
          onPress={handleSubmit}
        >
          <MaterialIcons name="send" size={18} color="#FFFFFF" />
          <Text style={[styles.actionText, styles.submitText]}>Submit</Text>
        </TouchableOpacity>
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
    marginBottom: spacing.md,
    gap: spacing.md,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
  },
  avatarPlaceholder: {
    backgroundColor: '#E5E7EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    ...typography.button,
    color: colors.text.primary,
  },
  mainInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  name: {
    ...typography.heading3,
    color: colors.text.primary,
  },
  title: {
    ...typography.bodySmall,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  starsContainer: {
    flexDirection: 'row',
    gap: 2,
  },
  ratingText: {
    ...typography.caption,
    color: colors.text.tertiary,
  },
  details: {
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  detailRow: {
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
  actions: {
    flexDirection: 'row',
    gap: spacing.sm,
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
  submitBtn: {
    backgroundColor: '#2563EB',
  },
  actionText: {
    ...typography.caption,
    color: '#2563EB',
    fontWeight: '600',
  },
  submitText: {
    color: '#FFFFFF',
  },
});
