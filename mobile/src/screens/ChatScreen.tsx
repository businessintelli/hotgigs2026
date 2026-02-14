import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useMutation, useQuery } from '@tanstack/react-query';
import { MaterialIcons } from '@react-native-vector-icons/MaterialIcons';
import { spacing, typography, colors, shadows } from '@theme/index';
import { apiClient } from '@api/client';
import { ChatBubble } from '@components/ChatBubble';
import { ChatMessage } from '@types/index';
import RNHapticFeedback from 'react-native-haptic-feedback';

const ChatScreen: React.FC = () => {
  const [messageText, setMessageText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  const { data: messages = [], isLoading } = useQuery({
    queryKey: ['chat-history'],
    queryFn: async () => {
      const response = await apiClient.chat.getHistory(100);
      return response.data as ChatMessage[];
    },
    staleTime: 1 * 60 * 1000,
  });

  const sendMutation = useMutation({
    mutationFn: (message: string) =>
      apiClient.chat.sendMessage(message),
    onSuccess: (response) => {
      // Add new messages to the list
      setMessageText('');
      scrollToBottom();
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
    },
  });

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const handleSend = async () => {
    if (!messageText.trim()) return;

    RNHapticFeedback.trigger('selection', {
      enableVibrateFallback: true,
      ignoreAndroidSystemSettings: false,
    });

    await sendMutation.mutateAsync(messageText.trim());
  };

  const quickActions = [
    { icon: 'search', label: 'Search Candidates', action: 'Find candidates with specific skills' },
    { icon: 'assignment', label: 'Job Description', action: 'Generate job description' },
    { icon: 'trending-up', label: 'Pipeline Analysis', action: 'Analyze hiring pipeline' },
    { icon: 'calendar-today', label: 'Schedule', action: 'Schedule interviews' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      {messages.length === 0 && !isLoading ? (
        <View style={styles.emptyState}>
          <View style={styles.aiIcon}>
            <MaterialIcons name="smart-toy" size={48} color="#2563EB" />
          </View>

          <Text style={styles.welcomeTitle}>HR AI Copilot</Text>
          <Text style={styles.welcomeSubtitle}>
            Your intelligent assistant for recruitment and talent management
          </Text>

          <View style={styles.quickActionsContainer}>
            <Text style={styles.quickActionsTitle}>Quick Actions</Text>
            {quickActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.quickAction, shadows.sm]}
                onPress={() => setMessageText(action.action)}
              >
                <MaterialIcons
                  name={action.icon as any}
                  size={24}
                  color="#2563EB"
                />
                <View style={styles.quickActionText}>
                  <Text style={styles.quickActionTitle}>{action.label}</Text>
                  <Text style={styles.quickActionDesc}>{action.action}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={({ item }) => (
            <ChatBubble
              message={item}
              isCurrentUser={item.sender === 'user'}
            />
          )}
          contentContainerStyle={styles.messagesContainer}
          onContentSizeChange={scrollToBottom}
          ListHeaderComponent={
            isLoading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="small" color="#2563EB" />
              </View>
            ) : null
          }
          scrollEnabled={true}
        />
      )}

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inputContainer}
      >
        <View style={[styles.inputWrapper, shadows.md]}>
          <TextInput
            style={styles.input}
            placeholder="Ask me anything..."
            placeholderTextColor={colors.text.tertiary}
            value={messageText}
            onChangeText={setMessageText}
            multiline
            maxHeight={100}
            editable={!sendMutation.isPending}
          />

          <TouchableOpacity
            style={[
              styles.sendButton,
              !messageText.trim() && styles.sendButtonDisabled,
            ]}
            onPress={handleSend}
            disabled={!messageText.trim() || sendMutation.isPending}
          >
            {sendMutation.isPending ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <MaterialIcons name="send" size={20} color="#FFFFFF" />
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  aiIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  welcomeTitle: {
    ...typography.heading2,
    color: colors.text.primary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  welcomeSubtitle: {
    ...typography.body,
    color: colors.text.secondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  quickActionsContainer: {
    width: '100%',
    gap: spacing.md,
  },
  quickActionsTitle: {
    ...typography.heading3,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  quickAction: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.lg,
  },
  quickActionText: {
    flex: 1,
  },
  quickActionTitle: {
    ...typography.button,
    color: colors.text.primary,
  },
  quickActionDesc: {
    ...typography.caption,
    color: colors.text.secondary,
    marginTop: spacing.xs,
  },
  messagesContainer: {
    paddingVertical: spacing.lg,
  },
  loadingContainer: {
    paddingVertical: spacing.lg,
    alignItems: 'center',
  },
  inputContainer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: '#F9FAFB',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 48,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text.primary,
    maxHeight: 100,
    paddingVertical: spacing.sm,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
});

export default ChatScreen;
