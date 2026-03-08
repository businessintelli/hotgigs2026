import React from 'react';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

interface SLABreach {
  id: string;
  requirement: string;
  client: string;
  breachType: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  dateOccurred: string;
}

interface SLAConfig {
  id: string;
  metric: string;
  targetValue: number;
  currentValue: number;
  unit: string;
}

const mockSLABreaches: SLABreach[] = [
  {
    id: '1',
    requirement: 'Req #1042 - Senior Java Developer',
    client: 'Acme Corp',
    breachType: 'Fill Time Exceeded',
    severity: 'CRITICAL',
    dateOccurred: '2025-03-07',
  },
  {
    id: '2',
    requirement: 'Req #1045 - Project Manager',
    client: 'TechCorp Inc',
    breachType: 'Response Time',
    severity: 'HIGH',
    dateOccurred: '2025-03-06',
  },
  {
    id: '3',
    requirement: 'Req #1038 - Data Engineer',
    client: 'GlobalTech',
    breachType: 'Quality Score',
    severity: 'MEDIUM',
    dateOccurred: '2025-03-05',
  },
];

const mockSLAMetrics: SLAConfig[] = [
  {
    id: '1',
    metric: 'Average Response Time',
    targetValue: 4,
    currentValue: 3.5,
    unit: 'hours',
  },
  {
    id: '2',
    metric: 'Average Fill Time',
    targetValue: 15,
    currentValue: 18,
    unit: 'days',
  },
  {
    id: '3',
    metric: 'Quality Score',
    targetValue: 90,
    currentValue: 85,
    unit: '%',
  },
  {
    id: '4',
    metric: 'Candidate Acceptance Rate',
    targetValue: 80,
    currentValue: 78,
    unit: '%',
  },
  {
    id: '5',
    metric: 'Placement Retention Rate',
    targetValue: 85,
    currentValue: 82,
    unit: '%',
  },
];

const getSeverityBadge = (severity: string) => {
  switch (severity) {
    case 'CRITICAL':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'HIGH':
      return 'bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400';
    case 'MEDIUM':
      return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400';
    case 'LOW':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

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

const getMetricStatus = (target: number, current: number): 'good' | 'warning' | 'critical' => {
  const percentage = (current / target) * 100;
  if (percentage >= 95) return 'good';
  if (percentage >= 85) return 'warning';
  return 'critical';
};

export const SLADashboard: React.FC = () => {
  const openBreaches = mockSLABreaches.length;
  const resolvedBreaches = 12;
  const activeSLAs = 8;
  const avgScore = Math.round(
    mockSLAMetrics.reduce((sum, m) => sum + m.currentValue, 0) / mockSLAMetrics.length
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">SLA Monitoring</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Track service level agreements, breaches, and performance metrics
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={CheckCircleIcon} label="Active SLAs" value={activeSLAs} color="bg-emerald-500" />
        <MetricCard icon={ExclamationTriangleIcon} label="Breaches (Open)" value={openBreaches} color="bg-red-500" subtitle="3 critical" />
        <MetricCard icon={CheckCircleIcon} label="Resolved" value={resolvedBreaches} color="bg-blue-500" />
        <MetricCard icon={ChartBarIcon} label="Avg Score" value={`${avgScore}%`} color="bg-purple-500" />
      </div>

      {/* Breach Alerts Section */}
      {openBreaches > 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
            Active Breaches ({openBreaches})
          </h2>
          <div className="space-y-3">
            {mockSLABreaches.map((breach) => (
              <div key={breach.id} className="flex items-start gap-4 p-4 rounded-lg bg-neutral-50 dark:bg-neutral-700/30 border border-neutral-200 dark:border-neutral-700">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-neutral-900 dark:text-white">{breach.requirement}</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityBadge(breach.severity)}`}>
                      {breach.severity}
                    </span>
                  </div>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">{breach.client} • {breach.breachType}</p>
                  <p className="text-xs text-neutral-500 mt-1">Occurred: {new Date(breach.dateOccurred).toLocaleDateString()}</p>
                </div>
                <button className="px-3 py-1 bg-primary-500 text-white rounded-lg text-xs font-medium hover:bg-primary-600 transition-colors whitespace-nowrap">
                  Resolve
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SLA Metrics Table */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">SLA Metrics</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Metric
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Target
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Current
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Progress
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {mockSLAMetrics.map((metric) => {
                const status = getMetricStatus(metric.targetValue, metric.currentValue);
                const percentage = Math.round((metric.currentValue / metric.targetValue) * 100);
                const statusColor = status === 'good' ? 'bg-emerald-500' : status === 'warning' ? 'bg-yellow-500' : 'bg-red-500';

                return (
                  <tr key={metric.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      {metric.metric}
                    </td>
                    <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                      {metric.targetValue}{metric.unit}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      {metric.currentValue}{metric.unit}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        status === 'good'
                          ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
                          : status === 'warning'
                            ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400'
                            : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                      }`}>
                        {status === 'good' ? 'On Target' : status === 'warning' ? 'At Risk' : 'Critical'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${statusColor}`}
                            style={{ width: `${Math.min(percentage, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-neutral-600 dark:text-neutral-400 w-8">
                          {percentage}%
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SLADashboard;
