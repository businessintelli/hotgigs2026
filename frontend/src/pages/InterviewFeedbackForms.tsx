import React, { useState } from 'react';
import {
  ClipboardDocumentCheckIcon,
  StarIcon,
  UserGroupIcon,
  ScaleIcon,
  PlusIcon,
  ChartBarIcon,
  CheckBadgeIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  MinusIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolid } from '@heroicons/react/24/solid';

// ── Types ──
interface RubricCriterion {
  name: string;
  description: string;
  weight: number;
  scale_labels: Record<number, string>;
}
interface Rubric {
  id: number;
  name: string;
  description: string;
  job_role: string | null;
  interview_stage: string;
  criteria: RubricCriterion[];
  is_active: boolean;
}
interface FeedbackEntry {
  id: number;
  interview_id: number;
  interviewer_name: string;
  candidate_name: string;
  job_title: string;
  interview_stage: string;
  criteria_scores: Record<string, number>;
  weighted_total: number;
  overall_rating: number;
  recommendation: string;
  strengths: string[];
  weaknesses: string[];
  submitted_at: string;
}
interface Calibration {
  interviewer_name: string;
  avg_rating: number;
  total_reviews: number;
  harshness_score: number;
  consistency_score: number;
}

// ── Mock Data ──
const RUBRICS: Rubric[] = [
  {
    id: 1, name: 'Software Engineer — Technical', description: 'Technical assessment for SWE roles',
    job_role: 'Software Engineer', interview_stage: 'technical', is_active: true,
    criteria: [
      { name: 'Problem Solving', description: 'Break down complex problems', weight: 0.25, scale_labels: { 1: 'Cannot identify', 2: 'Struggles', 3: 'Adequate', 4: 'Strong', 5: 'Exceptional' } },
      { name: 'Code Quality', description: 'Clean, readable code', weight: 0.20, scale_labels: { 1: 'Messy', 2: 'Functional', 3: 'Acceptable', 4: 'Clean', 5: 'Exemplary' } },
      { name: 'System Design', description: 'Architecture thinking', weight: 0.20, scale_labels: { 1: 'None', 2: 'Basic', 3: 'Competent', 4: 'Strong', 5: 'Expert' } },
      { name: 'Communication', description: 'Explains clearly', weight: 0.15, scale_labels: { 1: 'Cannot explain', 2: 'Unclear', 3: 'Adequate', 4: 'Clear', 5: 'Exceptional' } },
      { name: 'Culture Fit', description: 'Team alignment', weight: 0.20, scale_labels: { 1: 'Poor', 2: 'Concerns', 3: 'Neutral', 4: 'Good', 5: 'Excellent' } },
    ],
  },
  {
    id: 2, name: 'Leadership — Behavioral', description: 'Behavioral interview for leadership',
    job_role: 'Manager', interview_stage: 'behavioral', is_active: true,
    criteria: [
      { name: 'Leadership Style', description: 'Effective leadership', weight: 0.25, scale_labels: {} },
      { name: 'Conflict Resolution', description: 'Handles disagreements', weight: 0.20, scale_labels: {} },
      { name: 'Strategic Thinking', description: 'Long-term vision', weight: 0.20, scale_labels: {} },
      { name: 'Team Development', description: 'Grows team members', weight: 0.20, scale_labels: {} },
      { name: 'Stakeholder Mgmt', description: 'Manages across', weight: 0.15, scale_labels: {} },
    ],
  },
  {
    id: 3, name: 'General — Phone Screen', description: 'Initial phone screen rubric',
    job_role: null, interview_stage: 'phone_screen', is_active: true,
    criteria: [
      { name: 'Relevant Experience', description: 'Depth of experience', weight: 0.30, scale_labels: {} },
      { name: 'Communication', description: 'Clarity and professionalism', weight: 0.25, scale_labels: {} },
      { name: 'Motivation', description: 'Interest in role', weight: 0.25, scale_labels: {} },
      { name: 'Availability', description: 'Timeline fit', weight: 0.20, scale_labels: {} },
    ],
  },
];

const CANDIDATES = ['Alex Chen', 'Maya Patel', 'James Wilson', 'Sofia Rodriguez', 'David Kim'];
const INTERVIEWERS = ['Sarah Mitchell', 'Robert Chen', 'Jennifer Park', 'Michael Torres', 'Angela Williams'];
const RECS = ['strong_hire', 'hire', 'neutral', 'no_hire'];

