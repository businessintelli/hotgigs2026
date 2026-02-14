import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { ChatMessage, TypingIndicator } from './ChatMessage';
import type { ChatMessage as ChatMessageType } from '@/types';

interface ChatWindowProps {
  messages: ChatMessageType[];
  loading?: boolean;
  onSendMessage: (content: string) => Promise<void>;
  suggestedActions?: string[];
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  loading = false,
  onSendMessage,
  suggestedActions,
}) => {
  const [input, setInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSubmitting) return;

    const message = input.trim();
    setInput('');
    setIsSubmitting(true);

    try {
      await onSendMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSuggestedAction = async (action: string) => {
    setInput(action);
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-neutral-800 rounded-lg">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <p className="text-lg font-semibold text-neutral-900 dark:text-white mb-2">
                Start a conversation
              </p>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Ask anything about your recruitment pipeline
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                content={msg.content}
                role={msg.role}
                timestamp={new Date(msg.created_at).toLocaleTimeString()}
              />
            ))}
            {loading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Suggested Actions */}
      {suggestedActions && suggestedActions.length > 0 && messages.length === 0 && (
        <div className="px-4 py-3 border-t border-neutral-200 dark:border-neutral-700">
          <p className="text-xs font-semibold text-neutral-600 dark:text-neutral-400 mb-2">
            Try asking:
          </p>
          <div className="space-y-2">
            {suggestedActions.slice(0, 3).map((action, i) => (
              <button
                key={i}
                onClick={() => handleSuggestedAction(action)}
                className="w-full text-left px-3 py-2 text-sm rounded border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250 truncate"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSendMessage}
        className="border-t border-neutral-200 dark:border-neutral-700 p-4"
      >
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isSubmitting || loading}
            className={clsx(
              'flex-1 rounded-lg border border-neutral-200 dark:border-neutral-700',
              'bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white',
              'placeholder-neutral-500 dark:placeholder-neutral-400',
              'px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          />
          <button
            type="submit"
            disabled={!input.trim() || isSubmitting || loading}
            className={clsx(
              'p-2 rounded-lg transition-all duration-250',
              'bg-primary-500 hover:bg-primary-600 text-white',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};
