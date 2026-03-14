import React, { useState } from 'react';

/* ─── types ─── */
interface TemplateVariable {
  key: string; label: string; type: string; required: boolean;
  default?: string; options?: string[];
}
interface Template {
  id: number; name: string; agreement_type: string; category: string;
  description: string; version: string; auto_sign_sender: boolean;
  default_signatory_id: number; requires_witness: boolean;
  variables: TemplateVariable[];
}
interface Signatory {
  id: number; name: string; designation: string; email: string;
  can_sign_types: string[] | null; max_contract_value: number | null;
}

const typeColors: Record<string, string> = {
  msa: 'bg-blue-100 text-blue-800', nda: 'bg-violet-100 text-violet-800',
  sow: 'bg-emerald-100 text-emerald-800', po: 'bg-amber-100 text-amber-800',
  staffing: 'bg-rose-100 text-rose-800', non_compete: 'bg-red-100 text-red-800',
};

/* ─── mock data ─── */
const signatories: Signatory[] = [
  { id: 1, name: 'Robert Chen', designation: 'CEO & Managing Director', email: 'robert.chen@hotgigs.com', can_sign_types: null, max_contract_value: null },
  { id: 2, name: 'Lisa Park', designation: 'VP of Operations', email: 'lisa.park@hotgigs.com', can_sign_types: ['sow', 'po', 'staffing', 'rate_card'], max_contract_value: 500000 },
  { id: 3, name: 'David Martinez', designation: 'Legal Counsel', email: 'david.martinez@hotgigs.com', can_sign_types: ['msa', 'nda', 'non_compete', 'ip_assignment'], max_contract_value: null },
];

