import React, { useState } from 'react';

/* ─── type helpers ─── */
const fmt = (n: number) => '$' + n.toLocaleString();
const typeColors: Record<string, string> = {
  msa: 'bg-blue-100 text-blue-800', nda: 'bg-violet-100 text-violet-800',
  sow: 'bg-emerald-100 text-emerald-800', po: 'bg-amber-100 text-amber-800',
  staffing: 'bg-rose-100 text-rose-800', non_compete: 'bg-red-100 text-red-800',
  custom: 'bg-neutral-100 text-neutral-800',
};
const statusColors: Record<string, string> = {
  draft: 'bg-neutral-100 text-neutral-700', pending_review: 'bg-yellow-100 text-yellow-800',
  pending_signature: 'bg-blue-100 text-blue-800', changes_requested: 'bg-orange-100 text-orange-800',
  partially_signed: 'bg-indigo-100 text-indigo-800', fully_executed: 'bg-emerald-100 text-emerald-800',
  active: 'bg-green-100 text-green-800', expired: 'bg-red-100 text-red-800', voided: 'bg-neutral-200 text-neutral-600',
};

/* ─── mock data (matches api/v1/agreements.py) ─── */
const signatories = [
  { id: 1, name: 'Robert Chen', designation: 'CEO & Managing Director', email: 'robert.chen@hotgigs.com', phone: '+1-555-0101', is_default: true, can_sign_types: null as string[] | null, max_contract_value: null as number | null, is_active: true },
  { id: 2, name: 'Lisa Park', designation: 'VP of Operations', email: 'lisa.park@hotgigs.com', phone: '+1-555-0102', is_default: false, can_sign_types: ['sow', 'po', 'staffing', 'rate_card'], max_contract_value: 500000, is_active: true },
  { id: 3, name: 'David Martinez', designation: 'Legal Counsel', email: 'david.martinez@hotgigs.com', phone: '+1-555-0103', is_default: false, can_sign_types: ['msa', 'nda', 'non_compete', 'ip_assignment'], max_contract_value: null, is_active: true },
];

const templates = [
  { id: 1, name: 'Master Service Agreement — Standard', agreement_type: 'msa', category: 'client', description: 'Standard MSA for staffing engagements with clients.', version: '3.2', is_active: true, is_default: true, auto_sign_sender: true, default_signatory_id: 1, requires_witness: false, requires_notary: false, variables: 9, usage_count: 24, created_by: 'Robert Chen', updated_at: '2026-02-15', tags: ['client', 'staffing', 'standard'] },
  { id: 2, name: 'Non-Disclosure Agreement — Mutual', agreement_type: 'nda', category: 'general', description: 'Mutual NDA for protecting confidential information.', version: '2.1', is_active: true, is_default: true, auto_sign_sender: true, default_signatory_id: 3, requires_witness: false, requires_notary: false, variables: 7, usage_count: 38, created_by: 'David Martinez', updated_at: '2026-01-20', tags: ['nda', 'mutual'] },
  { id: 3, name: 'Statement of Work — IT Staffing', agreement_type: 'sow', category: 'client', description: 'SOW for IT staffing projects with scope, rates, deliverables.', version: '2.0', is_active: true, is_default: true, auto_sign_sender: true, default_signatory_id: 2, requires_witness: false, requires_notary: false, variables: 11, usage_count: 15, created_by: 'Lisa Park', updated_at: '2026-03-01', tags: ['sow', 'it', 'staffing'] },
  { id: 4, name: 'Purchase Order — Standard', agreement_type: 'po', category: 'supplier', description: 'Standard PO for procurement of staffing services.', version: '1.5', is_active: true, is_default: true, auto_sign_sender: true, default_signatory_id: 2, requires_witness: false, requires_notary: false, variables: 8, usage_count: 31, created_by: 'Lisa Park', updated_at: '2026-02-28', tags: ['po', 'supplier'] },
  { id: 5, name: 'Supplier Staffing Agreement', agreement_type: 'staffing', category: 'supplier', description: 'Agreement with staffing suppliers for contract resources.', version: '2.3', is_active: true, is_default: false, auto_sign_sender: true, default_signatory_id: 1, requires_witness: false, requires_notary: false, variables: 8, usage_count: 8, created_by: 'Robert Chen', updated_at: '2026-01-10', tags: ['supplier', 'staffing'] },
  { id: 6, name: 'Non-Compete Agreement — Associate', agreement_type: 'non_compete', category: 'associate', description: 'Non-compete/non-solicitation for placed associates.', version: '1.2', is_active: true, is_default: true, auto_sign_sender: true, default_signatory_id: 3, requires_witness: true, requires_notary: false, variables: 6, usage_count: 12, created_by: 'David Martinez', updated_at: '2026-02-05', tags: ['non-compete', 'associate'] },
];

