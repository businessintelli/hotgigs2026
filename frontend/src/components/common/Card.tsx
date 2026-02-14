import React from 'react';
import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
  bordered?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  onClick,
  hoverable = false,
  bordered = true,
}) => {
  return (
    <div
      className={clsx(
        'rounded-lg bg-white dark:bg-neutral-800',
        bordered && 'border border-neutral-200 dark:border-neutral-700',
        hoverable && 'cursor-pointer hover:shadow-lg transition-shadow duration-250',
        'shadow-sm',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
  divider?: boolean;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  className,
  divider = true,
}) => (
  <div
    className={clsx(
      'px-6 py-4',
      divider && 'border-b border-neutral-200 dark:border-neutral-700',
      className
    )}
  >
    {children}
  </div>
);

interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const CardBody: React.FC<CardBodyProps> = ({ children, className }) => (
  <div className={clsx('px-6 py-4', className)}>{children}</div>
);

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className }) => (
  <div
    className={clsx(
      'px-6 py-4 border-t border-neutral-200 dark:border-neutral-700',
      className
    )}
  >
    {children}
  </div>
);
