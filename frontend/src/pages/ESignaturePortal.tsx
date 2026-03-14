import React, { useState } from 'react';

const fmt = (n: number) => '$' + n.toLocaleString();

const statusColors: Record<string, string> = {
  pending_signature: 'bg-blue-100 text-blue-800', changes_requested: 'bg-orange-100 text-orange-800',
  fully_executed: 'bg-emerald-100 text-emerald-800', voided: 'bg-neutral-200 text-neutral-600',
  pending_review: 'bg-yellow-100 text-yellow-800', draft: 'bg-neutral-100 text-neutral-700',
};
const typeColors: Record<string, string> = {
  msa: 'bg-blue-100 text-blue-800', nda: 'bg-violet-100 text-violet-800',
  sow: 'bg-emerald-100 text-emerald-800', po: 'bg-amber-100 text-amber-800',
  staffing: 'bg-rose-100 text-rose-800', non_compete: 'bg-red-100 text-red-800',
};

/* ─── mock: agreements needing action ─── */
const pendingAgreements = [
  {
    id: 3, agreement_number: 'AGR-2026-0015', agreement_type: 'sow',
    title: 'SOW — Cloud Migration Project (TechCorp)',
    status: 'pending_signature',
    sender_org: 'HotGigs MSP', sender_name: 'Lisa Park', sender_designation: 'VP Operations',
    sender_signed: true, sender_signed_at: '2026-03-12T11:00:00Z',
    recipient_org: 'TechCorp Inc', recipient_name: 'Mike Johnson', recipient_designation: 'Project Director',
    recipient_email: 'mike.j@techcorp.com',
    recipient_signed: false, recipient_signed_at: null as string | null,
    contract_value: 485000, effective_date: '2026-04-01', expiry_date: '2026-09-30',
    sent_at: '2026-03-12T11:05:00Z',
    content_sections: [
      { title: 'Section 1 — Parties', text: 'This Statement of Work is entered into between HotGigs MSP ("Provider") and TechCorp Inc ("Client") under the terms of MSA AGR-2026-0001.' },
      { title: 'Section 2 — Project Scope', text: 'Provider will supply qualified IT professionals to support Client\'s cloud migration initiative, including infrastructure assessment, migration planning, execution, and post-migration support.' },
      { title: 'Section 3 — Duration', text: 'This SOW is effective from April 1, 2026 through September 30, 2026.' },
      { title: 'Section 4 — Rates & Compensation', text: 'Bill Rate: $125/hr. Estimated Hours: 3,880. Not-to-exceed: $485,000. Payment Terms: Net 30.' },
      { title: 'Section 5 — Deliverables', text: 'Infrastructure audit report, migration plan, phased migration execution, system validation testing, knowledge transfer documentation.' },
      { title: 'Section 6 — Acceptance', text: 'Client shall review deliverables within 5 business days. Failure to respond constitutes acceptance.' },
    ],
  },
  {
    id: 4, agreement_number: 'AGR-2026-0018', agreement_type: 'po',
    title: 'PO — StaffPro Q2 Staffing Services',
    status: 'changes_requested',
    sender_org: 'HotGigs MSP', sender_name: 'Lisa Park', sender_designation: 'VP Operations',
    sender_signed: true, sender_signed_at: '2026-03-10T14:00:00Z',
    recipient_org: 'StaffPro Solutions', recipient_name: 'Karen White', recipient_designation: 'Account Manager',
    recipient_email: 'karen.w@staffpro.com',
    recipient_signed: false, recipient_signed_at: null,
    contract_value: 225000, effective_date: '2026-04-01', expiry_date: '2026-06-30',
    sent_at: '2026-03-10T14:05:00Z',
    content_sections: [
      { title: 'Section 1 — Parties', text: 'This Purchase Order is issued by HotGigs MSP to StaffPro Solutions for Q2 2026 staffing services.' },
      { title: 'Section 2 — Services', text: 'Supplier shall provide staffing resources as requested, including .NET developers, QA engineers, and DevOps specialists.' },
      { title: 'Section 3 — Term', text: 'April 1, 2026 through June 30, 2026.' },
      { title: 'Section 4 — Payment Terms', text: 'Payment shall be made within 30 days of receipt of invoice.' },
      { title: 'Section 5 — Total Amount', text: 'Total PO value: $225,000. Invoicing shall be monthly based on actual hours worked.' },
      { title: 'Section 6 — Termination', text: 'Either party may terminate this agreement upon providing a 30-day written notice to the other party.' },
      { title: 'Section 7 — Compliance', text: 'Supplier shall maintain all required insurance and comply with applicable employment laws.' },
    ],
  },
];

