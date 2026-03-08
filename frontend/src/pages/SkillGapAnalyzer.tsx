import React, { useState } from 'react';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, MinusIcon, BoltIcon, StarIcon } from '@heroicons/react/24/outline';

interface Skill {
  name: string;
  proficiency: 'Expert' | 'Proficient' | 'Intermediate' | 'Beginner' | 'Missing';
  demand: 'HIGH' | 'MEDIUM' | 'LOW';
  trendDirection: 'up' | 'stable' | 'down';
}

interface DevelopmentRecommendation {
  priority: 1 | 2 | 3;
  skill: string;
  currentLevel: string;
  targetLevel: string;
  action: string;
  estimatedTime: string;
}

const mockSkillsData: Skill[] = [
  { name: 'React', proficiency: 'Expert', demand: 'HIGH', trendDirection: 'up' },
  { name: 'TypeScript', proficiency: 'Proficient', demand: 'HIGH', trendDirection: 'up' },
  { name: 'Node.js', proficiency: 'Proficient', demand: 'HIGH', trendDirection: 'stable' },
  { name: 'AWS', proficiency: 'Proficient', demand: 'HIGH', trendDirection: 'up' },
  { name: 'Python', proficiency: 'Intermediate', demand: 'MEDIUM', trendDirection: 'up' },
  { name: 'Docker', proficiency: 'Intermediate', demand: 'HIGH', trendDirection: 'up' },
  { name: 'Kubernetes', proficiency: 'Beginner', demand: 'HIGH', trendDirection: 'up' },
  { name: 'GraphQL', proficiency: 'Intermediate', demand: 'MEDIUM', trendDirection: 'up' },
  { name: 'MongoDB', proficiency: 'Proficient', demand: 'MEDIUM', trendDirection: 'stable' },
  { name: 'PostgreSQL', proficiency: 'Proficient', demand: 'MEDIUM', trendDirection: 'stable' },
  { name: 'Machine Learning', proficiency: 'Missing', demand: 'MEDIUM', trendDirection: 'up' },
  { name: 'Rust', proficiency: 'Missing', demand: 'MEDIUM', trendDirection: 'up' },
  { name: 'Microservices', proficiency: 'Proficient', demand: 'HIGH', trendDirection: 'up' },
  { name: 'System Design', proficiency: 'Intermediate', demand: 'HIGH', trendDirection: 'up' },
  { name: 'Git', proficiency: 'Expert', demand: 'LOW', trendDirection: 'stable' },
];

const mockDevelopmentRecommendations: DevelopmentRecommendation[] = [
  {
    priority: 1,
    skill: 'Kubernetes',
    currentLevel: 'Beginner',
    targetLevel: 'Proficient',
    action: 'Complete Kubernetes certification course, deploy 3+ projects',
    estimatedTime: '6-8 weeks',
  },
  {
    priority: 1,
    skill: 'Machine Learning',
    currentLevel: 'Missing',
    targetLevel: 'Intermediate',
    action: 'Take ML fundamentals course, build 2 ML projects',
    estimatedTime: '8-10 weeks',
  },
  {
    priority: 2,
    skill: 'System Design',
    currentLevel: 'Intermediate',
    targetLevel: 'Proficient',
    action: 'Practice system design interviews, design 5+ large-scale systems',
    estimatedTime: '4-6 weeks',
  },
  {
    priority: 2,
    skill: 'Rust',
    currentLevel: 'Missing',
    targetLevel: 'Beginner',
    action: 'Complete Rust fundamentals, build one CLI tool',
    estimatedTime: '4-5 weeks',
  },
  {
    priority: 3,
    skill: 'Python',
    currentLevel: 'Intermediate',
    targetLevel: 'Proficient',
    action: 'Build backend service using Python/Django',
    estimatedTime: '3-4 weeks',
  },
  {
    priority: 3,
    skill: 'GraphQL',
    currentLevel: 'Intermediate',
    targetLevel: 'Proficient',
    action: 'Build production GraphQL API, optimize queries',
    estimatedTime: '2-3 weeks',
  },
];

const getProficiencyColor = (level: string): string => {
  switch (level) {
    case 'Expert':
      return 'bg-emerald-700 dark:bg-emerald-600';
    case 'Proficient':
      return 'bg-emerald-500 dark:bg-emerald-500';
    case 'Intermediate':
      return 'bg-amber-500 dark:bg-amber-500';
    case 'Beginner':
      return 'bg-orange-500 dark:bg-orange-500';
    case 'Missing':
      return 'bg-red-500 dark:bg-red-500';
    default:
      return 'bg-gray-500';
  }
};

