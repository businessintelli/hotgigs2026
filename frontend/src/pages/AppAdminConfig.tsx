import React, { useState } from 'react';

// ─── Types ───────────────────────────────────────────────────
interface Integration {
  id: number;
  integration_type: string;
  name: string;
  description: string;
  provider: string;
  status: string;
  base_url: string;
  api_key_masked: string | null;
  config_json: Record<string, any> | null;
  is_active: boolean;
  available_to_all_orgs: boolean;
  rate_limit_per_minute: number | null;
  rate_limit_per_day: number | null;
  last_health_check: string | null;
  health_status: string | null;
  usage_today?: Record<string, number>;
  orgs_connected?: number;
  allowed_org_ids?: number[];
}

interface FeatureFlag {
  id: number;
  flag_key: string;
  name: string;
  description: string;
  status: string;
  category: string;
  rollout_percentage: number;
  allowed_org_ids: number[] | null;
}

interface LicenseConfig {
  config_key: string;
  config_value: string;
  config_type: string;
  category: string;
  description: string;
}

// ─── Mock Data ───────────────────────────────────────────────
const integrations: Integration[] = [
  {
    id: 1, integration_type: 'ai_provider', name: 'OpenAI GPT-4o',
    description: 'Primary AI model for email classification, resume parsing, draft generation, and match scoring',
    provider: 'openai', status: 'connected', base_url: 'https://api.openai.com/v1', api_key_masked: 'sk-...7xKm',
    config_json: { model: 'gpt-4o', max_tokens: 4096, temperature: 0.3, fallback_model: 'gpt-4o-mini' },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: 500, rate_limit_per_day: 50000,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy',
    usage_today: { requests: 1247, tokens: 892000 },
  },
  {
    id: 2, integration_type: 'slack', name: 'Slack Platform App',
    description: 'HotGigs Slack app — installed by each company into their workspace via OAuth',
    provider: 'slack', status: 'connected', base_url: 'https://slack.com/api', api_key_masked: 'xoxb-...F4tQ',
    config_json: { client_id: '4829374928.7482937492', scopes: ['chat:write', 'channels:read', 'users:read', 'files:write'] },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: null, rate_limit_per_day: null,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy', orgs_connected: 3,
  },
  {
    id: 3, integration_type: 'whatsapp', name: 'Twilio WhatsApp Business',
    description: 'Platform-level Twilio for WhatsApp Business API',
    provider: 'twilio', status: 'connected', base_url: 'https://api.twilio.com', api_key_masked: 'AC...8f2d',
    config_json: { account_sid: 'AC...', messaging_service_sid: 'MG...', from_number: '+1-555-HOTGIGS' },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: 60, rate_limit_per_day: 5000,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy',
  },
  {
    id: 4, integration_type: 'telegram', name: 'Telegram Bot API',
    description: 'Platform-level Telegram bot for alert notifications',
    provider: 'telegram', status: 'connected', base_url: 'https://api.telegram.org', api_key_masked: 'bot...3xYz',
    config_json: { bot_username: '@HotGigsAgent_bot' },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: 30, rate_limit_per_day: 2000,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy',
  },
  {
    id: 5, integration_type: 'email_gateway', name: 'SendGrid Email Gateway',
    description: 'Transactional email delivery for notifications and candidate communications',
    provider: 'sendgrid', status: 'connected', base_url: 'https://api.sendgrid.com/v3', api_key_masked: 'SG...j9Kp',
    config_json: { from_email: 'noreply@hotgigs.ai', from_name: 'HotGigs Platform', daily_limit: 10000 },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: 100, rate_limit_per_day: 10000,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy',
  },
  {
    id: 6, integration_type: 'sms_gateway', name: 'Twilio SMS',
    description: 'SMS notifications for critical alerts when other channels unavailable',
    provider: 'twilio', status: 'connected', base_url: 'https://api.twilio.com', api_key_masked: 'AC...8f2d',
    config_json: { from_number: '+1-555-0100' },
    is_active: true, available_to_all_orgs: false, rate_limit_per_minute: 30, rate_limit_per_day: 1000,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy', allowed_org_ids: [1, 2],
  },
  {
    id: 7, integration_type: 'bgc_provider', name: 'HireRight Background Checks',
    description: 'Automated BGC initiation for onboarding workflows',
    provider: 'hireright', status: 'connected', base_url: 'https://api.hireright.com/v1', api_key_masked: 'hr...Kx4p',
    config_json: { package_ids: { standard: 'PKG-001', enhanced: 'PKG-002', executive: 'PKG-003' } },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: null, rate_limit_per_day: null,
    last_health_check: '2026-03-13T08:00:00Z', health_status: 'healthy',
  },
  {
    id: 8, integration_type: 'storage', name: 'AWS S3 Document Storage',
    description: 'Cloud storage for resumes, contracts, and documents',
    provider: 'aws_s3', status: 'connected', base_url: 'https://s3.amazonaws.com', api_key_masked: 'AKIA...7xKm',
    config_json: { bucket: 'hotgigs-documents', region: 'us-east-1', max_file_size_mb: 25 },
    is_active: true, available_to_all_orgs: true, rate_limit_per_minute: null, rate_limit_per_day: null,
    last_health_check: '2026-03-13T09:00:00Z', health_status: 'healthy',
  },
  {
    id: 9, integration_type: 'video_conferencing', name: 'Zoom Meetings',
    description: 'Auto-scheduling interview video calls',
    provider: 'zoom', status: 'disconnected', base_url: 'https://api.zoom.us/v2', api_key_masked: null,
    config_json: null, is_active: false, available_to_all_orgs: true,
    rate_limit_per_minute: null, rate_limit_per_day: null, last_health_check: null, health_status: null,
  },
  {
    id: 10, integration_type: 'calendar', name: 'Google Calendar',
    description: 'Calendar sync for interview scheduling',
    provider: 'google', status: 'disconnected', base_url: 'https://www.googleapis.com/calendar/v3', api_key_masked: null,
    config_json: null, is_active: false, available_to_all_orgs: true,
    rate_limit_per_minute: null, rate_limit_per_day: null, last_health_check: null, health_status: null,
  },
];

