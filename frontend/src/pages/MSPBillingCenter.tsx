import React, { useState, useEffect } from 'react';

interface FeeTier {
  id: number; tier_name: string; revenue_min: number; revenue_max: number | null;
  fee_percentage: number; status: string; fee_type: string;
}
interface SupplierRevenue {
  supplier_org_id: number; supplier_name: string; current_revenue: number;
  current_tier: string; fee_percentage: number; ytd_msp_fees: number;
  active_placements: number; next_tier_at: number | null; savings_at_next_tier: number | null;
}
interface CascadeChain {
  timesheet_id: number; candidate_name: string; period: string; total_hours: number;
  bill_rate: number; pay_rate: number; msp_fee_pct: number;
  cascade_status: string; client_invoice_status: string; supplier_invoice_status: string;
}
interface CascadeInvoice {
  id: number; invoice_number: string; invoice_type: string; from_org_name: string;
  to_org_name: string; total_amount: number; msp_fee_amount: number;
  status: string; auto_approved: boolean; total_hours: number | null;
}

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
const fmtK = (n: number) => n >= 1000000 ? `$${(n/1000000).toFixed(1)}M` : n >= 1000 ? `$${(n/1000).toFixed(0)}K` : fmt(n);

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700', archived: 'bg-gray-100 text-gray-600',
  paid: 'bg-green-100 text-green-700', approved: 'bg-blue-100 text-blue-700',
  pending: 'bg-yellow-100 text-yellow-700', generated: 'bg-purple-100 text-purple-700',
  sent: 'bg-indigo-100 text-indigo-700', auto_approved: 'bg-teal-100 text-teal-700',
  fully_cascaded: 'bg-green-100 text-green-700', partially_cascaded: 'bg-yellow-100 text-yellow-700',
};

