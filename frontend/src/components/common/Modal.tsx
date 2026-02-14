import React, { useEffect } from 'react';
import clsx from 'clsx';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnEscape?: boolean;
  closeOnBackdropClick?: boolean;
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnEscape = true,
  closeOnBackdropClick = true,
}) => {
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (closeOnEscape && e.key === 'Escape') {
        onClose();
      }
    };

    const handleBackdropClick = (e: MouseEvent) => {
      if (
        closeOnBackdropClick &&
        e.target instanceof HTMLElement &&
        e.target.id === 'modal-backdrop'
      ) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('click', handleBackdropClick);

    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('click', handleBackdropClick);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose, closeOnEscape, closeOnBackdropClick]);

  if (!isOpen) return null;

  return (
    <div
      id="modal-backdrop"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70 backdrop-blur-sm"
    >
      <div className={clsx('w-full mx-4 rounded-lg bg-white dark:bg-neutral-800', sizeClasses[size])}>
        {title && (
          <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-700 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors duration-250"
              type="button"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
        )}
        <div className="px-6 py-4 max-h-[calc(100vh-240px)] overflow-y-auto">
          {children}
        </div>
        {footer && (
          <div className="flex gap-3 border-t border-neutral-200 dark:border-neutral-700 px-6 py-4">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
