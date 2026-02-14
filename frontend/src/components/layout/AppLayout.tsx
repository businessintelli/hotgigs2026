import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { MobileNav } from './MobileNav';
import { useMobile } from '@/hooks/useMobile';

interface AppLayoutProps {
  children: React.ReactNode;
  title?: string;
  showMobileNav?: boolean;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  title,
  showMobileNav = true,
}) => {
  const { isMobile } = useMobile();
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  useEffect(() => {
    if (!isMobile) {
      setSidebarOpen(true);
    }
  }, [isMobile]);

  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [isMobile]);

  return (
    <div className="flex h-screen bg-neutral-50 dark:bg-neutral-900 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation */}
        <TopNav
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          title={title}
        />

        {/* Page content */}
        <main className={clsx(
          'flex-1 overflow-y-auto',
          showMobileNav && isMobile && 'pb-mobile-nav'
        )}>
          {children}
        </main>

        {/* Mobile bottom navigation */}
        {showMobileNav && isMobile && <MobileNav />}
      </div>
    </div>
  );
};
