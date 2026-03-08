import React, { useState, useEffect } from 'react';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import client from '@/api/client';

interface ComplianceRecord {
  id: string;
  requirement: string;
  completionDate: string;
  dueDate: string;
  status: 'COMPLETED' | 'PENDING' | 'EXPIRED' | 'FAILED';
}

const mockComplianceRecords: ComplianceRecord[] = [
  {
    id: '1',
    requirement: 'Background Check - John Smith',
    completionDate: '2025-03-05',
    dueDate: '2025-03-10',
    status: 'COMPLETED',
  },
  {
    id: '2',
    requirement: 'Skills Assessment - Jane Doe',
    completionDate: '',
    dueDate: '2025-03-12',
    status: 'PENDING',
  },
  {
    id: '3',
    requirement: 'Reference Check - Mike Johnson',
    completionDate: '',
    dueDate: '2025-02-28',
    status: 'EXPIRED',
  },
  {
    id: '4',
    requirement: 'Drug Screening - Alice Brown',
    completionDate: '2025-03-01',
    dueDate: '2025-03-15',
    status: 'COMPLETED',
  },
  {
    id: '5',
    requirement: 'Compliance Training - Bob Wilson',
    completionDate: '',
    dueDate: '2025-03-08',
    status: 'PENDING',
  },
  {
    id: '6',
    requirement: 'Right to Work - Sarah Lee',
    completionDate: '2025-02-15',
    dueDate: '2025-03-01',
    status: 'FAILED',
  },
  {
    id: '7',
    requirement: 'NDA Signature - David Kim',
    completionDate: '2025-03-04',
    dueDate: '2025-03-20',
    status: 'COMPLETED',
  },
  {
    id: '8',
    requirement: 'Tax Forms W4 - Emma Chen',
    completionDate: '',
    dueDate: '2025-03-18',
    status: 'PENDING',
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'COMPLETED':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case 'PENDING':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'EXPIRED':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'FAILED':
      return 'bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const MetricCard: React.FC<{ icon: any; label: string; value: number; color: string }> = ({
  icon: Icon, label, value, color,
}) => (
  <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
    <div className="flex items-center gap-4">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-neutral-900 dark:text-white">{value}</p>
        <p className="text-sm text-neutral-500 dark:text-neutral-400">{label}</p>
      </div>
    </div>
  </div>
);

export const ComplianceDashboard: React.FC = () => {
  const [records, setRecords] = useState<ComplianceRecord[]>(mockComplianceRecords);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComplianceData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await client.get('/compliance/requirements');
        if (response.data && response.data.length > 0) {
          setRecords(response.data);
        }
      } catch (err) {
        console.error('Failed to fetch compliance records, using mock data:', err);
        setError('Failed to load compliance records, using mock data');
      } finally {
        setLoading(false);
      }
    };

    fetchComplianceData();
  }, []);

  const totalRequirements = records.length;
  const completed = records.filter(r => r.status === 'COMPLETED').length;
  const pending = records.filter(r => r.status === 'PENDING').length;
  const expired = records.filter(r => r.status === 'EXPIRED').length;
  const failed = records.filter(r => r.status === 'FAILED').length;
  const complianceScore = totalRequirements > 0 ? Math.round((completed / totalRequirements) * 100) : 0;

  const getGaugeColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getGaugeBg = (score: number) => {
    if (score >= 80) return 'bg-emerald-100 dark:bg-emerald-900/20';
    if (score >= 50) return 'bg-yellow-100 dark:bg-yellow-900/20';
    return 'bg-red-100 dark:bg-red-900/20';
  };

  return (
    <div className="space-y-6">
      {/* Loading Spinner */}
      {loading && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">{error}</p>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Compliance Dashboard</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Monitor compliance requirements and contractor onboarding status
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard icon={CheckCircleIcon} label="Total Requirements" value={totalRequirements} color="bg-blue-500" />
        <MetricCard icon={CheckCircleIcon} label="Completed" value={completed} color="bg-emerald-500" />
        <MetricCard icon={ClockIcon} label="Pending" value={pending} color="bg-amber-500" />
        <MetricCard icon={ExclamationTriangleIcon} label="Expired" value={expired} color="bg-red-500" />
        <MetricCard icon={XCircleIcon} label="Failed" value={failed} color="bg-orange-500" />
      </div>

      {/* Compliance Score Gauge */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Overall Compliance Score</h2>
        <div className="flex items-center justify-center">
          <div className={`relative w-48 h-48 rounded-full flex items-center justify-center ${getGaugeBg(complianceScore)}`}>
            <div className="text-center">
              <p className={`text-5xl font-bold ${getGaugeColor(complianceScore)}`}>{complianceScore}%</p>
              <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-2">
                {complianceScore >= 80 ? 'Excellent' : complianceScore >= 50 ? 'Fair' : 'At Risk'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Records Table */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Compliance Records</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Requirement
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Completion Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {records.map((record) => (
                <tr key={record.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                    {record.requirement}
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                    {new Date(record.dueDate).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                    {record.completionDate ? new Date(record.completionDate).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(record.status)}`}>
                      {record.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ComplianceDashboard;
