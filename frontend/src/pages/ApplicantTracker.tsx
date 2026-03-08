import React, { useState } from 'react';
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface PipelineStage {
  stage: string;
  count: number;
  avgDays: number;
  isBottleneck: boolean;
}

interface TopCandidate {
  id: string;
  name: string;
  currentStage: string;
  score: number;
  daysInStage: number;
  skills: string[];
}

interface ConversionMetric {
  from: string;
  to: string;
  percentage: number;
  count: string;
}

const mockPipelineStages: PipelineStage[] = [
  { stage: 'Sourced', count: 200, avgDays: 2, isBottleneck: false },
  { stage: 'Screened', count: 85, avgDays: 3, isBottleneck: false },
  { stage: 'Submitted', count: 42, avgDays: 5, isBottleneck: false },
  { stage: 'Interviewed', count: 18, avgDays: 8, isBottleneck: true },
  { stage: 'Offered', count: 5, avgDays: 3, isBottleneck: false },
  { stage: 'Placed', count: 3, avgDays: 1, isBottleneck: false },
];

const mockTopCandidates: TopCandidate[] = [
  {
    id: '1',
    name: 'Jennifer Martinez',
    currentStage: 'Offered',
    score: 94,
    daysInStage: 2,
    skills: ['React', 'TypeScript', 'AWS'],
  },
  {
    id: '2',
    name: 'Alex Chen',
    currentStage: 'Interviewed',
    score: 89,
    daysInStage: 5,
    skills: ['Node.js', 'React', 'MongoDB'],
  },
  {
    id: '3',
    name: 'Sarah Williams',
    currentStage: 'Interviewed',
    score: 85,
    daysInStage: 3,
    skills: ['Vue.js', 'React', 'Python'],
  },
  {
    id: '4',
    name: 'Mike Johnson',
    currentStage: 'Submitted',
    score: 81,
    daysInStage: 4,
    skills: ['JavaScript', 'Node.js', 'AWS'],
  },
  {
    id: '5',
    name: 'Emma Davis',
    currentStage: 'Submitted',
    score: 78,
    daysInStage: 6,
    skills: ['React', 'Python', 'PostgreSQL'],
  },
];

const conversionRates: ConversionMetric[] = [
  { from: 'Sourced', to: 'Screened', percentage: 42, count: '85/200' },
  { from: 'Screened', to: 'Submitted', percentage: 49, count: '42/85' },
  { from: 'Submitted', to: 'Interviewed', percentage: 43, count: '18/42' },
  { from: 'Interviewed', to: 'Offered', percentage: 28, count: '5/18' },
  { from: 'Offered', to: 'Placed', percentage: 60, count: '3/5' },
];

