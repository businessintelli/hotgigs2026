import React, { useState, useEffect } from 'react';

interface Channel {
  id: number; user_id: number; channel_type: string; channel_identifier: string;
  channel_name: string | null; is_active: boolean; is_primary: boolean;
  notification_preferences: Record<string, boolean> | null;
  quiet_hours_start: string | null; quiet_hours_end: string | null;
}
interface Alert {
  id: number; channel_type: string; alert_type: string; title: string;
  message: string; priority: string; status: string;
  sent_at: string | null; delivered_at: string | null; read_at: string | null;
}
interface ChannelMapping {
  id: number; event_type: string; channel_id: string; channel_name: string;
  is_active: boolean; auto_thread: boolean; mention_roles: string[] | null;
}

const channelIcons: Record<string, string> = {
  slack: '💬', whatsapp: '📱', telegram: '✈️', email: '📧',
  in_app: '🔔', sms: '💬', teams: '👥',
};
const alertTypeIcons: Record<string, string> = {
  escalation: '🚨', action_item: '📋', daily_summary: '📊',
  resume_match: '🎯', interview: '📅', onboarding: '✅', offboarding: '👋',
};
const statusColors: Record<string, string> = {
  queued: 'bg-gray-100 text-gray-600', sent: 'bg-blue-100 text-blue-700',
  delivered: 'bg-green-100 text-green-700', read: 'bg-green-200 text-green-800',
  failed: 'bg-red-100 text-red-700',
};
const priorityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-700', high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700', low: 'bg-green-100 text-green-700',
};

const mockDashboard = {
  total_channels_configured: 4, alerts_sent_today: 5, alerts_sent_this_week: 32,
  delivery_rate: 0.98, read_rate: 0.72,
  by_channel: {
    slack: { sent: 22, delivered: 22, read: 18 },
    whatsapp: { sent: 6, delivered: 6, read: 5 },
    telegram: { sent: 4, delivered: 4, read: 2 },
  },
  by_type: { escalation: 3, daily_summary: 7, action_item: 12, resume_match: 6, interview: 4 },
  slack_stats: {
    channels_mapped: 8, messages_sent_today: 14, active_threads: 6,
    pending_requests: { onboarding: 2, interview: 3, offboarding: 1 },
  },
};