const templates: Template[] = [
  {
    id: 1, name: 'Master Service Agreement — Standard', agreement_type: 'msa', category: 'client',
    description: 'Standard MSA for staffing engagements with clients.', version: '3.2',
    auto_sign_sender: true, default_signatory_id: 1, requires_witness: false,
    variables: [
      { key: 'client_company_name', label: 'Client Company Name', type: 'text', required: true },
      { key: 'client_address', label: 'Client Address', type: 'textarea', required: true },
      { key: 'client_signatory_name', label: 'Client Signatory Name', type: 'text', required: true },
      { key: 'client_signatory_designation', label: 'Client Signatory Title', type: 'text', required: true },
      { key: 'client_email', label: 'Client Email', type: 'email', required: true },
      { key: 'effective_date', label: 'Effective Date', type: 'date', required: true },
      { key: 'term_months', label: 'Term (Months)', type: 'number', required: true, default: '12' },
      { key: 'payment_terms', label: 'Payment Terms', type: 'select', required: true, options: ['Net 30', 'Net 45', 'Net 60'] },
      { key: 'governing_law_state', label: 'Governing Law State', type: 'text', required: true, default: 'California' },
    ],
  },
  {
    id: 2, name: 'Non-Disclosure Agreement — Mutual', agreement_type: 'nda', category: 'general',
    description: 'Mutual NDA for protecting confidential information.', version: '2.1',
    auto_sign_sender: true, default_signatory_id: 3, requires_witness: false,
    variables: [
      { key: 'party_name', label: 'Other Party Name', type: 'text', required: true },
      { key: 'party_company', label: 'Other Party Company', type: 'text', required: false },
      { key: 'party_address', label: 'Other Party Address', type: 'textarea', required: true },
      { key: 'party_email', label: 'Other Party Email', type: 'email', required: true },
      { key: 'effective_date', label: 'Effective Date', type: 'date', required: true },
      { key: 'confidentiality_period_years', label: 'Confidentiality Period (Years)', type: 'number', required: true, default: '2' },
      { key: 'purpose', label: 'Purpose of Disclosure', type: 'textarea', required: true },
    ],
  },
  {
    id: 3, name: 'Statement of Work — IT Staffing', agreement_type: 'sow', category: 'client',
    description: 'SOW for IT staffing projects with scope, rates, deliverables.', version: '2.0',
    auto_sign_sender: true, default_signatory_id: 2, requires_witness: false,
    variables: [
      { key: 'client_company_name', label: 'Client Company', type: 'text', required: true },
      { key: 'client_signatory', label: 'Client Signatory', type: 'text', required: true },
      { key: 'client_email', label: 'Client Email', type: 'email', required: true },
      { key: 'parent_msa_number', label: 'Parent MSA Number', type: 'text', required: true },
      { key: 'project_name', label: 'Project Name', type: 'text', required: true },
      { key: 'scope_description', label: 'Scope of Work', type: 'textarea', required: true },
      { key: 'start_date', label: 'Start Date', type: 'date', required: true },
      { key: 'end_date', label: 'End Date', type: 'date', required: true },
      { key: 'bill_rate', label: 'Bill Rate ($/hr)', type: 'number', required: true },
      { key: 'estimated_hours', label: 'Estimated Hours', type: 'number', required: true },
      { key: 'not_to_exceed', label: 'Not-to-Exceed Amount ($)', type: 'number', required: false },
    ],
  },
  {
    id: 4, name: 'Purchase Order — Standard', agreement_type: 'po', category: 'supplier',
    description: 'Standard PO for procurement of staffing services.', version: '1.5',
    auto_sign_sender: true, default_signatory_id: 2, requires_witness: false,
    variables: [
      { key: 'supplier_name', label: 'Supplier Company Name', type: 'text', required: true },
      { key: 'supplier_contact', label: 'Supplier Contact Name', type: 'text', required: true },
      { key: 'supplier_email', label: 'Supplier Email', type: 'email', required: true },
      { key: 'supplier_address', label: 'Supplier Address', type: 'textarea', required: true },
      { key: 'po_description', label: 'Description of Services', type: 'textarea', required: true },
      { key: 'total_amount', label: 'Total PO Amount ($)', type: 'number', required: true },
      { key: 'payment_terms', label: 'Payment Terms', type: 'select', required: true, options: ['Net 15', 'Net 30', 'Net 45'] },
      { key: 'delivery_date', label: 'Expected Delivery Date', type: 'date', required: true },
    ],
  },
  {
    id: 5, name: 'Supplier Staffing Agreement', agreement_type: 'staffing', category: 'supplier',
    description: 'Agreement with staffing suppliers for contract resources.', version: '2.3',
    auto_sign_sender: true, default_signatory_id: 1, requires_witness: false,
    variables: [
      { key: 'supplier_name', label: 'Supplier Name', type: 'text', required: true },
      { key: 'supplier_contact', label: 'Contact Person', type: 'text', required: true },
      { key: 'supplier_email', label: 'Email', type: 'email', required: true },
      { key: 'supplier_address', label: 'Address', type: 'textarea', required: true },
      { key: 'effective_date', label: 'Effective Date', type: 'date', required: true },
      { key: 'markup_structure', label: 'Markup Structure', type: 'textarea', required: true },
      { key: 'payment_terms', label: 'Payment Terms', type: 'select', required: true, options: ['Net 30', 'Net 45'] },
      { key: 'insurance_requirements', label: 'Insurance Requirements', type: 'textarea', required: false },
    ],
  },
  {
    id: 6, name: 'Non-Compete Agreement — Associate', agreement_type: 'non_compete', category: 'associate',
    description: 'Non-compete/non-solicitation for placed associates.', version: '1.2',
    auto_sign_sender: true, default_signatory_id: 3, requires_witness: true,
    variables: [
      { key: 'associate_name', label: 'Associate Full Name', type: 'text', required: true },
      { key: 'associate_email', label: 'Associate Email', type: 'email', required: true },
      { key: 'associate_address', label: 'Associate Address', type: 'textarea', required: true },
      { key: 'client_name', label: 'Client Name', type: 'text', required: true },
      { key: 'restriction_period_months', label: 'Restriction Period (Months)', type: 'number', required: true, default: '12' },
      { key: 'geographic_scope', label: 'Geographic Scope', type: 'text', required: true, default: 'United States' },
    ],
  },
];

const steps = ['Select Template', 'Fill Details', 'Signing Options', 'Review & Send'] as const;
type Step = typeof steps[number];