const FunnelChart: React.FC<{ stages: PipelineStage[] }> = ({ stages }) => {
  const maxCount = Math.max(...stages.map((s) => s.count));

  return (
    <div className="space-y-4">
      {stages.map((stage, i) => {
        const width = (stage.count / maxCount) * 100;
        const conversionToNext = i < stages.length - 1 ? Math.round((stages[i + 1].count / stage.count) * 100) : 0;

        return (
          <div key={stage.stage}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-neutral-900 dark:text-white">{stage.stage}</span>
              <div className="text-sm text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold">{stage.count}</span>
                <span className="mx-2">•</span>
                <span>{stage.avgDays} days avg</span>
              </div>
            </div>
            <div className="relative">
              <div className="w-full h-10 bg-neutral-200 dark:bg-neutral-700 rounded overflow-hidden flex items-center" style={{ width: `${width}%` }}>
                <div
                  className={`h-full flex items-center justify-center font-semibold text-white text-sm transition-all duration-300 ${
                    stage.isBottleneck ? 'bg-red-500' : 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                  }`}
                  style={{ width: '100%' }}
                >
                  {stage.count}
                </div>
              </div>
              {i < stages.length - 1 && (
                <div className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
                  {conversionToNext}% conversion to {stages[i + 1].stage}
                </div>
              )}
            </div>
            {stage.isBottleneck && (
              <div className="mt-2 flex items-center gap-2 text-xs text-red-600 dark:text-red-400">
                <ExclamationTriangleIcon className="w-4 h-4" />
                <span>Bottleneck: {stage.avgDays} days in stage</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export const ApplicantTracker: React.FC = () => {
  const [expandedStage, setExpandedStage] = useState<string | null>('Interviewed');

  const totalApplicants = mockPipelineStages.reduce((sum, s) => sum + s.count, 0);
  const placed = mockPipelineStages.find((s) => s.stage === 'Placed')?.count || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Applicant Tracker</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Full pipeline analytics for Senior Frontend Engineer @ TechCorp</p>
      </div>

      {/* Job Header Card */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">Position</p>
            <p className="text-lg font-semibold text-neutral-900 dark:text-white mt-1">Senior Frontend Engineer</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">Client</p>
            <p className="text-lg font-semibold text-neutral-900 dark:text-white mt-1">TechCorp Industries</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">Days Open</p>
            <p className="text-lg font-semibold text-neutral-900 dark:text-white mt-1">42 days</p>
          </div>
          <div>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">Total Applicants</p>
            <p className="text-lg font-semibold text-neutral-900 dark:text-white mt-1">{totalApplicants}</p>
          </div>
        </div>
      </div>

      {/* Pipeline Funnel */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Pipeline Funnel</h3>
        <FunnelChart stages={mockPipelineStages} />
      </div>

      {/* Stage Details */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Stage Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockPipelineStages.map((stage) => (
            <div
              key={stage.stage}
              className={`p-4 rounded-lg border-2 ${
                stage.isBottleneck
                  ? 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10'
                  : 'border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-700/30'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-neutral-900 dark:text-white">{stage.stage}</h4>
                {stage.isBottleneck && <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />}
              </div>
              <div className="space-y-2">
                <p className="text-2xl font-bold text-neutral-900 dark:text-white">{stage.count}</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  {stage.avgDays} days avg in stage
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Candidates */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Top Candidates</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Current Stage
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Days in Stage
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Key Skills
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {mockTopCandidates.map((candidate) => (
                <tr key={candidate.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">{candidate.name}</td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        candidate.currentStage === 'Offered'
                          ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
                          : candidate.currentStage === 'Interviewed'
                            ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                            : 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
                      }`}
                    >
                      {candidate.currentStage}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-emerald-600 dark:text-emerald-400">{candidate.score}%</td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                    {candidate.daysInStage} days
                    {candidate.daysInStage > 5 && (
                      <span className="ml-2 text-orange-600 dark:text-orange-400">⚠️</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex flex-wrap gap-1">
                      {candidate.skills.map((skill) => (
                        <span key={skill} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Conversion Rate Metrics */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Conversion Rate Metrics</h3>
        <div className="space-y-4">
          {conversionRates.map((metric, i) => (
            <div key={i} className="p-4 rounded-lg border border-neutral-200 dark:border-neutral-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-neutral-900 dark:text-white">
                  {metric.from} → {metric.to}
                </span>
                <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">{metric.percentage}%</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden mr-3">
                  <div
                    className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
                    style={{ width: `${metric.percentage}%` }}
                  />
                </div>
                <span className="text-xs text-neutral-500 dark:text-neutral-400">{metric.count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottleneck Alert */}
      <div className="bg-red-50 dark:bg-red-900/10 rounded-xl p-6 border-l-4 border-l-red-500">
        <div className="flex items-start gap-4">
          <ExclamationTriangleIcon className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2">Pipeline Bottleneck Detected</h4>
            <p className="text-sm text-red-800 dark:text-red-200">
              The Interview stage has 18 candidates stuck for an average of 8 days. Consider scheduling more interviews or adding another interviewer to accelerate the process.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApplicantTracker;
