import React, { useState } from 'react';

const fmt = (n: number) => '$' + n.toLocaleString();

// ─── Aging Buckets ───────────────────────────────────────────
const bucketLabels: Record<string, string> = {
  current: 'Current (0-30)',
  '31_45': '31-45 Days',
  '46_60': '46-60 Days',
  '61_90': '61-90 Days',
  over_90: '90+ Days',
};

const bucketColors: Record<string, string> = {
  current: 'bg-emerald-500',
  '31_45': 'bg-amber-500',
  '46_60': 'bg-orange-500',
  '61_90': 'bg-red-400',
  over_90: 'bg-red-600',
};

const bucketBadgeColors: Record<string, string> = {
  current: 'bg-emerald-100 text-emerald-700',
  '31_45': 'bg-amber-100 text-amber-700',
  '46_60': 'bg-orange-100 text-orange-700',
  '61_90': 'bg-red-100 text-red-700',
  over_90: 'bg-red-100 text-red-800',
};

// ─── AR Mock Data ────────────────────────────────────────────
const receivables = [
  { id: 'INV-2026-0042', client: 'TechCorp Inc', issue: '2026-03-01', due: '2026-03-31', amount: 68000, paid: 0, balance: 68000, status: 'sent', bucket: 'current', days: 12 },
  { id: 'INV-2026-0041', client: 'TechCorp Inc', issue: '2026-02-15', due: '2026-03-17', amount: 72000, paid: 0, balance: 72000, status: 'sent', bucket: 'current', days: 26 },
  { id: 'INV-2026-0039', client: 'MedFirst Health', issue: '2026-02-01', due: '2026-03-17', amount: 54000, paid: 0, balance: 54000, status: 'sent', bucket: 'current', days: 40 },
  { id: 'INV-2026-0038', client: 'FinanceGroup LLC', issue: '2026-01-25', due: '2026-02-24', amount: 48000, paid: 0, balance: 48000, status: 'overdue', bucket: '31_45', days: 47 },
  { id: 'INV-2026-0035', client: 'MedFirst Health', issue: '2026-01-15', due: '2026-03-01', amount: 41000, paid: 0, balance: 41000, status: 'overdue', bucket: '31_45', days: 57 },
  { id: 'INV-2026-0032', client: 'BuildRight Construction', issue: '2026-01-05', due: '2026-03-06', amount: 72000, paid: 0, balance: 72000, status: 'sent', bucket: 'current', days: 67 },
  { id: 'INV-2025-0128', client: 'FinanceGroup LLC', issue: '2025-12-20', due: '2026-01-19', amount: 52000, paid: 0, balance: 52000, status: 'overdue', bucket: '46_60', days: 83 },
  { id: 'INV-2025-0122', client: 'RetailMax Corp', issue: '2025-12-10', due: '2026-01-09', amount: 38000, paid: 0, balance: 38000, status: 'overdue', bucket: '61_90', days: 93 },
  { id: 'INV-2025-0115', client: 'AutoDrive Systems', issue: '2025-11-15', due: '2025-12-30', amount: 42000, paid: 0, balance: 42000, status: 'overdue', bucket: 'over_90', days: 118 },
  { id: 'INV-2025-0108', client: 'BuildRight Construction', issue: '2025-11-01', due: '2025-12-31', amount: 35000, paid: 12000, balance: 23000, status: 'partial', bucket: 'over_90', days: 132 },
];

const arSummary = {
  current: { count: 4, total: 266000, percent: 47.2 },
  '31_45': { count: 2, total: 89000, percent: 15.8 },
  '46_60': { count: 1, total: 52000, percent: 9.2 },
  '61_90': { count: 1, total: 38000, percent: 6.7 },
  over_90: { count: 2, total: 65000, percent: 11.5 },
  total_outstanding: 628000, total_overdue: 244000, dso: 42,
};

