import React from 'react';
import { BuildingOfficeIcon, PlusIcon } from '@heroicons/react/24/outline';

const sampleClients = [
  { id: 1, name: 'Acme Corporation', industry: 'Technology', status: 'active', requirements: 12, placements: 5, contact: 'john@acme.com' },
  { id: 2, name: 'GlobalTech Solutions', industry: 'Finance', status: 'active', requirements: 8, placements: 3, contact: 'sarah@globaltech.com' },
  { id: 3, name: 'DataCorp Inc', industry: 'Healthcare', status: 'active', requirements: 15, placements: 7, contact: 'mike@datacorp.com' },
  { id: 4, name: 'InnovateTech', industry: 'E-commerce', status: 'pending_review', requirements: 0, placements: 0, contact: 'admin@innovatetech.com' },
];

const statusColors: Record<string, string> = {
  active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400',
  pending_review: 'bg-amber-100 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400',
  suspended: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400',
};

export const ClientsList: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Client Organizations</h1>
          <p className="text-neutral-500 dark:text-neutral-400 mt-1">Manage your client portfolio</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium">
          <PlusIcon className="w-4 h-4" />
          Onboard Client
        </button>
      </div>

      <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-neutral-50 dark:bg-neutral-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Organization</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Industry</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Requirements</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Placements</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
            {sampleClients.map((client) => (
              <tr key={client.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-750">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
                      <BuildingOfficeIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-neutral-900 dark:text-white">{client.name}</p>
                      <p className="text-xs text-neutral-500">{client.contact}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{client.industry}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[client.status] || ''}`}>
                    {client.status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{client.requirements}</td>
                <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{client.placements}</td>
                <td className="px-6 py-4">
                  <button className="text-sm text-primary-500 hover:text-primary-600">View Details</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
