import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import {
  ArrowDownTrayIcon,
  DocumentTextIcon,
  UserGroupIcon,
  BriefcaseIcon,
  DocumentArrowDownIcon,
  DocumentCheckIcon,
  CalendarIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface ExportType {
  id: string;
  icon: React.ReactNode;
  name: string;
  recordCount: number;
  lastExportDate?: string;
}

interface ExportRecord {
  id: string;
  filename: string;
  type: string;
  format: 'CSV' | 'JSON' | 'Excel';
  recordCount: number;
  fileSize: string;
  date: string;
  downloadUrl: string;
}

const exportTypes: ExportType[] = [
  {
    id: 'candidates',
    icon: <UserGroupIcon className="w-8 h-8" />,
    name: 'Candidates',
    recordCount: 1250,
    lastExportDate: '2026-03-07',
  },
  {
    id: 'requirements',
    icon: <DocumentTextIcon className="w-8 h-8" />,
    name: 'Requirements',
    recordCount: 342,
    lastExportDate: '2026-03-06',
  },
  {
    id: 'placements',
    icon: <BriefcaseIcon className="w-8 h-8" />,
    name: 'Placements',
    recordCount: 187,
    lastExportDate: '2026-03-07',
  },
  {
    id: 'match_results',
    icon: <DocumentCheckIcon className="w-8 h-8" />,
    name: 'Match Results',
    recordCount: 2340,
    lastExportDate: '2026-03-05',
  },
  {
    id: 'submissions',
    icon: <DocumentArrowDownIcon className="w-8 h-8" />,
    name: 'Submissions',
    recordCount: 598,
    lastExportDate: '2026-03-08',
  },
];

const filterOptions: Record<string, string[]> = {
  candidates: ['Status', 'Skills', 'Experience Level', 'Location', 'Availability'],
  requirements: ['Status', 'Client', 'Skills Required', 'Rate Range', 'Duration'],
  placements: ['Status', 'Client', 'Start Date', 'Candidate', 'Rate'],
  match_results: ['Score Range', 'Match Type', 'Date Range', 'Client'],
  submissions: ['Status', 'Requirement', 'Candidate', 'Date Range', 'Submitter'],
};

const mockExports: ExportRecord[] = [
  {
    id: 1,
    filename: 'candidates_export_20260308.csv',
    type: 'Candidates',
    format: 'CSV',
    recordCount: 1250,
    fileSize: '4.2 MB',
    date: '2026-03-08 10:35 AM',
    downloadUrl: '#',
  },
  {
    id: 2,
    filename: 'requirements_export_20260308.xlsx',
    type: 'Requirements',
    format: 'Excel',
    recordCount: 342,
    fileSize: '1.8 MB',
    date: '2026-03-08 09:12 AM',
    downloadUrl: '#',
  },
  {
    id: 3,
    filename: 'match_results_20260307.json',
    type: 'Match Results',
    format: 'JSON',
    recordCount: 2340,
    fileSize: '12.5 MB',
    date: '2026-03-07 03:45 PM',
    downloadUrl: '#',
  },
  {
    id: 4,
    filename: 'placements_march_2026.csv',
    type: 'Placements',
    format: 'CSV',
    recordCount: 187,
    fileSize: '892 KB',
    date: '2026-03-07 02:20 PM',
    downloadUrl: '#',
  },
  {
    id: 5,
    filename: 'submissions_bulk_20260306.xlsx',
    type: 'Submissions',
    format: 'Excel',
    recordCount: 598,
    fileSize: '3.1 MB',
    date: '2026-03-06 11:55 AM',
    downloadUrl: '#',
  },
];

export const ExportCenter: React.FC = () => {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<'CSV' | 'JSON' | 'Excel'>('CSV');
  const [showExportPanel, setShowExportPanel] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const handleExportCardClick = (typeId: string) => {
    setSelectedType(typeId);
    setShowExportPanel(true);
    setExportMessage(null);
  };

  const handleExportNow = () => {
    const selectedTypeObj = exportTypes.find(t => t.id === selectedType);
    if (selectedTypeObj) {
      const filename = `${selectedType}_export_${new Date().toISOString().split('T')[0]}.${selectedFormat === 'CSV' ? 'csv' : selectedFormat === 'JSON' ? 'json' : 'xlsx'}`;
      const recordCount = selectedTypeObj.recordCount;
      setExportMessage(`Generating export... Download ready: ${filename} (${recordCount} records)`);
      setTimeout(() => {
        setShowExportPanel(false);
        setSelectedType(null);
      }, 2000);
    }
  };

  return (
    <AppLayout title="Export Center">
      <div className="p-4 md:p-6 space-y-6 pb-8">
        {/* Export Type Cards */}
        <div>
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
            Select Data to Export
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {exportTypes.map((type) => (
              <Card
                key={type.id}
                hoverable
                onClick={() => handleExportCardClick(type.id)}
                className="cursor-pointer"
              >
                <CardBody className="flex flex-col items-center text-center">
                  <div className="text-primary-500 mb-3">{type.icon}</div>
                  <h3 className="font-semibold text-neutral-900 dark:text-white mb-2">
                    {type.name}
                  </h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3">
                    {type.recordCount.toLocaleString()} records
                  </p>
                  {type.lastExportDate && (
                    <p className="text-xs text-neutral-500 dark:text-neutral-500">
                      Last: {type.lastExportDate}
                    </p>
                  )}
                </CardBody>
              </Card>
            ))}
          </div>
        </div>

        {/* Export Config Panel */}
        {showExportPanel && selectedType && (
          <Card className="bg-neutral-50 dark:bg-neutral-900 border-2 border-primary-200 dark:border-primary-800">
            <CardHeader className="flex items-center justify-between">
              <span className="font-semibold text-neutral-900 dark:text-white">
                Configure Export: {exportTypes.find(t => t.id === selectedType)?.name}
              </span>
              <button
                onClick={() => setShowExportPanel(false)}
                className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              >
                ✕
              </button>
            </CardHeader>

            <CardBody className="space-y-6">
              {/* Format Selector */}
              <div>
                <label className="block text-sm font-semibold text-neutral-900 dark:text-white mb-3">
                  Export Format
                </label>
                <div className="flex gap-3">
                  {['CSV', 'JSON', 'Excel'].map((format) => (
                    <button
                      key={format}
                      onClick={() => setSelectedFormat(format as 'CSV' | 'JSON' | 'Excel')}
                      className={clsx(
                        'px-4 py-2 rounded-lg font-medium transition-all',
                        selectedFormat === format
                          ? 'bg-primary-500 text-white'
                          : 'bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 hover:border-primary-400'
                      )}
                    >
                      {format}
                    </button>
                  ))}
                </div>
              </div>

              {/* Filters */}
              <div>
                <label className="block text-sm font-semibold text-neutral-900 dark:text-white mb-3">
                  Apply Filters (optional)
                </label>
                <div className="space-y-3">
                  {filterOptions[selectedType]?.map((filter) => (
                    <div key={filter} className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id={filter}
                        className="w-4 h-4 rounded border-neutral-300 dark:border-neutral-600 text-primary-500 focus:ring-primary-500"
                      />
                      <label
                        htmlFor={filter}
                        className="text-sm text-neutral-700 dark:text-neutral-300 cursor-pointer flex-1"
                      >
                        {filter}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Date Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-900 dark:text-white mb-2">
                    From Date
                  </label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-900 dark:text-white mb-2">
                    To Date
                  </label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-neutral-300 dark:border-neutral-600">
                <button
                  onClick={() => setShowExportPanel(false)}
                  className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleExportNow}
                  className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium flex items-center gap-2 ml-auto"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  Export Now
                </button>
              </div>

              {/* Success Message */}
              {exportMessage && (
                <div className="bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-lg p-4">
                  <p className="text-sm text-success-800 dark:text-success-200">
                    {exportMessage}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        )}

        {/* Export History */}
        <Card>
          <CardHeader>Export History</CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Filename
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Type
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Format
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Records
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Size
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Date
                    </th>
                    <th className="text-center py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {mockExports.map((record) => (
                    <tr
                      key={record.id}
                      className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                    >
                      <td className="py-3 px-4 font-mono text-xs text-neutral-900 dark:text-white">
                        {record.filename}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2.5 py-0.5 bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 rounded text-xs font-medium">
                          {record.type}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={clsx(
                          'px-2.5 py-0.5 rounded text-xs font-medium',
                          record.format === 'CSV' && 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300',
                          record.format === 'JSON' && 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300',
                          record.format === 'Excel' && 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300',
                        )}>
                          {record.format}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-medium text-neutral-900 dark:text-white">
                        {record.recordCount.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-neutral-600 dark:text-neutral-400">
                        {record.fileSize}
                      </td>
                      <td className="py-3 px-4 text-neutral-600 dark:text-neutral-400 flex items-center gap-2">
                        <CalendarIcon className="w-4 h-4 flex-shrink-0" />
                        {record.date}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <a
                          href={record.downloadUrl}
                          className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors"
                        >
                          <ArrowDownTrayIcon className="w-3 h-3" />
                          Download
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      </div>
    </AppLayout>
  );
};

ExportCenter.displayName = 'ExportCenter';

export default ExportCenter;
