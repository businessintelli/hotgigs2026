import React, { useState } from 'react';

const fmt = (n: number) => '$' + n.toLocaleString();

// ─── Mock Data ───────────────────────────────────────────────
const customers = [
  { id: 1, name: 'TechCorp Inc', industry: 'Technology', ytd: 425000, mtd: 148000, last: 142000, growth: 4.2, associates: 12, avg_rate: 125, hours: 3400, outstanding: 186000, terms: 'Net 30' },
  { id: 2, name: 'MedFirst Health', industry: 'Healthcare', ytd: 312000, mtd: 108000, last: 102000, growth: 5.9, associates: 8, avg_rate: 95, hours: 2560, outstanding: 95000, terms: 'Net 45' },
  { id: 3, name: 'FinanceGroup LLC', industry: 'Financial Services', ytd: 268000, mtd: 92000, last: 88000, growth: 4.5, associates: 6, avg_rate: 145, hours: 1920, outstanding: 132000, terms: 'Net 30' },
  { id: 4, name: 'BuildRight Construction', industry: 'Construction', ytd: 198000, mtd: 72000, last: 65000, growth: 10.8, associates: 9, avg_rate: 68, hours: 2880, outstanding: 72000, terms: 'Net 60' },
  { id: 5, name: 'RetailMax Corp', industry: 'Retail', ytd: 156000, mtd: 54000, last: 52000, growth: 3.8, associates: 5, avg_rate: 82, hours: 1600, outstanding: 54000, terms: 'Net 30' },
  { id: 6, name: 'AutoDrive Systems', industry: 'Automotive', ytd: 124000, mtd: 42000, last: 40000, growth: 5.0, associates: 3, avg_rate: 135, hours: 960, outstanding: 42000, terms: 'Net 45' },
  { id: 7, name: 'EduTech Academy', industry: 'Education', ytd: 62000, mtd: 32000, last: 23000, growth: 39.1, associates: 2, avg_rate: 78, hours: 640, outstanding: 32000, terms: 'Net 30' },
];

const suppliers = [
  { id: 1, name: 'StaffPro Solutions', category: 'Staffing', ytd: 385000, mtd: 138000, last: 132000, associates: 18, avg_rate: 72, outstanding: 142000, terms: 'Net 30', on_time: 96.5 },
  { id: 2, name: 'TalentBridge Agency', category: 'Staffing', ytd: 248000, mtd: 88000, last: 82000, associates: 10, avg_rate: 65, outstanding: 88000, terms: 'Net 30', on_time: 98.2 },
  { id: 3, name: 'CodeForce Inc', category: 'Staffing — IT', ytd: 192000, mtd: 68000, last: 64000, associates: 6, avg_rate: 95, outstanding: 68000, terms: 'Net 45', on_time: 94.8 },
  { id: 4, name: 'HireRight Inc', category: 'Background Checks', ytd: 24000, mtd: 8000, last: 7500, associates: 0, avg_rate: 0, outstanding: 8000, terms: 'Net 30', on_time: 100.0 },
  { id: 5, name: 'ADP Payroll Services', category: 'Payroll Processing', ytd: 18000, mtd: 6000, last: 6000, associates: 0, avg_rate: 0, outstanding: 6000, terms: 'Net 15', on_time: 100.0 },
  { id: 6, name: 'SecureInsure Corp', category: 'Insurance', ytd: 36000, mtd: 12000, last: 12000, associates: 0, avg_rate: 0, outstanding: 0, terms: 'Net 60', on_time: 100.0 },
];

type Tab = 'revenue' | 'expenses';

export const RevenueExpenseBreakdown: React.FC = () => {
  const [tab, setTab] = useState<Tab>('revenue');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Revenue & Expense Breakdown</h1>
          <p className="text-neutral-500 mt-1">Revenue by customer and expenses by supplier with detailed analytics</p>
        </div>
        <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">Export Report</button>
      </div>

      <div className="border-b border-neutral-200">
        <nav className="flex gap-6">
          {[{ key: 'revenue' as Tab, label: 'Revenue by Customer' }, { key: 'expenses' as Tab, label: 'Expenses by Supplier' }].map(t => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`pb-3 text-sm font-medium border-b-2 transition-colors ${tab === t.key ? 'border-violet-600 text-violet-700' : 'border-transparent text-neutral-500 hover:text-neutral-700'}`}>
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {tab === 'revenue' ? <RevenueTab /> : <ExpensesTab />}
    </div>
  );
};

