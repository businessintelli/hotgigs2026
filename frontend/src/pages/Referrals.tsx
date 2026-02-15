import React from 'react';
import { GiftIcon } from '@heroicons/react/24/outline';

export const Referrals: React.FC = () => {
  return (
    <div className="p-4 md:p-6 space-y-6 pb-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Referrals</h1>
          <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">Track employee referrals and incentives</p>
        </div>
      </div>
      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 p-12 text-center">
        <GiftIcon className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-neutral-700 dark:text-neutral-300 mb-2">Coming Soon</h2>
        <p className="text-neutral-500 dark:text-neutral-400 max-w-md mx-auto">
          Track employee referrals and manage referral incentives. This module is available in the full Docker deployment.
        </p>
      </div>
    </div>
  );
};