const agreements = [
  { id: 1, agreement_number: 'AGR-2026-0001', template_id: 1, agreement_type: 'msa', title: 'Master Service Agreement — TechCorp Inc', status: 'fully_executed', sender_name: 'Robert Chen', recipient_org_name: 'TechCorp Inc', recipient_name: 'Sarah Mitchell', recipient_email: 'sarah.m@techcorp.com', effective_date: '2025-06-01', expiry_date: '2026-05-31', contract_value: 2400000, sender_signed: true, sender_signed_at: '2025-05-28', recipient_signed: true, recipient_signed_at: '2025-05-29', sent_at: '2025-05-28' },
  { id: 2, agreement_number: 'AGR-2026-0002', template_id: 2, agreement_type: 'nda', title: 'Mutual NDA — MedFirst Health', status: 'fully_executed', sender_name: 'David Martinez', recipient_org_name: 'MedFirst Health', recipient_name: 'Dr. James Wilson', recipient_email: 'jwilson@medfirst.com', effective_date: '2025-08-01', expiry_date: '2027-07-31', contract_value: null as number | null, sender_signed: true, sender_signed_at: '2025-07-28', recipient_signed: true, recipient_signed_at: '2025-07-29', sent_at: '2025-07-28' },
  { id: 3, agreement_number: 'AGR-2026-0015', template_id: 3, agreement_type: 'sow', title: 'SOW — Cloud Migration Project (TechCorp)', status: 'pending_signature', sender_name: 'Lisa Park', recipient_org_name: 'TechCorp Inc', recipient_name: 'Mike Johnson', recipient_email: 'mike.j@techcorp.com', effective_date: '2026-04-01', expiry_date: '2026-09-30', contract_value: 485000, sender_signed: true, sender_signed_at: '2026-03-12', recipient_signed: false, recipient_signed_at: null as string | null, sent_at: '2026-03-12' },
  { id: 4, agreement_number: 'AGR-2026-0018', template_id: 4, agreement_type: 'po', title: 'PO — StaffPro Q2 Staffing Services', status: 'changes_requested', sender_name: 'Lisa Park', recipient_org_name: 'StaffPro Solutions', recipient_name: 'Karen White', recipient_email: 'karen.w@staffpro.com', effective_date: '2026-04-01', expiry_date: '2026-06-30', contract_value: 225000, sender_signed: true, sender_signed_at: '2026-03-10', recipient_signed: false, recipient_signed_at: null, sent_at: '2026-03-10' },
  { id: 5, agreement_number: 'AGR-2026-0020', template_id: 5, agreement_type: 'staffing', title: 'Staffing Agreement — CodeForce Inc', status: 'pending_review', sender_name: 'Robert Chen', recipient_org_name: 'CodeForce Inc', recipient_name: 'Alex Petrov', recipient_email: 'alex.p@codeforce.io', effective_date: '2026-04-01', expiry_date: '2027-03-31', contract_value: 1200000, sender_signed: false, sender_signed_at: null, recipient_signed: false, recipient_signed_at: null, sent_at: null as string | null },
  { id: 6, agreement_number: 'AGR-2026-0022', template_id: 2, agreement_type: 'nda', title: 'Mutual NDA — BuildRight Construction', status: 'draft', sender_name: 'David Martinez', recipient_org_name: 'BuildRight Construction', recipient_name: 'Tom Hayes', recipient_email: 'thayes@buildright.com', effective_date: null as string | null, expiry_date: null, contract_value: null, sender_signed: false, sender_signed_at: null, recipient_signed: false, recipient_signed_at: null, sent_at: null },
];

