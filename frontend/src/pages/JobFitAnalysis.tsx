import React, { useState } from 'react';
import { CheckCircleIcon, UserGroupIcon, BriefcaseIcon } from '@heroicons/react/24/outline';

interface CandidateCard {
  id: string;
  name: string;
  title: string;
  score: number;
  skills: string[];
  radarValues: number[];
}

interface JobCard {
  id: string;
  title: string;
  company: string;
  score: number;
  whyGoodFit: string;
}

const mockCandidatesForJob: CandidateCard[] = [
  {
    id: '1',
    name: 'Jennifer Martinez',
    title: 'Senior Frontend Engineer',
    score: 94,
    skills: ['React', 'TypeScript', 'AWS'],
    radarValues: [92, 85, 78, 90, 82, 88, 81],
  },
  {
    id: '2',
    name: 'Alex Chen',
    title: 'Full Stack Developer',
    score: 89,
    skills: ['Node.js', 'React', 'MongoDB'],
    radarValues: [88, 82, 75, 85, 79, 90, 78],
  },
  {
    id: '3',
    name: 'Sarah Williams',
    title: 'Frontend Specialist',
    score: 85,
    skills: ['Vue.js', 'React', 'CSS'],
    radarValues: [85, 78, 72, 82, 76, 85, 80],
  },
  {
    id: '4',
    name: 'Mike Johnson',
    title: 'JavaScript Developer',
    score: 81,
    skills: ['React', 'Node.js', 'Express'],
    radarValues: [82, 75, 70, 80, 72, 88, 75],
  },
  {
    id: '5',
    name: 'Emma Davis',
    title: 'Web Developer',
    score: 78,
    skills: ['JavaScript', 'React', 'PostgreSQL'],
    radarValues: [78, 72, 68, 75, 70, 82, 74],
  },
  {
    id: '6',
    name: 'David Wilson',
    title: 'React Developer',
    score: 76,
    skills: ['React', 'TypeScript', 'Node.js'],
    radarValues: [76, 70, 65, 73, 68, 80, 72],
  },
  {
    id: '7',
    name: 'Lisa Anderson',
    title: 'Full Stack Engineer',
    score: 73,
    skills: ['Node.js', 'React', 'AWS'],
    radarValues: [74, 68, 62, 70, 65, 78, 70],
  },
  {
    id: '8',
    name: 'Chris Brown',
    title: 'Junior Developer',
    score: 69,
    skills: ['JavaScript', 'React', 'CSS'],
    radarValues: [70, 65, 58, 68, 62, 75, 68],
  },
  {
    id: '9',
    name: 'Rachel Green',
    title: 'Frontend Developer',
    score: 67,
    skills: ['React', 'CSS', 'JavaScript'],
    radarValues: [68, 63, 55, 66, 60, 72, 66],
  },
  {
    id: '10',
    name: 'Tom Miller',
    title: 'Developer',
    score: 64,
    skills: ['JavaScript', 'HTML', 'CSS'],
    radarValues: [65, 60, 52, 63, 58, 70, 64],
  },
];

const mockJobsForCandidate: JobCard[] = [
  {
    id: '1',
    title: 'Senior Frontend Engineer',
    company: 'TechCorp',
    score: 94,
    whyGoodFit: 'Exceptional React skills, 10+ years experience, perfect location match',
  },
  {
    id: '2',
    title: 'Tech Lead - Web Platform',
    company: 'InnovateLabs',
    score: 89,
    whyGoodFit: 'Leadership experience, strong TypeScript background, team alignment',
  },
  {
    id: '3',
    title: 'Full Stack Engineer',
    company: 'CloudSystems',
    score: 85,
    whyGoodFit: 'AWS expertise, full stack capabilities, culture fit strong',
  },
  {
    id: '4',
    title: 'Senior JavaScript Engineer',
    company: 'DataFlow',
    score: 82,
    whyGoodFit: 'Strong JavaScript foundation, modern tooling knowledge, immediate availability',
  },
  {
    id: '5',
    title: 'Principal Engineer',
    company: 'FutureAI',
    score: 78,
    whyGoodFit: 'AI/ML interest area, system design skills, mentoring capability',
  },
];