const featureFlags: FeatureFlag[] = [
  { id: 1, flag_key: 'email_agent', name: 'Email Agent', description: 'AI-powered email classification, drafting, and action extraction', status: 'enabled', category: 'ai', rollout_percentage: 100, allowed_org_ids: null },
  { id: 2, flag_key: 'auto_resume_processing', name: 'Auto Resume Processing', description: 'Automatically parse and score resumes from incoming emails', status: 'enabled', category: 'ai', rollout_percentage: 100, allowed_org_ids: null },
  { id: 3, flag_key: 'cascade_invoicing', name: 'Cascading Auto-Invoicing', description: 'Auto-generate downstream invoices when upstream is approved', status: 'enabled', category: 'billing', rollout_percentage: 100, allowed_org_ids: null },
  { id: 4, flag_key: 'whatsapp_alerts', name: 'WhatsApp Alert Delivery', description: 'Send critical alerts via WhatsApp Business API', status: 'enabled', category: 'notifications', rollout_percentage: 100, allowed_org_ids: null },
  { id: 5, flag_key: 'telegram_alerts', name: 'Telegram Alert Delivery', description: 'Send alerts via Telegram bot', status: 'beta', category: 'notifications', rollout_percentage: 50, allowed_org_ids: [1] },
  { id: 6, flag_key: 'ai_interview_scheduling', name: 'AI Interview Scheduling', description: 'Let AI agent auto-schedule interviews based on availability', status: 'disabled', category: 'ai', rollout_percentage: 0, allowed_org_ids: null },
  { id: 7, flag_key: 'advanced_analytics_v2', name: 'Advanced Analytics V2', description: 'Next-gen analytics dashboards with predictive insights', status: 'beta', category: 'analytics', rollout_percentage: 25, allowed_org_ids: [1, 2] },
  { id: 8, flag_key: 'multi_language_support', name: 'Multi-Language Support', description: 'Email drafts and notifications in multiple languages', status: 'disabled', category: 'general', rollout_percentage: 0, allowed_org_ids: null },
];

