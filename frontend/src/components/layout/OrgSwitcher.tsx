import React, { useState } from 'react';
import clsx from 'clsx';
import { BuildingOffice2Icon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { useOrganizationStore } from '@/store/organizationStore';
import type { Organization } from '@/store/organizationStore';

const orgTypeColors: Record<string, string> = {
  msp: 'bg-indigo-500',
  client: 'bg-emerald-500',
  supplier: 'bg-amber-500',
};

const orgTypeLabels: Record<string, string> = {
  msp: 'MSP',
  client: 'Client',
  supplier: 'Supplier',
};

export const OrgSwitcher: React.FC = () => {
  const { currentOrg, organizations } = useOrganizationStore();
  const [isOpen, setIsOpen] = useState(false);

  if (!currentOrg) return null;

  const handleSwitch = async (org: Organization) => {
    // In production, call /organizations/{id}/switch API
    useOrganizationStore.getState().setCurrentOrg(org);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg',
          'bg-neutral-800 hover:bg-neutral-700 transition-colors',
          'text-white text-sm'
        )}
      >
        <div className={clsx('w-2 h-2 rounded-full', orgTypeColors[currentOrg.org_type] || 'bg-gray-500')} />
        <span className="font-medium max-w-[150px] truncate">{currentOrg.name}</span>
        <span className="text-xs text-neutral-400">
          {orgTypeLabels[currentOrg.org_type] || currentOrg.org_type}
        </span>
        {organizations.length > 1 && <ChevronDownIcon className="w-4 h-4 text-neutral-400" />}
      </button>

      {isOpen && organizations.length > 1 && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-neutral-800 rounded-lg shadow-xl border border-neutral-700 py-1 z-50">
          {organizations.map((org) => (
            <button
              key={org.id}
              onClick={() => handleSwitch(org)}
              className={clsx(
                'w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-neutral-700 transition-colors',
                org.id === currentOrg.id && 'bg-neutral-700'
              )}
            >
              <div className={clsx('w-2 h-2 rounded-full', orgTypeColors[org.org_type] || 'bg-gray-500')} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{org.name}</p>
                <p className="text-xs text-neutral-400">{orgTypeLabels[org.org_type] || org.org_type}</p>
              </div>
              {org.id === currentOrg.id && (
                <span className="text-xs text-primary-400">Active</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
