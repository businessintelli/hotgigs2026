import React, { useState } from 'react';

/* ─── helpers ─── */
const scoreBg = (s: number) => s >= 80 ? 'bg-emerald-100 text-emerald-800' : s >= 60 ? 'bg-blue-100 text-blue-800' : s >= 40 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';
const recColors: Record<string, string> = { strong_hire: 'bg-emerald-600', hire: 'bg-emerald-500', maybe: 'bg-amber-500', no_hire: 'bg-red-500', strong_no_hire: 'bg-red-700' };

/* ─── types ─── */
interface Question {
  id: number; question_text: string; category: string; question_type: string;
  technology: string | null; skill_tag: string | null; difficulty_level: string | null;
  options?: string[]; scoring_guide?: Record<string, string>;
  weight: number; is_required: boolean; is_eliminatory: boolean; min_passing_score: number | null;
}

/* ─── mock questions ─── */
const questions: Question[] = [
  { id: 1, question_text: 'Rate the candidate\'s proficiency in Python programming', category: 'technical', question_type: 'rating_1_5', technology: 'Python', skill_tag: 'backend', difficulty_level: 'medium', scoring_guide: { '1': 'No knowledge', '2': 'Basic syntax', '3': 'Working knowledge', '4': 'Advanced (decorators, generators, async)', '5': 'Expert (metaclasses, C extensions)' }, weight: 1.5, is_required: true, is_eliminatory: false, min_passing_score: 3 },
  { id: 2, question_text: 'Evaluate SQL and database design skills', category: 'technical', question_type: 'rating_1_5', technology: 'SQL', skill_tag: 'database', difficulty_level: 'medium', scoring_guide: { '1': 'Cannot write basic queries', '2': 'Simple SELECT/INSERT', '3': 'JOINs, subqueries, indexing', '4': 'Query optimization, stored procedures', '5': 'Database architecture, sharding' }, weight: 1.3, is_required: true, is_eliminatory: false, min_passing_score: 3 },
  { id: 3, question_text: 'Rate experience with React/frontend frameworks', category: 'framework', question_type: 'rating_1_5', technology: 'React', skill_tag: 'frontend', difficulty_level: 'medium', scoring_guide: { '1': 'No experience', '2': 'Basic components', '3': 'Hooks, state mgmt', '4': 'Performance, testing', '5': 'Architecture, advanced patterns' }, weight: 1.2, is_required: false, is_eliminatory: false, min_passing_score: null },
  { id: 4, question_text: 'Evaluate AWS/cloud infrastructure knowledge', category: 'technical', question_type: 'rating_1_5', technology: 'AWS', skill_tag: 'devops', difficulty_level: 'hard', scoring_guide: { '1': 'No cloud experience', '2': 'Basic S3/EC2', '3': 'Lambda, RDS, VPC', '4': 'Multi-region, cost optimization', '5': 'Solutions architect level' }, weight: 1.2, is_required: false, is_eliminatory: false, min_passing_score: null },
  { id: 5, question_text: 'System design: Design a URL shortener (or similar)', category: 'system_design', question_type: 'rating_1_10', technology: null, skill_tag: 'architecture', difficulty_level: 'hard', scoring_guide: { '1-3': 'Incomplete', '4-6': 'Basic with gaps', '7-8': 'Solid with scalability', '9-10': 'Exceptional' }, weight: 2.0, is_required: false, is_eliminatory: false, min_passing_score: 5 },
  { id: 20, question_text: 'Current work authorization status?', category: 'work_authorization', question_type: 'select', technology: null, skill_tag: 'visa', difficulty_level: null, options: ['US Citizen', 'Green Card', 'H1B', 'H1B Transfer', 'OPT', 'CPT', 'L1', 'TN', 'EAD', 'Requires Sponsorship', 'Other'], weight: 1.0, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 22, question_text: 'Willing to transfer H1B if currently employed elsewhere?', category: 'immigration', question_type: 'yes_no', technology: null, skill_tag: 'visa', difficulty_level: null, weight: 0.8, is_required: false, is_eliminatory: false, min_passing_score: null },
  { id: 24, question_text: 'Rate confidence in candidate\'s immigration timeline and stability', category: 'immigration', question_type: 'rating_1_5', technology: null, skill_tag: 'visa', scoring_guide: { '1': 'High risk — expiring', '2': 'Moderate risk — needs transfer', '3': 'Manageable', '4': 'Stable long-term', '5': 'No risk — citizen/GC' }, difficulty_level: null, weight: 1.0, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 30, question_text: 'Where is the candidate currently located?', category: 'location', question_type: 'free_text', technology: null, skill_tag: 'location', difficulty_level: null, weight: 0.8, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 31, question_text: 'Willing to relocate if required?', category: 'relocation', question_type: 'select', technology: null, skill_tag: 'location', difficulty_level: null, options: ['Yes — anywhere', 'Yes — within same state', 'Yes — within region', 'Only for the right opportunity', 'No — remote only', 'Already local'], weight: 0.8, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 33, question_text: 'Preferred work arrangement?', category: 'availability', question_type: 'select', technology: null, skill_tag: 'availability', difficulty_level: null, options: ['On-site only', 'Hybrid (2-3 days)', 'Hybrid (1 day)', 'Remote only', 'Flexible'], weight: 0.6, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 40, question_text: 'When available to start?', category: 'availability', question_type: 'select', technology: null, skill_tag: 'availability', difficulty_level: null, options: ['Immediately', '1 week', '2 weeks', '30 days', '60+ days'], weight: 0.8, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 41, question_text: 'Expected hourly rate ($/hr)?', category: 'compensation', question_type: 'numeric', technology: null, skill_tag: 'compensation', difficulty_level: null, weight: 1.0, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 50, question_text: 'Rate English communication skills', category: 'communication', question_type: 'rating_1_5', technology: null, skill_tag: 'soft_skills', scoring_guide: { '1': 'Significant barrier', '2': 'Basic, some difficulty', '3': 'Functional', '4': 'Good — clear and articulate', '5': 'Excellent — native level' }, difficulty_level: null, weight: 1.2, is_required: true, is_eliminatory: false, min_passing_score: 3 },
  { id: 60, question_text: 'Years of relevant experience in required stack', category: 'project_experience', question_type: 'numeric', technology: null, skill_tag: 'experience', difficulty_level: null, weight: 1.0, is_required: true, is_eliminatory: false, min_passing_score: null },
  { id: 61, question_text: 'Rate depth of hands-on project experience', category: 'project_experience', question_type: 'rating_1_5', technology: null, skill_tag: 'experience', scoring_guide: { '1': 'No real projects', '2': 'Academic only', '3': '1-2 professional projects', '4': 'Multiple enterprise projects', '5': 'Led architecture of major systems' }, difficulty_level: null, weight: 1.3, is_required: true, is_eliminatory: false, min_passing_score: 2 },
];

