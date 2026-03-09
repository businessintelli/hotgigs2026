import React, { useState, useEffect, useCallback } from 'react';
import {
  BeakerIcon,
  PlayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  BoltIcon,
  CommandLineIcon,
  DocumentMagnifyingGlassIcon,
  ServerIcon,
  ComputerDesktopIcon,
  ArrowTrendingUpIcon,
  InformationCircleIcon,
  FunnelIcon,
  WrenchScrewdriverIcon,
} from '@heroicons/react/24/outline';

// ── Types ──
interface TestResult {
  test_id: string;
  category: string;
  name: string;
  status: 'passed' | 'failed' | 'warning' | 'skipped' | 'error';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
  details?: string;
  duration_ms?: number;
}

interface TestReport {
  report_id: string;
  run_type: string;
  started_at: string;
  completed_at: string;
  duration_seconds: number;
  total_tests: number;
  passed: number;
  failed: number;
  warnings: number;
  skipped: number;
  errors: number;
  pass_rate: number;
  summary: {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
    errors: number;
    pass_rate: number;
    health_score: number;
  };
  results_by_category: Record<string, TestResult[]>;
  recommendations: Recommendation[];
}

interface Recommendation {
  test_id: string;
  severity: string;
  category: string;
  title: string;
  description: string;
  fix_suggestion: string;
}

interface HealthData {
  overall_health: number;
  status: string;
  components: {
    name: string;
    health: number;
    status: string;
    last_checked: string;
  }[];
  trends: { date: string; score: number }[];
}

interface CoverageData {
  api_coverage: number;
  frontend_coverage: number;
  model_coverage: number;
  overall_coverage: number;
  uncovered_areas: { area: string; type: string; priority: string }[];
}

// ── Constants ──
const API = '/api/v1/test-agent';

const RUN_TYPES = [
  { id: 'full', label: 'Full Suite', icon: BeakerIcon, desc: 'All tests — API, frontend, models, routes' },
  { id: 'quick_smoke', label: 'Quick Smoke', icon: BoltIcon, desc: 'Fast health check in ~30s' },
  { id: 'api_only', label: 'API Only', icon: ServerIcon, desc: 'Validate all API endpoints' },
  { id: 'frontend_only', label: 'Frontend Only', icon: ComputerDesktopIcon, desc: 'Validate React pages + build' },
];

const STATUS_CONFIG: Record<string, { color: string; bg: string; icon: any }> = {
  passed: { color: 'text-emerald-700', bg: 'bg-emerald-50', icon: CheckCircleIcon },
  failed: { color: 'text-red-700', bg: 'bg-red-50', icon: XCircleIcon },
  warning: { color: 'text-amber-700', bg: 'bg-amber-50', icon: ExclamationTriangleIcon },
  skipped: { color: 'text-gray-500', bg: 'bg-gray-50', icon: InformationCircleIcon },
  error: { color: 'text-red-800', bg: 'bg-red-100', icon: XCircleIcon },
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-blue-100 text-blue-800',
  info: 'bg-gray-100 text-gray-600',
};

const CATEGORY_ICONS: Record<string, any> = {
  api_endpoints: ServerIcon,
  frontend_pages: ComputerDesktopIcon,
  frontend_build: CommandLineIcon,
  models_schemas: DocumentMagnifyingGlassIcon,
  route_consistency: ArrowPathIcon,
  dependencies: WrenchScrewdriverIcon,
};

