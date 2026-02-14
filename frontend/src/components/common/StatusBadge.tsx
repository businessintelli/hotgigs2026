import React from 'react';
import clsx from 'clsx';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

const getStatusStyles = (status: string) => {
  const statusLower = status.toLowerCase();

  // Requirement statuses
  if (statusLower === 'open' || statusLower === 'active')
    return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';
  if (statusLower === 'closed')
    return 'bg-neutral-50 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300';
  if (statusLower === 'on_hold')
    return 'bg-warning-50 text-warning-700 dark:bg-warning-900 dark:text-warning-200';
  if (statusLower === 'filled')
    return 'bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-200';

  // Submission statuses
  if (statusLower === 'draft')
    return 'bg-neutral-50 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300';
  if (statusLower === 'pending')
    return 'bg-warning-50 text-warning-700 dark:bg-warning-900 dark:text-warning-200';
  if (statusLower === 'approved')
    return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';
  if (statusLower === 'submitted')
    return 'bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-200';
  if (statusLower === 'customer_review')
    return 'bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-200';
  if (statusLower === 'placed')
    return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';
  if (statusLower === 'rejected')
    return 'bg-danger-50 text-danger-700 dark:bg-danger-900 dark:text-danger-200';

  // Interview statuses
  if (statusLower === 'scheduled')
    return 'bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-200';
  if (statusLower === 'completed')
    return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';
  if (statusLower === 'cancelled')
    return 'bg-danger-50 text-danger-700 dark:bg-danger-900 dark:text-danger-200';
  if (statusLower === 'no_show')
    return 'bg-danger-50 text-danger-700 dark:bg-danger-900 dark:text-danger-200';

  // Contract statuses
  if (statusLower === 'pending_signature')
    return 'bg-warning-50 text-warning-700 dark:bg-warning-900 dark:text-warning-200';
  if (statusLower === 'signed' || statusLower === 'completed')
    return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';
  if (statusLower === 'expired')
    return 'bg-danger-50 text-danger-700 dark:bg-danger-900 dark:text-danger-200';

  // Candidate statuses
  if (statusLower === 'inactive')
    return 'bg-neutral-50 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300';
  if (statusLower === 'archived')
    return 'bg-neutral-50 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300';

  // Priority statuses
  if (statusLower === 'high' || statusLower === 'critical')
    return 'bg-danger-50 text-danger-700 dark:bg-danger-900 dark:text-danger-200';
  if (statusLower === 'medium')
    return 'bg-warning-50 text-warning-700 dark:bg-warning-900 dark:text-warning-200';
  if (statusLower === 'low')
    return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';

  // Default
  return 'bg-neutral-50 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300';
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold',
        getStatusStyles(status),
        className
      )}
    >
      {status.replace(/_/g, ' ')}
    </span>
  );
};

interface PriorityBadgeProps {
  priority: 'low' | 'medium' | 'high' | 'critical';
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority, className }) => {
  return <StatusBadge status={priority} className={className} />;
};