export function NotificationCollabHub() {
  const [tab, setTab] = useState<'dashboard' | 'channels' | 'alerts' | 'slack'>('dashboard');
  const [channels, setChannels] = useState<Channel[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [mappings, setMappings] = useState<ChannelMapping[]>([]);
  const [dashboard, setDashboard] = useState(mockDashboard);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = '/api/v1/notification-hub';
    Promise.all([
      fetch(`${base}/channels`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/alerts?limit=20`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/slack/channels`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${base}/dashboard`).then(r => r.ok ? r.json() : mockDashboard),
    ]).then(([ch, al, mp, da]) => {
      setChannels(ch.items || []);
      setAlerts(al.items || []);
      setMappings(mp.items || []);
      setDashboard(da.total_channels_configured ? da : mockDashboard);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'channels', label: 'My Channels', count: channels.filter(c => c.is_active).length },
    { key: 'alerts', label: 'Alert History', count: alerts.length },
    { key: 'slack', label: 'Slack Collaboration', count: mappings.length },
  ] as const;

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  );

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notification & Collaboration Hub</h1>
          <p className="text-sm text-gray-500 mt-1">Slack, WhatsApp, Telegram alerts · Team collaboration · Instant response channels</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          + Connect Channel
        </button>
      </div>

      <div className="border-b border-gray-200">
        <nav className="flex gap-6">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}>
              {t.label}
              {'count' in t && t.count > 0 && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">{t.count}</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* ─── Dashboard Tab ─── */}
      {tab === 'dashboard' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: 'Channels Active', value: dashboard.total_channels_configured, color: 'bg-blue-50 text-blue-700' },
              { label: 'Alerts Today', value: dashboard.alerts_sent_today, color: 'bg-indigo-50 text-indigo-700' },
              { label: 'This Week', value: dashboard.alerts_sent_this_week, color: 'bg-purple-50 text-purple-700' },
              { label: 'Delivery Rate', value: `${Math.round(dashboard.delivery_rate * 100)}%`, color: 'bg-green-50 text-green-700' },
              { label: 'Read Rate', value: `${Math.round(dashboard.read_rate * 100)}%`, color: 'bg-teal-50 text-teal-700' },
            ].map(kpi => (
              <div key={kpi.label} className={`rounded-xl p-4 ${kpi.color}`}>
                <p className="text-xs font-medium opacity-70">{kpi.label}</p>
                <p className="text-2xl font-bold mt-1">{kpi.value}</p>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Channel Performance */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Channel Performance</h3>
              <div className="space-y-4">
                {Object.entries(dashboard.by_channel).map(([ch, stats]) => (
                  <div key={ch} className="flex items-center gap-4">
                    <span className="text-2xl">{channelIcons[ch] ?? '📨'}</span>
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium capitalize text-gray-700">{ch}</span>
                        <span className="text-xs text-gray-500">{stats.read}/{stats.sent} read</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(stats.read / stats.sent) * 100}%` }} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Slack Collaboration Stats */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Slack Team Collaboration</h3>
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="p-3 rounded-lg bg-purple-50">
                  <p className="text-xs text-purple-600">Channels Mapped</p>
                  <p className="text-xl font-bold text-purple-700">{dashboard.slack_stats.channels_mapped}</p>
                </div>
                <div className="p-3 rounded-lg bg-blue-50">
                  <p className="text-xs text-blue-600">Messages Today</p>
                  <p className="text-xl font-bold text-blue-700">{dashboard.slack_stats.messages_sent_today}</p>
                </div>
                <div className="p-3 rounded-lg bg-indigo-50">
                  <p className="text-xs text-indigo-600">Active Threads</p>
                  <p className="text-xl font-bold text-indigo-700">{dashboard.slack_stats.active_threads}</p>
                </div>
                <div className="p-3 rounded-lg bg-orange-50">
                  <p className="text-xs text-orange-600">Pending Requests</p>
                  <p className="text-xl font-bold text-orange-700">
                    {Object.values(dashboard.slack_stats.pending_requests).reduce((a, b) => a + b, 0)}
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500">Pending by Type</p>
                {Object.entries(dashboard.slack_stats.pending_requests).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center p-2 rounded bg-gray-50">
                    <span className="text-sm capitalize text-gray-700">{type}</span>
                    <span className="px-2 py-0.5 rounded-full text-xs bg-orange-100 text-orange-700 font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Alert by Type */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Alerts by Category (This Week)</h3>
            <div className="flex flex-wrap gap-3">
              {Object.entries(dashboard.by_type).map(([type, count]) => (
                <div key={type} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-50 border border-gray-100">
                  <span className="text-lg">{alertTypeIcons[type] ?? '🔔'}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-700 capitalize">{type.replace('_', ' ')}</p>
                    <p className="text-xs text-gray-500">{count} alerts</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ─── Channels Tab ─── */}
      {tab === 'channels' && (
        <div className="space-y-4">
          {channels.map(ch => (
            <div key={ch.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-3xl">{channelIcons[ch.channel_type] ?? '📨'}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-base font-semibold text-gray-900">{ch.channel_name || ch.channel_identifier}</p>
                      {ch.is_primary && <span className="px-2 py-0.5 rounded-full text-[10px] bg-blue-100 text-blue-700 font-medium">PRIMARY</span>}
                    </div>
                    <p className="text-sm text-gray-500 capitalize">{ch.channel_type} · {ch.channel_identifier}</p>
                    {ch.quiet_hours_start && (
                      <p className="text-xs text-gray-400 mt-0.5">Quiet hours: {ch.quiet_hours_start} - {ch.quiet_hours_end}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ch.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {ch.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <button className="px-3 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50">Test</button>
                  <button className="px-3 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50">Edit</button>
                </div>
              </div>
              {ch.notification_preferences && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {Object.entries(ch.notification_preferences).map(([pref, enabled]) => (
                    <span key={pref} className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                      enabled ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-400 line-through'
                    }`}>
                      {pref.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ─── Alert History Tab ─── */}
      {tab === 'alerts' && (
        <div className="space-y-3">
          {alerts.map(alert => (
            <div key={alert.id} className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <span className="text-xl mt-0.5">{alertTypeIcons[alert.alert_type] ?? '🔔'}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                    <p className="text-xs text-gray-600 mt-1 whitespace-pre-line line-clamp-3">{alert.message.replace(/\*/g, '').replace(/<[^>]+>/g, '')}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {channelIcons[alert.channel_type]} {alert.channel_type} · Sent: {alert.sent_at ? new Date(alert.sent_at).toLocaleString() : '—'}
                      {alert.read_at && ` · Read: ${new Date(alert.read_at).toLocaleString()}`}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${priorityColors[alert.priority]}`}>
                    {alert.priority}
                  </span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${statusColors[alert.status]}`}>
                    {alert.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ─── Slack Collaboration Tab ─── */}
      {tab === 'slack' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">💬</span>
                <div>
                  <h3 className="text-base font-semibold text-gray-900">HotGigs MSP Team</h3>
                  <p className="text-xs text-gray-500">Workspace: T04HOTGIGS · Bot: @HotGigsAgent</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700 font-medium">Connected</span>
            </div>

            <h4 className="text-sm font-medium text-gray-700 mb-3">Event → Channel Mappings</h4>
            <div className="bg-gray-50 rounded-lg overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-2">Event Type</th>
                    <th className="px-4 py-2">Slack Channel</th>
                    <th className="px-4 py-2">Auto-Thread</th>
                    <th className="px-4 py-2">Mention</th>
                    <th className="px-4 py-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {mappings.map(m => (
                    <tr key={m.id} className="hover:bg-white transition-colors">
                      <td className="px-4 py-2">
                        <span className="flex items-center gap-2">
                          <span>{alertTypeIcons[m.event_type] ?? '🔔'}</span>
                          <span className="capitalize font-medium text-gray-700">{m.event_type.replace('_', ' ')}</span>
                        </span>
                      </td>
                      <td className="px-4 py-2 text-blue-600 font-mono text-xs">{m.channel_name}</td>
                      <td className="px-4 py-2">
                        {m.auto_thread
                          ? <span className="text-green-600 text-xs">Yes</span>
                          : <span className="text-gray-400 text-xs">No</span>}
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex gap-1">
                          {m.mention_roles?.map(role => (
                            <span key={role} className="px-1.5 py-0 rounded text-[10px] bg-blue-50 text-blue-600">{role}</span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${m.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                          {m.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Collaboration Use Cases */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 p-5">
            <h3 className="text-sm font-semibold text-blue-800 mb-3">Slack Collaboration Use Cases</h3>
            <div className="grid md:grid-cols-3 gap-4 text-xs">
              <div className="p-3 bg-white rounded-lg border border-blue-100">
                <p className="font-semibold text-blue-700 mb-2">📅 Interview Coordination</p>
                <p className="text-blue-600">Instant Slack thread for each interview request/reschedule. All stakeholders tagged. Real-time scheduling in-thread.</p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-blue-100">
                <p className="font-semibold text-blue-700 mb-2">✅ Onboarding/Offboarding</p>
                <p className="text-blue-600">Checklist threads with task assignments. @mentions for IT, facilities, HR. Auto-close when all items done.</p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-blue-100">
                <p className="font-semibold text-blue-700 mb-2">🚨 Escalation Response</p>
                <p className="text-blue-600">Critical alerts → dedicated #escalations channel + DMs. SLA timer visible. Quick-action buttons for response.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
