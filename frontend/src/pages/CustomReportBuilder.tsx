import React, { useState, useCallback } from 'react';
import {
  ChartBarIcon,
  TableCellsIcon,
  PlusIcon,
  TrashIcon,
  StarIcon,
  ClockIcon,
  PlayIcon,
  ArrowDownTrayIcon,
  DocumentDuplicateIcon,
  ShareIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  AdjustmentsHorizontalIcon,
  FunnelIcon,
  ChevronRightIcon,
  ArrowPathIcon,
  BellIcon,
  PencilSquareIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  BookmarkIcon,
  Cog6ToothIcon,
  EnvelopeIcon,
  PauseIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';

// ── Types ──
type TabKey = 'builder' | 'saved' | 'schedules' | 'templates';

interface Dimension {
  key: string;
  label: string;
  category: string;
  description: string;
}

interface Metric {
  key: string;
  label: string;
  description: string;
  format: string;
}

interface SavedReport {
  id: number;
  name: string;
  description: string;
  dimensions: string[];
  metrics: string[];
  filters: Record<string, string>;
  visualization: string;
  is_favorite: boolean;
  is_shared: boolean;
  last_run_at: string | null;
  run_count: number;
  created_at: string;
}

interface Schedule {
  id: number;
  name: string;
  report_name: string;
  report_type: 'saved' | 'predefined';
  cron: string;
  frequency_label: string;
  delivery: string;
  recipients: string[];
  format: string;
  enabled: boolean;
  last_run: string | null;
  next_run: string;
  status: string;
  run_count: number;
}

// ── Config Data ──
const DIMENSIONS: Dimension[] = [
  { key: 'client', label: 'Client', category: 'Entity', description: 'Group by client organization' },
  { key: 'job', label: 'Job / Requirement', category: 'Entity', description: 'Group by job order' },
  { key: 'supplier', label: 'Supplier', category: 'Entity', description: 'Group by supplier organization' },
  { key: 'recruiter', label: 'Recruiter', category: 'Entity', description: 'Group by recruiter' },
  { key: 'department', label: 'Department', category: 'Entity', description: 'Group by department' },
  { key: 'location', label: 'Location', category: 'Geography', description: 'Group by job location' },
  { key: 'skill', label: 'Skill', category: 'Attribute', description: 'Group by primary skill' },
  { key: 'source', label: 'Source Channel', category: 'Attribute', description: 'Group by candidate source' },
  { key: 'priority', label: 'Priority', category: 'Attribute', description: 'Group by job priority' },
  { key: 'phase', label: 'Pipeline Phase', category: 'Pipeline', description: 'Group by current ATS phase' },
  { key: 'month', label: 'Month', category: 'Time', description: 'Group by calendar month' },
  { key: 'quarter', label: 'Quarter', category: 'Time', description: 'Group by calendar quarter' },
];

const METRICS: Metric[] = [
  { key: 'placements', label: 'Placements', description: 'Total placements', format: 'number' },
  { key: 'submissions', label: 'Submissions', description: 'Total submissions', format: 'number' },
  { key: 'interviews', label: 'Interviews', description: 'Interviews conducted', format: 'number' },
  { key: 'offers', label: 'Offers', description: 'Offers extended', format: 'number' },
  { key: 'fill_rate', label: 'Fill Rate', description: 'Jobs filled / total jobs', format: 'percent' },
  { key: 'avg_ttf', label: 'Avg Time-to-Fill', description: 'Average days to fill', format: 'days' },
  { key: 'avg_match_score', label: 'Avg Match Score', description: 'Average AI match score', format: 'number' },
  { key: 'conversion_rate', label: 'Conversion Rate', description: 'Applicant to placement %', format: 'percent' },
  { key: 'revenue', label: 'Revenue', description: 'Total billing revenue', format: 'currency' },
  { key: 'cost_per_hire', label: 'Cost per Hire', description: 'Average cost per placement', format: 'currency' },
  { key: 'rejection_rate', label: 'Rejection Rate', description: 'Candidates rejected %', format: 'percent' },
  { key: 'sla_adherence', label: 'SLA Adherence', description: 'SLA compliance rate', format: 'percent' },
  { key: 'quality_score', label: 'Quality Score', description: 'Submission quality rating', format: 'number' },
  { key: 'compliance_score', label: 'Compliance Score', description: 'Regulatory compliance', format: 'percent' },
  { key: 'pipeline_count', label: 'Pipeline Count', description: 'Active candidates in pipeline', format: 'number' },
  { key: 'offer_acceptance', label: 'Offer Acceptance', description: 'Offers accepted %', format: 'percent' },
];

const VISUALIZATIONS = [
  { key: 'table', label: 'Data Table', icon: TableCellsIcon },
  { key: 'bar_chart', label: 'Bar Chart', icon: ChartBarIcon },
  { key: 'line_chart', label: 'Line Chart', icon: ChartBarIcon },
  { key: 'pie_chart', label: 'Pie Chart', icon: ChartBarIcon },
  { key: 'heatmap', label: 'Heatmap', icon: TableCellsIcon },
  { key: 'stacked_bar', label: 'Stacked Bar', icon: ChartBarIcon },
  { key: 'funnel', label: 'Funnel', icon: FunnelIcon },
];

const TEMPLATES = [
  { id: 'tpl-1', name: 'Client Performance Overview', description: 'Compare all clients by placements, fill rate, and revenue', dimensions: ['client'], metrics: ['placements', 'fill_rate', 'revenue', 'avg_ttf', 'submissions'], visualization: 'table' },
  { id: 'tpl-2', name: 'Recruiter Leaderboard', description: 'Rank recruiters by conversion rate and placements', dimensions: ['recruiter'], metrics: ['placements', 'submissions', 'conversion_rate', 'avg_match_score', 'revenue'], visualization: 'bar_chart' },
  { id: 'tpl-3', name: 'Supplier Quality Matrix', description: 'Supplier performance by quality, compliance, and SLA', dimensions: ['supplier'], metrics: ['quality_score', 'compliance_score', 'sla_adherence', 'fill_rate', 'rejection_rate'], visualization: 'heatmap' },
  { id: 'tpl-4', name: 'Monthly Hiring Trend', description: 'Monthly placements, submissions, and conversion over time', dimensions: ['month'], metrics: ['placements', 'submissions', 'conversion_rate', 'avg_ttf'], visualization: 'line_chart' },
  { id: 'tpl-5', name: 'Source Attribution Analysis', description: 'Which sourcing channels deliver best candidates', dimensions: ['source'], metrics: ['submissions', 'placements', 'conversion_rate', 'avg_match_score', 'cost_per_hire'], visualization: 'bar_chart' },
  { id: 'tpl-6', name: 'Client × Supplier Performance', description: 'Cross-dimensional view of client-supplier placements', dimensions: ['client', 'supplier'], metrics: ['placements', 'fill_rate', 'avg_ttf'], visualization: 'heatmap' },
  { id: 'tpl-7', name: 'Skill Demand & Supply', description: 'Top skills by demand, supply, and fill rate', dimensions: ['skill'], metrics: ['pipeline_count', 'placements', 'fill_rate', 'avg_ttf', 'revenue'], visualization: 'stacked_bar' },
  { id: 'tpl-8', name: 'Priority-based Pipeline', description: 'Job pipeline health by priority level', dimensions: ['priority', 'phase'], metrics: ['pipeline_count', 'avg_ttf', 'conversion_rate'], visualization: 'funnel' },
];

// ── Mock Saved Reports ──
const MOCK_SAVED: SavedReport[] = [
  { id: 1, name: 'Weekly Client Summary', description: 'Placements and revenue by client - last 7 days', dimensions: ['client'], metrics: ['placements', 'revenue', 'fill_rate'], filters: { date_range: 'last_7_days' }, visualization: 'bar_chart', is_favorite: true, is_shared: true, last_run_at: '2026-03-08T14:30:00Z', run_count: 24, created_at: '2026-01-15' },
  { id: 2, name: 'Recruiter Monthly KPIs', description: 'Individual recruiter performance metrics', dimensions: ['recruiter', 'month'], metrics: ['submissions', 'placements', 'conversion_rate', 'avg_match_score'], filters: { date_range: 'last_30_days' }, visualization: 'table', is_favorite: true, is_shared: false, last_run_at: '2026-03-07T09:00:00Z', run_count: 12, created_at: '2026-02-01' },
  { id: 3, name: 'Supplier Scorecard Q1', description: 'Quality and compliance scores for all suppliers', dimensions: ['supplier'], metrics: ['quality_score', 'compliance_score', 'sla_adherence', 'fill_rate'], filters: { date_range: 'this_quarter' }, visualization: 'heatmap', is_favorite: false, is_shared: true, last_run_at: '2026-03-05T16:00:00Z', run_count: 8, created_at: '2026-01-20' },
  { id: 4, name: 'Source ROI Analysis', description: 'Cost per hire and conversion by source channel', dimensions: ['source'], metrics: ['submissions', 'placements', 'cost_per_hire', 'conversion_rate'], filters: {}, visualization: 'pie_chart', is_favorite: false, is_shared: false, last_run_at: null, run_count: 0, created_at: '2026-03-01' },
];

// ── Mock Schedules ──
const MOCK_SCHEDULES: Schedule[] = [
  { id: 1, name: 'Weekly Client Summary', report_name: 'Weekly Client Summary', report_type: 'saved', cron: '0 8 * * 1', frequency_label: 'Every Monday at 8:00 AM', delivery: 'both', recipients: ['admin@hotgigs.com', 'msp-lead@hotgigs.com'], format: 'pdf', enabled: true, last_run: '2026-03-03T08:00:00Z', next_run: '2026-03-10T08:00:00Z', status: 'success', run_count: 8 },
  { id: 2, name: 'Daily Pipeline Health', report_name: 'Pipeline Aging Report', report_type: 'predefined', cron: '0 7 * * 1-5', frequency_label: 'Weekdays at 7:00 AM', delivery: 'email', recipients: ['team@hotgigs.com'], format: 'xlsx', enabled: true, last_run: '2026-03-07T07:00:00Z', next_run: '2026-03-10T07:00:00Z', status: 'success', run_count: 42 },
  { id: 3, name: 'Monthly Executive Report', report_name: 'MSP Executive Summary', report_type: 'predefined', cron: '0 9 1 * *', frequency_label: 'First of every month at 9:00 AM', delivery: 'both', recipients: ['ceo@hotgigs.com', 'cfo@hotgigs.com', 'vp-ops@hotgigs.com'], format: 'pdf', enabled: true, last_run: '2026-03-01T09:00:00Z', next_run: '2026-04-01T09:00:00Z', status: 'success', run_count: 3 },
  { id: 4, name: 'Quarterly Supplier Review', report_name: 'Supplier Scorecard Q1', report_type: 'saved', cron: '0 10 1 1,4,7,10 *', frequency_label: 'Quarterly on 1st at 10:00 AM', delivery: 'email', recipients: ['procurement@hotgigs.com'], format: 'xlsx', enabled: false, last_run: '2026-01-01T10:00:00Z', next_run: '2026-04-01T10:00:00Z', status: 'success', run_count: 1 },
];

// ── Mock data generator for preview ──
const generateMockPreviewData = (dimensions: string[], metrics: string[]): Record<string, any>[] => {
  const dimValues: Record<string, string[]> = {
    client: ['TechCorp', 'CloudNine', 'AnalyticsPro', 'InnovateCo', 'GlobalFinance'],
    job: ['Senior Engineer', 'DevOps Lead', 'Data Scientist', 'Product Manager', 'UX Designer'],
    supplier: ['TalentForce', 'PrimeStaff', 'EliteHire', 'SwiftTalent', 'NexGen'],
    recruiter: ['Jane R.', 'John M.', 'Sarah K.', 'David C.', 'Emily P.'],
    department: ['Engineering', 'Product', 'Data Science', 'Design', 'Operations'],
    location: ['San Francisco', 'Austin', 'New York', 'Remote', 'Seattle'],
    skill: ['React', 'Python', 'AWS', 'Kubernetes', 'Data Science'],
    source: ['LinkedIn', 'Referral', 'Job Board', 'Direct', 'Agency'],
    priority: ['Urgent', 'High', 'Normal', 'Low'],
    phase: ['Sourced', 'Screening', 'Submitted', 'Interview', 'Offer', 'Placed'],
    month: ['Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026', 'Feb 2026', 'Mar 2026'],
    quarter: ['Q3 2025', 'Q4 2025', 'Q1 2026'],
  };

  const metricGenerators: Record<string, () => number> = {
    placements: () => Math.floor(Math.random() * 20) + 1,
    submissions: () => Math.floor(Math.random() * 50) + 10,
    interviews: () => Math.floor(Math.random() * 30) + 5,
    offers: () => Math.floor(Math.random() * 15) + 1,
    fill_rate: () => Math.round((Math.random() * 40 + 50) * 10) / 10,
    avg_ttf: () => Math.round((Math.random() * 25 + 10) * 10) / 10,
    avg_match_score: () => Math.round((Math.random() * 20 + 75) * 10) / 10,
    conversion_rate: () => Math.round((Math.random() * 20 + 5) * 10) / 10,
    revenue: () => Math.floor(Math.random() * 500000) + 100000,
    cost_per_hire: () => Math.floor(Math.random() * 5000) + 2000,
    rejection_rate: () => Math.round((Math.random() * 25 + 5) * 10) / 10,
    sla_adherence: () => Math.round((Math.random() * 15 + 85) * 10) / 10,
    quality_score: () => Math.round((Math.random() * 2 + 3) * 10) / 10,
    compliance_score: () => Math.round((Math.random() * 10 + 88) * 10) / 10,
    pipeline_count: () => Math.floor(Math.random() * 40) + 5,
    offer_acceptance: () => Math.round((Math.random() * 30 + 60) * 10) / 10,
  };

  const primaryDim = dimensions[0] || 'client';
  const values = dimValues[primaryDim] || ['Item 1', 'Item 2', 'Item 3'];

  return values.map(val => {
    const row: Record<string, any> = { [primaryDim]: val };
    if (dimensions[1]) {
      row[dimensions[1]] = (dimValues[dimensions[1]] || ['A'])[Math.floor(Math.random() * (dimValues[dimensions[1]]?.length || 1))];
    }
    metrics.forEach(m => {
      row[m] = (metricGenerators[m] || (() => Math.floor(Math.random() * 100)))();
    });
    return row;
  });
};

const formatMetricValue = (key: string, value: number): string => {
  const m = METRICS.find(mt => mt.key === key);
  if (!m) return String(value);
  switch (m.format) {
    case 'percent': return value.toFixed(1) + '%';
    case 'currency': return value >= 1000000 ? '$' + (value / 1000000).toFixed(1) + 'M' : '$' + (value / 1000).toFixed(0) + 'K';
    case 'days': return value.toFixed(1) + 'd';
    default: return String(typeof value === 'number' ? (value % 1 === 0 ? value : value.toFixed(1)) : value);
  }
};

// ══════════════════════════════════════════════
// BUILDER TAB
// ══════════════════════════════════════════════
const BuilderTab: React.FC = () => {
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>(['client']);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['placements', 'fill_rate', 'revenue']);
  const [selectedViz, setSelectedViz] = useState('table');
  const [reportName, setReportName] = useState('');
  const [reportDesc, setReportDesc] = useState('');
  const [dateRange, setDateRange] = useState('last_90_days');
  const [previewData, setPreviewData] = useState<Record<string, any>[] | null>(null);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  const toggleDimension = (key: string) => {
    setSelectedDimensions(prev => prev.includes(key) ? prev.filter(d => d !== key) : [...prev, key].slice(0, 3));
    setPreviewData(null);
  };

  const toggleMetric = (key: string) => {
    setSelectedMetrics(prev => prev.includes(key) ? prev.filter(m => m !== key) : [...prev, key].slice(0, 8));
    setPreviewData(null);
  };

  const runPreview = () => {
    if (selectedDimensions.length === 0 || selectedMetrics.length === 0) return;
    setPreviewData(generateMockPreviewData(selectedDimensions, selectedMetrics));
  };

  const dimCategories = [...new Set(DIMENSIONS.map(d => d.category))];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Panel — Dimensions & Metrics */}
      <div className="lg:col-span-1 space-y-4">
        {/* Dimensions */}
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h3 className="text-sm font-semibold text-neutral-700 mb-3 flex items-center gap-2">
            <AdjustmentsHorizontalIcon className="w-4 h-4" /> Dimensions <span className="text-[10px] text-neutral-400">(max 3)</span>
          </h3>
          {dimCategories.map(cat => (
            <div key={cat} className="mb-3">
              <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider mb-1.5">{cat}</p>
              <div className="flex flex-wrap gap-1.5">
                {DIMENSIONS.filter(d => d.category === cat).map(dim => (
                  <button key={dim.key} onClick={() => toggleDimension(dim.key)} title={dim.description} className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-all ${selectedDimensions.includes(dim.key) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-neutral-600 border-neutral-200 hover:border-blue-300'}`}>
                    {dim.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Metrics */}
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h3 className="text-sm font-semibold text-neutral-700 mb-3 flex items-center gap-2">
            <ChartBarIcon className="w-4 h-4" /> Metrics <span className="text-[10px] text-neutral-400">(max 8)</span>
          </h3>
          <div className="space-y-1">
            {METRICS.map(m => (
              <button key={m.key} onClick={() => toggleMetric(m.key)} title={m.description} className={`w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-xs transition-all ${selectedMetrics.includes(m.key) ? 'bg-emerald-50 text-emerald-700 border border-emerald-300' : 'text-neutral-600 hover:bg-neutral-50'}`}>
                <span>{m.label}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${selectedMetrics.includes(m.key) ? 'bg-emerald-200' : 'bg-neutral-100 text-neutral-400'}`}>{m.format}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h3 className="text-sm font-semibold text-neutral-700 mb-3 flex items-center gap-2">
            <FunnelIcon className="w-4 h-4" /> Filters
          </h3>
          <div className="space-y-2">
            <div>
              <label className="text-[10px] text-neutral-500 font-medium">Date Range</label>
              <select value={dateRange} onChange={e => setDateRange(e.target.value)} className="w-full mt-1 px-3 py-1.5 border border-neutral-200 rounded-lg text-xs">
                <option value="last_7_days">Last 7 Days</option>
                <option value="last_30_days">Last 30 Days</option>
                <option value="last_90_days">Last 90 Days</option>
                <option value="this_quarter">This Quarter</option>
                <option value="this_year">This Year</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
          </div>
        </div>

        {/* Visualization */}
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h3 className="text-sm font-semibold text-neutral-700 mb-3 flex items-center gap-2">
            <EyeIcon className="w-4 h-4" /> Visualization
          </h3>
          <div className="grid grid-cols-2 gap-1.5">
            {VISUALIZATIONS.map(v => {
              const VizIcon = v.icon;
              return (
                <button key={v.key} onClick={() => setSelectedViz(v.key)} className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-medium border transition-all ${selectedViz === v.key ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-neutral-600 border-neutral-200 hover:border-indigo-300'}`}>
                  <VizIcon className="w-3.5 h-3.5" /> {v.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Right Panel — Preview & Actions */}
      <div className="lg:col-span-2 space-y-4">
        {/* Action Bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button onClick={runPreview} disabled={selectedDimensions.length === 0 || selectedMetrics.length === 0} className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
              <PlayIcon className="w-4 h-4" /> Run Preview
            </button>
            <button onClick={() => setShowSaveModal(true)} className="inline-flex items-center gap-1.5 px-4 py-2 bg-white text-neutral-700 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50">
              <BookmarkIcon className="w-4 h-4" /> Save Report
            </button>
            <button onClick={() => setShowScheduleModal(true)} className="inline-flex items-center gap-1.5 px-4 py-2 bg-white text-neutral-700 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50">
              <ClockIcon className="w-4 h-4" /> Schedule
            </button>
          </div>
          <div className="flex items-center gap-2">
            <button className="inline-flex items-center gap-1 px-3 py-1.5 text-xs text-neutral-500 hover:text-neutral-700 border border-neutral-200 rounded-lg">
              <ArrowDownTrayIcon className="w-3.5 h-3.5" /> Export PDF
            </button>
            <button className="inline-flex items-center gap-1 px-3 py-1.5 text-xs text-neutral-500 hover:text-neutral-700 border border-neutral-200 rounded-lg">
              <ArrowDownTrayIcon className="w-3.5 h-3.5" /> Export XLSX
            </button>
          </div>
        </div>

        {/* Config Summary */}
        <div className="bg-neutral-50 rounded-xl border border-neutral-200 p-4">
          <div className="flex items-center gap-6 text-xs">
            <div>
              <span className="text-neutral-400">Dimensions:</span>{' '}
              {selectedDimensions.map(d => <span key={d} className="inline-flex px-2 py-0.5 bg-blue-100 text-blue-700 rounded mx-0.5 font-medium">{DIMENSIONS.find(dim => dim.key === d)?.label}</span>)}
              {selectedDimensions.length === 0 && <span className="text-neutral-400 italic">None selected</span>}
            </div>
            <div>
              <span className="text-neutral-400">Metrics:</span>{' '}
              {selectedMetrics.length > 0 ? <span className="text-neutral-700 font-medium">{selectedMetrics.length} selected</span> : <span className="text-neutral-400 italic">None</span>}
            </div>
            <div>
              <span className="text-neutral-400">Viz:</span>{' '}
              <span className="text-neutral-700 font-medium capitalize">{selectedViz.replace('_', ' ')}</span>
            </div>
          </div>
        </div>

        {/* Preview Area */}
        {!previewData ? (
          <div className="bg-white rounded-xl border border-dashed border-neutral-300 p-16 text-center">
            <ChartBarIcon className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
            <p className="text-neutral-500 text-sm">Select dimensions and metrics, then click <strong>Run Preview</strong></p>
            <p className="text-neutral-400 text-xs mt-1">Choose up to 3 dimensions and 8 metrics to build your custom report</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-neutral-200 bg-neutral-50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="w-4 h-4 text-emerald-500" />
                <span className="text-sm font-medium text-neutral-700">Preview Results</span>
                <span className="text-xs text-neutral-400">{previewData.length} rows</span>
              </div>
              <button onClick={runPreview} className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1">
                <ArrowPathIcon className="w-3 h-3" /> Refresh
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-neutral-50 border-b border-neutral-200">
                    {selectedDimensions.map(d => (
                      <th key={d} className="text-left px-3 py-2 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{DIMENSIONS.find(dim => dim.key === d)?.label}</th>
                    ))}
                    {selectedMetrics.map(m => (
                      <th key={m} className="text-right px-3 py-2 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{METRICS.find(mt => mt.key === m)?.label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {previewData.map((row, i) => (
                    <tr key={i} className="hover:bg-blue-50/30">
                      {selectedDimensions.map(d => (
                        <td key={d} className="px-3 py-2 text-sm font-medium text-neutral-800">{row[d] || '-'}</td>
                      ))}
                      {selectedMetrics.map(m => (
                        <td key={m} className="px-3 py-2 text-sm text-right text-neutral-700">{formatMetricValue(m, row[m])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Save Modal */}
        {showSaveModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={() => setShowSaveModal(false)}>
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
              <h3 className="text-lg font-bold text-neutral-900 mb-4">Save Report</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-neutral-500">Report Name</label>
                  <input type="text" value={reportName} onChange={e => setReportName(e.target.value)} placeholder="e.g., Weekly Client Summary" className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="text-xs font-medium text-neutral-500">Description</label>
                  <textarea value={reportDesc} onChange={e => setReportDesc(e.target.value)} placeholder="Brief description of this report..." className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm h-20 resize-none" />
                </div>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 text-sm text-neutral-600">
                    <input type="checkbox" className="rounded" /> Share with organization
                  </label>
                </div>
              </div>
              <div className="flex items-center justify-end gap-2 mt-6">
                <button onClick={() => setShowSaveModal(false)} className="px-4 py-2 text-sm text-neutral-600 hover:bg-neutral-100 rounded-lg">Cancel</button>
                <button onClick={() => { setShowSaveModal(false); }} className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700">Save Report</button>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Modal */}
        {showScheduleModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={() => setShowScheduleModal(false)}>
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6" onClick={e => e.stopPropagation()}>
              <h3 className="text-lg font-bold text-neutral-900 mb-4">Schedule Report</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-neutral-500">Schedule Name</label>
                  <input type="text" placeholder="e.g., Weekly Client Summary" className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-neutral-500">Frequency</label>
                    <select className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm">
                      <option>Daily at 8:00 AM</option>
                      <option>Weekdays at 8:00 AM</option>
                      <option>Weekly on Monday</option>
                      <option>Bi-weekly on Monday</option>
                      <option>Monthly on 1st</option>
                      <option>Quarterly</option>
                      <option>Custom Cron</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-neutral-500">Export Format</label>
                    <select className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm">
                      <option value="pdf">PDF</option>
                      <option value="xlsx">Excel (XLSX)</option>
                      <option value="csv">CSV</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-neutral-500">Delivery Method</label>
                  <select className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm">
                    <option value="both">Email + In-App Notification</option>
                    <option value="email">Email Only</option>
                    <option value="in_app">In-App Notification Only</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-neutral-500">Recipients (comma-separated emails)</label>
                  <input type="text" placeholder="admin@company.com, manager@company.com" className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm" />
                </div>
              </div>
              <div className="flex items-center justify-end gap-2 mt-6">
                <button onClick={() => setShowScheduleModal(false)} className="px-4 py-2 text-sm text-neutral-600 hover:bg-neutral-100 rounded-lg">Cancel</button>
                <button onClick={() => { setShowScheduleModal(false); }} className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700">Create Schedule</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ══════════════════════════════════════════════
// SAVED REPORTS TAB
// ══════════════════════════════════════════════
const SavedReportsTab: React.FC = () => {
  const [reports, setReports] = useState(MOCK_SAVED);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'favorites' | 'shared'>('all');

  const filtered = reports.filter(r => {
    const matchesSearch = r.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || (filter === 'favorites' && r.is_favorite) || (filter === 'shared' && r.is_shared);
    return matchesSearch && matchesFilter;
  });

  const toggleFavorite = (id: number) => setReports(prev => prev.map(r => r.id === id ? { ...r, is_favorite: !r.is_favorite } : r));

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search saved reports..." className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg text-sm" />
        </div>
        <div className="flex items-center gap-1 bg-neutral-100 rounded-lg p-0.5">
          {(['all', 'favorites', 'shared'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)} className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize ${filter === f ? 'bg-white shadow-sm text-neutral-800' : 'text-neutral-500'}`}>{f}</button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(report => (
          <div key={report.id} className="bg-white rounded-xl border border-neutral-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-neutral-900">{report.name}</h4>
                  <button onClick={() => toggleFavorite(report.id)}>
                    {report.is_favorite ? <StarSolidIcon className="w-4 h-4 text-amber-400" /> : <StarIcon className="w-4 h-4 text-neutral-300 hover:text-amber-400" />}
                  </button>
                  {report.is_shared && <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 text-[10px] font-medium">Shared</span>}
                </div>
                <p className="text-xs text-neutral-500 mt-0.5">{report.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap mb-3">
              {report.dimensions.map(d => <span key={d} className="px-2 py-0.5 rounded bg-blue-50 text-blue-600 text-[10px] font-medium">{DIMENSIONS.find(dim => dim.key === d)?.label || d}</span>)}
              <span className="text-neutral-300">|</span>
              {report.metrics.slice(0, 3).map(m => <span key={m} className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-600 text-[10px] font-medium">{METRICS.find(mt => mt.key === m)?.label || m}</span>)}
              {report.metrics.length > 3 && <span className="text-[10px] text-neutral-400">+{report.metrics.length - 3}</span>}
            </div>
            <div className="flex items-center justify-between text-xs text-neutral-500">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1"><PlayIcon className="w-3 h-3" />Run {report.run_count}x</span>
                {report.last_run_at && <span className="flex items-center gap-1"><ClockIcon className="w-3 h-3" />Last: {new Date(report.last_run_at).toLocaleDateString()}</span>}
              </div>
              <div className="flex items-center gap-1">
                <button className="p-1.5 rounded hover:bg-blue-50 text-blue-600" title="Run Now"><PlayIcon className="w-3.5 h-3.5" /></button>
                <button className="p-1.5 rounded hover:bg-neutral-100" title="Schedule"><ClockIcon className="w-3.5 h-3.5" /></button>
                <button className="p-1.5 rounded hover:bg-neutral-100" title="Duplicate"><DocumentDuplicateIcon className="w-3.5 h-3.5" /></button>
                <button className="p-1.5 rounded hover:bg-neutral-100" title="Export"><ArrowDownTrayIcon className="w-3.5 h-3.5" /></button>
                <button className="p-1.5 rounded hover:bg-red-50 text-red-500" title="Delete"><TrashIcon className="w-3.5 h-3.5" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ══════════════════════════════════════════════
// SCHEDULES TAB
// ══════════════════════════════════════════════
const SchedulesTab: React.FC = () => {
  const [schedules, setSchedules] = useState(MOCK_SCHEDULES);

  const toggleEnabled = (id: number) => setSchedules(prev => prev.map(s => s.id === id ? { ...s, enabled: !s.enabled } : s));

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-neutral-50 border-b border-neutral-200">
              {['Schedule', 'Report', 'Frequency', 'Delivery', 'Format', 'Last Run', 'Next Run', 'Status', 'Actions'].map(h => (
                <th key={h} className="text-left px-3 py-2.5 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {schedules.map(s => (
              <tr key={s.id} className={`hover:bg-blue-50/30 ${!s.enabled ? 'opacity-50' : ''}`}>
                <td className="px-3 py-2.5">
                  <p className="text-sm font-medium text-neutral-900">{s.name}</p>
                  <p className="text-[10px] text-neutral-500">{s.run_count} runs</p>
                </td>
                <td className="px-3 py-2.5">
                  <p className="text-xs text-neutral-700">{s.report_name}</p>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${s.report_type === 'saved' ? 'bg-blue-50 text-blue-600' : 'bg-purple-50 text-purple-600'}`}>{s.report_type}</span>
                </td>
                <td className="px-3 py-2.5 text-xs text-neutral-600">{s.frequency_label}</td>
                <td className="px-3 py-2.5">
                  <span className="flex items-center gap-1 text-xs text-neutral-600">
                    {s.delivery === 'email' || s.delivery === 'both' ? <EnvelopeIcon className="w-3 h-3" /> : null}
                    {s.delivery === 'in_app' || s.delivery === 'both' ? <BellIcon className="w-3 h-3" /> : null}
                    <span className="capitalize">{s.delivery}</span>
                  </span>
                  <p className="text-[10px] text-neutral-400">{s.recipients.length} recipient{s.recipients.length !== 1 ? 's' : ''}</p>
                </td>
                <td className="px-3 py-2.5 text-xs text-neutral-600 uppercase">{s.format}</td>
                <td className="px-3 py-2.5 text-xs text-neutral-600">{s.last_run ? new Date(s.last_run).toLocaleDateString() : '-'}</td>
                <td className="px-3 py-2.5 text-xs text-neutral-600">{new Date(s.next_run).toLocaleDateString()}</td>
                <td className="px-3 py-2.5">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${s.status === 'success' ? 'bg-emerald-50 text-emerald-600' : s.status === 'failed' ? 'bg-red-50 text-red-600' : 'bg-neutral-100 text-neutral-600'}`}>
                    {s.status === 'success' ? <CheckCircleIcon className="w-3 h-3" /> : <XCircleIcon className="w-3 h-3" />}
                    {s.status}
                  </span>
                </td>
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-1">
                    <button onClick={() => toggleEnabled(s.id)} className={`p-1 rounded ${s.enabled ? 'hover:bg-amber-50 text-amber-600' : 'hover:bg-emerald-50 text-emerald-600'}`} title={s.enabled ? 'Pause' : 'Resume'}>
                      {s.enabled ? <PauseIcon className="w-3.5 h-3.5" /> : <PlayIcon className="w-3.5 h-3.5" />}
                    </button>
                    <button className="p-1 rounded hover:bg-blue-50 text-blue-600" title="Run Now"><PlayIcon className="w-3.5 h-3.5" /></button>
                    <button className="p-1 rounded hover:bg-neutral-100" title="Edit"><PencilSquareIcon className="w-3.5 h-3.5" /></button>
                    <button className="p-1 rounded hover:bg-red-50 text-red-500" title="Delete"><TrashIcon className="w-3.5 h-3.5" /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ══════════════════════════════════════════════
// TEMPLATES TAB
// ══════════════════════════════════════════════
const TemplatesTab: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {TEMPLATES.map(tpl => (
      <div key={tpl.id} className="bg-white rounded-xl border border-neutral-200 p-4 hover:shadow-md transition-shadow">
        <h4 className="text-sm font-bold text-neutral-900 mb-1">{tpl.name}</h4>
        <p className="text-xs text-neutral-500 mb-3">{tpl.description}</p>
        <div className="flex items-center gap-1.5 flex-wrap mb-3">
          {tpl.dimensions.map(d => <span key={d} className="px-2 py-0.5 rounded bg-blue-50 text-blue-600 text-[10px] font-medium">{DIMENSIONS.find(dim => dim.key === d)?.label || d}</span>)}
          <span className="text-neutral-300">|</span>
          <span className="text-[10px] text-neutral-500">{tpl.metrics.length} metrics</span>
          <span className="text-neutral-300">|</span>
          <span className="text-[10px] text-neutral-500 capitalize">{tpl.visualization.replace('_', ' ')}</span>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700">
            <PlusIcon className="w-3.5 h-3.5" /> Use Template
          </button>
          <button className="inline-flex items-center gap-1 px-3 py-1.5 border border-neutral-200 rounded-lg text-xs text-neutral-600 hover:bg-neutral-50">
            <EyeIcon className="w-3.5 h-3.5" /> Preview
          </button>
        </div>
      </div>
    ))}
  </div>
);

// ══════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════
export const CustomReportBuilder: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('builder');

  const tabs: { key: TabKey; label: string; icon: React.ForwardRefExoticComponent<any>; count?: number }[] = [
    { key: 'builder', label: 'Report Builder', icon: AdjustmentsHorizontalIcon },
    { key: 'saved', label: 'Saved Reports', icon: BookmarkIcon, count: MOCK_SAVED.length },
    { key: 'schedules', label: 'Schedules', icon: ClockIcon, count: MOCK_SCHEDULES.length },
    { key: 'templates', label: 'Templates', icon: DocumentDuplicateIcon, count: TEMPLATES.length },
  ];

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Custom Report Builder</h1>
          <p className="text-sm text-neutral-500 mt-1">Build, save, schedule, and export custom analytics reports</p>
        </div>
        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-100 text-purple-700 text-xs font-medium">
          <Cog6ToothIcon className="w-3.5 h-3.5" /> Admin & MSP Admin Only
        </span>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-neutral-100 rounded-lg p-1 mb-6 w-fit">
        {tabs.map(tab => {
          const TabIcon = tab.icon;
          return (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)} className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === tab.key ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'}`}>
              <TabIcon className="w-4 h-4" /> {tab.label}
              {tab.count !== undefined && <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${activeTab === tab.key ? 'bg-blue-100 text-blue-700' : 'bg-neutral-200 text-neutral-500'}`}>{tab.count}</span>}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'builder' && <BuilderTab />}
      {activeTab === 'saved' && <SavedReportsTab />}
      {activeTab === 'schedules' && <SchedulesTab />}
      {activeTab === 'templates' && <TemplatesTab />}
    </div>
  );
};
