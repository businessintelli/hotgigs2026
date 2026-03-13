import React, { useState } from 'react';

// ─── Mock Data ───────────────────────────────────────────────
const plMonthly = [
  { period: '2026-01', revenue: 485000, cogs: 312000, gross_profit: 173000, gross_margin: 35.7, opex: 98000, operating_income: 75000, other_income: 3200, other_expenses: 1800, net_income: 76400, net_margin: 15.8 },
  { period: '2026-02', revenue: 512000, cogs: 325000, gross_profit: 187000, gross_margin: 36.5, opex: 102000, operating_income: 85000, other_income: 2800, other_expenses: 2100, net_income: 85700, net_margin: 16.7 },
  { period: '2026-03', revenue: 548000, cogs: 341000, gross_profit: 207000, gross_margin: 37.8, opex: 105000, operating_income: 102000, other_income: 3500, other_expenses: 1500, net_income: 104000, net_margin: 19.0 },
];

const ytdSummary = { revenue: 1545000, cogs: 978000, gross_profit: 567000, gross_margin: 36.7, opex: 305000, operating_income: 262000, net_income: 266100, net_margin: 17.2 };

const revenueLines = [
  { account: 'Staffing Revenue — IT', amount: 285000, percent: 52.0 },
  { account: 'Staffing Revenue — Engineering', amount: 142000, percent: 25.9 },
  { account: 'Staffing Revenue — Healthcare', amount: 78000, percent: 14.2 },
  { account: 'Staffing Revenue — Finance', amount: 33000, percent: 6.0 },
  { account: 'Placement Fees', amount: 10000, percent: 1.8 },
];

const cogsLines = [
  { account: 'Associate Payroll', amount: 268000, percent: 78.6 },
  { account: 'Payroll Taxes & Benefits', amount: 42000, percent: 12.3 },
  { account: 'Workers Compensation', amount: 18000, percent: 5.3 },
  { account: 'Background Checks', amount: 8000, percent: 2.3 },
  { account: 'Drug Testing', amount: 5000, percent: 1.5 },
];

const opexLines = [
  { account: 'Salaries — Internal Staff', amount: 52000, percent: 49.5 },
  { account: 'Office & Facilities', amount: 15000, percent: 14.3 },
  { account: 'Technology & Software', amount: 12000, percent: 11.4 },
  { account: 'Marketing & Sales', amount: 9000, percent: 8.6 },
  { account: 'Insurance — General', amount: 8000, percent: 7.6 },
  { account: 'Professional Services', amount: 5000, percent: 4.8 },
  { account: 'Travel & Entertainment', amount: 4000, percent: 3.8 },
];

const balanceSheet = {
  assets: {
    current: [
      { name: 'Cash & Equivalents', amount: 342000 },
      { name: 'Accounts Receivable', amount: 628000 },
      { name: 'Unbilled Revenue', amount: 85000 },
      { name: 'Prepaid Expenses', amount: 24000 },
    ],
    non_current: [
      { name: 'Property & Equipment', amount: 45000 },
      { name: 'Intangible Assets', amount: 12000 },
      { name: 'Deposits', amount: 8000 },
    ],
  },
  liabilities: {
    current: [
      { name: 'Accounts Payable', amount: 412000 },
      { name: 'Accrued Payroll', amount: 168000 },
      { name: 'Payroll Taxes Payable', amount: 32000 },
      { name: 'Accrued Expenses', amount: 18000 },
      { name: 'Current Portion Debt', amount: 25000 },
    ],
    non_current: [
      { name: 'Long-Term Debt', amount: 75000 },
      { name: 'Deferred Revenue', amount: 15000 },
    ],
  },
  equity: [
    { name: 'Common Stock', amount: 100000 },
    { name: 'Retained Earnings', amount: 299000 },
  ],
};

const fmt = (n: number) => '$' + n.toLocaleString();

type Tab = 'pl' | 'balance_sheet';

export const ProfitAndLoss: React.FC = () => {
  const [tab, setTab] = useState<Tab>('pl');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Financial Statements</h1>
          <p className="text-neutral-500 mt-1">P&L and Balance Sheet for the current fiscal year</p>
        </div>
        <div className="flex items-center gap-2">
          <select className="px-3 py-1.5 border border-neutral-200 rounded-lg text-sm bg-white">
            <option>FY 2026</option>
            <option>FY 2025</option>
          </select>
          <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">Export PDF</button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-neutral-200">
        <nav className="flex gap-6">
          {[{ key: 'pl' as Tab, label: 'Profit & Loss' }, { key: 'balance_sheet' as Tab, label: 'Balance Sheet' }].map(t => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`pb-3 text-sm font-medium border-b-2 transition-colors ${tab === t.key ? 'border-violet-600 text-violet-700' : 'border-transparent text-neutral-500 hover:text-neutral-700'}`}>
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {tab === 'pl' ? <PLTab /> : <BalanceSheetTab />}
    </div>
  );
};

