import React, { useState } from 'react';
import {
  CheckCircleIcon,
  XMarkIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';

interface ClientTimesheet {
  id: string;
  contractor: string;
  supplier: string;
  period: string;
  hours: number;
  amount: number;
  status: 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED';
  submittedDate: string;
}

const mockClientTimesheets: ClientTimesheet[] = [
  {
    id: '1',
    contractor: 'Jane Doe',
    supplier: 'ProStaffing',
    period: 'Mar 1-7, 2025',
    hours: 38,
    amount: 5700,
    status: 'PENDING_APPROVAL',
    submittedDate: '2025-03-07',
  },
  {
    id: '2',
    contractor: 'Alice Brown',
    supplier: 'TechStaff Inc',
    period: 'Mar 1-7, 2025',
    hours: 36,
    amount: 4800,
    status: 'PENDING_APPROVAL',
    submittedDate: '2025-03-07',
  },
  {
    id: '3',
    contractor: 'Mike Johnson',
    supplier: 'GlobalTech Staffing',
    period: 'Feb 24-Mar 2, 2025',
    hours: 40,
    amount: 5200,
    status: 'APPROVED',
    submittedDate: '2025-03-04',
  },
  {
    id: '4',
    contractor: 'Sarah Lee',
    supplier: 'ProStaffing',
    period: 'Feb 24-Mar 2, 2025',
    hours: 39,
    amount: 5850,
    status: 'APPROVED',
    submittedDate: '2025-03-04',
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'PENDING_APPROVAL':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'APPROVED':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case 'REJECTED':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const ClientTimesheets: React.FC = () => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showConfirmation, setShowConfirmation] = useState<{ id: string; action: 'approve' | 'reject' } | null>(null);

  const pendingTimesheets = mockClientTimesheets.filter(ts => ts.status === 'PENDING_APPROVAL');
  const approvedTimesheets = mockClientTimesheets.filter(ts => ts.status === 'APPROVED');
  const rejectedTimesheets = mockClientTimesheets.filter(ts => ts.status === 'REJECTED');

  const handleApprove = (id: string) => {
    setShowConfirmation(null);
    // In a real app, this would call an API
    console.log('Approved timesheet:', id);
  };

  const handleReject = (id: string) => {
    setShowConfirmation(null);
    // In a real app, this would call an API
    console.log('Rejected timesheet:', id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Timesheets</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Review and approve timesheets from your contractors
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">Pending Approval</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">{pendingTimesheets.length}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">Approved</p>
          <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-2">{approvedTimesheets.length}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">Total Amount</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
            ${mockClientTimesheets.reduce((sum, ts) => sum + ts.amount, 0).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Pending Timesheets */}
      {pendingTimesheets.length > 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="p-6 border-b border-neutral-200 dark:border-neutral-700 bg-amber-50 dark:bg-amber-900/10">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Pending Approval ({pendingTimesheets.length})</h2>
          </div>
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
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {pendingTimesheets.map((timesheet) => (
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
                        ${timesheet.amount.toLocaleString()}
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
                          <button
                            onClick={() => setShowConfirmation({ id: timesheet.id, action: 'approve' })}
                            className="px-3 py-1 text-xs bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded hover:bg-emerald-200 dark:hover:bg-emerald-900/40 transition-colors font-medium"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => setShowConfirmation({ id: timesheet.id, action: 'reject' })}
                            className="px-3 py-1 text-xs bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors font-medium"
                          >
                            Reject
                          </button>
                        </div>
                      </td>
                    </tr>
                    {expandedId === timesheet.id && (
                      <tr className="bg-neutral-50 dark:bg-neutral-700/20">
                        <td colSpan={6} className="px-6 py-4">
                          <div className="space-y-3">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Contractor</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.contractor}</p>
                              </div>
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Supplier</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.supplier}</p>
                              </div>
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Period</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.period}</p>
                              </div>
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Submitted</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{new Date(timesheet.submittedDate).toLocaleDateString()}</p>
                              </div>
                            </div>
                            <div className="pt-2 border-t border-neutral-200 dark:border-neutral-600">
                              <p className="text-xs text-neutral-500 dark:text-neutral-400">Hours & Amount</p>
                              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                                {timesheet.hours} hours @ ${(timesheet.amount / timesheet.hours).toFixed(2)}/hr = ${timesheet.amount.toLocaleString()}
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
      )}

      {/* Approved Timesheets */}
      {approvedTimesheets.length > 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="p-6 border-b border-neutral-200 dark:border-neutral-700 bg-emerald-50 dark:bg-emerald-900/10">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Approved ({approvedTimesheets.length})</h2>
          </div>
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
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {approvedTimesheets.map((timesheet) => (
                  <tr key={timesheet.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
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
                    <td className="px-6 py-4 text-sm font-medium text-emerald-600 dark:text-emerald-400">
                      ${timesheet.amount.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 max-w-md w-full shadow-lg">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-2">
              {showConfirmation.action === 'approve' ? 'Approve Timesheet?' : 'Reject Timesheet?'}
            </h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-6">
              {showConfirmation.action === 'approve'
                ? 'This timesheet will be marked as approved and forwarded for payment processing.'
                : 'This timesheet will be rejected and returned to the supplier for revision.'}
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmation(null)}
                className="flex-1 px-4 py-2 bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-white rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors text-sm font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (showConfirmation.action === 'approve') {
                    handleApprove(showConfirmation.id);
                  } else {
                    handleReject(showConfirmation.id);
                  }
                }}
                className={`flex-1 px-4 py-2 text-white rounded-lg transition-colors text-sm font-medium ${
                  showConfirmation.action === 'approve'
                    ? 'bg-emerald-500 hover:bg-emerald-600'
                    : 'bg-red-500 hover:bg-red-600'
                }`}
              >
                {showConfirmation.action === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientTimesheets;
