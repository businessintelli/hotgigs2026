import React, { useState } from 'react';
import {
  EnvelopeIcon,
  BellIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  EyeIcon,
  ClockIcon,
  PaperAirplaneIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

// ── Types ──
interface EmailLog {
  id: number;
  candidate_name: string;
  candidate_email: string;
  job_title: string;
  notification_type: string;
  subject: string;
  status: 'sent' | 'delivered' | 'opened' | 'failed';
  sent_at: string;
  delivered_at: string | null;
  opened_at: string | null;
}

interface EmailTemplate {
  id: number;
  name: string;
  trigger_event: string;
  subject: string;
  preview: string;
  is_active: boolean;
}

// ── Mock Data ──
const CANDIDATES = ['Alex Chen', 'Maya Patel', 'James Wilson', 'Sofia Rodriguez', 'David Kim',
  'Emma Thompson', 'Carlos Rivera', 'Priya Sharma', 'Tyler Johnson', 'Aisha Hassan'];
const TYPES = ['applied', 'screening', 'shortlisted', 'interviewing', 'offered', 'rejected'];
const STATUSES: EmailLog['status'][] = ['sent', 'delivered', 'opened', 'failed'];
const JOBS = ['Senior Python Dev', 'React Lead', 'DevOps Engineer', 'Data Scientist'];

const mockLogs: EmailLog[] = Array.from({ length: 30 }, (_, i) => {
  const name = CANDIDATES[i % CANDIDATES.length];
  const st = STATUSES[Math.floor(Math.random() * 4)];
  const sentDate = new Date(Date.now() - Math.random() * 30 * 86400000);
  return {
    id: i + 1, candidate_name: name,
    candidate_email: `${name.toLowerCase().replace(' ', '.')}@email.com`,
    job_title: JOBS[i % JOBS.length],
    notification_type: TYPES[i % TYPES.length],
    subject: `Application update: ${TYPES[i % TYPES.length]}`,
    status: st, sent_at: sentDate.toISOString(),
    delivered_at: st !== 'failed' ? new Date(sentDate.getTime() + 60000).toISOString() : null,
    opened_at: st === 'opened' ? new Date(sentDate.getTime() + 3600000).toISOString() : null,
  };
});

const mockTemplates: EmailTemplate[] = [
  { id: 1, name: 'Application Received', trigger_event: 'applied', subject: 'Your application for {job_title} has been received', preview: 'Thank you for applying...', is_active: true },
  { id: 2, name: 'Under Review', trigger_event: 'screening', subject: 'Your application is being reviewed', preview: 'Good news! Your application...', is_active: true },
  { id: 3, name: 'Shortlisted', trigger_event: 'shortlisted', subject: 'Congratulations! You\'ve been shortlisted', preview: 'We\'re pleased to inform you...', is_active: true },
  { id: 4, name: 'Interview Scheduled', trigger_event: 'interviewing', subject: 'Interview scheduled for {job_title}', preview: 'Your interview has been scheduled...', is_active: true },
  { id: 5, name: 'Offer Extended', trigger_event: 'offered', subject: 'Offer for {job_title}', preview: 'We\'re excited to extend an offer...', is_active: true },
  { id: 6, name: 'Not Selected', trigger_event: 'rejected', subject: 'Update on your application', preview: 'After careful consideration...', is_active: false },
];

const statusIcon = (s: EmailLog['status']) => {
  switch (s) {
    case 'sent': return <PaperAirplaneIcon className="h-4 w-4 text-blue-500" />;
    case 'delivered': return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
    case 'opened': return <EyeIcon className="h-4 w-4 text-purple-500" />;
    case 'failed': return <ExclamationCircleIcon className="h-4 w-4 text-red-500" />;
  }
};

const statusBadge = (s: EmailLog['status']) => {
  const cls: Record<string, string> = {
    sent: 'bg-blue-100 text-blue-700', delivered: 'bg-green-100 text-green-700',
    opened: 'bg-purple-100 text-purple-700', failed: 'bg-red-100 text-red-700',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${cls[s]}`}>{s}</span>;
};

const typeBadge = (t: string) => {
  const cls: Record<string, string> = {
    applied: 'bg-blue-50 text-blue-600', screening: 'bg-indigo-50 text-indigo-600',
    shortlisted: 'bg-violet-50 text-violet-600', interviewing: 'bg-amber-50 text-amber-600',
    offered: 'bg-emerald-50 text-emerald-600', rejected: 'bg-red-50 text-red-600',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls[t] || 'bg-neutral-100 text-neutral-600'}`}>{t}</span>;
};

export const CandidateNotifications: React.FC = () => {
  const [tab, setTab] = useState<'history' | 'templates' | 'settings' | 'analytics'>('history');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredLogs = mockLogs.filter(l => {
    if (filterType !== 'all' && l.notification_type !== filterType) return false;
    if (filterStatus !== 'all' && l.status !== filterStatus) return false;
    return true;
  });

  // Stats
  const totalSent = mockLogs.length;
  const delivered = mockLogs.filter(l => l.delivered_at).length;
  const opened = mockLogs.filter(l => l.opened_at).length;
  const failed = mockLogs.filter(l => l.status === 'failed').length;

  const tabs = [
    { key: 'history' as const, label: 'Email History', icon: EnvelopeIcon },
    { key: 'templates' as const, label: 'Templates', icon: DocumentTextIcon },
    { key: 'analytics' as const, label: 'Analytics', icon: ChartBarIcon },
    { key: 'settings' as const, label: 'Settings', icon: Cog6ToothIcon },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
          <BellIcon className="h-6 w-6 text-blue-600" />
          Candidate Notifications
        </h1>
        <p className="text-sm text-neutral-500 mt-1">Auto-notify candidates when their status changes in the pipeline</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Sent', value: totalSent, icon: PaperAirplaneIcon, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Delivered', value: `${delivered} (${totalSent ? Math.round((delivered / totalSent) * 100) : 0}%)`, icon: CheckCircleIcon, color: 'text-green-600', bg: 'bg-green-50' },
          { label: 'Opened', value: `${opened} (${totalSent ? Math.round((opened / totalSent) * 100) : 0}%)`, icon: EyeIcon, color: 'text-purple-600', bg: 'bg-purple-50' },
          { label: 'Failed', value: failed, icon: ExclamationCircleIcon, color: 'text-red-600', bg: 'bg-red-50' },
        ].map((kpi) => {
          const KIcon = kpi.icon;
          return (
            <div key={kpi.label} className="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
              <div className={`${kpi.bg} p-2 rounded-lg`}><KIcon className={`h-5 w-5 ${kpi.color}`} /></div>
              <div>
                <p className="text-xs text-neutral-500">{kpi.label}</p>
                <p className={`text-lg font-bold ${kpi.color}`}>{kpi.value}</p>
              </div>
            </div>
          );
        })}
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

      {/* ── HISTORY TAB ── */}
      {tab === 'history' && (
        <div className="bg-white rounded-xl border border-neutral-200">
          <div className="p-4 border-b flex items-center gap-3">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="border rounded-lg px-3 py-1.5 text-sm"
            >
              <option value="all">All Types</option>
              {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="border rounded-lg px-3 py-1.5 text-sm"
            >
              <option value="all">All Statuses</option>
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <span className="text-xs text-neutral-400 ml-auto">{filteredLogs.length} results</span>
          </div>
          <table className="w-full">
            <thead>
              <tr className="text-xs text-neutral-500 border-b bg-neutral-50">
                <th className="text-left py-2 px-4 font-medium">Candidate</th>
                <th className="text-left py-2 px-4 font-medium">Job</th>
                <th className="text-center py-2 px-4 font-medium">Type</th>
                <th className="text-left py-2 px-4 font-medium">Subject</th>
                <th className="text-center py-2 px-4 font-medium">Status</th>
                <th className="text-center py-2 px-4 font-medium">Sent</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.slice(0, 20).map((log) => (
                <tr key={log.id} className="border-b last:border-0 hover:bg-neutral-50">
                  <td className="py-3 px-4">
                    <p className="text-sm font-medium text-neutral-800">{log.candidate_name}</p>
                    <p className="text-xs text-neutral-400">{log.candidate_email}</p>
                  </td>
                  <td className="py-3 px-4 text-sm text-neutral-600">{log.job_title}</td>
                  <td className="py-3 px-4 text-center">{typeBadge(log.notification_type)}</td>
                  <td className="py-3 px-4 text-sm text-neutral-600 max-w-xs truncate">{log.subject}</td>
                  <td className="py-3 px-4 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      {statusIcon(log.status)}
                      {statusBadge(log.status)}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center text-xs text-neutral-400">
                    <ClockIcon className="h-3.5 w-3.5 inline mr-1" />
                    {new Date(log.sent_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── TEMPLATES TAB ── */}
      {tab === 'templates' && (
        <div className="space-y-4">
          {mockTemplates.map((tmpl) => (
            <div key={tmpl.id} className={`bg-white rounded-xl border p-5 ${tmpl.is_active ? 'border-neutral-200' : 'border-dashed border-neutral-300 opacity-60'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${tmpl.is_active ? 'bg-blue-50' : 'bg-neutral-100'}`}>
                    <EnvelopeIcon className={`h-5 w-5 ${tmpl.is_active ? 'text-blue-600' : 'text-neutral-400'}`} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-neutral-800">{tmpl.name}</p>
                    <p className="text-xs text-neutral-500 mt-0.5">Trigger: {typeBadge(tmpl.trigger_event)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    tmpl.is_active ? 'bg-green-100 text-green-700' : 'bg-neutral-100 text-neutral-500'
                  }`}>
                    {tmpl.is_active ? 'Active' : 'Disabled'}
                  </span>
                  <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">Edit</button>
                </div>
              </div>
              <div className="mt-3 bg-neutral-50 rounded-lg p-3">
                <p className="text-xs text-neutral-500">Subject:</p>
                <p className="text-sm text-neutral-700 font-medium mt-0.5">{tmpl.subject}</p>
                <p className="text-xs text-neutral-500 mt-2">Preview:</p>
                <p className="text-sm text-neutral-600 mt-0.5">{tmpl.preview}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── ANALYTICS TAB ── */}
      {tab === 'analytics' && (
        <div className="space-y-6">
          {/* Delivery Funnel */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4">Email Delivery Funnel</h3>
            <div className="space-y-3">
              {[
                { label: 'Sent', count: totalSent, pct: 100, color: 'bg-blue-500' },
                { label: 'Delivered', count: delivered, pct: Math.round((delivered / totalSent) * 100), color: 'bg-green-500' },
                { label: 'Opened', count: opened, pct: Math.round((opened / totalSent) * 100), color: 'bg-purple-500' },
              ].map((step) => (
                <div key={step.label} className="flex items-center gap-3">
                  <div className="w-20 text-sm font-medium text-neutral-700 text-right">{step.label}</div>
                  <div className="flex-1 bg-neutral-100 rounded-full h-7 overflow-hidden">
                    <div className={`${step.color} h-full rounded-full flex items-center justify-end pr-3`} style={{ width: `${step.pct}%` }}>
                      <span className="text-xs font-bold text-white">{step.count}</span>
                    </div>
                  </div>
                  <div className="w-12 text-sm text-neutral-500 text-right">{step.pct}%</div>
                </div>
              ))}
            </div>
          </div>

          {/* By Type Breakdown */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4">Notifications by Type</h3>
            <div className="grid grid-cols-3 gap-3">
              {TYPES.map((t) => {
                const count = mockLogs.filter(l => l.notification_type === t).length;
                return (
                  <div key={t} className="bg-neutral-50 rounded-lg p-3 text-center">
                    <div className="mb-1">{typeBadge(t)}</div>
                    <p className="text-2xl font-bold text-neutral-800 mt-2">{count}</p>
                    <p className="text-xs text-neutral-400">emails sent</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── SETTINGS TAB ── */}
      {tab === 'settings' && (
        <div className="bg-white rounded-xl border border-neutral-200 p-6 space-y-6">
          <h3 className="text-sm font-semibold text-neutral-700">Notification Settings</h3>
          {[
            { label: 'Auto-notify on status change', desc: 'Automatically send emails when candidate status changes', checked: true },
            { label: 'CC hiring manager', desc: 'Include hiring manager on all candidate notifications', checked: false },
            { label: 'Daily digest for recruiters', desc: 'Send a daily summary of all notifications sent', checked: true },
            { label: 'Include company branding', desc: 'Use branded email templates with logo and colors', checked: true },
          ].map((setting) => (
            <div key={setting.label} className="flex items-center justify-between py-3 border-b last:border-0">
              <div>
                <p className="text-sm font-medium text-neutral-800">{setting.label}</p>
                <p className="text-xs text-neutral-500 mt-0.5">{setting.desc}</p>
              </div>
              <div className={`w-10 h-6 rounded-full relative cursor-pointer transition-colors ${setting.checked ? 'bg-blue-500' : 'bg-neutral-300'}`}>
                <div className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-transform ${setting.checked ? 'translate-x-5' : 'translate-x-1'}`} />
              </div>
            </div>
          ))}

          <div className="mt-4">
            <p className="text-sm font-medium text-neutral-700 mb-2">Enabled Events</p>
            <div className="flex flex-wrap gap-2">
              {TYPES.map((t) => (
                <label key={t} className="flex items-center gap-2 bg-neutral-50 rounded-lg px-3 py-2 cursor-pointer">
                  <input type="checkbox" defaultChecked={t !== 'rejected'} className="rounded text-blue-600" />
                  <span className="text-sm text-neutral-700 capitalize">{t}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
