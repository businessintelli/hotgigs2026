import React, { useState } from 'react';

/* ─── helpers ─── */
const scoreBg = (s: number) => s >= 80 ? 'bg-emerald-100 text-emerald-800' : s >= 60 ? 'bg-blue-100 text-blue-800' : s >= 40 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';
const scoreBarColor = (s: number) => s >= 80 ? 'bg-emerald-500' : s >= 60 ? 'bg-blue-500' : s >= 40 ? 'bg-amber-500' : 'bg-red-500';
const decisionBg: Record<string, string> = {
  proceed: 'bg-emerald-100 text-emerald-800', shortlist: 'bg-emerald-600 text-white',
  hold: 'bg-amber-100 text-amber-800', reject: 'bg-red-100 text-red-800',
  needs_review: 'bg-violet-100 text-violet-800', pending: 'bg-neutral-100 text-neutral-600',
};
const sourceBg: Record<string, string> = {
  application: 'bg-blue-100 text-blue-700', manual_import: 'bg-violet-100 text-violet-700',
  referral: 'bg-emerald-100 text-emerald-700', job_board: 'bg-orange-100 text-orange-700',
  resume_upload: 'bg-cyan-100 text-cyan-700', ai_sourced: 'bg-pink-100 text-pink-700',
};

/* ─── types ─── */
interface ChecklistItem {
  id: number; checklist_id: number; category: string; question_text: string;
  question_type: string; options?: string[]; weight: number; is_required: boolean;
  is_eliminatory: boolean; min_passing_score: number; display_order: number; help_text?: string;
}
interface Checklist {
  id: number; name: string; description: string; is_default: boolean;
  is_active: boolean; applicable_to: string[]; items: ChecklistItem[];
}
interface Answer {
  id: number; checklist_item_id: number; answer_rating?: number; answer_yes_no?: boolean;
  answer_choice?: string; answer_text?: string; answer_checklist?: string[];
  score: number; is_passing: boolean; evaluator_notes: string;
}
interface FeedbackRecord {
  id: number; candidate_id: number; candidate_name: string;
  requirement_id: number | null; requirement_title: string | null;
  checklist_id: number; screener_name: string; screener_email: string;
  screening_source: string;
  overall_score: number; skills_score: number; experience_score: number;
  authorization_score: number; location_score: number; rate_score: number;
  availability_score: number; communication_score: number;
  decision: string; decision_reason: string | null; decision_at: string | null;
  summary_notes: string; strengths: string[]; concerns: string[]; red_flags: string[];
  is_draft: boolean; completed_at: string | null; duration_minutes: number | null;
  created_at: string; answers: Answer[];
}

/* ─── mock checklists ─── */
const CHECKLISTS: Checklist[] = [
  {
    id: 1, name: 'Standard Application Screening', description: 'Default checklist for all incoming job applications',
    is_default: true, is_active: true, applicable_to: ['application', 'job_board', 'referral'],
    items: [
      { id: 1, checklist_id: 1, category: 'skills_match', question_text: 'Does the candidate possess the required primary skills?', question_type: 'rating_1_5', weight: 2.0, is_required: true, is_eliminatory: true, min_passing_score: 3, display_order: 1, help_text: 'Rate 1-5 based on resume and profile match' },
      { id: 2, checklist_id: 1, category: 'experience_level', question_text: 'Meets minimum years of experience requirement?', question_type: 'yes_no', weight: 1.5, is_required: true, is_eliminatory: true, min_passing_score: 0, display_order: 2, help_text: 'Check against job posting' },
      { id: 3, checklist_id: 1, category: 'work_authorization', question_text: 'Work authorization status?', question_type: 'select', options: ['US Citizen', 'Green Card', 'H1B', 'H1B Transfer', 'OPT/CPT', 'EAD', 'TN Visa', 'L1', 'Requires Sponsorship', 'Unknown'], weight: 2.0, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 3, help_text: 'Verify legal right to work' },
      { id: 4, checklist_id: 1, category: 'location_fit', question_text: 'Location/relocation fit?', question_type: 'select', options: ['Local — no relocation', 'Remote — approved', 'Willing to relocate', 'Relocation needed — hesitant', 'Location mismatch'], weight: 1.5, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 4, help_text: 'Consider remote/hybrid/onsite' },
      { id: 5, checklist_id: 1, category: 'rate_fit', question_text: 'Rate/salary within budgeted range?', question_type: 'rating_1_5', weight: 1.5, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 5, help_text: '1=way over, 5=well within' },
      { id: 6, checklist_id: 1, category: 'availability', question_text: 'When can the candidate start?', question_type: 'select', options: ['Immediately', 'Within 1 week', 'Within 2 weeks', 'Within 1 month', 'More than 1 month', 'Unknown'], weight: 1.0, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 6, help_text: "Compare against client's urgency" },
      { id: 7, checklist_id: 1, category: 'communication', question_text: 'Communication quality (resume, initial correspondence)?', question_type: 'rating_1_5', weight: 1.0, is_required: false, is_eliminatory: false, min_passing_score: 0, display_order: 7, help_text: 'Based on resume, cover letter' },
      { id: 8, checklist_id: 1, category: 'education', question_text: 'Meets educational requirements?', question_type: 'yes_no', weight: 0.5, is_required: false, is_eliminatory: false, min_passing_score: 0, display_order: 8 },
      { id: 9, checklist_id: 1, category: 'overall', question_text: 'Overall impression — would you want to talk to this candidate?', question_type: 'rating_1_5', weight: 1.5, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 9, help_text: 'Professional assessment' },
      { id: 10, checklist_id: 1, category: 'background', question_text: 'Any red flags observed?', question_type: 'free_text', weight: 0, is_required: false, is_eliminatory: false, min_passing_score: 0, display_order: 10, help_text: 'Gaps, inconsistencies, job hopping' },
    ],
  },
  {
    id: 2, name: 'Quick Import Screening', description: 'Lightweight screening for recruiter-imported candidates',
    is_default: false, is_active: true, applicable_to: ['manual_import', 'resume_upload', 'ai_sourced'],
    items: [
      { id: 11, checklist_id: 2, category: 'skills_match', question_text: 'Primary technology match to open requirements', question_type: 'rating_1_5', weight: 2.0, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 1 },
      { id: 12, checklist_id: 2, category: 'experience_level', question_text: 'Experience level assessment', question_type: 'select', options: ['Junior (0-2 yrs)', 'Mid (3-5 yrs)', 'Senior (6-10 yrs)', 'Lead/Principal (10+ yrs)'], weight: 1.5, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 2 },
      { id: 13, checklist_id: 2, category: 'work_authorization', question_text: 'Work authorization (if known)', question_type: 'select', options: ['US Citizen', 'Green Card', 'H1B', 'OPT/CPT', 'EAD', 'Requires Sponsorship', 'Unknown'], weight: 1.5, is_required: false, is_eliminatory: false, min_passing_score: 0, display_order: 3 },
      { id: 14, checklist_id: 2, category: 'rate_fit', question_text: 'Estimated market rate alignment', question_type: 'rating_1_5', weight: 1.0, is_required: false, is_eliminatory: false, min_passing_score: 0, display_order: 4 },
      { id: 15, checklist_id: 2, category: 'overall', question_text: 'Priority level for outreach', question_type: 'select', options: ['High — contact immediately', 'Medium — add to pipeline', 'Low — keep on file', 'Skip — not a fit'], weight: 1.5, is_required: true, is_eliminatory: false, min_passing_score: 0, display_order: 5 },
      { id: 16, checklist_id: 2, category: 'overall', question_text: 'Recruiter notes on candidate potential', question_type: 'free_text', weight: 0, is_required: false, is_eliminatory: false, min_passing_score: 0, display_order: 6 },
    ],
  },
];