export function MSPBillingCenter() {
  const [tab, setTab] = useState<'tiers' | 'suppliers' | 'cascading' | 'invoices'>('tiers');
  const [feeTiers, setFeeTiers] = useState<FeeTier[]>([]);
  const [suppliers, setSuppliers] = useState<SupplierRevenue[]>([]);
  const [chains, setChains] = useState<CascadeChain[]>([]);
  const [invoices, setInvoices] = useState<CascadeInvoice[]>([]);
  const [kpis, setKpis] = useState({ total_billed: 0, total_paid: 0, total_msp_fees: 0, cascade_completion_rate: 0, total_outstanding: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = '/api/v1/msp-billing';
    Promise.all([
      fetch(`${base}/fee-tiers`).then(r => r.json()),
      fetch(`${base}/supplier-revenue`).then(r => r.json()),
      fetch(`${base}/cascade-chains`).then(r => r.json()),
      fetch(`${base}/cascade-invoices?limit=30`).then(r => r.json()),
      fetch(`${base}/dashboard`).then(r => r.json()),
    ]).then(([t, s, c, inv, d]) => {
      setFeeTiers(t.fee_tiers || []);
      setSuppliers(s.suppliers || []);
      setChains(c.chains || []);
      setInvoices(inv.invoices || []);
      setKpis(d);
    }).catch(() => {
      // Mock data fallback
      setFeeTiers([
        { id: 1, tier_name: 'Starter (0-1M)', revenue_min: 0, revenue_max: 1000000, fee_percentage: 5.0, status: 'active', fee_type: 'percentage_of_bill' },
        { id: 2, tier_name: 'Growth (1M-5M)', revenue_min: 1000000, revenue_max: 5000000, fee_percentage: 4.0, status: 'active', fee_type: 'percentage_of_bill' },
        { id: 3, tier_name: 'Enterprise (5M-10M)', revenue_min: 5000000, revenue_max: 10000000, fee_percentage: 3.5, status: 'active', fee_type: 'percentage_of_bill' },
        { id: 4, tier_name: 'Strategic (10M+)', revenue_min: 10000000, revenue_max: null, fee_percentage: 3.0, status: 'active', fee_type: 'percentage_of_bill' },
      ]);
      setSuppliers([
        { supplier_org_id: 100, supplier_name: 'TechStaff Pro', current_revenue: 750000, current_tier: 'Starter (0-1M)', fee_percentage: 5.0, ytd_msp_fees: 37500, active_placements: 12, next_tier_at: 1000000, savings_at_next_tier: 7500 },
        { supplier_org_id: 101, supplier_name: 'GlobalForce HR', current_revenue: 2800000, current_tier: 'Growth (1M-5M)', fee_percentage: 4.0, ytd_msp_fees: 112000, active_placements: 28, next_tier_at: 5000000, savings_at_next_tier: 14000 },
        { supplier_org_id: 102, supplier_name: 'PrimeRecruit Inc', current_revenue: 6200000, current_tier: 'Enterprise (5M-10M)', fee_percentage: 3.5, ytd_msp_fees: 217000, active_placements: 35, next_tier_at: 10000000, savings_at_next_tier: 31000 },
        { supplier_org_id: 103, supplier_name: 'NexGen Staffing', current_revenue: 12500000, current_tier: 'Strategic (10M+)', fee_percentage: 3.0, ytd_msp_fees: 375000, active_placements: 40, next_tier_at: null, savings_at_next_tier: null },
        { supplier_org_id: 104, supplier_name: 'ApexTalent', current_revenue: 450000, current_tier: 'Starter (0-1M)', fee_percentage: 5.0, ytd_msp_fees: 22500, active_placements: 8, next_tier_at: 1000000, savings_at_next_tier: 4500 },
      ]);
      setChains([
        { timesheet_id: 5000, candidate_name: 'Alice J.', period: 'Feb 3-9', total_hours: 40, bill_rate: 95, pay_rate: 65, msp_fee_pct: 4.0, cascade_status: 'fully_cascaded', client_invoice_status: 'paid', supplier_invoice_status: 'paid' },
        { timesheet_id: 5001, candidate_name: 'Bob M.', period: 'Feb 3-9', total_hours: 38, bill_rate: 110, pay_rate: 75, msp_fee_pct: 3.5, cascade_status: 'fully_cascaded', client_invoice_status: 'approved', supplier_invoice_status: 'auto_approved' },
        { timesheet_id: 5002, candidate_name: 'Carol C.', period: 'Feb 10-16', total_hours: 42, bill_rate: 85, pay_rate: 58, msp_fee_pct: 5.0, cascade_status: 'partially_cascaded', client_invoice_status: 'approved', supplier_invoice_status: 'pending' },
        { timesheet_id: 5003, candidate_name: 'David P.', period: 'Feb 10-16', total_hours: 40, bill_rate: 130, pay_rate: 88, msp_fee_pct: 3.0, cascade_status: 'pending', client_invoice_status: 'pending', supplier_invoice_status: 'pending' },
      ]);
      setInvoices([
        { id: 1, invoice_number: 'INV-C-20260001', invoice_type: 'client_to_msp', from_org_name: 'Client Corp 1', to_org_name: 'HotGigs MSP', total_amount: 3800, msp_fee_amount: 152, status: 'paid', auto_approved: false, total_hours: 40 },
        { id: 2, invoice_number: 'INV-S-20260001', invoice_type: 'msp_to_supplier', from_org_name: 'HotGigs MSP', to_org_name: 'TechStaff Pro', total_amount: 2600, msp_fee_amount: 0, status: 'paid', auto_approved: true, total_hours: 40 },
        { id: 3, invoice_number: 'INV-C-20260002', invoice_type: 'client_to_msp', from_org_name: 'Client Corp 2', to_org_name: 'HotGigs MSP', total_amount: 4180, msp_fee_amount: 146.3, status: 'approved', auto_approved: false, total_hours: 38 },
        { id: 4, invoice_number: 'INV-S-20260002', invoice_type: 'msp_to_supplier', from_org_name: 'HotGigs MSP', to_org_name: 'GlobalForce HR', total_amount: 2850, msp_fee_amount: 0, status: 'auto_approved', auto_approved: true, total_hours: 38 },
      ]);
      setKpis({ total_billed: 245600, total_paid: 178400, total_msp_fees: 9820, cascade_completion_rate: 87.5, total_outstanding: 67200 });
    }).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { key: 'tiers' as const, label: 'Fee Tiers', count: feeTiers.length },
    { key: 'suppliers' as const, label: 'Supplier Revenue', count: suppliers.length },
    { key: 'cascading' as const, label: 'Cascade Chains', count: chains.length },
    { key: 'invoices' as const, label: 'All Invoices', count: invoices.length },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">MSP Billing & Cascading Invoices</h1>
        <p className="text-gray-500 mt-1">Tiered fee management, supplier revenue tracking, and automatic cascading invoicing</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Billed', value: fmtK(kpis.total_billed), color: 'blue' },
          { label: 'Total Paid', value: fmtK(kpis.total_paid), color: 'green' },
          { label: 'Outstanding', value: fmtK(kpis.total_outstanding), color: 'yellow' },
          { label: 'MSP Fees YTD', value: fmtK(kpis.total_msp_fees), color: 'purple' },
          { label: 'Cascade Rate', value: `${kpis.cascade_completion_rate}%`, color: 'teal' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-lg border p-4 shadow-sm">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 text-${k.color}-600`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${tab === t.key ? 'bg-white shadow text-blue-700' : 'text-gray-600 hover:text-gray-900'}`}>
            {t.label} <span className="ml-1 text-xs text-gray-400">({t.count})</span>
          </button>
        ))}
      </div>

      {loading ? <div className="text-center py-12 text-gray-400">Loading...</div> : (
        <>
          {/* Fee Tiers Tab */}
          {tab === 'tiers' && (
            <div className="bg-white rounded-lg border shadow-sm">
              <div className="p-4 border-b flex justify-between items-center">
                <h2 className="font-semibold text-lg">MSP Fee Tier Brackets</h2>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Tier</button>
              </div>
              <div className="divide-y">
                {feeTiers.map(tier => (
                  <div key={tier.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-gray-900">{tier.tier_name}</span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[tier.status] || 'bg-gray-100'}`}>{tier.status}</span>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        Revenue: {fmtK(tier.revenue_min)} — {tier.revenue_max ? fmtK(tier.revenue_max) : 'Unlimited'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-600">{tier.fee_percentage}%</p>
                      <p className="text-xs text-gray-400">{tier.fee_type.replace(/_/g, ' ')}</p>
                    </div>
                  </div>
                ))}
              </div>
              {/* Visual tier bar */}
              <div className="p-4 bg-gray-50 rounded-b-lg">
                <p className="text-xs text-gray-500 mb-2 uppercase tracking-wide">Revenue Tier Visualization</p>
                <div className="flex h-8 rounded-lg overflow-hidden">
                  {feeTiers.map((tier, i) => {
                    const colors = ['bg-red-400', 'bg-yellow-400', 'bg-blue-400', 'bg-green-400'];
                    const widths = [20, 30, 25, 25];
                    return (
                      <div key={tier.id} className={`${colors[i]} flex items-center justify-center text-white text-xs font-bold`} style={{ width: `${widths[i]}%` }}>
                        {tier.fee_percentage}%
                      </div>
                    );
                  })}
                </div>
                <div className="flex text-xs text-gray-400 mt-1">
                  <span style={{ width: '20%' }}>$0</span>
                  <span style={{ width: '30%' }}>$1M</span>
                  <span style={{ width: '25%' }}>$5M</span>
                  <span style={{ width: '25%' }}>$10M+</span>
                </div>
              </div>
            </div>
          )}

          {/* Supplier Revenue Tab */}
          {tab === 'suppliers' && (
            <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
              <div className="p-4 border-b flex justify-between items-center">
                <h2 className="font-semibold text-lg">Supplier Revenue & Applied Tiers</h2>
                <button className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">Recalculate All</button>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left p-3 font-medium text-gray-600">Supplier</th>
                    <th className="text-right p-3 font-medium text-gray-600">YTD Revenue</th>
                    <th className="text-center p-3 font-medium text-gray-600">Current Tier</th>
                    <th className="text-center p-3 font-medium text-gray-600">Fee %</th>
                    <th className="text-right p-3 font-medium text-gray-600">MSP Fees YTD</th>
                    <th className="text-center p-3 font-medium text-gray-600">Placements</th>
                    <th className="text-right p-3 font-medium text-gray-600">Next Tier At</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {suppliers.map(s => (
                    <tr key={s.supplier_org_id} className="hover:bg-gray-50">
                      <td className="p-3 font-medium">{s.supplier_name}</td>
                      <td className="p-3 text-right font-mono">{fmtK(s.current_revenue)}</td>
                      <td className="p-3 text-center"><span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{s.current_tier}</span></td>
                      <td className="p-3 text-center font-bold text-blue-600">{s.fee_percentage}%</td>
                      <td className="p-3 text-right font-mono text-green-600">{fmtK(s.ytd_msp_fees)}</td>
                      <td className="p-3 text-center">{s.active_placements}</td>
                      <td className="p-3 text-right text-gray-500">{s.next_tier_at ? fmtK(s.next_tier_at) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Cascade Chains Tab */}
          {tab === 'cascading' && (
            <div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-blue-800">How Cascading Works</h3>
                <p className="text-sm text-blue-600 mt-1">When a client or MSP approves a timesheet, downstream invoices are <strong>automatically generated and approved</strong>. No separate downstream approvals needed — upstream approval cascades through the entire chain.</p>
                <div className="flex items-center gap-2 mt-2 text-sm text-blue-700">
                  <span className="bg-blue-200 px-2 py-1 rounded">Client Approves Time</span>
                  <span>→</span>
                  <span className="bg-blue-200 px-2 py-1 rounded">Client→MSP Invoice Generated</span>
                  <span>→</span>
                  <span className="bg-blue-200 px-2 py-1 rounded">MSP→Supplier Invoice Auto-Approved</span>
                  <span>→</span>
                  <span className="bg-green-200 px-2 py-1 rounded text-green-700">All Parties Settled</span>
                </div>
              </div>
              <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left p-3 font-medium text-gray-600">Contractor</th>
                      <th className="text-center p-3 font-medium text-gray-600">Period</th>
                      <th className="text-center p-3 font-medium text-gray-600">Hours</th>
                      <th className="text-right p-3 font-medium text-gray-600">Bill Rate</th>
                      <th className="text-right p-3 font-medium text-gray-600">Pay Rate</th>
                      <th className="text-center p-3 font-medium text-gray-600">MSP Fee</th>
                      <th className="text-center p-3 font-medium text-gray-600">Client Invoice</th>
                      <th className="text-center p-3 font-medium text-gray-600">Supplier Invoice</th>
                      <th className="text-center p-3 font-medium text-gray-600">Cascade</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {chains.map(c => (
                      <tr key={c.timesheet_id} className="hover:bg-gray-50">
                        <td className="p-3 font-medium">{c.candidate_name}</td>
                        <td className="p-3 text-center text-gray-600">{c.period}</td>
                        <td className="p-3 text-center">{c.total_hours}</td>
                        <td className="p-3 text-right font-mono">${c.bill_rate}</td>
                        <td className="p-3 text-right font-mono">${c.pay_rate}</td>
                        <td className="p-3 text-center font-bold text-purple-600">{c.msp_fee_pct}%</td>
                        <td className="p-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[c.client_invoice_status] || 'bg-gray-100'}`}>{c.client_invoice_status}</span></td>
                        <td className="p-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[c.supplier_invoice_status] || 'bg-gray-100'}`}>{c.supplier_invoice_status}</span></td>
                        <td className="p-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[c.cascade_status] || 'bg-gray-100'}`}>{c.cascade_status.replace(/_/g, ' ')}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* All Invoices Tab */}
          {tab === 'invoices' && (
            <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
              <div className="p-4 border-b"><h2 className="font-semibold text-lg">All Cascade Invoices</h2></div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left p-3 font-medium text-gray-600">Invoice #</th>
                    <th className="text-center p-3 font-medium text-gray-600">Type</th>
                    <th className="text-left p-3 font-medium text-gray-600">From</th>
                    <th className="text-left p-3 font-medium text-gray-600">To</th>
                    <th className="text-right p-3 font-medium text-gray-600">Amount</th>
                    <th className="text-right p-3 font-medium text-gray-600">MSP Fee</th>
                    <th className="text-center p-3 font-medium text-gray-600">Auto</th>
                    <th className="text-center p-3 font-medium text-gray-600">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {invoices.map(inv => (
                    <tr key={inv.id} className="hover:bg-gray-50">
                      <td className="p-3 font-mono text-xs">{inv.invoice_number}</td>
                      <td className="p-3 text-center"><span className={`text-xs px-2 py-0.5 rounded ${inv.invoice_type === 'client_to_msp' ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'}`}>{inv.invoice_type === 'client_to_msp' ? 'Client→MSP' : 'MSP→Supplier'}</span></td>
                      <td className="p-3 text-gray-700">{inv.from_org_name}</td>
                      <td className="p-3 text-gray-700">{inv.to_org_name}</td>
                      <td className="p-3 text-right font-mono">{fmt(inv.total_amount)}</td>
                      <td className="p-3 text-right font-mono text-purple-600">{inv.msp_fee_amount > 0 ? fmt(inv.msp_fee_amount) : '—'}</td>
                      <td className="p-3 text-center">{inv.auto_approved ? <span className="text-green-500">✓ Auto</span> : <span className="text-gray-400">Manual</span>}</td>
                      <td className="p-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[inv.status] || 'bg-gray-100'}`}>{inv.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