const licenseConfigs: LicenseConfig[] = [
  { config_key: 'max_organizations', config_value: '50', config_type: 'int', category: 'limits', description: 'Maximum number of organizations' },
  { config_key: 'max_users_per_org', config_value: '200', config_type: 'int', category: 'limits', description: 'Maximum users per organization' },
  { config_key: 'max_email_syncs_per_day', config_value: '100000', config_type: 'int', category: 'limits', description: 'Maximum email syncs per day' },
  { config_key: 'max_ai_requests_per_day', config_value: '50000', config_type: 'int', category: 'limits', description: 'Maximum AI model requests per day' },
  { config_key: 'max_file_storage_gb', config_value: '500', config_type: 'int', category: 'limits', description: 'Total file storage limit (GB)' },
  { config_key: 'session_timeout_minutes', config_value: '60', config_type: 'int', category: 'security', description: 'Session timeout in minutes' },
  { config_key: 'enforce_2fa', config_value: 'false', config_type: 'bool', category: 'security', description: 'Require 2FA for all users' },
  { config_key: 'password_min_length', config_value: '10', config_type: 'int', category: 'security', description: 'Minimum password length' },
  { config_key: 'data_retention_days', config_value: '365', config_type: 'int', category: 'compliance', description: 'Data retention period in days' },
  { config_key: 'audit_log_enabled', config_value: 'true', config_type: 'bool', category: 'compliance', description: 'Enable audit logging' },
];

const dashboardData = {
  system_health: 'healthy',
  total_organizations: 3,
  total_users: 42,
  active_sessions: 18,
  integrations: { total: 10, connected: 8, disconnected: 2, errors: 0 },
  feature_flags: { total: 8, enabled: 4, beta: 2, disabled: 2 },
  usage_today: { ai_requests: 1247, emails_processed: 856, resumes_parsed: 23, notifications_sent: 142, api_calls: 12847 },
  storage: { used_gb: 47.3, limit_gb: 500, percent: 9.5 },
  organizations_summary: [
    { id: 1, name: 'HotGigs MSP', type: 'MSP', users: 15, integrations_active: 6 },
    { id: 2, name: 'TechCorp Inc', type: 'CLIENT', users: 18, integrations_active: 4 },
    { id: 3, name: 'StaffPro Solutions', type: 'SUPPLIER', users: 9, integrations_active: 3 },
  ],
};

// ─── Helpers ─────────────────────────────────────────────────
const providerIcon = (provider: string) => {
  const icons: Record<string, string> = {
    openai: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z',
    slack: 'M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155',
    twilio: 'M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z',
    telegram: 'M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5',
    sendgrid: 'M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75',
    hireright: 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
    aws_s3: 'M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125',
    zoom: 'M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9.75c.966 0 1.75-.784 1.75-1.75V7a1.75 1.75 0 00-1.75-1.75H4.5c-.966 0-1.75.784-1.75 1.75v10c0 .966.784 1.75 1.75 1.75z',
    google: 'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5',
  };
  return icons[provider] || 'M11.42 15.17l-4.655-5.163a.5.5 0 01.745-.656l4.16 4.622 4.16-4.622a.5.5 0 01.745.656l-4.655 5.163a.5.5 0 01-.5 0z';
};

// ─── Tabs ────────────────────────────────────────────────────
type Tab = 'overview' | 'integrations' | 'feature_flags' | 'license' | 'organizations';

export const AppAdminConfig: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const tabs: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'System Overview' },
    { key: 'integrations', label: 'Platform Integrations' },
    { key: 'feature_flags', label: 'Feature Flags' },
    { key: 'license', label: 'License & Security' },
    { key: 'organizations', label: 'Organizations' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">App Admin Configuration</h1>
          <p className="text-neutral-500 mt-1">Platform-level integrations, feature flags, license limits, and system health</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${
            dashboardData.system_health === 'healthy' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
          }`}>
            <span className={`w-2 h-2 rounded-full ${dashboardData.system_health === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
            System {dashboardData.system_health === 'healthy' ? 'Healthy' : 'Issue'}
          </span>
          <span className="px-3 py-1.5 rounded-full bg-violet-50 text-violet-700 text-sm font-medium">Super Admin</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-neutral-200">
        <nav className="flex gap-6">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === t.key
                  ? 'border-violet-600 text-violet-700'
                  : 'border-transparent text-neutral-500 hover:text-neutral-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'integrations' && <IntegrationsTab />}
      {activeTab === 'feature_flags' && <FeatureFlagsTab />}
      {activeTab === 'license' && <LicenseTab />}
      {activeTab === 'organizations' && <OrganizationsTab />}
    </div>
  );
};

