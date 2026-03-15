import React, { useState } from 'react';
import { DataTable } from '@/components/common/DataTable';
import { SearchInput } from '@/components/common/SearchInput';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Card, CardBody } from '@/components/common/Card';
import { useApi } from '@/hooks/useApi';
import { getCandidates } from '@/api/candidates';
import { PlusIcon } from '@heroicons/react/24/outline';
import type { Candidate } from '@/types';

/* ─── Screening status enrichment (would come from /screening-feedback/records API) ─── */
const screeningEnrichment: Record<string, {
  status: 'screened' | 'shortlisted' | 'hold' | 'rejected' | 'pending' | 'not_screened';
  score: number; source: string; screener: string; date: string;
  decision_reason: string; strengths: string[]; concerns: string[];
}> = {
  'Rajesh Kumar': { status: 'screened', score: 78, source: 'application', screener: 'Alice Morgan', date: '2026-03-10', decision_reason: 'Strong Python skills, H1B transfer manageable', strengths: ['Strong Python/SQL', 'Relevant experience'], concerns: ['H1B transfer delay'] },
  'Emily Chen': { status: 'shortlisted', score: 92, source: 'application', screener: 'Alice Morgan', date: '2026-03-10', decision_reason: 'Exceptional — US Citizen, strong match', strengths: ['Exceptional Python', 'US Citizen', 'Leadership'], concerns: ['Rate above midpoint'] },
  'Marcus Johnson': { status: 'hold', score: 58, source: 'referral', screener: 'Bob Chen', date: '2026-03-11', decision_reason: 'OPT expiring — immigration risk', strengths: ['React/TS fundamentals', 'Available now'], concerns: ['OPT expiring', 'Limited experience'] },
  'Sarah Williams': { status: 'screened', score: 82, source: 'manual_import', screener: 'Alice Morgan', date: '2026-03-12', decision_reason: 'Strong frontend lead — assign to reqs', strengths: ['12 years frontend', 'Team leadership', 'US Citizen'], concerns: ['1 month notice'] },
  'David Park': { status: 'rejected', score: 45, source: 'job_board', screener: 'Bob Chen', date: '2026-03-12', decision_reason: 'Insufficient experience, resume inconsistencies', strengths: ['Available immediately'], concerns: ['Experience below req', 'Resume inconsistencies'] },
  'Priya Sharma': { status: 'pending', score: 0, source: 'application', screener: 'Alice Morgan', date: '2026-03-14', decision_reason: '', strengths: [], concerns: [] },
};

const screeningBadge = (status: string) => {
  switch (status) {
    case 'shortlisted': return 'bg-emerald-600 text-white';
    case 'screened': return 'bg-emerald-100 text-emerald-800';
    case 'hold': return 'bg-amber-100 text-amber-800';
    case 'rejected': return 'bg-red-100 text-red-800';
    case 'pending': return 'bg-orange-100 text-orange-700';
    default: return 'bg-neutral-100 text-neutral-500';
  }
};

const screeningIcon = (status: string) => {
  switch (status) {
    case 'shortlisted': return '★';
    case 'screened': return '✓';
    case 'hold': return '⏸';
    case 'rejected': return '✗';
    case 'pending': return '…';
    default: return '';
  }
};

const scoreBg = (s: number) => s >= 80 ? 'bg-emerald-100 text-emerald-800' : s >= 60 ? 'bg-blue-100 text-blue-800' : s >= 40 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';
const scoreBarColor = (s: number) => s >= 80 ? 'bg-emerald-500' : s >= 60 ? 'bg-blue-500' : s >= 40 ? 'bg-amber-500' : 'bg-red-500';

const sourceBadge = (src: string) => {
  const m: Record<string, string> = {
    application: 'bg-blue-100 text-blue-700', manual_import: 'bg-violet-100 text-violet-700',
    referral: 'bg-emerald-100 text-emerald-700', job_board: 'bg-orange-100 text-orange-700',
  };
  return m[src] || 'bg-neutral-100 text-neutral-600';
};

