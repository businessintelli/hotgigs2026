import React, { useState, useCallback } from 'react';
import clsx from 'clsx';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface SearchInputProps {
  placeholder?: string;
  value?: string;
  onSearch: (value: string) => void;
  className?: string;
  autoFocus?: boolean;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  placeholder = 'Search...',
  value = '',
  onSearch,
  className,
  autoFocus = false,
}) => {
  const [inputValue, setInputValue] = useState(value);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onSearch(newValue);
  }, [onSearch]);

  const handleClear = useCallback(() => {
    setInputValue('');
    onSearch('');
  }, [onSearch]);

  return (
    <div className={clsx('relative', className)}>
      <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 dark:text-neutral-500 pointer-events-none" />
      <input
        type="text"
        placeholder={placeholder}
        value={inputValue}
        onChange={handleChange}
        autoFocus={autoFocus}
        className={clsx(
          'w-full pl-10 pr-10 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700',
          'bg-white dark:bg-neutral-800',
          'text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'transition-all duration-250'
        )}
      />
      {inputValue && (
        <button
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors duration-250"
          type="button"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      )}
    </div>
  );
};
