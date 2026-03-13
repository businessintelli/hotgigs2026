import React, { useState } from 'react';

const fmt = (n: number) => '$' + n.toLocaleString();

const associates = [
  {
    id: 1, name: 'James Rodriguez', title: 'Sr. Software Engineer', client: 'TechCorp Inc', supplier: 'StaffPro Solutions',
    bill_rate: 135, pay_rate: 85, markup: 58.8, margin_hr: 50, status: 'active', start: '2025-06-15', hours_ytd: 440, hours_mtd: 168,
    revenue: { ytd: 59400, mtd: 22680, last: 21600 },
    costs: { payroll: { ytd: 37400, mtd: 14280 }, benefits: { ytd: 4800, mtd: 1600 }, insurance: { ytd: 2400, mtd: 800 }, taxes: { ytd: 5610, mtd: 2142 }, bgc: { ytd: 350, mtd: 0 }, reimburse: { ytd: 1200, mtd: 400 }, total: { ytd: 51760, mtd: 19222 } },
    profit: { ytd: 7640, mtd: 3458 }, margin: 12.9,
    trend: [{ m: 'Jan', rev: 21600, cost: 16250, pft: 5350 }, { m: 'Feb', rev: 21600, cost: 16288, pft: 5312 }, { m: 'Mar', rev: 22680, cost: 19222, pft: 3458 }],
  },
  {
    id: 2, name: 'Priya Sharma', title: 'Data Analyst', client: 'FinanceGroup LLC', supplier: 'TalentBridge Agency',
    bill_rate: 105, pay_rate: 62, markup: 69.4, margin_hr: 43, status: 'active', start: '2025-09-01', hours_ytd: 400, hours_mtd: 160,
    revenue: { ytd: 42000, mtd: 16800, last: 16800 },
    costs: { payroll: { ytd: 24800, mtd: 9920 }, benefits: { ytd: 3600, mtd: 1200 }, insurance: { ytd: 1800, mtd: 600 }, taxes: { ytd: 3720, mtd: 1488 }, bgc: { ytd: 250, mtd: 0 }, reimburse: { ytd: 600, mtd: 200 }, total: { ytd: 34770, mtd: 13408 } },
    profit: { ytd: 7230, mtd: 3392 }, margin: 17.2,
    trend: [{ m: 'Jan', rev: 16800, cost: 10654, pft: 6146 }, { m: 'Feb', rev: 16800, cost: 10708, pft: 6092 }, { m: 'Mar', rev: 16800, cost: 13408, pft: 3392 }],
  },
  {
    id: 3, name: 'Marcus Johnson', title: 'Registered Nurse', client: 'MedFirst Health', supplier: 'StaffPro Solutions',
    bill_rate: 92, pay_rate: 58, markup: 58.6, margin_hr: 34, status: 'active', start: '2025-04-01', hours_ytd: 480, hours_mtd: 176,
    revenue: { ytd: 44160, mtd: 16192, last: 14720 },
    costs: { payroll: { ytd: 27840, mtd: 10208 }, benefits: { ytd: 4200, mtd: 1400 }, insurance: { ytd: 3600, mtd: 1200 }, taxes: { ytd: 4176, mtd: 1531 }, bgc: { ytd: 450, mtd: 0 }, reimburse: { ytd: 800, mtd: 150 }, total: { ytd: 41066, mtd: 14489 } },
    profit: { ytd: 3094, mtd: 1703 }, margin: 7.0,
    trend: [{ m: 'Jan', rev: 14720, cost: 12928, pft: 1792 }, { m: 'Feb', rev: 14720, cost: 13649, pft: 1071 }, { m: 'Mar', rev: 16192, cost: 14489, pft: 1703 }],
  },
  {
    id: 4, name: 'Emily Chen', title: 'DevOps Engineer', client: 'TechCorp Inc', supplier: 'CodeForce Inc',
    bill_rate: 155, pay_rate: 105, markup: 47.6, margin_hr: 50, status: 'active', start: '2025-11-01', hours_ytd: 400, hours_mtd: 168,
    revenue: { ytd: 62000, mtd: 26040, last: 24800 },
    costs: { payroll: { ytd: 42000, mtd: 17640 }, benefits: { ytd: 4800, mtd: 1600 }, insurance: { ytd: 2400, mtd: 800 }, taxes: { ytd: 6300, mtd: 2646 }, bgc: { ytd: 350, mtd: 0 }, reimburse: { ytd: 1500, mtd: 500 }, total: { ytd: 57350, mtd: 23186 } },
    profit: { ytd: 4650, mtd: 2854 }, margin: 7.5,
    trend: [{ m: 'Jan', rev: 24800, cost: 17082, pft: 7718 }, { m: 'Feb', rev: 24800, cost: 17082, pft: 7718 }, { m: 'Mar', rev: 26040, cost: 23186, pft: 2854 }],
  },
  {
    id: 5, name: 'David Wilson', title: 'Project Manager', client: 'BuildRight Construction', supplier: 'TalentBridge Agency',
    bill_rate: 88, pay_rate: 55, markup: 60.0, margin_hr: 33, status: 'active', start: '2025-08-15', hours_ytd: 420, hours_mtd: 160,
    revenue: { ytd: 36960, mtd: 14080, last: 14080 },
    costs: { payroll: { ytd: 23100, mtd: 8800 }, benefits: { ytd: 3600, mtd: 1200 }, insurance: { ytd: 1800, mtd: 600 }, taxes: { ytd: 3465, mtd: 1320 }, bgc: { ytd: 250, mtd: 0 }, reimburse: { ytd: 2200, mtd: 800 }, total: { ytd: 34415, mtd: 12720 } },
    profit: { ytd: 2545, mtd: 1360 }, margin: 6.9,
    trend: [{ m: 'Jan', rev: 14080, cost: 10848, pft: 3232 }, { m: 'Feb', rev: 14080, cost: 10847, pft: 3233 }, { m: 'Mar', rev: 14080, cost: 12720, pft: 1360 }],
  },
  {
    id: 6, name: 'Sarah Thompson', title: 'UX Designer', client: 'RetailMax Corp', supplier: 'StaffPro Solutions',
    bill_rate: 110, pay_rate: 68, markup: 61.8, margin_hr: 42, status: 'active', start: '2026-01-06', hours_ytd: 360, hours_mtd: 152,
    revenue: { ytd: 39600, mtd: 16720, last: 17600 },
    costs: { payroll: { ytd: 24480, mtd: 10336 }, benefits: { ytd: 3600, mtd: 1200 }, insurance: { ytd: 1800, mtd: 600 }, taxes: { ytd: 3672, mtd: 1550 }, bgc: { ytd: 350, mtd: 0 }, reimburse: { ytd: 450, mtd: 150 }, total: { ytd: 34352, mtd: 13836 } },
    profit: { ytd: 5248, mtd: 2884 }, margin: 13.3,
    trend: [{ m: 'Jan', rev: 17600, cost: 10258, pft: 7342 }, { m: 'Feb', rev: 17600, cost: 10258, pft: 7342 }, { m: 'Mar', rev: 16720, cost: 13836, pft: 2884 }],
  },
];