/* ─── mock records ─── */
const RECORDS: FeedbackRecord[] = [
  { id: 1, candidate_id: 1, candidate_name: 'Rajesh Kumar', requirement_id: 101, requirement_title: 'Sr Python Developer', checklist_id: 1, screener_name: 'Alice Morgan', screener_email: 'alice@co.com', screening_source: 'application', overall_score: 78, skills_score: 85, experience_score: 80, authorization_score: 55, location_score: 80, rate_score: 70, availability_score: 90, communication_score: 75, decision: 'proceed', decision_reason: 'Strong Python skills, H1B transfer manageable', decision_at: '2026-03-10T10:30:00Z', summary_notes: 'Solid backend developer, 8+ years Python/SQL. H1B transfer — verify timeline.', strengths: ['Strong Python/SQL', 'Relevant experience', 'Good communication'], concerns: ['H1B transfer delay', 'Limited React'], red_flags: [], is_draft: false, completed_at: '2026-03-10T10:45:00Z', duration_minutes: 15, created_at: '2026-03-10T10:30:00Z', answers: [{ id: 1, checklist_item_id: 1, answer_rating: 4, score: 80, is_passing: true, evaluator_notes: 'Python, SQL, AWS — 3/4 required' }, { id: 2, checklist_item_id: 2, answer_yes_no: true, score: 100, is_passing: true, evaluator_notes: '8 yrs' }, { id: 3, checklist_item_id: 3, answer_choice: 'H1B Transfer', score: 55, is_passing: true, evaluator_notes: '' }, { id: 4, checklist_item_id: 4, answer_choice: 'Remote — approved', score: 80, is_passing: true, evaluator_notes: '' }, { id: 5, checklist_item_id: 5, answer_rating: 4, score: 80, is_passing: true, evaluator_notes: '$75/hr, budget $80' }, { id: 6, checklist_item_id: 6, answer_choice: 'Within 2 weeks', score: 80, is_passing: true, evaluator_notes: '' }, { id: 7, checklist_item_id: 7, answer_rating: 4, score: 80, is_passing: true, evaluator_notes: '' }, { id: 8, checklist_item_id: 8, answer_yes_no: true, score: 100, is_passing: true, evaluator_notes: 'MS CS' }, { id: 9, checklist_item_id: 9, answer_rating: 4, score: 80, is_passing: true, evaluator_notes: 'Good overall' }, { id: 10, checklist_item_id: 10, answer_text: 'No red flags.', score: 0, is_passing: true, evaluator_notes: '' }] },
  { id: 2, candidate_id: 2, candidate_name: 'Emily Chen', requirement_id: 101, requirement_title: 'Sr Python Developer', checklist_id: 1, screener_name: 'Alice Morgan', screener_email: 'alice@co.com', screening_source: 'application', overall_score: 92, skills_score: 95, experience_score: 90, authorization_score: 100, location_score: 100, rate_score: 80, availability_score: 80, communication_score: 95, decision: 'shortlist', decision_reason: 'Exceptional — US Citizen, strong match, excellent communication', decision_at: '2026-03-10T11:00:00Z', summary_notes: '10+ years Python, strong system design. US Citizen. Slight rate premium but justified.', strengths: ['Exceptional Python/System Design', 'US Citizen', 'Leadership experience'], concerns: ['Rate slightly above midpoint', '3-week notice'], red_flags: [], is_draft: false, completed_at: '2026-03-10T11:12:00Z', duration_minutes: 12, created_at: '2026-03-10T10:48:00Z', answers: [{ id: 11, checklist_item_id: 1, answer_rating: 5, score: 100, is_passing: true, evaluator_notes: 'All required + extras' }, { id: 12, checklist_item_id: 2, answer_yes_no: true, score: 100, is_passing: true, evaluator_notes: '10+ years' }, { id: 13, checklist_item_id: 3, answer_choice: 'US Citizen', score: 100, is_passing: true, evaluator_notes: '' }, { id: 14, checklist_item_id: 9, answer_rating: 5, score: 100, is_passing: true, evaluator_notes: 'Top candidate' }] },
  { id: 3, candidate_id: 3, candidate_name: 'Marcus Johnson', requirement_id: 102, requirement_title: 'React Developer', checklist_id: 1, screener_name: 'Bob Chen', screener_email: 'bob@co.com', screening_source: 'referral', overall_score: 58, skills_score: 70, experience_score: 60, authorization_score: 40, location_score: 60, rate_score: 65, availability_score: 80, communication_score: 60, decision: 'hold', decision_reason: 'OPT expiring — immigration risk needs clarification', decision_at: '2026-03-11T14:20:00Z', summary_notes: 'Junior-mid React dev. OPT expiring in 4 months. Hold pending immigration clarification.', strengths: ['React/TS fundamentals', 'Trusted referral', 'Available now'], concerns: ['OPT expiring', 'Limited experience (3yr)', 'No backend'], red_flags: ['OPT expiration in 4 months, no H1B petition filed'], is_draft: false, completed_at: '2026-03-11T14:35:00Z', duration_minutes: 15, created_at: '2026-03-11T14:15:00Z', answers: [{ id: 21, checklist_item_id: 1, answer_rating: 3, score: 60, is_passing: true, evaluator_notes: 'React yes, limited depth' }, { id: 22, checklist_item_id: 3, answer_choice: 'OPT/CPT', score: 40, is_passing: true, evaluator_notes: 'Expiring Aug 2026' }, { id: 23, checklist_item_id: 9, answer_rating: 3, score: 60, is_passing: true, evaluator_notes: 'Immigration risk' }] },
  { id: 4, candidate_id: 4, candidate_name: 'Sarah Williams', requirement_id: null, requirement_title: null, checklist_id: 2, screener_name: 'Alice Morgan', screener_email: 'alice@co.com', screening_source: 'manual_import', overall_score: 82, skills_score: 90, experience_score: 85, authorization_score: 100, location_score: 80, rate_score: 75, availability_score: 60, communication_score: 80, decision: 'proceed', decision_reason: 'Strong frontend lead — assign to open React/Lead reqs', decision_at: '2026-03-12T09:15:00Z', summary_notes: 'LinkedIn import. 12 yrs frontend, 5 leading teams. US Citizen. 1-month notice.', strengths: ['12 years frontend', 'Team leadership', 'US Citizen', 'Strong portfolio'], concerns: ['1 month notice', 'Rate may be high'], red_flags: [], is_draft: false, completed_at: '2026-03-12T09:22:00Z', duration_minutes: 7, created_at: '2026-03-12T09:10:00Z', answers: [{ id: 28, checklist_item_id: 11, answer_rating: 5, score: 100, is_passing: true, evaluator_notes: 'React, TS, Next.js, leadership' }, { id: 29, checklist_item_id: 12, answer_choice: 'Lead/Principal (10+ yrs)', score: 100, is_passing: true, evaluator_notes: '' }, { id: 30, checklist_item_id: 15, answer_choice: 'High — contact immediately', score: 100, is_passing: true, evaluator_notes: 'Great fit for multiple reqs' }] },
  { id: 5, candidate_id: 5, candidate_name: 'David Park', requirement_id: 103, requirement_title: 'Data Engineer', checklist_id: 1, screener_name: 'Bob Chen', screener_email: 'bob@co.com', screening_source: 'job_board', overall_score: 45, skills_score: 50, experience_score: 40, authorization_score: 60, location_score: 80, rate_score: 90, availability_score: 100, communication_score: 40, decision: 'reject', decision_reason: 'Insufficient experience, resume inconsistencies', decision_at: '2026-03-12T16:00:00Z', summary_notes: 'Only 2 yrs experience for Sr role. Resume claims dont match history.', strengths: ['Available immediately', 'Rate within budget'], concerns: ['Experience far below req', 'Claims dont match history'], red_flags: ['Resume inconsistencies', 'Poor attention to detail'], is_draft: false, completed_at: '2026-03-12T16:08:00Z', duration_minutes: 8, created_at: '2026-03-12T15:55:00Z', answers: [{ id: 34, checklist_item_id: 1, answer_rating: 2, score: 40, is_passing: false, evaluator_notes: 'Claims not supported' }, { id: 35, checklist_item_id: 2, answer_yes_no: false, score: 0, is_passing: false, evaluator_notes: '2 yrs vs 5 min' }, { id: 36, checklist_item_id: 9, answer_rating: 2, score: 40, is_passing: false, evaluator_notes: 'Not suitable' }] },
  { id: 6, candidate_id: 6, candidate_name: 'Priya Sharma', requirement_id: 101, requirement_title: 'Sr Python Developer', checklist_id: 1, screener_name: 'Alice Morgan', screener_email: 'alice@co.com', screening_source: 'application', overall_score: 0, skills_score: 0, experience_score: 0, authorization_score: 0, location_score: 0, rate_score: 0, availability_score: 0, communication_score: 0, decision: 'pending', decision_reason: null, decision_at: null, summary_notes: '', strengths: [], concerns: [], red_flags: [], is_draft: true, completed_at: null, duration_minutes: null, created_at: '2026-03-14T08:00:00Z', answers: [] },
];