export const AgreementBuilder: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [signatoryId, setSignatoryId] = useState<number>(0);
  const [autoSign, setAutoSign] = useState(true);
  const [sendImmediately, setSendImmediately] = useState(false);
  const [agreementTitle, setAgreementTitle] = useState('');
  const [contractValue, setContractValue] = useState('');
  const [sent, setSent] = useState(false);

  const selectTemplate = (t: Template) => {
    setSelectedTemplate(t);
    setSignatoryId(t.default_signatory_id);
    setAutoSign(t.auto_sign_sender);
    const defaults: Record<string, string> = {};
    t.variables.forEach(v => { if (v.default) defaults[v.key] = v.default; });
    setFormValues(defaults);
    setAgreementTitle(`${t.name} — `);
    setCurrentStep(1);
  };

  const canProceedStep1 = () => {
    if (!selectedTemplate) return false;
    return selectedTemplate.variables.filter(v => v.required).every(v => formValues[v.key]?.trim());
  };

  const handleSend = () => { setSent(true); };

  const eligibleSignatories = selectedTemplate
    ? signatories.filter(s => !s.can_sign_types || s.can_sign_types.includes(selectedTemplate.agreement_type))
    : signatories;

  /* ─── Step 0: Template Selection ─── */
  const Step0 = () => (
    <div className="space-y-4">
      <p className="text-sm text-neutral-600">Choose an agreement template to start building your document.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map(t => (
          <button key={t.id} onClick={() => selectTemplate(t)}
            className="text-left bg-white rounded-xl border border-neutral-200 p-5 hover:border-violet-400 hover:shadow-md transition-all group">
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${typeColors[t.agreement_type]}`}>{t.agreement_type.toUpperCase()}</span>
              <span className="text-[10px] text-neutral-400">v{t.version}</span>
            </div>
            <h4 className="text-sm font-semibold text-neutral-900 group-hover:text-violet-700">{t.name}</h4>
            <p className="text-xs text-neutral-500 mt-1">{t.description}</p>
            <div className="flex items-center gap-3 mt-3 text-xs text-neutral-400">
              <span>{t.variables.length} fields</span>
              <span>{t.category}</span>
              {t.auto_sign_sender && <span className="text-emerald-600">Auto-sign</span>}
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  /* ─── Step 1: Fill Details ─── */
  const Step1 = () => {
    if (!selectedTemplate) return null;
    return (
      <div className="space-y-6">
        <div className="bg-violet-50 rounded-xl border border-violet-200 p-4 flex items-center justify-between">
          <div>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${typeColors[selectedTemplate.agreement_type]}`}>{selectedTemplate.agreement_type.toUpperCase()}</span>
            <span className="text-sm font-medium text-violet-900 ml-2">{selectedTemplate.name}</span>
          </div>
          <button onClick={() => { setSelectedTemplate(null); setCurrentStep(0); }} className="text-xs text-violet-600 hover:underline">Change Template</button>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-1">Agreement Title</h3>
          <input type="text" value={agreementTitle} onChange={e => setAgreementTitle(e.target.value)}
            className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm" placeholder="Enter agreement title..." />
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Fill in Agreement Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {selectedTemplate.variables.map(v => (
              <div key={v.key} className={v.type === 'textarea' ? 'md:col-span-2' : ''}>
                <label className="block text-xs font-medium text-neutral-700 mb-1">
                  {v.label} {v.required && <span className="text-red-500">*</span>}
                </label>
                {v.type === 'textarea' ? (
                  <textarea value={formValues[v.key] || ''} onChange={e => setFormValues({ ...formValues, [v.key]: e.target.value })}
                    rows={3} className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm resize-none" placeholder={`Enter ${v.label.toLowerCase()}...`} />
                ) : v.type === 'select' ? (
                  <select value={formValues[v.key] || ''} onChange={e => setFormValues({ ...formValues, [v.key]: e.target.value })}
                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm bg-white">
                    <option value="">Select...</option>
                    {v.options?.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <input type={v.type === 'number' ? 'number' : v.type === 'date' ? 'date' : v.type === 'email' ? 'email' : 'text'}
                    value={formValues[v.key] || ''} onChange={e => setFormValues({ ...formValues, [v.key]: e.target.value })}
                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm" placeholder={v.default || `Enter ${v.label.toLowerCase()}...`} />
                )}
              </div>
            ))}
          </div>

          {/* Contract value (optional for all) */}
          <div className="mt-4 pt-4 border-t border-neutral-100">
            <label className="block text-xs font-medium text-neutral-700 mb-1">Contract Value ($)</label>
            <input type="number" value={contractValue} onChange={e => setContractValue(e.target.value)}
              className="w-64 px-3 py-2 border border-neutral-200 rounded-lg text-sm" placeholder="Optional" />
          </div>
        </div>

        <div className="flex justify-between">
          <button onClick={() => { setSelectedTemplate(null); setCurrentStep(0); }} className="px-4 py-2 text-sm text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50">Back</button>
          <button onClick={() => setCurrentStep(2)} disabled={!canProceedStep1()}
            className={`px-6 py-2 text-sm rounded-lg ${canProceedStep1() ? 'bg-violet-600 text-white hover:bg-violet-700' : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'}`}>
            Next: Signing Options
          </button>
        </div>
      </div>
    );
  };

  /* ─── Step 2: Signing Options ─── */
  const Step2 = () => {
    if (!selectedTemplate) return null;
    const chosen = signatories.find(s => s.id === signatoryId);
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Sender Signing Authority</h3>
          <div className="space-y-3">
            {eligibleSignatories.map(s => (
              <label key={s.id}
                className={`flex items-center gap-4 p-4 rounded-lg border cursor-pointer ${signatoryId === s.id ? 'border-violet-400 bg-violet-50' : 'border-neutral-200 hover:border-neutral-300'}`}>
                <input type="radio" name="signatory" checked={signatoryId === s.id} onChange={() => setSignatoryId(s.id)} className="accent-violet-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-neutral-900">{s.name}</p>
                  <p className="text-xs text-neutral-500">{s.designation}</p>
                </div>
                <div className="text-right text-xs text-neutral-500">
                  <p>{s.can_sign_types ? s.can_sign_types.join(', ').toUpperCase() : 'All Types'}</p>
                  <p>{s.max_contract_value ? `Max $${s.max_contract_value.toLocaleString()}` : 'Unlimited'}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Signing Preferences</h3>
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" checked={autoSign} onChange={e => setAutoSign(e.target.checked)} className="accent-violet-600 w-4 h-4" />
              <div>
                <p className="text-sm text-neutral-900">Auto-sign as sender when sending</p>
                <p className="text-xs text-neutral-500">Your signature will be applied automatically using the selected signatory authority</p>
              </div>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" checked={sendImmediately} onChange={e => setSendImmediately(e.target.checked)} className="accent-violet-600 w-4 h-4" />
              <div>
                <p className="text-sm text-neutral-900">Send immediately after creation</p>
                <p className="text-xs text-neutral-500">Skip the draft stage and send directly for recipient signature</p>
              </div>
            </label>
          </div>
        </div>

        {chosen && autoSign && (
          <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-4">
            <p className="text-xs text-emerald-800">
              <span className="font-semibold">{chosen.name}</span> ({chosen.designation}) will auto-sign this agreement on behalf of HotGigs MSP.
            </p>
          </div>
        )}

        <div className="flex justify-between">
          <button onClick={() => setCurrentStep(1)} className="px-4 py-2 text-sm text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50">Back</button>
          <button onClick={() => setCurrentStep(3)} className="px-6 py-2 text-sm bg-violet-600 text-white rounded-lg hover:bg-violet-700">Next: Review</button>
        </div>
      </div>
    );
  };

  /* ─── Step 3: Review & Send ─── */
  const Step3 = () => {
    if (!selectedTemplate) return null;
    const chosen = signatories.find(s => s.id === signatoryId);

    if (sent) {
      return (
        <div className="bg-white rounded-xl border border-neutral-200 p-12 text-center">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
          </div>
          <h3 className="text-xl font-bold text-neutral-900">Agreement {sendImmediately ? 'Sent' : 'Created'}!</h3>
          <p className="text-sm text-neutral-500 mt-2">
            {sendImmediately
              ? `The agreement has been sent to the recipient for signature. ${autoSign ? 'Your signature was auto-applied.' : ''}`
              : 'The agreement has been saved as a draft. You can send it from the Agreement Center.'}
          </p>
          <p className="text-xs text-neutral-400 mt-4">Agreement Number: AGR-2026-0025</p>
          <div className="flex justify-center gap-3 mt-6">
            <button onClick={() => { setSent(false); setCurrentStep(0); setSelectedTemplate(null); setFormValues({}); }}
              className="px-4 py-2 text-sm bg-violet-600 text-white rounded-lg hover:bg-violet-700">Create Another</button>
            <button className="px-4 py-2 text-sm border border-neutral-200 rounded-lg hover:bg-neutral-50">View Agreement</button>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Review Agreement</h3>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs text-neutral-500 mb-1">Template</p>
              <p className="text-sm font-medium text-neutral-900">{selectedTemplate.name}</p>
              <span className={`text-[10px] px-2 py-0.5 rounded-full mt-1 inline-block ${typeColors[selectedTemplate.agreement_type]}`}>{selectedTemplate.agreement_type.toUpperCase()}</span>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Title</p>
              <p className="text-sm font-medium text-neutral-900">{agreementTitle || '(Untitled)'}</p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-neutral-100">
            <p className="text-xs text-neutral-500 mb-3">Filled Variables</p>
            <div className="grid grid-cols-2 gap-3">
              {selectedTemplate.variables.map(v => (
                <div key={v.key} className={v.type === 'textarea' ? 'col-span-2' : ''}>
                  <p className="text-[10px] text-neutral-400">{v.label}</p>
                  <p className="text-sm text-neutral-900">{formValues[v.key] || <span className="text-neutral-300 italic">Not provided</span>}</p>
                </div>
              ))}
            </div>
          </div>

          {contractValue && (
            <div className="mt-4 pt-4 border-t border-neutral-100">
              <p className="text-xs text-neutral-500">Contract Value</p>
              <p className="text-lg font-bold text-violet-700">${Number(contractValue).toLocaleString()}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Signing Summary</h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs text-neutral-500 mb-1">Sender Signatory</p>
              <p className="text-sm font-medium text-neutral-900">{chosen?.name}</p>
              <p className="text-xs text-neutral-500">{chosen?.designation}</p>
              {autoSign && <p className="text-xs text-emerald-600 mt-1">Will auto-sign on send</p>}
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Delivery</p>
              <p className="text-sm text-neutral-900">{sendImmediately ? 'Send immediately' : 'Save as draft'}</p>
            </div>
          </div>
        </div>

        <div className="flex justify-between">
          <button onClick={() => setCurrentStep(2)} className="px-4 py-2 text-sm text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50">Back</button>
          <div className="flex gap-3">
            <button onClick={() => { setSendImmediately(false); handleSend(); }}
              className="px-6 py-2 text-sm border border-neutral-200 rounded-lg hover:bg-neutral-50">Save as Draft</button>
            <button onClick={() => { setSendImmediately(true); handleSend(); }}
              className="px-6 py-2 text-sm bg-violet-600 text-white rounded-lg hover:bg-violet-700">Sign & Send</button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Agreement Builder</h1>
        <p className="text-neutral-500 mt-1">Create and send agreements from templates with dynamic field filling and e-signature</p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <React.Fragment key={s}>
            <button onClick={() => { if (i <= currentStep) setCurrentStep(i); }}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all ${
                i === currentStep ? 'bg-violet-600 text-white' : i < currentStep ? 'bg-violet-100 text-violet-700 cursor-pointer' : 'bg-neutral-100 text-neutral-400'
              }`}>
              <span className="w-5 h-5 rounded-full border flex items-center justify-center text-[10px] font-bold">{i + 1}</span>
              {s}
            </button>
            {i < steps.length - 1 && <div className={`flex-1 h-0.5 ${i < currentStep ? 'bg-violet-400' : 'bg-neutral-200'}`} />}
          </React.Fragment>
        ))}
      </div>

      {currentStep === 0 && <Step0 />}
      {currentStep === 1 && <Step1 />}
      {currentStep === 2 && <Step2 />}
      {currentStep === 3 && <Step3 />}
    </div>
  );
};

export default AgreementBuilder;
