import React, { useState } from 'react';
import {
  BuildingOffice2Icon,
  BriefcaseIcon,
  TruckIcon,
  UserGroupIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  FunnelIcon,
  TableCellsIcon,
  ShieldExclamationIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  StarIcon,
  ClockIcon,
  MapPinIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

// ── Role Config ──
type UserRole = 'msp_admin' | 'company_admin' | 'company_recruiter';

interface RoleConfig {
  label: string;
  description: string;
  color: string;
  bgColor: string;
}

const ROLE_CONFIG: Record<UserRole, RoleConfig> = {
  msp_admin: { label: 'MSP Admin', description: 'Full access to all reports across all clients, suppliers, and recruiters', color: 'text-purple-700', bgColor: 'bg-purple-100 border-purple-300' },
  company_admin: { label: 'Company Admin', description: 'Access to your company data: jobs, recruiters, and suppliers serving you', color: 'text-blue-700', bgColor: 'bg-blue-100 border-blue-300' },
  company_recruiter: { label: 'Company Recruiter', description: 'Access to your own performance and assigned jobs', color: 'text-emerald-700', bgColor: 'bg-emerald-100 border-emerald-300' },
};

// ── Report Tab Config ──
interface ReportTab {
  key: string;
  label: string;
  icon: React.ForwardRefExoticComponent<any>;
  roles: UserRole[]; // which roles can see this tab
  description: string;
}

const REPORT_TABS: ReportTab[] = [
  { key: 'by_client', label: 'By Client', icon: BuildingOffice2Icon, roles: ['msp_admin'], description: 'Client performance across the program' },
  { key: 'by_job', label: 'By Job', icon: BriefcaseIcon, roles: ['msp_admin', 'company_admin', 'company_recruiter'], description: 'Job-level statistics and applicant breakdown' },
  { key: 'by_supplier', label: 'By Supplier', icon: TruckIcon, roles: ['msp_admin', 'company_admin'], description: 'Supplier performance and fill rates' },
  { key: 'by_recruiter', label: 'By Recruiter', icon: UserGroupIcon, roles: ['msp_admin', 'company_admin', 'company_recruiter'], description: 'Recruiter performance and activity' },
  { key: 'by_company', label: 'Company Executive', icon: ChartBarIcon, roles: ['msp_admin', 'company_admin'], description: 'Company-wide executive summary' },
  { key: 'pipeline_velocity', label: 'Pipeline Velocity', icon: ArrowTrendingUpIcon, roles: ['msp_admin', 'company_admin', 'company_recruiter'], description: 'Pipeline phase timing and bottlenecks' },
  { key: 'conversion_funnel', label: 'Conversion Funnel', icon: FunnelIcon, roles: ['msp_admin', 'company_admin', 'company_recruiter'], description: 'Full hiring funnel with drop-off analysis' },
  { key: 'cross_dimensional', label: 'Cross-Dimensional', icon: TableCellsIcon, roles: ['msp_admin', 'company_admin'], description: 'Multi-dimensional performance matrices' },
];

// ── Mock Data ──
const clientData = [
  { id: 1, name: 'TechCorp Industries', jobs: 18, active: 5, submissions: 142, interviews: 48, offers: 12, placements: 8, ttf: 24.5, fillRate: 72.0, matchScore: 84.2, spend: 1245000, satisfaction: 4.6 },
  { id: 2, name: 'CloudNine Systems', jobs: 12, active: 4, submissions: 96, interviews: 32, offers: 9, placements: 6, ttf: 18.2, fillRate: 78.0, matchScore: 87.1, spend: 980000, satisfaction: 4.8 },
  { id: 3, name: 'AnalyticsPro', jobs: 8, active: 3, submissions: 74, interviews: 22, offers: 6, placements: 4, ttf: 28.3, fillRate: 66.7, matchScore: 81.5, spend: 620000, satisfaction: 4.3 },
  { id: 4, name: 'InnovateCo', jobs: 15, active: 6, submissions: 118, interviews: 40, offers: 10, placements: 7, ttf: 21.0, fillRate: 70.0, matchScore: 85.8, spend: 1080000, satisfaction: 4.5 },
  { id: 5, name: 'DesignHub', jobs: 6, active: 2, submissions: 45, interviews: 15, offers: 4, placements: 3, ttf: 20.1, fillRate: 75.0, matchScore: 82.9, spend: 340000, satisfaction: 4.4 },
  { id: 6, name: 'AI Dynamics', jobs: 10, active: 3, submissions: 88, interviews: 30, offers: 8, placements: 5, ttf: 26.7, fillRate: 62.5, matchScore: 86.4, spend: 890000, satisfaction: 4.7 },
  { id: 7, name: 'GlobalFinance Corp', jobs: 22, active: 8, submissions: 185, interviews: 62, offers: 16, placements: 11, ttf: 19.8, fillRate: 68.8, matchScore: 83.7, spend: 1650000, satisfaction: 4.2 },
];

const jobData = [
  { id: 'JO-1001', title: 'Senior Full Stack Engineer', client: 'TechCorp', priority: 'urgent', rate: '$135/hr', applicants: 24, sourced: 8, screening: 5, submitted: 4, interview: 3, offer: 2, placed: 1, rejected: 1, conversion: 4.2, daysOpen: 28 },
  { id: 'JO-1002', title: 'DevOps Lead', client: 'CloudNine', priority: 'high', rate: '$150/hr', applicants: 18, sourced: 4, screening: 3, submitted: 3, interview: 3, offer: 2, placed: 2, rejected: 1, conversion: 11.1, daysOpen: 22 },
  { id: 'JO-1003', title: 'Data Scientist', client: 'AnalyticsPro', priority: 'normal', rate: '$125/hr', applicants: 31, sourced: 12, screening: 6, submitted: 5, interview: 4, offer: 1, placed: 1, rejected: 2, conversion: 3.2, daysOpen: 35 },
  { id: 'JO-1004', title: 'Product Manager', client: 'InnovateCo', priority: 'high', rate: '$140/hr', applicants: 12, sourced: 3, screening: 2, submitted: 3, interview: 2, offer: 1, placed: 1, rejected: 0, conversion: 8.3, daysOpen: 18 },
  { id: 'JO-1005', title: 'UX Designer', client: 'DesignHub', priority: 'normal', rate: '$110/hr', applicants: 9, sourced: 3, screening: 2, submitted: 2, interview: 1, offer: 1, placed: 0, rejected: 0, conversion: 0, daysOpen: 7 },
  { id: 'JO-1006', title: 'ML Engineer', client: 'AI Dynamics', priority: 'urgent', rate: '$160/hr', applicants: 28, sourced: 6, screening: 4, submitted: 5, interview: 5, offer: 3, placed: 2, rejected: 3, conversion: 7.1, daysOpen: 40 },
  { id: 'JO-1007', title: 'Solutions Architect', client: 'GlobalFinance', priority: 'high', rate: '$155/hr', applicants: 15, sourced: 4, screening: 3, submitted: 3, interview: 2, offer: 1, placed: 1, rejected: 1, conversion: 6.7, daysOpen: 25 },
  { id: 'JO-1008', title: 'Security Engineer', client: 'GlobalFinance', priority: 'urgent', rate: '$145/hr', applicants: 20, sourced: 7, screening: 4, submitted: 3, interview: 3, offer: 2, placed: 1, rejected: 0, conversion: 5.0, daysOpen: 30 },
];

const supplierData = [
  { id: 1, name: 'TalentForce Solutions', candidates: 145, placements: 28, fillRate: 82.4, avgScore: 86.2, avgTTS: 3.2, rejectionRate: 12.4, i2o: 58.3, quality: 4.6, compliance: 97.5, revenue: 2800000, contracts: 8, sla: 96.2 },
  { id: 2, name: 'PrimeStaff Group', candidates: 118, placements: 22, fillRate: 76.8, avgScore: 83.7, avgTTS: 4.1, rejectionRate: 18.6, i2o: 52.1, quality: 4.3, compliance: 94.8, revenue: 2100000, contracts: 6, sla: 92.5 },
  { id: 3, name: 'EliteHire Agency', candidates: 92, placements: 19, fillRate: 79.2, avgScore: 88.1, avgTTS: 2.8, rejectionRate: 8.7, i2o: 63.2, quality: 4.8, compliance: 99.1, revenue: 1950000, contracts: 5, sla: 98.1 },
  { id: 4, name: 'SwiftTalent Inc.', candidates: 78, placements: 14, fillRate: 70.5, avgScore: 81.4, avgTTS: 5.2, rejectionRate: 22.3, i2o: 45.8, quality: 3.9, compliance: 91.2, revenue: 1350000, contracts: 4, sla: 88.7 },
  { id: 5, name: 'NexGen Recruiters', candidates: 110, placements: 24, fillRate: 80.0, avgScore: 85.9, avgTTS: 3.5, rejectionRate: 14.1, i2o: 55.6, quality: 4.5, compliance: 96.3, revenue: 2400000, contracts: 7, sla: 94.8 },
  { id: 6, name: 'CoreStaff Partners', candidates: 65, placements: 11, fillRate: 68.8, avgScore: 80.2, avgTTS: 6.1, rejectionRate: 25.4, i2o: 41.2, quality: 3.7, compliance: 89.5, revenue: 980000, contracts: 3, sla: 86.3 },
];

const recruiterData = [
  { id: 1, name: 'Jane Rodriguez', submissions: 68, placements: 14, conversion: 20.6, avgTTS: 2.4, avgScore: 87.3, revenue: 1420000, activeReqs: 8, pipeline: { sourced: 12, screening: 6, submitted: 8, interview: 4, offer: 2 }, topSkills: ['React', 'Node.js', 'AWS'], topClients: ['TechCorp', 'CloudNine'], trend: [8, 10, 12, 14, 11, 13] },
  { id: 2, name: 'John Martinez', submissions: 52, placements: 11, conversion: 21.2, avgTTS: 2.8, avgScore: 85.1, revenue: 1180000, activeReqs: 6, pipeline: { sourced: 8, screening: 4, submitted: 6, interview: 3, offer: 1 }, topSkills: ['Python', 'DevOps', 'Kubernetes'], topClients: ['AI Dynamics', 'AnalyticsPro'], trend: [6, 8, 9, 10, 8, 11] },
  { id: 3, name: 'Sarah Kim', submissions: 74, placements: 16, conversion: 21.6, avgTTS: 2.1, avgScore: 89.2, revenue: 1680000, activeReqs: 10, pipeline: { sourced: 15, screening: 8, submitted: 10, interview: 5, offer: 3 }, topSkills: ['Java', 'Microservices', 'Cloud'], topClients: ['GlobalFinance', 'InnovateCo'], trend: [10, 12, 14, 16, 13, 15] },
  { id: 4, name: 'David Chen', submissions: 45, placements: 8, conversion: 17.8, avgTTS: 3.5, avgScore: 82.8, revenue: 860000, activeReqs: 5, pipeline: { sourced: 6, screening: 3, submitted: 5, interview: 2, offer: 1 }, topSkills: ['UX/UI', 'Figma', 'Product'], topClients: ['DesignHub', 'InnovateCo'], trend: [5, 7, 8, 6, 9, 10] },
  { id: 5, name: 'Emily Park', submissions: 61, placements: 13, conversion: 21.3, avgTTS: 2.6, avgScore: 86.5, revenue: 1350000, activeReqs: 7, pipeline: { sourced: 10, screening: 5, submitted: 7, interview: 4, offer: 2 }, topSkills: ['Data Science', 'ML', 'Python'], topClients: ['AI Dynamics', 'AnalyticsPro'], trend: [8, 9, 11, 12, 10, 11] },
];

const funnelData = [
  { phase: 'Sourced', count: 580, dropOff: 0, avgDays: 0 },
  { phase: 'Screening', count: 312, dropOff: 46.2, avgDays: 2.8 },
  { phase: 'Submitted', count: 198, dropOff: 36.5, avgDays: 3.2 },
  { phase: 'Interview', count: 124, dropOff: 37.4, avgDays: 5.1 },
  { phase: 'Offer', count: 62, dropOff: 50.0, avgDays: 4.8 },
  { phase: 'Accepted', count: 48, dropOff: 22.6, avgDays: 2.1 },
  { phase: 'Placed', count: 42, dropOff: 12.5, avgDays: 6.5 },
];

const velocityData = [
  { phase: 'Sourced → Screening', avgDays: 2.8, byUrgent: 1.4, byHigh: 2.2, byNormal: 3.8 },
  { phase: 'Screening → Submitted', avgDays: 3.2, byUrgent: 1.8, byHigh: 2.6, byNormal: 4.5 },
  { phase: 'Submitted → Interview', avgDays: 5.1, byUrgent: 2.5, byHigh: 4.2, byNormal: 7.8 },
  { phase: 'Interview → Offer', avgDays: 4.8, byUrgent: 2.2, byHigh: 3.8, byNormal: 7.1 },
  { phase: 'Offer → Accepted', avgDays: 2.1, byUrgent: 1.0, byHigh: 1.8, byNormal: 3.2 },
  { phase: 'Accepted → Placed', avgDays: 6.5, byUrgent: 4.0, byHigh: 5.5, byNormal: 8.8 },
];

// ── Utility Components ──
const ScoreBadge: React.FC<{ value: number; suffix?: string; good?: number; warn?: number }> = ({ value, suffix = '%', good = 80, warn = 60 }) => {
  const color = value >= good ? 'text-emerald-600 bg-emerald-50' : value >= warn ? 'text-amber-600 bg-amber-50' : 'text-red-600 bg-red-50';
  return <span className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold ${color}`}>{typeof value === 'number' ? value.toFixed(1) : value}{suffix}</span>;
};

const formatCurrency = (val: number) => val >= 1000000 ? `$${(val / 1000000).toFixed(1)}M` : `$${(val / 1000).toFixed(0)}K`;

const priorityColors: Record<string, string> = { urgent: 'bg-red-100 text-red-700', high: 'bg-orange-100 text-orange-700', normal: 'bg-blue-100 text-blue-700', low: 'bg-gray-100 text-gray-600' };

// ── SVG Bar Chart ──
const BarChart: React.FC<{ data: { label: string; value: number; color: string }[]; maxValue?: number; height?: number }> = ({ data, maxValue, height = 120 }) => {
  const max = maxValue || Math.max(...data.map(d => d.value));
  const barWidth = Math.min(40, (300 - data.length * 4) / data.length);
  const chartWidth = data.length * (barWidth + 8) + 20;
  return (
    <svg width="100%" height={height + 30} viewBox={`0 0 ${chartWidth} ${height + 30}`} className="overflow-visible">
      {data.map((d, i) => {
        const barHeight = max > 0 ? (d.value / max) * height : 0;
        const x = i * (barWidth + 8) + 10;
        return (
          <g key={i}>
            <rect x={x} y={height - barHeight} width={barWidth} height={barHeight} className={d.color} rx={3} />
            <text x={x + barWidth / 2} y={height - barHeight - 4} textAnchor="middle" className="text-[8px] fill-neutral-600 font-medium">{d.value}</text>
            <text x={x + barWidth / 2} y={height + 14} textAnchor="middle" className="text-[7px] fill-neutral-500">{d.label}</text>
          </g>
        );
      })}
    </svg>
  );
};

// ══════════════════════════════════════════════
// REPORT VIEWS
// ══════════════════════════════════════════════

const ClientReport: React.FC = () => (
  <div className="space-y-4">
    {/* Summary Cards */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[
        { label: 'Total Clients', value: clientData.length, icon: BuildingOffice2Icon },
        { label: 'Active Jobs', value: clientData.reduce((s, c) => s + c.active, 0), icon: BriefcaseIcon },
        { label: 'Total Placements', value: clientData.reduce((s, c) => s + c.placements, 0), icon: CheckCircleIcon },
        { label: 'Total Revenue', value: formatCurrency(clientData.reduce((s, c) => s + c.spend, 0)), icon: CurrencyDollarIcon },
      ].map(m => (
        <div key={m.label} className="bg-white rounded-xl border border-neutral-200 p-4">
          <div className="flex items-center gap-2 mb-2"><m.icon className="w-4 h-4 text-neutral-400" /><span className="text-xs text-neutral-500">{m.label}</span></div>
          <p className="text-xl font-bold text-neutral-900">{m.value}</p>
        </div>
      ))}
    </div>
    {/* Table */}
    <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
      <table className="w-full">
        <thead><tr className="bg-neutral-50 border-b border-neutral-200">
          {['Client', 'Jobs', 'Active', 'Submissions', 'Interviews', 'Placements', 'Fill Rate', 'Avg TTF', 'Match Score', 'Spend', 'Rating'].map(h => (
            <th key={h} className="text-left px-3 py-2.5 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{h}</th>
          ))}
        </tr></thead>
        <tbody className="divide-y divide-neutral-100">
          {clientData.map(c => (
            <tr key={c.id} className="hover:bg-blue-50/40">
              <td className="px-3 py-2.5 text-sm font-medium text-neutral-900">{c.name}</td>
              <td className="px-3 py-2.5 text-sm text-neutral-700">{c.jobs}</td>
              <td className="px-3 py-2.5 text-sm text-neutral-700">{c.active}</td>
              <td className="px-3 py-2.5 text-sm text-neutral-700">{c.submissions}</td>
              <td className="px-3 py-2.5 text-sm text-neutral-700">{c.interviews}</td>
              <td className="px-3 py-2.5 text-sm font-semibold text-emerald-600">{c.placements}</td>
              <td className="px-3 py-2.5"><ScoreBadge value={c.fillRate} /></td>
              <td className="px-3 py-2.5 text-sm text-neutral-600">{c.ttf}d</td>
              <td className="px-3 py-2.5"><ScoreBadge value={c.matchScore} suffix="" good={85} warn={75} /></td>
              <td className="px-3 py-2.5 text-sm font-medium text-neutral-700">{formatCurrency(c.spend)}</td>
              <td className="px-3 py-2.5"><span className="flex items-center gap-1 text-sm"><StarIcon className="w-3.5 h-3.5 text-amber-400" />{c.satisfaction}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const JobReport: React.FC<{ role: UserRole }> = ({ role }) => {
  const data = role === 'company_recruiter' ? jobData.slice(0, 4) : jobData;
  return (
    <div className="space-y-4">
      {role === 'company_recruiter' && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-2.5 text-xs text-amber-700">Showing only your assigned jobs ({data.length} of {jobData.length})</div>
      )}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden overflow-x-auto">
        <table className="w-full min-w-[900px]">
          <thead><tr className="bg-neutral-50 border-b border-neutral-200">
            {['Job', 'Client', 'Priority', 'Rate', 'Applicants', 'Sourced', 'Screen', 'Submit', 'Interview', 'Offer', 'Placed', 'Rejected', 'Conv %', 'Days Open'].map(h => (
              <th key={h} className="text-left px-2.5 py-2.5 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {data.map(j => (
              <tr key={j.id} className="hover:bg-blue-50/40">
                <td className="px-2.5 py-2"><p className="text-xs font-semibold text-neutral-900">{j.title}</p><p className="text-[10px] text-neutral-500">{j.id}</p></td>
                <td className="px-2.5 py-2 text-xs text-neutral-700">{j.client}</td>
                <td className="px-2.5 py-2"><span className={`px-2 py-0.5 rounded-full text-[10px] font-medium capitalize ${priorityColors[j.priority]}`}>{j.priority}</span></td>
                <td className="px-2.5 py-2 text-xs font-medium text-emerald-600">{j.rate}</td>
                <td className="px-2.5 py-2 text-xs font-bold text-neutral-800">{j.applicants}</td>
                <td className="px-2.5 py-2 text-xs text-slate-600">{j.sourced}</td>
                <td className="px-2.5 py-2 text-xs text-blue-600">{j.screening}</td>
                <td className="px-2.5 py-2 text-xs text-indigo-600">{j.submitted}</td>
                <td className="px-2.5 py-2 text-xs text-amber-600">{j.interview}</td>
                <td className="px-2.5 py-2 text-xs text-purple-600">{j.offer}</td>
                <td className="px-2.5 py-2 text-xs font-bold text-emerald-600">{j.placed}</td>
                <td className="px-2.5 py-2 text-xs text-red-500">{j.rejected}</td>
                <td className="px-2.5 py-2"><ScoreBadge value={j.conversion} suffix="%" good={10} warn={5} /></td>
                <td className="px-2.5 py-2 text-xs text-neutral-600">{j.daysOpen}d</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const SupplierReport: React.FC = () => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[
        { label: 'Total Suppliers', value: supplierData.length },
        { label: 'Total Placements', value: supplierData.reduce((s, v) => s + v.placements, 0) },
        { label: 'Avg Fill Rate', value: (supplierData.reduce((s, v) => s + v.fillRate, 0) / supplierData.length).toFixed(1) + '%' },
        { label: 'Total Revenue', value: formatCurrency(supplierData.reduce((s, v) => s + v.revenue, 0)) },
      ].map(m => (
        <div key={m.label} className="bg-white rounded-xl border border-neutral-200 p-4">
          <span className="text-xs text-neutral-500">{m.label}</span>
          <p className="text-xl font-bold text-neutral-900 mt-1">{m.value}</p>
        </div>
      ))}
    </div>
    <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden overflow-x-auto">
      <table className="w-full min-w-[1000px]">
        <thead><tr className="bg-neutral-50 border-b border-neutral-200">
          {['Supplier', 'Candidates', 'Placements', 'Fill Rate', 'Avg Score', 'Avg TTS', 'Reject %', 'I2O %', 'Quality', 'Compliance', 'Revenue', 'SLA'].map(h => (
            <th key={h} className="text-left px-2.5 py-2.5 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{h}</th>
          ))}
        </tr></thead>
        <tbody className="divide-y divide-neutral-100">
          {supplierData.map(s => (
            <tr key={s.id} className="hover:bg-blue-50/40">
              <td className="px-2.5 py-2.5 text-sm font-medium text-neutral-900">{s.name}</td>
              <td className="px-2.5 py-2.5 text-sm text-neutral-700">{s.candidates}</td>
              <td className="px-2.5 py-2.5 text-sm font-semibold text-emerald-600">{s.placements}</td>
              <td className="px-2.5 py-2.5"><ScoreBadge value={s.fillRate} good={75} warn={60} /></td>
              <td className="px-2.5 py-2.5"><ScoreBadge value={s.avgScore} suffix="" good={85} warn={75} /></td>
              <td className="px-2.5 py-2.5 text-sm text-neutral-600">{s.avgTTS}d</td>
              <td className="px-2.5 py-2.5"><ScoreBadge value={s.rejectionRate} suffix="%" good={100 as any} warn={20} /></td>
              <td className="px-2.5 py-2.5"><ScoreBadge value={s.i2o} suffix="%" good={55} warn={40} /></td>
              <td className="px-2.5 py-2.5"><span className="flex items-center gap-1 text-sm"><StarIcon className="w-3.5 h-3.5 text-amber-400" />{s.quality.toFixed(1)}</span></td>
              <td className="px-2.5 py-2.5"><ScoreBadge value={s.compliance} good={95} warn={90} /></td>
              <td className="px-2.5 py-2.5 text-sm font-medium text-neutral-700">{formatCurrency(s.revenue)}</td>
              <td className="px-2.5 py-2.5"><ScoreBadge value={s.sla} good={95} warn={88} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const RecruiterReport: React.FC<{ role: UserRole }> = ({ role }) => {
  const data = role === 'company_recruiter' ? recruiterData.slice(0, 1) : recruiterData;
  return (
    <div className="space-y-4">
      {role === 'company_recruiter' && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-2.5 text-xs text-emerald-700">Showing your personal performance report</div>
      )}
      {data.map(r => (
        <div key={r.id} className="bg-white rounded-xl border border-neutral-200 p-5">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-700">{r.name.split(' ').map(n => n[0]).join('')}</div>
              <div>
                <h4 className="text-sm font-bold text-neutral-900">{r.name}</h4>
                <p className="text-xs text-neutral-500">{r.activeReqs} active requisitions</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-emerald-600">{formatCurrency(r.revenue)}</p>
              <p className="text-[10px] text-neutral-500">Revenue Generated</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
            {[
              { label: 'Submissions', value: r.submissions },
              { label: 'Placements', value: r.placements },
              { label: 'Conversion', value: r.conversion.toFixed(1) + '%' },
              { label: 'Avg TTS', value: r.avgTTS + 'd' },
              { label: 'Avg Score', value: r.avgScore.toFixed(1) },
            ].map(m => (
              <div key={m.label} className="bg-neutral-50 rounded-lg p-2.5 text-center">
                <p className="text-xs text-neutral-500">{m.label}</p>
                <p className="text-sm font-bold text-neutral-800">{m.value}</p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Pipeline */}
            <div>
              <p className="text-xs font-semibold text-neutral-500 mb-2">Pipeline</p>
              <div className="space-y-1">
                {Object.entries(r.pipeline).map(([phase, count]) => (
                  <div key={phase} className="flex items-center justify-between text-xs">
                    <span className="text-neutral-600 capitalize">{phase}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(count / 15) * 100}%` }} />
                      </div>
                      <span className="text-neutral-800 font-medium w-4 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            {/* Monthly Trend */}
            <div>
              <p className="text-xs font-semibold text-neutral-500 mb-2">6-Month Trend</p>
              <BarChart data={r.trend.map((v, i) => ({ label: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'][i], value: v, color: 'fill-blue-400' }))} height={60} />
            </div>
            {/* Top Skills & Clients */}
            <div>
              <p className="text-xs font-semibold text-neutral-500 mb-2">Specialization</p>
              <div className="flex flex-wrap gap-1 mb-2">
                {r.topSkills.map(s => <span key={s} className="px-2 py-0.5 rounded bg-blue-50 text-blue-600 text-[10px] font-medium">{s}</span>)}
              </div>
              <p className="text-[10px] text-neutral-500 mt-1">Top Clients:</p>
              <div className="flex flex-wrap gap-1">
                {r.topClients.map(c => <span key={c} className="px-2 py-0.5 rounded bg-neutral-100 text-neutral-600 text-[10px]">{c}</span>)}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const CompanyExecutive: React.FC = () => {
  const totalPlacements = clientData.reduce((s, c) => s + c.placements, 0);
  const totalRevenue = clientData.reduce((s, c) => s + c.spend, 0);
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Jobs', value: clientData.reduce((s, c) => s + c.active, 0), delta: '+12% MoM' },
          { label: 'Pipeline Candidates', value: 580, delta: '+8% MoM' },
          { label: 'Placements YTD', value: totalPlacements, delta: '+15% vs LY' },
          { label: 'Avg Time-to-Fill', value: '22.8d', delta: '-3.2d vs LQ' },
        ].map(m => (
          <div key={m.label} className="bg-white rounded-xl border border-neutral-200 p-4">
            <span className="text-xs text-neutral-500">{m.label}</span>
            <p className="text-xl font-bold text-neutral-900 mt-1">{m.value}</p>
            <span className="text-[10px] font-medium text-emerald-600">{m.delta}</span>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Top Clients */}
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Top Clients by Placements</h4>
          <div className="space-y-2">
            {[...clientData].sort((a, b) => b.placements - a.placements).slice(0, 5).map((c, i) => (
              <div key={c.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center">{i + 1}</span>
                  <span className="text-sm text-neutral-700">{c.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-emerald-600">{c.placements}</span>
                  <div className="w-20 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${(c.placements / 11) * 100}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* Top Suppliers */}
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Top Suppliers by Fill Rate</h4>
          <div className="space-y-2">
            {[...supplierData].sort((a, b) => b.fillRate - a.fillRate).slice(0, 5).map((s, i) => (
              <div key={s.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-purple-100 text-purple-700 text-[10px] font-bold flex items-center justify-center">{i + 1}</span>
                  <span className="text-sm text-neutral-700">{s.name}</span>
                </div>
                <ScoreBadge value={s.fillRate} good={75} warn={65} />
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Revenue */}
      <div className="bg-white rounded-xl border border-neutral-200 p-4">
        <h4 className="text-sm font-semibold text-neutral-700 mb-3">Revenue by Client</h4>
        <BarChart data={clientData.map(c => ({ label: c.name.split(' ')[0], value: Math.round(c.spend / 1000), color: 'fill-blue-400' }))} height={100} />
        <p className="text-[10px] text-neutral-500 mt-1 text-center">Revenue in $K</p>
      </div>
    </div>
  );
};

const PipelineVelocity: React.FC = () => (
  <div className="space-y-4">
    <div className="bg-white rounded-xl border border-neutral-200 p-5">
      <h4 className="text-sm font-semibold text-neutral-700 mb-4">Average Days per Phase Transition</h4>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead><tr className="border-b border-neutral-200">
            {['Phase Transition', 'Avg Days', 'Urgent', 'High', 'Normal', 'Bottleneck?'].map(h => (
              <th key={h} className="text-left px-3 py-2.5 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {velocityData.map(v => {
              const isBottleneck = v.avgDays >= 5;
              return (
                <tr key={v.phase} className="hover:bg-neutral-50">
                  <td className="px-3 py-2.5 text-sm font-medium text-neutral-800">{v.phase}</td>
                  <td className="px-3 py-2.5"><span className={`text-sm font-bold ${isBottleneck ? 'text-red-600' : 'text-neutral-800'}`}>{v.avgDays}d</span></td>
                  <td className="px-3 py-2.5 text-sm text-red-600 font-medium">{v.byUrgent}d</td>
                  <td className="px-3 py-2.5 text-sm text-orange-600 font-medium">{v.byHigh}d</td>
                  <td className="px-3 py-2.5 text-sm text-blue-600 font-medium">{v.byNormal}d</td>
                  <td className="px-3 py-2.5">{isBottleneck && <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-red-50 text-red-600 text-[10px] font-medium"><ExclamationTriangleIcon className="w-3 h-3" />Bottleneck</span>}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
    <div className="bg-white rounded-xl border border-neutral-200 p-5">
      <h4 className="text-sm font-semibold text-neutral-700 mb-3">Total Pipeline Time (Sourced → Placed)</h4>
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Urgent', value: velocityData.reduce((s, v) => s + v.byUrgent, 0).toFixed(1), color: 'text-red-600 bg-red-50' },
          { label: 'High', value: velocityData.reduce((s, v) => s + v.byHigh, 0).toFixed(1), color: 'text-orange-600 bg-orange-50' },
          { label: 'Normal', value: velocityData.reduce((s, v) => s + v.byNormal, 0).toFixed(1), color: 'text-blue-600 bg-blue-50' },
        ].map(m => (
          <div key={m.label} className={`rounded-xl p-4 text-center ${m.color}`}>
            <p className="text-xs font-medium opacity-70">{m.label} Priority</p>
            <p className="text-2xl font-bold mt-1">{m.value} days</p>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const ConversionFunnel: React.FC = () => {
  const maxCount = funnelData[0].count;
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-neutral-200 p-5">
        <h4 className="text-sm font-semibold text-neutral-700 mb-4">Hiring Funnel</h4>
        <div className="space-y-2">
          {funnelData.map((f, i) => {
            const width = (f.count / maxCount) * 100;
            const colors = ['bg-slate-400', 'bg-blue-400', 'bg-indigo-400', 'bg-amber-400', 'bg-purple-400', 'bg-teal-400', 'bg-emerald-500'];
            return (
              <div key={f.phase}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-neutral-700">{f.phase}</span>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="font-bold text-neutral-800">{f.count}</span>
                    {f.dropOff > 0 && <span className="text-red-500">-{f.dropOff}% drop</span>}
                    {f.avgDays > 0 && <span className="text-neutral-500">~{f.avgDays}d</span>}
                  </div>
                </div>
                <div className="w-full h-6 bg-neutral-100 rounded-lg overflow-hidden flex items-center">
                  <div className={`h-full ${colors[i]} rounded-lg transition-all`} style={{ width: `${width}%` }}>
                    <span className="text-[10px] text-white font-medium pl-2 leading-6">{width.toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="bg-white rounded-xl border border-neutral-200 p-5">
        <h4 className="text-sm font-semibold text-neutral-700 mb-3">Overall Conversion</h4>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-blue-50 rounded-xl p-4">
            <p className="text-xs text-blue-600">Sourced → Placed</p>
            <p className="text-2xl font-bold text-blue-700">{((42 / 580) * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-amber-50 rounded-xl p-4">
            <p className="text-xs text-amber-600">Interview → Placed</p>
            <p className="text-2xl font-bold text-amber-700">{((42 / 124) * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-emerald-50 rounded-xl p-4">
            <p className="text-xs text-emerald-600">Offer → Placed</p>
            <p className="text-2xl font-bold text-emerald-700">{((42 / 62) * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const CrossDimensional: React.FC = () => {
  const clientSupplierMatrix = [
    { client: 'TechCorp', tf: 3, ps: 2, eh: 1, st: 0, ng: 1, cs: 1 },
    { client: 'CloudNine', tf: 2, ps: 1, eh: 2, st: 0, ng: 1, cs: 0 },
    { client: 'AnalyticsPro', tf: 1, ps: 1, eh: 0, st: 1, ng: 1, cs: 0 },
    { client: 'GlobalFinance', tf: 4, ps: 2, eh: 2, st: 1, ng: 1, cs: 1 },
    { client: 'InnovateCo', tf: 2, ps: 1, eh: 1, st: 1, ng: 2, cs: 0 },
  ];
  const suppliers = ['TF', 'PS', 'EH', 'ST', 'NG', 'CS'];
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-neutral-200 p-5">
        <h4 className="text-sm font-semibold text-neutral-700 mb-4">Client x Supplier Placements Matrix</h4>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead><tr className="border-b border-neutral-200">
              <th className="text-left px-3 py-2 text-[10px] font-semibold text-neutral-500">Client \ Supplier</th>
              {suppliers.map(s => <th key={s} className="text-center px-3 py-2 text-[10px] font-semibold text-neutral-500">{s}</th>)}
            </tr></thead>
            <tbody className="divide-y divide-neutral-100">
              {clientSupplierMatrix.map(row => (
                <tr key={row.client}>
                  <td className="px-3 py-2 text-xs font-medium text-neutral-800">{row.client}</td>
                  {[row.tf, row.ps, row.eh, row.st, row.ng, row.cs].map((v, i) => (
                    <td key={i} className="px-3 py-2 text-center">
                      {v > 0 ? (
                        <span className={`inline-flex w-6 h-6 items-center justify-center rounded text-[10px] font-bold ${v >= 3 ? 'bg-emerald-100 text-emerald-700' : v >= 2 ? 'bg-blue-100 text-blue-700' : 'bg-neutral-100 text-neutral-600'}`}>{v}</span>
                      ) : <span className="text-neutral-300">-</span>}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-[10px] text-neutral-400 mt-2">TF=TalentForce, PS=PrimeStaff, EH=EliteHire, ST=SwiftTalent, NG=NexGen, CS=CoreStaff</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Priority x Avg Time-to-Fill</h4>
          <div className="space-y-2">
            {[
              { priority: 'Urgent', ttf: 12.9, color: 'bg-red-400' },
              { priority: 'High', ttf: 20.1, color: 'bg-orange-400' },
              { priority: 'Normal', ttf: 35.2, color: 'bg-blue-400' },
            ].map(p => (
              <div key={p.priority} className="flex items-center gap-3">
                <span className="text-xs text-neutral-600 w-14">{p.priority}</span>
                <div className="flex-1 h-4 bg-neutral-100 rounded-full overflow-hidden">
                  <div className={`h-full ${p.color} rounded-full`} style={{ width: `${(p.ttf / 40) * 100}%` }} />
                </div>
                <span className="text-xs font-bold text-neutral-800 w-10 text-right">{p.ttf}d</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Source x Conversion Rate</h4>
          <div className="space-y-2">
            {[
              { source: 'Referral', rate: 18.5, color: 'bg-emerald-400' },
              { source: 'Direct', rate: 14.2, color: 'bg-blue-400' },
              { source: 'LinkedIn', rate: 8.7, color: 'bg-indigo-400' },
              { source: 'Job Board', rate: 5.3, color: 'bg-amber-400' },
            ].map(s => (
              <div key={s.source} className="flex items-center gap-3">
                <span className="text-xs text-neutral-600 w-16">{s.source}</span>
                <div className="flex-1 h-4 bg-neutral-100 rounded-full overflow-hidden">
                  <div className={`h-full ${s.color} rounded-full`} style={{ width: `${(s.rate / 20) * 100}%` }} />
                </div>
                <span className="text-xs font-bold text-neutral-800 w-10 text-right">{s.rate}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ══════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════

export const AggregateReports: React.FC = () => {
  const [activeRole, setActiveRole] = useState<UserRole>('msp_admin');
  const [activeTab, setActiveTab] = useState('by_client');
  const [dateRange, setDateRange] = useState({ start: '2026-01-01', end: '2026-03-08' });

  const availableTabs = REPORT_TABS.filter(t => t.roles.includes(activeRole));

  // If current tab isn't available for new role, switch to first available
  const effectiveTab = availableTabs.find(t => t.key === activeTab) ? activeTab : availableTabs[0]?.key || 'by_job';

  const renderReport = () => {
    switch (effectiveTab) {
      case 'by_client': return <ClientReport />;
      case 'by_job': return <JobReport role={activeRole} />;
      case 'by_supplier': return <SupplierReport />;
      case 'by_recruiter': return <RecruiterReport role={activeRole} />;
      case 'by_company': return <CompanyExecutive />;
      case 'pipeline_velocity': return <PipelineVelocity />;
      case 'conversion_funnel': return <ConversionFunnel />;
      case 'cross_dimensional': return <CrossDimensional />;
      default: return null;
    }
  };

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Aggregate Reports</h1>
          <p className="text-sm text-neutral-500 mt-1">Cross-dimensional performance analytics by client, job, supplier, and recruiter</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-neutral-500">
            <CalendarDaysIcon className="w-4 h-4" />
            <input type="date" value={dateRange.start} onChange={e => setDateRange(p => ({ ...p, start: e.target.value }))} className="px-2 py-1 border border-neutral-200 rounded text-xs" />
            <span>to</span>
            <input type="date" value={dateRange.end} onChange={e => setDateRange(p => ({ ...p, end: e.target.value }))} className="px-2 py-1 border border-neutral-200 rounded text-xs" />
          </div>
        </div>
      </div>

      {/* Role Selector */}
      <div className="mb-6">
        <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Viewing as</p>
        <div className="flex items-center gap-2">
          {(Object.keys(ROLE_CONFIG) as UserRole[]).map(role => {
            const conf = ROLE_CONFIG[role];
            const isActive = activeRole === role;
            const tabCount = REPORT_TABS.filter(t => t.roles.includes(role)).length;
            return (
              <button key={role} onClick={() => setActiveRole(role)} className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium border transition-all ${isActive ? conf.bgColor + ' border-current ' + conf.color : 'bg-white border-neutral-200 text-neutral-500 hover:border-neutral-300'}`}>
                <ShieldExclamationIcon className="w-4 h-4" />
                {conf.label}
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${isActive ? 'bg-white/60' : 'bg-neutral-100'}`}>{tabCount} reports</span>
              </button>
            );
          })}
        </div>
        <p className="text-xs text-neutral-400 mt-1.5">{ROLE_CONFIG[activeRole].description}</p>
      </div>

      {/* Report Tabs */}
      <div className="flex items-center gap-1 bg-neutral-100 rounded-lg p-1 mb-6 overflow-x-auto">
        {availableTabs.map(tab => {
          const TabIcon = tab.icon;
          const isActive = effectiveTab === tab.key;
          return (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)} className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-medium whitespace-nowrap transition-all ${isActive ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'}`}>
              <TabIcon className="w-3.5 h-3.5" /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Report Content */}
      {renderReport()}
    </div>
  );
};