const ScoreDistributionChart: React.FC<{ data: CandidateCard[] }> = ({ data }) => {
  const buckets = {
    '90-100': 0,
    '80-89': 0,
    '70-79': 0,
    '60-69': 0,
    '0-59': 0,
  };

  data.forEach((c) => {
    if (c.score >= 90) buckets['90-100']++;
    else if (c.score >= 80) buckets['80-89']++;
    else if (c.score >= 70) buckets['70-79']++;
    else if (c.score >= 60) buckets['60-69']++;
    else buckets['0-59']++;
  });

  const maxCount = Math.max(...Object.values(buckets));

  return (
    <div className="space-y-3">
      {Object.entries(buckets).map(([range, count]) => (
        <div key={range}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">{range}</span>
            <span className="text-sm font-semibold text-neutral-900 dark:text-white">{count}</span>
          </div>
          <div className="w-full h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600"
              style={{ width: `${(count / maxCount) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

const SimplifiedRadar: React.FC<{ values: number[] }> = ({ values }) => {
  const size = 80;
  const center = size / 2;
  const maxRadius = 30;
  const angles = Array.from({ length: values.length }, (_, i) => (i * 2 * Math.PI) / values.length - Math.PI / 2);

  const points = values.map((score, i) => {
    const radius = (score / 100) * maxRadius;
    return {
      x: center + radius * Math.cos(angles[i]),
      y: center + radius * Math.sin(angles[i]),
    };
  });

  const polygonPoints = points.map((p) => `${p.x},${p.y}`).join(' ');

  return (
    <svg width={size} height={size} className="mx-auto">
      <circle cx={center} cy={center} r={maxRadius} fill="none" stroke="currentColor" strokeWidth="1" className="text-neutral-300 dark:text-neutral-600" />
      {angles.map((angle, i) => (
        <line key={`axis-${i}`} x1={center} y1={center} x2={center + maxRadius * Math.cos(angle)} y2={center + maxRadius * Math.sin(angle)} stroke="currentColor" strokeWidth="1" className="text-neutral-300 dark:text-neutral-600" />
      ))}
      <polygon points={polygonPoints} fill="rgba(34, 197, 94, 0.2)" stroke="rgb(34, 197, 94)" strokeWidth="1.5" />
    </svg>
  );
};

export const JobFitAnalysis: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'candidates' | 'jobs'>('candidates');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Job Fit Analysis</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Bidirectional matching analysis</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-neutral-200 dark:border-neutral-700">
        <button
          onClick={() => setActiveTab('candidates')}
          className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
            activeTab === 'candidates'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-neutral-600 dark:text-neutral-400'
          }`}
        >
          <div className="flex items-center gap-2">
            <UserGroupIcon className="w-5 h-5" />
            Candidates for Job
          </div>
        </button>
        <button
          onClick={() => setActiveTab('jobs')}
          className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
            activeTab === 'jobs'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-neutral-600 dark:text-neutral-400'
          }`}
        >
          <div className="flex items-center gap-2">
            <BriefcaseIcon className="w-5 h-5" />
            Jobs for Candidate
          </div>
        </button>
      </div>

      {activeTab === 'candidates' && (
        <>
          {/* AI Recommendation Banner */}
          <div className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-xl p-4 border border-emerald-200 dark:border-emerald-800 flex items-start gap-3">
            <CheckCircleIcon className="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-emerald-900 dark:text-emerald-100">AI Recommendation</p>
              <p className="text-sm text-emerald-800 dark:text-emerald-200 mt-1">
                Based on job requirements, Jennifer Martinez (94%) and Alex Chen (89%) are your top candidates. Consider scheduling interviews this week.
              </p>
            </div>
          </div>

          {/* Job Summary */}
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Job Overview</h3>
            <div className="space-y-2">
              <p className="text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold text-neutral-900 dark:text-white">Position:</span> Senior Frontend Engineer
              </p>
              <p className="text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold text-neutral-900 dark:text-white">Client:</span> TechCorp Industries
              </p>
              <p className="text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold text-neutral-900 dark:text-white">Requirements:</span> React, TypeScript, Node.js, AWS, 5+ years experience
              </p>
            </div>
          </div>

          {/* Score Distribution */}
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Candidate Score Distribution</h3>
            <ScoreDistributionChart data={mockCandidatesForJob} />
          </div>

          {/* Top Candidates */}
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Top 10 Candidates</h3>
            <div className="space-y-4">
              {mockCandidatesForJob.map((candidate) => (
                <div key={candidate.id} className="flex items-center gap-4 p-4 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <SimplifiedRadar values={candidate.radarValues} />
                  <div className="flex-1">
                    <p className="font-semibold text-neutral-900 dark:text-white">{candidate.name}</p>
                    <p className="text-sm text-neutral-500 dark:text-neutral-400">{candidate.title}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {candidate.skills.map((skill) => (
                        <span key={skill} className="px-2 py-1 rounded text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{candidate.score}%</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Match Score</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {activeTab === 'jobs' && (
        <>
          {/* Candidate Summary */}
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Candidate Overview</h3>
            <div className="space-y-2">
              <p className="text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold text-neutral-900 dark:text-white">Name:</span> Jennifer Martinez
              </p>
              <p className="text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold text-neutral-900 dark:text-white">Title:</span> Senior Software Engineer
              </p>
              <p className="text-neutral-600 dark:text-neutral-400">
                <span className="font-semibold text-neutral-900 dark:text-white">Skills:</span> React, TypeScript, Node.js, AWS, Python
              </p>
            </div>
          </div>

          {/* Jobs for Candidate */}
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Top 5 Matching Jobs</h3>
            <div className="space-y-4">
              {mockJobsForCandidate.map((job) => (
                <div key={job.id} className="p-4 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-semibold text-neutral-900 dark:text-white">{job.title}</p>
                      <p className="text-sm text-neutral-500 dark:text-neutral-400">{job.company}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{job.score}%</p>
                      <p className="text-xs text-neutral-500 dark:text-neutral-400">Match Score</p>
                    </div>
                  </div>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    <span className="font-semibold text-neutral-900 dark:text-white">Why it's a good fit:</span> {job.whyGoodFit}
                  </p>
                  <div className="mt-3 flex items-center gap-2">
                    <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: `${job.score}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default JobFitAnalysis;