/* ─── mock open requirements (for new screening) ─── */
const OPEN_REQS = [
  { id: 101, title: 'Sr Python Developer', client: 'TechCorp', location: 'Remote', rate_range: '$70-80/hr' },
  { id: 102, title: 'React Developer', client: 'FinanceHub', location: 'NYC (Hybrid)', rate_range: '$65-75/hr' },
  { id: 103, title: 'Data Engineer', client: 'DataMax', location: 'Austin, TX', rate_range: '$80-95/hr' },
  { id: 104, title: 'DevOps Engineer', client: 'CloudScale', location: 'Remote', rate_range: '$75-90/hr' },
  { id: 105, title: 'Sr React Developer / Lead', client: 'HealthTech', location: 'Chicago (Onsite)', rate_range: '$85-100/hr' },
];

/* ─── mock candidates for new screening ─── */
const CANDIDATES_LIST = [
  { id: 1, name: 'Rajesh Kumar', title: 'Python Developer', location: 'Dallas, TX' },
  { id: 2, name: 'Emily Chen', title: 'Full Stack Engineer', location: 'San Jose, CA' },
  { id: 3, name: 'Marcus Johnson', title: 'React Developer', location: 'Atlanta, GA' },
  { id: 4, name: 'Sarah Williams', title: 'Frontend Lead', location: 'Chicago, IL' },
  { id: 5, name: 'David Park', title: 'Data Engineer', location: 'Austin, TX' },
  { id: 6, name: 'Priya Sharma', title: 'Python Developer', location: 'Boston, MA' },
  { id: 7, name: 'Alex Rivera', title: 'DevOps Engineer', location: 'Denver, CO' },
  { id: 8, name: 'Wei Zhang', title: 'ML Engineer', location: 'Seattle, WA' },
];

