import React, { useState, useEffect } from 'react';

interface Integration {
  id: number; organization_id: number; integration_type: string; name: string;
  status: string; is_active: boolean; uses_app_level_credentials: boolean;
  config_json: Record<string, any> | null; connected_at: string | null; last_used_at: string | null;
}
interface NotifRule {
  id: number; rule_name: string; event_type: string;
  channels: { type: string; channel?: string; mention?: string[]; to?: string; phone?: string }[];
  priority_filter: string[] | null; is_active: boolean; override_quiet_hours_for_critical: boolean;
}

const channelIcons: Record<string, string> = {
  slack: '💬', whatsapp: '📱', telegram: '✈️', teams: '👥',
  email_gateway: '📧', email: '📧', sms_gateway: '💬',
};
const statusBadge: Record<string, string> = {
  connected: 'bg-green-100 text-green-700', disconnected: 'bg-gray-100 text-gray-500',
  error: 'bg-red-100 text-red-700', pending: 'bg-yellow-100 text-yellow-700',
};
const eventIcons: Record<string, string> = {
  escalation: '🚨', interview_request: '📅', interview_reschedule: '🔄',
  onboarding: '✅', offboarding: '👋', resume_match: '🎯',
  daily_summary: '📊', mom_action_item: '📋', sla_breach: '⚠️',
  candidate_application: '📄', timesheet_approval: '⏱️',
};

