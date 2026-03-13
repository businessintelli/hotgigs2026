import React, { useState, useEffect } from 'react';

interface Email {
  id: number; from_address: string; from_name: string | null; subject: string;
  body_text: string | null; received_at: string; is_read: boolean;
  has_attachments: boolean; attachment_count: number;
  classification: string | null; priority: string | null;
  confidence_score: number | null; ai_summary: string | null;
  requires_response: boolean; is_user_in_cc_only: boolean;
  sentiment: string | null; classification_tags: string[] | null;
  draft_generated: boolean; alert_sent: boolean;
  resume_processed: boolean; action_items_extracted: boolean;
}
interface Draft {
  id: number; email_message_id: number; draft_subject: string;
  draft_body: string; draft_tone: string; status: string;
  ai_reasoning: string | null; confidence_score: number | null; created_at: string;
}
interface ActionItem {
  id: number; title: string; assigned_to_name: string | null;
  due_date: string | null; priority: string; status: string;
  is_escalation: boolean; source: string;
}

const classIcons: Record<string, string> = {
  escalation_urgent: '🚨', candidate_application: '📄', interview_request: '📅',
  interview_reschedule: '🔄', onboarding_related: '✅', offboarding_related: '👋',
  meeting_minutes: '📝', timesheet_approval: '⏱️', fyi_cc: '📰',
  general: '📧', newsletter: '📰', invoice_related: '💰', spam: '🚫',
};
const priorityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  low: 'bg-green-100 text-green-700 border-green-200',
  fyi: 'bg-gray-100 text-gray-600 border-gray-200',
};
const statusColors: Record<string, string> = {
  generated: 'bg-purple-100 text-purple-700', reviewed: 'bg-blue-100 text-blue-700',
  sent: 'bg-green-100 text-green-700', discarded: 'bg-gray-100 text-gray-500',
  pending: 'bg-yellow-100 text-yellow-700', in_progress: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700', escalated: 'bg-red-100 text-red-700',
};

const mockDashboard = {
  total_emails_today: 8, action_required: 4, escalations: 1,
  fyi_emails: 2, resumes_captured: 2, drafts_generated: 5,
  action_items_pending: 7, alerts_sent_today: 3,
  response_rate: 0.85, avg_response_time_hours: 1.2,
};