const PLTab: React.FC = () => (
  <div className="space-y-6">
    {/* YTD KPIs */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[
        { label: 'YTD Revenue', value: fmt(ytdSummary.revenue), color: 'text-blue-700', sub: '' },
        { label: 'Gross Profit', value: fmt(ytdSummary.gross_profit), color: 'text-emerald-700', sub: `${ytdSummary.gross_margin}% margin` },
        { label: 'Operating Income', value: fmt(ytdSummary.operating_income), color: 'text-violet-700', sub: '' },
        { label: 'Net Income', value: fmt(ytdSummary.net_income), color: 'text-emerald-700', sub: `${ytdSummary.net_margin}% margin` },
      ].map(kpi => (
        <div key={kpi.label} className="bg-white rounded-xl border border-neutral-200 p-5">
          <p className="text-xs text-neutral-500 uppercase tracking-wide">{kpi.label}</p>
          <p className={`text-2xl font-bold mt-1 ${kpi.color}`}>{kpi.value}</p>
          {kpi.sub && <p className="text-xs text-neutral-500 mt-0.5">{kpi.sub}</p>}
        </div>
      ))}
    </div>

    {/* Monthly P&L Table */}
    <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
      <div className="px-5 py-3 bg-neutral-50 border-b border-neutral-200">
        <h3 className="text-sm font-semibold text-neutral-900">Monthly P&L Statement — 2026</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-neutral-100">
            <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Line Item</th>
            {plMonthly.map(m => <th key={m.period} className="text-right px-4 py-3 text-xs font-medium text-neutral-500">{m.period}</th>)}
            <th className="text-right px-5 py-3 text-xs font-medium text-violet-600">YTD</th>
          </tr>
        </thead>
        <tbody>
          {[
            { label: 'Revenue', key: 'revenue', bold: true, color: '' },
            { label: 'Cost of Goods Sold', key: 'cogs', bold: false, color: 'text-red-600' },
            { label: 'Gross Profit', key: 'gross_profit', bold: true, color: 'text-emerald-700' },
            { label: 'Gross Margin %', key: 'gross_margin', bold: false, color: 'text-neutral-500', isPercent: true },
            { label: 'Operating Expenses', key: 'opex', bold: false, color: 'text-red-600' },
            { label: 'Operating Income', key: 'operating_income', bold: true, color: 'text-violet-700' },
            { label: 'Other Income', key: 'other_income', bold: false, color: '' },
            { label: 'Other Expenses', key: 'other_expenses', bold: false, color: 'text-red-600' },
            { label: 'Net Income', key: 'net_income', bold: true, color: 'text-emerald-700' },
            { label: 'Net Margin %', key: 'net_margin', bold: false, color: 'text-neutral-500', isPercent: true },
          ].map((row: any) => {
            const ytdVal = row.isPercent
              ? (row.key === 'gross_margin' ? ytdSummary.gross_margin : ytdSummary.net_margin)
              : (ytdSummary as any)[row.key] || plMonthly.reduce((s, m) => s + ((m as any)[row.key] || 0), 0);
            return (
              <tr key={row.key} className={`border-b border-neutral-50 ${row.bold ? 'bg-neutral-50' : ''}`}>
                <td className={`px-5 py-2.5 ${row.bold ? 'font-semibold text-neutral-900' : 'text-neutral-700 pl-8'}`}>{row.label}</td>
                {plMonthly.map(m => (
                  <td key={m.period} className={`text-right px-4 py-2.5 ${row.color || ''} ${row.bold ? 'font-semibold' : ''}`}>
                    {row.isPercent ? `${(m as any)[row.key]}%` : fmt((m as any)[row.key])}
                  </td>
                ))}
                <td className={`text-right px-5 py-2.5 font-semibold ${row.color || 'text-violet-700'}`}>
                  {row.isPercent ? `${ytdVal}%` : fmt(ytdVal)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>

    {/* Breakdown Sections */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {[
        { title: 'Revenue Breakdown (Mar)', lines: revenueLines, color: 'bg-blue-50 text-blue-700' },
        { title: 'COGS Breakdown (Mar)', lines: cogsLines, color: 'bg-red-50 text-red-700' },
        { title: 'OpEx Breakdown (Mar)', lines: opexLines, color: 'bg-amber-50 text-amber-700' },
      ].map(section => (
        <div key={section.title} className="bg-white rounded-xl border border-neutral-200 p-5">
          <h4 className="text-xs font-semibold text-neutral-900 mb-3">{section.title}</h4>
          <div className="space-y-2">
            {section.lines.map(line => (
              <div key={line.account}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-neutral-700 truncate mr-2">{line.account}</span>
                  <span className="font-medium text-neutral-900 whitespace-nowrap">{fmt(line.amount)}</span>
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-1.5">
                  <div className={`h-1.5 rounded-full ${section.color.split(' ')[0].replace('50', '400')}`} style={{ width: `${line.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

const BalanceSheetTab: React.FC = () => {
  const currentAssetsTotal = balanceSheet.assets.current.reduce((s, a) => s + a.amount, 0);
  const nonCurrentAssetsTotal = balanceSheet.assets.non_current.reduce((s, a) => s + a.amount, 0);
  const totalAssets = currentAssetsTotal + nonCurrentAssetsTotal;
  const currentLiabTotal = balanceSheet.liabilities.current.reduce((s, a) => s + a.amount, 0);
  const nonCurrentLiabTotal = balanceSheet.liabilities.non_current.reduce((s, a) => s + a.amount, 0);
  const totalLiabilities = currentLiabTotal + nonCurrentLiabTotal;
  const totalEquity = balanceSheet.equity.reduce((s, a) => s + a.amount, 0);

  const Section = ({ title, items, total, totalLabel, headerColor }: { title: string; items: { name: string; amount: number }[]; total: number; totalLabel: string; headerColor: string }) => (
    <div className="mb-4">
      <h4 className={`text-xs font-semibold uppercase tracking-wide mb-2 ${headerColor}`}>{title}</h4>
      {items.map(item => (
        <div key={item.name} className="flex items-center justify-between py-1.5 text-sm border-b border-neutral-50">
          <span className="text-neutral-700 pl-4">{item.name}</span>
          <span className="text-neutral-900 font-mono">{fmt(item.amount)}</span>
        </div>
      ))}
      <div className="flex items-center justify-between py-2 text-sm font-semibold bg-neutral-50 px-4 rounded mt-1">
        <span className="text-neutral-900">{totalLabel}</span>
        <span className="text-neutral-900 font-mono">{fmt(total)}</span>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Quick View */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total Assets', value: fmt(totalAssets), color: 'text-blue-700' },
          { label: 'Total Liabilities', value: fmt(totalLiabilities), color: 'text-red-700' },
          { label: 'Total Equity', value: fmt(totalEquity), color: 'text-emerald-700' },
        ].map(kpi => (
          <div key={kpi.label} className="bg-white rounded-xl border border-neutral-200 p-5 text-center">
            <p className="text-xs text-neutral-500 uppercase">{kpi.label}</p>
            <p className={`text-2xl font-bold mt-1 ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Assets */}
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Assets</h3>
          <Section title="Current Assets" items={balanceSheet.assets.current} total={currentAssetsTotal} totalLabel="Total Current Assets" headerColor="text-blue-600" />
          <Section title="Non-Current Assets" items={balanceSheet.assets.non_current} total={nonCurrentAssetsTotal} totalLabel="Total Non-Current Assets" headerColor="text-blue-600" />
          <div className="flex items-center justify-between py-3 mt-2 border-t-2 border-blue-200">
            <span className="text-sm font-bold text-blue-900">TOTAL ASSETS</span>
            <span className="text-lg font-bold text-blue-700 font-mono">{fmt(totalAssets)}</span>
          </div>
        </div>

        {/* Liabilities & Equity */}
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Liabilities & Equity</h3>
          <Section title="Current Liabilities" items={balanceSheet.liabilities.current} total={currentLiabTotal} totalLabel="Total Current Liabilities" headerColor="text-red-600" />
          <Section title="Non-Current Liabilities" items={balanceSheet.liabilities.non_current} total={nonCurrentLiabTotal} totalLabel="Total Non-Current Liabilities" headerColor="text-red-600" />
          <div className="flex items-center justify-between py-2 mt-1 border-t border-red-200">
            <span className="text-sm font-bold text-red-900">TOTAL LIABILITIES</span>
            <span className="text-lg font-bold text-red-700 font-mono">{fmt(totalLiabilities)}</span>
          </div>

          <div className="mt-4">
            <Section title="Stockholders' Equity" items={balanceSheet.equity} total={totalEquity} totalLabel="Total Equity" headerColor="text-emerald-600" />
          </div>

          <div className="flex items-center justify-between py-3 mt-2 border-t-2 border-neutral-300">
            <span className="text-sm font-bold text-neutral-900">TOTAL LIABILITIES & EQUITY</span>
            <span className="text-lg font-bold text-neutral-900 font-mono">{fmt(totalLiabilities + totalEquity)}</span>
          </div>

          {/* Balance Check */}
          <div className={`mt-3 p-3 rounded-lg text-xs font-medium text-center ${
            totalAssets === totalLiabilities + totalEquity ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
          }`}>
            {totalAssets === totalLiabilities + totalEquity ? 'Balance Sheet is balanced (Assets = Liabilities + Equity)' : 'WARNING: Balance sheet does not balance'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfitAndLoss;