// ── Mock Data Generator ──
function generateMockReport(): TestReport {
  const categories = ['api_endpoints', 'frontend_pages', 'frontend_build', 'models_schemas', 'route_consistency', 'dependencies'];
  const resultsByCategory: Record<string, TestResult[]> = {};
  let totalPassed = 0, totalFailed = 0, totalWarnings = 0;

  categories.forEach(cat => {
    const count = cat === 'api_endpoints' ? 180 : cat === 'frontend_pages' ? 42 : cat === 'models_schemas' ? 108 : 30;
    const results: TestResult[] = [];
    for (let i = 0; i < count; i++) {
      const rand = Math.random();
      const status = rand < 0.90 ? 'passed' : rand < 0.93 ? 'warning' : rand < 0.97 ? 'warning' : 'failed';
      if (status === 'passed') totalPassed++;
      else if (status === 'failed') totalFailed++;
      else totalWarnings++;
      results.push({
        test_id: `${cat}_${i}`,
        category: cat,
        name: `${cat.replace('_', ' ')} test #${i + 1}`,
        status,
        severity: status === 'failed' ? 'high' : status === 'warning' ? 'medium' : 'low',
        message: status === 'passed' ? 'OK' : status === 'warning' ? 'Minor issue detected' : 'Test failed',
        duration_ms: Math.floor(Math.random() * 500) + 10,
      });
    }
    resultsByCategory[cat] = results;
  });

  const total = totalPassed + totalFailed + totalWarnings;
  return {
    report_id: `test_${Date.now()}`,
    run_type: 'full',
    started_at: new Date(Date.now() - 125000).toISOString(),
    completed_at: new Date().toISOString(),
    duration_seconds: 125.4,
    total_tests: total,
    passed: totalPassed,
    failed: totalFailed,
    warnings: totalWarnings,
    skipped: 0,
    errors: 0,
    pass_rate: Math.round((totalPassed / total) * 1000) / 10,
    summary: {
      total,
      passed: totalPassed,
      failed: totalFailed,
      warnings: totalWarnings,
      errors: 0,
      pass_rate: Math.round((totalPassed / total) * 1000) / 10,
      health_score: Math.round((totalPassed / total) * 100 * 10) / 10,
    },
    results_by_category: resultsByCategory,
    recommendations: [
      { test_id: 'build_chunk', severity: 'medium', category: 'frontend_build', title: 'Large bundle chunks detected', description: 'Some chunks exceed 500KB', fix_suggestion: 'Implement code splitting with React.lazy() for large pages' },
      { test_id: 'heroicon_dep', severity: 'low', category: 'frontend_pages', title: 'Deprecated icon imports', description: '3 pages use old Heroicons v1 names', fix_suggestion: 'Update to v2 naming: TrendingUpIcon → ArrowTrendingUpIcon' },
      { test_id: 'unused_model', severity: 'low', category: 'models_schemas', title: 'Unused model fields', description: '5 models have fields not used by any endpoint', fix_suggestion: 'Review and clean up unused columns or add endpoints' },
      { test_id: 'missing_index', severity: 'high', category: 'models_schemas', title: 'Missing database indexes', description: 'High-traffic query columns lack indexes', fix_suggestion: 'Add composite index on (organization_id, status) for placement_records' },
      { test_id: 'slow_endpoint', severity: 'medium', category: 'api_endpoints', title: 'Slow endpoint detected', description: '/api/v1/aggregate-reports/cross-dimensional avg 2.3s', fix_suggestion: 'Add caching or pre-computed materialized views' },
    ],
  };
}

function generateMockHealth(): HealthData {
  return {
    overall_health: 92.2,
    status: 'healthy',
    components: [
      { name: 'API Endpoints', health: 98.5, status: 'healthy', last_checked: new Date().toISOString() },
      { name: 'Frontend Build', health: 95.0, status: 'healthy', last_checked: new Date().toISOString() },
      { name: 'Database Models', health: 91.3, status: 'healthy', last_checked: new Date().toISOString() },
      { name: 'Route Consistency', health: 88.0, status: 'warning', last_checked: new Date().toISOString() },
      { name: 'Dependencies', health: 96.7, status: 'healthy', last_checked: new Date().toISOString() },
    ],
    trends: Array.from({ length: 14 }, (_, i) => ({
      date: new Date(Date.now() - (13 - i) * 86400000).toISOString().slice(0, 10),
      score: 85 + Math.random() * 10,
    })),
  };
}

function generateMockCoverage(): CoverageData {
  return {
    api_coverage: 94.2,
    frontend_coverage: 87.5,
    model_coverage: 91.0,
    overall_coverage: 90.9,
    uncovered_areas: [
      { area: '/api/v1/vms/timesheets/{id}/compliance-check', type: 'api', priority: 'high' },
      { area: 'msp/VMSTimesheets.tsx', type: 'frontend', priority: 'medium' },
      { area: 'ExpenseEntry model', type: 'model', priority: 'low' },
      { area: '/api/v1/invoicing/supplier-remittance', type: 'api', priority: 'medium' },
    ],
  };
}

