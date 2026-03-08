import React from 'react';
import { StarIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface FeedbackDimension {
  name: string;
  average: number;
  color: string;
}

interface InterviewerFeedback {
  id: string;
  interviewer: string;
  isAnonymous: boolean;
  rating: number;
  technicalScore: number;
  communicationScore: number;
  cultureFitScore: number;
  problemSolvingScore: number;
  strengths: string[];
  weaknesses: string[];
  recommendation: 'Strong Hire' | 'Hire' | 'Maybe' | 'No Hire' | 'Strong No Hire';
}

const mockFeedback: InterviewerFeedback[] = [
  {
    id: '1',
    interviewer: 'John Smith',
    isAnonymous: false,
    rating: 4.5,
    technicalScore: 90,
    communicationScore: 85,
    cultureFitScore: 88,
    problemSolvingScore: 92,
    strengths: [
      'Excellent technical knowledge',
      'Clear communication of ideas',
      'Strong problem-solving approach',
      'Good team collaboration skills',
    ],
    weaknesses: ['Slightly limited DevOps experience'],
    recommendation: 'Strong Hire',
  },
  {
    id: '2',
    interviewer: 'Jane Doe',
    isAnonymous: false,
    rating: 4.0,
    technicalScore: 85,
    communicationScore: 88,
    cultureFitScore: 90,
    problemSolvingScore: 87,
    strengths: [
      'Passionate about technology',
      'Great cultural fit',
      'Good communication skills',
      'Willing to learn',
    ],
    weaknesses: ['Some gaps in cloud architecture'],
    recommendation: 'Hire',
  },
  {
    id: '3',
    interviewer: 'Anonymous',
    isAnonymous: true,
    rating: 4.0,
    technicalScore: 88,
    communicationScore: 82,
    cultureFitScore: 85,
    problemSolvingScore: 89,
    strengths: [
      'Strong fundamentals',
      'Good problem solving',
      'Well-prepared for interview',
    ],
    weaknesses: ['Could improve system design knowledge'],
    recommendation: 'Hire',
  },
  {
    id: '4',
    interviewer: 'Mike Johnson',
    isAnonymous: false,
    rating: 3.5,
    technicalScore: 82,
    communicationScore: 80,
    cultureFitScore: 87,
    problemSolvingScore: 85,
    strengths: ['Good overall fit', 'Learns quickly', 'Good attitude'],
    weaknesses: ['Limited senior-level experience', 'Could be more assertive'],
    recommendation: 'Maybe',
  },
];

const getRecommendationColor = (recommendation: InterviewerFeedback['recommendation']) => {
  switch (recommendation) {
    case 'Strong Hire':
      return 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400';
    case 'Hire':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'Maybe':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'No Hire':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'Strong No Hire':
      return 'bg-red-200 dark:bg-red-900/30 text-red-800 dark:text-red-300';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getScoreColor = (score: number): string => {
  if (score >= 85) return 'emerald';
  if (score >= 70) return 'amber';
  return 'red';
};

const getScoreBgClass = (score: number): string => {
  if (score >= 85) return 'bg-emerald-100 dark:bg-emerald-900/20';
  if (score >= 70) return 'bg-amber-100 dark:bg-amber-900/20';
  return 'bg-red-100 dark:bg-red-900/20';
};

const getScoreTextClass = (score: number): string => {
  if (score >= 85) return 'text-emerald-700 dark:text-emerald-400';
  if (score >= 70) return 'text-amber-700 dark:text-amber-400';
  return 'text-red-700 dark:text-red-400';
};

const StarRating: React.FC<{ rating: number }> = ({ rating }) => {
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <StarIcon
          key={i}
          className={`w-4 h-4 ${
            i < Math.floor(rating)
              ? 'fill-amber-400 text-amber-400'
              : i < rating
              ? 'fill-amber-400 text-amber-400 opacity-50'
              : 'text-neutral-300 dark:text-neutral-600'
          }`}
        />
      ))}
    </div>
  );
};

const ScoreBar: React.FC<{ score: number; label: string }> = ({ score, label }) => {
  const bgColor =
    score >= 85 ? 'bg-emerald-500' : score >= 70 ? 'bg-amber-500' : 'bg-red-500';

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{label}</span>
        <span className={`text-sm font-semibold ${getScoreTextClass(score)}`}>{score}</span>
      </div>
      <div className="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${bgColor} transition-all duration-300`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
};

