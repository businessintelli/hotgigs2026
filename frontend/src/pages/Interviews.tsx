import React, { useState } from 'react';

/* ─── helpers ─── */
const scoreBg = (s: number) => s >= 80 ? 'bg-emerald-100 text-emerald-800' : s >= 60 ? 'bg-blue-100 text-blue-800' : s >= 40 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';
const statusColors: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700', in_progress: 'bg-violet-100 text-violet-700',
  completed: 'bg-emerald-100 text-emerald-700', cancelled: 'bg-neutral-100 text-neutral-600',
  no_show: 'bg-red-100 text-red-700',
};
const typeColors: Record<string, string> = {
  phone_screen: 'bg-amber-100 text-amber-700', ai_chat: 'bg-violet-100 text-violet-700',
  video_customer: 'bg-blue-100 text-blue-700', technical: 'bg-emerald-100 text-emerald-700',
  onsite: 'bg-rose-100 text-rose-700', panel: 'bg-indigo-100 text-indigo-700',
};
const recColors: Record<string, string> = { strong_hire: 'bg-emerald-600', hire: 'bg-emerald-500', maybe: 'bg-amber-500', no_hire: 'bg-red-500', strong_no_hire: 'bg-red-700' };

/* ─── screening status enrichment (from /screening-feedback API) ─── */
const screeningLookup: Record<number, { status: string; score: number; date: string }> = {
  1: { status: 'screened', score: 78, date: '2026-03-10' },     // Rajesh Kumar
  2: { status: 'shortlisted', score: 92, date: '2026-03-10' },  // Emily Chen
  3: { status: 'hold', score: 58, date: '2026-03-11' },         // Marcus Johnson
  4: { status: 'pending', score: 0, date: '2026-03-14' },       // Priya Sharma
  5: { status: 'not_screened', score: 0, date: '' },             // Alex Torres
  6: { status: 'not_screened', score: 0, date: '' },             // Nina Patel
};
const screeningBadgeCls = (s: string) => {
  switch (s) {
    case 'shortlisted': return 'bg-emerald-600 text-white';
    case 'screened': return 'bg-emerald-100 text-emerald-800';
    case 'hold': return 'bg-amber-100 text-amber-800';
    case 'rejected': return 'bg-red-100 text-red-800';
    case 'pending': return 'bg-orange-100 text-orange-700';
    default: return 'bg-neutral-100 text-neutral-400';
  }
};
const screeningIcon = (s: string) => {
  switch (s) { case 'shortlisted': return '★'; case 'screened': return '✓'; case 'hold': return '⏸'; case 'rejected': return '✗'; case 'pending': return '…'; default: return ''; }
};

