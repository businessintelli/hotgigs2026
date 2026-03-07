import React from 'react';
import { TruckIcon, PlusIcon, StarIcon } from '@heroicons/react/24/outline';

const sampleSuppliers = [
  { id: 1, name: 'TechStaff Inc', tier: 'platinum', submissions: 45, placements: 12, quality: 92, status: 'active' },
  { id: 2, name: 'ProStaffing Solutions', tier: 'gold', submissions: 32, placements: 8, quality: 85, status: 'active' },
  { id: 3, name: 'GlobalRecruit', tier: 'silver', submissions: 18, placements: 4, quality: 78, status: 'active' },
  { id: 4, name: 'FastHire Agency', tier: 'bronze', submissions: 10, placements: 2, quality: 65, status: 'active' },
  { id: 5, name: 'NewTalent Co', tier: 'new', submissions: 3, placements: 0, quality: 0, status: 'pending_review' },
];

const tierColors: Record<string, string> = {
  platinum: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-400',
  gold: 'bg-amber-100 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400',
  silver: 'bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300',
  bronze: 'bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400',
  new: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400',
  standard: 'bg-neutral-100 text-neutral-600',
};

export const SuppliersList: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Supplier Organizations</h1>
          <p className="text-neutral-500 dark:text-neutral-400 mt-1">Manage your supplier network with performance scorecards</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors text-sm font-medium">
          <PlusIcon className="w-4 h-4" />
          Onboard Supplier
        </button>
      </div>

      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-neutral-50 dark:bg-neutral-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Supplier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Tier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Submissions</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Placements</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Quality Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
            {sampleSuppliers.map((supplier) => (
              <tr key={supplier.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-750">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center">
                      <TruckIcon className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                    </div>
                    <p className="text-sm font-medium text-neutral-900 dark:text-white">{supplier.name}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${tierColors[supplier.tier] || ''}`}>
                    {supplier.tier}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{supplier.submissions}</td>
                <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{supplier.placements}</td>
                <td className="px-6 py-4">
                  {supplier.quality > 0 ? (
                    <div className="flex items-center gap-1">
                      <div className="w-16 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${supplier.quality >= 80 ? 'bg-emerald-500' : supplier.quality >= 60 ? 'bg-amber-500' : 'bg-red-500'}`}
                          style={{ width: `${supplier.quality}%` }}
                        />
                      </div>
                      <span className="text-xs text-neutral-500">{supplier.quality}%</span>
                    </div>
                  ) : (
                    <span className="text-xs text-neutral-400">N/A</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <button className="text-sm text-primary-500 hover:text-primary-600">View Scorecard</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
