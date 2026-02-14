import React from 'react';
import clsx from 'clsx';
import { Card, CardBody } from './Card';

interface KPICardProps {
  icon?: React.ReactNode;
  label: string;
  value: string | number;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  subtitle?: string;
  className?: string;
  color?: 'primary' | 'success' | 'warning' | 'danger';
}

const colorClasses = {
  primary: {
    bg: 'bg-primary-50 dark:bg-primary-900/20',
    icon: 'text-primary-500 dark:text-primary-400',
  },
  success: {
    bg: 'bg-success-50 dark:bg-success-900/20',
    icon: 'text-success-500 dark:text-success-400',
  },
  warning: {
    bg: 'bg-warning-50 dark:bg-warning-900/20',
    icon: 'text-warning-500 dark:text-warning-400',
  },
  danger: {
    bg: 'bg-danger-50 dark:bg-danger-900/20',
    icon: 'text-danger-500 dark:text-danger-400',
  },
};

export const KPICard: React.FC<KPICardProps> = ({
  icon,
  label,
  value,
  trend,
  subtitle,
  className,
  color = 'primary',
}) => {
  const styles = colorClasses[color];

  return (
    <Card className={className}>
      <CardBody className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
              {label}
            </p>
            <p className="mt-2 text-3xl font-bold text-neutral-900 dark:text-white">
              {value}
            </p>
            {subtitle && (
              <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
                {subtitle}
              </p>
            )}
            {trend && (
              <div
                className={clsx(
                  'mt-2 flex items-center text-xs font-semibold',
                  trend.isPositive
                    ? 'text-success-600 dark:text-success-400'
                    : 'text-danger-600 dark:text-danger-400'
                )}
              >
                <span>{trend.isPositive ? '↑' : '↓'}</span>
                <span className="ml-1">{Math.abs(trend.value)}%</span>
              </div>
            )}
          </div>
          {icon && (
            <div className={clsx('rounded-lg p-3', styles.bg)}>
              <div className={clsx('w-6 h-6', styles.icon)}>{icon}</div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
};