// ─── AP Mock Data ────────────────────────────────────────────
const payables = [
  { id: 'BILL-2026-0089', supplier: 'StaffPro Solutions', issue: '2026-03-01', due: '2026-03-31', amount: 72000, paid: 0, balance: 72000, status: 'sent', bucket: 'current', days: 12, category: 'Staffing' },
  { id: 'BILL-2026-0088', supplier: 'TalentBridge Agency', issue: '2026-03-01', due: '2026-03-31', amount: 44000, paid: 0, balance: 44000, status: 'sent', bucket: 'current', days: 12, category: 'Staffing' },
  { id: 'BILL-2026-0085', supplier: 'StaffPro Solutions', issue: '2026-02-15', due: '2026-03-17', amount: 66000, paid: 0, balance: 66000, status: 'sent', bucket: 'current', days: 26, category: 'Staffing' },
  { id: 'BILL-2026-0082', supplier: 'CodeForce Inc', issue: '2026-02-01', due: '2026-03-17', amount: 34000, paid: 0, balance: 34000, status: 'sent', bucket: 'current', days: 40, category: 'IT Staffing' },
  { id: 'BILL-2026-0078', supplier: 'StaffPro Solutions', issue: '2026-01-15', due: '2026-02-14', amount: 68000, paid: 0, balance: 68000, status: 'overdue', bucket: '31_45', days: 57, category: 'Staffing' },
  { id: 'BILL-2026-0075', supplier: 'CodeForce Inc', issue: '2026-01-01', due: '2026-02-15', amount: 34000, paid: 0, balance: 34000, status: 'overdue', bucket: '31_45', days: 71, category: 'IT Staffing' },
  { id: 'BILL-2025-0215', supplier: 'HireRight Inc', issue: '2025-12-15', due: '2026-01-14', amount: 8000, paid: 0, balance: 8000, status: 'overdue', bucket: '46_60', days: 88, category: 'BGC' },
  { id: 'BILL-2025-0210', supplier: 'SecureInsure Corp', issue: '2025-12-01', due: '2026-01-30', amount: 12000, paid: 0, balance: 12000, status: 'overdue', bucket: '46_60', days: 102, category: 'Insurance' },
];

const apSummary = {
  current: { count: 4, total: 216000, percent: 52.4 },
  '31_45': { count: 2, total: 102000, percent: 24.8 },
  '46_60': { count: 2, total: 20000, percent: 4.9 },
  '61_90': { count: 0, total: 0, percent: 0 },
  over_90: { count: 0, total: 0, percent: 0 },
  total_outstanding: 412000, total_overdue: 122000, dpo: 38,
};

type Tab = 'receivables' | 'payables';

export const ReceivablesPayables: React.FC = () => {
  const [tab, setTab] = useState<Tab>('receivables');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Receivables & Payables</h1>
          <p className="text-neutral-500 mt-1">AR/AP aging reports with Net 30/45/60/90+ timeline breakdowns</p>
        </div>
        <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">Export Aging Report</button>
      </div>

      <div className="border-b border-neutral-200">
        <nav className="flex gap-6">
          {[{ key: 'receivables' as Tab, label: 'Accounts Receivable (AR)' }, { key: 'payables' as Tab, label: 'Accounts Payable (AP)' }].map(t => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`pb-3 text-sm font-medium border-b-2 transition-colors ${tab === t.key ? 'border-violet-600 text-violet-700' : 'border-transparent text-neutral-500 hover:text-neutral-700'}`}>
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {tab === 'receivables' ? <ARTab /> : <APTab />}
    </div>
  );
};