export const Candidates: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [screeningFilter, setScreeningFilter] = useState('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

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

  const getScreening = (row: Candidate) => {
    const name = `${row.first_name} ${row.last_name}`;
    return screeningEnrichment[name] || null;
  };

  /* Screening stats */
  const allNames = Object.keys(screeningEnrichment);
  const screenedCount = allNames.filter(n => ['screened', 'shortlisted'].includes(screeningEnrichment[n].status)).length;
  const shortlistedCount = allNames.filter(n => screeningEnrichment[n].status === 'shortlisted').length;
  const holdCount = allNames.filter(n => screeningEnrichment[n].status === 'hold').length;
  const pendingCount = allNames.filter(n => screeningEnrichment[n].status === 'pending' || screeningEnrichment[n].status === 'not_screened').length;
  const rejectedCount = allNames.filter(n => screeningEnrichment[n].status === 'rejected').length;

  const columns = [
    {
      key: 'first_name' as const,
      label: 'Name',
      sortable: true,
      render: (value: unknown, row: Candidate) => {
        const sc = getScreening(row);
        return (
          <div className="flex items-center gap-2">
            <div>
              <span className="font-medium">{row.first_name} {row.last_name}</span>
              {sc && (
                <span className={`ml-2 inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${screeningBadge(sc.status)}`}>
                  {screeningIcon(sc.status)} {sc.status === 'not_screened' ? 'Not Screened' : sc.status}
                </span>
              )}
              {!sc && (
                <span className="ml-2 inline-flex items-center text-[10px] px-1.5 py-0.5 rounded-full bg-neutral-100 text-neutral-400 font-medium">
                  No screening
                </span>
              )}
            </div>
          </div>
        );
      },
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
      label: 'Screening',
      render: (_value: unknown, row: Candidate) => {
        const sc = getScreening(row);
        if (!sc) return <span className="text-neutral-300 text-xs">—</span>;
        if (sc.status === 'not_screened') return <a href="/screening-feedback" className="text-[10px] text-violet-600 hover:underline font-medium">Screen Now</a>;
        if (sc.status === 'pending') return (
          <div className="flex items-center gap-1">
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-orange-100 text-orange-700 font-semibold">DRAFT</span>
            <a href="/screening-feedback" className="text-[10px] text-violet-600 hover:underline">Continue</a>
          </div>
        );
        return (
          <div className="flex items-center gap-1.5">
            <span className={`text-xs font-bold px-2 py-0.5 rounded ${scoreBg(sc.score)}`}>{sc.score}</span>
            <a href="/screening-feedback" className="text-[10px] text-violet-600 hover:underline">View</a>
          </div>
        );
      },
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
          <div className="flex gap-2">
            <a href="/screening-feedback" className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-medium transition-colors duration-250 text-sm">
              Screening Center
            </a>
            <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors duration-250">
              <PlusIcon className="w-5 h-5" />
              <span>Add Candidate</span>
            </button>
          </div>
        </div>

        {/* Screening Summary Bar */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 uppercase tracking-wide">Screening Status Overview</span>
            <div className="flex gap-1">
              {['all', 'shortlisted', 'screened', 'hold', 'pending', 'rejected'].map(f => (
                <button key={f} onClick={() => setScreeningFilter(f)}
                  className={`px-2.5 py-1 text-[10px] rounded-full font-medium transition-colors ${screeningFilter === f ? 'bg-violet-600 text-white' : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200'}`}>
                  {f === 'all' ? 'All' : f}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-2 h-6">
            {[
              { key: 'shortlisted', label: 'Shortlisted', count: shortlistedCount, color: 'bg-emerald-600' },
              { key: 'screened', label: 'Screened', count: screenedCount - shortlistedCount, color: 'bg-emerald-400' },
              { key: 'hold', label: 'Hold', count: holdCount, color: 'bg-amber-400' },
              { key: 'pending', label: 'Pending', count: pendingCount, color: 'bg-orange-300' },
              { key: 'rejected', label: 'Rejected', count: rejectedCount, color: 'bg-red-400' },
            ].filter(s => s.count > 0).map(s => (
              <div key={s.key} className={`${s.color} rounded flex items-center justify-center text-white text-[10px] font-semibold`} style={{ flex: s.count }}>
                {s.label} ({s.count})
              </div>
            ))}
          </div>
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
