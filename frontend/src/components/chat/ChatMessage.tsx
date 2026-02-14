import React from 'react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  content: string;
  role: 'user' | 'assistant';
  timestamp?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  content,
  role,
  timestamp,
}) => {
  return (
    <div
      className={clsx(
        'flex gap-3 mb-4',
        role === 'user' && 'justify-end'
      )}
    >
      <div
        className={clsx(
          'max-w-xs md:max-w-md rounded-lg px-4 py-2',
          role === 'user'
            ? 'bg-primary-500 text-white'
            : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-900 dark:text-white'
        )}
      >
        <div className={clsx(
          'text-sm',
          role === 'assistant' && 'prose prose-sm dark:prose-invert max-w-none'
        )}>
          {role === 'assistant' ? (
            <ReactMarkdown>{content}</ReactMarkdown>
          ) : (
            content
          )}
        </div>
        {timestamp && (
          <p className={clsx(
            'text-xs mt-1',
            role === 'user' ? 'text-primary-100' : 'text-neutral-500 dark:text-neutral-400'
          )}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
};

export const TypingIndicator: React.FC = () => (
  <div className="flex gap-1">
    <div className="w-2 h-2 bg-neutral-400 dark:bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
    <div className="w-2 h-2 bg-neutral-400 dark:bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
    <div className="w-2 h-2 bg-neutral-400 dark:bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
  </div>
);
