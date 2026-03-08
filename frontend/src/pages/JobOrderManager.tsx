import React, { useState } from 'react';
import {
  FunnelIcon,
  ChevronDownIcon,
  ArrowUpRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface JobOrder {
  id: string;
  title: string;
  client: string;
  priority: 'URGENT' | 'HIGH' | 'NORMAL' | 'LOW';
  distributionType: 'Exclusive' | 'Shared' | 'Open';
  targetDate: string;
  submissions: {
    count: number;
    max: number;
  };
  status: 'Open' | 'Filled' | 'OnHold' | 'Closed';
}

interface Supplier {
  id: string;
  name: string;
  submissionStatus: 'No Submission' | 'Submitted' | 'Viewed' | 'Accepted' | 'Rejected';
}

const mockJobOrders: JobOrder[] = [
  {
    id: '1',
    title: 'Senior Frontend Engineer',
    client: 'TechCorp Industries',
    priority: 'URGENT',
    distributionType: 'Exclusive',
    targetDate: 'Mar 15, 2026',
    submissions: { count: 5, max: 10 },
    status: 'Open',
  },
  {
    id: '2',
    title: 'Full Stack Developer',
    client: 'CloudSystems Inc',
    priority: 'HIGH',
    distributionType: 'Shared',
    targetDate: 'Mar 20, 2026',
    submissions: { count: 8, max: 15 },
    status: 'Open',
  },
  {
    id: '3',
    title: 'DevOps Engineer',
    client: 'DataFlow Solutions',
    priority: 'HIGH',
    distributionType: 'Open',
    targetDate: 'Mar 25, 2026',
    submissions: { count: 3, max: 20 },
    status: 'Open',
  },
  {
    id: '4',
    title: 'Product Manager',
    client: 'InnovateLabs',
    priority: 'NORMAL',
    distributionType: 'Exclusive',
    targetDate: 'Apr 5, 2026',
    submissions: { count: 2, max: 5 },
    status: 'OnHold',
  },
  {
    id: '5',
    title: 'Senior React Developer',
    client: 'TechCorp Industries',
    priority: 'NORMAL',
    distributionType: 'Shared',
    targetDate: 'Mar 18, 2026',
    submissions: { count: 12, max: 10 },
    status: 'Filled',
  },
  {
    id: '6',
    title: 'QA Automation Engineer',
    client: 'WebDynamics',
    priority: 'NORMAL',
    distributionType: 'Open',
    targetDate: 'Apr 1, 2026',
    submissions: { count: 1, max: 8 },
    status: 'Open',
  },
  {
    id: '7',
    title: 'Backend Engineer (Java)',
    client: 'FinanceAI',
    priority: 'LOW',
    distributionType: 'Exclusive',
    targetDate: 'Apr 15, 2026',
    submissions: { count: 0, max: 3 },
    status: 'Open',
  },
  {
    id: '8',
    title: 'UI/UX Designer',
    client: 'DesignStudio',
    priority: 'LOW',
    distributionType: 'Shared',
    targetDate: 'May 1, 2026',
    submissions: { count: 4, max: 6 },
    status: 'Closed',
  },
];

const mockSuppliers: Supplier[] = [
  {
    id: '1',
    name: 'TalentPool Recruiting',
    submissionStatus: 'Submitted',
  },
  {
    id: '2',
    name: 'Elite Staffing Solutions',
    submissionStatus: 'Viewed',
  },
  {
    id: '3',
    name: 'FastHire Inc',
    submissionStatus: 'Accepted',
  },
  {
    id: '4',
    name: 'Global Talent Partners',
    submissionStatus: 'No Submission',
  },
  {
    id: '5',
    name: 'Premier Placement Group',
    submissionStatus: 'Rejected',
  },
];

const getPriorityColor = (priority: JobOrder['priority']) => {
  switch (priority) {
    case 'URGENT':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'HIGH':
      return 'bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400';
    case 'NORMAL':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'LOW':
      return 'bg-gray-100 dark:bg-gray-900/20 text-gray-700 dark:text-gray-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getStatusColor = (status: JobOrder['status']) => {
  switch (status) {
    case 'Open':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'Filled':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case 'OnHold':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'Closed':
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getSubmissionStatusColor = (status: Supplier['submissionStatus']) => {
  switch (status) {
    case 'Submitted':
      return 'bg-blue-50 dark:bg-blue-900/10 text-blue-700 dark:text-blue-400';
    case 'Viewed':
      return 'bg-amber-50 dark:bg-amber-900/10 text-amber-700 dark:text-amber-400';
    case 'Accepted':
      return 'bg-green-50 dark:bg-green-900/10 text-green-700 dark:text-green-400';
    case 'Rejected':
      return 'bg-red-50 dark:bg-red-900/10 text-red-700 dark:text-red-400';
    case 'No Submission':
      return 'bg-neutral-50 dark:bg-neutral-900/10 text-neutral-700 dark:text-neutral-400';
    default:
      return 'bg-neutral-50 dark:bg-neutral-900/10 text-neutral-700 dark:text-neutral-400';
  }
};

export const JobOrderManager: React.FC = () => {
  const [selectedJobOrder, setSelectedJobOrder] = useState<JobOrder | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [clientFilter, setClientFilter] = useState<string>('');

  const stats = [
    {
      label: 'Open Orders',
      value: mockJobOrders.filter(j => j.status === 'Open').length,
      icon: CheckCircleIcon,
      color: 'text-green-500',
    },
    {
      label: 'On Hold',
      value: mockJobOrders.filter(j => j.status === 'OnHold').length,
      icon: ExclamationTriangleIcon,
      color: 'text-amber-500',
    },
    {
      label: 'Filled This Month',
      value: mockJobOrders.filter(j => j.status === 'Filled').length,
      icon: CheckCircleIcon,
      color: 'text-emerald-500',
    },
    {
      label: 'Avg Time to Fill',
      value: '12.4',
      suffix: 'days',
      color: 'text-blue-500',
    },
  ];

  const filteredOrders = mockJobOrders.filter(order => {
    if (statusFilter && order.status !== statusFilter) return false;
    if (priorityFilter && order.priority !== priorityFilter) return false;
    if (clientFilter && order.client !== clientFilter) return false;
    return true;
  });

  const clients = Array.from(new Set(mockJobOrders.map(j => j.client)));
  const statuses = Array.from(new Set(mockJobOrders.map(j => j.status)));
  const priorities = Array.from(new Set(mockJobOrders.map(j => j.priority)));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Job Order Manager</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Manage job orders and track distributions</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon || (() => null);
          return (
            <div
              key={idx}
              className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-neutral-500 dark:text-neutral-400">{stat.label}</p>
                  <div className="mt-2 flex items-baseline gap-1">
                    <p className="text-3xl font-bold text-neutral-900 dark:text-white">{stat.value}</p>
                    {stat.suffix && (
                      <p className="text-sm text-neutral-500 dark:text-neutral-400">{stat.suffix}</p>
                    )}
                  </div>
                </div>
                {stat.color && (
                  <div className={`${stat.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center gap-2 mb-4">
          <FunnelIcon className="w-5 h-5 text-neutral-500 dark:text-neutral-400" />
          <h3 className="font-semibold text-neutral-900 dark:text-white">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white"
            >
              <option value="">All Statuses</option>
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white"
            >
              <option value="">All Priorities</option>
              {priorities.map(priority => (
                <option key={priority} value={priority}>{priority}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Client</label>
            <select
              value={clientFilter}
              onChange={(e) => setClientFilter(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white"
            >
              <option value="">All Clients</option>
              {clients.map(client => (
                <option key={client} value={client}>{client}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Job Orders Table */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-neutral-50 dark:bg-neutral-700/30">
              <tr className="border-b border-neutral-200 dark:border-neutral-700">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Distribution
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Target Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Submissions
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {filteredOrders.map((order) => (
                <tr key={order.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">{order.title}</td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{order.client}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${getPriorityColor(order.priority)}`}>
                      {order.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{order.distributionType}</td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{order.targetDate}</td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500"
                          style={{ width: `${(order.submissions.count / order.submissions.max) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                        {order.submissions.count}/{order.submissions.max}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => setSelectedJobOrder(order)}
                      className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Distribution Panel */}
      {selectedJobOrder && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
              Distribution Details: {selectedJobOrder.title}
            </h3>
            <button
              onClick={() => setSelectedJobOrder(null)}
              className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
            >
              ✕
            </button>
          </div>
          <div className="space-y-3">
            {mockSuppliers.map((supplier) => (
              <div
                key={supplier.id}
                className="flex items-center justify-between p-4 border border-neutral-200 dark:border-neutral-700 rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-neutral-200 dark:bg-neutral-700 flex items-center justify-center text-sm font-semibold text-neutral-700 dark:text-neutral-300">
                    {supplier.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-neutral-900 dark:text-white">{supplier.name}</p>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${getSubmissionStatusColor(supplier.submissionStatus)}`}
                >
                  {supplier.submissionStatus}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobOrderManager;