// ─── Overview Tab ────────────────────────────────────────────
const OverviewTab: React.FC = () => {
  const { usage_today: u, storage, integrations: ig, feature_flags: ff } = dashboardData;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Organizations', value: dashboardData.total_organizations, color: 'bg-blue-50 text-blue-700' },
          { label: 'Total Users', value: dashboardData.total_users, color: 'bg-emerald-50 text-emerald-700' },
          { label: 'Active Sessions', value: dashboardData.active_sessions, color: 'bg-amber-50 text-amber-700' },
          { label: 'Integrations Active', value: `${ig.connected}/${ig.total}`, color: 'bg-violet-50 text-violet-700' },
        ].map(kpi => (
          <div key={kpi.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{kpi.label}</p>
            <p className={`text-2xl font-bold mt-1 ${kpi.color.split(' ')[1]}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Usage Today */}
      <div className="bg-white rounded-xl border border-neutral-200 p-6">
        <h3 className="text-sm font-semibold text-neutral-900 mb-4">Platform Usage Today</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: 'AI Requests', value: u.ai_requests.toLocaleString(), icon: '9813' },
            { label: 'Emails Processed', value: u.emails_processed.toLocaleString(), icon: '21.75' },
            { label: 'Resumes Parsed', value: u.resumes_parsed.toString(), icon: '19.5' },
            { label: 'Notifications Sent', value: u.notifications_sent.toLocaleString(), icon: '14.857' },
            { label: 'API Calls', value: u.api_calls.toLocaleString(), icon: '17.25' },
          ].map(item => (
            <div key={item.label} className="text-center p-3 bg-neutral-50 rounded-lg">
              <p className="text-xl font-bold text-neutral-900">{item.value}</p>
              <p className="text-xs text-neutral-500 mt-1">{item.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Storage & Feature Flags Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Storage Gauge */}
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Storage Usage</h3>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <div className="w-full bg-neutral-100 rounded-full h-4">
                <div className="bg-violet-500 h-4 rounded-full transition-all" style={{ width: `${storage.percent}%` }} />
              </div>
              <div className="flex justify-between mt-2 text-xs text-neutral-500">
                <span>{storage.used_gb} GB used</span>
                <span>{storage.limit_gb} GB limit</span>
              </div>
            </div>
            <span className="text-2xl font-bold text-violet-700">{storage.percent}%</span>
          </div>
        </div>

        {/* Feature Flag Summary */}
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Feature Flags</h3>
          <div className="flex items-center gap-6">
            {[
              { label: 'Enabled', count: ff.enabled, color: 'bg-emerald-100 text-emerald-700' },
              { label: 'Beta', count: ff.beta, color: 'bg-amber-100 text-amber-700' },
              { label: 'Disabled', count: ff.disabled, color: 'bg-neutral-100 text-neutral-500' },
            ].map(f => (
              <div key={f.label} className="text-center">
                <span className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-lg font-bold ${f.color}`}>{f.count}</span>
                <p className="text-xs text-neutral-500 mt-1">{f.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Integration Health Overview */}
      <div className="bg-white rounded-xl border border-neutral-200 p-6">
        <h3 className="text-sm font-semibold text-neutral-900 mb-4">Integration Health</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {integrations.map(ig => (
            <div key={ig.id} className={`flex items-center gap-2 p-3 rounded-lg border ${
              ig.status === 'connected' ? 'border-emerald-200 bg-emerald-50' : 'border-neutral-200 bg-neutral-50'
            }`}>
              <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${
                ig.health_status === 'healthy' ? 'bg-emerald-500' : ig.status === 'disconnected' ? 'bg-neutral-400' : 'bg-red-500'
              }`} />
              <div className="min-w-0">
                <p className="text-xs font-medium text-neutral-800 truncate">{ig.name.split(' ').slice(0, 2).join(' ')}</p>
                <p className="text-[10px] text-neutral-500">{ig.provider}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Two-Tier Admin Explanation */}
      <div className="bg-gradient-to-r from-violet-50 to-blue-50 rounded-xl border border-violet-200 p-6">
        <h3 className="text-sm font-semibold text-violet-900 mb-3">Two-Tier Admin Architecture</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-6 h-6 rounded bg-violet-600 text-white flex items-center justify-center text-xs font-bold">A</span>
              <span className="text-sm font-medium text-violet-900">App Admin (This Page)</span>
            </div>
            <ul className="space-y-1 text-xs text-violet-700">
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-violet-400" />Platform-level API keys (OpenAI, Twilio, SendGrid)</li>
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-violet-400" />Global Slack app OAuth credentials</li>
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-violet-400" />Feature flags &amp; license limits</li>
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-violet-400" />System health &amp; usage monitoring</li>
            </ul>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-6 h-6 rounded bg-blue-600 text-white flex items-center justify-center text-xs font-bold">C</span>
              <span className="text-sm font-medium text-blue-900">Company Admin</span>
            </div>
            <ul className="space-y-1 text-xs text-blue-700">
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-blue-400" />Per-org Slack workspace connections</li>
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-blue-400" />Company WhatsApp/Telegram numbers</li>
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-blue-400" />Notification routing rules</li>
              <li className="flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-blue-400" />Email agent behavior &amp; branding</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Integrations Tab ────────────────────────────────────────
const IntegrationsTab: React.FC = () => {
  const [filter, setFilter] = useState<string>('all');
  const types = ['all', ...Array.from(new Set(integrations.map(i => i.integration_type)))];
  const filtered = filter === 'all' ? integrations : integrations.filter(i => i.integration_type === filter);

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        {types.map(t => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === t ? 'bg-violet-600 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            {t === 'all' ? 'All' : t.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Integration Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(ig => (
          <div key={ig.id} className={`bg-white rounded-xl border p-5 ${
            ig.status === 'connected' ? 'border-neutral-200' : 'border-dashed border-neutral-300'
          }`}>
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  ig.status === 'connected' ? 'bg-violet-100' : 'bg-neutral-100'
                }`}>
                  <svg className={`w-5 h-5 ${ig.status === 'connected' ? 'text-violet-600' : 'text-neutral-400'}`} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d={providerIcon(ig.provider)} />
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900">{ig.name}</h4>
                  <p className="text-xs text-neutral-500">{ig.provider} &middot; {ig.integration_type.replace(/_/g, ' ')}</p>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                ig.status === 'connected' ? 'bg-emerald-100 text-emerald-700' : 'bg-neutral-100 text-neutral-500'
              }`}>
                {ig.status}
              </span>
            </div>

            <p className="text-xs text-neutral-600 mb-3">{ig.description}</p>

            {ig.status === 'connected' && (
              <div className="space-y-2">
                {ig.api_key_masked && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-neutral-500">API Key:</span>
                    <code className="bg-neutral-100 px-2 py-0.5 rounded text-neutral-700 font-mono text-[10px]">{ig.api_key_masked}</code>
                  </div>
                )}
                {ig.base_url && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-neutral-500">Endpoint:</span>
                    <span className="text-neutral-700 font-mono text-[10px]">{ig.base_url}</span>
                  </div>
                )}

                {/* Rate Limits */}
                {(ig.rate_limit_per_minute || ig.rate_limit_per_day) && (
                  <div className="flex items-center gap-3 text-xs">
                    {ig.rate_limit_per_minute && <span className="text-neutral-500">{ig.rate_limit_per_minute}/min</span>}
                    {ig.rate_limit_per_day && <span className="text-neutral-500">{ig.rate_limit_per_day.toLocaleString()}/day</span>}
                  </div>
                )}

                {/* Usage Stats */}
                {ig.usage_today && (
                  <div className="flex items-center gap-3 text-xs mt-1">
                    <span className="text-blue-600 font-medium">{ig.usage_today.requests.toLocaleString()} requests today</span>
                    <span className="text-neutral-400">{(ig.usage_today.tokens / 1000).toFixed(0)}K tokens</span>
                  </div>
                )}

                {ig.orgs_connected !== undefined && (
                  <span className="inline-block text-xs text-blue-600 font-medium">{ig.orgs_connected} orgs connected</span>
                )}

                {/* Availability */}
                <div className="flex items-center gap-2 pt-1">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                    ig.available_to_all_orgs ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
                  }`}>
                    {ig.available_to_all_orgs ? 'All Organizations' : `Restricted (${ig.allowed_org_ids?.length || 0} orgs)`}
                  </span>
                  {ig.health_status && (
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                      ig.health_status === 'healthy' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'
                    }`}>
                      {ig.health_status}
                    </span>
                  )}
                </div>

                {/* Config Preview */}
                {ig.config_json && (
                  <details className="mt-2">
                    <summary className="text-[10px] text-neutral-400 cursor-pointer hover:text-neutral-600">View config</summary>
                    <pre className="mt-1 bg-neutral-50 border border-neutral-200 rounded p-2 text-[10px] text-neutral-600 overflow-x-auto max-h-32">
                      {JSON.stringify(ig.config_json, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {ig.status === 'disconnected' && (
              <button className="mt-2 w-full px-3 py-2 bg-violet-600 text-white text-xs font-medium rounded-lg hover:bg-violet-700 transition-colors">
                Connect {ig.name.split(' ')[0]}
              </button>
            )}

            {/* Action Buttons */}
            {ig.status === 'connected' && (
              <div className="flex items-center gap-2 mt-3 pt-3 border-t border-neutral-100">
                <button className="px-3 py-1.5 bg-neutral-100 text-neutral-700 text-xs rounded-lg hover:bg-neutral-200 transition-colors">Test</button>
                <button className="px-3 py-1.5 bg-neutral-100 text-neutral-700 text-xs rounded-lg hover:bg-neutral-200 transition-colors">Edit</button>
                <button className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                  ig.is_active ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'
                }`}>
                  {ig.is_active ? 'Disable' : 'Enable'}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add New */}
      <button className="w-full py-4 border-2 border-dashed border-neutral-300 rounded-xl text-neutral-500 text-sm hover:border-violet-400 hover:text-violet-600 transition-colors">
        + Add Platform Integration
      </button>
    </div>
  );
};

