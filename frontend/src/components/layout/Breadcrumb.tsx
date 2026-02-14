import React from 'react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';
import { ChevronRightIcon } from '@heroicons/react/24/outline';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items, className }) => {
  return (
    <nav className={clsx('flex items-center gap-2', className)}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          {index > 0 && (
            <ChevronRightIcon className="w-4 h-4 text-neutral-400 dark:text-neutral-600" />
          )}
          {item.href ? (
            <Link
              to={item.href}
              className="text-primary-500 hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-250"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-neutral-700 dark:text-neutral-300">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
};