const changeRequests = [
  { id: 1, agreement_id: 4, requested_by: 'Karen White', section: 'Section 4 — Payment Terms', original_text: 'Payment shall be made within 30 days of receipt of invoice.', proposed_text: 'Payment shall be made within 45 days of receipt of invoice.', reason: 'Our standard payment processing cycle requires 45 days for supplier invoices.', status: 'pending' },
  { id: 2, agreement_id: 4, requested_by: 'Karen White', section: 'Section 6 — Termination', original_text: 'Either party may terminate this agreement upon providing a 30-day written notice to the other party.', proposed_text: 'Either party may terminate with 60 days written notice.', reason: 'We need additional time to transition resources on active assignments.', status: 'pending' },
];

const auditTrail = [
  { action: 'created', actor: 'Lisa Park', timestamp: '2026-03-10T13:50:00Z', details: 'Agreement created from PO template' },
  { action: 'sender_signed', actor: 'Lisa Park', timestamp: '2026-03-10T14:00:00Z', details: 'Auto-signed as sender' },
  { action: 'sent', actor: 'System', timestamp: '2026-03-10T14:05:00Z', details: 'Sent to karen.w@staffpro.com' },
  { action: 'viewed', actor: 'Karen White', timestamp: '2026-03-11T09:30:00Z', details: 'Recipient viewed agreement' },
  { action: 'change_requested', actor: 'Karen White', timestamp: '2026-03-11T10:15:00Z', details: '2 change requests submitted' },
];

type View = 'inbox' | 'document';

