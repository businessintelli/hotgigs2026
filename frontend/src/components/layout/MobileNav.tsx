import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import {
  HomeIcon,
  CheckCircleIcon,
  SparklesIcon,
  DocumentChartBarIcon,
  EllipsisHorizontalIcon,
} from '@heroicons/react/24/outline';

const mobileNavItems = [
  { icon: HomeIcon, label: 'Home', href: '/dashboard' },
  { icon: CheckCircleIcon, label: 'Pipeline', href: '/submissions' },
  { icon: SparklesIcon, label: 'AI', href: '/copilot' },
  { icon: DocumentChartBarIcon, label: 'Reports', href: '/reports' },
  { icon: EllipsisHorizontalIcon, label: 'More', href: '/settings' },
];

export const MobileNav: React.FC = () => {
  const location = useLocation();

  const isActive = (href: string) => location.pathname === href;

  return (
    <nav className="fixed bottom-0 left-0 right-0 md:hidden bg-white dark:bg-neutral-800 border-t border-neutral-200 dark:border-neutral-700 z-40">
      <div className="flex items-center justify-around">
        {mobileNavItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={clsx(
              'flex-1 flex flex-col items-center gap-1 px-4 py-3 transition-all duration-250',
              isActive(item.href)
                ? 'text-primary-500 border-t-2 border-primary-500'
                : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'
            )}
          >
            <item.icon className="w-6 h-6" />
            <span className="text-xs font-medium">{item.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};
