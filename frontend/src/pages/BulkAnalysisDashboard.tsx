import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import {
  SparklesIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  ArrowTrendingUpIcon,
  CalendarIcon,
  AdjustmentsHorizontalIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface AnalysisJob {
  id: string;
  type: 'batch_scoring' | 'skill_extraction' | 'placement_prediction';
  status: 'COMPLETED' | 'PROCESSING' | 'FAILED';
  candidatesScored: number;
  avgScore: number;
  topScore: number;
  date: string;
  createdAt: string;
}

interface AnalysisType {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}

const analysisTypes: AnalysisType[] = [
  {
    id: 'batch_scoring',
    icon: <ArrowTrendingUpIcon className="w-8 h-8" />,
    title: 'Batch Scoring',
    description: 'Score candidates in bulk against job requirements',
  },
  {
    id: 'skill_extraction',
    icon: <AdjustmentsHorizontalIcon className="w-8 h-8" />,
    title: 'Skill Extraction',
    description: 'Automatically extract and categorize skills from resumes',
  },
  {
    id: 'placement_prediction',
    icon: <SparklesIcon className="w-8 h-8" />,
    title: 'Placement Prediction',
    description: 'Predict placement success probability using AI',
  },
];

const skills = [
  'React', 'Python', 'Java', 'JavaScript', 'TypeScript',
  'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
  'SQL', 'MongoDB', 'Node.js', 'Go', 'Rust',
];

const mockAnalysisJobs: AnalysisJob[] = [
  {
    id: 'AI-20260307-001',
    type: 'batch_scoring',
    status: 'COMPLETED',
    candidatesScored: 156,
    avgScore: 74.2,
    topScore: 98,
    date: '2026-03-07',
    createdAt: new Date(Date.now() - 4 * 3600000).toISOString(),
  },
  {
    id: 'AI-20260307-002',
    type: 'skill_extraction',
    status: 'COMPLETED',
    candidatesScored: 89,
    avgScore: 81.5,
    topScore: 95,
    date: '2026-03-07',
    createdAt: new Date(Date.now() - 6 * 3600000).toISOString(),
  },
  {
    id: 'AI-20260308-001',
    type: 'placement_prediction',
    status: 'PROCESSING',
    candidatesScored: 45,
    avgScore: 72.8,
    topScore: 91,
    date: '2026-03-08',
    createdAt: new Date(Date.now() - 15 * 60000).toISOString(),
  },
];

const mockInsights = [
  {
    id: 1,
    icon: '⚠️',
    title: 'Skill Shortage Alert',
    description: 'React developers in high demand with only 12 available vs 28 open positions',
    timestamp: '2 hours ago',
  },
  {
    id: 2,
    icon: '📈',
    title: 'Top Emerging Skill',
    description: 'TypeScript adoption is up 34% among new candidates this month',
    timestamp: '4 hours ago',
  },
  {
    id: 3,
    icon: '🎯',
    title: 'Best Match Found',
    description: 'High-probability placement match identified for Senior Python role (96% fit)',
    timestamp: '6 hours ago',
  },
  {
    id: 4,
    icon: '📊',
    title: 'Trend Analysis',
    description: 'Cloud platforms (AWS, GCP) show 45% higher placement success rate',
    timestamp: '8 hours ago',
  },
  {
    id: 5,
    icon: '⭐',
    title: 'Quality Improvement',
    description: 'Average candidate quality score improved to 74.2 (up from 71.5 last month)',
    timestamp: '10 hours ago',
  },
];

export const BulkAnalysisDashboard: React.FC = () => {
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<string | null>(null);
  const [showConfigForm, setShowConfigForm] = useState(false);

  const getJobStatusIcon = (status: AnalysisJob['status']) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircleIcon className="w-4 h-4 text-success-500" />;
      case 'PROCESSING':
        return <ArrowPathIcon className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'FAILED':
        return <div className="w-4 h-4 bg-danger-500 rounded-full" />;
    }
  };

  return (
    <AppLayout title="Bulk Analysis Dashboard">
      <div className="p-4 md:p-6 space-y-6 pb-8">
        {/* Section A: Run New Analysis */}
        <div>
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
            Run New Analysis
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analysisTypes.map((type) => (
              <Card
                key={type.id}
                hoverable
                onClick={() => {
                  setSelectedAnalysisType(type.id);
                  setShowConfigForm(true);
                }}
                className="cursor-pointer"
              >
                <CardBody className="flex flex-col items-center text-center py-8">
                  <div className="text-primary-500 mb-4">{type.icon}</div>
                  <h3 className="font-semibold text-neutral-900 dark:text-white mb-2">
                    {type.title}
                  </h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
                    {type.description}
                  </p>
                  <button className="px-4 py-2 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-lg hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors text-sm font-medium">
                    Run Analysis
                  </button>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Config Form */}
          {showConfigForm && selectedAnalysisType && (
            <Card className="mt-6 bg-neutral-50 dark:bg-neutral-900">
              <CardHeader className="flex items-center justify-between">
                <span>Configure Analysis</span>
                <button
                  onClick={() => setShowConfigForm(false)}
                  className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
                >
                  ✕
                </button>
              </CardHeader>
              <CardBody className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-900 dark:text-white mb-2">
                    Requirement ID (optional)
                  </label>
                  <input
                    type="text"
                    placeholder="REQ-2026-001"
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-900 dark:text-white mb-2">
                    Candidate IDs (comma-separated)
                  </label>
                  <textarea
                    placeholder="CAN-001, CAN-002, CAN-003"
                    rows={3}
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400"
                  />
                </div>
                <div className="flex gap-3 pt-4">
                  <button className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors">
                    Cancel
                  </button>
                  <button className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium">
                    Submit Analysis
                  </button>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Success Message */}
          {showConfigForm && (
            <div className="mt-4 bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-lg p-4">
              <p className="text-sm text-success-800 dark:text-success-200">
                <span className="font-semibold">Analysis job queued</span> — Job #AI-20260308-001 created
              </p>
            </div>
          )}
        </div>

        {/* Section B: Analysis Results Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Skill Demand Heatmap */}
          <Card>
            <CardHeader>Skill Demand Heatmap</CardHeader>
            <CardBody>
              <div className="grid grid-cols-3 gap-3">
                {skills.map((skill, index) => {
                  const demandLevel = (index % 5) / 4;
                  const bgColor = `hsla(206, 100%, 50%, ${demandLevel * 0.8 + 0.2})`;
                  return (
                    <div
                      key={skill}
                      className="p-3 rounded-lg text-center text-sm font-medium text-white"
                      style={{ backgroundColor: bgColor }}
                    >
                      {skill}
                    </div>
                  );
                })}
              </div>
              <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-4 text-center">
                Color intensity shows demand level (darker = higher demand)
              </p>
            </CardBody>
          </Card>

          {/* Platform Stats */}
          <div className="space-y-4">
            <Card>
              <CardBody>
                <div className="flex items-start gap-3">
                  <div className="text-primary-500">
                    <ArrowTrendingUpIcon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                      Total Candidates Scored
                    </p>
                    <p className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                      1,240
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <div className="flex items-start gap-3">
                  <div className="text-success-500">
                    <CheckCircleIcon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                      Avg Platform Score
                    </p>
                    <p className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                      74.2%
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <div className="flex items-start gap-3">
                  <div className="text-blue-500">
                    <SparklesIcon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                      Placement Success Rate
                    </p>
                    <p className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                      68%
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <div className="flex items-start gap-3">
                  <div className="text-warning-500">
                    <CalendarIcon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 uppercase tracking-wider font-semibold">
                      Avg Time to Fill
                    </p>
                    <p className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                      18.5 days
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        </div>

        {/* AI Insights Feed */}
        <Card>
          <CardHeader>AI Insights Feed</CardHeader>
          <CardBody>
            <div className="space-y-4">
              {mockInsights.map((insight) => (
                <div
                  key={insight.id}
                  className="flex gap-4 pb-4 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0 last:pb-0"
                >
                  <div className="text-2xl flex-shrink-0">{insight.icon}</div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-neutral-900 dark:text-white">
                      {insight.title}
                    </h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                      {insight.description}
                    </p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-2">
                      {insight.timestamp}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Recent Batch Scores */}
        <Card>
          <CardHeader>Recent Batch Scores</CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Job ID
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Type
                    </th>
                    <th className="text-center py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Status
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Candidates
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Avg Score
                    </th>
                    <th className="text-right py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Top Score
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700 dark:text-neutral-300">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {mockAnalysisJobs.map((job) => (
                    <tr
                      key={job.id}
                      className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                    >
                      <td className="py-3 px-4 font-mono text-xs text-primary-600 dark:text-primary-400">
                        {job.id}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2.5 py-0.5 bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 rounded text-xs font-medium">
                          {job.type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          {getJobStatusIcon(job.status)}
                          <StatusBadge status={job.status} />
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right font-medium text-neutral-900 dark:text-white">
                        {job.candidatesScored}
                      </td>
                      <td className="py-3 px-4 text-right font-medium text-neutral-900 dark:text-white">
                        {job.avgScore.toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 text-right font-medium text-success-600 dark:text-success-400">
                        {job.topScore}%
                      </td>
                      <td className="py-3 px-4 text-neutral-600 dark:text-neutral-400">
                        {job.date}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      </div>
    </AppLayout>
  );
};

BulkAnalysisDashboard.displayName = 'BulkAnalysisDashboard';

export default BulkAnalysisDashboard;