/* ─── mock feedback sessions ─── */
const feedbackSessions = [
  { id: 1, candidate_name: 'Rajesh Kumar', requirement_title: 'Senior Python Developer — TechCorp', feedback_source: 'recruiter', overall_rating: 4.2, overall_recommendation: 'hire', technical_score: 85, communication_score: 80, immigration_score: 65, job_fit_score: 82, visibility: 'internal_only', shared_with_submission: false, completed_at: '2026-03-10', share_technical_scores: true, share_immigration_details: false, share_detailed_notes: false },
  { id: 2, candidate_name: 'Emily Chen', requirement_title: 'Senior Python Developer — TechCorp', feedback_source: 'ai_bot', overall_rating: 4.5, overall_recommendation: 'strong_hire', technical_score: 92, communication_score: 90, immigration_score: 100, job_fit_score: 91, visibility: 'share_with_client', shared_with_submission: true, completed_at: '2026-03-11', share_technical_scores: true, share_immigration_details: true, share_detailed_notes: true },
  { id: 3, candidate_name: 'Marcus Johnson', requirement_title: 'Full Stack Developer — MedFirst', feedback_source: 'recruiter', overall_rating: 3.6, overall_recommendation: 'maybe', technical_score: 68, communication_score: 72, immigration_score: 40, job_fit_score: 58, visibility: 'internal_only', shared_with_submission: false, completed_at: '2026-03-12', share_technical_scores: true, share_immigration_details: false, share_detailed_notes: false },
  { id: 4, candidate_name: 'Rajesh Kumar', requirement_title: 'Backend Engineer — DataFlow Analytics', feedback_source: 'ai_bot', overall_rating: 4.4, overall_recommendation: 'hire', technical_score: 88, communication_score: 82, immigration_score: 65, job_fit_score: 85, visibility: 'share_with_client', shared_with_submission: true, completed_at: '2026-03-14', share_technical_scores: true, share_immigration_details: false, share_detailed_notes: true },
];