export const AssociateFinancials: React.FC = () => {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const selected = associates.find(a => a.id === selectedId);

  const totalRevYTD = associates.reduce((s, a) => s + a.revenue.ytd, 0);
  const totalCostYTD = associates.reduce((s, a) => s + a.costs.total.ytd, 0);
  const totalProfitYTD = associates.reduce((s, a) => s + a.profit.ytd, 0);
  const avgMargin = associates.reduce((s, a) => s + a.margin, 0) / associates.length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Associate 360° Financial View</h1>
          <p className="text-neutral-500 mt-1">Revenue, payroll, benefits, insurance, and profit per associate</p>
        </div>
        <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">Export</button>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Revenue YTD', value: fmt(totalRevYTD), color: 'text-blue-700' },
          { label: 'Total Costs YTD', value: fmt(totalCostYTD), color: 'text-red-700' },
          { label: 'Total Profit YTD', value: fmt(totalProfitYTD), color: 'text-emerald-700' },
          { label: 'Avg Effective Margin', value: `${avgMargin.toFixed(1)}%`, color: 'text-violet-700' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Associate Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {associates.map(a => (
          <div key={a.id} onClick={() => setSelectedId(selectedId === a.id ? null : a.id)} className={`bg-white rounded-xl border p-5 cursor-pointer transition-all hover:shadow-md ${selectedId === a.id ? 'border-violet-400 ring-2 ring-violet-100' : 'border-neutral-200'}`}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-sm font-semibold text-neutral-900">{a.name}</h4>
                <p className="text-xs text-neutral-500">{a.title}</p>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${a.margin >= 15 ? 'bg-emerald-100 text-emerald-700' : a.margin >= 10 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                {a.margin}% margin
              </span>
            </div>

            <div className="flex items-center gap-2 text-xs text-neutral-500 mb-3">
              <span>{a.client}</span>
              <span className="text-neutral-300">|</span>
              <span>{a.supplier}</span>
            </div>

            {/* Rate Info */}
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="text-center p-2 bg-blue-50 rounded-lg">
                <p className="text-xs font-bold text-blue-700">${a.bill_rate}</p>
                <p className="text-[10px] text-blue-500">Bill Rate</p>
              </div>
              <div className="text-center p-2 bg-red-50 rounded-lg">
                <p className="text-xs font-bold text-red-700">${a.pay_rate}</p>
                <p className="text-[10px] text-red-500">Pay Rate</p>
              </div>
              <div className="text-center p-2 bg-emerald-50 rounded-lg">
                <p className="text-xs font-bold text-emerald-700">${a.margin_hr}</p>
                <p className="text-[10px] text-emerald-500">Margin/hr</p>
              </div>
            </div>

            {/* Revenue vs Costs */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-neutral-500">YTD Revenue</span>
                <span className="font-semibold text-blue-700">{fmt(a.revenue.ytd)}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-neutral-500">YTD Total Cost</span>
                <span className="font-semibold text-red-700">{fmt(a.costs.total.ytd)}</span>
              </div>
              <div className="flex items-center justify-between text-xs border-t border-neutral-100 pt-1.5">
                <span className="text-neutral-700 font-medium">YTD Profit</span>
                <span className={`font-bold ${a.profit.ytd >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>{fmt(a.profit.ytd)}</span>
              </div>
            </div>

            {/* Mini trend chart bars */}
            <div className="mt-3 flex items-end gap-1 h-10">
              {a.trend.map((t, i) => {
                const maxRev = Math.max(...a.trend.map(x => x.rev));
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                    <div className="w-full flex items-end gap-0.5" style={{ height: '32px' }}>
                      <div className="flex-1 bg-blue-300 rounded-t" style={{ height: `${(t.rev / maxRev) * 100}%` }} />
                      <div className="flex-1 bg-emerald-400 rounded-t" style={{ height: `${(t.pft / maxRev) * 100}%` }} />
                    </div>
                    <span className="text-[9px] text-neutral-400">{t.m}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Detail Panel */}
      {selected && (
        <div className="bg-white rounded-xl border border-violet-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-neutral-900">{selected.name} — 360° Financial Detail</h3>
              <p className="text-sm text-neutral-500">{selected.title} at {selected.client} (via {selected.supplier})</p>
            </div>
            <button onClick={() => setSelectedId(null)} className="text-neutral-400 hover:text-neutral-600">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Rates & Hours */}
            <div>
              <h4 className="text-xs font-semibold text-neutral-900 uppercase mb-3">Rates & Hours</h4>
              <div className="space-y-2">
                {[
                  { label: 'Bill Rate', value: `$${selected.bill_rate}/hr` },
                  { label: 'Pay Rate', value: `$${selected.pay_rate}/hr` },
                  { label: 'Markup', value: `${selected.markup}%` },
                  { label: 'Margin/Hour', value: `$${selected.margin_hr}` },
                  { label: 'Hours YTD', value: selected.hours_ytd.toString() },
                  { label: 'Hours MTD', value: selected.hours_mtd.toString() },
                  { label: 'Start Date', value: selected.start },
                ].map(row => (
                  <div key={row.label} className="flex items-center justify-between text-sm">
                    <span className="text-neutral-500">{row.label}</span>
                    <span className="font-medium text-neutral-900">{row.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Cost Breakdown */}
            <div>
              <h4 className="text-xs font-semibold text-neutral-900 uppercase mb-3">Cost Breakdown (YTD)</h4>
              <div className="space-y-2">
                {[
                  { label: 'Payroll', value: selected.costs.payroll.ytd, color: 'bg-red-400' },
                  { label: 'Benefits', value: selected.costs.benefits.ytd, color: 'bg-orange-400' },
                  { label: 'Insurance', value: selected.costs.insurance.ytd, color: 'bg-amber-400' },
                  { label: 'Payroll Taxes', value: selected.costs.taxes.ytd, color: 'bg-yellow-400' },
                  { label: 'BGC/Drug Test', value: selected.costs.bgc.ytd, color: 'bg-pink-400' },
                  { label: 'Reimbursements', value: selected.costs.reimburse.ytd, color: 'bg-rose-400' },
                ].map(item => (
                  <div key={item.label}>
                    <div className="flex items-center justify-between text-xs mb-0.5">
                      <span className="text-neutral-600">{item.label}</span>
                      <span className="font-medium text-neutral-900">{fmt(item.value)}</span>
                    </div>
                    <div className="w-full bg-neutral-100 rounded-full h-1.5">
                      <div className={`${item.color} h-1.5 rounded-full`} style={{ width: `${(item.value / selected.costs.total.ytd) * 100}%` }} />
                    </div>
                  </div>
                ))}
                <div className="flex items-center justify-between text-sm font-bold pt-2 border-t border-neutral-200">
                  <span className="text-neutral-900">Total Costs</span>
                  <span className="text-red-700">{fmt(selected.costs.total.ytd)}</span>
                </div>
              </div>
            </div>

            {/* P&L Summary */}
            <div>
              <h4 className="text-xs font-semibold text-neutral-900 uppercase mb-3">Profitability</h4>
              <div className="space-y-3">
                <div className="p-4 bg-blue-50 rounded-lg text-center">
                  <p className="text-xs text-blue-600">YTD Revenue</p>
                  <p className="text-xl font-bold text-blue-700">{fmt(selected.revenue.ytd)}</p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg text-center">
                  <p className="text-xs text-red-600">YTD Total Costs</p>
                  <p className="text-xl font-bold text-red-700">{fmt(selected.costs.total.ytd)}</p>
                </div>
                <div className={`p-4 rounded-lg text-center ${selected.profit.ytd >= 0 ? 'bg-emerald-50' : 'bg-red-50'}`}>
                  <p className={`text-xs ${selected.profit.ytd >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>YTD Profit</p>
                  <p className={`text-xl font-bold ${selected.profit.ytd >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>{fmt(selected.profit.ytd)}</p>
                </div>
                <div className="p-3 bg-violet-50 rounded-lg text-center">
                  <p className="text-xs text-violet-600">Effective Margin</p>
                  <p className="text-lg font-bold text-violet-700">{selected.margin}%</p>
                </div>
              </div>

              {/* Monthly Trend */}
              <h4 className="text-xs font-semibold text-neutral-900 uppercase mt-4 mb-2">Monthly Trend</h4>
              <div className="space-y-1.5">
                {selected.trend.map(t => (
                  <div key={t.m} className="flex items-center justify-between text-xs">
                    <span className="text-neutral-500 w-8">{t.m}</span>
                    <span className="text-blue-600">{fmt(t.rev)}</span>
                    <span className="text-red-600">{fmt(t.cost)}</span>
                    <span className={`font-medium ${t.pft >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>{fmt(t.pft)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <div className="px-5 py-3 bg-neutral-50 border-b border-neutral-200">
          <h3 className="text-sm font-semibold text-neutral-900">Associate Financial Comparison</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-100">
              <th className="text-left px-5 py-3 text-xs font-medium text-neutral-500">Associate</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Bill Rate</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Pay Rate</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Margin/hr</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">YTD Revenue</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">YTD Costs</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">YTD Profit</th>
              <th className="text-right px-3 py-3 text-xs font-medium text-neutral-500">Margin %</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {associates.map(a => (
              <tr key={a.id} className="hover:bg-neutral-50 cursor-pointer" onClick={() => setSelectedId(a.id)}>
                <td className="px-5 py-3">
                  <p className="font-medium text-neutral-900">{a.name}</p>
                  <p className="text-xs text-neutral-500">{a.client}</p>
                </td>
                <td className="px-3 py-3 text-right">${a.bill_rate}</td>
                <td className="px-3 py-3 text-right">${a.pay_rate}</td>
                <td className="px-3 py-3 text-right font-medium text-emerald-700">${a.margin_hr}</td>
                <td className="px-3 py-3 text-right font-medium text-blue-700">{fmt(a.revenue.ytd)}</td>
                <td className="px-3 py-3 text-right text-red-600">{fmt(a.costs.total.ytd)}</td>
                <td className={`px-3 py-3 text-right font-bold ${a.profit.ytd >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>{fmt(a.profit.ytd)}</td>
                <td className="px-3 py-3 text-right">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${a.margin >= 15 ? 'bg-emerald-100 text-emerald-700' : a.margin >= 10 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>{a.margin}%</span>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-neutral-50 border-t border-neutral-200">
            <tr>
              <td className="px-5 py-3 font-bold">Total / Average</td>
              <td className="px-3 py-3 text-right font-medium">${Math.round(associates.reduce((s, a) => s + a.bill_rate, 0) / associates.length)}</td>
              <td className="px-3 py-3 text-right font-medium">${Math.round(associates.reduce((s, a) => s + a.pay_rate, 0) / associates.length)}</td>
              <td className="px-3 py-3 text-right font-medium text-emerald-700">${Math.round(associates.reduce((s, a) => s + a.margin_hr, 0) / associates.length)}</td>
              <td className="px-3 py-3 text-right font-bold text-blue-700">{fmt(totalRevYTD)}</td>
              <td className="px-3 py-3 text-right font-bold text-red-600">{fmt(totalCostYTD)}</td>
              <td className="px-3 py-3 text-right font-bold text-emerald-700">{fmt(totalProfitYTD)}</td>
              <td className="px-3 py-3 text-right font-bold">{avgMargin.toFixed(1)}%</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default AssociateFinancials;
