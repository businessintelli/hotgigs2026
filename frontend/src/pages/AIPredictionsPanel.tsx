import React, { useState } from 'react';
import { ExclamationTriangleIcon, ArrowArrowTrendingUpIcon, CheckCircleIcon, LightBulbIcon, ShieldExclamationIcon, ClockIcon } from '@heroicons/react/24/outline';

interface WorkforceForecast {
  category: string;
  demand: number;
  confidence: number;
}

interface SupplierPrediction {
  name: string;
  fillProbability: number;
}

interface SkillShortageAlert {
  skill: string;
  riskLevel: 'HIGH' | 'MEDIUM' | 'LOW';
  currentSupply: number;
  projectedDemand: number;
}

interface AIInsight {
  id: string;
  message: string;
  category: 'recommendation' | 'warning' | 'opportunity';
  timestamp: string;
}

const mockWorkforceForecast: WorkforceForecast[] = [
  { category: 'Software Engineer', demand: 62, confidence: 88 },
  { category: 'QA Engineer', demand: 31, confidence: 82 },
  { category: 'DevOps Engineer', demand: 28, confidence: 79 },
  { category: 'Frontend Developer', demand: 45, confidence: 85 },
  { category: 'Backend Developer', demand: 38, confidence: 84 },
  { category: 'Full Stack Developer', demand: 22, confidence: 76 },
];

const mockSupplierPredictions: SupplierPrediction[] = [
  { name: 'TechStaff Inc', fillProbability: 92 },
  { name: 'GlobalTalent Partners', fillProbability: 87 },
  { name: 'ProStaffing Solutions', fillProbability: 78 },
  { name: 'Elite Recruiters', fillProbability: 71 },
  { name: 'NextGen Staffing', fillProbability: 63 },
];

const mockSkillShortageAlerts: SkillShortageAlert[] = [
  { skill: 'Kubernetes', riskLevel: 'HIGH', currentSupply: 12, projectedDemand: 45 },
  { skill: 'Machine Learning', riskLevel: 'HIGH', currentSupply: 8, projectedDemand: 38 },
  { skill: 'Rust', riskLevel: 'MEDIUM', currentSupply: 15, projectedDemand: 32 },
  { skill: 'Go', riskLevel: 'MEDIUM', currentSupply: 20, projectedDemand: 35 },
  { skill: 'React', riskLevel: 'LOW', currentSupply: 95, projectedDemand: 120 },
];

const mockAIInsights: AIInsight[] = [
  {
    id: '1',
    message: 'Market trend: Kubernetes demand increasing 35% QoQ. Consider attracting specialized candidates.',
    category: 'opportunity',
    timestamp: '2 hours ago',
  },
  {
    id: '2',
    message: 'TechStaff Inc has submitted 8 candidates in past week (avg: 4). Consider exclusive partnership.',
    category: 'recommendation',
    timestamp: '4 hours ago',
  },
  {
    id: '3',
    message: 'Conversion rate dropped 5% last week. Interview process may need optimization.',
    category: 'warning',
    timestamp: '6 hours ago',
  },
  {
    id: '4',
    message: 'Sarah Lee (candidate) predicted to close 3 offers in next 30 days. Highest probability this quarter.',
    category: 'opportunity',
    timestamp: '8 hours ago',
  },
  {
    id: '5',
    message: 'DevOps roles filling 20% slower than predicted. Recommend increasing recruiter focus.',
    category: 'warning',
    timestamp: '12 hours ago',
  },
  {
    id: '6',
    message: 'React + Node.js combo candidates rare. Consider upskilling program to address gap.',
    category: 'recommendation',
    timestamp: '1 day ago',
  },
];

const mockRevenueForecost = {
  projection: '$2.8M',
  confidence: 84,
  range: '$2.4M - $3.1M',
};

const mockComplianceAlerts = [
  { item: 'NDA Renewal - John Smith', daysUntil: 12 },
  { item: 'Background Check - Jane Doe', daysUntil: 5 },
  { item: 'Certification Renewal - Mike Johnson', daysUntil: 8 },
];

const GaugeChart: React.FC<{ probability: number; size?: number }> = ({ probability, size = 120 }) => {
  const circumference = 2 * Math.PI * (size / 2 - 10);
  const offset = circumference - (probability / 100) * circumference;

  const getColor = () => {
    if (probability >= 80) return 'emerald';
    if (probability >= 60) return 'amber';
    return 'red';
  };

  const color = getColor();
  const colorClass =
    color === 'emerald'
      ? 'text-emerald-600 dark:text-emerald-400'
      : color === 'amber'
        ? 'text-amber-600 dark:text-amber-400'
        : 'text-red-600 dark:text-red-400';

  return (
    <div className="flex flex-col items-center">
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size / 2 + 10} className="transform -rotate-90">
          <circle cx={size / 2} cy={size / 2} r={size / 2 - 10} fill="none" stroke="currentColor" strokeWidth="4" className="text-neutral-200 dark:text-neutral-700" />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={size / 2 - 10}
            fill="none"
            stroke="currentColor"
            strokeWidth="4"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={colorClass}
            style={{ transition: 'stroke-dashoffset 0.3s ease' }}
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className={`text-2xl font-bold ${colorClass}`}>{probability}%</span>
        </div>
      </div>
    </div>
  );
};