export const ESignaturePortal: React.FC = () => {
  const [view, setView] = useState<View>('inbox');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [activeDocTab, setActiveDocTab] = useState<'document' | 'changes' | 'audit'>('document');
  const [signMode, setSignMode] = useState(false);
  const [changeRequestSection, setChangeRequestSection] = useState('');
  const [changeRequestText, setChangeRequestText] = useState('');
  const [changeRequestReason, setChangeRequestReason] = useState('');
  const [showChangeForm, setShowChangeForm] = useState(false);
  const [signedSections, setSignedSections] = useState<Set<number>>(new Set());

  const selected = pendingAgreements.find(a => a.id === selectedId);
  const relatedChanges = changeRequests.filter(cr => cr.agreement_id === selectedId);

  const openAgreement = (id: number) => { setSelectedId(id); setView('document'); setActiveDocTab('document'); setSignMode(false); setShowChangeForm(false); };

  /* ─── Inbox View ─── */
  const InboxView = () => (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Awaiting Your Signature', value: 1, color: 'text-blue-700' },
          { label: 'Changes Requested', value: 1, color: 'text-orange-700' },
          { label: 'Completed Today', value: 0, color: 'text-emerald-700' },
          { label: 'Total Pending', value: 2, color: 'text-violet-700' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-4">
            <p className="text-xs text-neutral-500">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Agreement cards */}
      <div className="space-y-4">
        {pendingAgreements.map(a => (
          <div key={a.id} className="bg-white rounded-xl border border-neutral-200 p-5 hover:shadow-md transition-shadow cursor-pointer" onClick={() => openAgreement(a.id)}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${typeColors[a.agreement_type]}`}>{a.agreement_type.toUpperCase()}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${statusColors[a.status]}`}>{a.status.replace(/_/g, ' ')}</span>
                  {a.status === 'changes_requested' && (
                    <span className="text-[10px] px-2 py-0.5 bg-orange-500 text-white rounded-full font-medium">
                      {changeRequests.filter(cr => cr.agreement_id === a.id).length} changes
                    </span>
                  )}
                </div>
                <h3 className="text-sm font-semibold text-neutral-900">{a.title}</h3>
                <p className="text-xs text-neutral-500 mt-1">{a.agreement_number}</p>
              </div>
              <div className="text-right ml-4">
                {a.contract_value && <p className="text-lg font-bold text-violet-700">{fmt(a.contract_value)}</p>}
                <p className="text-xs text-neutral-400">Sent {a.sent_at?.split('T')[0]}</p>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <div className="flex items-center gap-6 text-xs">
                <div><span className="text-neutral-500">From:</span> <span className="text-neutral-900 font-medium">{a.sender_name}</span> <span className="text-neutral-400">({a.sender_org})</span></div>
                <div><span className="text-neutral-500">To:</span> <span className="text-neutral-900 font-medium">{a.recipient_name}</span> <span className="text-neutral-400">({a.recipient_org})</span></div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <span className={`w-5 h-5 rounded-full text-[9px] flex items-center justify-center font-bold ${a.sender_signed ? 'bg-emerald-500 text-white' : 'bg-neutral-200 text-neutral-500'}`}>S</span>
                  <span className={`w-5 h-5 rounded-full text-[9px] flex items-center justify-center font-bold ${a.recipient_signed ? 'bg-emerald-500 text-white' : 'bg-neutral-200 text-neutral-500'}`}>R</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  /* ─── Document View ─── */
  const DocumentView = () => {
    if (!selected) return null;
    return (
      <div className="space-y-4">
        <button onClick={() => setView('inbox')} className="text-sm text-violet-600 hover:underline">&larr; Back to Inbox</button>

        {/* Header */}
        <div className="bg-white rounded-xl border border-neutral-200 p-5">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${typeColors[selected.agreement_type]}`}>{selected.agreement_type.toUpperCase()}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full ${statusColors[selected.status]}`}>{selected.status.replace(/_/g, ' ')}</span>
              </div>
              <h2 className="text-lg font-bold text-neutral-900">{selected.title}</h2>
              <p className="text-xs text-neutral-500 mt-1">{selected.agreement_number} | {selected.effective_date} to {selected.expiry_date}</p>
            </div>
            {selected.contract_value && <p className="text-xl font-bold text-violet-700">{fmt(selected.contract_value)}</p>}
          </div>

          {/* Parties */}
          <div className="grid grid-cols-2 gap-6 mt-4 pt-4 border-t border-neutral-100">
            <div className="p-3 bg-neutral-50 rounded-lg">
              <p className="text-[10px] text-neutral-500 uppercase tracking-wide mb-1">Sender</p>
              <p className="text-sm font-medium text-neutral-900">{selected.sender_name}</p>
              <p className="text-xs text-neutral-500">{selected.sender_designation} — {selected.sender_org}</p>
              {selected.sender_signed && (
                <div className="mt-2 flex items-center gap-1">
                  <span className="w-4 h-4 bg-emerald-500 text-white rounded-full flex items-center justify-center text-[9px]">✓</span>
                  <span className="text-[10px] text-emerald-600">Signed {selected.sender_signed_at?.split('T')[0]}</span>
                </div>
              )}
            </div>
            <div className="p-3 bg-neutral-50 rounded-lg">
              <p className="text-[10px] text-neutral-500 uppercase tracking-wide mb-1">Recipient</p>
              <p className="text-sm font-medium text-neutral-900">{selected.recipient_name}</p>
              <p className="text-xs text-neutral-500">{selected.recipient_designation} — {selected.recipient_org}</p>
              <p className="text-xs text-neutral-400">{selected.recipient_email}</p>
              {selected.recipient_signed ? (
                <div className="mt-2 flex items-center gap-1">
                  <span className="w-4 h-4 bg-emerald-500 text-white rounded-full flex items-center justify-center text-[9px]">✓</span>
                  <span className="text-[10px] text-emerald-600">Signed {selected.recipient_signed_at?.split('T')[0]}</span>
                </div>
              ) : (
                <p className="text-[10px] text-orange-600 mt-2">Awaiting signature</p>
              )}
            </div>
          </div>
        </div>

        {/* Sub-tabs */}
        <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
          {(['document', 'changes', 'audit'] as const).map(t => (
            <button key={t} onClick={() => setActiveDocTab(t)}
              className={`px-4 py-1.5 text-xs rounded-md ${activeDocTab === t ? 'bg-white text-neutral-900 shadow-sm font-medium' : 'text-neutral-600 hover:text-neutral-900'}`}>
              {t === 'document' ? 'Document' : t === 'changes' ? `Changes (${relatedChanges.length})` : 'Audit Trail'}
            </button>
          ))}
        </div>

        {/* Document content */}
        {activeDocTab === 'document' && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-neutral-200 p-6">
              {selected.content_sections.map((sec, i) => (
                <div key={i} className={`py-4 ${i > 0 ? 'border-t border-neutral-100' : ''}`}>
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-neutral-900">{sec.title}</h4>
                    {signMode && !signedSections.has(i) && (
                      <button onClick={() => setSignedSections(new Set([...signedSections, i]))}
                        className="text-[10px] px-2 py-0.5 bg-emerald-600 text-white rounded hover:bg-emerald-700">Initial</button>
                    )}
                    {signedSections.has(i) && (
                      <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded">Initialed ✓</span>
                    )}
                  </div>
                  <p className="text-sm text-neutral-700 mt-2 leading-relaxed">{sec.text}</p>
                </div>
              ))}
            </div>

            {/* Action bar */}
            <div className="bg-white rounded-xl border border-neutral-200 p-4 flex items-center justify-between">
              <div className="flex gap-2">
                {!signMode ? (
                  <>
                    <button onClick={() => setSignMode(true)}
                      className="px-4 py-2 bg-emerald-600 text-white text-sm rounded-lg hover:bg-emerald-700">Sign Agreement</button>
                    <button onClick={() => setShowChangeForm(!showChangeForm)}
                      className="px-4 py-2 bg-orange-600 text-white text-sm rounded-lg hover:bg-orange-700">Request Changes</button>
                    <button className="px-4 py-2 border border-neutral-200 text-sm rounded-lg hover:bg-neutral-50">Download PDF</button>
                  </>
                ) : (
                  <>
                    <button onClick={() => setSignMode(false)} className="px-4 py-2 border border-neutral-200 text-sm rounded-lg hover:bg-neutral-50">Cancel</button>
                    <button className="px-4 py-2 bg-emerald-600 text-white text-sm rounded-lg hover:bg-emerald-700">
                      Apply Signature & Execute
                    </button>
                  </>
                )}
              </div>
              {signMode && (
                <div className="text-xs text-neutral-500">
                  <span className="font-medium text-emerald-600">{signedSections.size}</span> of {selected.content_sections.length} sections initialed
                </div>
              )}
            </div>

            {/* Change request form */}
            {showChangeForm && (
              <div className="bg-orange-50 rounded-xl border border-orange-200 p-6">
                <h4 className="text-sm font-semibold text-orange-900 mb-4">Request a Change</h4>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-medium text-neutral-700">Section</label>
                    <select value={changeRequestSection} onChange={e => setChangeRequestSection(e.target.value)}
                      className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm bg-white">
                      <option value="">Select section...</option>
                      {selected.content_sections.map((s, i) => <option key={i} value={s.title}>{s.title}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-neutral-700">Proposed Text</label>
                    <textarea value={changeRequestText} onChange={e => setChangeRequestText(e.target.value)}
                      rows={3} className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm resize-none" placeholder="Enter your proposed changes..." />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-neutral-700">Reason</label>
                    <textarea value={changeRequestReason} onChange={e => setChangeRequestReason(e.target.value)}
                      rows={2} className="w-full mt-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm resize-none" placeholder="Why is this change needed?" />
                  </div>
                  <div className="flex gap-2">
                    <button className="px-4 py-2 bg-orange-600 text-white text-sm rounded-lg hover:bg-orange-700">Submit Change Request</button>
                    <button onClick={() => setShowChangeForm(false)} className="px-4 py-2 border border-neutral-200 text-sm rounded-lg hover:bg-neutral-50">Cancel</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Changes tab */}
        {activeDocTab === 'changes' && (
          <div className="space-y-4">
            {relatedChanges.length === 0 ? (
              <div className="bg-white rounded-xl border border-neutral-200 p-8 text-center text-neutral-500 text-sm">No change requests for this agreement.</div>
            ) : (
              relatedChanges.map(cr => (
                <div key={cr.id} className="bg-white rounded-xl border border-neutral-200 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-neutral-900">{cr.section}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full ${cr.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : cr.status === 'accepted' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                        {cr.status}
                      </span>
                    </div>
                    <span className="text-xs text-neutral-500">By {cr.requested_by}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-red-50 rounded-lg">
                      <p className="text-[10px] text-red-600 font-medium mb-1">Original Text</p>
                      <p className="text-sm text-red-900">{cr.original_text}</p>
                    </div>
                    <div className="p-3 bg-emerald-50 rounded-lg">
                      <p className="text-[10px] text-emerald-600 font-medium mb-1">Proposed Text</p>
                      <p className="text-sm text-emerald-900">{cr.proposed_text}</p>
                    </div>
                  </div>

                  <div className="mt-3 p-2 bg-neutral-50 rounded text-xs text-neutral-600">
                    <span className="font-medium">Reason:</span> {cr.reason}
                  </div>

                  {cr.status === 'pending' && (
                    <div className="flex gap-2 mt-3">
                      <button className="px-3 py-1.5 bg-emerald-600 text-white text-xs rounded-lg hover:bg-emerald-700">Accept Change</button>
                      <button className="px-3 py-1.5 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700">Reject Change</button>
                      <button className="px-3 py-1.5 border border-neutral-200 text-xs rounded-lg hover:bg-neutral-50">Counter-Propose</button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Audit trail tab */}
        {activeDocTab === 'audit' && (
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-neutral-200" />
              <div className="space-y-6">
                {auditTrail.map((entry, i) => (
                  <div key={i} className="relative pl-10">
                    <div className={`absolute left-2.5 w-3 h-3 rounded-full border-2 border-white ${
                      entry.action === 'sender_signed' ? 'bg-emerald-500' :
                      entry.action === 'change_requested' ? 'bg-orange-500' :
                      entry.action === 'sent' ? 'bg-blue-500' :
                      entry.action === 'viewed' ? 'bg-violet-500' : 'bg-neutral-400'
                    }`} />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-neutral-900">{entry.action.replace(/_/g, ' ')}</span>
                        <span className="text-xs text-neutral-400">{entry.timestamp.replace('T', ' ').replace('Z', '')}</span>
                      </div>
                      <p className="text-xs text-neutral-600 mt-0.5"><span className="font-medium">{entry.actor}</span> — {entry.details}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">E-Signature Portal</h1>
        <p className="text-neutral-500 mt-1">Review, sign, and manage agreement signatures and change requests</p>
      </div>

      {view === 'inbox' && <InboxView />}
      {view === 'document' && <DocumentView />}
    </div>
  );
};

export default ESignaturePortal;