export function EmailAgentCenter() {
  const [tab, setTab] = useState<'dashboard' | 'inbox' | 'drafts' | 'actions'>('dashboard');
  const [emails, setEmails] = useState<Email[]>([]);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [dashboard, setDashboard] = useState(mockDashboard);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [classFilter, setClassFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');

  useEffect(() => {
    const base = '/api/v1/email-agent';
    const base2 = '/api/v1/mom-actions';
    Promise.all([
      fetch(`${base}/inbox`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/drafts`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base2}/actions`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/dashboard`).then(r => r.ok ? r.json() : mockDashboard),
    ]).then(([inbox, dr, act, dash]) => {
      setEmails(inbox.items || []);
      setDrafts(dr.items || []);
      setActions(act.items || []);
      setDashboard(dash.total_emails_today ? dash : mockDashboard);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const filteredEmails = emails.filter(e =>
    (classFilter === 'all' || e.classification === classFilter) &&
    (priorityFilter === 'all' || e.priority === priorityFilter)
  );

  const tabs = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'inbox', label: 'Smart Inbox', count: emails.filter(e => !e.is_read).length },
    { key: 'drafts', label: 'AI Drafts', count: drafts.filter(d => d.status === 'generated').length },
    { key: 'actions', label: 'Action Items', count: actions.filter(a => a.status !== 'completed').length },
  ] as const;

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
    </div>
  );

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email Agent Command Center</h1>
          <p className="text-sm text-gray-500 mt-1">AI-powered email reading, classification, response drafting & action extraction</p>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
            Sync Now
          </button>
          <button className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50">
            Agent Settings
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-6">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}>
              {t.label}
              {'count' in t && t.count > 0 && (
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${t.key === 'actions' ? 'bg-orange-100 text-orange-700' : 'bg-indigo-100 text-indigo-700'}`}>{t.count}</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* ─── Dashboard Tab ─── */}
      {tab === 'dashboard' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {[
              { label: 'Emails Today', value: dashboard.total_emails_today, color: 'bg-indigo-50 text-indigo-700' },
              { label: 'Action Required', value: dashboard.action_required, color: 'bg-orange-50 text-orange-700' },
              { label: 'Escalations', value: dashboard.escalations, color: 'bg-red-50 text-red-700' },
              { label: 'FYI/CC', value: dashboard.fyi_emails, color: 'bg-gray-50 text-gray-700' },
              { label: 'Resumes Found', value: dashboard.resumes_captured, color: 'bg-green-50 text-green-700' },
              { label: 'Drafts Ready', value: dashboard.drafts_generated, color: 'bg-purple-50 text-purple-700' },
              { label: 'Action Items', value: dashboard.action_items_pending, color: 'bg-yellow-50 text-yellow-700' },
              { label: 'Alerts Sent', value: dashboard.alerts_sent_today, color: 'bg-blue-50 text-blue-700' },
            ].map(kpi => (
              <div key={kpi.label} className={`rounded-xl p-3 ${kpi.color}`}>
                <p className="text-[10px] font-medium opacity-70 uppercase">{kpi.label}</p>
                <p className="text-xl font-bold mt-1">{kpi.value}</p>
              </div>
            ))}
          </div>

          {/* Agent Activity Feed */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Agent Activity</h3>
              <div className="space-y-3">
                {[
                  { icon: '🚨', text: 'Escalation detected: Java Developer SLA Risk → Alerts sent to Slack + WhatsApp', time: '08:16 AM', type: 'critical' },
                  { icon: '📄', text: 'Resume parsed: Priya Sharma (Python Dev) → Match score: 87.5% → Added to platform', time: '07:32 AM', type: 'success' },
                  { icon: '✏️', text: '5 draft responses generated for action-required emails', time: '07:30 AM', type: 'info' },
                  { icon: '📝', text: 'MOM extracted: Q1 Workforce Planning → 4 action items created', time: 'Yesterday', type: 'info' },
                  { icon: '📊', text: 'Daily summary delivered to Slack #recruiting-general', time: '09:00 AM', type: 'info' },
                ].map((a, i) => (
                  <div key={i} className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50">
                    <span className="text-lg mt-0.5">{a.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-700">{a.text}</p>
                      <p className="text-xs text-gray-400 mt-0.5">{a.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">How the Email Agent Works</h3>
              <div className="space-y-4 text-xs text-gray-600">
                {[
                  { step: '1', title: 'Email Ingestion', desc: 'Connects to Gmail/Outlook, syncs inbox in real-time' },
                  { step: '2', title: 'AI Classification', desc: 'Classifies each email: escalation, application, interview, MOM, FYI, etc.' },
                  { step: '3', title: 'Smart Actions', desc: 'Drafts responses, extracts resumes, identifies action items from MOMs' },
                  { step: '4', title: 'Escalation Alerts', desc: 'Urgent items → instant alerts via Slack, WhatsApp, Telegram' },
                  { step: '5', title: 'Resume Processing', desc: 'Parses resumes, scores against requirements, adds to platform' },
                  { step: '6', title: 'Daily Summary', desc: 'Delivers digest of FYI/CC emails + action item status to Slack' },
                ].map(s => (
                  <div key={s.step} className="flex gap-3">
                    <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-bold flex-shrink-0">{s.step}</div>
                    <div><p className="font-medium text-gray-800">{s.title}</p><p className="text-gray-500">{s.desc}</p></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── Smart Inbox Tab ─── */}
      {tab === 'inbox' && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <select value={classFilter} onChange={e => setClassFilter(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Classifications</option>
              {[...new Set(emails.map(e => e.classification).filter(Boolean))].map(c => (
                <option key={c!} value={c!}>{classIcons[c!] || '📧'} {c!.replace('_', ' ')}</option>
              ))}
            </select>
            <select value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Priorities</option>
              {['critical', 'high', 'medium', 'low'].map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            {filteredEmails.map(email => (
              <div key={email.id}
                onClick={() => setSelectedEmail(selectedEmail?.id === email.id ? null : email)}
                className={`bg-white rounded-xl border p-4 cursor-pointer transition-all ${
                  !email.is_read ? 'border-indigo-200 bg-indigo-50/30' : 'border-gray-200'
                } ${selectedEmail?.id === email.id ? 'ring-2 ring-indigo-400' : 'hover:border-gray-300'}`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <span className="text-xl mt-0.5">{classIcons[email.classification ?? 'general'] ?? '📧'}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className={`text-sm truncate ${!email.is_read ? 'font-bold text-gray-900' : 'font-medium text-gray-700'}`}>
                          {email.subject}
                        </p>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        From: {email.from_name || email.from_address} · {new Date(email.received_at).toLocaleString()}
                      </p>
                      {email.ai_summary && (
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">{email.ai_summary}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${priorityColors[email.priority ?? 'medium']}`}>
                      {email.priority?.toUpperCase()}
                    </span>
                    <div className="flex gap-1">
                      {email.requires_response && <span className="px-1.5 py-0 rounded text-[10px] bg-orange-100 text-orange-700">Reply Needed</span>}
                      {email.draft_generated && <span className="px-1.5 py-0 rounded text-[10px] bg-purple-100 text-purple-700">Draft Ready</span>}
                      {email.resume_processed && <span className="px-1.5 py-0 rounded text-[10px] bg-green-100 text-green-700">Resume Parsed</span>}
                      {email.alert_sent && <span className="px-1.5 py-0 rounded text-[10px] bg-red-100 text-red-700">Alert Sent</span>}
                      {email.has_attachments && <span className="px-1.5 py-0 rounded text-[10px] bg-gray-100 text-gray-600">📎 {email.attachment_count}</span>}
                    </div>
                  </div>
                </div>
                {/* Expanded detail */}
                {selectedEmail?.id === email.id && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-1">AI Summary</p>
                        <p className="text-sm text-gray-700">{email.ai_summary}</p>
                        <div className="flex gap-2 mt-2">
                          {email.classification_tags?.map(tag => (
                            <span key={tag} className="px-2 py-0.5 rounded-full text-[10px] bg-indigo-50 text-indigo-600">{tag}</span>
                          ))}
                        </div>
                      </div>
                      <div className="flex flex-col gap-2">
                        <p className="text-xs font-medium text-gray-500">Quick Actions</p>
                        <div className="flex flex-wrap gap-2">
                          <button className="px-3 py-1 bg-indigo-600 text-white rounded text-xs hover:bg-indigo-700">View Draft</button>
                          <button className="px-3 py-1 bg-white border border-gray-300 text-gray-700 rounded text-xs hover:bg-gray-50">Generate Draft</button>
                          <button className="px-3 py-1 bg-white border border-gray-300 text-gray-700 rounded text-xs hover:bg-gray-50">Extract Actions</button>
                          <button className="px-3 py-1 bg-red-50 border border-red-200 text-red-700 rounded text-xs hover:bg-red-100">Escalate</button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── AI Drafts Tab ─── */}
      {tab === 'drafts' && (
        <div className="space-y-4">
          {drafts.map(draft => {
            const email = emails.find(e => e.id === draft.email_message_id);
            return (
              <div key={draft.id} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{draft.draft_subject}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      In reply to: {email?.from_name || email?.from_address || 'Unknown'} · Tone: {draft.draft_tone}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[draft.status] ?? 'bg-gray-100'}`}>
                      {draft.status}
                    </span>
                    {draft.confidence_score && (
                      <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                        {Math.round(draft.confidence_score * 100)}% confidence
                      </span>
                    )}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-line border border-gray-100">
                  {draft.draft_body}
                </div>
                {draft.ai_reasoning && (
                  <div className="mt-3 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                    <p className="text-xs font-medium text-indigo-700 mb-1">AI Reasoning</p>
                    <p className="text-xs text-indigo-600">{draft.ai_reasoning}</p>
                  </div>
                )}
                <div className="flex gap-2 mt-3">
                  <button className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium hover:bg-green-700">Approve & Send</button>
                  <button className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-50">Edit Draft</button>
                  <button className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-50">Regenerate</button>
                  <button className="px-3 py-1.5 bg-white border border-red-200 text-red-600 rounded-lg text-xs font-medium hover:bg-red-50">Discard</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ─── Action Items Tab ─── */}
      {tab === 'actions' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Action Item</th>
                  <th className="px-4 py-3">Source</th>
                  <th className="px-4 py-3">Assigned To</th>
                  <th className="px-4 py-3">Due Date</th>
                  <th className="px-4 py-3">Priority</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {actions.map(a => (
                  <tr key={a.id} className={`hover:bg-gray-50 ${a.is_escalation ? 'bg-red-50/30' : ''}`}>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {a.is_escalation && <span className="text-red-500">🚨</span>}
                        <p className="font-medium text-gray-900">{a.title}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                        {a.source === 'mom_document' ? '📝 MOM' : '📧 Email'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{a.assigned_to_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-600 text-xs">{a.due_date || '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priorityColors[a.priority]}`}>
                        {a.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[a.status] ?? 'bg-gray-100'}`}>
                        {a.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button className="px-2 py-0.5 text-xs text-indigo-600 hover:bg-indigo-50 rounded">Follow Up</button>
                        <button className="px-2 py-0.5 text-xs text-red-600 hover:bg-red-50 rounded">Escalate</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