const MOCK_FEEDBACK: FeedbackEntry[] = Array.from({ length: 15 }, (_, i) => {
  const rubric = RUBRICS[i % RUBRICS.length];
  const scores: Record<string, number> = {};
  rubric.criteria.forEach(c => { scores[c.name] = Math.floor(Math.random() * 3) + 2; });
  const weighted = rubric.criteria.reduce((s, c) => s + (scores[c.name] || 3) * c.weight, 0);
  return {
    id: i + 1, interview_id: 100 + i,
    interviewer_name: INTERVIEWERS[i % INTERVIEWERS.length],
    candidate_name: CANDIDATES[i % CANDIDATES.length],
    job_title: ['Senior Python Dev', 'React Lead', 'DevOps Engineer'][i % 3],
    interview_stage: rubric.interview_stage,
    criteria_scores: scores, weighted_total: Math.round(weighted * 100) / 100,
    overall_rating: Math.floor(Math.random() * 3) + 2,
    recommendation: RECS[Math.floor(Math.random() * 4)],
    strengths: ['Strong communicator', 'Deep technical skills', 'Fast learner'].slice(0, Math.floor(Math.random() * 3) + 1),
    weaknesses: ['Limited design experience', 'Could improve communication'].slice(0, Math.floor(Math.random() * 2)),
    submitted_at: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
  };
});

const CALIBRATIONS: Calibration[] = INTERVIEWERS.map((name) => ({
  interviewer_name: name,
  avg_rating: Math.round((Math.random() * 1.5 + 2.8) * 10) / 10,
  total_reviews: Math.floor(Math.random() * 8) + 3,
  harshness_score: Math.round((Math.random() * 1.4 - 0.7) * 100) / 100,
  consistency_score: Math.round((Math.random() * 0.3 + 0.6) * 100) / 100,
}));