export function CompanyAdminConfig() {
  const [tab, setTab] = useState<'overview' | 'integrations' | 'notifications' | 'email_agent' | 'branding'>('overview');
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [rules, setRules] = useState<NotifRule[]>([]);
  const [emailConfig, setEmailConfig] = useState<Record<string, any>>({});
  const [branding, setBranding] = useState<Record<string, any>>({});
  const [dashboard, setDashboard] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = '/api/v1/company-admin';
    Promise.all([
      fetch(`${base}/integrations?org_id=1`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/notification-rules?org_id=1`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/email-agent-config?org_id=1`).then(r => r.ok ? r.json() : {}),
      fetch(`${base}/branding?org_id=1`).then(r => r.ok ? r.json() : {}),
      fetch(`${base}/dashboard?org_id=1`).then(r => r.ok ? r.json() : {}),
    ]).then(([intg, rl, ea, br, da]) => {
      setIntegrations(intg.items || []);
      setRules(rl.items || []);
      setEmailConfig(ea || {});
      setBranding(br || {});
      setDashboard(da || {});
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'integrations', label: 'Integrations', count: integrations.length },
    { key: 'notifications', label: 'Notification Rules', count: rules.length },
    { key: 'email_agent', label: 'Email Agent Config' },
    { key: 'branding', label: 'Branding & Settings' },
  ] as const;

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" /></div>;

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Company Admin Configuration</h1>
          <p className="text-sm text-gray-500 mt-1">Configure your organization's Slack, WhatsApp, Telegram, email, notification rules, and branding</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs bg-purple-100 text-purple-700 font-medium">
            {branding.company_name || 'My Organization'}
          </span>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="flex gap-6">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${tab === t.key ? 'border-purple-600 text-purple-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
              {t.label}
              {'count' in t && t.count > 0 && <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">{t.count}</span>}
            </button>
          ))}
        </nav>
      </div>

      {/* ─── Overview ─── */}
      {tab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: 'Integrations', value: dashboard.integrations?.connected ?? 0, sub: `of ${dashboard.integrations?.total ?? 0}`, color: 'bg-purple-50 text-purple-700' },
              { label: 'Notification Rules', value: dashboard.notification_rules?.active ?? 0, sub: 'active', color: 'bg-blue-50 text-blue-700' },
              { label: 'Channels Active', value: dashboard.channels_active ?? 0, sub: 'connected', color: 'bg-green-50 text-green-700' },
              { label: 'Alerts Today', value: dashboard.alerts_sent_today ?? 0, sub: 'sent', color: 'bg-orange-50 text-orange-700' },
              { label: 'Emails Processed', value: dashboard.email_agent?.emails_processed_today ?? 0, sub: 'today', color: 'bg-indigo-50 text-indigo-700' },
            ].map(k => (
              <div key={k.label} className={`rounded-xl p-4 ${k.color}`}>
                <p className="text-xs font-medium opacity-70">{k.label}</p>
                <p className="text-2xl font-bold mt-1">{k.value} <span className="text-xs font-normal opacity-60">{k.sub}</span></p>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Connected Channels</h3>
            <div className="grid md:grid-cols-5 gap-3">
              {(dashboard.available_integrations || []).map((i: any) => (
                <div key={i.type} className={`p-4 rounded-xl border text-center ${i.connected ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'}`}>
                  <span className="text-3xl">{channelIcons[i.type] ?? '🔌'}</span>
                  <p className="text-sm font-medium capitalize mt-2 text-gray-700">{i.type.replace('_', ' ')}</p>
                  <p className={`text-xs mt-1 ${i.connected ? 'text-green-600' : 'text-gray-400'}`}>
                    {i.connected ? 'Connected' : 'Not Connected'}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-100 p-5">
            <h3 className="text-sm font-semibold text-purple-800 mb-3">Company vs App Admin</h3>
            <div className="grid md:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-white rounded-lg border border-purple-100">
                <p className="font-semibold text-purple-700 mb-2">🏢 Company Admin (This Page)</p>
                <ul className="space-y-1 text-purple-600">
                  <li>• Your organization's own Slack workspace connection</li>
                  <li>• Your WhatsApp/Telegram numbers and channels</li>
                  <li>• Notification routing rules (which events → which channels)</li>
                  <li>• Email agent behavior: classification, drafting, escalation keywords</li>
                  <li>• Company branding: colors, logo, timezone, currency</li>
                </ul>
              </div>
              <div className="p-3 bg-white rounded-lg border border-indigo-100">
                <p className="font-semibold text-indigo-700 mb-2">🔧 App Admin (Platform Level)</p>
                <ul className="space-y-1 text-indigo-600">
                  <li>• Platform-wide API keys (OpenAI, Twilio, SendGrid)</li>
                  <li>• Slack app OAuth credentials (shared across all orgs)</li>
                  <li>• Feature flags and rollout control</li>
                  <li>• License limits and usage quotas</li>
                  <li>• System health and integration monitoring</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── Integrations Tab ─── */}
      {tab === 'integrations' && (
        <div className="space-y-4">
          {integrations.map(intg => (
            <div key={intg.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-3xl">{channelIcons[intg.integration_type] ?? '🔌'}</span>
                  <div>
                    <p className="text-base font-semibold text-gray-900">{intg.name}</p>
                    <p className="text-xs text-gray-500 capitalize">{intg.integration_type.replace('_', ' ')}</p>
                    {intg.uses_app_level_credentials && (
                      <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] bg-indigo-50 text-indigo-600">Uses Platform API Keys</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge[intg.status]}`}>{intg.status}</span>
                  <button className="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50">{intg.status === 'connected' ? 'Edit' : 'Connect'}</button>
                  <button className="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50">Test</button>
                </div>
              </div>
              {intg.config_json && (
                <div className="mt-3 bg-gray-50 rounded-lg p-3">
                  {intg.integration_type === 'slack' && intg.config_json.channels && (
                    <div>
                      <p className="text-xs font-medium text-gray-600 mb-2">Channel Mappings</p>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(intg.config_json.channels as Record<string, string>).map(([key, ch]) => (
                          <span key={key} className="px-2 py-1 rounded bg-white border border-gray-200 text-xs">
                            <span className="text-gray-500">{key}:</span> <span className="text-blue-600 font-mono">{ch}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {intg.integration_type === 'whatsapp' && (
                    <p className="text-xs text-gray-600">Phone: <span className="font-mono">{intg.config_json.phone_number}</span> · Provider: {intg.config_json.provider}</p>
                  )}
                  {intg.integration_type === 'telegram' && (
                    <p className="text-xs text-gray-600">Bot: <span className="font-mono">{intg.config_json.bot_username}</span></p>
                  )}
                  {intg.integration_type === 'email_gateway' && (
                    <p className="text-xs text-gray-600">From: {intg.config_json.from_email} · Reply-To: {intg.config_json.reply_to}</p>
                  )}
                </div>
              )}
              {intg.connected_at && (
                <p className="text-[10px] text-gray-400 mt-2">Connected: {new Date(intg.connected_at).toLocaleDateString()} · Last used: {intg.last_used_at ? new Date(intg.last_used_at).toLocaleString() : 'Never'}</p>
              )}
            </div>
          ))}
          <button className="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl text-sm text-gray-500 hover:border-purple-400 hover:text-purple-600 transition-colors">
            + Add Integration
          </button>
        </div>
      )}

      {/* ─── Notification Rules Tab ─── */}
      {tab === 'notifications' && (
        <div className="space-y-4">
          {rules.map(rule => (
            <div key={rule.id} className={`bg-white rounded-xl border p-5 ${rule.is_active ? 'border-gray-200' : 'border-gray-100 opacity-60'}`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{eventIcons[rule.event_type] ?? '🔔'}</span>
                    <p className="text-sm font-semibold text-gray-900">{rule.rule_name}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5 capitalize">Event: {rule.event_type.replace(/_/g, ' ')}</p>
                </div>
                <div className="flex items-center gap-2">
                  {rule.override_quiet_hours_for_critical && (
                    <span className="px-2 py-0.5 rounded text-[10px] bg-red-50 text-red-600">Overrides Quiet Hours</span>
                  )}
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${rule.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {rule.is_active ? 'Active' : 'Disabled'}
                  </span>
                  <button className="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50">Edit</button>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {rule.channels.map((ch, i) => (
                  <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-100">
                    <span>{channelIcons[ch.type] ?? '📨'}</span>
                    <span className="text-xs font-medium text-gray-700 capitalize">{ch.type}</span>
                    {ch.channel && <span className="text-xs text-blue-600 font-mono">{ch.channel}</span>}
                    {ch.to && <span className="text-xs text-gray-500">{ch.to}</span>}
                    {ch.mention && ch.mention.map(m => (
                      <span key={m} className="px-1 py-0 rounded text-[10px] bg-blue-50 text-blue-600">{m}</span>
                    ))}
                  </div>
                ))}
              </div>
              {rule.priority_filter && (
                <div className="flex gap-1 mt-2">
                  <span className="text-[10px] text-gray-400">Priority filter:</span>
                  {rule.priority_filter.map(p => (
                    <span key={p} className="px-1.5 py-0 rounded text-[10px] bg-orange-50 text-orange-600 capitalize">{p}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          <button className="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl text-sm text-gray-500 hover:border-purple-400 hover:text-purple-600 transition-colors">
            + Add Notification Rule
          </button>
        </div>
      )}

      {/* ─── Email Agent Config Tab ─── */}
      {tab === 'email_agent' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">Email Agent Settings</h3>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${emailConfig.is_enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                {emailConfig.is_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                { label: 'Auto Classify', value: emailConfig.auto_classify, key: 'auto_classify' },
                { label: 'Auto Draft Responses', value: emailConfig.auto_draft_responses, key: 'auto_draft_responses' },
                { label: 'Auto Process Resumes', value: emailConfig.auto_process_resumes, key: 'auto_process_resumes' },
                { label: 'Auto Extract Action Items', value: emailConfig.auto_extract_action_items, key: 'auto_extract_action_items' },
                { label: 'Auto Alert Escalations', value: emailConfig.auto_alert_escalations, key: 'auto_alert_escalations' },
                { label: 'Spam Filter', value: emailConfig.spam_filter_enabled, key: 'spam_filter_enabled' },
              ].map(toggle => (
                <div key={toggle.key} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                  <span className="text-sm text-gray-700">{toggle.label}</span>
                  <div className={`w-10 h-5 rounded-full flex items-center px-0.5 ${toggle.value ? 'bg-purple-500' : 'bg-gray-300'}`}>
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${toggle.value ? 'translate-x-5' : ''}`} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {emailConfig.monitored_mailboxes && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Monitored Mailboxes</h3>
              <div className="space-y-2">
                {(emailConfig.monitored_mailboxes as any[]).map((mb, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">📧</span>
                      <div>
                        <p className="text-sm font-medium text-gray-700">{mb.email}</p>
                        <p className="text-xs text-gray-400">Provider: {mb.provider} · Folders: {(mb.folders as string[]).join(', ')}</p>
                      </div>
                    </div>
                    <button className="px-3 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50">Remove</button>
                  </div>
                ))}
              </div>
              <button className="mt-3 text-xs text-purple-600 hover:text-purple-700 font-medium">+ Add Mailbox</button>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Escalation Keywords</h3>
              <div className="flex flex-wrap gap-2">
                {(emailConfig.escalation_keywords as string[] || []).map(kw => (
                  <span key={kw} className="px-2 py-1 rounded-full text-xs bg-red-50 text-red-600 border border-red-100">{kw}</span>
                ))}
              </div>
              <button className="mt-3 text-xs text-purple-600 hover:text-purple-700 font-medium">+ Add Keyword</button>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Summary Delivery</h3>
              <p className="text-sm text-gray-600">Daily summary at <span className="font-mono text-purple-600">{emailConfig.daily_summary_time || '09:00'}</span></p>
              <div className="flex gap-2 mt-2">
                {(emailConfig.daily_summary_channels as any[] || []).map((ch: any, i: number) => (
                  <span key={i} className="px-2 py-1 rounded text-xs bg-gray-50 border border-gray-200">
                    {channelIcons[ch.type] ?? '📨'} {ch.channel || ch.to}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── Branding Tab ─── */}
      {tab === 'branding' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Company Branding</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div><label className="text-xs font-medium text-gray-500">Company Name</label><input className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={branding.company_name || ''} readOnly /></div>
                <div><label className="text-xs font-medium text-gray-500">Notification From Name</label><input className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={branding.notification_from_name || ''} readOnly /></div>
                <div><label className="text-xs font-medium text-gray-500">Email Footer</label><input className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={branding.email_footer_text || ''} readOnly /></div>
              </div>
              <div className="space-y-3">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="text-xs font-medium text-gray-500">Primary Color</label>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-8 h-8 rounded-lg border" style={{ backgroundColor: branding.primary_color || '#6366f1' }} />
                      <span className="text-sm font-mono text-gray-600">{branding.primary_color || '#6366f1'}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <label className="text-xs font-medium text-gray-500">Secondary Color</label>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-8 h-8 rounded-lg border" style={{ backgroundColor: branding.secondary_color || '#8b5cf6' }} />
                      <span className="text-sm font-mono text-gray-600">{branding.secondary_color || '#8b5cf6'}</span>
                    </div>
                  </div>
                </div>
                <div><label className="text-xs font-medium text-gray-500">Timezone</label><input className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={branding.timezone || ''} readOnly /></div>
                <div className="flex gap-4">
                  <div className="flex-1"><label className="text-xs font-medium text-gray-500">Date Format</label><input className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={branding.date_format || ''} readOnly /></div>
                  <div className="flex-1"><label className="text-xs font-medium text-gray-500">Currency</label><input className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={branding.currency || ''} readOnly /></div>
                </div>
              </div>
            </div>
            <button className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700">Save Changes</button>
          </div>
        </div>
      )}
    </div>
  );
}
