import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { spacing, typography, shadows, colors } from '@theme/index';
import { ChatMessage } from '@types/index';
import { format } from 'date-fns';

interface ChatBubbleProps {
  message: ChatMessage;
  isCurrentUser: boolean;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  message,
  isCurrentUser,
}) => {
  return (
    <View
      style={[
        styles.container,
        isCurrentUser ? styles.userContainer : styles.assistantContainer,
      ]}
    >
      <View
        style={[
          styles.bubble,
          isCurrentUser ? styles.userBubble : styles.assistantBubble,
          shadows.sm,
        ]}
      >
        <Text
          style={[
            styles.text,
            isCurrentUser ? styles.userText : styles.assistantText,
          ]}
        >
          {message.content}
        </Text>

        {message.attachments && message.attachments.length > 0 && (
          <View style={styles.attachmentsContainer}>
            {message.attachments.map((attachment, index) => (
              <View key={index} style={styles.attachment}>
                <Text style={styles.attachmentText}>{attachment.name}</Text>
              </View>
            ))}
          </View>
        )}
      </View>

      <Text style={styles.timestamp}>
        {format(new Date(message.timestamp), 'HH:mm')}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
  },
  userContainer: {
    alignItems: 'flex-end',
  },
  assistantContainer: {
    alignItems: 'flex-start',
  },
  bubble: {
    maxWidth: '80%',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 12,
  },
  userBubble: {
    backgroundColor: '#2563EB',
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: '#F3F4F6',
    borderBottomLeftRadius: 4,
  },
  text: {
    ...typography.body,
  },
  userText: {
    color: '#FFFFFF',
  },
  assistantText: {
    color: colors.text.primary,
  },
  timestamp: {
    ...typography.caption,
    color: colors.text.tertiary,
    marginTop: spacing.xs,
  },
  attachmentsContainer: {
    marginTop: spacing.sm,
    gap: spacing.xs,
  },
  attachment: {
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
  },
  attachmentText: {
    ...typography.caption,
    color: '#FFFFFF',
  },
});
