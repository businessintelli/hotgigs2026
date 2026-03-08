import React from 'react';
import { ArrowTrendingUpIcon, CheckCircleIcon, UserGroupIcon, ClockIcon, AdjustmentsVerticalIcon } from '@heroicons/react/24/outline';

interface KPI {
  label: string;
  value: number | string;
  icon: React.ForwardRefExoticComponent<any>;
  color: string;
  subtitle?: string;
}

interface MonthlyStat {
  month: string;
  submissions: number;
  placements: number;
}

interface PipelineStage {
  stage: string;
  avgDays: number;
  color: string;
  isBottleneck: boolean;
}

const mockKPIs: KPI[] = [
  { label: 'Total Submissions', value: 287, icon: UserGroupIcon, color: 'bg-blue-500', subtitle: 'this quarter' },
  { label: 'Placements Closed', value: 43, icon: CheckCircleIcon, color: 'bg-emerald-500', subtitle: '15% growth YoY' },
  { label: 'Conversion Rate', value: '15%', icon: ArrowTrendingUpIcon, color: 'bg-purple-500', subtitle: 'industry avg: 12%' },
  { label: 'Avg Fill Time', value: '18 days', icon: ClockIcon, color: 'bg-amber-500', subtitle: '-2 days this month' },
  { label: 'Team Ranking', value: '#3 of 15', icon: AdjustmentsVerticalIcon, color: 'bg-indigo-500', subtitle: 'up from #5' },
];

const mockMontlyData: MonthlyStat[] = [
  { month: 'Aug', submissions: 38, placements: 5 },
  { month: 'Sep', submissions: 42, placements: 7 },
  { month: 'Oct', submissions: 35, placements: 6 },
  { month: 'Nov', submissions: 48, placements: 8 },
  { month: 'Dec', submissions: 55, placements: 9 },
  { month: 'Jan', submissions: 69, placements: 8 },
];

const mockPipelineVelocity: PipelineStage[] = [
  { stage: 'Prospect', avgDays: 2, color: 'emerald', isBottleneck: false },
  { stage: 'Qualified', avgDays: 3, color: 'emerald', isBottleneck: false },
  { stage: 'Submitted', avgDays: 4, color: 'emerald', isBottleneck: false },
  { stage: 'Interview', avgDays: 7, color: 'amber', isBottleneck: false },
  { stage: 'Offer', avgDays: 5, color: 'emerald', isBottleneck: false },
  { stage: 'Placed', avgDays: 2, color: 'emerald', isBottleneck: false },
];

const topSkillsPlaced = [
  { skill: 'React', count: 23 },
  { skill: 'Python', count: 19 },
  { skill: 'AWS', count: 17 },
  { skill: 'TypeScript', count: 15 },
  { skill: 'Node.js', count: 14 },
  { skill: 'Docker', count: 12 },
];

const topClients = [
  { name: 'TechCorp Industries', placements: 12, avgFillTime: '16 days', revenue: '$156,000' },
  { name: 'DataFlow Solutions', placements: 9, avgFillTime: '19 days', revenue: '$117,000' },
  { name: 'CloudSystems Inc', placements: 8, avgFillTime: '21 days', revenue: '$104,000' },
  { name: 'InnovateLabs', placements: 7, avgFillTime: '18 days', revenue: '$91,000' },
  { name: 'FutureAI Corp', placements: 7, avgFillTime: '17 days', revenue: '$91,000' },
];

const MonthlyChart: React.FC<{ data: MonthlyStat[] }> = ({ data }) => {
  const maxSubs = Math.max(...data.map((d) => d.submissions));
  const maxPlace = Math.max(...data.map((d) => d.placements));

  return (
    <div className="flex gap-8 items-end justify-center overflow-x-auto pb-4">
      {data.map((stat) => (
        <div key={stat.month} className="flex flex-col items-center gap-2 min-w-max">
          <div className="flex gap-2 items-end h-32">
            <div className="flex flex-col items-center">
              <div
                className="w-6 h-32 bg-blue-400 dark:bg-blue-500 rounded-t"
                style={{ height: (stat.submissions / maxSubs) * 100 }}
              />
              <span className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Sub</span>
            </div>
            <div className="flex flex-col items-center">
              <div
                className="w-6 h-32 bg-emerald-400 dark:bg-emerald-500 rounded-t"
                style={{ height: (stat.placements / maxPlace) * 100 }}
              />
              <span className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Place</span>
            </div>
          </div>
          <span className="text-sm font-semibold text-neutral-900 dark:text-white">{stat.month}</span>
        </div>
      ))}
    </div>
  );
};

const KPICard: React.FC<{ kpi: KPI }> = ({ kpi }) => {
  const { icon: Icon, label, value, color, subtitle } = kpi;
  return (
    <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-neutral-900 dark:text-white">{value}</p>
          <p className="text-sm text-neutral-500 dark:text-neutral-400">{label}</p>
          {subtitle && <p className="text-xs text-neutral-400 mt-0.5">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
};

export const RecruiterDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Recruiter Performance Dashboard</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Your metrics, analytics, and performance tracking</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {mockKPIs.map((kpi) => (
          <KPICard key={kpi.label} kpi={kpi} />
        ))}
      </div>

      {/* Monthly Trend Chart */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Monthly Submissions & Placements Trend</h3>
        <MonthlyChart data={mockMontlyData} />
      </div>

      {/* Pipeline Velocity */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Pipeline Velocity by Stage</h3>
        <div className="space-y-4">
          {mockPipelineVelocity.map((stage) => {
            const colorClass =
              stage.color === 'emerald'
                ? 'bg-emerald-500'
                : 'bg-amber-500';
            return (
              <div key={stage.stage}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-neutral-900 dark:text-white">{stage.stage}</span>
                  <span className={`text-sm font-semibold ${stage.color === 'emerald' ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                    {stage.avgDays} days avg
                  </span>
                </div>
                <div className="w-full h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${colorClass} transition-all duration-300`}
                    style={{ width: `${(stage.avgDays / 10) * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Skills Placed */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Top Skills Placed</h3>
        <div className="space-y-3">
          {topSkillsPlaced.map((item) => {
            const maxCount = Math.max(...topSkillsPlaced.map((s) => s.count));
            return (
              <div key={item.skill}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-neutral-900 dark:text-white">{item.skill}</span>
                  <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">{item.count} placements</span>
                </div>
                <div className="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${(item.count / maxCount) * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Clients */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Top Clients by Placements</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Client Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Placements
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Avg Fill Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Revenue Generated
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {topClients.map((client) => (
                <tr key={client.name} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">{client.name}</td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{client.placements}</td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{client.avgFillTime}</td>
                  <td className="px-6 py-4 text-sm font-semibold text-emerald-600 dark:text-emerald-400">{client.revenue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Comparison */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 rounded-xl p-8 border border-blue-200 dark:border-blue-800">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Performance vs Team Average</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-3">Conversion Rate</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">15%</span>
              <span className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">+3% above average</span>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-3">Average Fill Time</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">18 days</span>
              <span className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">-2 days faster</span>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-3">Placements YTD</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">43</span>
              <span className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">+15% growth</span>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-3">Team Ranking</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">#3 / 15</span>
              <span className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">up from #5</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterDashboard;
