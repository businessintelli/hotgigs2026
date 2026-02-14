import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import {
  HomeIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CheckCircleIcon,
  CalendarIcon,
  DocumentDuplicateIcon,
  BuildingLibraryIcon,
  FaceSmileIcon,
  SparklesIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon,
  ShieldExclamationIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import { useUIStore } from '@/store/uiStore';
import { useAuth } from '@/hooks/useAuth';

const navigationGroups = [
  {
    label: 'OVERVIEW',
    items: [{ icon: HomeIcon, label: 'Dashboard', href: '/dashboard' }],
  },
  {
    label: 'PIPELINE',
    items: [
      { icon: DocumentTextIcon, label: 'Requirements', href: '/requirements' },
      { icon: UserGroupIcon, label: 'Candidates', href: '/candidates' },
      { icon: CheckCircleIcon, label: 'Submissions', href: '/submissions' },
      { icon: CalendarIcon, label: 'Interviews', href: '/interviews' },
    ],
  },
  {
    label: 'MANAGEMENT',
    items: [
      { icon: DocumentDuplicateIcon, label: 'Contracts', href: '/contracts' },
      { icon: BuildingLibraryIcon, label: 'Suppliers', href: '/suppliers' },
      { icon: FaceSmileIcon, label: 'Referrals', href: '/referrals' },
    ],
  },
  {
    label: 'AI TOOLS',
    items: [
      { icon: SparklesIcon, label: 'Copilot', href: '/copilot' },
    ],
  },
  {
    label: 'REPORTS & ADMIN',
    items: [
      { icon: DocumentChartBarIcon, label: 'Reports', href: '/reports' },
      { icon: Cog6ToothIcon, label: 'Settings', href: '/settings' },
      { icon: ShieldExclamationIcon, label: 'Admin', href: '/admin', roleRequired: 'admin' },
    ],
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const location = useLocation();
  const { user } = useAuth();
  const { sidebarCollapsed, setSidebarCollapsed } = useUIStore();

  const isActive = (href: string) => location.pathname === href;

  const canAccessItem = (item: any) => {
    if (!item.roleRequired) return true;
    return user?.role === item.roleRequired || user?.role === 'admin';
  };

  return (
    <>
      {/* Mobile backdrop */}
      {!isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed left-0 top-0 h-full bg-neutral-900 dark:bg-neutral-950 text-white',
          'transition-all duration-250 z-40',
          'flex flex-col',
          sidebarCollapsed ? 'w-20' : 'w-sidebar',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          'md:translate-x-0 md:static'
        )}
      >
        {/* Logo Section */}
        <div className={clsx(
          'border-b border-neutral-800 p-4 flex items-center justify-between',
          sidebarCollapsed && 'justify-center'
        )}>
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center font-bold text-sm">
                HR
              </div>
              <span className="font-bold text-lg">Platform</span>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="hidden lg:block text-neutral-400 hover:text-white transition-colors"
            type="button"
          >
            {sidebarCollapsed ? (
              <ChevronRightIcon className="w-5 h-5" />
            ) : (
              <ChevronLeftIcon className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* User Section */}
        <div className={clsx(
          'border-b border-neutral-800 p-4',
          sidebarCollapsed && 'flex justify-center'
        )}>
          {!sidebarCollapsed && user && (
            <div>
              <p className="text-sm font-semibold">{user.first_name}</p>
              <p className="text-xs text-neutral-400">{user.role}</p>
            </div>
          )}
          {sidebarCollapsed && user && (
            <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center font-bold text-sm">
              {user.first_name.charAt(0)}
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-6">
          {navigationGroups.map((group) => (
            <div key={group.label}>
              {!sidebarCollapsed && (
                <p className="px-4 py-2 text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                  {group.label}
                </p>
              )}
              <div className={clsx(
                'space-y-1',
                sidebarCollapsed && 'flex flex-col items-center'
              )}>
                {group.items
                  .filter(canAccessItem)
                  .map((item) => (
                    <Link
                      key={item.href}
                      to={item.href}
                      className={clsx(
                        'flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-250',
                        'text-neutral-300 hover:text-white hover:bg-neutral-800',
                        isActive(item.href) &&
                          'bg-primary-500 text-white hover:bg-primary-600'
                      )}
                      title={sidebarCollapsed ? item.label : undefined}
                      onClick={onClose}
                    >
                      <item.icon className="w-5 h-5 flex-shrink-0" />
                      {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
                    </Link>
                  ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-neutral-800 p-4">
          <p className="text-xs text-neutral-500 text-center">
            {!sidebarCollapsed && 'v1.0.0'}
          </p>
        </div>
      </aside>
    </>
  );
};
