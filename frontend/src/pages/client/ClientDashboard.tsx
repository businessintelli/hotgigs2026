import React from 'react';
import {
  DocumentTextIcon,
  UserGroupIcon,
  CheckCircleIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';

export const ClientDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Client Dashboard</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Your workforce requirements and submissions</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: DocumentTextIcon, label: 'Active Requirements', value: 8, color: 'bg-blue-500' },
          { icon: UserGroupIcon, label: 'Pending Submissions', value: 12, color: 'bg-amber-500' },
          { icon: CheckCircleIcon, label: 'Active Placements', value: 5, color: 'bg-emerald-500' },
          { icon: CalendarIcon, label: 'Interviews This Week', value: 3, color: 'bg-indigo-500' },
        ].map((item, i) => (
          <div key={i} className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${item.color}`}>
                <item.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-neutral-900 dark:text-white">{item.value}</p>
                <p className="text-sm text-neutral-500">{item.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">New Submissions from MSP</h2>
        <div className="space-y-3">
          {[
            { candidate: 'Alice Chen', role: 'Project Manager Lead', score: 91, status: 'Awaiting Review' },
            { candidate: 'David Kim', role: 'DevOps Engineer', score: 79, status: 'Awaiting Review' },
            { candidate: 'Bob Wilson', role: 'Data Engineer', score: 88, status: 'Shortlisted' },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-neutral-100 dark:border-neutral-700 last:border-0">
              <div>
                <p className="text-sm font-medium text-neutral-900 dark:text-white">{item.candidate}</p>
                <p className="text-xs text-neutral-500">{item.role}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-emerald-500">{item.score}% match</span>
                <span className="text-xs bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 px-2 py-1 rounded-full">{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
