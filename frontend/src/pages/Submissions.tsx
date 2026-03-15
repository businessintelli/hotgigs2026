import React, { useState } from 'react';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { useApi } from '@/hooks/useApi';
import { getSubmissions } from '@/api/submissions';
import type { Submission } from '@/types';

/* ─── helpers ─── */
const fitScoreBg = (s: number) =>
  s >= 85 ? 'bg-emerald-500 text-white' :
  s >= 70 ? 'bg-emerald-100 text-emerald-800' :
  s >= 55 ? 'bg-blue-100 text-blue-800' :
  s >= 40 ? 'bg-amber-100 text-amber-800' :
  'bg-red-100 text-red-800';

const fitLabel = (s: number) =>
  s >= 85 ? 'Strong Fit' : s >= 70 ? 'Good Fit' : s >= 55 ? 'Partial Fit' : s >= 40 ? 'Weak Fit' : 'Poor Fit';

const recColors: Record<string, string> = {
  strong_hire: 'bg-emerald-600', hire: 'bg-emerald-500', maybe: 'bg-amber-500',
  no_hire: 'bg-red-500', strong_no_hire: 'bg-red-700',
};

/* ─── screening status badge helpers ─── */
const screeningBadgeCls = (status: string) => {
  switch (status) {
    case 'shortlisted': return 'bg-emerald-600 text-white';
    case 'screened': return 'bg-emerald-100 text-emerald-800';
    case 'hold': return 'bg-amber-100 text-amber-800';
    case 'rejected': return 'bg-red-100 text-red-800';
    case 'pending': return 'bg-orange-100 text-orange-700';
    default: return 'bg-neutral-100 text-neutral-400';
  }
};
const screeningIcon = (status: string) => {
  switch (status) {
    case 'shortlisted': return '★'; case 'screened': return '✓'; case 'hold': return '⏸';
    case 'rejected': return '✗'; case 'pending': return '…'; default: return '';
  }
};

/* ─── mock enrichment data (feedback scores, persistent scores, screening status) ─── */
const candidateScoreEnrichment: Record<string, {
  fitScore: number; techScore: number; commScore: number; immigScore: number;
  feedbackCount: number; recommendation: string | null; skills: { name: string; score: number }[];
  riskFactors: string[]; hasFeedback: boolean; sharedWithSubmission: boolean;
  screeningStatus: string; screeningScore: number;
}> = {
  // These would come from the /interview-feedback/job-match, /persistent-scores, and /screening-feedback/records APIs
  'Rajesh Kumar': { fitScore: 82, techScore: 85, commScore: 80, immigScore: 65, feedbackCount: 2, recommendation: 'hire', skills: [{ name: 'Python', score: 90 }, { name: 'SQL', score: 80 }, { name: 'AWS', score: 60 }], riskFactors: ['H1B transfer needed'], hasFeedback: true, sharedWithSubmission: true, screeningStatus: 'screened', screeningScore: 78 },
  'Emily Chen': { fitScore: 91, techScore: 92, commScore: 90, immigScore: 100, feedbackCount: 1, recommendation: 'strong_hire', skills: [{ name: 'Python', score: 100 }, { name: 'SQL', score: 80 }, { name: 'System Design', score: 80 }], riskFactors: ['Rate at top of budget'], hasFeedback: true, sharedWithSubmission: true, screeningStatus: 'shortlisted', screeningScore: 92 },
  'Marcus Johnson': { fitScore: 58, techScore: 62, commScore: 72, immigScore: 40, feedbackCount: 1, recommendation: 'maybe', skills: [{ name: 'React', score: 80 }, { name: 'Python', score: 60 }, { name: 'SQL', score: 60 }], riskFactors: ['OPT expiring', 'Wants remote — role is hybrid'], hasFeedback: true, sharedWithSubmission: false, screeningStatus: 'hold', screeningScore: 58 },
  'Priya Sharma': { fitScore: 0, techScore: 0, commScore: 0, immigScore: 0, feedbackCount: 0, recommendation: null, skills: [], riskFactors: [], hasFeedback: false, sharedWithSubmission: false, screeningStatus: 'pending', screeningScore: 0 },
  'Alex Torres': { fitScore: 0, techScore: 0, commScore: 0, immigScore: 0, feedbackCount: 0, recommendation: null, skills: [], riskFactors: [], hasFeedback: false, sharedWithSubmission: false, screeningStatus: 'not_screened', screeningScore: 0 },
};