/* ─── mock data ─── */
const mockInterviews = [
  { id: 101, candidate_id: 1, candidate_name: 'Rajesh Kumar', requirement_id: 201, requirement_title: 'Senior Python Developer — TechCorp', interview_type: 'phone_screen', status: 'completed', scheduled_at: '2026-03-10T10:00:00Z', duration_minutes: 45, interviewer: 'Sarah Mitchell', ai_score: 4.2, rating: 4, feedback_submitted: true, feedback_session_id: 1, scores: { technical: 85, communication: 80, immigration: 65, job_fit: 82 }, recommendation: 'hire' },
  { id: 102, candidate_id: 2, candidate_name: 'Emily Chen', requirement_id: 201, requirement_title: 'Senior Python Developer — TechCorp', interview_type: 'ai_chat', status: 'completed', scheduled_at: '2026-03-11T14:00:00Z', duration_minutes: 35, interviewer: 'AI Interview Bot', ai_score: 4.5, rating: 5, feedback_submitted: true, feedback_session_id: 2, scores: { technical: 92, communication: 90, immigration: 100, job_fit: 91 }, recommendation: 'strong_hire' },
  { id: 103, candidate_id: 3, candidate_name: 'Marcus Johnson', requirement_id: 202, requirement_title: 'Full Stack Developer — MedFirst', interview_type: 'phone_screen', status: 'completed', scheduled_at: '2026-03-12T09:00:00Z', duration_minutes: 50, interviewer: 'Tom Richards', ai_score: 3.6, rating: 3, feedback_submitted: true, feedback_session_id: 3, scores: { technical: 68, communication: 72, immigration: 40, job_fit: 58 }, recommendation: 'maybe' },
  { id: 104, candidate_id: 1, candidate_name: 'Rajesh Kumar', requirement_id: 203, requirement_title: 'Backend Engineer — DataFlow Analytics', interview_type: 'ai_chat', status: 'completed', scheduled_at: '2026-03-14T11:00:00Z', duration_minutes: 40, interviewer: 'AI Interview Bot', ai_score: 4.4, rating: 4, feedback_submitted: true, feedback_session_id: 4, scores: { technical: 88, communication: 82, immigration: 65, job_fit: 85 }, recommendation: 'hire' },
  { id: 105, candidate_id: 4, candidate_name: 'Priya Sharma', requirement_id: 201, requirement_title: 'Senior Python Developer — TechCorp', interview_type: 'technical', status: 'scheduled', scheduled_at: '2026-03-16T10:00:00Z', duration_minutes: 60, interviewer: 'Mike Chen', ai_score: null as number | null, rating: null as number | null, feedback_submitted: false, feedback_session_id: null as number | null, scores: null, recommendation: null as string | null },
  { id: 106, candidate_id: 5, candidate_name: 'Alex Torres', requirement_id: 202, requirement_title: 'Full Stack Developer — MedFirst', interview_type: 'video_customer', status: 'scheduled', scheduled_at: '2026-03-16T14:00:00Z', duration_minutes: 45, interviewer: 'Client Panel', ai_score: null, rating: null, feedback_submitted: false, feedback_session_id: null, scores: null, recommendation: null },
  { id: 107, candidate_id: 6, candidate_name: 'Nina Patel', requirement_id: 204, requirement_title: 'Data Engineer — CloudScale', interview_type: 'phone_screen', status: 'in_progress', scheduled_at: '2026-03-15T15:00:00Z', duration_minutes: 30, interviewer: 'Sarah Mitchell', ai_score: null, rating: null, feedback_submitted: false, feedback_session_id: null, scores: null, recommendation: null },
];

/* ── Structured feedback form question categories (inline) ── */
const questionCategories = [
  { key: 'tech', label: 'Technical Assessment', count: 8 },
  { key: 'immigration', label: 'Immigration & Work Auth', count: 5 },
  { key: 'logistics', label: 'Location & Availability', count: 5 },
  { key: 'soft', label: 'Communication & Culture', count: 3 },
  { key: 'exp', label: 'Experience & Projects', count: 2 },
];

const tabs = ['All Interviews', 'Scheduled', 'Completed', 'Give Feedback'] as const;
type Tab = typeof tabs[number];

