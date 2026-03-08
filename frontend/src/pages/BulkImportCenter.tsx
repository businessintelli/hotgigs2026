import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import {
  CloudArrowUpIcon,
  DocumentArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface ImportJob {
  id: string;
  type: 'resumes' | 'candidates' | 'requirements' | 'placements' | 'associates';
  fileName: string;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'COMPLETED_WITH_ERRORS' | 'FAILED';
  progress?: number;
  totalRecords: number;
  successCount: number;
  failureCount: number;
  skippedCount: number;
  duration?: number;
  startedAt: string;
  completedAt?: string;
}

interface FailureRecord {
  rowNumber: number;
  originalData: Record<string, any>;
  errorMessage: string;
  fieldErrors: Record<string, string>;
}

interface ImportJobDetail extends ImportJob {
  successRecords: Array<{ rowNumber: number; name: string; createdId: string }>;
  failureRecords: FailureRecord[];
  skippedRecords: Array<{ rowNumber: number; reason: string }>;
  notification: string;
}

const importTypeInfo: Record<string, { label: string; columns: string[] }> = {
  resumes: {
    label: 'Resumes (PDF/DOC)',
    columns: ['Resume File', 'Candidate Name', 'Email', 'Phone'],
  },
  candidates: {
    label: 'Candidates (Excel)',
    columns: ['First Name', 'Last Name', 'Email', 'Phone', 'Skills', 'Experience (Years)'],
  },
  requirements: {
    label: 'Requirements (Excel)',
    columns: ['Title', 'Client', 'Status', 'Skills Required', 'Rate', 'Duration'],
  },
  placements: {
    label: 'Placements (Excel)',
    columns: ['Candidate', 'Requirement', 'Start Date', 'Status', 'Rate'],
  },
  associates: {
    label: 'Associates (Excel)',
    columns: ['Name', 'Email', 'Phone', 'Department', 'Role'],
  },
};

const mockJobs: ImportJob[] = [
  {
    id: 'IMP-20260308-001',
    type: 'candidates',
    fileName: 'candidates_batch_01.xlsx',
    status: 'QUEUED',
    totalRecords: 150,
    successCount: 0,
    failureCount: 0,
    skippedCount: 0,
    startedAt: new Date(Date.now() - 5 * 60000).toISOString(),
  },
  {
    id: 'IMP-20260308-002',
    type: 'resumes',
    fileName: 'resumes_march.pdf',
    status: 'PROCESSING',
    progress: 67,
    totalRecords: 45,
    successCount: 30,
    failureCount: 2,
    skippedCount: 0,
    startedAt: new Date(Date.now() - 15 * 60000).toISOString(),
  },
  {
    id: 'IMP-20260307-045',
    type: 'requirements',
    fileName: 'requirements_q1.xlsx',
    status: 'COMPLETED',
    progress: 100,
    totalRecords: 28,
    successCount: 28,
    failureCount: 0,
    skippedCount: 0,
    startedAt: new Date(Date.now() - 2 * 3600000).toISOString(),
    completedAt: new Date(Date.now() - 1.5 * 3600000).toISOString(),
    duration: 1800,
  },
  {
    id: 'IMP-20260307-044',
    type: 'placements',
    fileName: 'placements_march.xlsx',
    status: 'COMPLETED',
    progress: 100,
    totalRecords: 35,
    successCount: 35,
    failureCount: 0,
    skippedCount: 0,
    startedAt: new Date(Date.now() - 4 * 3600000).toISOString(),
    completedAt: new Date(Date.now() - 3.5 * 3600000).toISOString(),
    duration: 1800,
  },
  {
    id: 'IMP-20260307-043',
    type: 'candidates',
    fileName: 'candidates_legacy.xlsx',
    status: 'COMPLETED_WITH_ERRORS',
    progress: 100,
    totalRecords: 89,
    successCount: 82,
    failureCount: 5,
    skippedCount: 2,
    startedAt: new Date(Date.now() - 6 * 3600000).toISOString(),
    completedAt: new Date(Date.now() - 5.5 * 3600000).toISOString(),
    duration: 2400,
  },
  {
    id: 'IMP-20260307-042',
    type: 'associates',
    fileName: 'associates_batch.xlsx',
    status: 'COMPLETED_WITH_ERRORS',
    progress: 100,
    totalRecords: 12,
    successCount: 10,
    failureCount: 2,
    skippedCount: 0,
    startedAt: new Date(Date.now() - 8 * 3600000).toISOString(),
    completedAt: new Date(Date.now() - 7.5 * 3600000).toISOString(),
    duration: 900,
  },
  {
    id: 'IMP-20260306-041',
    type: 'requirements',
    fileName: 'requirements_old.xlsx',
    status: 'FAILED',
    progress: 0,
    totalRecords: 15,
    successCount: 0,
    failureCount: 15,
    skippedCount: 0,
    startedAt: new Date(Date.now() - 24 * 3600000).toISOString(),
    completedAt: new Date(Date.now() - 24 * 3600000 + 30000).toISOString(),
    duration: 30,
  },
];

const mockJobDetail: ImportJobDetail = {
  id: 'IMP-20260307-043',
  type: 'candidates',
  fileName: 'candidates_legacy.xlsx',
  status: 'COMPLETED_WITH_ERRORS',
  progress: 100,
  totalRecords: 89,
  successCount: 82,
  failureCount: 5,
  skippedCount: 2,
  startedAt: new Date(Date.now() - 6 * 3600000).toISOString(),
  completedAt: new Date(Date.now() - 5.5 * 3600000).toISOString(),
  duration: 2400,
  successRecords: [
    { rowNumber: 1, name: 'Alice Johnson', createdId: 'CAN-001234' },
    { rowNumber: 2, name: 'Bob Smith', createdId: 'CAN-001235' },
    { rowNumber: 4, name: 'Carol Williams', createdId: 'CAN-001236' },
  ],
  failureRecords: [
    {
      rowNumber: 3,
      originalData: { name: 'John Smith', email: 'john@', skills: 'Python, Java', experience: 5 },
      errorMessage: 'Invalid email format',
      fieldErrors: { email: 'Email must be valid format (user@domain.com)' },
    },
    {
      rowNumber: 7,
      originalData: { name: '', email: 'jane@example.com', skills: '', experience: 3 },
      errorMessage: 'Required field missing: skills',
      fieldErrors: { skills: 'Skills field cannot be empty' },
    },
    {
      rowNumber: 12,
      originalData: { name: 'Jane Doe', email: 'jane.doe@example.com', skills: 'React', experience: '$abc' },
      errorMessage: 'Invalid rate format. Expected number.',
      fieldErrors: { experience: 'Experience must be a number (0-50)' },
    },
  ],
  skippedRecords: [
    { rowNumber: 5, reason: 'Duplicate email: already exists in system' },
    { rowNumber: 15, reason: 'Required field missing: email' },
  ],
  notification: 'Import completed with 5 errors. 82 records imported successfully. Review and re-import failed records.',
};

const getStatusIcon = (status: ImportJob['status']) => {
  switch (status) {
    case 'QUEUED':
      return <div className="w-4 h-4 rounded-full border-2 border-gray-400 animate-pulse" />;
    case 'PROCESSING':
      return <ArrowPathIcon className="w-4 h-4 text-blue-500 animate-spin" />;
    case 'COMPLETED':
      return <CheckCircleIcon className="w-4 h-4 text-success-500" />;
    case 'COMPLETED_WITH_ERRORS':
      return <ExclamationTriangleIcon className="w-4 h-4 text-warning-500" />;
    case 'FAILED':
      return <XCircleIcon className="w-4 h-4 text-danger-500" />;
  }
};

const getStatusColor = (status: ImportJob['status']) => {
  switch (status) {
    case 'QUEUED':
      return 'bg-gray-50 text-gray-700 dark:bg-gray-900 dark:text-gray-200';
    case 'PROCESSING':
      return 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200';
    case 'COMPLETED':
      return 'bg-success-50 text-success-700 dark:bg-success-900 dark:text-success-200';
    case 'COMPLETED_WITH_ERRORS':
      return 'bg-warning-50 text-warning-700 dark:bg-warning-900 dark:text-warning-200';
    case 'FAILED':
      return 'bg-danger-50 text-danger-700 dark:bg-danger-900 dark:text-danger-200';
  }
};

export const BulkImportCenter: React.FC = () => {
  const [selectedType, setSelectedType] = useState<ImportJob['type']>('candidates');
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'success' | 'failures' | 'skipped'>('failures');
  const [lastUpdated] = useState(new Date());

  const handleDownloadTemplate = (type: ImportJob['type']) => {
    console.log('Download template for:', type);
  };

  const handleStartImport = () => {
    console.log('Start import for:', selectedType);
  };

  const handleDownloadFailures = () => {
    console.log('Download failures as Excel');
  };

  const handleReImportFailed = () => {
    console.log('Re-import failed records');
  };

  const selectedJobDetail = expandedJobId === mockJobDetail.id ? mockJobDetail : null;

  return (
    <AppLayout title="Bulk Import Center">
      <div className="p-4 md:p-6 space-y-6 pb-8">
        {/* Section A: Upload Zone */}
        <Card>
          <CardHeader>Upload Files</CardHeader>
          <CardBody className="space-y-6">
            {/* Import Type Tabs */}
            <div className="flex flex-wrap gap-2 border-b border-neutral-200 dark:border-neutral-700">
              {Object.entries(importTypeInfo).map(([type, info]) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type as ImportJob['type'])}
                  className={clsx(
                    'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                    selectedType === type
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
                  )}
                >
                  {info.label.split(' ')[0]}
                </button>
              ))}
            </div>

            {/* Drag and Drop Zone */}
            <div className="border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg p-8 text-center hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-950 transition-colors">
              <CloudArrowUpIcon className="w-12 h-12 mx-auto text-neutral-400 dark:text-neutral-600 mb-3" />
              <p className="text-lg font-medium text-neutral-900 dark:text-white mb-1">
                Drop files here or click to browse
              </p>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
                {importTypeInfo[selectedType].label}
              </p>
              <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
                Select File
              </button>
            </div>

            {/* Expected Columns */}
            <div className="bg-neutral-50 dark:bg-neutral-900 rounded-lg p-4">
              <p className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
                Expected Columns:
              </p>
              <div className="flex flex-wrap gap-2">
                {importTypeInfo[selectedType].columns.map((col) => (
                  <span
                    key={col}
                    className="px-3 py-1 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded text-xs text-neutral-700 dark:text-neutral-300"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>

            {/* Download Template & Start Import */}
            <div className="flex gap-3">
              <button
                onClick={() => handleDownloadTemplate(selectedType)}
                className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors flex items-center gap-2"
              >
                <ArrowDownTrayIcon className="w-4 h-4" />
                Download Template
              </button>
              <button
                onClick={handleStartImport}
                className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium"
              >
                Start Import
              </button>
            </div>

            {/* Success Message */}
            <div className="bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-lg p-4">
              <p className="text-sm text-success-800 dark:text-success-200">
                <span className="font-semibold">Import queued</span> — Job #IMP-20260308-001 created
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Section B: Active & Recent Jobs */}
        <Card>
          <CardHeader className="flex items-center justify-between">
            <span>Active & Recent Import Jobs</span>
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              Last updated: {Math.round((Date.now() - lastUpdated.getTime()) / 1000)}s ago
            </span>
          </CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Job ID
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Type
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      File Name
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Status
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Records
                    </th>
                    <th className="text-center py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {mockJobs.map((job) => (
                    <tr
                      key={job.id}
                      className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                    >
                      <td className="py-3 px-4 font-mono text-xs text-primary-600 dark:text-primary-400">
                        {job.id}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2.5 py-0.5 bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 rounded text-xs font-medium">
                          {job.type.charAt(0).toUpperCase() + job.type.slice(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-neutral-900 dark:text-white">{job.fileName}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.status)}
                          <StatusBadge status={job.status} />
                        </div>
                        {job.status === 'PROCESSING' && job.progress !== undefined && (
                          <div className="mt-2 w-24 h-1.5 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500 transition-all duration-300"
                              style={{ width: `${job.progress}%` }}
                            />
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="space-y-1 text-xs">
                          <div className="font-semibold text-neutral-900 dark:text-white">
                            {job.totalRecords} total
                          </div>
                          <div className="text-success-600 dark:text-success-400">
                            {job.successCount} success
                          </div>
                          {job.failureCount > 0 && (
                            <button className="text-danger-600 dark:text-danger-400 hover:underline">
                              {job.failureCount} failures
                            </button>
                          )}
                          {job.skippedCount > 0 && (
                            <div className="text-neutral-500 dark:text-neutral-400">
                              {job.skippedCount} skipped
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => setExpandedJobId(expandedJobId === job.id ? null : job.id)}
                          className="px-3 py-1 text-xs font-medium bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors"
                        >
                          {expandedJobId === job.id ? 'Hide' : 'View'} Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>

        {/* Section C: Job Detail Panel */}
        {selectedJobDetail && (
          <Card className="bg-neutral-50 dark:bg-neutral-900">
            <CardHeader className="flex items-center justify-between border-b border-neutral-300 dark:border-neutral-600">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  Job Details: {selectedJobDetail.id}
                </h3>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                  {selectedJobDetail.type} • {selectedJobDetail.fileName}
                </p>
              </div>
              <button
                onClick={() => setExpandedJobId(null)}
                className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              >
                ✕
              </button>
            </CardHeader>

            <CardBody className="space-y-6">
              {/* Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-neutral-800 rounded-lg p-3">
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                    Started
                  </p>
                  <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                    {new Date(selectedJobDetail.startedAt).toLocaleString()}
                  </p>
                </div>
                {selectedJobDetail.completedAt && (
                  <div className="bg-white dark:bg-neutral-800 rounded-lg p-3">
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                      Completed
                    </p>
                    <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                      {new Date(selectedJobDetail.completedAt).toLocaleString()}
                    </p>
                  </div>
                )}
                {selectedJobDetail.duration && (
                  <div className="bg-white dark:bg-neutral-800 rounded-lg p-3">
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                      Duration
                    </p>
                    <p className="text-sm font-medium text-neutral-900 dark:text-white mt-1">
                      {Math.round(selectedJobDetail.duration / 60)}m {selectedJobDetail.duration % 60}s
                    </p>
                  </div>
                )}
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-neutral-900 dark:text-white">
                    {selectedJobDetail.totalRecords}
                  </p>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">Total Records</p>
                </div>
                <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-success-600 dark:text-success-400">
                    {selectedJobDetail.successCount}
                  </p>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">Success</p>
                </div>
                <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-danger-600 dark:text-danger-400">
                    {selectedJobDetail.failureCount}
                  </p>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">Failures</p>
                </div>
                <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-neutral-500 dark:text-neutral-400">
                    {selectedJobDetail.skippedCount}
                  </p>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">Skipped</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-semibold text-neutral-900 dark:text-white">Overall Progress</p>
                  <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">100%</p>
                </div>
                <div className="w-full h-2 bg-neutral-300 dark:bg-neutral-700 rounded-full overflow-hidden">
                  <div className="h-full bg-success-500 w-full" />
                </div>
              </div>

              {/* Tabs */}
              <div className="border-b border-neutral-300 dark:border-neutral-600 flex gap-4">
                {selectedJobDetail.successCount > 0 && (
                  <button
                    onClick={() => setActiveTab('success')}
                    className={clsx(
                      'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                      activeTab === 'success'
                        ? 'border-success-500 text-success-600 dark:text-success-400'
                        : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
                    )}
                  >
                    Success ({selectedJobDetail.successCount})
                  </button>
                )}
                {selectedJobDetail.failureCount > 0 && (
                  <button
                    onClick={() => setActiveTab('failures')}
                    className={clsx(
                      'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                      activeTab === 'failures'
                        ? 'border-danger-500 text-danger-600 dark:text-danger-400'
                        : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
                    )}
                  >
                    Failures ({selectedJobDetail.failureCount})
                  </button>
                )}
                {selectedJobDetail.skippedCount > 0 && (
                  <button
                    onClick={() => setActiveTab('skipped')}
                    className={clsx(
                      'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                      activeTab === 'skipped'
                        ? 'border-neutral-500 text-neutral-600 dark:text-neutral-400'
                        : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
                    )}
                  >
                    Skipped ({selectedJobDetail.skippedCount})
                  </button>
                )}
              </div>

              {/* Tab Content */}
              {activeTab === 'success' && selectedJobDetail.successCount > 0 && (
                <div className="space-y-3">
                  {selectedJobDetail.successRecords.map((record) => (
                    <div
                      key={record.rowNumber}
                      className="bg-white dark:bg-neutral-800 rounded p-3 flex justify-between items-center"
                    >
                      <div>
                        <p className="text-sm font-medium text-neutral-900 dark:text-white">
                          Row #{record.rowNumber}: {record.name}
                        </p>
                        <p className="text-xs text-neutral-600 dark:text-neutral-400">ID: {record.createdId}</p>
                      </div>
                      <CheckCircleIcon className="w-5 h-5 text-success-500 flex-shrink-0" />
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'failures' && selectedJobDetail.failureCount > 0 && (
                <div className="space-y-3">
                  {selectedJobDetail.failureRecords.map((record) => (
                    <div
                      key={record.rowNumber}
                      className="bg-white dark:bg-neutral-800 rounded p-4 border border-danger-200 dark:border-danger-800"
                    >
                      <div className="flex items-start gap-3 mb-2">
                        <XCircleIcon className="w-5 h-5 text-danger-500 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-neutral-900 dark:text-white">
                            Row #{record.rowNumber}
                          </p>
                          <p className="text-xs text-danger-600 dark:text-danger-400 mt-1">
                            {record.errorMessage}
                          </p>
                        </div>
                      </div>
                      {Object.entries(record.fieldErrors).length > 0 && (
                        <div className="mt-3 ml-8 space-y-1 bg-neutral-50 dark:bg-neutral-900 rounded p-2">
                          {Object.entries(record.fieldErrors).map(([field, error]) => (
                            <p key={field} className="text-xs text-neutral-700 dark:text-neutral-300">
                              <span className="font-medium">{field}:</span> {error}
                            </p>
                          ))}
                        </div>
                      )}
                      {Object.keys(record.originalData).length > 0 && (
                        <details className="mt-3 ml-8">
                          <summary className="text-xs font-medium text-neutral-600 dark:text-neutral-400 cursor-pointer hover:text-neutral-900 dark:hover:text-white">
                            View original data
                          </summary>
                          <div className="mt-2 p-2 bg-neutral-50 dark:bg-neutral-900 rounded text-xs space-y-1 font-mono text-neutral-700 dark:text-neutral-300">
                            {Object.entries(record.originalData).map(([key, value]) => (
                              <p key={key}>
                                <span className="font-semibold">{key}:</span> {String(value || '(empty)')}
                              </p>
                            ))}
                          </div>
                        </details>
                      )}
                    </div>
                  ))}

                  {/* Failure Actions */}
                  <div className="flex gap-3 pt-3">
                    <button
                      onClick={handleDownloadFailures}
                      className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors flex items-center gap-2 text-sm font-medium"
                    >
                      <ArrowDownTrayIcon className="w-4 h-4" />
                      Download Failures as Excel
                    </button>
                    <button
                      onClick={handleReImportFailed}
                      className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2 text-sm font-medium"
                    >
                      <ArrowPathIcon className="w-4 h-4" />
                      Re-import Failed Records
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'skipped' && selectedJobDetail.skippedCount > 0 && (
                <div className="space-y-3">
                  {selectedJobDetail.skippedRecords.map((record) => (
                    <div key={record.rowNumber} className="bg-white dark:bg-neutral-800 rounded p-3">
                      <p className="text-sm font-medium text-neutral-900 dark:text-white">
                        Row #{record.rowNumber}
                      </p>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                        Reason: {record.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Notification */}
              {selectedJobDetail.notification && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    <span className="font-semibold">Notification:</span> {selectedJobDetail.notification}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        )}
      </div>
    </AppLayout>
  );
};

BulkImportCenter.displayName = 'BulkImportCenter';

export default BulkImportCenter;
