import React, { useState, useEffect } from 'react';
import { StarIcon, ArrowTrendingUpIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import client from '@/api/client';

interface ScoreDimension {
  name: string;
  score: number;
  color: string;
}

interface Skill {
  name: string;
  proficiency: number;
  market_demand: 'HIGH' | 'MEDIUM' | 'LOW';
}

interface RecommendedJob {
  id: string;
  title: string;
  company: string;
  matchScore: number;
}

const mockCandidateData = {
  candidateId: 1,
  name: 'Jennifer Martinez',
  overallScore: 87,
  matchStrength: 'Strong Match' as const,
  dimensions: [
    { name: 'Skills', score: 92, color: 'emerald' },
    { name: 'Experience', score: 85, color: 'emerald' },
    { name: 'Education', score: 78, color: 'amber' },
    { name: 'Location', score: 90, color: 'emerald' },
    { name: 'Rate', score: 82, color: 'emerald' },
    { name: 'Availability', score: 88, color: 'emerald' },
    { name: 'Culture Fit', score: 81, color: 'amber' },
  ] as ScoreDimension[],
  strongSkills: [
    { name: 'React', proficiency: 95 },
    { name: 'TypeScript', proficiency: 90 },
    { name: 'Node.js', proficiency: 88 },
    { name: 'AWS', proficiency: 85 },
  ],
  skillGaps: [
    { name: 'Kubernetes', importance: 'High' },
    { name: 'Machine Learning', importance: 'Medium' },
  ],
  standoutQualities: [
    '10+ years software development experience',
    'Led teams of 8+ engineers',
    'Expert in modern JavaScript ecosystem',
    'Strong communication skills',
    'Proven track record at FAANG companies',
  ],
  recommendedJobs: [
    { id: '1', title: 'Senior Frontend Engineer', company: 'TechCorp', matchScore: 94 },
    { id: '2', title: 'Tech Lead - Web Platform', company: 'InnovateLabs', matchScore: 89 },
    { id: '3', title: 'Full Stack Engineer', company: 'CloudSystems', matchScore: 85 },
    { id: '4', title: 'Senior JavaScript Engineer', company: 'DataFlow', matchScore: 82 },
    { id: '5', title: 'Principal Engineer', company: 'FutureAI', matchScore: 78 },
  ],
};

const getScoreColor = (score: number): string => {
  if (score >= 80) return 'emerald';
  if (score >= 50) return 'amber';
  return 'red';
};

const getScoreBgClass = (score: number): string => {
  if (score >= 80) return 'bg-emerald-100 dark:bg-emerald-900/20';
  if (score >= 50) return 'bg-amber-100 dark:bg-amber-900/20';
  return 'bg-red-100 dark:bg-red-900/20';
};

const getScoreTextClass = (score: number): string => {
  if (score >= 80) return 'text-emerald-700 dark:text-emerald-400';
  if (score >= 50) return 'text-amber-700 dark:text-amber-400';
  return 'text-red-700 dark:text-red-400';
};

const ProgressBar: React.FC<{ score: number; color: string }> = ({ score, color }) => {
  const bgColor = color === 'emerald' ? 'bg-emerald-500' : color === 'amber' ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
      <div
        className={`h-full ${bgColor} transition-all duration-300`}
        style={{ width: `${score}%` }}
      />
    </div>
  );
};

const RadarChart: React.FC<{ dimensions: ScoreDimension[] }> = ({ dimensions }) => {
  const size = 300;
  const center = size / 2;
  const maxRadius = 100;
  const levels = 5;

  // Calculate points for radar
  const angles = dimensions.map((_, i) => (i * 2 * Math.PI) / dimensions.length - Math.PI / 2);
  const points = dimensions.map((dim, i) => {
    const angle = angles[i];
    const radius = (dim.score / 100) * maxRadius;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
      angle,
      dim,
    };
  });

  // Generate grid lines
  const gridPoints = Array.from({ length: levels }, (_, level) => {
    const levelRadius = ((level + 1) / levels) * maxRadius;
    return angles.map((angle) => ({
      x: center + levelRadius * Math.cos(angle),
      y: center + levelRadius * Math.sin(angle),
    }));
  });

  const polygonPoints = points.map((p) => `${p.x},${p.y}`).join(' ');

  return (
    <svg width={size} height={size} className="mx-auto">
      {/* Grid circles */}
      {Array.from({ length: levels }).map((_, i) => (
        <circle
          key={`grid-${i}`}
          cx={center}
          cy={center}
          r={((i + 1) / levels) * maxRadius}
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          className="text-neutral-300 dark:text-neutral-600"
        />
      ))}

      {/* Axis lines */}
      {angles.map((angle, i) => (
        <line
          key={`axis-${i}`}
          x1={center}
          y1={center}
          x2={center + maxRadius * Math.cos(angle)}
          y2={center + maxRadius * Math.sin(angle)}
          stroke="currentColor"
          strokeWidth="1"
          className="text-neutral-300 dark:text-neutral-600"
        />
      ))}

      {/* Data polygon */}
      <polygon
        points={polygonPoints}
        fill="rgba(34, 197, 94, 0.15)"
        stroke="rgb(34, 197, 94)"
        strokeWidth="2"
      />

      {/* Data points */}
      {points.map((p, i) => (
        <g key={`point-${i}`}>
          <circle cx={p.x} cy={p.y} r="4" fill="rgb(34, 197, 94)" />
        </g>
      ))}

      {/* Labels */}
      {points.map((p, i) => {
        const labelRadius = maxRadius + 35;
        const labelX = center + labelRadius * Math.cos(p.angle);
        const labelY = center + labelRadius * Math.sin(p.angle);
        return (
          <text
            key={`label-${i}`}
            x={labelX}
            y={labelY}
            textAnchor="middle"
            dominantBaseline="middle"
            className="text-xs font-semibold fill-neutral-700 dark:fill-neutral-300"
          >
            {p.dim.name}
          </text>
        );
      })}
    </svg>
  );
};