export const Interviews: React.FC = () => {
  const [tab, setTab] = useState<Tab>('All Interviews');
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [feedbackTarget, setFeedbackTarget] = useState<typeof mockInterviews[0] | null>(null);
  const [feedbackAnswers, setFeedbackAnswers] = useState<Record<number, number>>({});
  const [feedbackRec, setFeedbackRec] = useState('');
  const [feedbackNotes, setFeedbackNotes] = useState('');

  const filteredInterviews = mockInterviews.filter(i => {
    if (tab === 'Scheduled') return i.status === 'scheduled' || i.status === 'in_progress';
    if (tab === 'Completed') return i.status === 'completed';
    if (statusFilter !== 'all') return i.status === statusFilter;
    return true;
  });

  const openFeedbackForm = (interview: typeof mockInterviews[0]) => {
    setFeedbackTarget(interview);
    setFeedbackAnswers({});
    setFeedbackRec('');
    setFeedbackNotes('');
    setTab('Give Feedback');
  };

  /* ─── Interview List ─── */
  const InterviewList = () => (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {['all', 'scheduled', 'in_progress', 'completed', 'cancelled'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 text-xs rounded-full border ${statusFilter === s ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50'}`}>
              {s === 'all' ? 'All' : s.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
        <div className="text-xs text-neutral-500">
          {filteredInterviews.length} interview{filteredInterviews.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: 'Total', value: mockInterviews.length, color: 'text-neutral-900' },
          { label: 'Scheduled', value: mockInterviews.filter(i => i.status === 'scheduled').length, color: 'text-blue-700' },
          { label: 'In Progress', value: mockInterviews.filter(i => i.status === 'in_progress').length, color: 'text-violet-700' },
          { label: 'Completed', value: mockInterviews.filter(i => i.status === 'completed').length, color: 'text-emerald-700' },
          { label: 'Feedback Pending', value: mockInterviews.filter(i => i.status === 'completed' && !i.feedback_submitted).length, color: 'text-orange-700' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-neutral-200 p-3 text-center">
            <p className={`text-xl font-bold ${k.color}`}>{k.value}</p>
            <p className="text-[10px] text-neutral-500 uppercase">{k.label}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-neutral-50 border-b border-neutral-200">
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Candidate</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Job</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Type</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Interviewer</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Scheduled</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Score</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Screening</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Status</th>
              <th className="text-center py-3 px-4 text-xs text-neutral-500 font-medium">Feedback</th>
              <th className="text-left py-3 px-4 text-xs text-neutral-500 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredInterviews.map(i => (
              <React.Fragment key={i.id}>
                <tr className="border-b border-neutral-100 hover:bg-neutral-50 cursor-pointer" onClick={() => setExpandedId(expandedId === i.id ? null : i.id)}>
                  <td className="py-3 px-4">
                    <p className="font-medium text-neutral-900">
                      {i.candidate_name}
                      {(() => { const sc = screeningLookup[i.candidate_id]; return sc ? (
                        <span className={`ml-1.5 text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${screeningBadgeCls(sc.status)}`}>
                          {screeningIcon(sc.status)} {sc.status === 'not_screened' ? 'not screened' : sc.status}
                        </span>
                      ) : null; })()}
                    </p>
                    <p className="text-[10px] text-neutral-400">ID: {i.candidate_id}</p>
                  </td>
                  <td className="py-3 px-4 text-xs text-neutral-600 max-w-[200px] truncate">{i.requirement_title}</td>
                  <td className="py-3 px-4">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${typeColors[i.interview_type] || 'bg-neutral-100 text-neutral-700'}`}>
                      {i.interview_type.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-xs text-neutral-700">{i.interviewer}</td>
                  <td className="py-3 px-4 text-xs text-neutral-500">{i.scheduled_at.split('T')[0]}</td>
                  <td className="py-3 px-4 text-center">
                    {i.ai_score ? (
                      <span className="text-sm font-bold text-violet-700">{i.ai_score}</span>
                    ) : <span className="text-neutral-300">—</span>}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {(() => { const sc = screeningLookup[i.candidate_id]; if (!sc || sc.status === 'not_screened') return <a href="/screening-feedback" className="text-[10px] text-violet-600 hover:underline">Screen</a>; return (
                      <div className="flex flex-col items-center gap-0.5">
                        {sc.score > 0 && <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${scoreBg(sc.score)}`}>{sc.score}</span>}
                        {sc.status === 'pending' && <span className="text-[9px] text-orange-600">draft</span>}
                      </div>
                    ); })()}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${statusColors[i.status]}`}>{i.status.replace(/_/g, ' ')}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {i.feedback_submitted ? (
                      <span className="text-emerald-600 text-xs font-bold">✓</span>
                    ) : i.status === 'completed' ? (
                      <span className="text-orange-500 text-xs font-bold">!</span>
                    ) : (
                      <span className="text-neutral-300">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {(i.status === 'completed' || i.status === 'in_progress') && !i.feedback_submitted ? (
                      <button onClick={e => { e.stopPropagation(); openFeedbackForm(i); }}
                        className="px-3 py-1 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700">
                        Give Feedback
                      </button>
                    ) : i.feedback_submitted ? (
                      <button onClick={e => { e.stopPropagation(); setExpandedId(i.id); }}
                        className="px-3 py-1 bg-white text-neutral-600 text-xs rounded-lg border border-neutral-200 hover:bg-neutral-50">
                        View Feedback
                      </button>
                    ) : null}
                  </td>
                </tr>

                {/* Expanded detail row */}
                {expandedId === i.id && (
                  <tr><td colSpan={10} className="bg-neutral-50 p-5">
                    <div className="grid grid-cols-4 gap-6">
                      {/* Interview Details */}
                      <div>
                        <p className="text-xs font-semibold text-neutral-700 mb-2">Interview Details</p>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between"><span className="text-neutral-500">Type:</span><span>{i.interview_type.replace(/_/g, ' ')}</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Duration:</span><span>{i.duration_minutes} min</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Interviewer:</span><span>{i.interviewer}</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Candidate ID:</span><span>{i.candidate_id}</span></div>
                          <div className="flex justify-between"><span className="text-neutral-500">Job ID:</span><span>{i.requirement_id}</span></div>
                        </div>
                      </div>

                      {/* Score Breakdown */}
                      {i.scores ? (
                        <div>
                          <p className="text-xs font-semibold text-neutral-700 mb-2">Score Breakdown</p>
                          <div className="space-y-2">
                            {Object.entries(i.scores).map(([k, v]) => (
                              <div key={k} className="flex items-center gap-2">
                                <span className="text-[10px] w-20 text-neutral-500 capitalize">{k.replace(/_/g, ' ')}</span>
                                <div className="flex-1 h-2 bg-neutral-200 rounded-full">
                                  <div className={`h-2 rounded-full ${v >= 80 ? 'bg-emerald-500' : v >= 60 ? 'bg-blue-500' : v >= 40 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${v}%` }} />
                                </div>
                                <span className="text-xs font-medium w-8 text-right">{v}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div><p className="text-xs text-neutral-400">No scores yet — interview not completed</p></div>
                      )}

                      {/* Recommendation */}
                      <div>
                        <p className="text-xs font-semibold text-neutral-700 mb-2">Recommendation</p>
                        {i.recommendation ? (
                          <span className={`text-xs px-3 py-1 rounded-full text-white ${recColors[i.recommendation]}`}>
                            {i.recommendation.replace(/_/g, ' ')}
                          </span>
                        ) : (
                          <span className="text-xs text-neutral-400">Pending feedback</span>
                        )}
                        {i.ai_score && (
                          <div className="mt-3">
                            <p className="text-[10px] text-neutral-500">Overall Rating</p>
                            <div className="flex items-center gap-1 mt-0.5">
                              {[1, 2, 3, 4, 5].map(s => (
                                <span key={s} className={`text-sm ${(i.rating || 0) >= s ? 'text-amber-400' : 'text-neutral-200'}`}>★</span>
                              ))}
                              <span className="text-xs text-neutral-600 ml-1">{i.rating}/5</span>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div>
                        <p className="text-xs font-semibold text-neutral-700 mb-2">Actions</p>
                        <div className="flex flex-wrap gap-2">
                          {!i.feedback_submitted && (i.status === 'completed' || i.status === 'in_progress') && (
                            <button onClick={() => openFeedbackForm(i)}
                              className="px-3 py-1.5 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700">
                              Give Feedback
                            </button>
                          )}
                          {i.feedback_submitted && (
                            <a href={`/detailed-feedback?session=${i.feedback_session_id}`}
                              className="px-3 py-1.5 bg-white text-violet-600 text-xs rounded-lg border border-violet-200 hover:bg-violet-50">
                              View Full Feedback
                            </a>
                          )}
                          <a href={`/score-intelligence?candidate=${i.candidate_id}`}
                            className="px-3 py-1.5 bg-white text-neutral-600 text-xs rounded-lg border border-neutral-200 hover:bg-neutral-50">
                            Score Profile
                          </a>
                          <a href="/screening-feedback"
                            className="px-3 py-1.5 bg-white text-violet-600 text-xs rounded-lg border border-violet-200 hover:bg-violet-50">
                            Screening
                          </a>
                        </div>
                      </div>
                    </div>
                    {/* Screening info row */}
                    {(() => { const sc = screeningLookup[i.candidate_id]; if (!sc || sc.status === 'not_screened') return null; return (
                      <div className="mt-3 pt-3 border-t border-neutral-200">
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-semibold text-neutral-700">Screening:</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${screeningBadgeCls(sc.status)}`}>
                            {screeningIcon(sc.status)} {sc.status}
                          </span>
                          {sc.score > 0 && <span className={`text-xs font-bold px-2 py-0.5 rounded ${scoreBg(sc.score)}`}>{sc.score}/100</span>}
                          {sc.date && <span className="text-[10px] text-neutral-400">screened {sc.date}</span>}
                          <a href="/screening-feedback" className="text-[10px] text-violet-600 hover:underline ml-auto">View Full Screening</a>
                        </div>
                      </div>
                    ); })()}
                  </td></tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  /* ─── Give Feedback Tab (Inline Structured Form) ─── */
  const GiveFeedbackTab = () => {
    if (!feedbackTarget) {
      // No target selected — show completed interviews without feedback
      const pending = mockInterviews.filter(i => i.status === 'completed' && !i.feedback_submitted);
      const inProgress = mockInterviews.filter(i => i.status === 'in_progress');
      const eligible = [...inProgress, ...pending];

      return (
        <div className="space-y-4">
          <div className="bg-violet-50 rounded-xl border border-violet-200 p-4">
            <p className="text-sm text-violet-900 font-medium">Select an interview to provide structured feedback</p>
            <p className="text-xs text-violet-700 mt-1">Choose from completed or in-progress interviews below, or click "Give Feedback" on any interview row.</p>
          </div>

          {eligible.length === 0 ? (
            <div className="bg-white rounded-xl border border-neutral-200 p-8 text-center text-neutral-500">
              All interviews have feedback submitted. Well done!
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {eligible.map(i => (
                <button key={i.id} onClick={() => openFeedbackForm(i)}
                  className="text-left bg-white rounded-xl border border-neutral-200 p-4 hover:border-violet-400 hover:shadow-md transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${statusColors[i.status]}`}>{i.status.replace(/_/g, ' ')}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${typeColors[i.interview_type]}`}>{i.interview_type.replace(/_/g, ' ')}</span>
                  </div>
                  <p className="text-sm font-semibold text-neutral-900">{i.candidate_name}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{i.requirement_title}</p>
                  <div className="flex items-center justify-between mt-3 text-xs text-neutral-400">
                    <span>{i.scheduled_at.split('T')[0]}</span>
                    <span>{i.interviewer}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      );
    }

    // Active feedback form
    const techQuestions = [
      { id: 1, text: 'Python programming proficiency', tech: 'Python' },
      { id: 2, text: 'SQL and database design skills', tech: 'SQL' },
      { id: 3, text: 'React/frontend framework experience', tech: 'React' },
      { id: 4, text: 'AWS/cloud infrastructure knowledge', tech: 'AWS' },
    ];
    const immigrationQuestions = [
      { id: 20, text: 'Work authorization stability & timeline', tech: null },
      { id: 24, text: 'Immigration risk assessment', tech: null },
    ];
    const logisticsQuestions = [
      { id: 30, text: 'Location suitability for the role', tech: null },
      { id: 31, text: 'Relocation willingness', tech: null },
      { id: 40, text: 'Availability to start', tech: null },
    ];
    const softQuestions = [
      { id: 50, text: 'English communication skills', tech: null },
      { id: 51, text: 'Professionalism and presentation', tech: null },
    ];
    const expQuestions = [
      { id: 61, text: 'Depth of hands-on project experience', tech: null },
    ];

    const allQ = [...techQuestions, ...immigrationQuestions, ...logisticsQuestions, ...softQuestions, ...expQuestions];
    const answered = Object.keys(feedbackAnswers).length;
    const computedScore = answered > 0 ? Math.round(Object.values(feedbackAnswers).reduce((a, b) => a + b, 0) / answered * 20) : 0;

    const renderRatingGroup = (label: string, qs: typeof techQuestions) => (
      <div className="bg-white rounded-xl border border-neutral-200 p-4">
        <h4 className="text-xs font-semibold text-neutral-700 mb-3">{label}</h4>
        <div className="space-y-3">
          {qs.map(q => (
            <div key={q.id} className="flex items-center gap-3">
              <div className="flex-1">
                <p className="text-sm text-neutral-900">{q.text}</p>
                {q.tech && <span className="text-[9px] px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded">{q.tech}</span>}
              </div>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map(r => (
                  <button key={r} onClick={() => setFeedbackAnswers(prev => ({ ...prev, [q.id]: r }))}
                    className={`w-8 h-8 rounded-lg border text-xs font-bold ${feedbackAnswers[q.id] === r ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-500 border-neutral-200 hover:border-violet-300'}`}>
                    {r}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );

    return (
      <div className="space-y-4">
        {/* Context banner */}
        <div className="bg-violet-50 rounded-xl border border-violet-200 p-4 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-[10px] px-2 py-0.5 rounded-full ${typeColors[feedbackTarget.interview_type]}`}>{feedbackTarget.interview_type.replace(/_/g, ' ')}</span>
              <span className="text-[10px] text-neutral-500">Interview #{feedbackTarget.id}</span>
            </div>
            <p className="text-sm font-semibold text-violet-900">
              Feedback for <span className="text-violet-700">{feedbackTarget.candidate_name}</span>
            </p>
            <p className="text-xs text-violet-700 mt-0.5">{feedbackTarget.requirement_title}</p>
            <div className="flex items-center gap-4 mt-1 text-[10px] text-violet-600">
              <span>Candidate #{feedbackTarget.candidate_id}</span>
              <span>Job #{feedbackTarget.requirement_id}</span>
              <span>Interviewer: {feedbackTarget.interviewer}</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-violet-600">Computed Score</p>
            <p className="text-2xl font-bold text-violet-700">{computedScore}<span className="text-sm text-violet-400">/100</span></p>
            <p className="text-[10px] text-violet-500">{answered}/{allQ.length} rated</p>
          </div>
        </div>

        <button onClick={() => setFeedbackTarget(null)} className="text-xs text-violet-600 hover:underline">&larr; Back to interview selection</button>

        {/* Rating sections */}
        {renderRatingGroup('Technical Assessment', techQuestions)}
        {renderRatingGroup('Immigration & Work Authorization', immigrationQuestions)}
        {renderRatingGroup('Location & Availability', logisticsQuestions)}
        {renderRatingGroup('Communication & Culture', softQuestions)}
        {renderRatingGroup('Experience & Projects', expQuestions)}

        {/* Overall assessment */}
        <div className="bg-white rounded-xl border border-neutral-200 p-5">
          <h4 className="text-xs font-semibold text-neutral-700 mb-3">Overall Assessment</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-neutral-600 mb-2 block">Recommendation</label>
              <div className="flex gap-2 flex-wrap">
                {['strong_hire', 'hire', 'maybe', 'no_hire', 'strong_no_hire'].map(r => (
                  <button key={r} onClick={() => setFeedbackRec(r)}
                    className={`px-3 py-1.5 rounded-lg text-xs border ${feedbackRec === r ? `${recColors[r]} text-white border-transparent` : 'bg-white text-neutral-600 border-neutral-200'}`}>
                    {r.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs text-neutral-600 mb-2 block">Notes</label>
              <textarea value={feedbackNotes} onChange={e => setFeedbackNotes(e.target.value)}
                rows={3} className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm resize-none" placeholder="Summary notes..." />
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-4">
            <button onClick={() => setFeedbackTarget(null)} className="px-4 py-2 text-sm border border-neutral-200 rounded-lg hover:bg-neutral-50">Cancel</button>
            <button className="px-4 py-2 text-sm bg-white text-violet-600 border border-violet-200 rounded-lg hover:bg-violet-50">Save Draft</button>
            <button className="px-6 py-2 text-sm bg-violet-600 text-white rounded-lg hover:bg-violet-700">Submit Feedback & Compute Scores</button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-4 md:p-6 space-y-6 pb-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Interviews</h1>
          <p className="text-sm text-neutral-500 mt-1">Schedule, manage, and provide structured feedback for candidate interviews</p>
        </div>
        <button className="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700">+ Schedule Interview</button>
      </div>

      <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
        {tabs.map(t => (
          <button key={t} onClick={() => { setTab(t); if (t !== 'Give Feedback') setFeedbackTarget(null); }}
            className={`px-4 py-2 text-sm rounded-md transition-all ${tab === t ? 'bg-white text-neutral-900 shadow-sm font-medium' : 'text-neutral-600 hover:text-neutral-900'}`}>
            {t}
            {t === 'Give Feedback' && mockInterviews.filter(i => i.status === 'completed' && !i.feedback_submitted).length > 0 && (
              <span className="ml-1.5 w-4 h-4 bg-orange-500 text-white text-[9px] rounded-full inline-flex items-center justify-center">
                {mockInterviews.filter(i => i.status === 'completed' && !i.feedback_submitted).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {(tab === 'All Interviews' || tab === 'Scheduled' || tab === 'Completed') && <InterviewList />}
      {tab === 'Give Feedback' && <GiveFeedbackTab />}
    </div>
  );
};