const categoryLabels: Record<string, string> = {
  technical: 'Technical Skills', framework: 'Frameworks', system_design: 'System Design', coding: 'Coding',
  work_authorization: 'Work Authorization', immigration: 'Immigration', location: 'Location',
  relocation: 'Relocation', availability: 'Availability', compensation: 'Compensation',
  communication: 'Communication', culture_fit: 'Culture Fit', project_experience: 'Project Experience',
};

const categoryGroups = [
  { key: 'tech', label: 'Technical Assessment', categories: ['technical', 'framework', 'system_design', 'coding'] },
  { key: 'immigration', label: 'Immigration & Work Authorization', categories: ['work_authorization', 'immigration'] },
  { key: 'logistics', label: 'Location, Availability & Compensation', categories: ['location', 'relocation', 'availability', 'compensation'] },
  { key: 'soft', label: 'Communication & Culture', categories: ['communication', 'culture_fit'] },
  { key: 'exp', label: 'Experience & Projects', categories: ['project_experience'] },
];

const tabs = ['Collect Feedback', 'All Sessions', 'Visibility Control'] as const;
type Tab = typeof tabs[number];

export const DetailedFeedbackCollector: React.FC = () => {
  const [tab, setTab] = useState<Tab>('Collect Feedback');
  const [answers, setAnswers] = useState<Record<number, { rating?: number; text?: string; choice?: string; numeric?: number; notes?: string }>>({});
  const [recommendation, setRecommendation] = useState('');
  const [summaryNotes, setSummaryNotes] = useState('');
  const [feedbackSource, setFeedbackSource] = useState('recruiter');
  const [expandedGroup, setExpandedGroup] = useState<string | null>('tech');
  const [expandedSession, setExpandedSession] = useState<number | null>(null);

  const updateAnswer = (qId: number, field: string, value: any) => {
    setAnswers(prev => ({ ...prev, [qId]: { ...prev[qId], [field]: value } }));
  };

  const getQuestionsForGroup = (categories: string[]) =>
    questions.filter(q => categories.includes(q.category));

  const computeScore = () => {
    let totalWeightedScore = 0; let totalWeight = 0;
    questions.forEach(q => {
      const a = answers[q.id];
      if (!a) return;
      let normalized = 0;
      if (q.question_type === 'rating_1_5' && a.rating) { normalized = (a.rating / 5) * 100; }
      else if (q.question_type === 'rating_1_10' && a.rating) { normalized = (a.rating / 10) * 100; }
      else return;
      totalWeightedScore += normalized * q.weight;
      totalWeight += q.weight;
    });
    return totalWeight > 0 ? Math.round(totalWeightedScore / totalWeight) : 0;
  };

  const answeredCount = Object.keys(answers).filter(k => {
    const a = answers[Number(k)];
    return a && (a.rating || a.text || a.choice || a.numeric !== undefined);
  }).length;
  const requiredCount = questions.filter(q => q.is_required).length;
  const answeredRequired = questions.filter(q => q.is_required).filter(q => {
    const a = answers[q.id];
    return a && (a.rating || a.text || a.choice || a.numeric !== undefined);
  }).length;

  /* ─── Question renderer ─── */
  const renderQuestion = (q: Question) => {
    const a = answers[q.id] || {};
    return (
      <div key={q.id} className={`p-4 rounded-lg border ${q.is_eliminatory ? 'border-red-200 bg-red-50' : 'border-neutral-200 bg-white'}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              {q.is_required && <span className="text-red-500 text-xs font-bold">*</span>}
              <p className="text-sm font-medium text-neutral-900">{q.question_text}</p>
            </div>
            <div className="flex items-center gap-2 mt-1">
              {q.technology && <span className="text-[10px] px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">{q.technology}</span>}
              {q.difficulty_level && <span className="text-[10px] px-1.5 py-0.5 bg-neutral-100 text-neutral-600 rounded">{q.difficulty_level}</span>}
              <span className="text-[10px] text-neutral-400">Weight: {q.weight}x</span>
              {q.min_passing_score && <span className="text-[10px] text-orange-600">Min pass: {q.min_passing_score}</span>}
              {q.is_eliminatory && <span className="text-[10px] px-1.5 py-0.5 bg-red-600 text-white rounded">ELIMINATORY</span>}
            </div>
          </div>
        </div>

        <div className="mt-3">
          {(q.question_type === 'rating_1_5') && (
            <div>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map(r => (
                  <button key={r} onClick={() => updateAnswer(q.id, 'rating', r)}
                    className={`w-10 h-10 rounded-lg border text-sm font-bold transition-all ${a.rating === r ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200 hover:border-violet-300'}`}>
                    {r}
                  </button>
                ))}
              </div>
              {q.scoring_guide && (
                <div className="mt-2 grid grid-cols-5 gap-1">
                  {Object.entries(q.scoring_guide).map(([k, v]) => (
                    <p key={k} className="text-[9px] text-neutral-400 text-center">{v}</p>
                  ))}
                </div>
              )}
            </div>
          )}
          {(q.question_type === 'rating_1_10') && (
            <div>
              <div className="flex gap-1 flex-wrap">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(r => (
                  <button key={r} onClick={() => updateAnswer(q.id, 'rating', r)}
                    className={`w-8 h-8 rounded-lg border text-xs font-bold ${a.rating === r ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200 hover:border-violet-300'}`}>
                    {r}
                  </button>
                ))}
              </div>
            </div>
          )}
          {q.question_type === 'select' && (
            <select value={a.choice || ''} onChange={e => updateAnswer(q.id, 'choice', e.target.value)}
              className="w-full max-w-md px-3 py-2 border border-neutral-200 rounded-lg text-sm bg-white">
              <option value="">Select...</option>
              {q.options?.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          )}
          {q.question_type === 'yes_no' && (
            <div className="flex gap-2">
              {['Yes', 'No'].map(v => (
                <button key={v} onClick={() => updateAnswer(q.id, 'choice', v)}
                  className={`px-4 py-2 rounded-lg border text-sm ${a.choice === v ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200 hover:border-violet-300'}`}>
                  {v}
                </button>
              ))}
            </div>
          )}
          {q.question_type === 'free_text' && (
            <input type="text" value={a.text || ''} onChange={e => updateAnswer(q.id, 'text', e.target.value)}
              className="w-full max-w-md px-3 py-2 border border-neutral-200 rounded-lg text-sm" placeholder="Enter answer..." />
          )}
          {q.question_type === 'numeric' && (
            <input type="number" value={a.numeric ?? ''} onChange={e => updateAnswer(q.id, 'numeric', parseFloat(e.target.value) || undefined)}
              className="w-40 px-3 py-2 border border-neutral-200 rounded-lg text-sm" placeholder="Enter number..." />
          )}
          {q.question_type === 'date' && (
            <input type="date" value={a.text || ''} onChange={e => updateAnswer(q.id, 'text', e.target.value)}
              className="w-48 px-3 py-2 border border-neutral-200 rounded-lg text-sm" />
          )}
        </div>

        <div className="mt-2">
          <input type="text" value={a.notes || ''} onChange={e => updateAnswer(q.id, 'notes', e.target.value)}
            className="w-full px-3 py-1.5 border border-neutral-100 rounded text-xs text-neutral-600" placeholder="Evaluator notes (optional)..." />
        </div>
      </div>
    );
  };

  /* ─── Collect Feedback Tab ─── */
  const CollectTab = () => (
    <div className="space-y-4">
      {/* Top info bar */}
      <div className="bg-white rounded-xl border border-neutral-200 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <label className="text-xs text-neutral-500">Feedback Source</label>
            <select value={feedbackSource} onChange={e => setFeedbackSource(e.target.value)}
              className="ml-2 px-2 py-1 border border-neutral-200 rounded text-xs bg-white">
              <option value="recruiter">Recruiter</option>
              <option value="ai_bot">AI Bot</option>
              <option value="hiring_manager">Hiring Manager</option>
              <option value="technical_panel">Technical Panel</option>
              <option value="client">Client</option>
            </select>
          </div>
          <div className="text-xs text-neutral-500">
            Progress: <span className="font-bold text-violet-700">{answeredCount}/{questions.length}</span> answered
            (<span className="font-bold text-orange-600">{answeredRequired}/{requiredCount}</span> required)
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-xs text-neutral-500">Computed Score</p>
            <p className="text-xl font-bold text-violet-700">{computeScore()}<span className="text-sm text-neutral-400">/100</span></p>
          </div>
        </div>
      </div>

      {/* Question groups — accordion */}
      {categoryGroups.map(group => {
        const groupQuestions = getQuestionsForGroup(group.categories);
        if (groupQuestions.length === 0) return null;
        const isExpanded = expandedGroup === group.key;
        const groupAnswered = groupQuestions.filter(q => {
          const a = answers[q.id];
          return a && (a.rating || a.text || a.choice || a.numeric !== undefined);
        }).length;

        return (
          <div key={group.key} className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
            <button onClick={() => setExpandedGroup(isExpanded ? null : group.key)}
              className="w-full flex items-center justify-between p-4 hover:bg-neutral-50 transition-colors text-left">
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${groupAnswered === groupQuestions.length ? 'bg-emerald-500' : groupAnswered > 0 ? 'bg-amber-500' : 'bg-neutral-300'}`} />
                <h3 className="text-sm font-semibold text-neutral-900">{group.label}</h3>
                <span className="text-xs text-neutral-400">{groupAnswered}/{groupQuestions.length}</span>
              </div>
              <span className="text-neutral-400 text-sm">{isExpanded ? '▼' : '▶'}</span>
            </button>
            {isExpanded && (
              <div className="p-4 pt-0 space-y-3">
                {groupQuestions.map(renderQuestion)}
              </div>
            )}
          </div>
        );
      })}

      {/* Overall assessment */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5">
        <h3 className="text-sm font-semibold text-neutral-900 mb-4">Overall Assessment</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-neutral-700 mb-2 block">Recommendation</label>
            <div className="flex gap-2 flex-wrap">
              {['strong_hire', 'hire', 'maybe', 'no_hire', 'strong_no_hire'].map(r => (
                <button key={r} onClick={() => setRecommendation(r)}
                  className={`px-3 py-1.5 rounded-lg text-xs border ${recommendation === r ? `${recColors[r]} text-white border-transparent` : 'bg-white text-neutral-600 border-neutral-200 hover:border-neutral-300'}`}>
                  {r.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-neutral-700 mb-2 block">Summary Notes</label>
            <textarea value={summaryNotes} onChange={e => setSummaryNotes(e.target.value)}
              rows={3} className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm resize-none" placeholder="Overall assessment notes..." />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-4">
          <button className="px-4 py-2 text-sm border border-neutral-200 rounded-lg hover:bg-neutral-50">Save Draft</button>
          <button className="px-4 py-2 text-sm bg-violet-600 text-white rounded-lg hover:bg-violet-700"
            disabled={answeredRequired < requiredCount}>
            Complete & Compute Scores
          </button>
        </div>
      </div>
    </div>
  );

  /* ─── All Sessions Tab ─── */
  const SessionsTab = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-neutral-50 border-b border-neutral-200">
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Candidate</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Job</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Source</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Rating</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Tech</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Comm</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Immig</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Job Fit</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Rec</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Shared</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {feedbackSessions.map(s => (
              <React.Fragment key={s.id}>
                <tr className="border-b border-neutral-100 hover:bg-neutral-50 cursor-pointer" onClick={() => setExpandedSession(expandedSession === s.id ? null : s.id)}>
                  <td className="py-3 px-4 font-medium text-neutral-900">{s.candidate_name}</td>
                  <td className="py-3 px-4 text-neutral-600 text-xs">{s.requirement_title}</td>
                  <td className="py-3 px-4">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${s.feedback_source === 'ai_bot' ? 'bg-violet-100 text-violet-700' : 'bg-blue-100 text-blue-700'}`}>
                      {s.feedback_source === 'ai_bot' ? 'AI Bot' : 'Recruiter'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-neutral-900">{s.overall_rating}</td>
                  <td className="py-3 px-4 text-center"><span className={`text-xs px-2 py-0.5 rounded-full ${scoreBg(s.technical_score)}`}>{s.technical_score}</span></td>
                  <td className="py-3 px-4 text-center"><span className={`text-xs px-2 py-0.5 rounded-full ${scoreBg(s.communication_score)}`}>{s.communication_score}</span></td>
                  <td className="py-3 px-4 text-center"><span className={`text-xs px-2 py-0.5 rounded-full ${scoreBg(s.immigration_score)}`}>{s.immigration_score}</span></td>
                  <td className="py-3 px-4 text-center"><span className={`text-xs px-2 py-0.5 rounded-full ${scoreBg(s.job_fit_score)}`}>{s.job_fit_score}</span></td>
                  <td className="py-3 px-4">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full text-white ${recColors[s.overall_recommendation] || 'bg-neutral-400'}`}>
                      {s.overall_recommendation.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {s.shared_with_submission ? <span className="text-emerald-600 text-xs font-bold">✓</span> : <span className="text-neutral-300 text-xs">—</span>}
                  </td>
                  <td className="py-3 px-4 text-xs text-neutral-500">{s.completed_at}</td>
                </tr>
                {expandedSession === s.id && (
                  <tr><td colSpan={11} className="bg-neutral-50 p-4">
                    <div className="grid grid-cols-3 gap-4 text-xs">
                      <div>
                        <p className="font-semibold text-neutral-700 mb-2">Score Breakdown</p>
                        <div className="space-y-1">
                          {[
                            { l: 'Technical', v: s.technical_score }, { l: 'Communication', v: s.communication_score },
                            { l: 'Immigration', v: s.immigration_score }, { l: 'Job Fit', v: s.job_fit_score },
                          ].map(x => (
                            <div key={x.l} className="flex items-center gap-2">
                              <span className="w-20 text-neutral-500">{x.l}</span>
                              <div className="flex-1 h-2 bg-neutral-200 rounded-full"><div className="h-2 bg-violet-500 rounded-full" style={{ width: `${x.v}%` }} /></div>
                              <span className="w-8 text-right font-medium">{x.v}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="font-semibold text-neutral-700 mb-2">Visibility Settings</p>
                        <div className="space-y-1">
                          <div className="flex justify-between"><span className="text-neutral-500">Visibility:</span><span>{s.visibility.replace(/_/g, ' ')}</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Share tech scores:</span><span className={s.share_technical_scores ? 'text-emerald-600' : 'text-neutral-400'}>{s.share_technical_scores ? 'Yes' : 'No'}</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Share immigration:</span><span className={s.share_immigration_details ? 'text-emerald-600' : 'text-neutral-400'}>{s.share_immigration_details ? 'Yes' : 'No'}</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Share notes:</span><span className={s.share_detailed_notes ? 'text-emerald-600' : 'text-neutral-400'}>{s.share_detailed_notes ? 'Yes' : 'No'}</span></div>
                        </div>
                      </div>
                      <div>
                        <p className="font-semibold text-neutral-700 mb-2">Actions</p>
                        <div className="flex flex-wrap gap-2">
                          <button className="px-3 py-1 bg-violet-600 text-white rounded text-xs">View Full Feedback</button>
                          <button className="px-3 py-1 bg-white border border-neutral-200 rounded text-xs">Edit Visibility</button>
                          {!s.shared_with_submission && <button className="px-3 py-1 bg-emerald-600 text-white rounded text-xs">Attach to Submission</button>}
                        </div>
                      </div>
                    </div>
                  </td></tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  /* ─── Visibility Control Tab ─── */
  const VisibilityTab = () => (
    <div className="space-y-6">
      <div className="bg-violet-50 rounded-xl border border-violet-200 p-4">
        <h3 className="text-sm font-semibold text-violet-900 mb-1">Recruiter Visibility Controls</h3>
        <p className="text-xs text-violet-700">Control what feedback information is shared when attaching to candidate submissions. Immigration details, compensation, and detailed notes are hidden by default — you decide what the client or supplier sees.</p>
      </div>

      {feedbackSessions.map(s => (
        <div key={s.id} className="bg-white rounded-xl border border-neutral-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-semibold text-neutral-900">{s.candidate_name}</h4>
              <p className="text-xs text-neutral-500">{s.requirement_title} — {s.completed_at}</p>
            </div>
            <span className={`text-[10px] px-2 py-0.5 rounded-full text-white ${recColors[s.overall_recommendation]}`}>{s.overall_recommendation.replace(/_/g, ' ')}</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Share Technical Scores', key: 'share_technical_scores', current: s.share_technical_scores, desc: 'Python, SQL, AWS scores visible to external party' },
              { label: 'Share Immigration Details', key: 'share_immigration_details', current: s.share_immigration_details, desc: 'Visa status, immigration risk, sponsorship needs' },
              { label: 'Share Compensation Info', key: 'share_compensation_details', current: false, desc: 'Expected rate, negotiability, budget comparison' },
              { label: 'Share Detailed Notes', key: 'share_detailed_notes', current: s.share_detailed_notes, desc: 'Summary notes, concerns, evaluator comments' },
            ].map(toggle => (
              <div key={toggle.key} className={`p-3 rounded-lg border ${toggle.current ? 'border-emerald-200 bg-emerald-50' : 'border-neutral-200 bg-neutral-50'}`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-neutral-900">{toggle.label}</span>
                  <div className={`w-8 h-4 rounded-full ${toggle.current ? 'bg-emerald-500' : 'bg-neutral-300'} flex items-center`}>
                    <div className={`w-3 h-3 rounded-full bg-white transition-all ${toggle.current ? 'ml-4' : 'ml-0.5'}`} />
                  </div>
                </div>
                <p className="text-[10px] text-neutral-500">{toggle.desc}</p>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between mt-4 pt-3 border-t border-neutral-100">
            <div className="flex items-center gap-2">
              <span className="text-xs text-neutral-500">Visibility:</span>
              <select defaultValue={s.visibility} className="px-2 py-1 border border-neutral-200 rounded text-xs bg-white">
                <option value="internal_only">Internal Only</option>
                <option value="share_with_client">Share with Client</option>
                <option value="share_with_supplier">Share with Supplier</option>
                <option value="public">Public</option>
              </select>
            </div>
            <div className="flex gap-2">
              {s.shared_with_submission ? (
                <span className="text-xs text-emerald-600 font-medium">Attached to submission ✓</span>
              ) : (
                <button className="px-3 py-1.5 bg-emerald-600 text-white text-xs rounded-lg hover:bg-emerald-700">Attach to Submission</button>
              )}
              <button className="px-3 py-1.5 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700">Save Settings</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Detailed Interview Feedback</h1>
        <p className="text-neutral-500 mt-1">Collect structured feedback with technical and non-technical questions. Control what's shared during submission.</p>
      </div>

      <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm rounded-md transition-all ${tab === t ? 'bg-white text-neutral-900 shadow-sm font-medium' : 'text-neutral-600 hover:text-neutral-900'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Collect Feedback' && <CollectTab />}
      {tab === 'All Sessions' && <SessionsTab />}
      {tab === 'Visibility Control' && <VisibilityTab />}
    </div>
  );
};

export default DetailedFeedbackCollector;