const dashboard = {
  total_agreements: 22,
  by_status: { draft: 3, pending_review: 2, changes_requested: 1, pending_signature: 4, partially_signed: 1, fully_executed: 8, active: 2, expired: 1 } as Record<string, number>,
  by_type: { msa: 5, nda: 6, sow: 4, po: 3, staffing: 2, non_compete: 1, custom: 1 } as Record<string, number>,
  signing_metrics: { avg_time_to_sign_hours: 28.5, completion_rate: 87.5, change_request_rate: 12.5 },
  expiring_soon: [{ agreement_number: 'AGR-2026-0001', title: 'MSA — TechCorp Inc', expiry_date: '2026-05-31', days_remaining: 78 }],
  recent_activity: [
    { action: 'change_requested', agreement: 'AGR-2026-0018', by: 'Karen White', at: '2026-03-11' },
    { action: 'sent', agreement: 'AGR-2026-0015', by: 'Lisa Park', at: '2026-03-12' },
    { action: 'drafted', agreement: 'AGR-2026-0022', by: 'David Martinez', at: '2026-03-13' },
  ],
};

const tabs = ['Dashboard', 'Agreements', 'Templates', 'Signatories'] as const;
type Tab = typeof tabs[number];

/* ─────────────────────────────────────────────── */
/*  COMPONENT                                      */
/* ─────────────────────────────────────────────── */
export const AgreementCenter: React.FC = () => {
  const [tab, setTab] = useState<Tab>('Dashboard');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [expandedTemplate, setExpandedTemplate] = useState<number | null>(null);
  const [expandedAgreement, setExpandedAgreement] = useState<number | null>(null);

  /* ─── Dashboard Tab ─── */
  const DashboardTab = () => (
    <div className="space-y-6">
      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Agreements', value: dashboard.total_agreements, color: 'text-blue-700' },
          { label: 'Avg Sign Time', value: `${dashboard.signing_metrics.avg_time_to_sign_hours}h`, color: 'text-violet-700' },
          { label: 'Completion Rate', value: `${dashboard.signing_metrics.completion_rate}%`, color: 'text-emerald-700' },
          { label: 'Change Request Rate', value: `${dashboard.signing_metrics.change_request_rate}%`, color: 'text-amber-700' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Status pipeline */}
      <div className="bg-white rounded-xl border border-neutral-200 p-6">
        <h3 className="text-sm font-semibold text-neutral-900 mb-4">Agreement Pipeline</h3>
        <div className="flex gap-2">
          {Object.entries(dashboard.by_status).map(([status, count]) => (
            <div key={status} className="flex-1 text-center">
              <div className="text-lg font-bold text-neutral-900">{count}</div>
              <div className={`text-[10px] px-2 py-0.5 rounded-full inline-block mt-1 ${statusColors[status] || 'bg-neutral-100 text-neutral-700'}`}>
                {status.replace(/_/g, ' ')}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* By Type + Expiring + Activity */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">By Type</h3>
          <div className="space-y-2">
            {Object.entries(dashboard.by_type).map(([t, c]) => (
              <div key={t} className="flex items-center justify-between">
                <span className={`text-xs px-2 py-0.5 rounded-full ${typeColors[t] || 'bg-neutral-100 text-neutral-800'}`}>{t.toUpperCase()}</span>
                <span className="text-sm font-semibold text-neutral-900">{c}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Expiring Soon</h3>
          {dashboard.expiring_soon.map(e => (
            <div key={e.agreement_number} className="p-3 bg-red-50 rounded-lg border border-red-200">
              <p className="text-sm font-medium text-red-800">{e.title}</p>
              <div className="flex justify-between mt-1 text-xs text-red-600">
                <span>{e.agreement_number}</span>
                <span className="font-semibold">{e.days_remaining} days</span>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {dashboard.recent_activity.map((a, i) => (
              <div key={i} className="flex items-start gap-2">
                <div className={`w-2 h-2 rounded-full mt-1.5 ${a.action === 'change_requested' ? 'bg-orange-500' : a.action === 'sent' ? 'bg-blue-500' : 'bg-neutral-400'}`} />
                <div className="text-xs">
                  <span className="font-medium text-neutral-900">{a.by}</span>
                  <span className="text-neutral-500"> {a.action.replace(/_/g, ' ')} </span>
                  <span className="text-neutral-700 font-medium">{a.agreement}</span>
                  <p className="text-neutral-400 mt-0.5">{a.at}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  /* ─── Templates Tab ─── */
  const TemplatesTab = () => {
    const filtered = templates.filter(t => typeFilter === 'all' || t.agreement_type === typeFilter);
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {['all', 'msa', 'nda', 'sow', 'po', 'staffing', 'non_compete'].map(f => (
              <button key={f} onClick={() => setTypeFilter(f)}
                className={`px-3 py-1 text-xs rounded-full border ${typeFilter === f ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50'}`}>
                {f === 'all' ? 'All' : f.toUpperCase()}
              </button>
            ))}
          </div>
          <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">+ New Template</button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map(t => (
            <div key={t.id} className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
              <div className="p-5 cursor-pointer" onClick={() => setExpandedTemplate(expandedTemplate === t.id ? null : t.id)}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${typeColors[t.agreement_type]}`}>{t.agreement_type.toUpperCase()}</span>
                      <span className="text-[10px] text-neutral-400">v{t.version}</span>
                      {t.is_default && <span className="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-700 rounded">DEFAULT</span>}
                    </div>
                    <h4 className="text-sm font-semibold text-neutral-900 mt-2">{t.name}</h4>
                    <p className="text-xs text-neutral-500 mt-1">{t.description}</p>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-lg font-bold text-violet-700">{t.usage_count}</p>
                    <p className="text-[10px] text-neutral-400">uses</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-3 text-xs text-neutral-500">
                  <span>{t.variables} fields</span>
                  <span>Category: {t.category}</span>
                  <span>By {t.created_by}</span>
                  <span>Updated {t.updated_at}</span>
                </div>
              </div>

              {expandedTemplate === t.id && (
                <div className="border-t border-neutral-100 p-5 bg-neutral-50">
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <p className="text-neutral-500 mb-1">Signing Config</p>
                      <div className="space-y-1">
                        <div className="flex justify-between"><span>Auto-sign sender:</span><span className={t.auto_sign_sender ? 'text-emerald-600 font-medium' : 'text-neutral-400'}>{t.auto_sign_sender ? 'Yes' : 'No'}</span></div>
                        <div className="flex justify-between"><span>Default signatory:</span><span className="font-medium">{signatories.find(s => s.id === t.default_signatory_id)?.name}</span></div>
                        <div className="flex justify-between"><span>Requires witness:</span><span>{t.requires_witness ? 'Yes' : 'No'}</span></div>
                        <div className="flex justify-between"><span>Requires notary:</span><span>{t.requires_notary ? 'Yes' : 'No'}</span></div>
                      </div>
                    </div>
                    <div>
                      <p className="text-neutral-500 mb-1">Tags</p>
                      <div className="flex flex-wrap gap-1">
                        {t.tags.map(tag => (
                          <span key={tag} className="px-2 py-0.5 bg-neutral-200 text-neutral-700 rounded text-[10px]">{tag}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="px-3 py-1.5 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700">Use Template</button>
                    <button className="px-3 py-1.5 bg-white text-neutral-700 text-xs rounded-lg border border-neutral-200 hover:bg-neutral-50">Edit</button>
                    <button className="px-3 py-1.5 bg-white text-neutral-700 text-xs rounded-lg border border-neutral-200 hover:bg-neutral-50">Clone</button>
                    <button className="px-3 py-1.5 bg-white text-neutral-700 text-xs rounded-lg border border-neutral-200 hover:bg-neutral-50">Preview</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  /* ─── Agreements Tab ─── */
  const AgreementsTab = () => {
    const filtered = agreements
      .filter(a => typeFilter === 'all' || a.agreement_type === typeFilter)
      .filter(a => statusFilter === 'all' || a.status === statusFilter);
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex gap-2 flex-wrap">
            <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} className="px-3 py-1.5 border border-neutral-200 rounded-lg text-xs bg-white">
              <option value="all">All Types</option>
              {['msa', 'nda', 'sow', 'po', 'staffing', 'non_compete'].map(t => <option key={t} value={t}>{t.toUpperCase()}</option>)}
            </select>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="px-3 py-1.5 border border-neutral-200 rounded-lg text-xs bg-white">
              <option value="all">All Status</option>
              {['draft', 'pending_review', 'pending_signature', 'changes_requested', 'fully_executed', 'expired'].map(s => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
          <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">+ New Agreement</button>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-neutral-50 border-b border-neutral-200">
                <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Agreement</th>
                <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Type</th>
                <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Recipient</th>
                <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Value</th>
                <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Status</th>
                <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Signatures</th>
                <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Dates</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(a => (
                <React.Fragment key={a.id}>
                  <tr className="border-b border-neutral-100 hover:bg-neutral-50 cursor-pointer" onClick={() => setExpandedAgreement(expandedAgreement === a.id ? null : a.id)}>
                    <td className="py-3 px-4">
                      <p className="text-sm font-medium text-neutral-900">{a.title}</p>
                      <p className="text-[10px] text-neutral-400 mt-0.5">{a.agreement_number}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full ${typeColors[a.agreement_type]}`}>{a.agreement_type.toUpperCase()}</span>
                    </td>
                    <td className="py-3 px-4">
                      <p className="text-sm text-neutral-900">{a.recipient_org_name}</p>
                      <p className="text-[10px] text-neutral-500">{a.recipient_name}</p>
                    </td>
                    <td className="py-3 px-4 text-sm font-medium text-neutral-900">{a.contract_value ? fmt(a.contract_value) : '—'}</td>
                    <td className="py-3 px-4">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full ${statusColors[a.status]}`}>{a.status.replace(/_/g, ' ')}</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <span className={`w-4 h-4 rounded-full text-[9px] flex items-center justify-center font-bold ${a.sender_signed ? 'bg-emerald-500 text-white' : 'bg-neutral-200 text-neutral-500'}`}>S</span>
                        <span className={`w-4 h-4 rounded-full text-[9px] flex items-center justify-center font-bold ${a.recipient_signed ? 'bg-emerald-500 text-white' : 'bg-neutral-200 text-neutral-500'}`}>R</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-xs text-neutral-500">
                      {a.effective_date && <p>Eff: {a.effective_date}</p>}
                      {a.expiry_date && <p>Exp: {a.expiry_date}</p>}
                    </td>
                  </tr>
                  {expandedAgreement === a.id && (
                    <tr><td colSpan={7} className="bg-neutral-50 p-4">
                      <div className="grid grid-cols-3 gap-6 text-xs">
                        <div>
                          <p className="font-semibold text-neutral-700 mb-2">Sender</p>
                          <p className="text-neutral-900">{a.sender_name}</p>
                          <p className="text-neutral-500">HotGigs MSP</p>
                          {a.sender_signed_at && <p className="text-emerald-600 mt-1">Signed: {a.sender_signed_at}</p>}
                        </div>
                        <div>
                          <p className="font-semibold text-neutral-700 mb-2">Recipient</p>
                          <p className="text-neutral-900">{a.recipient_name}</p>
                          <p className="text-neutral-500">{a.recipient_org_name}</p>
                          <p className="text-neutral-500">{a.recipient_email}</p>
                          {a.recipient_signed_at && <p className="text-emerald-600 mt-1">Signed: {a.recipient_signed_at}</p>}
                        </div>
                        <div>
                          <p className="font-semibold text-neutral-700 mb-2">Actions</p>
                          <div className="flex flex-wrap gap-2">
                            {a.status === 'draft' && <button className="px-3 py-1 bg-violet-600 text-white rounded text-xs">Send for Signature</button>}
                            {a.status === 'changes_requested' && <button className="px-3 py-1 bg-orange-600 text-white rounded text-xs">Review Changes</button>}
                            {a.status === 'pending_signature' && <button className="px-3 py-1 bg-blue-600 text-white rounded text-xs">Send Reminder</button>}
                            <button className="px-3 py-1 bg-white text-neutral-700 border border-neutral-200 rounded text-xs">View Document</button>
                            <button className="px-3 py-1 bg-white text-neutral-700 border border-neutral-200 rounded text-xs">Audit Trail</button>
                          </div>
                        </div>
                      </div>
                    </td></tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  /* ─── Signatories Tab ─── */
  const SignatoriesTab = () => (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">+ Add Signatory</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {signatories.map(s => (
          <div key={s.id} className={`bg-white rounded-xl border p-5 ${s.is_default ? 'border-violet-300 ring-1 ring-violet-200' : 'border-neutral-200'}`}>
            {s.is_default && <span className="text-[10px] px-2 py-0.5 bg-violet-100 text-violet-700 rounded-full font-medium">DEFAULT SIGNATORY</span>}
            <div className="flex items-center gap-3 mt-3">
              <div className="w-12 h-12 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 font-bold text-lg">
                {s.name.split(' ').map(w => w[0]).join('')}
              </div>
              <div>
                <p className="text-sm font-semibold text-neutral-900">{s.name}</p>
                <p className="text-xs text-neutral-500">{s.designation}</p>
              </div>
            </div>
            <div className="mt-4 space-y-2 text-xs">
              <div className="flex justify-between"><span className="text-neutral-500">Email</span><span className="text-neutral-700">{s.email}</span></div>
              <div className="flex justify-between"><span className="text-neutral-500">Phone</span><span className="text-neutral-700">{s.phone}</span></div>
              <div className="flex justify-between"><span className="text-neutral-500">Can Sign</span>
                <span className="text-neutral-700">{s.can_sign_types ? s.can_sign_types.map(t => t.toUpperCase()).join(', ') : 'All Types'}</span>
              </div>
              <div className="flex justify-between"><span className="text-neutral-500">Max Value</span>
                <span className="text-neutral-700">{s.max_contract_value ? fmt(s.max_contract_value) : 'Unlimited'}</span>
              </div>
            </div>
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-neutral-100">
              <span className={`text-[10px] px-2 py-0.5 rounded-full ${s.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-neutral-100 text-neutral-500'}`}>{s.is_active ? 'Active' : 'Inactive'}</span>
              <div className="flex gap-2">
                <button className="text-xs text-violet-600 hover:underline">Edit</button>
                <button className="text-xs text-neutral-500 hover:underline">Signature</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Agreement Center</h1>
          <p className="text-neutral-500 mt-1">Manage MSA, NDA, SOW, PO, and all agreement types with e-signature workflows</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
        {tabs.map(t => (
          <button key={t} onClick={() => { setTab(t); setTypeFilter('all'); setStatusFilter('all'); }}
            className={`px-4 py-2 text-sm rounded-md transition-all ${tab === t ? 'bg-white text-neutral-900 shadow-sm font-medium' : 'text-neutral-600 hover:text-neutral-900'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Dashboard' && <DashboardTab />}
      {tab === 'Templates' && <TemplatesTab />}
      {tab === 'Agreements' && <AgreementsTab />}
      {tab === 'Signatories' && <SignatoriesTab />}
    </div>
  );
};

export default AgreementCenter;