/* ═══════════════════════ COMPONENT ═══════════════════════ */
export default function ScreeningFeedbackCenter() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'applicants' | 'import' | 'manage'>('dashboard');
  const [expandedRecord, setExpandedRecord] = useState<number | null>(null);
  const [filterDecision, setFilterDecision] = useState('all');
  const [filterSource, setFilterSource] = useState('all');
  const [showNewScreening, setShowNewScreening] = useState(false);
  const [screeningScenario, setScreeningScenario] = useState<'application' | 'import' | 'manage'>('application');
  const [selectedChecklist, setSelectedChecklist] = useState<Checklist | null>(null);
  const [screeningAnswers, setScreeningAnswers] = useState<Record<number, any>>({});
  const [screeningNotes, setScreeningNotes] = useState<Record<number, string>>({});
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null);
  const [selectedReq, setSelectedReq] = useState<number | null>(null);
  const [decisionValue, setDecisionValue] = useState('pending');
  const [summaryNotes, setSummaryNotes] = useState('');
  const [strengthsText, setStrengthsText] = useState('');
  const [concernsText, setConcernsText] = useState('');
  const [screeningSuccess, setScreeningSuccess] = useState(false);

  /* Derived */
  const filtered = RECORDS.filter(r => {
    if (filterDecision !== 'all' && r.decision !== filterDecision) return false;
    if (filterSource !== 'all' && r.screening_source !== filterSource) return false;
    return true;
  });

  /* KPIs */
  const completed = RECORDS.filter(r => !r.is_draft);
  const avgScore = Math.round(completed.reduce((a, r) => a + r.overall_score, 0) / Math.max(completed.length, 1));
  const pendingCount = RECORDS.filter(r => r.is_draft || r.decision === 'pending').length;

  /* Compute screening score from answers */
  const computeScore = () => {
    if (!selectedChecklist) return 0;
    let totalWeight = 0, weightedSum = 0;
    selectedChecklist.items.forEach(item => {
      if (item.weight > 0 && screeningAnswers[item.id] !== undefined) {
        let score = 0;
        if (item.question_type === 'rating_1_5') score = ((screeningAnswers[item.id] || 0) / 5) * 100;
        else if (item.question_type === 'yes_no') score = screeningAnswers[item.id] === true ? 100 : 0;
        else if (item.question_type === 'select') score = screeningAnswers[item.id] ? 70 : 0;
        totalWeight += item.weight;
        weightedSum += score * item.weight;
      }
    });
    return totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0;
  };

  /* Reset screening form */
  const resetForm = () => {
    setShowNewScreening(false);
    setSelectedChecklist(null);
    setScreeningAnswers({});
    setScreeningNotes({});
    setSelectedCandidate(null);
    setSelectedReq(null);
    setDecisionValue('pending');
    setSummaryNotes('');
    setStrengthsText('');
    setConcernsText('');
    setScreeningSuccess(false);
  };

  /* Start screening for a specific scenario */
  const startScreening = (scenario: 'application' | 'import' | 'manage') => {
    resetForm();
    setScreeningScenario(scenario);
    const defaultCl = scenario === 'import'
      ? CHECKLISTS.find(c => c.applicable_to.includes('manual_import'))
      : CHECKLISTS.find(c => c.is_default);
    setSelectedChecklist(defaultCl || CHECKLISTS[0]);
    setShowNewScreening(true);
  };

  /* ─── Render Question Input ─── */
  const renderQuestionInput = (item: ChecklistItem) => {
    const val = screeningAnswers[item.id];
    switch (item.question_type) {
      case 'rating_1_5':
        return (
          <div className="flex gap-1.5">
            {[1, 2, 3, 4, 5].map(r => (
              <button key={r} onClick={() => setScreeningAnswers(p => ({ ...p, [item.id]: r }))}
                className={`w-9 h-9 rounded-lg text-sm font-semibold transition-colors ${val === r
                  ? r >= 4 ? 'bg-emerald-500 text-white' : r >= 3 ? 'bg-amber-500 text-white' : 'bg-red-500 text-white'
                  : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200'}`}>
                {r}
              </button>
            ))}
          </div>
        );
      case 'yes_no':
        return (
          <div className="flex gap-2">
            {[true, false].map(v => (
              <button key={String(v)} onClick={() => setScreeningAnswers(p => ({ ...p, [item.id]: v }))}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${val === v
                  ? v ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                  : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200'}`}>
                {v ? 'Yes' : 'No'}
              </button>
            ))}
          </div>
        );
      case 'select':
        return (
          <select className="border rounded-lg px-3 py-1.5 text-sm w-full max-w-md"
            value={val || ''} onChange={e => setScreeningAnswers(p => ({ ...p, [item.id]: e.target.value }))}>
            <option value="">— Select —</option>
            {(item.options || []).map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        );
      case 'free_text':
        return (
          <textarea className="border rounded-lg px-3 py-2 text-sm w-full max-w-lg" rows={2} placeholder="Enter notes..."
            value={val || ''} onChange={e => setScreeningAnswers(p => ({ ...p, [item.id]: e.target.value }))} />
        );
      case 'checklist':
        return (
          <div className="flex flex-wrap gap-2">
            {(item.options || []).map(o => {
              const checked = (val || []).includes(o);
              return (
                <label key={o} className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-sm cursor-pointer ${checked ? 'bg-blue-100 text-blue-700' : 'bg-neutral-100 text-neutral-500'}`}>
                  <input type="checkbox" checked={checked} className="rounded" onChange={() => {
                    const cur = val || [];
                    setScreeningAnswers(p => ({ ...p, [item.id]: checked ? cur.filter((x: string) => x !== o) : [...cur, o] }));
                  }} />
                  {o}
                </label>
              );
            })}
          </div>
        );
      default: return null;
    }
  };

  /* ─── Tabs ─── */
  const tabs = [
    { key: 'dashboard' as const, label: 'Dashboard', desc: 'Overview & stats' },
    { key: 'applicants' as const, label: 'Application Screening', desc: 'Scenario 1: screen applicants' },
    { key: 'import' as const, label: 'Import Screening', desc: 'Scenario 2: screen at import' },
    { key: 'manage' as const, label: 'All Screenings', desc: 'Scenario 3: manage all' },
  ];

  return (
    <div className="p-6 max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Screening Feedback Center</h1>
          <p className="text-sm text-neutral-500 mt-1">Screen candidates at application, import, or anytime from management</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => startScreening('application')} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
            Screen Application
          </button>
          <button onClick={() => startScreening('import')} className="bg-violet-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-violet-700">
            Screen Import
          </button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-6 gap-4">
        {[
          { label: 'Total Screenings', value: RECORDS.length, color: 'neutral' },
          { label: 'Avg Score', value: `${avgScore}/100`, color: 'blue' },
          { label: 'Shortlisted', value: RECORDS.filter(r => r.decision === 'shortlist').length, color: 'emerald' },
          { label: 'Proceeding', value: RECORDS.filter(r => r.decision === 'proceed').length, color: 'cyan' },
          { label: 'On Hold', value: RECORDS.filter(r => r.decision === 'hold').length, color: 'amber' },
          { label: 'Pending/Draft', value: pendingCount, color: 'red' },
        ].map((kpi, i) => (
          <div key={i} className="bg-white rounded-xl border p-4 text-center shadow-sm">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{kpi.label}</p>
            <p className={`text-2xl font-bold mt-1 text-${kpi.color}-600`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-neutral-100 rounded-lg p-1 w-fit">
        {tabs.map(t => (
          <button key={t.key} onClick={() => { setActiveTab(t.key); setShowNewScreening(false); }}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === t.key ? 'bg-white shadow text-neutral-900' : 'text-neutral-500 hover:text-neutral-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ════════════════════ NEW SCREENING FORM (shared across scenarios) ════════════════════ */}
      {showNewScreening && selectedChecklist && (
        <div className="bg-white rounded-xl border shadow-sm">
          <div className="p-5 border-b flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">
                {screeningScenario === 'application' ? 'Screen Application' : screeningScenario === 'import' ? 'Screen Imported Candidate' : 'Add Screening Feedback'}
              </h2>
              <p className="text-xs text-neutral-500 mt-0.5">Using: {selectedChecklist.name}</p>
            </div>
            <button onClick={resetForm} className="text-neutral-400 hover:text-neutral-600 text-xl">&times;</button>
          </div>

          {!screeningSuccess ? (
            <div className="p-5 space-y-5">
              {/* Context — candidate & requirement selection */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-50 rounded-lg">
                <div>
                  <label className="text-xs font-medium text-neutral-600 mb-1 block">Candidate *</label>
                  <select className="border rounded-lg px-3 py-2 text-sm w-full" value={selectedCandidate ?? ''} onChange={e => setSelectedCandidate(Number(e.target.value) || null)}>
                    <option value="">— Select candidate —</option>
                    {CANDIDATES_LIST.map(c => <option key={c.id} value={c.id}>{c.name} — {c.title}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-neutral-600 mb-1 block">Requirement {screeningScenario !== 'import' ? '*' : '(optional)'}</label>
                  <select className="border rounded-lg px-3 py-2 text-sm w-full" value={selectedReq ?? ''} onChange={e => setSelectedReq(Number(e.target.value) || null)}>
                    <option value="">— {screeningScenario === 'import' ? 'General screening (no specific req)' : 'Select requirement'} —</option>
                    {OPEN_REQS.map(r => <option key={r.id} value={r.id}>{r.title} — {r.client} ({r.rate_range})</option>)}
                  </select>
                </div>
              </div>

              {/* Checklist selector */}
              <div className="flex items-center gap-3">
                <span className="text-xs font-medium text-neutral-600">Checklist:</span>
                {CHECKLISTS.filter(c => c.is_active).map(c => (
                  <button key={c.id} onClick={() => { setSelectedChecklist(c); setScreeningAnswers({}); setScreeningNotes({}); }}
                    className={`px-3 py-1 rounded-lg text-xs font-medium ${selectedChecklist.id === c.id ? 'bg-blue-600 text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'}`}>
                    {c.name} {c.is_default && '(default)'}
                  </button>
                ))}
              </div>

              {/* Questions */}
              <div className="space-y-4">
                {selectedChecklist.items.sort((a, b) => a.display_order - b.display_order).map(item => (
                  <div key={item.id} className={`border rounded-lg p-4 ${item.is_eliminatory ? 'border-red-200 bg-red-50/30' : ''}`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-semibold ${
                            item.category === 'skills_match' ? 'bg-blue-100 text-blue-700' :
                            item.category === 'work_authorization' ? 'bg-amber-100 text-amber-700' :
                            item.category === 'location_fit' ? 'bg-cyan-100 text-cyan-700' :
                            item.category === 'rate_fit' ? 'bg-emerald-100 text-emerald-700' :
                            item.category === 'overall' ? 'bg-violet-100 text-violet-700' :
                            'bg-neutral-100 text-neutral-600'
                          }`}>{item.category.replace('_', ' ')}</span>
                          {item.is_required && <span className="text-red-500 text-xs">*</span>}
                          {item.is_eliminatory && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 text-red-700 font-semibold">ELIMINATORY</span>}
                          {item.weight > 0 && <span className="text-[10px] text-neutral-400">wt: {item.weight}x</span>}
                        </div>
                        <p className="text-sm font-medium mt-1">{item.question_text}</p>
                        {item.help_text && <p className="text-xs text-neutral-400 mt-0.5">{item.help_text}</p>}
                      </div>
                    </div>
                    {renderQuestionInput(item)}
                    {/* Per-question notes */}
                    <input type="text" placeholder="Notes (optional)..." className="mt-2 border rounded px-2 py-1 text-xs w-full max-w-lg text-neutral-500"
                      value={screeningNotes[item.id] || ''} onChange={e => setScreeningNotes(p => ({ ...p, [item.id]: e.target.value }))} />
                  </div>
                ))}
              </div>

              {/* Decision & summary */}
              <div className="border-t pt-4 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-medium text-neutral-600 block mb-1">Screening Decision</label>
                    <div className="flex flex-wrap gap-2">
                      {['shortlist', 'proceed', 'hold', 'needs_review', 'reject'].map(d => (
                        <button key={d} onClick={() => setDecisionValue(d)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${decisionValue === d ? decisionBg[d] : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200'}`}>
                          {d.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-neutral-600 block mb-1">Computed Score</label>
                    <div className="flex items-center gap-3">
                      <span className={`text-3xl font-bold px-3 py-1 rounded-lg ${scoreBg(computeScore())}`}>{computeScore()}</span>
                      <span className="text-neutral-400 text-sm">/ 100</span>
                    </div>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-neutral-600 block mb-1">Summary Notes</label>
                  <textarea className="border rounded-lg px-3 py-2 text-sm w-full" rows={2} value={summaryNotes} onChange={e => setSummaryNotes(e.target.value)} placeholder="Key observations and reasoning..." />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-medium text-neutral-600 block mb-1">Strengths (comma-separated)</label>
                    <input className="border rounded-lg px-3 py-2 text-sm w-full" value={strengthsText} onChange={e => setStrengthsText(e.target.value)} placeholder="e.g. Strong Python, Good communication" />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-neutral-600 block mb-1">Concerns / Red Flags (comma-separated)</label>
                    <input className="border rounded-lg px-3 py-2 text-sm w-full" value={concernsText} onChange={e => setConcernsText(e.target.value)} placeholder="e.g. H1B risk, Limited experience" />
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex gap-3 pt-2">
                  <button onClick={() => setScreeningSuccess(true)} disabled={!selectedCandidate}
                    className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50">
                    Save as Draft
                  </button>
                  <button onClick={() => setScreeningSuccess(true)} disabled={!selectedCandidate || decisionValue === 'pending'}
                    className="bg-emerald-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50">
                    Submit Screening Feedback
                  </button>
                  <button onClick={resetForm} className="px-5 py-2 rounded-lg text-sm text-neutral-500 hover:bg-neutral-100">Cancel</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center">
              <div className="text-4xl mb-3">✅</div>
              <h3 className="text-lg font-semibold text-neutral-800">Screening Feedback Saved!</h3>
              <p className="text-sm text-neutral-500 mt-1">
                Candidate: {CANDIDATES_LIST.find(c => c.id === selectedCandidate)?.name} | Score: {computeScore()}/100 | Decision: {decisionValue}
              </p>
              <div className="flex gap-3 justify-center mt-4">
                <button onClick={() => { resetForm(); startScreening(screeningScenario); }} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Screen Another</button>
                <button onClick={resetForm} className="border px-4 py-2 rounded-lg text-sm text-neutral-600">Close</button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ════════════════════ TAB: DASHBOARD ════════════════════ */}
      {activeTab === 'dashboard' && !showNewScreening && (
        <div className="space-y-6">
          {/* Decision pipeline */}
          <div className="bg-white rounded-xl border p-5 shadow-sm">
            <h3 className="font-semibold text-neutral-800 mb-3">Screening Pipeline</h3>
            <div className="flex gap-2 h-8">
              {[
                { key: 'shortlist', label: 'Shortlisted', count: RECORDS.filter(r => r.decision === 'shortlist').length, color: 'bg-emerald-600' },
                { key: 'proceed', label: 'Proceed', count: RECORDS.filter(r => r.decision === 'proceed').length, color: 'bg-emerald-400' },
                { key: 'hold', label: 'Hold', count: RECORDS.filter(r => r.decision === 'hold').length, color: 'bg-amber-400' },
                { key: 'needs_review', label: 'Needs Review', count: RECORDS.filter(r => r.decision === 'needs_review').length, color: 'bg-violet-400' },
                { key: 'reject', label: 'Rejected', count: RECORDS.filter(r => r.decision === 'reject').length, color: 'bg-red-400' },
                { key: 'pending', label: 'Pending', count: RECORDS.filter(r => r.decision === 'pending').length, color: 'bg-neutral-300' },
              ].filter(s => s.count > 0).map(s => (
                <div key={s.key} className={`${s.color} rounded-lg flex items-center justify-center text-white text-xs font-semibold`}
                  style={{ flex: s.count }}>
                  {s.label} ({s.count})
                </div>
              ))}
            </div>
          </div>

          {/* By source breakdown */}
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border p-5 shadow-sm">
              <h3 className="font-semibold text-neutral-800 mb-3">By Source</h3>
              {['application', 'manual_import', 'referral', 'job_board'].map(src => {
                const count = RECORDS.filter(r => r.screening_source === src).length;
                return (
                  <div key={src} className="flex items-center justify-between py-2 border-b last:border-0">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${sourceBg[src]}`}>{src.replace('_', ' ')}</span>
                    <span className="font-semibold text-sm">{count}</span>
                  </div>
                );
              })}
            </div>
            <div className="bg-white rounded-xl border p-5 shadow-sm">
              <h3 className="font-semibold text-neutral-800 mb-3">Top Screeners</h3>
              {[
                { name: 'Alice Morgan', count: 4, avgScore: 84, avgMin: 11 },
                { name: 'Bob Chen', count: 2, avgScore: 52, avgMin: 12 },
              ].map(s => (
                <div key={s.name} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <span className="font-medium text-sm">{s.name}</span>
                    <span className="text-xs text-neutral-400 ml-2">{s.count} screenings</span>
                  </div>
                  <div className="flex items-center gap-3 text-xs">
                    <span className={`px-2 py-0.5 rounded font-semibold ${scoreBg(s.avgScore)}`}>Avg: {s.avgScore}</span>
                    <span className="text-neutral-400">{s.avgMin} min/avg</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent activity */}
          <div className="bg-white rounded-xl border p-5 shadow-sm">
            <h3 className="font-semibold text-neutral-800 mb-3">Recent Screenings</h3>
            <div className="space-y-2">
              {RECORDS.slice().reverse().slice(0, 5).map(r => (
                <div key={r.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-neutral-200 rounded-full flex items-center justify-center text-xs font-semibold">{r.candidate_name.split(' ').map(n => n[0]).join('')}</div>
                    <div>
                      <span className="font-medium text-sm">{r.candidate_name}</span>
                      <span className="text-xs text-neutral-400 ml-2">{r.requirement_title || 'General'}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${sourceBg[r.screening_source]}`}>{r.screening_source.replace('_', ' ')}</span>
                    {!r.is_draft && <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.overall_score)}`}>{r.overall_score}</span>}
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold capitalize ${decisionBg[r.decision]}`}>{r.decision}</span>
                    {r.is_draft && <span className="text-[10px] px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded font-semibold">DRAFT</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ════════════════════ TAB: APPLICATION SCREENING ════════════════════ */}
      {activeTab === 'applicants' && !showNewScreening && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-neutral-800">Application Queue — Candidates Awaiting Screening</h3>
              <button onClick={() => startScreening('application')} className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700">
                + New Application Screening
              </button>
            </div>
            <p className="text-xs text-neutral-500 mb-4">These candidates have submitted applications and need recruiter screening. Click "Screen" to fill out the checklist.</p>

            {/* Pending application screenings */}
            {RECORDS.filter(r => r.screening_source === 'application').length === 0 ? (
              <p className="text-neutral-400 text-sm py-8 text-center">No application screenings found.</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-neutral-50 text-neutral-600">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Candidate</th>
                    <th className="px-4 py-2 text-left font-medium">Requirement</th>
                    <th className="px-4 py-2 text-center font-medium">Score</th>
                    <th className="px-4 py-2 text-center font-medium">Decision</th>
                    <th className="px-4 py-2 text-center font-medium">Screener</th>
                    <th className="px-4 py-2 text-center font-medium">Date</th>
                    <th className="px-4 py-2 text-center font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {RECORDS.filter(r => r.screening_source === 'application').map(r => (
                    <React.Fragment key={r.id}>
                      <tr className="border-t hover:bg-neutral-50 cursor-pointer" onClick={() => setExpandedRecord(expandedRecord === r.id ? null : r.id)}>
                        <td className="px-4 py-3 font-medium">{r.candidate_name} {r.is_draft && <span className="text-[10px] ml-1 px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded font-semibold">DRAFT</span>}</td>
                        <td className="px-4 py-3 text-neutral-600">{r.requirement_title}</td>
                        <td className="px-4 py-3 text-center">{!r.is_draft ? <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.overall_score)}`}>{r.overall_score}</span> : <span className="text-neutral-300">—</span>}</td>
                        <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-semibold capitalize ${decisionBg[r.decision]}`}>{r.decision}</span></td>
                        <td className="px-4 py-3 text-center text-neutral-500">{r.screener_name}</td>
                        <td className="px-4 py-3 text-center text-neutral-400 text-xs">{r.created_at.split('T')[0]}</td>
                        <td className="px-4 py-3 text-center">
                          <button onClick={e => { e.stopPropagation(); startScreening('application'); setSelectedCandidate(r.candidate_id); setSelectedReq(r.requirement_id); }}
                            className="text-xs font-medium text-blue-600 hover:underline">
                            {r.is_draft ? 'Continue' : 'Edit'}
                          </button>
                        </td>
                      </tr>
                      {expandedRecord === r.id && !r.is_draft && (
                        <tr><td colSpan={7} className="bg-neutral-50 px-6 py-4">
                          <div className="space-y-3">
                            <div className="grid grid-cols-4 gap-3">
                              {[
                                { label: 'Skills', score: r.skills_score }, { label: 'Experience', score: r.experience_score },
                                { label: 'Authorization', score: r.authorization_score }, { label: 'Location', score: r.location_score },
                                { label: 'Rate Fit', score: r.rate_score }, { label: 'Availability', score: r.availability_score },
                                { label: 'Communication', score: r.communication_score }, { label: 'Overall', score: r.overall_score },
                              ].map(d => (
                                <div key={d.label} className="text-center">
                                  <p className="text-[10px] text-neutral-500 uppercase">{d.label}</p>
                                  <div className="h-1.5 bg-neutral-200 rounded-full mt-1"><div className={`h-full rounded-full ${scoreBarColor(d.score)}`} style={{ width: `${d.score}%` }} /></div>
                                  <p className="text-xs font-semibold mt-0.5">{d.score}</p>
                                </div>
                              ))}
                            </div>
                            {r.summary_notes && <p className="text-xs text-neutral-600"><span className="font-semibold">Notes:</span> {r.summary_notes}</p>}
                            {r.strengths.length > 0 && <p className="text-xs"><span className="font-semibold text-emerald-700">Strengths:</span> {r.strengths.join(', ')}</p>}
                            {r.concerns.length > 0 && <p className="text-xs"><span className="font-semibold text-amber-700">Concerns:</span> {r.concerns.join(', ')}</p>}
                            {r.red_flags.length > 0 && <p className="text-xs"><span className="font-semibold text-red-700">Red Flags:</span> {r.red_flags.join(', ')}</p>}
                            {r.decision_reason && <p className="text-xs"><span className="font-semibold">Decision Reason:</span> {r.decision_reason}</p>}
                          </div>
                        </td></tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* ════════════════════ TAB: IMPORT SCREENING ════════════════════ */}
      {activeTab === 'import' && !showNewScreening && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-neutral-800">Import-Time Screening</h3>
              <button onClick={() => startScreening('import')} className="bg-violet-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-violet-700">
                + Import & Screen Candidate
              </button>
            </div>
            <p className="text-xs text-neutral-500 mb-4">When you manually add or import a candidate, use the Quick Import Screening checklist to capture initial assessment. These screenings may not be tied to a specific requirement.</p>

            {RECORDS.filter(r => ['manual_import', 'resume_upload', 'ai_sourced'].includes(r.screening_source)).length === 0 ? (
              <p className="text-neutral-400 text-sm py-8 text-center">No import screenings found.</p>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {RECORDS.filter(r => ['manual_import', 'resume_upload', 'ai_sourced'].includes(r.screening_source)).map(r => (
                  <div key={r.id} className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-violet-100 text-violet-700 rounded-full flex items-center justify-center text-xs font-semibold">{r.candidate_name.split(' ').map(n => n[0]).join('')}</div>
                        <div>
                          <span className="font-semibold text-sm">{r.candidate_name}</span>
                          <span className={`ml-2 px-2 py-0.5 rounded text-[10px] font-medium ${sourceBg[r.screening_source]}`}>{r.screening_source.replace('_', ' ')}</span>
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.overall_score)}`}>{r.overall_score}</span>
                    </div>
                    <p className="text-xs text-neutral-500">{r.requirement_title || 'General screening — not linked to a specific requirement'}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {r.strengths.map((s, i) => <span key={i} className="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-700 rounded">{s}</span>)}
                    </div>
                    <div className="flex items-center justify-between mt-3 pt-2 border-t">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold capitalize ${decisionBg[r.decision]}`}>{r.decision}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-neutral-400">{r.screener_name} · {r.created_at.split('T')[0]}</span>
                        <button onClick={() => { startScreening('import'); setSelectedCandidate(r.candidate_id); }} className="text-xs font-medium text-violet-600 hover:underline">Edit</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ════════════════════ TAB: ALL SCREENINGS (MANAGE) ════════════════════ */}
      {activeTab === 'manage' && !showNewScreening && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border shadow-sm">
            <div className="p-5 border-b flex items-center justify-between">
              <h3 className="font-semibold text-neutral-800">All Screening Records</h3>
              <div className="flex items-center gap-3">
                <select className="border rounded-lg px-3 py-1.5 text-sm" value={filterDecision} onChange={e => setFilterDecision(e.target.value)}>
                  <option value="all">All Decisions</option>
                  {['shortlist', 'proceed', 'hold', 'reject', 'needs_review', 'pending'].map(d => <option key={d} value={d}>{d}</option>)}
                </select>
                <select className="border rounded-lg px-3 py-1.5 text-sm" value={filterSource} onChange={e => setFilterSource(e.target.value)}>
                  <option value="all">All Sources</option>
                  {['application', 'manual_import', 'referral', 'job_board'].map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                </select>
                <button onClick={() => startScreening('manage')} className="bg-neutral-800 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-neutral-700">
                  + Add Screening
                </button>
              </div>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-neutral-50 text-neutral-600">
                <tr>
                  <th className="px-4 py-2 text-left font-medium">Candidate</th>
                  <th className="px-4 py-2 text-left font-medium">Requirement</th>
                  <th className="px-4 py-2 text-center font-medium">Source</th>
                  <th className="px-4 py-2 text-center font-medium">Score</th>
                  <th className="px-4 py-2 text-center font-medium">Skills</th>
                  <th className="px-4 py-2 text-center font-medium">Auth</th>
                  <th className="px-4 py-2 text-center font-medium">Rate</th>
                  <th className="px-4 py-2 text-center font-medium">Decision</th>
                  <th className="px-4 py-2 text-center font-medium">Screener</th>
                  <th className="px-4 py-2 text-center font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(r => (
                  <React.Fragment key={r.id}>
                    <tr className="border-t hover:bg-neutral-50 cursor-pointer" onClick={() => setExpandedRecord(expandedRecord === r.id ? null : r.id)}>
                      <td className="px-4 py-3">
                        <span className="font-medium">{r.candidate_name}</span>
                        {r.is_draft && <span className="ml-1 text-[10px] px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded font-semibold">DRAFT</span>}
                      </td>
                      <td className="px-4 py-3 text-neutral-600">{r.requirement_title || <span className="text-neutral-300">General</span>}</td>
                      <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-[10px] font-medium ${sourceBg[r.screening_source]}`}>{r.screening_source.replace('_', ' ')}</span></td>
                      <td className="px-4 py-3 text-center">{!r.is_draft ? <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.overall_score)}`}>{r.overall_score}</span> : '—'}</td>
                      <td className="px-4 py-3 text-center">{!r.is_draft ? <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.skills_score)}`}>{r.skills_score}</span> : '—'}</td>
                      <td className="px-4 py-3 text-center">{!r.is_draft ? <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.authorization_score)}`}>{r.authorization_score}</span> : '—'}</td>
                      <td className="px-4 py-3 text-center">{!r.is_draft ? <span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(r.rate_score)}`}>{r.rate_score}</span> : '—'}</td>
                      <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-semibold capitalize ${decisionBg[r.decision]}`}>{r.decision}</span></td>
                      <td className="px-4 py-3 text-center text-xs text-neutral-500">{r.screener_name}</td>
                      <td className="px-4 py-3 text-center">
                        <button onClick={e => { e.stopPropagation(); startScreening('manage'); setSelectedCandidate(r.candidate_id); setSelectedReq(r.requirement_id); }}
                          className="text-xs font-medium text-blue-600 hover:underline">
                          {r.is_draft ? 'Continue' : 'Edit'}
                        </button>
                      </td>
                    </tr>
                    {expandedRecord === r.id && !r.is_draft && (
                      <tr><td colSpan={10} className="bg-neutral-50 px-6 py-4">
                        <div className="space-y-3">
                          <div className="grid grid-cols-4 gap-3">
                            {[
                              { label: 'Skills', score: r.skills_score }, { label: 'Experience', score: r.experience_score },
                              { label: 'Authorization', score: r.authorization_score }, { label: 'Location', score: r.location_score },
                              { label: 'Rate Fit', score: r.rate_score }, { label: 'Availability', score: r.availability_score },
                              { label: 'Communication', score: r.communication_score }, { label: 'Overall', score: r.overall_score },
                            ].map(d => (
                              <div key={d.label} className="text-center">
                                <p className="text-[10px] text-neutral-500 uppercase">{d.label}</p>
                                <div className="h-1.5 bg-neutral-200 rounded-full mt-1"><div className={`h-full rounded-full ${scoreBarColor(d.score)}`} style={{ width: `${d.score}%` }} /></div>
                                <p className="text-xs font-semibold mt-0.5">{d.score}</p>
                              </div>
                            ))}
                          </div>
                          {r.summary_notes && <p className="text-xs text-neutral-600"><span className="font-semibold">Notes:</span> {r.summary_notes}</p>}
                          {r.strengths.length > 0 && <p className="text-xs"><span className="font-semibold text-emerald-700">Strengths:</span> {r.strengths.join(', ')}</p>}
                          {r.concerns.length > 0 && <p className="text-xs"><span className="font-semibold text-amber-700">Concerns:</span> {r.concerns.join(', ')}</p>}
                          {r.red_flags.length > 0 && <p className="text-xs"><span className="font-semibold text-red-700">Red Flags:</span> {r.red_flags.join(', ')}</p>}
                          {r.decision_reason && <p className="text-xs"><span className="font-semibold">Decision Reason:</span> {r.decision_reason}</p>}
                          {/* Answers detail */}
                          {r.answers.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-semibold text-neutral-700 mb-1">Checklist Answers:</p>
                              <div className="grid grid-cols-2 gap-2">
                                {r.answers.map(a => {
                                  const item = (CHECKLISTS.find(c => c.id === r.checklist_id)?.items || []).find(i => i.id === a.checklist_item_id);
                                  return (
                                    <div key={a.id} className="flex items-center gap-2 text-[11px]">
                                      <span className={`w-6 h-6 rounded flex items-center justify-center text-white text-[10px] font-bold ${a.is_passing ? 'bg-emerald-500' : 'bg-red-500'}`}>
                                        {a.answer_rating ?? (a.answer_yes_no === true ? '✓' : a.answer_yes_no === false ? '✗' : '•')}
                                      </span>
                                      <span className="text-neutral-600 truncate">{item?.question_text || `Q#${a.checklist_item_id}`}</span>
                                      {a.answer_choice && <span className="text-neutral-400 ml-auto truncate max-w-[120px]">{a.answer_choice}</span>}
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      </td></tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && <p className="text-neutral-400 text-sm py-8 text-center">No screenings match your filters.</p>}
          </div>
        </div>
      )}
    </div>
  );
}

export { ScreeningFeedbackCenter };
