import React from 'react';

const fmt = (n: number) => '$' + n.toLocaleString();

const summary = {
  ytd_revenue: 1545000, ytd_expenses: 978000, ytd_gross_profit: 567000, ytd_net_income: 266100,
  avg_monthly_revenue: 515000, revenue_growth_yoy: 18.4, gross_margin: 36.7, net_margin: 17.2,
  revenue_per_associate: 35340, avg_bill_rate: 108.50, avg_pay_rate: 68.20, avg_markup: 59.1,
};

const monthlyTrend = [
  { month: '2025-04', revenue: 320000, expenses: 218000, profit: 102000 },
  { month: '2025-05', revenue: 345000, expenses: 232000, profit: 113000 },
  { month: '2025-06', revenue: 368000, expenses: 245000, profit: 123000 },
  { month: '2025-07', revenue: 382000, expenses: 252000, profit: 130000 },
  { month: '2025-08', revenue: 395000, expenses: 260000, profit: 135000 },
  { month: '2025-09', revenue: 412000, expenses: 271000, profit: 141000 },
  { month: '2025-10', revenue: 428000, expenses: 280000, profit: 148000 },
  { month: '2025-11', revenue: 445000, expenses: 290000, profit: 155000 },
  { month: '2025-12', revenue: 462000, expenses: 298000, profit: 164000 },
  { month: '2026-01', revenue: 485000, expenses: 312000, profit: 173000 },
  { month: '2026-02', revenue: 512000, expenses: 325000, profit: 187000 },
  { month: '2026-03', revenue: 548000, expenses: 341000, profit: 207000 },
];

const byIndustry = [
  { industry: 'Technology', revenue: 549000, percent: 35.5, color: 'bg-blue-500' },
  { industry: 'Healthcare', revenue: 312000, percent: 20.2, color: 'bg-emerald-500' },
  { industry: 'Financial Services', revenue: 268000, percent: 17.3, color: 'bg-violet-500' },
  { industry: 'Construction', revenue: 198000, percent: 12.8, color: 'bg-amber-500' },
  { industry: 'Retail', revenue: 156000, percent: 10.1, color: 'bg-rose-500' },
  { industry: 'Automotive/Education', revenue: 62000, percent: 4.0, color: 'bg-cyan-500' },
];

const topAssociates = [
  { name: 'Emily Chen', revenue: 62000, margin: 7.5, hours: 400 },
  { name: 'James Rodriguez', revenue: 59400, margin: 12.9, hours: 440 },
  { name: 'Marcus Johnson', revenue: 44160, margin: 7.0, hours: 480 },
  { name: 'Priya Sharma', revenue: 42000, margin: 17.2, hours: 400 },
  { name: 'Sarah Thompson', revenue: 39600, margin: 13.3, hours: 360 },
];

