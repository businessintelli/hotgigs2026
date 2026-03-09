import React, { useState } from 'react';
import {
  ChartBarIcon,
  FunnelIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/react/24/outline';

// ── Types ──
interface PhaseConversion {
  from_phase: string;
  to_phase: string;
  candidates_entered: number;
  candidates_converted: number;
  conversion_rate: number;
  avg_time_hours: number;
  trend: string;
}
interface FunnelData {
  job_id: number;
  job_title: string;
  phases: string[];
  phase_counts: Record<string, number>;
  conversions: PhaseConversion[];
  total_candidates: number;
  overall_conversion: number;
  bottleneck_phase: string | null;
  bottleneck_reason: string | null;
  avg_days_to_hire: number;
}

// ── Mock Data Generator ──
const PHASES = ['Applied', 'Screening', 'Reviewed', 'Shortlisted', 'Interviewing', 'Offered', 'Hired'];
const JOBS = [
  { id: 1, title: 'Senior Python Developer', total: 142 },
  { id: 2, title: 'React Frontend Lead', total: 98 },
  { id: 3, title: 'DevOps Engineer', total: 76 },
  { id: 4, title: 'Data Scientist', total: 115 },
  { id: 5, title: 'Product Manager', total: 89 },
];

function generateFunnel(job: typeof JOBS[0]): FunnelData {
  let remaining = job.total;
  const rates = [0.65, 0.60, 0.55, 0.70, 0.80, 0.88];
  const phaseCounts: Record<string, number> = {};
  PHASES.forEach((p, i) => {
    phaseCounts[p] = remaining;
    if (i < PHASES.length - 1) remaining = Math.max(1, Math.round(remaining * rates[i]));
  });
  const conversions: PhaseConversion[] = [];
  for (let i = 0; i < PHASES.length - 1; i++) {
    const entered = phaseCounts[PHASES[i]];
    const converted = phaseCounts[PHASES[i + 1]];
    const rate = entered ? Math.round((converted / entered) * 1000) / 10 : 0;
    conversions.push({
      from_phase: PHASES[i], to_phase: PHASES[i + 1],
      candidates_entered: entered, candidates_converted: converted,
      conversion_rate: rate, avg_time_hours: Math.round(Math.random() * 80 + 12),
      trend: ['improving', 'stable', 'declining'][Math.floor(Math.random() * 3)],
    });
  }
  const worst = conversions.reduce((a, b) => a.conversion_rate < b.conversion_rate ? a : b);
  return {
    job_id: job.id, job_title: job.title, phases: PHASES,
    phase_counts: phaseCounts, conversions,
    total_candidates: job.total,
    overall_conversion: Math.round((phaseCounts['Hired'] / job.total) * 1000) / 10,
    bottleneck_phase: worst.from_phase,
    bottleneck_reason: `Only ${worst.conversion_rate}% convert from ${worst.from_phase} to ${worst.to_phase}`,
    avg_days_to_hire: Math.round(Math.random() * 25 + 18),
  };
}

// ── Trend data ──
function generateTrends() {
  const data: { date: string; applied: number; hired: number; rate: number }[] = [];
  let applied = 120;
  for (let d = 29; d >= 0; d--) {
    const date = new Date(Date.now() - d * 86400000);
    applied += Math.floor(Math.random() * 10 - 4);
    applied = Math.max(50, applied);
    const hired = Math.round(applied * (0.12 + Math.random() * 0.06));
    data.push({
      date: `${date.getMonth() + 1}/${date.getDate()}`,
      applied, hired,
      rate: Math.round((hired / applied) * 1000) / 10,
    });
  }
  return data;
}

const PHASE_COLORS: Record<string, string> = {
  Applied: 'bg-blue-500', Screening: 'bg-indigo-500', Reviewed: 'bg-purple-500',
  Shortlisted: 'bg-violet-500', Interviewing: 'bg-amber-500', Offered: 'bg-emerald-500', Hired: 'bg-green-600',
};

const trendData = generateTrends();

export const PipelineAnalytics: React.FC = () => {
  const [selectedJob, setSelectedJob] = useState(0);
  const [tab, setTab] = useState<'funnel' | 'trends' | 'compare'>('funnel');

  const funnels = JOBS.map(generateFunnel);
  const funnel = funnels[selectedJob];
  const maxCount = funnel.total_candidates;

  const tabs = [
    { key: 'funnel' as const, label: 'Conversion Funnel', icon: FunnelIcon },
    { key: 'trends' as const, label: 'Trends Over Time', icon: ArrowTrendingUpIcon },
    { key: 'compare' as const, label: 'Compare Jobs', icon: ArrowsRightLeftIcon },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Pipeline Analytics</h1>
          <p className="text-sm text-neutral-500 mt-1">Conversion rates, funnel visualization, and bottleneck detection</p>
        </div>
        <select
          value={selectedJob}
          onChange={(e) => setSelectedJob(Number(e.target.value))}
          className="border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
        >
          {JOBS.map((j, i) => (
            <option key={j.id} value={i}>{j.title}</option>
          ))}
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Candidates', value: funnel.total_candidates, color: 'text-blue-600' },
          { label: 'Overall Conversion', value: `${funnel.overall_conversion}%`, color: 'text-green-600' },
          { label: 'Avg Days to Hire', value: funnel.avg_days_to_hire, color: 'text-amber-600' },
          { label: 'Bottleneck', value: funnel.bottleneck_phase || 'None', color: 'text-red-600' },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl border border-neutral-200 p-4">
            <p className="text-xs text-neutral-500">{kpi.label}</p>
            <p className={`text-2xl font-bold ${kpi.color} mt-1`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
              tab === key ? 'bg-white text-blue-700 shadow-sm' : 'text-neutral-600 hover:text-neutral-800'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ── FUNNEL TAB ── */}
      {tab === 'funnel' && (
        <div className="space-y-6">
          {/* Visual Funnel */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4 flex items-center gap-2">
              <FunnelIcon className="h-4 w-4" /> Conversion Funnel — {funnel.job_title}
            </h3>
            <div className="space-y-3">
              {PHASES.map((phase) => {
                const count = funnel.phase_counts[phase] || 0;
                const pct = maxCount ? (count / maxCount) * 100 : 0;
                return (
                  <div key={phase} className="flex items-center gap-3">
                    <div className="w-28 text-sm font-medium text-neutral-700 text-right">{phase}</div>
                    <div className="flex-1 bg-neutral-100 rounded-full h-8 relative overflow-hidden">
                      <div
                        className={`${PHASE_COLORS[phase] || 'bg-blue-500'} h-full rounded-full transition-all duration-500 flex items-center justify-end pr-3`}
                        style={{ width: `${Math.max(pct, 3)}%` }}
                      >
                        <span className="text-xs font-bold text-white">{count}</span>
                      </div>
                    </div>
                    <div className="w-16 text-sm text-neutral-500 text-right">{Math.round(pct)}%</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Conversion Rate Table */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4 flex items-center gap-2">
              <ChartBarIcon className="h-4 w-4" /> Phase-to-Phase Conversion Rates
            </h3>
            <table className="w-full">
              <thead>
                <tr className="text-xs text-neutral-500 border-b">
                  <th className="text-left py-2 font-medium">Transition</th>
                  <th className="text-center py-2 font-medium">Entered</th>
                  <th className="text-center py-2 font-medium">Converted</th>
                  <th className="text-center py-2 font-medium">Rate</th>
                  <th className="text-center py-2 font-medium">Avg Time</th>
                  <th className="text-center py-2 font-medium">Trend</th>
                </tr>
              </thead>
              <tbody>
                {funnel.conversions.map((c) => {
                  const isBottleneck = c.from_phase === funnel.bottleneck_phase;
                  return (
                    <tr key={`${c.from_phase}-${c.to_phase}`} className={`border-b last:border-0 ${isBottleneck ? 'bg-red-50' : ''}`}>
                      <td className="py-3 text-sm font-medium text-neutral-800">
                        {c.from_phase} <span className="text-neutral-400 mx-1">&rarr;</span> {c.to_phase}
                        {isBottleneck && (
                          <span className="ml-2 inline-flex items-center gap-1 text-xs text-red-600 bg-red-100 px-2 py-0.5 rounded-full">
                            <ExclamationTriangleIcon className="h-3 w-3" /> Bottleneck
                          </span>
                        )}
                      </td>
                      <td className="text-center text-sm text-neutral-600">{c.candidates_entered}</td>
                      <td className="text-center text-sm text-neutral-600">{c.candidates_converted}</td>
                      <td className="text-center">
                        <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${
                          c.conversion_rate >= 70 ? 'bg-green-100 text-green-700' :
                          c.conversion_rate >= 50 ? 'bg-amber-100 text-amber-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {c.conversion_rate}%
                        </span>
                      </td>
                      <td className="text-center text-sm text-neutral-500">
                        <ClockIcon className="h-3.5 w-3.5 inline mr-1" />
                        {Math.round(c.avg_time_hours / 24)}d
                      </td>
                      <td className="text-center">
                        {c.trend === 'improving' && <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mx-auto" />}
                        {c.trend === 'declining' && <ArrowTrendingDownIcon className="h-4 w-4 text-red-500 mx-auto" />}
                        {c.trend === 'stable' && <span className="text-xs text-neutral-400">—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Bottleneck Alert */}
          {funnel.bottleneck_phase && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-800">Bottleneck Detected at {funnel.bottleneck_phase}</p>
                <p className="text-sm text-red-600 mt-1">{funnel.bottleneck_reason}</p>
                <p className="text-xs text-red-500 mt-2">Recommendation: Review screening criteria or increase recruiter capacity for this phase.</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── TRENDS TAB ── */}
      {tab === 'trends' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4">30-Day Pipeline Trend</h3>
            <div className="space-y-1">
              {/* Mini chart as bars */}
              <div className="flex items-end gap-0.5 h-40">
                {trendData.map((d, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center justify-end gap-0.5">
                    <div
                      className="w-full bg-blue-400 rounded-t"
                      style={{ height: `${(d.applied / 180) * 100}%` }}
                      title={`${d.date}: ${d.applied} applied`}
                    />
                    <div
                      className="w-full bg-green-500 rounded-t"
                      style={{ height: `${(d.hired / 180) * 100}%` }}
                      title={`${d.date}: ${d.hired} hired`}
                    />
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-xs text-neutral-400 mt-2">
                <span>{trendData[0]?.date}</span>
                <span>{trendData[Math.floor(trendData.length / 2)]?.date}</span>
                <span>{trendData[trendData.length - 1]?.date}</span>
              </div>
              <div className="flex gap-4 mt-3">
                <span className="flex items-center gap-1.5 text-xs text-neutral-600">
                  <span className="w-3 h-3 bg-blue-400 rounded" /> Applied
                </span>
                <span className="flex items-center gap-1.5 text-xs text-neutral-600">
                  <span className="w-3 h-3 bg-green-500 rounded" /> Hired
                </span>
              </div>
            </div>
          </div>

          {/* Conversion rate trend */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4">Conversion Rate Trend (Applied → Hired)</h3>
            <div className="flex items-end gap-0.5 h-32">
              {trendData.map((d, i) => (
                <div key={i} className="flex-1 flex flex-col items-center justify-end">
                  <div
                    className={`w-full rounded-t ${d.rate > 15 ? 'bg-green-400' : d.rate > 10 ? 'bg-amber-400' : 'bg-red-400'}`}
                    style={{ height: `${(d.rate / 25) * 100}%` }}
                    title={`${d.date}: ${d.rate}%`}
                  />
                </div>
              ))}
            </div>
            <div className="flex justify-between text-xs text-neutral-400 mt-2">
              <span>{trendData[0]?.date}</span>
              <span>{trendData[trendData.length - 1]?.date}</span>
            </div>
          </div>
        </div>
      )}

      {/* ── COMPARE TAB ── */}
      {tab === 'compare' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4">Job Pipeline Comparison</h3>
            <table className="w-full">
              <thead>
                <tr className="text-xs text-neutral-500 border-b">
                  <th className="text-left py-2 font-medium">Job</th>
                  <th className="text-center py-2 font-medium">Candidates</th>
                  <th className="text-center py-2 font-medium">Hired</th>
                  <th className="text-center py-2 font-medium">Conversion</th>
                  <th className="text-center py-2 font-medium">Avg Days to Hire</th>
                  <th className="text-left py-2 font-medium">Funnel</th>
                </tr>
              </thead>
              <tbody>
                {funnels.map((f) => (
                  <tr key={f.job_id} className="border-b last:border-0 hover:bg-neutral-50">
                    <td className="py-3 text-sm font-medium text-neutral-800">{f.job_title}</td>
                    <td className="text-center text-sm text-neutral-600">{f.total_candidates}</td>
                    <td className="text-center text-sm font-semibold text-green-600">{f.phase_counts['Hired']}</td>
                    <td className="text-center">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${
                        f.overall_conversion >= 15 ? 'bg-green-100 text-green-700' :
                        f.overall_conversion >= 10 ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {f.overall_conversion}%
                      </span>
                    </td>
                    <td className="text-center text-sm text-neutral-500">{f.avg_days_to_hire}d</td>
                    <td className="py-3">
                      <div className="flex items-center gap-0.5 h-4">
                        {PHASES.map((p) => {
                          const pct = f.total_candidates ? (f.phase_counts[p] / f.total_candidates) * 100 : 0;
                          return (
                            <div
                              key={p}
                              className={`${PHASE_COLORS[p]} h-full rounded`}
                              style={{ width: `${Math.max(pct, 2)}%` }}
                              title={`${p}: ${f.phase_counts[p]}`}
                            />
                          );
                        })}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Best / Worst */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <p className="text-xs text-green-600 font-medium">Best Performing</p>
              <p className="text-lg font-bold text-green-800 mt-1">
                {funnels.reduce((a, b) => a.overall_conversion > b.overall_conversion ? a : b).job_title}
              </p>
              <p className="text-sm text-green-600 mt-1">
                {funnels.reduce((a, b) => a.overall_conversion > b.overall_conversion ? a : b).overall_conversion}% overall conversion
              </p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-xs text-red-600 font-medium">Biggest Bottleneck</p>
              <p className="text-lg font-bold text-red-800 mt-1">
                {funnels.reduce((a, b) => a.overall_conversion < b.overall_conversion ? a : b).job_title}
              </p>
              <p className="text-sm text-red-600 mt-1">
                {funnels.reduce((a, b) => a.overall_conversion < b.overall_conversion ? a : b).bottleneck_reason}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
