import React, { useState, useMemo } from 'react';
import clsx from 'clsx';
import { ChevronUpDownIcon, ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { Card, CardBody } from './Card';
import { LoadingSpinner, Skeleton } from './LoadingSpinner';
import { EmptyState } from './EmptyState';

interface Column<T> {
  key: keyof T;
  label: string;
  width?: string;
  sortable?: boolean;
  render?: (value: unknown, row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  onRowSelect?: (rows: T[]) => void;
  selectable?: boolean;
  hoverable?: boolean;
  pagination?: {
    page: number;
    per_page: number;
    total: number;
    onPageChange: (page: number) => void;
  };
}

type SortDirection = 'asc' | 'desc' | null;

export const DataTable = React.forwardRef<
  HTMLDivElement,
  DataTableProps<unknown>
>(
  (
    {
      columns,
      data,
      loading = false,
      error,
      emptyMessage = 'No data found',
      onRowClick,
      onRowSelect,
      selectable = false,
      hoverable = true,
      pagination,
    },
    ref
  ) => {
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>(null);
    const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());

    const sortedData = useMemo(() => {
      if (!sortKey || !sortDirection) return data;

      const sorted = [...data].sort((a, b) => {
        const aValue = (a as Record<string, unknown>)[sortKey];
        const bValue = (b as Record<string, unknown>)[sortKey];

        if (aValue === undefined || bValue === undefined) return 0;

        if (typeof aValue === 'string') {
          return sortDirection === 'asc'
            ? aValue.localeCompare(bValue as string)
            : (bValue as string).localeCompare(aValue);
        }

        if (typeof aValue === 'number') {
          return sortDirection === 'asc'
            ? (aValue as number) - (bValue as number)
            : (bValue as number) - (aValue as number);
        }

        return 0;
      });

      return sorted;
    }, [data, sortKey, sortDirection]);

    const handleSort = (key: string) => {
      if (sortKey === key) {
        if (sortDirection === 'asc') {
          setSortDirection('desc');
        } else if (sortDirection === 'desc') {
          setSortKey(null);
          setSortDirection(null);
        }
      } else {
        setSortKey(key);
        setSortDirection('asc');
      }
    };

    const handleSelectAll = (checked: boolean) => {
      if (checked) {
        setSelectedRows(new Set(data.map((_, i) => i)));
        onRowSelect?.(data);
      } else {
        setSelectedRows(new Set());
        onRowSelect?.([]);
      }
    };

    const handleSelectRow = (index: number) => {
      const newSelected = new Set(selectedRows);
      if (newSelected.has(index)) {
        newSelected.delete(index);
      } else {
        newSelected.add(index);
      }
      setSelectedRows(newSelected);
      onRowSelect?.(data.filter((_, i) => newSelected.has(i)));
    };

    if (loading) {
      return <Skeleton className="h-64" />;
    }

    if (error) {
      return (
        <Card>
          <CardBody className="text-center py-8">
            <p className="text-danger-600 dark:text-danger-400">{error}</p>
          </CardBody>
        </Card>
      );
    }

    if (data.length === 0) {
      return <EmptyState title={emptyMessage} />;
    }

    return (
      <Card ref={ref}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900">
              <tr>
                {selectable && (
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedRows.size === data.length && data.length > 0}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                      className="rounded border-neutral-300 dark:border-neutral-600"
                    />
                  </th>
                )}
                {columns.map((col) => (
                  <th
                    key={String(col.key)}
                    className={clsx(
                      'px-6 py-3 text-left text-sm font-semibold text-neutral-700 dark:text-neutral-300',
                      col.sortable && 'cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800'
                    )}
                    style={{ width: col.width }}
                    onClick={() => col.sortable && handleSort(String(col.key))}
                  >
                    <div className="flex items-center gap-2">
                      <span>{col.label}</span>
                      {col.sortable && (
                        <div className="flex-shrink-0">
                          {sortKey === String(col.key) ? (
                            sortDirection === 'asc' ? (
                              <ChevronUpIcon className="w-4 h-4" />
                            ) : (
                              <ChevronDownIcon className="w-4 h-4" />
                            )
                          ) : (
                            <ChevronUpDownIcon className="w-4 h-4 text-neutral-400" />
                          )}
                        </div>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {sortedData.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={clsx(
                    hoverable &&
                      'hover:bg-neutral-50 dark:hover:bg-neutral-900 transition-colors duration-250',
                    onRowClick && 'cursor-pointer'
                  )}
                  onClick={() => onRowClick?.(row as unknown)}
                >
                  {selectable && (
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedRows.has(rowIndex)}
                        onChange={() => handleSelectRow(rowIndex)}
                        onClick={(e) => e.stopPropagation()}
                        className="rounded border-neutral-300 dark:border-neutral-600"
                      />
                    </td>
                  )}
                  {columns.map((col) => (
                    <td
                      key={String(col.key)}
                      className="px-6 py-4 text-sm text-neutral-700 dark:text-neutral-300"
                      style={{ width: col.width }}
                    >
                      {col.render
                        ? col.render((row as Record<string, unknown>)[String(col.key)], row as unknown)
                        : String((row as Record<string, unknown>)[String(col.key)])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {pagination && (
          <div className="border-t border-neutral-200 dark:border-neutral-700 px-6 py-4 flex items-center justify-between">
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Showing {(pagination.page - 1) * pagination.per_page + 1} to{' '}
              {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
              {pagination.total} results
            </p>
            <div className="flex gap-2">
              <button
                onClick={() =>
                  pagination.page > 1 && pagination.onPageChange(pagination.page - 1)
                }
                disabled={pagination.page === 1}
                className="px-3 py-1 rounded border border-neutral-200 dark:border-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250"
              >
                Previous
              </button>
              <button
                onClick={() =>
                  pagination.page < Math.ceil(pagination.total / pagination.per_page) &&
                  pagination.onPageChange(pagination.page + 1)
                }
                disabled={
                  pagination.page >= Math.ceil(pagination.total / pagination.per_page)
                }
                className="px-3 py-1 rounded border border-neutral-200 dark:border-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </Card>
    );
  }
);

DataTable.displayName = 'DataTable';