// ── Main Component ──
export function TestingDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'results' | 'recommendations' | 'coverage' | 'history' | 'logs'>('overview');
  const [report, setReport] = useState<TestReport | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [coverage, setCoverage] = useState<CoverageData | null>(null);
  const [running, setRunning] = useState(false);
  const [runType, setRunType] = useState('full');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [logOutput, setLogOutput] = useState('');
  const [analyzingLogs, setAnalyzingLogs] = useState(false);

  // Load initial data
  useEffect(() => {
    setReport(generateMockReport());
    setHealth(generateMockHealth());
    setCoverage(generateMockCoverage());
    setHistory(Array.from({ length: 10 }, (_, i) => ({
      id: `run_${10 - i}`,
      run_type: ['full', 'quick_smoke', 'api_only', 'frontend_only'][i % 4],
      started_at: new Date(Date.now() - i * 3600000 * 6).toISOString(),
      duration_seconds: 30 + Math.random() * 120,
      health_score: 85 + Math.random() * 12,
      passed: 480 + Math.floor(Math.random() * 30),
      failed: Math.floor(Math.random() * 5),
      warnings: 20 + Math.floor(Math.random() * 20),
      total: 532,
      status: i === 3 ? 'failed' : 'completed',
    })));
  }, []);

  const handleRunTests = useCallback(async () => {
    setRunning(true);
    setLogOutput('');
    // Simulate test run
    const steps = [
      '▸ Initializing test agent...',
      '▸ Loading platform configuration (490 routes, 108 models)...',
      `▸ Running ${runType} test suite...`,
      '  ✓ API endpoint validation: 180 tests',
      '  ✓ Frontend page scanner: 42 pages checked',
      '  ✓ Frontend build: compiled 1340+ modules',
      '  ✓ Model/schema validation: 108 models',
      '  ✓ Route consistency check: sidebar ↔ routes',
      '  ✓ Dependency audit: Python + Node packages',
      '▸ Generating test report...',
      '▸ Calculating health score...',
      '✓ Test run complete!',
    ];
    for (const step of steps) {
      await new Promise(r => setTimeout(r, 400 + Math.random() * 600));
      setLogOutput(prev => prev + step + '\n');
    }
    setReport(generateMockReport());
    setHealth(generateMockHealth());
    setRunning(false);
  }, [runType]);

  const handleAnalyzeLogs = useCallback(async () => {
    setAnalyzingLogs(true);
    setLogOutput('▸ Scanning application logs...\n');
    const logLines = [
      '▸ Parsing FastAPI access logs (last 24h)...',
      '  Found 2,341 requests, 12 errors (0.5% error rate)',
      '▸ Analyzing frontend console errors...',
      '  Found 3 React hydration warnings',
      '▸ Checking database query performance...',
      '  2 slow queries detected (>1s)',
      '▸ Reviewing agent execution logs...',
      '  All 10 AI agents operational',
      '▸ Generating analysis report...',
      '',
      '═══ LOG ANALYSIS RESULTS ═══',
      'Overall Status: HEALTHY',
      '',
      'Issues Found:',
      '  [MEDIUM] POST /api/v1/aggregate-reports/cross-dimensional — avg 2.3s response',
      '  [LOW] React StrictMode double-render on CustomReportBuilder',
      '  [LOW] 3 deprecation warnings in node_modules',
      '',
      'Recommendations:',
      '  1. Add Redis caching for cross-dimensional report endpoint',
      '  2. Memoize expensive calculations in CustomReportBuilder',
      '  3. Update @tanstack/react-query to latest (fixes deprecation)',
    ];
    for (const line of logLines) {
      await new Promise(r => setTimeout(r, 300 + Math.random() * 400));
      setLogOutput(prev => prev + line + '\n');
    }
    setAnalyzingLogs(false);
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: ChartBarIcon },
    { id: 'results', label: 'Test Results', icon: BeakerIcon },
    { id: 'recommendations', label: 'Recommendations', icon: WrenchScrewdriverIcon },
    { id: 'coverage', label: 'Coverage', icon: ShieldCheckIcon },
    { id: 'history', label: 'History', icon: ClockIcon },
    { id: 'logs', label: 'Log Analysis', icon: CommandLineIcon },
  ] as const;

  // ── Health Score Gauge ──
  const HealthGauge = ({ score }: { score: number }) => {
    const color = score >= 90 ? '#10b981' : score >= 75 ? '#f59e0b' : '#ef4444';
    const circumference = 2 * Math.PI * 45;
    const filled = (score / 100) * circumference;
    return (
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="8" />
          <circle cx="50" cy="50" r="45" fill="none" stroke={color} strokeWidth="8" strokeDasharray={`${filled} ${circumference}`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold" style={{ color }}>{score.toFixed(1)}</span>
          <span className="text-xs text-gray-500">Health</span>
        </div>
      </div>
    );
  };

  // ── Status Badge ──
  const StatusBadge = ({ status }: { status: string }) => {
    const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.skipped;
    const Icon = cfg.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.color}`}>
        <Icon className="w-3.5 h-3.5" />
        {status}
      </span>
    );
  };

  // ── Severity Badge ──
  const SeverityBadge = ({ severity }: { severity: string }) => (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${SEVERITY_COLORS[severity] || SEVERITY_COLORS.info}`}>
      {severity}
    </span>
  );

  return (
    <div className="p-6 max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-violet-100 rounded-lg">
            <BeakerIcon className="w-6 h-6 text-violet-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">E2E Testing Dashboard</h1>
            <p className="text-sm text-gray-500">Continuous testing, log analysis & fix recommendations</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={runType}
            onChange={e => setRunType(e.target.value)}
            className="px-3 py-2 border rounded-lg text-sm bg-white"
          >
            {RUN_TYPES.map(t => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
          <button
            onClick={handleRunTests}
            disabled={running}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white ${
              running ? 'bg-violet-400 cursor-not-allowed' : 'bg-violet-600 hover:bg-violet-700'
            }`}
          >
            {running ? (
              <><ArrowPathIcon className="w-4 h-4 animate-spin" /> Running...</>
            ) : (
              <><PlayIcon className="w-4 h-4" /> Run Tests</>
            )}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-1">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  activeTab === tab.id
                    ? 'border-violet-600 text-violet-700'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ═══ OVERVIEW TAB ═══ */}
      {activeTab === 'overview' && report && health && (
        <div className="space-y-6">
          {/* Stats Row */}
          <div className="grid grid-cols-6 gap-4">
            {[
              { label: 'Total Tests', value: report.total_tests, color: 'text-gray-900' },
              { label: 'Passed', value: report.passed, color: 'text-emerald-600' },
              { label: 'Failed', value: report.failed, color: 'text-red-600' },
              { label: 'Warnings', value: report.warnings, color: 'text-amber-600' },
              { label: 'Pass Rate', value: `${report.pass_rate}%`, color: 'text-blue-600' },
              { label: 'Duration', value: `${report.duration_seconds.toFixed(0)}s`, color: 'text-gray-600' },
            ].map(s => (
              <div key={s.label} className="bg-white rounded-xl border p-4 text-center">
                <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                <div className="text-xs text-gray-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Health + Component Status */}
          <div className="grid grid-cols-3 gap-6">
            {/* Health Gauge */}
            <div className="bg-white rounded-xl border p-6 flex flex-col items-center">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Platform Health Score</h3>
              <HealthGauge score={health.overall_health} />
              <span className={`mt-3 px-3 py-1 rounded-full text-xs font-medium ${
                health.overall_health >= 90 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
              }`}>
                {health.status.toUpperCase()}
              </span>
            </div>

            {/* Component Health */}
            <div className="bg-white rounded-xl border p-6 col-span-2">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Component Health</h3>
              <div className="space-y-3">
                {health.components.map(c => (
                  <div key={c.name} className="flex items-center gap-3">
                    <div className="w-32 text-sm text-gray-600">{c.name}</div>
                    <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${c.health >= 90 ? 'bg-emerald-500' : c.health >= 75 ? 'bg-amber-500' : 'bg-red-500'}`}
                        style={{ width: `${c.health}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-14 text-right">{c.health.toFixed(1)}%</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      c.status === 'healthy' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                    }`}>{c.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Health Trend Chart */}
          <div className="bg-white rounded-xl border p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Health Score Trend (14 days)</h3>
            <div className="h-32 flex items-end gap-1">
              {health.trends.map((t, i) => {
                const height = ((t.score - 80) / 20) * 100;
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <div
                      className={`w-full rounded-t ${t.score >= 90 ? 'bg-emerald-400' : 'bg-amber-400'}`}
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`${t.date}: ${t.score.toFixed(1)}`}
                    />
                    {i % 2 === 0 && (
                      <span className="text-[9px] text-gray-400">{t.date.slice(5)}</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Top Recommendations Preview */}
          {report.recommendations.length > 0 && (
            <div className="bg-white rounded-xl border p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-700">Top Recommendations</h3>
                <button onClick={() => setActiveTab('recommendations')} className="text-xs text-violet-600 hover:underline">View all</button>
              </div>
              <div className="space-y-2">
                {report.recommendations.slice(0, 3).map(r => (
                  <div key={r.test_id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <SeverityBadge severity={r.severity} />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900">{r.title}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{r.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ═══ RESULTS TAB ═══ */}
      {activeTab === 'results' && report && (
        <div className="space-y-4">
          {/* Category Filter */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-gray-500 mr-2"><FunnelIcon className="w-4 h-4 inline" /> Category:</span>
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium ${!selectedCategory ? 'bg-violet-100 text-violet-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >All</button>
            {Object.keys(report.results_by_category).map(cat => {
              const Icon = CATEGORY_ICONS[cat] || BeakerIcon;
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium ${selectedCategory === cat ? 'bg-violet-100 text-violet-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {cat.replace(/_/g, ' ')}
                </button>
              );
            })}
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 mr-2">Status:</span>
            {[null, 'passed', 'failed', 'warning'].map(s => (
              <button
                key={s || 'all'}
                onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium ${statusFilter === s ? 'bg-violet-100 text-violet-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                {s || 'All'}
              </button>
            ))}
          </div>

          {/* Results by Category */}
          {Object.entries(report.results_by_category)
            .filter(([cat]) => !selectedCategory || cat === selectedCategory)
            .map(([category, results]) => {
              const filtered = statusFilter ? results.filter(r => r.status === statusFilter) : results;
              if (filtered.length === 0) return null;
              const CatIcon = CATEGORY_ICONS[category] || BeakerIcon;
              const passed = results.filter(r => r.status === 'passed').length;
              const failed = results.filter(r => r.status === 'failed').length;
              const warns = results.filter(r => r.status === 'warning').length;

              return (
                <div key={category} className="bg-white rounded-xl border overflow-hidden">
                  <div className="flex items-center justify-between px-5 py-3 bg-gray-50 border-b">
                    <div className="flex items-center gap-2">
                      <CatIcon className="w-5 h-5 text-violet-600" />
                      <span className="font-medium text-gray-900 capitalize">{category.replace(/_/g, ' ')}</span>
                      <span className="text-xs text-gray-500">({results.length} tests)</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-emerald-600">{passed} passed</span>
                      {failed > 0 && <span className="text-red-600">{failed} failed</span>}
                      {warns > 0 && <span className="text-amber-600">{warns} warnings</span>}
                    </div>
                  </div>
                  <div className="divide-y max-h-64 overflow-y-auto">
                    {filtered.slice(0, 50).map(r => (
                      <div key={r.test_id} className="flex items-center gap-3 px-5 py-2 text-sm hover:bg-gray-50">
                        <StatusBadge status={r.status} />
                        <span className="flex-1 text-gray-700 truncate">{r.name}</span>
                        <span className="text-xs text-gray-400">{r.message}</span>
                        {r.duration_ms && <span className="text-xs text-gray-400 w-14 text-right">{r.duration_ms}ms</span>}
                      </div>
                    ))}
                    {filtered.length > 50 && (
                      <div className="px-5 py-2 text-xs text-gray-400 text-center">
                        + {filtered.length - 50} more results
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* ═══ RECOMMENDATIONS TAB ═══ */}
      {activeTab === 'recommendations' && report && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Fix Recommendations for App Admin</h3>
            <div className="space-y-4">
              {report.recommendations.map((rec, i) => (
                <div key={rec.test_id} className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-start gap-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-violet-50 text-violet-600 font-bold text-sm flex-shrink-0">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={rec.severity} />
                        <span className="text-xs text-gray-400 uppercase">{rec.category.replace(/_/g, ' ')}</span>
                      </div>
                      <h4 className="font-medium text-gray-900">{rec.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                      <div className="mt-3 p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                        <div className="flex items-center gap-1 text-xs font-medium text-emerald-700 mb-1">
                          <WrenchScrewdriverIcon className="w-3.5 h-3.5" /> Suggested Fix
                        </div>
                        <p className="text-sm text-emerald-800">{rec.fix_suggestion}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ═══ COVERAGE TAB ═══ */}
      {activeTab === 'coverage' && coverage && (
        <div className="space-y-6">
          {/* Coverage Gauges */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'API Coverage', value: coverage.api_coverage },
              { label: 'Frontend Coverage', value: coverage.frontend_coverage },
              { label: 'Model Coverage', value: coverage.model_coverage },
              { label: 'Overall Coverage', value: coverage.overall_coverage },
            ].map(c => (
              <div key={c.label} className="bg-white rounded-xl border p-5 text-center">
                <div className="relative w-20 h-20 mx-auto mb-3">
                  <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" strokeWidth="10" />
                    <circle cx="50" cy="50" r="40" fill="none"
                      stroke={c.value >= 90 ? '#10b981' : c.value >= 75 ? '#f59e0b' : '#ef4444'}
                      strokeWidth="10"
                      strokeDasharray={`${(c.value / 100) * 251.3} 251.3`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center text-lg font-bold">{c.value}%</div>
                </div>
                <div className="text-sm text-gray-600">{c.label}</div>
              </div>
            ))}
          </div>

          {/* Uncovered Areas */}
          <div className="bg-white rounded-xl border p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Uncovered Areas</h3>
            <div className="space-y-2">
              {coverage.uncovered_areas.map((area, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    area.priority === 'high' ? 'bg-red-100 text-red-700' :
                    area.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>{area.priority}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700`}>{area.type}</span>
                  <span className="text-sm text-gray-700 font-mono">{area.area}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ═══ HISTORY TAB ═══ */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase">Run</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-right px-5 py-3 text-xs font-medium text-gray-500 uppercase">Health</th>
                <th className="text-right px-5 py-3 text-xs font-medium text-gray-500 uppercase">Passed</th>
                <th className="text-right px-5 py-3 text-xs font-medium text-gray-500 uppercase">Failed</th>
                <th className="text-right px-5 py-3 text-xs font-medium text-gray-500 uppercase">Warnings</th>
                <th className="text-right px-5 py-3 text-xs font-medium text-gray-500 uppercase">Duration</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-gray-500 uppercase">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {history.map(h => (
                <tr key={h.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 text-sm font-mono text-gray-600">{h.id}</td>
                  <td className="px-5 py-3">
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-violet-50 text-violet-700">
                      {h.run_type}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      h.status === 'completed' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                    }`}>{h.status}</span>
                  </td>
                  <td className="px-5 py-3 text-right text-sm font-medium">{h.health_score.toFixed(1)}%</td>
                  <td className="px-5 py-3 text-right text-sm text-emerald-600">{h.passed}</td>
                  <td className="px-5 py-3 text-right text-sm text-red-600">{h.failed}</td>
                  <td className="px-5 py-3 text-right text-sm text-amber-600">{h.warnings}</td>
                  <td className="px-5 py-3 text-right text-sm text-gray-500">{h.duration_seconds.toFixed(0)}s</td>
                  <td className="px-5 py-3 text-sm text-gray-500">
                    {new Date(h.started_at).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ═══ LOG ANALYSIS TAB ═══ */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <button
              onClick={handleAnalyzeLogs}
              disabled={analyzingLogs}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white ${
                analyzingLogs ? 'bg-violet-400 cursor-not-allowed' : 'bg-violet-600 hover:bg-violet-700'
              }`}
            >
              {analyzingLogs ? (
                <><ArrowPathIcon className="w-4 h-4 animate-spin" /> Analyzing...</>
              ) : (
                <><DocumentMagnifyingGlassIcon className="w-4 h-4" /> Analyze Logs</>
              )}
            </button>
            <span className="text-sm text-gray-500">Scans FastAPI access logs, frontend console, DB queries, and agent execution logs</span>
          </div>

          <div className="bg-gray-900 rounded-xl p-6 font-mono text-sm text-green-400 min-h-[400px] whitespace-pre-wrap overflow-auto">
            {logOutput || '$ Waiting for log analysis... Click "Analyze Logs" or "Run Tests" to begin.\n\nTip: Log analysis scans the last 24 hours of:\n  • FastAPI request/response logs\n  • Frontend console errors\n  • Database query performance\n  • AI agent execution logs\n  • Background job status\n\nResults include severity-ranked issues and fix recommendations for App Admin.'}
          </div>
        </div>
      )}
    </div>
  );
}