const getDemandBadgeColor = (demand: string): string => {
  switch (demand) {
    case 'HIGH':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'MEDIUM':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'LOW':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

const TrendIcon: React.FC<{ direction: string }> = ({ direction }) => {
  if (direction === 'up') {
    return <ArrowTrendingUpIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />;
  }
  if (direction === 'down') {
    return <ArrowTrendingDownIcon className="w-4 h-4 text-red-600 dark:text-red-400" />;
  }
  return <MinusIcon className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />;
};

const SkillHeatmap: React.FC<{ skills: Skill[] }> = ({ skills }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
      {skills.map((skill) => (
        <div key={skill.name} className="relative">
          <div className={`${getProficiencyColor(skill.proficiency)} rounded-lg p-4 text-white aspect-square flex flex-col items-center justify-center text-center`}>
            <div className="text-sm font-semibold">{skill.name}</div>
            <div className="text-xs opacity-90 mt-1">{skill.proficiency}</div>
          </div>
          <div className="flex items-center justify-center gap-1 mt-2">
            <span className={`text-xs px-2 py-1 rounded ${getDemandBadgeColor(skill.demand)}`}>{skill.demand}</span>
            <TrendIcon direction={skill.trendDirection} />
          </div>
        </div>
      ))}
    </div>
  );
};

const VennDiagram: React.FC = () => {
  const hasSkills = ['React', 'TypeScript', 'Node.js', 'Docker', 'AWS'];
  const demandSkills = ['React', 'TypeScript', 'Node.js', 'AWS', 'Kubernetes', 'Machine Learning', 'System Design'];

  return (
    <div className="flex flex-col lg:flex-row items-center justify-center gap-8">
      <div className="flex-1">
        <h4 className="font-semibold text-neutral-900 dark:text-white mb-4">Skills You Have</h4>
        <div className="space-y-2">
          {hasSkills.map((skill) => (
            <div key={skill} className="px-4 py-2 bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded-lg text-sm">
              ✓ {skill}
            </div>
          ))}
        </div>
      </div>

      <div className="hidden lg:flex items-center justify-center">
        <div className="relative w-32 h-32">
          <div className="absolute inset-0 flex items-center justify-center text-neutral-600 dark:text-neutral-400 text-sm font-semibold">Overlap: React, TypeScript, Node.js, AWS</div>
        </div>
      </div>

      <div className="flex-1">
        <h4 className="font-semibold text-neutral-900 dark:text-white mb-4">In-Demand Skills</h4>
        <div className="space-y-2">
          {demandSkills.map((skill) => (
            <div key={skill} className={hasSkills.includes(skill) ? 'px-4 py-2 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-lg text-sm' : 'px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg text-sm'}>
              {hasSkills.includes(skill) ? '✓' : '✕'} {skill}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const SkillGapAnalyzer: React.FC = () => {
  const [selectedPriority, setSelectedPriority] = useState<1 | 2 | 3 | 'all'>('all');

  const filteredRecommendations =
    selectedPriority === 'all' ? mockDevelopmentRecommendations : mockDevelopmentRecommendations.filter((r) => r.priority === selectedPriority);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Skill Gap Analyzer</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Professional skill assessment and development roadmap</p>
      </div>

      {/* Skill Strength Heatmap */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Skill Strength Heatmap</h3>
        <SkillHeatmap skills={mockSkillsData} />
        <div className="mt-6 pt-6 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-emerald-700"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Expert</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-emerald-500"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Proficient</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-amber-500"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Intermediate</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-orange-500"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Beginner</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-500"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Missing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Skill Gap Analysis - Venn Diagram Concept */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Skills Analysis</h3>
        <VennDiagram />
      </div>

      {/* Development Recommendations */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Development Recommendations</h3>

        {/* Priority Filter */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {['all', 1, 2, 3].map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPriority(p as any)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                selectedPriority === p
                  ? 'bg-primary-500 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600'
              }`}
            >
              {p === 'all' ? 'All Priorities' : `Priority ${p}`}
            </button>
          ))}
        </div>

        {/* Recommendations List */}
        <div className="space-y-4">
          {filteredRecommendations.map((rec, i) => {
            const priorityColor =
              rec.priority === 1
                ? 'border-l-4 border-l-red-500 bg-red-50 dark:bg-red-900/10'
                : rec.priority === 2
                  ? 'border-l-4 border-l-amber-500 bg-amber-50 dark:bg-amber-900/10'
                  : 'border-l-4 border-l-blue-500 bg-blue-50 dark:bg-blue-900/10';

            return (
              <div key={i} className={`p-4 rounded-lg ${priorityColor} border border-neutral-200 dark:border-neutral-700`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold text-neutral-900 dark:text-white">{rec.skill}</h4>
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          rec.priority === 1
                            ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                            : rec.priority === 2
                              ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
                              : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                        }`}
                      >
                        Priority {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">
                      {rec.currentLevel} → {rec.targetLevel}
                    </p>
                    <p className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">{rec.action}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Estimated time: {rec.estimatedTime}</p>
                  </div>
                  {rec.priority === 1 && <BoltIcon className="w-5 h-5 text-red-500 mt-1 flex-shrink-0" />}
                  {rec.priority === 2 && <StarIcon className="w-5 h-5 text-amber-500 mt-1 flex-shrink-0" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Skill Demand Trends */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Market Trends</h3>
        <div className="space-y-3">
          {mockSkillsData
            .filter((s) => s.demand === 'HIGH')
            .slice(0, 8)
            .map((skill) => (
              <div key={skill.name} className="flex items-center justify-between p-3 rounded-lg border border-neutral-200 dark:border-neutral-700">
                <span className="text-sm font-medium text-neutral-900 dark:text-white">{skill.name}</span>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 rounded text-xs font-semibold bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400">HIGH DEMAND</span>
                  <TrendIcon direction={skill.trendDirection} />
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default SkillGapAnalyzer;