export const InterviewInsights: React.FC = () => {
  const avgRating =
    (mockFeedback.reduce((sum, f) => sum + f.rating, 0) / mockFeedback.length).toFixed(1);
  const avgTechnical = Math.round(
    mockFeedback.reduce((sum, f) => sum + f.technicalScore, 0) / mockFeedback.length
  );
  const avgCommunication = Math.round(
    mockFeedback.reduce((sum, f) => sum + f.communicationScore, 0) / mockFeedback.length
  );
  const avgCultureFit = Math.round(
    mockFeedback.reduce((sum, f) => sum + f.cultureFitScore, 0) / mockFeedback.length
  );
  const avgProblemSolving = Math.round(
    mockFeedback.reduce((sum, f) => sum + f.problemSolvingScore, 0) / mockFeedback.length
  );

  const recommendationCounts = {
    'Strong Hire': mockFeedback.filter(f => f.recommendation === 'Strong Hire').length,
    'Hire': mockFeedback.filter(f => f.recommendation === 'Hire').length,
    'Maybe': mockFeedback.filter(f => f.recommendation === 'Maybe').length,
    'No Hire': mockFeedback.filter(f => f.recommendation === 'No Hire').length,
    'Strong No Hire': mockFeedback.filter(f => f.recommendation === 'Strong No Hire').length,
  };

  const maxCount = Math.max(...Object.values(recommendationCounts));

  const dimensions: FeedbackDimension[] = [
    { name: 'Technical Skills', average: avgTechnical, color: 'bg-blue-500' },
    { name: 'Communication', average: avgCommunication, color: 'bg-emerald-500' },
    { name: 'Culture Fit', average: avgCultureFit, color: 'bg-purple-500' },
    { name: 'Problem Solving', average: avgProblemSolving, color: 'bg-amber-500' },
  ];

  const majorityRecommendation =
    Object.entries(recommendationCounts).sort(([, a], [, b]) => b - a)[0][0] as InterviewerFeedback['recommendation'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Interview Insights</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Aggregated feedback and analysis for Sarah Johnson
        </p>
      </div>

      {/* Feedback Summary */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Feedback Summary</h3>

        {/* Overall Rating */}
        <div className="mb-8 pb-8 border-b border-neutral-200 dark:border-neutral-700">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-500 dark:text-neutral-400 mb-2">Overall Rating</p>
              <div className="flex items-baseline gap-2">
                <div className="text-4xl font-bold text-amber-600 dark:text-amber-400">{avgRating}</div>
                <span className="text-neutral-500 dark:text-neutral-400">/ 5.0</span>
              </div>
            </div>
            <StarRating rating={parseFloat(avgRating)} />
          </div>
        </div>

        {/* Dimension Scores */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {dimensions.map((dim) => (
            <div
              key={dim.name}
              className={`p-6 rounded-lg border border-neutral-200 dark:border-neutral-700 ${getScoreBgClass(dim.average)}`}
            >
              <p className="text-sm font-semibold text-neutral-900 dark:text-white mb-4">{dim.name}</p>
              <div className="flex items-baseline gap-3">
                <div className={`text-3xl font-bold ${getScoreTextClass(dim.average)}`}>
                  {dim.average}
                </div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">/ 100</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendation Distribution */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Recommendation Distribution</h3>

        <div className="space-y-4">
          {(['Strong Hire', 'Hire', 'Maybe', 'No Hire', 'Strong No Hire'] as const).map((rec) => {
            const count = recommendationCounts[rec];
            const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;

            const colorMap: Record<string, string> = {
              'Strong Hire': 'bg-emerald-500',
              'Hire': 'bg-green-500',
              'Maybe': 'bg-amber-500',
              'No Hire': 'bg-red-500',
              'Strong No Hire': 'bg-red-700',
            };

            return (
              <div key={rec}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-neutral-900 dark:text-white">{rec}</span>
                  <span className="text-sm font-semibold text-neutral-600 dark:text-neutral-400">{count}</span>
                </div>
                <div className="w-full h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${colorMap[rec]} transition-all duration-300`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Consensus Verdict */}
      <div className={`rounded-xl p-8 border-2 ${getRecommendationColor(majorityRecommendation)}`}>
        <div className="flex items-start gap-4">
          {majorityRecommendation.includes('Hire') && !majorityRecommendation.includes('No') ? (
            <CheckCircleIcon className="w-6 h-6 flex-shrink-0 mt-1" />
          ) : majorityRecommendation.includes('No') ? (
            <ExclamationTriangleIcon className="w-6 h-6 flex-shrink-0 mt-1" />
          ) : (
            <StarIcon className="w-6 h-6 flex-shrink-0 mt-1" />
          )}
          <div>
            <h4 className="font-semibold text-lg mb-1">Hiring Committee Verdict</h4>
            <p className="text-sm opacity-90">
              Based on the majority of interviewer recommendations, this candidate is a{' '}
              <strong className="font-semibold">{majorityRecommendation.toLowerCase()}</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Individual Feedback Cards */}
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">Individual Feedback</h3>

        {mockFeedback.map((feedback) => (
          <div
            key={feedback.id}
            className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-6 pb-6 border-b border-neutral-200 dark:border-neutral-700">
              <div>
                <h4 className="text-base font-semibold text-neutral-900 dark:text-white">
                  {feedback.isAnonymous ? 'Anonymous Interviewer' : feedback.interviewer}
                </h4>
                {feedback.isAnonymous && (
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Anonymous feedback</p>
                )}
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="flex justify-end mb-2">
                    <StarRating rating={feedback.rating} />
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${getRecommendationColor(feedback.recommendation)}`}>
                    {feedback.recommendation}
                  </span>
                </div>
              </div>
            </div>

            {/* Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 pb-8 border-b border-neutral-200 dark:border-neutral-700">
              <ScoreBar score={feedback.technicalScore} label="Technical Skills" />
              <ScoreBar score={feedback.communicationScore} label="Communication" />
              <ScoreBar score={feedback.cultureFitScore} label="Culture Fit" />
              <ScoreBar score={feedback.problemSolvingScore} label="Problem Solving" />
            </div>

            {/* Strengths and Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h5 className="font-semibold text-neutral-900 dark:text-white mb-3 flex items-center gap-2">
                  <CheckCircleIcon className="w-4 h-4 text-emerald-500" />
                  Strengths
                </h5>
                <ul className="space-y-2">
                  {feedback.strengths.map((strength, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-neutral-700 dark:text-neutral-300">
                      <span className="text-emerald-500 mt-1 flex-shrink-0">✓</span>
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h5 className="font-semibold text-neutral-900 dark:text-white mb-3 flex items-center gap-2">
                  <ExclamationTriangleIcon className="w-4 h-4 text-amber-500" />
                  Weaknesses
                </h5>
                <ul className="space-y-2">
                  {feedback.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-neutral-700 dark:text-neutral-300">
                      <span className="text-amber-500 mt-1 flex-shrink-0">⚠</span>
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InterviewInsights;