const RevenueTab: React.FC = () => {
  const totalYTD = customers.reduce((s, c) => s + c.ytd, 0);
  const totalMTD = customers.reduce((s, c) => s + c.mtd, 0);
  const totalOutstanding = customers.reduce((s, c) => s + c.outstanding, 0);

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'YTD Revenue', value: fmt(totalYTD), color: 'text-blue-700' },
          { label: 'MTD Revenue', value: fmt(totalMTD), color: 'text-emerald-700' },
          { label: 'Active Customers', value: customers.length.toString(), color: 'text-violet-700' },
          { label: 'Outstanding AR', value: fmt(totalOutstanding), color: 'text-amber-700' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Revenue Share Visualization */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5">
        <h3 className="text-sm font-semibold text-neutral-900 mb-3">Revenue Share by Customer (YTD)</h3>
        <div className="flex rounded-full h-6 overflow-hidden">
          {customers.map((c, i) => {
            const pct = (c.ytd / totalYTD) * 100;
            const colors = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500', 'bg-cyan-500', 'bg-orange-500'];
            return <div key={c.id} className={`${colors[i]} transition-all`} style={{ width: `${pct}%` }} title={`${c.name}: ${pct.toFixed(1)}%`} />;
          })}
        </div>
        <div className="flex flex-wrap gap-3 mt-3">
          {customers.map((c, i) => {
            const colors = ['bg-blue-500', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500', 'bg-cyan-500', 'bg-orange-500'];
            return (
              <div key={c.id} className="flex items-center gap-1.5 text-xs text-neutral-600">
                <span className={`w-2.5 h-2.5 rounded-full ${colors[i]}`} />
                {c.name} ({((c.ytd / totalYTD) * 100).toFixed(1)}%)
              </div>
            );
          })}
        </div>
      </div>

      {/* Customer Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Customer</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Industry</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">YTD Revenue</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">MTD</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Growth</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Associates</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Avg Rate</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Outstanding</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Terms</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {customers.map(c => (
              <tr key={c.id} className="hover:bg-neutral-50">
                <td className="px-5 py-3 font-medium text-neutral-900">{c.name}</td>
                <td className="px-3 py-3 text-neutral-600">{c.industry}</td>
                <td className="px-3 py-3 text-right font-semibold text-blue-700">{fmt(c.ytd)}</td>
                <td className="px-3 py-3 text-right text-neutral-700">{fmt(c.mtd)}</td>
                <td className="px-3 py-3 text-right">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${c.growth >= 10 ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-50 text-blue-700'}`}>
                    +{c.growth}%
                  </span>
                </td>
                <td className="px-3 py-3 text-center text-neutral-700">{c.associates}</td>
                <td className="px-3 py-3 text-right text-neutral-700">${c.avg_rate}/hr</td>
                <td className="px-3 py-3 text-right text-amber-700 font-medium">{fmt(c.outstanding)}</td>
                <td className="px-3 py-3 text-center"><span className="px-2 py-0.5 bg-neutral-100 text-neutral-600 rounded text-xs">{c.terms}</span></td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-neutral-50 border-t border-neutral-200">
            <tr>
              <td className="px-5 py-3 font-bold text-neutral-900">Total</td>
              <td className="px-3 py-3"></td>
              <td className="px-3 py-3 text-right font-bold text-blue-700">{fmt(totalYTD)}</td>
              <td className="px-3 py-3 text-right font-bold">{fmt(totalMTD)}</td>
              <td className="px-3 py-3"></td>
              <td className="px-3 py-3 text-center font-bold">{customers.reduce((s, c) => s + c.associates, 0)}</td>
              <td className="px-3 py-3"></td>
              <td className="px-3 py-3 text-right font-bold text-amber-700">{fmt(totalOutstanding)}</td>
              <td className="px-3 py-3"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

const ExpensesTab: React.FC = () => {
  const totalYTD = suppliers.reduce((s, c) => s + c.ytd, 0);
  const totalMTD = suppliers.reduce((s, c) => s + c.mtd, 0);
  const totalOutstanding = suppliers.reduce((s, c) => s + c.outstanding, 0);

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'YTD Expenses', value: fmt(totalYTD), color: 'text-red-700' },
          { label: 'MTD Expenses', value: fmt(totalMTD), color: 'text-red-600' },
          { label: 'Active Suppliers', value: suppliers.length.toString(), color: 'text-violet-700' },
          { label: 'Outstanding AP', value: fmt(totalOutstanding), color: 'text-amber-700' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Expense Share */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5">
        <h3 className="text-sm font-semibold text-neutral-900 mb-3">Expense Share by Supplier (YTD)</h3>
        <div className="flex rounded-full h-6 overflow-hidden">
          {suppliers.map((s, i) => {
            const pct = (s.ytd / totalYTD) * 100;
            const colors = ['bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-rose-500', 'bg-pink-500', 'bg-fuchsia-500'];
            return <div key={s.id} className={`${colors[i]} transition-all`} style={{ width: `${pct}%` }} title={`${s.name}: ${pct.toFixed(1)}%`} />;
          })}
        </div>
        <div className="flex flex-wrap gap-3 mt-3">
          {suppliers.map((s, i) => {
            const colors = ['bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-rose-500', 'bg-pink-500', 'bg-fuchsia-500'];
            return (
              <div key={s.id} className="flex items-center gap-1.5 text-xs text-neutral-600">
                <span className={`w-2.5 h-2.5 rounded-full ${colors[i]}`} />
                {s.name} ({((s.ytd / totalYTD) * 100).toFixed(1)}%)
              </div>
            );
          })}
        </div>
      </div>

      {/* Supplier Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Supplier</th>
              <th className="text-left px-3 py-3 text-xs font-medium text-neutral-500">Category</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">YTD Expenses</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">MTD</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Associates</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Avg Rate</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Outstanding</th>
              <th className="text-center px-3 py-3 text-xs font-medium text-neutral-500">Terms</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">On-Time %</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {suppliers.map(s => (
              <tr key={s.id} className="hover:bg-neutral-50">
                <td className="px-5 py-3 font-medium text-neutral-900">{s.name}</td>
                <td className="px-3 py-3 text-neutral-600">{s.category}</td>
                <td className="px-3 py-3 text-right font-semibold text-red-700">{fmt(s.ytd)}</td>
                <td className="px-3 py-3 text-right text-neutral-700">{fmt(s.mtd)}</td>
                <td className="px-3 py-3 text-center text-neutral-700">{s.associates || '—'}</td>
                <td className="px-3 py-3 text-right text-neutral-700">{s.avg_rate ? `$${s.avg_rate}/hr` : '—'}</td>
                <td className="px-3 py-3 text-right text-amber-700 font-medium">{fmt(s.outstanding)}</td>
                <td className="px-3 py-3 text-center"><span className="px-2 py-0.5 bg-neutral-100 text-neutral-600 rounded text-xs">{s.terms}</span></td>
                <td className="px-3 py-3 text-right">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${s.on_time >= 98 ? 'bg-emerald-100 text-emerald-700' : s.on_time >= 95 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                    {s.on_time}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-neutral-50 border-t border-neutral-200">
            <tr>
              <td className="px-5 py-3 font-bold text-neutral-900">Total</td>
              <td className="px-3 py-3"></td>
              <td className="px-3 py-3 text-right font-bold text-red-700">{fmt(totalYTD)}</td>
              <td className="px-3 py-3 text-right font-bold">{fmt(totalMTD)}</td>
              <td className="px-3 py-3 text-center font-bold">{suppliers.reduce((s, c) => s + c.associates, 0)}</td>
              <td className="px-3 py-3"></td>
              <td className="px-3 py-3 text-right font-bold text-amber-700">{fmt(totalOutstanding)}</td>
              <td className="px-3 py-3"></td>
              <td className="px-3 py-3"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default RevenueExpenseBreakdown;