const AgingSummaryBar = ({ summary, label }: { summary: Record<string, any>; label: string }) => {
  const total = summary.total_outstanding || 1;
  const buckets = ['current', '31_45', '46_60', '61_90', 'over_90'];

  return (
    <div className="bg-white rounded-xl border border-neutral-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-neutral-900">{label} Aging Summary</h3>
        <div className="flex items-center gap-4 text-xs">
          <span className="text-neutral-500">DSO/DPO: <span className="font-bold text-neutral-900">{summary.dso || summary.dpo} days</span></span>
          <span className="text-neutral-500">Total: <span className="font-bold text-neutral-900">{fmt(summary.total_outstanding)}</span></span>
          <span className="text-red-600">Overdue: <span className="font-bold">{fmt(summary.total_overdue)}</span></span>
        </div>
      </div>

      {/* Stacked Bar */}
      <div className="flex rounded-full h-8 overflow-hidden mb-4">
        {buckets.map(b => {
          const pct = ((summary[b]?.total || 0) / total) * 100;
          if (pct === 0) return null;
          return <div key={b} className={`${bucketColors[b]} transition-all flex items-center justify-center text-white text-[10px] font-medium`} style={{ width: `${pct}%` }}>{pct > 8 ? `${pct.toFixed(0)}%` : ''}</div>;
        })}
      </div>

      {/* Bucket Cards */}
      <div className="grid grid-cols-5 gap-3">
        {buckets.map(b => (
          <div key={b} className={`p-3 rounded-lg border ${summary[b]?.total > 0 ? 'border-neutral-200' : 'border-neutral-100 opacity-50'}`}>
            <div className="flex items-center gap-1.5 mb-1">
              <span className={`w-2.5 h-2.5 rounded-full ${bucketColors[b]}`} />
              <span className="text-[10px] font-medium text-neutral-600">{bucketLabels[b]}</span>
            </div>
            <p className="text-lg font-bold text-neutral-900">{fmt(summary[b]?.total || 0)}</p>
            <p className="text-[10px] text-neutral-500">{summary[b]?.count || 0} invoices</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const ARTab: React.FC = () => {
  const [bucketFilter, setBucketFilter] = useState<string>('all');
  const filtered = bucketFilter === 'all' ? receivables : receivables.filter(r => r.bucket === bucketFilter);

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Outstanding', value: fmt(arSummary.total_outstanding), color: 'text-blue-700' },
          { label: 'Overdue Amount', value: fmt(arSummary.total_overdue), color: 'text-red-700' },
          { label: 'Days Sales Outstanding', value: `${arSummary.dso} days`, color: 'text-violet-700' },
          { label: 'Open Invoices', value: receivables.length.toString(), color: 'text-neutral-900' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      <AgingSummaryBar summary={arSummary} label="AR" />

      {/* Filters */}
      <div className="flex items-center gap-2">
        {['all', 'current', '31_45', '46_60', '61_90', 'over_90'].map(b => (
          <button key={b} onClick={() => setBucketFilter(b)} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${bucketFilter === b ? 'bg-violet-600 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'}`}>
            {b === 'all' ? 'All' : bucketLabels[b]}
          </button>
        ))}
      </div>

      {/* Invoice Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Invoice #</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Customer</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Issue Date</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Due Date</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Amount</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Balance</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Status</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Aging</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Days</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {filtered.map(inv => (
              <tr key={inv.id} className="hover:bg-neutral-50">
                <td className="px-5 py-3 font-mono text-xs font-medium text-violet-700">{inv.id}</td>
                <td className="px-3 py-3 font-medium text-neutral-900">{inv.client}</td>
                <td className="px-3 py-3 text-neutral-600">{inv.issue}</td>
                <td className="px-3 py-3 text-neutral-600">{inv.due}</td>
                <td className="px-3 py-3 text-right text-neutral-700">{fmt(inv.amount)}</td>
                <td className="px-3 py-3 text-right font-semibold text-neutral-900">{fmt(inv.balance)}</td>
                <td className="px-3 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                    inv.status === 'overdue' ? 'bg-red-100 text-red-700' : inv.status === 'partial' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'
                  }`}>{inv.status}</span>
                </td>
                <td className="px-3 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${bucketBadgeColors[inv.bucket]}`}>{bucketLabels[inv.bucket]}</span>
                </td>
                <td className="px-3 py-3 text-right font-medium text-neutral-700">{inv.days}d</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const APTab: React.FC = () => {
  const [bucketFilter, setBucketFilter] = useState<string>('all');
  const filtered = bucketFilter === 'all' ? payables : payables.filter(r => r.bucket === bucketFilter);

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Outstanding', value: fmt(apSummary.total_outstanding), color: 'text-red-700' },
          { label: 'Overdue Amount', value: fmt(apSummary.total_overdue), color: 'text-red-600' },
          { label: 'Days Payable Outstanding', value: `${apSummary.dpo} days`, color: 'text-violet-700' },
          { label: 'Open Bills', value: payables.length.toString(), color: 'text-neutral-900' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      <AgingSummaryBar summary={apSummary} label="AP" />

      {/* Filters */}
      <div className="flex items-center gap-2">
        {['all', 'current', '31_45', '46_60', '61_90', 'over_90'].map(b => (
          <button key={b} onClick={() => setBucketFilter(b)} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${bucketFilter === b ? 'bg-violet-600 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'}`}>
            {b === 'all' ? 'All' : bucketLabels[b]}
          </button>
        ))}
      </div>

      {/* Bills Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Bill #</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Supplier</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Category</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Due Date</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Amount</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Balance</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Status</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Aging</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Days</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {filtered.map(bill => (
              <tr key={bill.id} className="hover:bg-neutral-50">
                <td className="px-5 py-3 font-mono text-xs font-medium text-violet-700">{bill.id}</td>
                <td className="px-3 py-3 font-medium text-neutral-900">{bill.supplier}</td>
                <td className="px-3 py-3 text-neutral-600">{bill.category}</td>
                <td className="px-3 py-3 text-neutral-600">{bill.due}</td>
                <td className="px-3 py-3 text-right text-neutral-700">{fmt(bill.amount)}</td>
                <td className="px-3 py-3 text-right font-semibold text-neutral-900">{fmt(bill.balance)}</td>
                <td className="px-3 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                    bill.status === 'overdue' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                  }`}>{bill.status}</span>
                </td>
                <td className="px-3 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${bucketBadgeColors[bill.bucket]}`}>{bucketLabels[bill.bucket]}</span>
                </td>
                <td className="px-3 py-3 text-right font-medium text-neutral-700">{bill.days}d</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReceivablesPayables;