const recBadge = (rec: string) => {
  const cls: Record<string, string> = {
    strong_hire: 'bg-green-100 text-green-700', hire: 'bg-emerald-100 text-emerald-700',
    neutral: 'bg-amber-100 text-amber-700', no_hire: 'bg-red-100 text-red-700',
  };
  const labels: Record<string, string> = {
    strong_hire: 'Strong Hire', hire: 'Hire', neutral: 'Neutral', no_hire: 'No Hire',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${cls[rec] || 'bg-neutral-100'}`}>{labels[rec] || rec}</span>;
};

const StarRating: React.FC<{ rating: number; max?: number }> = ({ rating, max = 5 }) => (
  <div className="flex gap-0.5">
    {Array.from({ length: max }, (_, i) =>
      i < rating ? <StarSolid key={i} className="h-4 w-4 text-amber-400" /> : <StarIcon key={i} className="h-4 w-4 text-neutral-300" />
    )}
  </div>
);

export const InterviewFeedbackForms: React.FC = () => {
  const [tab, setTab] = useState<'rubrics' | 'feedback' | 'fill' | 'calibrate'>('rubrics');
  const [selectedRubric, setSelectedRubric] = useState<Rubric | null>(null);
  const [formScores, setFormScores] = useState<Record<string, number>>({});
  const [formRec, setFormRec] = useState('neutral');
  const [formNotes, setFormNotes] = useState('');

  const tabs = [
    { key: 'rubrics' as const, label: 'Scoring Rubrics', icon: ClipboardDocumentCheckIcon },
    { key: 'fill' as const, label: 'Fill Feedback', icon: PlusIcon },
    { key: 'feedback' as const, label: 'All Feedback', icon: UserGroupIcon },
    { key: 'calibrate' as const, label: 'Calibration', icon: ScaleIcon },
  ];

  const startFillForm = (rubric: Rubric) => {
    setSelectedRubric(rubric);
    const scores: Record<string, number> = {};
    rubric.criteria.forEach(c => { scores[c.name] = 3; });
    setFormScores(scores);
    setFormRec('neutral');
    setFormNotes('');
    setTab('fill');
  };

  const calcWeighted = () => {
    if (!selectedRubric) return 0;
    return Math.round(selectedRubric.criteria.reduce((s, c) => s + (formScores[c.name] || 3) * c.weight, 0) * 100) / 100;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 flex items-center gap-2">
            <ClipboardDocumentCheckIcon className="h-6 w-6 text-blue-600" />
            Interview Feedback Forms
          </h1>
          <p className="text-sm text-neutral-500 mt-1">Structured scoring rubrics for consistent, fair evaluations</p>
        </div>
      </div>

      {/* KPI */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Active Rubrics', value: RUBRICS.filter(r => r.is_active).length, color: 'text-blue-600' },
          { label: 'Total Feedback', value: MOCK_FEEDBACK.length, color: 'text-green-600' },
          { label: 'Avg Rating', value: (MOCK_FEEDBACK.reduce((s, f) => s + f.overall_rating, 0) / MOCK_FEEDBACK.length).toFixed(1), color: 'text-amber-600' },
          { label: 'Hire Rate', value: `${Math.round((MOCK_FEEDBACK.filter(f => f.recommendation === 'hire' || f.recommendation === 'strong_hire').length / MOCK_FEEDBACK.length) * 100)}%`, color: 'text-emerald-600' },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl border border-neutral-200 p-4">
            <p className="text-xs text-neutral-500">{kpi.label}</p>
            <p className={`text-2xl font-bold ${kpi.color} mt-1`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
              tab === key ? 'bg-white text-blue-700 shadow-sm' : 'text-neutral-600 hover:text-neutral-800'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ── RUBRICS TAB ── */}
      {tab === 'rubrics' && (
        <div className="space-y-4">
          {RUBRICS.map((rubric) => (
            <div key={rubric.id} className="bg-white rounded-xl border border-neutral-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-base font-semibold text-neutral-800">{rubric.name}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{rubric.description}</p>
                  <div className="flex gap-2 mt-2">
                    {rubric.job_role && <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{rubric.job_role}</span>}
                    <span className="text-xs bg-purple-50 text-purple-600 px-2 py-0.5 rounded-full">{rubric.interview_stage}</span>
                  </div>
                </div>
                <button
                  onClick={() => startFillForm(rubric)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                >
                  <PlusIcon className="h-4 w-4" /> Use This Rubric
                </button>
              </div>

              <table className="w-full">
                <thead>
                  <tr className="text-xs text-neutral-500 border-b">
                    <th className="text-left py-2 font-medium">Criterion</th>
                    <th className="text-left py-2 font-medium">Description</th>
                    <th className="text-center py-2 font-medium">Weight</th>
                    <th className="text-center py-2 font-medium">Scale Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {rubric.criteria.map((c) => (
                    <tr key={c.name} className="border-b last:border-0">
                      <td className="py-2 text-sm font-medium text-neutral-800">{c.name}</td>
                      <td className="py-2 text-sm text-neutral-500">{c.description}</td>
                      <td className="py-2 text-center">
                        <span className="text-xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded-full">{Math.round(c.weight * 100)}%</span>
                      </td>
                      <td className="py-2 text-center">
                        <div className="flex justify-center gap-1">
                          {[1, 2, 3, 4, 5].map(n => (
                            <span key={n} className="w-6 h-6 rounded text-xs flex items-center justify-center bg-neutral-100 text-neutral-500">{n}</span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}

      {/* ── FILL FEEDBACK TAB ── */}
      {tab === 'fill' && selectedRubric && (
        <div className="bg-white rounded-xl border border-neutral-200 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-neutral-800">Scoring: {selectedRubric.name}</h3>
              <p className="text-xs text-neutral-500 mt-0.5">{selectedRubric.description}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-neutral-500">Weighted Score</p>
              <p className={`text-2xl font-bold ${calcWeighted() >= 4 ? 'text-green-600' : calcWeighted() >= 3 ? 'text-amber-600' : 'text-red-600'}`}>
                {calcWeighted()} / 5.0
              </p>
            </div>
          </div>

          {/* Criteria Scoring */}
          <div className="space-y-4">
            {selectedRubric.criteria.map((criterion) => (
              <div key={criterion.name} className="border border-neutral-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="text-sm font-semibold text-neutral-800">{criterion.name}</p>
                    <p className="text-xs text-neutral-500">{criterion.description}</p>
                  </div>
                  <span className="text-xs bg-neutral-100 text-neutral-500 px-2 py-0.5 rounded-full">{Math.round(criterion.weight * 100)}% weight</span>
                </div>
                <div className="flex gap-2 mt-3">
                  {[1, 2, 3, 4, 5].map((score) => {
                    const label = criterion.scale_labels[score] || ['Poor', 'Below Avg', 'Meets', 'Exceeds', 'Outstanding'][score - 1];
                    const selected = formScores[criterion.name] === score;
                    return (
                      <button
                        key={score}
                        onClick={() => setFormScores({ ...formScores, [criterion.name]: score })}
                        className={`flex-1 py-2 px-2 rounded-lg text-center border-2 transition-all ${
                          selected
                            ? score >= 4 ? 'border-green-500 bg-green-50' : score === 3 ? 'border-amber-500 bg-amber-50' : 'border-red-500 bg-red-50'
                            : 'border-neutral-200 hover:border-neutral-300'
                        }`}
                      >
                        <p className={`text-lg font-bold ${selected ? (score >= 4 ? 'text-green-700' : score === 3 ? 'text-amber-700' : 'text-red-700') : 'text-neutral-400'}`}>{score}</p>
                        <p className="text-xs text-neutral-500 mt-0.5 leading-tight">{label}</p>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Recommendation */}
          <div>
            <p className="text-sm font-semibold text-neutral-700 mb-2">Recommendation</p>
            <div className="flex gap-2">
              {[
                { value: 'strong_hire', label: 'Strong Hire', icon: HandThumbUpIcon, color: 'border-green-500 bg-green-50 text-green-700' },
                { value: 'hire', label: 'Hire', icon: HandThumbUpIcon, color: 'border-emerald-500 bg-emerald-50 text-emerald-700' },
                { value: 'neutral', label: 'Neutral', icon: MinusIcon, color: 'border-amber-500 bg-amber-50 text-amber-700' },
                { value: 'no_hire', label: 'No Hire', icon: HandThumbDownIcon, color: 'border-red-500 bg-red-50 text-red-700' },
              ].map(({ value, label, icon: RIcon, color }) => (
                <button
                  key={value}
                  onClick={() => setFormRec(value)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all ${
                    formRec === value ? color : 'border-neutral-200 text-neutral-500 hover:border-neutral-300'
                  }`}
                >
                  <RIcon className="h-4 w-4" />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div>
            <p className="text-sm font-semibold text-neutral-700 mb-2">Detailed Notes</p>
            <textarea
              value={formNotes}
              onChange={(e) => setFormNotes(e.target.value)}
              rows={4}
              className="w-full border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              placeholder="Add detailed observations, examples, and context..."
            />
          </div>

          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
              <CheckBadgeIcon className="h-5 w-5" /> Submit Feedback
            </button>
            <button className="flex items-center gap-2 px-6 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
              <SparklesIcon className="h-5 w-5" /> AI Assist
            </button>
          </div>
        </div>
      )}

      {/* ── ALL FEEDBACK TAB ── */}
      {tab === 'feedback' && (
        <div className="bg-white rounded-xl border border-neutral-200">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-neutral-500 border-b bg-neutral-50">
                <th className="text-left py-2 px-4 font-medium">Candidate</th>
                <th className="text-left py-2 px-4 font-medium">Job</th>
                <th className="text-left py-2 px-4 font-medium">Interviewer</th>
                <th className="text-center py-2 px-4 font-medium">Stage</th>
                <th className="text-center py-2 px-4 font-medium">Rating</th>
                <th className="text-center py-2 px-4 font-medium">Weighted</th>
                <th className="text-center py-2 px-4 font-medium">Recommendation</th>
                <th className="text-center py-2 px-4 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_FEEDBACK.map((f) => (
                <tr key={f.id} className="border-b last:border-0 hover:bg-neutral-50">
                  <td className="py-3 px-4 text-sm font-medium text-neutral-800">{f.candidate_name}</td>
                  <td className="py-3 px-4 text-sm text-neutral-600">{f.job_title}</td>
                  <td className="py-3 px-4 text-sm text-neutral-600">{f.interviewer_name}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="text-xs bg-purple-50 text-purple-600 px-2 py-0.5 rounded-full">{f.interview_stage}</span>
                  </td>
                  <td className="py-3 px-4"><StarRating rating={f.overall_rating} /></td>
                  <td className="py-3 px-4 text-center">
                    <span className={`text-sm font-bold ${f.weighted_total >= 4 ? 'text-green-600' : f.weighted_total >= 3 ? 'text-amber-600' : 'text-red-600'}`}>
                      {f.weighted_total}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">{recBadge(f.recommendation)}</td>
                  <td className="py-3 px-4 text-center text-xs text-neutral-400">{new Date(f.submitted_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── CALIBRATION TAB ── */}
      {tab === 'calibrate' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4 flex items-center gap-2">
              <ScaleIcon className="h-4 w-4" /> Interviewer Calibration Report
            </h3>
            <p className="text-xs text-neutral-500 mb-4">Compare scoring patterns to identify lenient or harsh evaluators and ensure consistency.</p>
            <table className="w-full">
              <thead>
                <tr className="text-xs text-neutral-500 border-b">
                  <th className="text-left py-2 font-medium">Interviewer</th>
                  <th className="text-center py-2 font-medium">Reviews</th>
                  <th className="text-center py-2 font-medium">Avg Rating</th>
                  <th className="text-center py-2 font-medium">Harshness</th>
                  <th className="text-center py-2 font-medium">Consistency</th>
                  <th className="text-center py-2 font-medium">Assessment</th>
                </tr>
              </thead>
              <tbody>
                {CALIBRATIONS.map((cal) => {
                  const assessment = cal.harshness_score < -0.3 ? 'Harsh' : cal.harshness_score > 0.3 ? 'Lenient' : 'Balanced';
                  const assessColor = assessment === 'Balanced' ? 'bg-green-100 text-green-700' : assessment === 'Harsh' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700';
                  return (
                    <tr key={cal.interviewer_name} className="border-b last:border-0 hover:bg-neutral-50">
                      <td className="py-3 text-sm font-medium text-neutral-800">{cal.interviewer_name}</td>
                      <td className="py-3 text-center text-sm text-neutral-600">{cal.total_reviews}</td>
                      <td className="py-3 text-center">
                        <span className="text-sm font-bold text-amber-600">{cal.avg_rating}</span>
                      </td>
                      <td className="py-3 text-center">
                        <span className={`text-sm font-semibold ${cal.harshness_score < 0 ? 'text-red-500' : 'text-green-500'}`}>
                          {cal.harshness_score > 0 ? '+' : ''}{cal.harshness_score}
                        </span>
                      </td>
                      <td className="py-3 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-16 bg-neutral-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${cal.consistency_score >= 0.8 ? 'bg-green-500' : cal.consistency_score >= 0.6 ? 'bg-amber-500' : 'bg-red-500'}`}
                              style={{ width: `${cal.consistency_score * 100}%` }}
                            />
                          </div>
                          <span className="text-xs text-neutral-500">{Math.round(cal.consistency_score * 100)}%</span>
                        </div>
                      </td>
                      <td className="py-3 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${assessColor}`}>{assessment}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Rating Distribution Vis */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-sm font-semibold text-neutral-700 mb-4 flex items-center gap-2">
              <ChartBarIcon className="h-4 w-4" /> Rating Distribution by Interviewer
            </h3>
            <div className="space-y-3">
              {CALIBRATIONS.map((cal) => (
                <div key={cal.interviewer_name} className="flex items-center gap-3">
                  <div className="w-32 text-sm font-medium text-neutral-700 truncate">{cal.interviewer_name}</div>
                  <div className="flex-1 flex gap-0.5 h-6">
                    {[1, 2, 3, 4, 5].map((score) => {
                      // Generate a distribution bar
                      const weight = score <= 2 ? (cal.harshness_score < 0 ? 25 : 10) :
                                     score === 3 ? 30 :
                                     (cal.harshness_score > 0 ? 25 : 15);
                      const colors = ['bg-red-400', 'bg-orange-400', 'bg-amber-400', 'bg-green-400', 'bg-emerald-500'];
                      return (
                        <div
                          key={score}
                          className={`${colors[score - 1]} rounded`}
                          style={{ width: `${weight}%` }}
                          title={`Score ${score}: ~${weight}%`}
                        />
                      );
                    })}
                  </div>
                </div>
              ))}
              <div className="flex gap-2 mt-2">
                {[1, 2, 3, 4, 5].map(s => {
                  const colors = ['bg-red-400', 'bg-orange-400', 'bg-amber-400', 'bg-green-400', 'bg-emerald-500'];
                  return (
                    <span key={s} className="flex items-center gap-1 text-xs text-neutral-500">
                      <span className={`w-3 h-3 ${colors[s - 1]} rounded`} /> {s}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
