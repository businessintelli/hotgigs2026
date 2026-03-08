import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  CheckCircleIcon,
  ClockIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';
import client from '@/api/client';

interface SupplierTimesheet {
  id: string;
  placement: string;
  contractor: string;
  period: string;
  hours: number;
  payAmount: number;
  status: 'DRAFT' | 'SUBMITTED' | 'MSP_REVIEW' | 'APPROVED' | 'REJECTED';
  submittedDate?: string;
}

const mockSupplierTimesheets: SupplierTimesheet[] = [
  {
    id: '1',
    placement: 'Req #1042 - Senior Java Developer',
    contractor: 'John Smith',
    period: 'Mar 1-7, 2025',
    hours: 40,
    payAmount: 4800,
    status: 'APPROVED',
    submittedDate: '2025-03-07',
  },
  {
    id: '2',
    placement: 'Req #1040 - React Developer',
    contractor: 'Jane Doe',
    period: 'Mar 1-7, 2025',
    hours: 38,
    payAmount: 4560,
    status: 'APPROVED',
    submittedDate: '2025-03-06',
  },
  {
    id: '3',
    placement: 'Req #1045 - Project Manager',
    contractor: 'Mike Johnson',
    period: 'Mar 1-7, 2025',
    hours: 40,
    payAmount: 3200,
    status: 'MSP_REVIEW',
    submittedDate: '2025-03-07',
  },
  {
    id: '4',
    placement: 'Req #1041 - Data Engineer',
    contractor: 'Alice Brown',
    period: 'Feb 24-Mar 2, 2025',
    hours: 36,
    payAmount: 3960,
    status: 'SUBMITTED',
    submittedDate: '2025-03-06',
  },
  {
    id: '5',
    placement: 'Req #1039 - QA Engineer',
    contractor: 'Bob Wilson',
    period: 'Feb 24-Mar 2, 2025',
    hours: 39,
    payAmount: 2730,
    status: 'DRAFT',
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'DRAFT':
      return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-400';
    case 'SUBMITTED':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'MSP_REVIEW':
      return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400';
    case 'APPROVED':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case 'REJECTED':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const SupplierTimesheets: React.FC = () => {
  const [allTimesheets, setAllTimesheets] = useState<SupplierTimesheet[]>(mockSupplierTimesheets);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    placement: '',
    period: '',
    hours: '',
  });

  useEffect(() => {
    const fetchTimesheets = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await client.get('/vms/timesheets?status=submitted');
        if (response.data && response.data.length > 0) {
          setAllTimesheets(response.data);
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

  const draftTimesheets = allTimesheets.filter(ts => ts.status === 'DRAFT');
  const submittedTimesheets = allTimesheets.filter(ts => ts.status !== 'DRAFT');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newTimesheet = {
        placement: formData.placement,
        period: formData.period,
        hours: parseFloat(formData.hours),
      };
      const response = await client.post('/vms/timesheets', newTimesheet);
      setAllTimesheets([...allTimesheets, response.data]);
      console.log('Timesheet submitted successfully:', response.data);
      setFormData({ placement: '', period: '', hours: '' });
      setIsCreateFormOpen(false);
    } catch (err) {
      console.error('Failed to submit timesheet:', err);
      alert('Failed to submit timesheet');
    }
  };

  const handleSubmitDraft = async (id: string) => {
    try {
      const timesheet = allTimesheets.find(ts => ts.id === id);
      if (!timesheet) return;
      const response = await client.post('/vms/timesheets', {
        ...timesheet,
        status: 'SUBMITTED',
      });
      setAllTimesheets(allTimesheets.map(ts =>
        ts.id === id ? { ...ts, status: 'SUBMITTED', submittedDate: new Date().toISOString().split('T')[0] } : ts
      ));
      console.log('Draft timesheet submitted');
    } catch (err) {
      console.error('Failed to submit draft:', err);
      alert('Failed to submit draft');
    }
  };

  const totalPayAmount = allTimesheets.reduce((sum, ts) => sum + ts.payAmount, 0);
  const approvedAmount = allTimesheets
    .filter(ts => ts.status === 'APPROVED')
    .reduce((sum, ts) => sum + ts.payAmount, 0);

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
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Timesheets</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Submit and track timesheets for your placements
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">Drafts</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">{draftTimesheets.length}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">Total Payable</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">${totalPayAmount.toLocaleString()}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">Approved & Paid</p>
          <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-2">${approvedAmount.toLocaleString()}</p>
        </div>
      </div>

      {/* Submit Timesheet Button */}
      <div className="flex justify-end">
        <button
          onClick={() => setIsCreateFormOpen(!isCreateFormOpen)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium"
        >
          <PlusIcon className="w-5 h-5" />
          Submit Timesheet
        </button>
      </div>

      {/* Submit Form - Inline */}
      {isCreateFormOpen && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700 space-y-4">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Submit New Timesheet</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                  Placement *
                </label>
                <select
                  required
                  value={formData.placement}
                  onChange={(e) => setFormData({ ...formData, placement: e.target.value })}
                  className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select a placement</option>
                  <option value="req-1042">Req #1042 - Senior Java Developer</option>
                  <option value="req-1040">Req #1040 - React Developer</option>
                  <option value="req-1045">Req #1045 - Project Manager</option>
                  <option value="req-1041">Req #1041 - Data Engineer</option>
                  <option value="req-1039">Req #1039 - QA Engineer</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                  Period (Start Date) *
                </label>
                <input
                  type="date"
                  required
                  value={formData.period}
                  onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                  className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                  Total Hours *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  max="168"
                  step="0.5"
                  value={formData.hours}
                  onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
                  placeholder="e.g., 40"
                  className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium"
              >
                Submit Timesheet
              </button>
              <button
                type="button"
                onClick={() => setIsCreateFormOpen(false)}
                className="px-4 py-2 bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-white rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Draft Timesheets */}
      {draftTimesheets.length > 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="p-6 border-b border-neutral-200 dark:border-neutral-700 bg-gray-50 dark:bg-gray-900/10">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Drafts ({draftTimesheets.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Placement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Contractor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Hours
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Pay Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {draftTimesheets.map((timesheet) => (
                  <tr key={timesheet.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      {timesheet.placement}
                    </td>
                    <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                      {timesheet.contractor}
                    </td>
                    <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                      {timesheet.period}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      {timesheet.hours}h
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                      ${timesheet.payAmount.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleSubmitDraft(timesheet.id)}
                          className="px-3 py-1 text-xs bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 rounded hover:bg-primary-200 dark:hover:bg-primary-900/40 transition-colors font-medium"
                          title="Submit"
                        >
                          Submit
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Submitted Timesheets */}
      {submittedTimesheets.length > 0 && (
        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">All Timesheets ({submittedTimesheets.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Placement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Contractor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Hours
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Pay Amount
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
                {submittedTimesheets.map((timesheet) => (
                  <React.Fragment key={timesheet.id}>
                    <tr className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                        {timesheet.placement}
                      </td>
                      <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                        {timesheet.contractor}
                      </td>
                      <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                        {timesheet.period}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                        {timesheet.hours}h
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">
                        ${timesheet.payAmount.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(timesheet.status)}`}>
                          {timesheet.status === 'MSP_REVIEW' ? 'MSP Review' : timesheet.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <button
                          onClick={() => setExpandedId(expandedId === timesheet.id ? null : timesheet.id)}
                          className="p-1 text-neutral-400 hover:text-primary-500 transition-colors"
                          title="View Details"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                    {expandedId === timesheet.id && (
                      <tr className="bg-neutral-50 dark:bg-neutral-700/20">
                        <td colSpan={7} className="px-6 py-4">
                          <div className="space-y-3">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Placement</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.placement}</p>
                              </div>
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Contractor</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.contractor}</p>
                              </div>
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Period</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">{timesheet.period}</p>
                              </div>
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">Status</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                                  {timesheet.status === 'MSP_REVIEW' ? 'In Review' : timesheet.status}
                                </p>
                              </div>
                            </div>
                            <div className="pt-2 border-t border-neutral-200 dark:border-neutral-600">
                              <p className="text-xs text-neutral-500 dark:text-neutral-400">Pay Details</p>
                              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                                {timesheet.hours} hours @ ${(timesheet.payAmount / timesheet.hours).toFixed(2)}/hr = ${timesheet.payAmount.toLocaleString()}
                              </p>
                            </div>
                            {timesheet.submittedDate && (
                              <div>
                                <p className="text-xs text-neutral-500 dark:text-neutral-400">Submitted</p>
                                <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                                  {new Date(timesheet.submittedDate).toLocaleDateString()}
                                </p>
                              </div>
                            )}
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
    </div>
  );
};

export default SupplierTimesheets;