export const RevenueAnalytics: React.FC = () => {
  const maxRev = Math.max(...monthlyTrend.map(m => m.revenue));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Revenue Analytics</h1>
          <p className="text-neutral-500 mt-1">Comprehensive revenue intelligence, trends, and performance metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <select className="px-3 py-1.5 border border-neutral-200 rounded-lg text-sm bg-white">
            <option>Last 12 Months</option>
            <option>YTD</option>
            <option>Last Quarter</option>
          </select>
          <button className="px-4 py-1.5 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">Export</button>
        </div>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'YTD Revenue', value: fmt(summary.ytd_revenue), color: 'text-blue-700', sub: `+${summary.revenue_growth_yoy}% YoY` },
          { label: 'Gross Profit', value: fmt(summary.ytd_gross_profit), color: 'text-emerald-700', sub: `${summary.gross_margin}% margin` },
          { label: 'Net Income', value: fmt(summary.ytd_net_income), color: 'text-violet-700', sub: `${summary.net_margin}% margin` },
          { label: 'Revenue/Associate', value: fmt(summary.revenue_per_associate), color: 'text-amber-700', sub: `${summary.avg_bill_rate} avg bill` },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-5">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
            <p className="text-xs text-neutral-500 mt-0.5">{k.sub}</p>
          </div>
        ))}
      </div>

      {/* Rate Metrics */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Avg Bill Rate', value: `$${summary.avg_bill_rate}/hr`, color: 'text-blue-600' },
          { label: 'Avg Pay Rate', value: `$${summary.avg_pay_rate}/hr`, color: 'text-red-600' },
          { label: 'Avg Markup', value: `${summary.avg_markup}%`, color: 'text-emerald-600' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-4 text-center">
            <p className="text-xs text-neutral-500">{k.label}</p>
            <p className={`text-xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Revenue Trend Chart (Bar-based) */}
      <div className="bg-white rounded-xl border border-neutral-200 p-6">
        <h3 className="text-sm font-semibold text-neutral-900 mb-4">12-Month Revenue Trend</h3>
        <div className="flex items-end gap-1.5" style={{ height: '200px' }}>
          {monthlyTrend.map(m => (
            <div key={m.month} className="flex-1 flex flex-col items-center">
              <div className="w-full flex flex-col items-center" style={{ height: '180px', justifyContent: 'flex-end' }}>
                <div className="w-full max-w-[40px] flex flex-col items-stretch">
                  <div className="bg-blue-400 rounded-t" style={{ height: `${(m.revenue / maxRev) * 140}px` }}>
                    <div className="bg-emerald-500 rounded-t" style={{ height: `${(m.profit / maxRev) * 140}px` }} />
                  </div>
                </div>
              </div>
              <span className="text-[9px] text-neutral-400 mt-1">{m.month.split('-')[1]}</span>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-center gap-6 mt-3 text-xs text-neutral-500">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-blue-400" />Revenue</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500" />Profit</span>
        </div>

        {/* Monthly Data Table */}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-neutral-100">
                <th className="text-left py-2 text-neutral-500">Month</th>
                {monthlyTrend.map(m => <th key={m.month} className="text-right py-2 text-neutral-500 px-1">{m.month.split('-')[1]}</th>)}
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-neutral-50">
                <td className="py-1.5 text-neutral-700 font-medium">Revenue</td>
                {monthlyTrend.map(m => <td key={m.month} className="text-right py-1.5 text-blue-700 px-1">{(m.revenue / 1000).toFixed(0)}K</td>)}
              </tr>
              <tr className="border-b border-neutral-50">
                <td className="py-1.5 text-neutral-700 font-medium">Expenses</td>
                {monthlyTrend.map(m => <td key={m.month} className="text-right py-1.5 text-red-600 px-1">{(m.expenses / 1000).toFixed(0)}K</td>)}
              </tr>
              <tr>
                <td className="py-1.5 text-neutral-700 font-bold">Profit</td>
                {monthlyTrend.map(m => <td key={m.month} className="text-right py-1.5 text-emerald-700 font-bold px-1">{(m.profit / 1000).toFixed(0)}K</td>)}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Revenue by Industry + Top Associates */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Industry Breakdown */}
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Revenue by Industry</h3>
          <div className="space-y-3">
            {byIndustry.map(ind => (
              <div key={ind.industry}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${ind.color}`} />
                    <span className="text-neutral-700">{ind.industry}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-neutral-900">{fmt(ind.revenue)}</span>
                    <span className="text-xs text-neutral-500 w-10 text-right">{ind.percent}%</span>
                  </div>
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-2 ml-5">
                  <div className={`${ind.color} h-2 rounded-full transition-all`} style={{ width: `${ind.percent}%` }} />
                </div>
              </div>
            ))}
          </div>

          {/* Pie-like summary */}
          <div className="mt-4 flex rounded-full h-6 overflow-hidden">
            {byIndustry.map(ind => (
              <div key={ind.industry} className={`${ind.color}`} style={{ width: `${ind.percent}%` }} />
            ))}
          </div>
        </div>

        {/* Top Associates */}
        <div className="bg-white rounded-xl border border-neutral-200 p-6">
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">Top Revenue-Generating Associates</h3>
          <div className="space-y-3">
            {topAssociates.map((a, i) => (
              <div key={a.name} className="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg">
                <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white ${
                  i === 0 ? 'bg-amber-500' : i === 1 ? 'bg-neutral-400' : i === 2 ? 'bg-orange-600' : 'bg-neutral-300'
                }`}>
                  {i + 1}
                </span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-neutral-900">{a.name}</p>
                  <div className="flex items-center gap-3 text-xs text-neutral-500">
                    <span>{fmt(a.revenue)} rev</span>
                    <span>{a.margin}% margin</span>
                    <span>{a.hours}h</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-blue-700">{fmt(a.revenue)}</p>
                  <p className="text-[10px] text-neutral-500">${(a.revenue / a.hours).toFixed(0)}/hr effective</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Revenue Growth Insights */}
      <div className="bg-gradient-to-r from-violet-50 to-blue-50 rounded-xl border border-violet-200 p-6">
        <h3 className="text-sm font-semibold text-violet-900 mb-3">Revenue Growth Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'MoM Revenue Growth', value: '+7.0%', detail: '$548K vs $512K', color: 'text-emerald-700' },
            { label: 'YoY Revenue Growth', value: '+18.4%', detail: 'vs same period last year', color: 'text-blue-700' },
            { label: 'Avg Monthly Revenue', value: fmt(summary.avg_monthly_revenue), detail: 'trailing 12 months', color: 'text-violet-700' },
            { label: 'Revenue Run Rate', value: fmt(548000 * 12), detail: 'annualized from March', color: 'text-amber-700' },
          ].map(insight => (
            <div key={insight.label} className="text-center p-3 bg-white/60 rounded-lg">
              <p className="text-xs text-neutral-600">{insight.label}</p>
              <p className={`text-xl font-bold mt-1 ${insight.color}`}>{insight.value}</p>
              <p className="text-[10px] text-neutral-500 mt-0.5">{insight.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RevenueAnalytics;
