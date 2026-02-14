import React, { useState } from 'react';
import clsx from 'clsx';
import {
  BellIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { useUIStore } from '@/store/uiStore';
import { useAuth } from '@/hooks/useAuth';

interface TopNavProps {
  onMenuClick?: () => void;
  title?: string;
}

export const TopNav: React.FC<TopNavProps> = ({ onMenuClick, title }) => {
  const { logout } = useAuth();
  const { darkMode, toggleDarkMode } = useUIStore();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
      <div className="flex items-center justify-between px-4 md:px-6 py-4 gap-4">
        {/* Left section */}
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {onMenuClick && (
            <button
              onClick={onMenuClick}
              className="md:hidden p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors duration-250"
              type="button"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}
          {title && (
            <h1 className="text-lg font-semibold text-neutral-900 dark:text-white truncate">
              {title}
            </h1>
          )}
        </div>

        {/* Right section */}
        <div className="flex items-center gap-2 md:gap-4">
          {/* Search */}
          <div className="hidden sm:flex items-center bg-neutral-100 dark:bg-neutral-700 rounded-lg px-3 py-2">
            <MagnifyingGlassIcon className="w-5 h-5 text-neutral-400 dark:text-neutral-500" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent border-none outline-none ml-2 w-32 text-sm placeholder-neutral-500 dark:placeholder-neutral-400 dark:text-white"
            />
          </div>

          {/* Notifications */}
          <button
            type="button"
            className="relative p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors duration-250"
          >
            <BellIcon className="w-6 h-6 text-neutral-700 dark:text-neutral-300" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
          </button>

          {/* Dark mode toggle */}
          <button
            onClick={toggleDarkMode}
            type="button"
            className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors duration-250"
          >
            {darkMode ? (
              <svg className="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-neutral-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zm5.657-9.193a1 1 0 00-1.414 0l-.707.707A1 1 0 005.05 13.536l.707-.707a1 1 0 001.414 0l.707-.707A1 1 0 0010.707 2.757z" clipRule="evenodd" />
              </svg>
            )}
          </button>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              type="button"
              className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors duration-250"
            >
              <UserCircleIcon className="w-6 h-6 text-neutral-700 dark:text-neutral-300" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-lg">
                <button
                  type="button"
                  className="w-full text-left px-4 py-2 hover:bg-neutral-50 dark:hover:bg-neutral-700 flex items-center gap-2 border-b border-neutral-200 dark:border-neutral-700"
                >
                  <Cog6ToothIcon className="w-5 h-5" />
                  <span>Settings</span>
                </button>
                <button
                  onClick={handleLogout}
                  type="button"
                  className="w-full text-left px-4 py-2 hover:bg-neutral-50 dark:hover:bg-neutral-700 flex items-center gap-2 text-danger-600 dark:text-danger-400"
                >
                  <ArrowLeftOnRectangleIcon className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
