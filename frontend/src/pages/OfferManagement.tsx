import React, { useState } from 'react';
import { ChevronRightIcon, ClockIcon, CheckCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface Offer {
  id: string;
  candidate: string;
  position: string;
  client: string;
  billRate: string;
  payRate: string;
  startDate: string;
  status: 'Draft' | 'Pending Approval' | 'Approved' | 'Extended' | 'Accepted' | 'Declined' | 'Expired' | 'Countered';
  expiryDate: string;
  daysUntilExpiry: number;
}

interface StatusChange {
  status: string;
  date: string;
  changedBy: string;
}

interface CounterOffer {
  id: string;
  proposedBillRate: string;
  proposedPayRate: string;
  proposedStartDate: string;
  status: 'Pending' | 'Accepted' | 'Rejected';
}

const mockOffers: Offer[] = [
  {
    id: '1',
    candidate: 'Sarah Johnson',
    position: 'Senior Frontend Engineer',
    client: 'TechCorp Industries',
    billRate: '$85/hr',
    payRate: '$65/hr',
    startDate: 'Mar 17, 2026',
    status: 'Accepted',
    expiryDate: 'Mar 15, 2026',
    daysUntilExpiry: 7,
  },
  {
    id: '2',
    candidate: 'Alex Chen',
    position: 'Full Stack Developer',
    client: 'CloudSystems Inc',
    billRate: '$75/hr',
    payRate: '$55/hr',
    startDate: 'Mar 20, 2026',
    status: 'Approved',
    expiryDate: 'Mar 18, 2026',
    daysUntilExpiry: 10,
  },
  {
    id: '3',
    candidate: 'Emma Davis',
    position: 'DevOps Engineer',
    client: 'DataFlow Solutions',
    billRate: '$80/hr',
    payRate: '$60/hr',
    startDate: 'Mar 25, 2026',
    status: 'Pending Approval',
    expiryDate: 'Mar 20, 2026',
    daysUntilExpiry: 12,
  },
  {
    id: '4',
    candidate: 'Mike Johnson',
    position: 'Product Manager',
    client: 'InnovateLabs',
    billRate: '$90/hr',
    payRate: '$70/hr',
    startDate: 'Apr 1, 2026',
    status: 'Countered',
    expiryDate: 'Mar 19, 2026',
    daysUntilExpiry: 11,
  },
  {
    id: '5',
    candidate: 'Jennifer Martinez',
    position: 'QA Engineer',
    client: 'WebDynamics',
    billRate: '$65/hr',
    payRate: '$50/hr',
    startDate: 'Mar 22, 2026',
    status: 'Expired',
    expiryDate: 'Mar 10, 2026',
    daysUntilExpiry: -1,
  },
  {
    id: '6',
    candidate: 'David Wong',
    position: 'UI/UX Designer',
    client: 'DesignStudio',
    billRate: '$70/hr',
    payRate: '$55/hr',
    startDate: 'Apr 5, 2026',
    status: 'Draft',
    expiryDate: 'Mar 25, 2026',
    daysUntilExpiry: 17,
  },
];

const mockStatusHistory: StatusChange[] = [
  { status: 'Accepted', date: 'Mar 9, 2026', changedBy: 'Candidate' },
  { status: 'Approved', date: 'Mar 8, 2026', changedBy: 'Hiring Manager' },
  { status: 'Pending Approval', date: 'Mar 7, 2026', changedBy: 'System' },
  { status: 'Draft', date: 'Mar 6, 2026', changedBy: 'John Smith' },
];

const mockCounterOffer: CounterOffer = {
  id: '1',
  proposedBillRate: '$95/hr',
  proposedPayRate: '$72/hr',
  proposedStartDate: 'Mar 20, 2026',
  status: 'Pending',
};

const pipelineStages = [
  { name: 'Draft', offers: 1 },
  { name: 'Pending Approval', offers: 1 },
  { name: 'Approved', offers: 1 },
  { name: 'Extended', offers: 0 },
  { name: 'Accepted', offers: 1 },
  { name: 'Declined', offers: 0 },
  { name: 'Expired', offers: 1 },
  { name: 'Countered', offers: 1 },
];

const getStatusColor = (status: Offer['status']) => {
  switch (status) {
    case 'Draft':
      return 'bg-gray-100 dark:bg-gray-900/20 text-gray-700 dark:text-gray-400';
    case 'Pending Approval':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'Approved':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'Extended':
      return 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400';
    case 'Accepted':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'Declined':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'Expired':
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
    case 'Countered':
      return 'bg-indigo-100 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getCounterOfferColor = (status: CounterOffer['status']) => {
  switch (status) {
    case 'Pending':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'Accepted':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'Rejected':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

export const OfferManagement: React.FC = () => {
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(mockOffers[0]);

  const totalOffers = mockOffers.length;
  const acceptedOffers = mockOffers.filter(o => o.status === 'Accepted').length;
  const declinedOffers = mockOffers.filter(o => o.status === 'Declined').length;
  const expiredOffers = mockOffers.filter(o => o.status === 'Expired').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Offer Management</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Track offer lifecycle and negotiations</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Total Offers</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">{totalOffers}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Accepted</p>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">{acceptedOffers}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Declined</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">{declinedOffers}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Expired</p>
          <p className="text-3xl font-bold text-neutral-600 dark:text-neutral-400 mt-2">{expiredOffers}</p>
        </div>
      </div>

      {/* Pipeline View */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Offer Pipeline</h3>
        <div className="flex flex-wrap gap-4 items-center justify-between">
          {pipelineStages.map((stage, idx) => (
            <div key={stage.name} className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-neutral-900 dark:text-white">{stage.offers}</div>
                <div className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">{stage.name}</div>
              </div>
              {idx !== pipelineStages.length - 1 && (
                <ChevronRightIcon className="w-5 h-5 text-neutral-400 hidden sm:block" />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Offers Table */}
        <div className="lg:col-span-2 bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-700/30">
                <tr className="border-b border-neutral-200 dark:border-neutral-700">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Candidate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                    Expiry
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {mockOffers.map((offer) => (
                  <tr
                    key={offer.id}
                    onClick={() => setSelectedOffer(offer)}
                    className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors cursor-pointer"
                  >
                    <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">{offer.candidate}</td>
                    <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{offer.position}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${getStatusColor(offer.status)}`}>
                        {offer.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">
                        <ClockIcon className={`w-4 h-4 ${offer.daysUntilExpiry < 3 ? 'text-red-500' : 'text-neutral-500'}`} />
                        <span className={offer.daysUntilExpiry < 3 ? 'text-red-600 dark:text-red-400 font-medium' : 'text-neutral-600 dark:text-neutral-400'}>
                          {offer.daysUntilExpiry} days
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Offer Detail Panel */}
        {selectedOffer && (
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Offer Details</h3>
            <div className="space-y-4">
              <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Candidate</p>
                <p className="text-base font-semibold text-neutral-900 dark:text-white mt-1">{selectedOffer.candidate}</p>
              </div>
              <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Position</p>
                <p className="text-base font-semibold text-neutral-900 dark:text-white mt-1">{selectedOffer.position}</p>
              </div>
              <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Client</p>
                <p className="text-base font-semibold text-neutral-900 dark:text-white mt-1">{selectedOffer.client}</p>
              </div>
              <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Bill Rate</p>
                <p className="text-base font-semibold text-neutral-900 dark:text-white mt-1">{selectedOffer.billRate}</p>
              </div>
              <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Pay Rate</p>
                <p className="text-base font-semibold text-neutral-900 dark:text-white mt-1">{selectedOffer.payRate}</p>
              </div>
              <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Start Date</p>
                <p className="text-base font-semibold text-neutral-900 dark:text-white mt-1">{selectedOffer.startDate}</p>
              </div>
              <div className="pb-4">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">Status</p>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block mt-2 ${getStatusColor(selectedOffer.status)}`}>
                  {selectedOffer.status}
                </span>
              </div>
            </div>

            {/* Status History */}
            <div className="mt-8 border-t border-neutral-200 dark:border-neutral-700 pt-6">
              <h4 className="font-semibold text-neutral-900 dark:text-white mb-4">Status History</h4>
              <div className="space-y-3">
                {mockStatusHistory.map((change, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircleIcon className="w-4 h-4 text-emerald-500 mt-1 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-neutral-900 dark:text-white">{change.status}</p>
                      <p className="text-xs text-neutral-500 dark:text-neutral-500">
                        {change.date} by {change.changedBy}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Counter Offer */}
            {selectedOffer.status === 'Countered' && (
              <div className="mt-8 border-t border-neutral-200 dark:border-neutral-700 pt-6">
                <h4 className="font-semibold text-neutral-900 dark:text-white mb-4">Counter Offer</h4>
                <div className="bg-indigo-50 dark:bg-indigo-900/10 rounded-lg p-4 space-y-3">
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Proposed Bill Rate</p>
                    <p className="text-sm font-semibold text-neutral-900 dark:text-white mt-1">{mockCounterOffer.proposedBillRate}</p>
                  </div>
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Proposed Pay Rate</p>
                    <p className="text-sm font-semibold text-neutral-900 dark:text-white mt-1">{mockCounterOffer.proposedPayRate}</p>
                  </div>
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Proposed Start Date</p>
                    <p className="text-sm font-semibold text-neutral-900 dark:text-white mt-1">{mockCounterOffer.proposedStartDate}</p>
                  </div>
                  <div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${getCounterOfferColor(mockCounterOffer.status)}`}>
                      {mockCounterOffer.status}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default OfferManagement;
