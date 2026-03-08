import React, { useState, useEffect } from 'react';
import {
  CheckCircleIcon,
  ClockIcon,
  EyeIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import client from '@/api/client';

interface Timesheet {
  id: string;
  contractor: string;
  period: string;
  hours: number;
  billAmount: number;
  status: 'SUBMITTED' | 'MSP_REVIEW' | 'CLIENT_APPROVAL' | 'APPROVED';
  supplier: string;
}

const mockTimesheets: Timesheet[] = [
  {
    id: '1',
    contractor: 'John Smith',
    period: 'Mar 1-7, 2025',
    hours: 40,
    billAmount: 6000,
    status: 'APPROVED',
    supplier: 'TechStaff Inc',
  },
  {
    id: '2',
    contractor: 'Jane Doe',
    period: 'Mar 1-7, 2025',
    hours: 38,
    billAmount: 5700,
    status: 'CLIENT_APPROVAL',
    supplier: 'ProStaffing',
  },
  {
    id: '3',
    contractor: 'Mike Johnson',
    period: 'Mar 1-7, 2025',
    hours: 40,
    billAmount: 5200,
    status: 'MSP_REVIEW',
    supplier: 'GlobalTech Staffing',
  },
  {
    id: '4',
    contractor: 'Alice Brown',
    period: 'Mar 1-7, 2025',
    hours: 36,
    billAmount: 4800,
    status: 'MSP_REVIEW',
    supplier: 'TechStaff Inc',
  },
  {
    id: '5',
    contractor: 'Bob Wilson',
    period: 'Mar 1-7, 2025',
    hours: 40,
    billAmount: 6400,
    status: 'SUBMITTED',
    supplier: 'Elite Staffing',
  },
  {
    id: '6',
    contractor: 'Sarah Lee',
    period: 'Feb 24-Mar 2, 2025',
    hours: 39,
    billAmount: 5850,
    status: 'APPROVED',
    supplier: 'ProStaffing',
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'SUBMITTED':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'MSP_REVIEW':
      return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400';
    case 'CLIENT_APPROVAL':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'APPROVED':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStageIcon = (stage: string) => {
  switch (stage) {
    case 'Submitted':
      return 'bg-blue-500';
    case 'MSP Review':
      return 'bg-yellow-500';
    case 'Client Approval':
      return 'bg-amber-500';
    case 'Approved':
      return 'bg-emerald-500';
    default:
      return 'bg-gray-500';
  }
};

export const VMSTimesheets: React.FC = () => {
  const [timesheets, setTimesheets] = useState<Timesheet[]>(mockTimesheets);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    const fetchTimesheets = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await client.get('/vms/timesheets');
        if (response.data && response.data.length > 0) {
          setTimesheets(response.data);
        }
      } catch (err) {
        console.error('Failed to fetch timesheets, using mock data:', err);
        setError('Failed to load timesheets, using mock data');
      } finally {
        setLoading(false);
      }
    };

    fetchTimesheets();
  }, []);

  const handleApproveTimesheet = async (id: string) => {
    try {
      await client.put(`/vms/timesheets/${id}/msp-review`, { action: 'approve' });
      setTimesheets(timesheets.map(ts => ts.id === id ? { ...ts, status: 'CLIENT_APPROVAL' } : ts));
      console.log('Timesheet approved');
    } catch (err) {
      console.error('Failed to approve timesheet:', err);
      alert('Failed to approve timesheet');
    }
  };

  const handleRejectTimesheet = async (id: string) => {
    try {
      await client.put(`/vms/timesheets/${id}/msp-review`, { action: 'reject' });
      setTimesheets(timesheets.filter(ts => ts.id !== id));
      console.log('Timesheet rejected');
    } catch (err) {
      console.error('Failed to reject timesheet:', err);
      alert('Failed to reject timesheet');
    }
  };

  const stages = [
    { label: 'Submitted', key: 'SUBMITTED' },
    { label: 'MSP Review', key: 'MSP_REVIEW' },
    { label: 'Client Approval', key: 'CLIENT_APPROVAL' },
    { label: 'Approved', key: 'APPROVED' },
  ];

  const stageCounts = stages.map(stage => ({
    ...stage,
    count: timesheets.filter(ts => ts.status === stage.key).length,
  }));

  const filteredTimesheets = filterStatus === 'ALL'
    ? timesheets
    : timesheets.filter(ts => ts.status === filterStatus);

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
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">VMS Timesheets</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Review and approve contractor timesheets through the approval pipeline
        </p>
      </div>

      {/* Pipeline View with Stage Counts */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Approval Pipeline</h2>
        <div className="flex items-center justify-between gap-4 flex-wrap">
          {stageCounts.map((stage, index) => (
            <React.Fragment key={stage.key}>
              <button
                onClick={() => setFilterStatus(stage.key)}
                className={`flex flex-col items-center gap-2 p-4 rounded-lg transition-all ${
                  filterStatus === stage.key
                    ? 'bg-primary-100 dark:bg-primary-900/20 border-2 border-primary-500'
                    : 'bg-neutral-100 dark:bg-neutral-700 border-2 border-neutral-200 dark:border-neutral-700 hover:border-primary-500'
                }`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white ${getStageIcon(stage.label)}`}>
                  {stage.count}
                </div>
                <span className="text-sm font-medium text-neutral-900 dark:text-white">{stage.label}</span>
              </button>
              {index < stageCounts.length - 1 && (
                <div className="hidden sm:block text-neutral-300 dark:text-neutral-700">→</div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">
            Showing {filteredTimesheets.length} timesheet{filteredTimesheets.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Timesheets Table */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Contractor
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Supplier
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Hours
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Bill Amount
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
              {filteredTimesheets.map((timesheet) => (
                <React.Fragment key={timesheet.id}>
                  <tr className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      {timesheet.contractor}
                    </td>
                    <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                      {timesheet.supplier}
                    </td>
                    <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                      {timesheet.period}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      {timesheet.hours}h
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      ${timesheet.billAmount.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(timesheet.status)}`}>
                        {timesheet.status === 'MSP_REVIEW' ? 'MSP Review' : timesheet.status === 'CLIENT_APPROVAL' ? 'Client Approval' : timesheet.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setExpandedId(expandedId === timesheet.id ? null : timesheet.id)}
                          className="p-1 text-neutral-400 hover:text-primary-500 transition-colors"
                          title="View Details"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        {(timesheet.status === 'SUBMITTED' || timesheet.status === 'MSP_REVIEW') && (
                          <>
                            <button
                              onClick={() => handleApproveTimesheet(timesheet.id)}
                              className="px-2 py-1 text-xs bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded hover:bg-emerald-200 dark:hover:bg-emerald-900/40 transition-colors"
                              title="Approve"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleRejectTimesheet(timesheet.id)}
                              className="px-2 py-1 text-xs bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors"
                              title="Reject"
                            >
                              Reject
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                  {expandedId === timesheet.id && (
                    <tr className="bg-neutral-50 dark:bg-neutral-700/20">
                      <td colSpan={7} className="px-6 py-4">
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div>
                              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Contractor</p>
                              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.contractor}</p>
                            </div>
                            <div>
                              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Period</p>
                              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.period}</p>
                            </div>
                            <div>
                              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Total Hours</p>
                              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.hours} hours</p>
                            </div>
                            <div>
                              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Bill Amount</p>
                              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">${timesheet.billAmount.toLocaleString()}</p>
                            </div>
                          </div>
                          <div className="pt-2 border-t border-neutral-200 dark:border-neutral-600">
                            <p className="text-xs text-neutral-500 dark:text-neutral-400">Current Status</p>
                            <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                              {timesheet.status === 'MSP_REVIEW' ? 'Awaiting MSP Review' : timesheet.status === 'CLIENT_APPROVAL' ? 'Awaiting Client Approval' : timesheet.status === 'SUBMITTED' ? 'Submitted' : 'Approved'}
                            </p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {filteredTimesheets.length === 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-12 text-center border border-neutral-200 dark:border-neutral-700">
          <p className="text-neutral-500 dark:text-neutral-400">No timesheets found in this stage.</p>
        </div>
      )}
    </div>
  );
};

export default VMSTimesheets;
