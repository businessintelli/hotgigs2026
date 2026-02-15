import React, { useState } from 'react';
import { DataTable } from '@/components/common/DataTable';
import { SearchInput } from '@/components/common/SearchInput';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Card, CardBody } from '@/components/common/Card';
import { useApi } from '@/hooks/useApi';
import { getCandidates } from '@/api/candidates';
import { PlusIcon } from '@heroicons/react/24/outline';
import type { Candidate } from '@/types';

export const Candidates: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const { data: candidatesData, isLoading } = useApi(
    ['candidates', page, search, statusFilter],
    () =>
      getCandidates({
        page,
        per_page: 10,
        search: search || undefined,
        status: statusFilter || undefined,
      })
  );

  const columns = [
    {
      key: 'first_name' as const,
      label: 'Name',
      sortable: true,
      render: (value: unknown, row: Candidate) =>
        `${row.first_name} ${row.last_name}`,
    },
    { key: 'email' as const, label: 'Email', sortable: true },
    { key: 'current_title' as const, label: 'Title' },
    { key: 'location' as const, label: 'Location' },
    {
      key: 'total_experience_years' as const,
      label: 'Experience',
      render: (value: unknown) => `${value} years`,
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (value: unknown) => <StatusBadge status={value as string} />,
    },
  ];

  return (
    <>
      <div className="p-4 md:p-6 space-y-6 pb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">
              Candidates
            </h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Manage candidate pool and profiles
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors duration-250">
            <PlusIcon className="w-5 h-5" />
            <span>Add Candidate</span>
          </button>
        </div>

        <Card>
          <CardBody className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <SearchInput
                placeholder="Search candidates..."
                value={search}
                onSearch={setSearch}
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="placed">Placed</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          </CardBody>
        </Card>

        <DataTable
          columns={columns}
          data={candidatesData?.data || []}
          loading={isLoading}
          emptyMessage="No candidates found"
          pagination={
            candidatesData
              ? {
                  page: candidatesData.page,
                  per_page: candidatesData.per_page,
                  total: candidatesData.total,
                  onPageChange: setPage,
                }
              : undefined
          }
        />
      </div>
    </>
  );
};
