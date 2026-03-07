import React from 'react';
import {
  BuildingOfficeIcon,
  TruckIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CheckCircleIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const MetricCard: React.FC<{ icon: any; label: string; value: string | number; color: string; subtitle?: string }> = ({
  icon: Icon, label, value, color, subtitle,
}) => (
  <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
    <div className="flex items-center gap-4">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-neutral-900 dark:text-white">{value}</p>
        <p className="text-sm text-neutral-500 dark:text-neutral-400">{label}</p>
        {subtitle && <p className="text-xs text-neutral-400 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  </div>
);

export const MSPDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">MSP Dashboard</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Manage your clients, suppliers, and workforce pipeline
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={BuildingOfficeIcon} label="Active Clients" value={12} color="bg-emerald-500" subtitle="2 pending onboarding" />
        <MetricCard icon={TruckIcon} label="Active Suppliers" value={28} color="bg-amber-500" subtitle="5 platinum tier" />
        <MetricCard icon={DocumentTextIcon} label="Open Requirements" value={34} color="bg-blue-500" subtitle="8 distributed this week" />
        <MetricCard icon={UserGroupIcon} label="Pending Reviews" value={15} color="bg-red-500" subtitle="3 overdue SLA" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={CheckCircleIcon} label="Active Placements" value={87} color="bg-indigo-500" />
        <MetricCard icon={ChartBarIcon} label="This Month" value="23 submissions" color="bg-purple-500" />
        <MetricCard icon={ClockIcon} label="Avg Fill Time" value="18 days" color="bg-cyan-500" />
        <MetricCard icon={ExclamationTriangleIcon} label="SLA Breaches" value={3} color="bg-orange-500" />
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium">
            Onboard Client
          </button>
          <button className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors text-sm font-medium">
            Onboard Supplier
          </button>
          <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium">
            Distribute Requirement
          </button>
          <button className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm font-medium">
            Review Submissions
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[
            { text: 'New requirement from Acme Corp — Senior Java Developer', time: '2 hours ago', type: 'requirement' },
            { text: 'TechStaff Inc submitted 3 candidates for Req #1042', time: '4 hours ago', type: 'submission' },
            { text: 'GlobalTech approved candidate John Smith for interview', time: '6 hours ago', type: 'feedback' },
            { text: 'New supplier ProStaffing onboarded (Gold tier)', time: '1 day ago', type: 'onboard' },
            { text: 'Placement started: Sarah Lee at DataCorp', time: '2 days ago', type: 'placement' },
          ].map((item, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b border-neutral-100 dark:border-neutral-700 last:border-0">
              <div className="w-2 h-2 rounded-full bg-primary-500 mt-2 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-neutral-700 dark:text-neutral-300">{item.text}</p>
                <p className="text-xs text-neutral-400">{item.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