// ─── Feature Flags Tab ───────────────────────────────────────
const FeatureFlagsTab: React.FC = () => {
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const categories = ['all', ...Array.from(new Set(featureFlags.map(f => f.category)))];
  const filtered = categoryFilter === 'all' ? featureFlags : featureFlags.filter(f => f.category === categoryFilter);

  const statusColor = (status: string) => {
    if (status === 'enabled') return 'bg-emerald-100 text-emerald-700';
    if (status === 'beta') return 'bg-amber-100 text-amber-700';
    return 'bg-neutral-100 text-neutral-500';
  };

  return (
    <div className="space-y-4">
      {/* Category Filters */}
      <div className="flex items-center gap-2">
        {categories.map(c => (
          <button
            key={c}
            onClick={() => setCategoryFilter(c)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              categoryFilter === c ? 'bg-violet-600 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            {c === 'all' ? 'All' : c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
      </div>

      {/* Flag Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Feature</th>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Category</th>
              <th className="text-center px-5 py-3 text-xs font-medium text-neutral-500">Status</th>
              <th className="text-center px-5 py-3 text-xs font-medium text-neutral-500">Rollout</th>
              <th className="text-center px-5 py-3 text-xs font-medium text-neutral-500">Restriction</th>
              <th className="text-right px-5 py-3 text-xs font-medium text-neutral-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {filtered.map(flag => (
              <tr key={flag.id} className="hover:bg-neutral-50 transition-colors">
                <td className="px-5 py-4">
                  <p className="font-medium text-neutral-900">{flag.name}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{flag.description}</p>
                  <code className="text-[10px] text-violet-500 font-mono">{flag.flag_key}</code>
                </td>
                <td className="px-5 py-4">
                  <span className="px-2 py-0.5 bg-neutral-100 text-neutral-600 rounded text-xs">{flag.category}</span>
                </td>
                <td className="px-5 py-4 text-center">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColor(flag.status)}`}>{flag.status}</span>
                </td>
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2 justify-center">
                    <div className="w-16 bg-neutral-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${flag.status === 'enabled' ? 'bg-emerald-500' : flag.status === 'beta' ? 'bg-amber-500' : 'bg-neutral-300'}`}
                        style={{ width: `${flag.rollout_percentage}%` }}
                      />
                    </div>
                    <span className="text-xs text-neutral-600 w-8 text-right">{flag.rollout_percentage}%</span>
                  </div>
                </td>
                <td className="px-5 py-4 text-center">
                  {flag.allowed_org_ids ? (
                    <span className="px-2 py-0.5 bg-amber-50 text-amber-600 rounded text-[10px] font-medium">
                      {flag.allowed_org_ids.length} org{flag.allowed_org_ids.length !== 1 ? 's' : ''}
                    </span>
                  ) : (
                    <span className="text-[10px] text-neutral-400">All orgs</span>
                  )}
                </td>
                <td className="px-5 py-4 text-right">
                  <div className="flex items-center gap-1 justify-end">
                    {flag.status !== 'enabled' && (
                      <button className="px-2.5 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-medium rounded hover:bg-emerald-100 transition-colors">Enable</button>
                    )}
                    {flag.status !== 'disabled' && (
                      <button className="px-2.5 py-1 bg-red-50 text-red-600 text-[10px] font-medium rounded hover:bg-red-100 transition-colors">Disable</button>
                    )}
                    <button className="px-2.5 py-1 bg-neutral-100 text-neutral-600 text-[10px] font-medium rounded hover:bg-neutral-200 transition-colors">Edit</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Feature Flag */}
      <button className="w-full py-3 border-2 border-dashed border-neutral-300 rounded-xl text-neutral-500 text-sm hover:border-violet-400 hover:text-violet-600 transition-colors">
        + Create Feature Flag
      </button>
    </div>
  );
};

// ─── License & Security Tab ─────────────────────────────────
const LicenseTab: React.FC = () => {
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const categories = ['all', 'limits', 'security', 'compliance'];
  const filtered = categoryFilter === 'all' ? licenseConfigs : licenseConfigs.filter(c => c.category === categoryFilter);

  const categoryColor = (cat: string) => {
    if (cat === 'limits') return 'bg-blue-100 text-blue-700';
    if (cat === 'security') return 'bg-red-100 text-red-700';
    return 'bg-emerald-100 text-emerald-700';
  };

  return (
    <div className="space-y-4">
      {/* Category Filters */}
      <div className="flex items-center gap-2">
        {categories.map(c => (
          <button
            key={c}
            onClick={() => setCategoryFilter(c)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              categoryFilter === c ? 'bg-violet-600 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            {c === 'all' ? 'All' : c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
      </div>

      {/* Config Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(cfg => (
          <div key={cfg.config_key} className="bg-white rounded-xl border border-neutral-200 p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-900">{cfg.description}</p>
                <code className="text-[10px] text-neutral-400 font-mono">{cfg.config_key}</code>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${categoryColor(cfg.category)}`}>
                {cfg.category}
              </span>
            </div>

            <div className="mt-3 flex items-center gap-3">
              {cfg.config_type === 'bool' ? (
                <div className="flex items-center gap-2">
                  <div className={`relative w-10 h-5 rounded-full cursor-pointer transition-colors ${
                    cfg.config_value === 'true' ? 'bg-violet-600' : 'bg-neutral-300'
                  }`}>
                    <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                      cfg.config_value === 'true' ? 'translate-x-5' : 'translate-x-0.5'
                    }`} />
                  </div>
                  <span className="text-sm font-medium text-neutral-700">{cfg.config_value === 'true' ? 'Enabled' : 'Disabled'}</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 flex-1">
                  <input
                    type="text"
                    defaultValue={cfg.config_value}
                    className="flex-1 px-3 py-1.5 border border-neutral-200 rounded-lg text-sm text-neutral-800 bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    readOnly
                  />
                  <button className="px-3 py-1.5 bg-violet-100 text-violet-700 text-xs rounded-lg hover:bg-violet-200 transition-colors">
                    Edit
                  </button>
                </div>
              )}
            </div>

            {/* Usage indicator for limits */}
            {cfg.category === 'limits' && cfg.config_key === 'max_file_storage_gb' && (
              <div className="mt-3">
                <div className="w-full bg-neutral-100 rounded-full h-2">
                  <div className="bg-violet-500 h-2 rounded-full" style={{ width: `${dashboardData.storage.percent}%` }} />
                </div>
                <p className="text-[10px] text-neutral-500 mt-1">{dashboardData.storage.used_gb} GB of {cfg.config_value} GB used</p>
              </div>
            )}

            {cfg.config_key === 'max_ai_requests_per_day' && (
              <div className="mt-3">
                <div className="w-full bg-neutral-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(dashboardData.usage_today.ai_requests / parseInt(cfg.config_value)) * 100}%` }} />
                </div>
                <p className="text-[10px] text-neutral-500 mt-1">{dashboardData.usage_today.ai_requests.toLocaleString()} of {parseInt(cfg.config_value).toLocaleString()} used today</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Organizations Tab ───────────────────────────────────────
const OrganizationsTab: React.FC = () => {
  const orgs = dashboardData.organizations_summary;

  const typeColor = (type: string) => {
    if (type === 'MSP') return 'bg-violet-100 text-violet-700';
    if (type === 'CLIENT') return 'bg-blue-100 text-blue-700';
    return 'bg-emerald-100 text-emerald-700';
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        {orgs.map(org => (
          <div key={org.id} className="bg-white rounded-xl border border-neutral-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-neutral-900">{org.name}</h4>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${typeColor(org.type)}`}>{org.type}</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-2 bg-neutral-50 rounded-lg">
                <p className="text-lg font-bold text-neutral-900">{org.users}</p>
                <p className="text-[10px] text-neutral-500">Users</p>
              </div>
              <div className="text-center p-2 bg-neutral-50 rounded-lg">
                <p className="text-lg font-bold text-neutral-900">{org.integrations_active}</p>
                <p className="text-[10px] text-neutral-500">Integrations</p>
              </div>
            </div>

            {/* Connected Integrations for this org */}
            <div className="mt-3 pt-3 border-t border-neutral-100">
              <p className="text-[10px] text-neutral-500 mb-2">Active Channels</p>
              <div className="flex gap-1.5 flex-wrap">
                {['Slack', 'WhatsApp', 'Email'].slice(0, org.integrations_active > 4 ? 3 : 2).map(ch => (
                  <span key={ch} className="px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded text-[10px] font-medium">{ch}</span>
                ))}
                {org.integrations_active > 3 && (
                  <span className="px-2 py-0.5 bg-neutral-100 text-neutral-500 rounded text-[10px]">+{org.integrations_active - 3}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Feature Access Matrix */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <div className="px-5 py-3 bg-neutral-50 border-b border-neutral-200">
          <h3 className="text-sm font-semibold text-neutral-900">Feature Access Matrix</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-100">
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Feature</th>
              {orgs.map(org => (
                <th key={org.id} className="text-center px-5 py-3 text-xs font-medium text-neutral-500">{org.name}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {featureFlags.map(flag => (
              <tr key={flag.id} className="hover:bg-neutral-50">
                <td className="px-5 py-3">
                  <span className="text-neutral-800">{flag.name}</span>
                  <span className={`ml-2 px-1.5 py-0.5 rounded text-[10px] font-medium ${
                    flag.status === 'enabled' ? 'bg-emerald-50 text-emerald-600' : flag.status === 'beta' ? 'bg-amber-50 text-amber-600' : 'bg-neutral-100 text-neutral-400'
                  }`}>{flag.status}</span>
                </td>
                {orgs.map(org => {
                  const hasAccess = flag.status !== 'disabled' && (!flag.allowed_org_ids || flag.allowed_org_ids.includes(org.id));
                  return (
                    <td key={org.id} className="text-center px-5 py-3">
                      {hasAccess ? (
                        <svg className="w-5 h-5 text-emerald-500 mx-auto" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 text-neutral-300 mx-auto" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Integration Sharing */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <div className="px-5 py-3 bg-neutral-50 border-b border-neutral-200">
          <h3 className="text-sm font-semibold text-neutral-900">Integration Availability by Organization</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-100">
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Integration</th>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Provider</th>
              <th className="text-center px-5 py-3 text-xs font-medium text-neutral-500">Status</th>
              <th className="text-center px-5 py-3 text-xs font-medium text-neutral-500">Availability</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {integrations.map(ig => (
              <tr key={ig.id} className="hover:bg-neutral-50">
                <td className="px-5 py-3 font-medium text-neutral-800">{ig.name}</td>
                <td className="px-5 py-3 text-neutral-600">{ig.provider}</td>
                <td className="px-5 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                    ig.status === 'connected' ? 'bg-emerald-100 text-emerald-700' : 'bg-neutral-100 text-neutral-500'
                  }`}>{ig.status}</span>
                </td>
                <td className="px-5 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                    ig.available_to_all_orgs ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
                  }`}>
                    {ig.available_to_all_orgs ? 'All Orgs' : `${ig.allowed_org_ids?.length || 0} orgs`}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AppAdminConfig;
