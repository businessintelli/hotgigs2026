import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { DataTable } from '@/components/common/DataTable';
import { SearchInput } from '@/components/common/SearchInput';
import { StatusBadge, PriorityBadge } from '@/components/common/StatusBadge';
import { Modal } from '@/components/common/Modal';
import { LoadingSpinner, Skeleton } from '@/components/common/LoadingSpinner';
import { useApi } from '@/hooks/useApi';
import { getRequirements } from '@/api/requirements';
import { PlusIcon } from '@heroicons/react/24/outline';
import type { Requirement } from '@/types';

export const Requirements: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: requirementsData, isLoading } = useApi(
    ['requirements', page, search, statusFilter, priorityFilter],
    () =>
      getRequirements({
        page,
        per_page: 10,
        search: search || undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
      })
  );

  const columns = [
    {
      key: 'title' as const,
      label: 'Title',
      sortable: true,
      render: (value: unknown, row: Requirement) => (
        <button
          onClick={() => navigate(`/requirements/${row.id}`)}
          className="font-medium text-primary-500 hover:text-primary-600 dark:hover:text-primary-400"
        >
          {value}
        </button>
      ),
    },
    {
      key: 'customer_name' as const,
      label: 'Customer',
      sortable: true,
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (value: unknown) => <StatusBadge status={value as string} />,
    },
    {
      key: 'priority' as const,
      label: 'Priority',
      render: (value: unknown) => <PriorityBadge priority={value as any} />,
    },
    {
      key: 'active_submissions' as const,
      label: 'Submissions',
    },
    {
      key: 'interviews_scheduled' as const,
      label: 'Interviews',
    },
  ];

  return (
    <AppLayout title="Requirements">
      <div className="p-4 md:p-6 space-y-6 pb-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">
              Job Requirements
            </h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Manage open positions and requirements
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors duration-250"
          >
            <PlusIcon className="w-5 h-5" />
            <span>New Requirement</span>
          </button>
        </div>

        {/* Filters */}
        <Card>
          <CardBody className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <SearchInput
                placeholder="Search requirements..."
                value={search}
                onSearch={setSearch}
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="on_hold">On Hold</option>
                <option value="filled">Filled</option>
              </select>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              >
                <option value="">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </CardBody>
        </Card>

        {/* Table */}
        <DataTable
          columns={columns}
          data={requirementsData?.data || []}
          loading={isLoading}
          emptyMessage="No requirements found"
          pagination={
            requirementsData
              ? {
                  page: requirementsData.page,
                  per_page: requirementsData.per_page,
                  total: requirementsData.total,
                  onPageChange: setPage,
                }
              : undefined
          }
        />
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Requirement"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              Title
            </label>
            <input
              type="text"
              placeholder="Senior Software Engineer"
              className="w-full px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              Customer
            </label>
            <select className="w-full px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option>Select customer...</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                Priority
              </label>
              <select className="w-full px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                Job Type
              </label>
              <select className="w-full px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="permanent">Permanent</option>
                <option value="contract">Contract</option>
                <option value="temporary">Temporary</option>
              </select>
            </div>
          </div>
        </div>
        <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200 dark:border-neutral-700">
          <button
            onClick={() => setShowCreateModal(false)}
            className="flex-1 px-4 py-2 border border-neutral-200 dark:border-neutral-700 rounded-lg font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250"
          >
            Cancel
          </button>
          <button
            onClick={() => setShowCreateModal(false)}
            className="flex-1 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors duration-250"
          >
            Create
          </button>
        </div>
      </Modal>
    </AppLayout>
  );
};