const InsightCard: React.FC<{ insight: AIInsight }> = ({ insight }) => {
  const bgColor =
    insight.category === 'opportunity'
      ? 'bg-emerald-50 dark:bg-emerald-900/10 border-emerald-200 dark:border-emerald-800'
      : insight.category === 'warning'
        ? 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800'
        : 'bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800';

  const icon =
    insight.category === 'opportunity' ? (
      <ArrowTrendingUpIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
    ) : insight.category === 'warning' ? (
      <ExclamationTriangleIcon className="w-4 h-4 text-red-600 dark:text-red-400" />
    ) : (
      <LightBulbIcon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
    );

  return (
    <div className={`p-4 rounded-lg border ${bgColor} flex items-start gap-3`}>
      <div className="flex-shrink-0 mt-0.5">{icon}</div>
      <div className="flex-1">
        <p className="text-sm text-neutral-700 dark:text-neutral-300">{insight.message}</p>
        <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">{insight.timestamp}</p>
      </div>
    </div>
  );
};

export const AIPredictionsPanel: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">AI Predictions Dashboard</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Advanced predictive analytics powered by machine learning</p>
      </div>

      {/* Workforce Forecast */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Next Quarter Workforce Forecast</h3>
        <div className="space-y-4">
          {mockWorkforceForecast.map((forecast) => (
            <div key={forecast.category}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-neutral-900 dark:text-white">{forecast.category}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">{forecast.demand}</span>
                  <span className="text-xs text-neutral-500 dark:text-neutral-400">positions</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600"
                    style={{ width: `${(forecast.demand / 62) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-neutral-500 dark:text-neutral-400 w-12 text-right">{forecast.confidence}% confidence</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Supplier Predictions */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Supplier Fill Probability Predictions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {mockSupplierPredictions.map((supplier) => (
            <div key={supplier.name} className="flex flex-col items-center p-4">
              <GaugeChart probability={supplier.fillProbability} size={100} />
              <p className="text-sm font-medium text-neutral-900 dark:text-white mt-4 text-center">{supplier.name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Skill Shortage Alerts */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Skill Shortage Risk Alerts</h3>
        <div className="space-y-3">
          {mockSkillShortageAlerts.map((alert) => {
            const bgColor =
              alert.riskLevel === 'HIGH'
                ? 'bg-red-50 dark:bg-red-900/10 border-l-red-500'
                : alert.riskLevel === 'MEDIUM'
                  ? 'bg-amber-50 dark:bg-amber-900/10 border-l-amber-500'
                  : 'bg-blue-50 dark:bg-blue-900/10 border-l-blue-500';

            const badgeColor =
              alert.riskLevel === 'HIGH'
                ? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                : alert.riskLevel === 'MEDIUM'
                  ? 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
                  : 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';

            return (
              <div key={alert.skill} className={`p-4 rounded-lg border-l-4 border ${bgColor}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold text-neutral-900 dark:text-white">{alert.skill}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${badgeColor}`}>{alert.riskLevel} RISK</span>
                    </div>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      Current supply: <span className="font-semibold">{alert.currentSupply}</span> | Projected demand: <span className="font-semibold">{alert.projectedDemand}</span> (gap: {alert.projectedDemand - alert.currentSupply})
                    </p>
                  </div>
                  <ExclamationTriangleIcon className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-1 flex-shrink-0" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Revenue Forecast */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 rounded-xl p-8 border border-green-200 dark:border-green-800">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Revenue Forecast</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">Q2 Projection</p>
            <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">{mockRevenueForecost.projection}</p>
          </div>
          <div>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">Confidence Level</p>
            <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">{mockRevenueForecost.confidence}%</p>
          </div>
          <div>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">Confidence Range</p>
            <p className="text-lg font-semibold text-emerald-600 dark:text-emerald-400">{mockRevenueForecost.range}</p>
          </div>
        </div>
      </div>

      {/* Compliance Risk Alerts */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6 flex items-center gap-2">
          <ShieldExclamationIcon className="w-5 h-5" />
          Compliance Risk Alerts
        </h3>
        <div className="space-y-3">
          {mockComplianceAlerts.map((alert, i) => (
            <div key={i} className={`p-4 rounded-lg border-l-4 ${alert.daysUntil <= 7 ? 'border-l-red-500 bg-red-50 dark:bg-red-900/10' : 'border-l-amber-500 bg-amber-50 dark:bg-amber-900/10'}`}>
              <div className="flex items-center justify-between">
                <p className="font-medium text-neutral-900 dark:text-white">{alert.item}</p>
                <div className="flex items-center gap-2">
                  <ClockIcon className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
                  <span className={`text-sm font-semibold ${alert.daysUntil <= 7 ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'}`}>
                    {alert.daysUntil} days
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Insights Feed */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6 flex items-center gap-2">
          <LightBulbIcon className="w-5 h-5" />
          AI Insights & Recommendations
        </h3>

        {/* Category Filter */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {['all', 'recommendation', 'warning', 'opportunity'].map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                selectedCategory === category
                  ? 'bg-primary-500 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300'
              }`}
            >
              {category === 'all' ? 'All Insights' : category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>

        {/* Insights List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {mockAIInsights
            .filter((insight) => !selectedCategory || selectedCategory === 'all' || insight.category === selectedCategory)
            .map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
        </div>
      </div>
    </div>
  );
};

export default AIPredictionsPanel;
