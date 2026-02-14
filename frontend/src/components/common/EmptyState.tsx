import React from 'react';
import clsx from 'clsx';
import { Card, CardBody } from './Card';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className,
}) => {
  return (
    <Card className={clsx('border-dashed', className)}>
      <CardBody className="py-12 px-6 flex flex-col items-center justify-center">
        {icon && (
          <div className="mb-4 text-neutral-300 dark:text-neutral-600 w-12 h-12">
            {icon}
          </div>
        )}
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-1">
          {title}
        </h3>
        {description && (
          <p className="text-sm text-neutral-600 dark:text-neutral-400 text-center mb-4 max-w-sm">
            {description}
          </p>
        )}
        {action && (
          <button
            onClick={action.onClick}
            className={clsx(
              'px-4 py-2 rounded-lg font-medium transition-all duration-250',
              'bg-primary-500 hover:bg-primary-600 text-white',
              'dark:bg-primary-600 dark:hover:bg-primary-700'
            )}
          >
            {action.label}
          </button>
        )}
      </CardBody>
    </Card>
  );
};
