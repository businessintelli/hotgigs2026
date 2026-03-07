import React from 'react';
import {
  BriefcaseIcon,
  PaperAirplaneIcon,
  CheckCircleIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

export const SupplierDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Supplier Dashboard</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Your opportunities, submissions, and performance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: BriefcaseIcon, label: 'Open Opportunities', value: 6, color: 'bg-blue-500' },
          { icon: PaperAirplaneIcon, label: 'My Submissions', value: 14, color: 'bg-amber-500' },
          { icon: CheckCircleIcon, label: 'Active Placements', value: 3, color: 'bg-emerald-500' },
          { icon: ChartBarIcon, label: 'Quality Score', value: '85%', color: 'bg-indigo-500' },
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
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">New Opportunities</h2>
        <div className="space-y-3">
          {[
            { title: 'Senior Java Developer', client: 'Fortune 500 Tech', deadline: '3 days', positions: 2, submitted: 0 },
            { title: 'React Lead Developer', client: 'Global Finance Corp', deadline: '5 days', positions: 1, submitted: 1 },
            { title: 'Data Engineer', client: 'HealthTech Inc', deadline: '7 days', positions: 3, submitted: 0 },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-neutral-100 dark:border-neutral-700 last:border-0">
              <div>
                <p className="text-sm font-medium text-neutral-900 dark:text-white">{item.title}</p>
                <p className="text-xs text-neutral-500">{item.client} &middot; {item.positions} position(s)</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-neutral-400">Deadline: {item.deadline}</span>
                <button className="px-3 py-1 bg-primary-500 text-white rounded-lg text-xs font-medium hover:bg-primary-600 transition-colors">
                  {item.submitted > 0 ? `${item.submitted} Submitted` : 'Submit Candidate'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