const submissionStages = [
  { id: 'draft', label: 'Draft', color: 'bg-neutral-100 dark:bg-neutral-700' },
  { id: 'pending', label: 'Pending', color: 'bg-warning-100 dark:bg-warning-900/20' },
  { id: 'approved', label: 'Approved', color: 'bg-success-100 dark:bg-success-900/20' },
  { id: 'submitted', label: 'Submitted', color: 'bg-primary-100 dark:bg-primary-900/20' },
  { id: 'customer_review', label: 'Customer Review', color: 'bg-primary-100 dark:bg-primary-900/20' },
  { id: 'placed', label: 'Placed', color: 'bg-success-100 dark:bg-success-900/20' },
];

export const Submissions: React.FC = () => {
  const [listView, setListView] = useState(false);
  const [sortByScore, setSortByScore] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const { data: submissionsData } = useApi(['submissions', 0, ''], () =>
    getSubmissions({ page: 1, per_page: 50 })
  );

  const getEnrichment = (submission: Submission) => {
    const name = `${submission.candidate.first_name} ${submission.candidate.last_name}`;
    return candidateScoreEnrichment[name] || { fitScore: 0, techScore: 0, commScore: 0, immigScore: 0, feedbackCount: 0, recommendation: null, skills: [], riskFactors: [], hasFeedback: false, sharedWithSubmission: false };
  };

  const submissionsByStage = (stage: string) => {
    const items = submissionsData?.data.filter((s) => s.status === stage) || [];
    if (sortByScore) {
      return items.sort((a, b) => {
        const ea = getEnrichment(a);
        const eb = getEnrichment(b);
        const scoreA = ea.fitScore || a.match_score;
        const scoreB = eb.fitScore || b.match_score;
        return scoreB - scoreA;
      });
    }
    return items;
  };

  const allSorted = () => {
    const items = submissionsData?.data || [];
    if (sortByScore) {
      return [...items].sort((a, b) => {
        const ea = getEnrichment(a);
        const eb = getEnrichment(b);
        return (eb.fitScore || b.match_score) - (ea.fitScore || a.match_score);
      });
    }
    return items;
  };

  if (listView) {
    return (
      <div className="p-4 md:p-6 space-y-6 pb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Submission Pipeline</h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Score-ranked candidates with feedback integration</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setSortByScore(!sortByScore)}
              className={`px-3 py-1.5 text-xs rounded-lg border ${sortByScore ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200'}`}>
              {sortByScore ? 'Sorted by Fit Score' : 'Default Order'}
            </button>
            <button onClick={() => setListView(false)}
              className="px-4 py-2 border border-neutral-200 dark:border-neutral-700 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors text-sm">
              Kanban View
            </button>
          </div>
        </div>

        <Card>
          <CardHeader>All Submissions {sortByScore && <span className="text-xs text-violet-600 font-normal ml-2">— ranked by fit score</span>}</CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-2 px-2 font-semibold text-xs text-neutral-500">#</th>
                    <th className="text-left py-2 px-2 font-semibold text-xs text-neutral-500">Candidate</th>
                    <th className="text-left py-2 px-2 font-semibold text-xs text-neutral-500">Requirement</th>
                    <th className="text-center py-2 px-2 font-semibold text-xs text-neutral-500">Fit Score</th>
                    <th className="text-center py-2 px-2 font-semibold text-xs text-neutral-500">Tech</th>
                    <th className="text-center py-2 px-2 font-semibold text-xs text-neutral-500">Comm</th>
                    <th className="text-center py-2 px-2 font-semibold text-xs text-neutral-500">Immig</th>
                    <th className="text-center py-2 px-2 font-semibold text-xs text-neutral-500">Match %</th>
                    <th className="text-left py-2 px-2 font-semibold text-xs text-neutral-500">Rec</th>
                    <th className="text-center py-2 px-2 font-semibold text-xs text-neutral-500">Feedback</th>
                    <th className="text-left py-2 px-2 font-semibold text-xs text-neutral-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {allSorted().map((submission, idx) => {
                    const e = getEnrichment(submission);
                    const name = `${submission.candidate.first_name} ${submission.candidate.last_name}`;
                    return (
                      <React.Fragment key={submission.id}>
                        <tr className="border-b border-neutral-100 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700 cursor-pointer"
                          onClick={() => setExpandedId(expandedId === submission.id ? null : submission.id)}>
                          <td className="py-2 px-2 text-xs text-neutral-400">{idx + 1}</td>
                          <td className="py-2 px-2">
                            <p className="font-medium text-neutral-900 dark:text-white">
                              {name}
                              <span className={`ml-1.5 text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${screeningBadgeCls(e.screeningStatus)}`}>
                                {screeningIcon(e.screeningStatus)} {e.screeningStatus === 'not_screened' ? 'not screened' : e.screeningStatus}
                              </span>
                            </p>
                            {e.hasFeedback && e.fitScore > 0 && (
                              <span className={`text-[9px] px-1.5 py-0.5 rounded-full mt-0.5 inline-block ${fitScoreBg(e.fitScore)}`}>
                                {fitLabel(e.fitScore)}
                              </span>
                            )}
                          </td>
                          <td className="py-2 px-2 text-xs text-neutral-600">{submission.requirement.title}</td>
                          <td className="py-2 px-2 text-center">
                            {e.fitScore > 0 ? (
                              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${fitScoreBg(e.fitScore)}`}>{e.fitScore}</span>
                            ) : <span className="text-neutral-300 text-xs">—</span>}
                          </td>
                          <td className="py-2 px-2 text-center">
                            {e.techScore > 0 ? <span className="text-xs font-medium">{e.techScore}</span> : <span className="text-neutral-300">—</span>}
                          </td>
                          <td className="py-2 px-2 text-center">
                            {e.commScore > 0 ? <span className="text-xs font-medium">{e.commScore}</span> : <span className="text-neutral-300">—</span>}
                          </td>
                          <td className="py-2 px-2 text-center">
                            {e.immigScore > 0 ? (
                              <span className={`text-xs font-medium ${e.immigScore < 50 ? 'text-red-600' : ''}`}>{e.immigScore}</span>
                            ) : <span className="text-neutral-300">—</span>}
                          </td>
                          <td className="py-2 px-2 text-center">
                            <span className="text-xs font-bold text-primary-600 dark:text-primary-400">{submission.match_score}%</span>
                          </td>
                          <td className="py-2 px-2">
                            {e.recommendation ? (
                              <span className={`text-[10px] px-2 py-0.5 rounded-full text-white ${recColors[e.recommendation]}`}>
                                {e.recommendation.replace(/_/g, ' ')}
                              </span>
                            ) : <span className="text-neutral-300 text-xs">—</span>}
                          </td>
                          <td className="py-2 px-2 text-center">
                            {e.hasFeedback ? (
                              <div className="flex items-center justify-center gap-1">
                                <span className="text-emerald-600 text-xs font-bold">✓</span>
                                <span className="text-[9px] text-neutral-400">{e.feedbackCount}</span>
                                {e.sharedWithSubmission && <span className="text-[9px] px-1 py-0.5 bg-violet-100 text-violet-600 rounded">shared</span>}
                              </div>
                            ) : (
                              <a href="/detailed-feedback" className="text-[10px] text-violet-600 hover:underline">Add</a>
                            )}
                          </td>
                          <td className="py-2 px-2"><StatusBadge status={submission.status} /></td>
                        </tr>

                        {/* Expanded row with score details */}
                        {expandedId === submission.id && e.hasFeedback && (
                          <tr><td colSpan={11} className="bg-neutral-50 dark:bg-neutral-800 p-4">
                            <div className="grid grid-cols-4 gap-4">
                              {/* Skills */}
                              <div>
                                <p className="text-xs font-semibold text-neutral-700 mb-2">Skill Scores (from interviews)</p>
                                <div className="space-y-1.5">
                                  {e.skills.map(sk => (
                                    <div key={sk.name} className="flex items-center gap-2">
                                      <span className="text-[10px] w-16 text-neutral-500">{sk.name}</span>
                                      <div className="flex-1 h-2 bg-neutral-200 rounded-full">
                                        <div className={`h-2 rounded-full ${sk.score >= 80 ? 'bg-emerald-500' : sk.score >= 60 ? 'bg-blue-500' : 'bg-amber-500'}`}
                                          style={{ width: `${sk.score}%` }} />
                                      </div>
                                      <span className="text-[10px] font-medium w-6 text-right">{sk.score}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              {/* Risk factors */}
                              <div>
                                <p className="text-xs font-semibold text-neutral-700 mb-2">Risk Factors</p>
                                {e.riskFactors.length > 0 ? (
                                  <div className="space-y-1">
                                    {e.riskFactors.map((r, i) => (
                                      <div key={i} className="flex items-start gap-1 text-xs text-orange-700">
                                        <span className="text-orange-500">⚠</span>{r}
                                      </div>
                                    ))}
                                  </div>
                                ) : <p className="text-xs text-emerald-600">No significant risks</p>}
                              </div>
                              {/* Scores summary */}
                              <div>
                                <p className="text-xs font-semibold text-neutral-700 mb-2">Score Summary</p>
                                <div className="space-y-1 text-xs">
                                  <div className="flex justify-between"><span className="text-neutral-500">Fit Score:</span><span className="font-bold">{e.fitScore}</span></div>
                                  <div className="flex justify-between"><span className="text-neutral-500">Technical:</span><span>{e.techScore}</span></div>
                                  <div className="flex justify-between"><span className="text-neutral-500">Communication:</span><span>{e.commScore}</span></div>
                                  <div className="flex justify-between"><span className="text-neutral-500">Immigration:</span><span className={e.immigScore < 50 ? 'text-red-600 font-medium' : ''}>{e.immigScore}</span></div>
                                  <div className="flex justify-between"><span className="text-neutral-500">Interviews:</span><span>{e.feedbackCount}</span></div>
                                </div>
                              </div>
                              {/* Actions */}
                              <div>
                                <p className="text-xs font-semibold text-neutral-700 mb-2">Actions</p>
                                <div className="flex flex-wrap gap-2">
                                  <a href={`/score-intelligence?candidate=${submission.candidate_id}`}
                                    className="px-3 py-1.5 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700">Score Profile</a>
                                  <a href="/detailed-feedback"
                                    className="px-3 py-1.5 bg-white text-neutral-600 text-xs rounded-lg border border-neutral-200 hover:bg-neutral-50">View Feedback</a>
                                  {!e.sharedWithSubmission && (
                                    <button className="px-3 py-1.5 bg-emerald-600 text-white text-xs rounded-lg hover:bg-emerald-700">Share with Client</button>
                                  )}
                                </div>
                              </div>
                            </div>
                          </td></tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  /* ─── Kanban View (enhanced) ─── */
  return (
    <div className="p-4 md:p-6 space-y-6 pb-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Submission Pipeline</h1>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            Score-ranked candidates with feedback integration
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setSortByScore(!sortByScore)}
            className={`px-3 py-1.5 text-xs rounded-lg border ${sortByScore ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200'}`}>
            {sortByScore ? 'Sorted by Score' : 'Default Order'}
          </button>
          <button onClick={() => setListView(true)}
            className="px-4 py-2 border border-neutral-200 dark:border-neutral-700 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors text-sm">
            List View
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 overflow-x-auto pb-4">
        {submissionStages.map((stage) => (
          <div key={stage.id} className="flex-shrink-0 w-full md:w-96">
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-neutral-900 dark:text-white">{stage.label}</h3>
                  <span className="text-xs font-bold px-2 py-1 rounded bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300">
                    {submissionsByStage(stage.id).length}
                  </span>
                </div>
              </CardHeader>
              <CardBody className="space-y-3">
                {submissionsByStage(stage.id).map((submission: Submission) => {
                  const e = getEnrichment(submission);
                  return (
                    <div key={submission.id}
                      className={`p-3 rounded-lg ${stage.color} cursor-move hover:shadow-md transition-shadow duration-250`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-sm text-neutral-900 dark:text-white">
                            {submission.candidate.first_name} {submission.candidate.last_name}
                          </p>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${screeningBadgeCls(e.screeningStatus)}`}>
                            {screeningIcon(e.screeningStatus)} {e.screeningStatus === 'not_screened' ? 'not screened' : e.screeningStatus}
                          </span>
                        </div>
                        {/* Fit score badge */}
                        {e.fitScore > 0 && (
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${fitScoreBg(e.fitScore)}`}>
                            {e.fitScore}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                        {submission.requirement.title}
                      </p>

                      {/* Score bar + match */}
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs font-bold text-primary-600 dark:text-primary-400">
                          {submission.match_score}% match
                        </span>
                        {submission.rate_proposed && (
                          <span className="text-xs text-neutral-600 dark:text-neutral-400">
                            ${submission.rate_proposed}
                          </span>
                        )}
                      </div>

                      {/* Enrichment badges */}
                      {e.hasFeedback && (
                        <div className="flex items-center gap-1 mt-2 flex-wrap">
                          {e.recommendation && (
                            <span className={`text-[8px] px-1.5 py-0.5 rounded-full text-white ${recColors[e.recommendation]}`}>
                              {e.recommendation.replace(/_/g, ' ')}
                            </span>
                          )}
                          {e.skills.slice(0, 2).map(sk => (
                            <span key={sk.name} className={`text-[8px] px-1.5 py-0.5 rounded ${sk.score >= 80 ? 'bg-emerald-50 text-emerald-700' : 'bg-neutral-200 text-neutral-600'}`}>
                              {sk.name} {sk.score}
                            </span>
                          ))}
                          {e.riskFactors.length > 0 && (
                            <span className="text-[8px] px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded">
                              {e.riskFactors.length} risk(s)
                            </span>
                          )}
                          {e.sharedWithSubmission && (
                            <span className="text-[8px] px-1 py-0.5 bg-violet-100 text-violet-600 rounded">shared</span>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
                {submissionsByStage(stage.id).length === 0 && (
                  <p className="text-xs text-neutral-400 dark:text-neutral-500 text-center py-8">No submissions</p>
                )}
              </CardBody>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
};