export const CandidateScoreCard: React.FC = () => {
  const [data, setData] = useState(mockCandidateData);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Mock API call with fallback to mock data
    const fetchData = async () => {
      try {
        setLoading(true);
        // const response = await client.get(`/analytics/candidate/1/scorecard`);
        // setData(response.data);
      } catch (err) {
        console.error('Failed to fetch scorecard, using mock data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const matchColor =
    data.matchStrength === 'Strong Match'
      ? 'emerald'
      : data.matchStrength === 'Good Match'
        ? 'blue'
        : 'amber';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Candidate Analysis</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Comprehensive AI-powered scoring and insights</p>
      </div>

      {/* Top Section: Name, Score, Badge */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="flex items-start justify-between gap-6">
          <div className="flex-1">
            <h2 className="text-3xl font-bold text-neutral-900 dark:text-white">{data.name}</h2>
            <p className="text-neutral-500 dark:text-neutral-400 mt-1">Senior Software Engineer</p>
          </div>
          <div className="text-right">
            <div className={`text-6xl font-bold mb-2 ${getScoreTextClass(data.overallScore)}`}>
              {data.overallScore}
            </div>
            <div
              className={`inline-block px-4 py-2 rounded-lg font-semibold text-sm ${
                matchColor === 'emerald'
                  ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
                  : matchColor === 'blue'
                    ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                    : 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
              }`}
            >
              {data.matchStrength}
            </div>
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Score Breakdown Radar</h3>
        <RadarChart dimensions={data.dimensions} />
      </div>

      {/* Score Breakdown Grid */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Dimension Scores</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
          {data.dimensions.map((dim) => (
            <div
              key={dim.name}
              className={`p-4 rounded-lg border border-neutral-200 dark:border-neutral-700 ${getScoreBgClass(dim.score)}`}
            >
              <p className="text-sm font-semibold text-neutral-900 dark:text-white mb-2">{dim.name}</p>
              <p className={`text-2xl font-bold mb-3 ${getScoreTextClass(dim.score)}`}>{dim.score}</p>
              <ProgressBar score={dim.score} color={dim.color} />
            </div>
          ))}
        </div>
      </div>

      {/* Strong Skills */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center gap-2 mb-6">
          <CheckCircleIcon className="w-5 h-5 text-emerald-500" />
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Strong Skills</h3>
        </div>
        <div className="space-y-3">
          {data.strongSkills.map((skill) => (
            <div key={skill.name}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-neutral-900 dark:text-white">{skill.name}</span>
                <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{skill.proficiency}%</span>
              </div>
              <div className="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 transition-all duration-300"
                  style={{ width: `${skill.proficiency}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Skill Gaps */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center gap-2 mb-6">
          <ExclamationTriangleIcon className="w-5 h-5 text-amber-500" />
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Skill Gaps & Development Areas</h3>
        </div>
        <div className="flex flex-wrap gap-3">
          {data.skillGaps.map((gap) => (
            <span
              key={gap.name}
              className={`px-3 py-2 rounded-lg text-sm font-medium ${
                gap.importance === 'High'
                  ? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                  : 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
              }`}
            >
              {gap.name} ({gap.importance})
            </span>
          ))}
        </div>
      </div>

      {/* Standout Qualities */}
      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/10 dark:to-yellow-900/10 rounded-xl p-8 border border-amber-200 dark:border-amber-800">
        <div className="flex items-center gap-2 mb-6">
          <StarIcon className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Standout Qualities</h3>
        </div>
        <ul className="space-y-3">
          {data.standoutQualities.map((quality, i) => (
            <li key={i} className="flex items-start gap-3">
              <span className="text-amber-600 dark:text-amber-400 font-bold mt-0.5">•</span>
              <span className="text-neutral-700 dark:text-neutral-300">{quality}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommended Jobs */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Top 5 Recommended Jobs</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700">
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider">
                  Match Score
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {data.recommendedJobs.map((job) => (
                <tr key={job.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-neutral-900 dark:text-white">{job.title}</td>
                  <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">{job.company}</td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500"
                          style={{ width: `${job.matchScore}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{job.matchScore}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CandidateScoreCard;
