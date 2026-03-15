import React, { useState } from 'react';

/* ─── helpers ─── */
const scoreBg = (s: number) => s >= 80 ? 'bg-emerald-100 text-emerald-800' : s >= 60 ? 'bg-blue-100 text-blue-800' : s >= 40 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';
const scoreBarColor = (s: number) => s >= 80 ? 'bg-emerald-500' : s >= 60 ? 'bg-blue-500' : s >= 40 ? 'bg-amber-500' : 'bg-red-500';
const trendIcon = (t: string) => t === 'improving' ? '↑' : t === 'declining' ? '↓' : '→';
const trendColor = (t: string) => t === 'improving' ? 'text-emerald-600' : t === 'declining' ? 'text-red-600' : 'text-neutral-500';
const recBg: Record<string, string> = { strong_fit: 'bg-emerald-600', good_fit: 'bg-emerald-500', partial_fit: 'bg-amber-500', poor_fit: 'bg-red-500' };

/* ─── types ─── */
interface PersistentScore {
  id: number; candidate_id: number; candidate_name: string;
  skill_or_technology: string; category: string;
  current_score: number; score_count: number; highest_score: number; lowest_score: number;
  confidence_level: number; trend: string; last_assessed_at: string;
  score_history: { date: string; score: number; interview_id: number }[];
}
interface JobMatch {
  id: number; candidate_id: number; candidate_name: string;
  requirement_id: number; requirement_title: string;
  overall_match_score: number; technical_match_score: number; experience_match_score: number;
  immigration_match_score: number; location_match_score: number;
  availability_match_score: number; culture_match_score: number; compensation_match_score: number;
  matched_skills: { skill: string; required_level: number; candidate_level: number; gap: number }[];
  missing_skills: string[]; exceeding_skills: string[]; risk_factors: string[];
  recommendation: string;
}
interface Recommendation {
  requirement_id: number; title: string; match_score: number; reason: string;
}

/* ─── mock data ─── */
const persistentScores: PersistentScore[] = [
  { id: 1, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Python', category: 'technical', current_score: 90, score_count: 2, highest_score: 100, lowest_score: 80, confidence_level: 0.85, trend: 'improving', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-03-10', score: 80, interview_id: 101 }, { date: '2026-03-14', score: 100, interview_id: 104 }] },
  { id: 2, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'SQL', category: 'technical', current_score: 80, score_count: 2, highest_score: 80, lowest_score: 80, confidence_level: 0.80, trend: 'stable', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-03-10', score: 80, interview_id: 101 }, { date: '2026-03-14', score: 80, interview_id: 104 }] },
  { id: 3, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'React', category: 'framework', current_score: 40, score_count: 1, highest_score: 40, lowest_score: 40, confidence_level: 0.45, trend: 'stable', last_assessed_at: '2026-03-10', score_history: [{ date: '2026-03-10', score: 40, interview_id: 101 }] },
  { id: 4, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'AWS', category: 'technical', current_score: 60, score_count: 1, highest_score: 60, lowest_score: 60, confidence_level: 0.45, trend: 'stable', last_assessed_at: '2026-03-10', score_history: [{ date: '2026-03-10', score: 60, interview_id: 101 }] },
  { id: 5, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Data Engineering', category: 'technical', current_score: 80, score_count: 1, highest_score: 80, lowest_score: 80, confidence_level: 0.50, trend: 'stable', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-03-14', score: 80, interview_id: 104 }] },
  { id: 6, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Communication', category: 'communication', current_score: 80, score_count: 2, highest_score: 80, lowest_score: 80, confidence_level: 0.82, trend: 'stable', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-03-10', score: 80, interview_id: 101 }, { date: '2026-03-14', score: 80, interview_id: 104 }] },
  { id: 7, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Immigration (H1B)', category: 'immigration', current_score: 60, score_count: 2, highest_score: 60, lowest_score: 60, confidence_level: 0.75, trend: 'stable', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-03-10', score: 60, interview_id: 101 }, { date: '2026-03-14', score: 60, interview_id: 104 }] },
  { id: 10, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'Python', category: 'technical', current_score: 100, score_count: 1, highest_score: 100, lowest_score: 100, confidence_level: 0.55, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-03-11', score: 100, interview_id: 102 }] },
  { id: 11, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'SQL', category: 'technical', current_score: 80, score_count: 1, highest_score: 80, lowest_score: 80, confidence_level: 0.50, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-03-11', score: 80, interview_id: 102 }] },
  { id: 12, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'React', category: 'framework', current_score: 60, score_count: 1, highest_score: 60, lowest_score: 60, confidence_level: 0.45, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-03-11', score: 60, interview_id: 102 }] },
  { id: 13, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'System Design', category: 'system_design', current_score: 80, score_count: 1, highest_score: 80, lowest_score: 80, confidence_level: 0.50, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-03-11', score: 80, interview_id: 102 }] },
  { id: 14, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'Communication', category: 'communication', current_score: 100, score_count: 1, highest_score: 100, lowest_score: 100, confidence_level: 0.55, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-03-11', score: 100, interview_id: 102 }] },
  { id: 15, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'Immigration', category: 'immigration', current_score: 100, score_count: 1, highest_score: 100, lowest_score: 100, confidence_level: 0.55, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-03-11', score: 100, interview_id: 102 }] },
  { id: 20, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'Python', category: 'technical', current_score: 60, score_count: 1, highest_score: 60, lowest_score: 60, confidence_level: 0.45, trend: 'stable', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-03-12', score: 60, interview_id: 103 }] },
  { id: 21, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'SQL', category: 'technical', current_score: 60, score_count: 1, highest_score: 60, lowest_score: 60, confidence_level: 0.45, trend: 'stable', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-03-12', score: 60, interview_id: 103 }] },
  { id: 22, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'React', category: 'framework', current_score: 80, score_count: 1, highest_score: 80, lowest_score: 80, confidence_level: 0.50, trend: 'stable', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-03-12', score: 80, interview_id: 103 }] },
  { id: 23, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'Immigration (OPT)', category: 'immigration', current_score: 40, score_count: 1, highest_score: 40, lowest_score: 40, confidence_level: 0.45, trend: 'stable', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-03-12', score: 40, interview_id: 103 }] },
];

const jobMatches: JobMatch[] = [
  { id: 1, candidate_id: 1, candidate_name: 'Rajesh Kumar', requirement_id: 201, requirement_title: 'Senior Python Developer — TechCorp', overall_match_score: 82, technical_match_score: 85, experience_match_score: 80, immigration_match_score: 65, location_match_score: 80, availability_match_score: 90, culture_match_score: 75, compensation_match_score: 75, matched_skills: [{ skill: 'Python', required_level: 80, candidate_level: 90, gap: 10 }, { skill: 'SQL', required_level: 70, candidate_level: 80, gap: 10 }, { skill: 'AWS', required_level: 60, candidate_level: 60, gap: 0 }], missing_skills: ['React (limited)'], exceeding_skills: ['Python', 'SQL'], risk_factors: ['H1B transfer needed'], recommendation: 'good_fit' },
  { id: 2, candidate_id: 2, candidate_name: 'Emily Chen', requirement_id: 201, requirement_title: 'Senior Python Developer — TechCorp', overall_match_score: 91, technical_match_score: 92, experience_match_score: 88, immigration_match_score: 100, location_match_score: 100, availability_match_score: 85, culture_match_score: 85, compensation_match_score: 70, matched_skills: [{ skill: 'Python', required_level: 80, candidate_level: 100, gap: 20 }, { skill: 'SQL', required_level: 70, candidate_level: 80, gap: 10 }, { skill: 'System Design', required_level: 60, candidate_level: 80, gap: 20 }], missing_skills: ['AWS (limited)'], exceeding_skills: ['Python', 'System Design', 'Communication'], risk_factors: ['Rate at top of budget'], recommendation: 'strong_fit' },
  { id: 3, candidate_id: 3, candidate_name: 'Marcus Johnson', requirement_id: 202, requirement_title: 'Full Stack Developer — MedFirst Health', overall_match_score: 58, technical_match_score: 62, experience_match_score: 55, immigration_match_score: 40, location_match_score: 50, availability_match_score: 75, culture_match_score: 70, compensation_match_score: 90, matched_skills: [{ skill: 'React', required_level: 70, candidate_level: 80, gap: 10 }, { skill: 'Python', required_level: 70, candidate_level: 60, gap: -10 }, { skill: 'SQL', required_level: 60, candidate_level: 60, gap: 0 }], missing_skills: ['Python (below req)', 'System Design'], exceeding_skills: ['React'], risk_factors: ['OPT expiring in 6 months', 'Wants remote — role is hybrid', 'Needs H1B'], recommendation: 'partial_fit' },
  { id: 4, candidate_id: 1, candidate_name: 'Rajesh Kumar', requirement_id: 203, requirement_title: 'Backend Engineer — DataFlow Analytics', overall_match_score: 85, technical_match_score: 88, experience_match_score: 82, immigration_match_score: 65, location_match_score: 90, availability_match_score: 85, culture_match_score: 78, compensation_match_score: 80, matched_skills: [{ skill: 'Python', required_level: 85, candidate_level: 90, gap: 5 }, { skill: 'SQL', required_level: 75, candidate_level: 80, gap: 5 }, { skill: 'Data Engineering', required_level: 70, candidate_level: 80, gap: 10 }], missing_skills: [], exceeding_skills: ['Python', 'Data Engineering'], risk_factors: ['H1B transfer pending'], recommendation: 'good_fit' },
];

const recommendations: Record<number, Recommendation[]> = {
  1: [
    { requirement_id: 204, title: 'Data Engineer — CloudScale', match_score: 87, reason: 'Strong Python (90) and Data Engineering (80). SQL (80) exceeds requirement.' },
    { requirement_id: 205, title: 'Backend Lead — FinTech Corp', match_score: 83, reason: 'Python expertise (90) and improving system design. Leadership potential.' },
    { requirement_id: 206, title: 'Python Developer — AI Startup', match_score: 79, reason: 'Python (90) strong match. AWS (60) may need assessment for cloud-heavy role.' },
  ],
  2: [
    { requirement_id: 207, title: 'Staff Engineer — TechGiant', match_score: 93, reason: 'Expert Python (100), strong system design (80), excellent communication (100).' },
    { requirement_id: 204, title: 'Data Engineer — CloudScale', match_score: 78, reason: 'Strong Python but no data engineering score yet. Recommend assessment.' },
  ],
  3: [
    { requirement_id: 208, title: 'Frontend Developer — Remote Co', match_score: 82, reason: 'Strong React (80), good communication. Remote role matches preference.' },
  ],
};

const candidates = [
  { id: 1, name: 'Rajesh Kumar', assessments: 2, avgScore: 74, skills: 7 },
  { id: 2, name: 'Emily Chen', assessments: 1, avgScore: 87, skills: 6 },
  { id: 3, name: 'Marcus Johnson', assessments: 1, avgScore: 60, skills: 4 },
];

const tabs = ['Score Profiles', 'Job Match Analysis', 'Recommendations'] as const;
type Tab = typeof tabs[number];

export const CandidateScoreIntelligence: React.FC = () => {
  const [tab, setTab] = useState<Tab>('Score Profiles');
  const [selectedCandidate, setSelectedCandidate] = useState<number>(1);
  const [expandedMatch, setExpandedMatch] = useState<number | null>(null);

  const candidateScores = persistentScores.filter(s => s.candidate_id === selectedCandidate);
  const candidateMatches = jobMatches.filter(m => m.candidate_id === selectedCandidate);
  const candidateRecs = recommendations[selectedCandidate] || [];
  const candidate = candidates.find(c => c.id === selectedCandidate)!;

  const ScoreProfilesTab = () => (
    <div className="space-y-6">
      {/* Candidate selector */}
      <div className="flex gap-3">
        {candidates.map(c => (
          <button key={c.id} onClick={() => setSelectedCandidate(c.id)}
            className={`flex-1 p-4 rounded-xl border transition-all ${selectedCandidate === c.id ? 'border-violet-400 bg-violet-50 shadow-sm' : 'border-neutral-200 bg-white hover:border-neutral-300'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-neutral-900">{c.name}</p>
                <p className="text-xs text-neutral-500 mt-0.5">{c.assessments} assessments · {c.skills} skills tracked</p>
              </div>
              <div className="text-right">
                <p className={`text-xl font-bold ${c.avgScore >= 80 ? 'text-emerald-600' : c.avgScore >= 60 ? 'text-blue-600' : 'text-amber-600'}`}>{c.avgScore}</p>
                <p className="text-[10px] text-neutral-400">avg score</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Score cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {candidateScores.map(s => (
          <div key={s.id} className="bg-white rounded-xl border border-neutral-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="text-sm font-semibold text-neutral-900">{s.skill_or_technology}</h4>
                <span className="text-[10px] px-1.5 py-0.5 bg-neutral-100 text-neutral-600 rounded">{s.category}</span>
              </div>
              <div className="text-right">
                <p className={`text-2xl font-bold ${s.current_score >= 80 ? 'text-emerald-600' : s.current_score >= 60 ? 'text-blue-600' : s.current_score >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
                  {s.current_score}
                </p>
                <span className={`text-xs font-medium ${trendColor(s.trend)}`}>{trendIcon(s.trend)} {s.trend}</span>
              </div>
            </div>

            {/* Score bar */}
            <div className="h-2 bg-neutral-200 rounded-full mb-3">
              <div className={`h-2 rounded-full transition-all ${scoreBarColor(s.current_score)}`} style={{ width: `${s.current_score}%` }} />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex justify-between"><span className="text-neutral-500">Assessments:</span><span className="font-medium">{s.score_count}</span></div>
              <div className="flex justify-between"><span className="text-neutral-500">Confidence:</span><span className="font-medium">{Math.round(s.confidence_level * 100)}%</span></div>
              <div className="flex justify-between"><span className="text-neutral-500">Highest:</span><span className="text-emerald-600 font-medium">{s.highest_score}</span></div>
              <div className="flex justify-between"><span className="text-neutral-500">Lowest:</span><span className="text-red-600 font-medium">{s.lowest_score}</span></div>
            </div>

            {/* Score history mini chart */}
            {s.score_history.length > 1 && (
              <div className="mt-3 pt-3 border-t border-neutral-100">
                <p className="text-[10px] text-neutral-400 mb-1">Score History</p>
                <div className="flex items-end gap-1 h-8">
                  {s.score_history.map((h, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center">
                      <div className={`w-full rounded-t ${scoreBarColor(h.score)}`} style={{ height: `${(h.score / 100) * 32}px` }} />
                      <span className="text-[8px] text-neutral-400 mt-0.5">{h.date.slice(5)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <p className="text-[10px] text-neutral-400 mt-2">Last assessed: {s.last_assessed_at}</p>
          </div>
        ))}
      </div>

      {/* Score comparison across candidates */}
      <div className="bg-white rounded-xl border border-neutral-200 p-6">
        <h3 className="text-sm font-semibold text-neutral-900 mb-4">Cross-Candidate Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="text-left py-2 px-3 text-xs text-neutral-500">Skill</th>
                {candidates.map(c => (
                  <th key={c.id} className="text-center py-2 px-3 text-xs text-neutral-500">{c.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {['Python', 'SQL', 'React', 'Communication', 'Immigration'].map(skill => (
                <tr key={skill} className="border-b border-neutral-100">
                  <td className="py-2 px-3 text-sm font-medium text-neutral-900">{skill}</td>
                  {candidates.map(c => {
                    const score = persistentScores.find(s => s.candidate_id === c.id && s.skill_or_technology.includes(skill));
                    return (
                      <td key={c.id} className="py-2 px-3 text-center">
                        {score ? (
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${scoreBg(score.current_score)}`}>{score.current_score}</span>
                        ) : (
                          <span className="text-xs text-neutral-300">—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const JobMatchTab = () => (
    <div className="space-y-4">
      {/* Candidate selector */}
      <div className="flex gap-2">
        {candidates.map(c => (
          <button key={c.id} onClick={() => setSelectedCandidate(c.id)}
            className={`px-4 py-2 rounded-lg text-sm border ${selectedCandidate === c.id ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-neutral-600 border-neutral-200'}`}>
            {c.name}
          </button>
        ))}
      </div>

      {candidateMatches.length === 0 ? (
        <div className="bg-white rounded-xl border border-neutral-200 p-8 text-center text-neutral-500">No job match scores computed yet.</div>
      ) : (
        candidateMatches.map(m => (
          <div key={m.id} className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
            <div className="p-5 cursor-pointer" onClick={() => setExpandedMatch(expandedMatch === m.id ? null : m.id)}>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900">{m.requirement_title}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full text-white ${recBg[m.recommendation]}`}>{m.recommendation.replace(/_/g, ' ')}</span>
                    {m.risk_factors.length > 0 && <span className="text-[10px] px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full">{m.risk_factors.length} risk(s)</span>}
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-3xl font-bold ${m.overall_match_score >= 80 ? 'text-emerald-600' : m.overall_match_score >= 60 ? 'text-blue-600' : 'text-amber-600'}`}>
                    {m.overall_match_score}
                  </p>
                  <p className="text-[10px] text-neutral-400">match score</p>
                </div>
              </div>

              {/* Score bars summary */}
              <div className="grid grid-cols-7 gap-2 mt-4">
                {[
                  { l: 'Tech', v: m.technical_match_score }, { l: 'Exp', v: m.experience_match_score },
                  { l: 'Immig', v: m.immigration_match_score }, { l: 'Location', v: m.location_match_score },
                  { l: 'Avail', v: m.availability_match_score }, { l: 'Culture', v: m.culture_match_score },
                  { l: 'Comp', v: m.compensation_match_score },
                ].map(x => (
                  <div key={x.l} className="text-center">
                    <div className="h-12 flex items-end justify-center mb-1">
                      <div className={`w-6 rounded-t ${scoreBarColor(x.v)}`} style={{ height: `${(x.v / 100) * 48}px` }} />
                    </div>
                    <p className="text-[9px] text-neutral-500">{x.l}</p>
                    <p className="text-[10px] font-bold text-neutral-900">{x.v}</p>
                  </div>
                ))}
              </div>
            </div>

            {expandedMatch === m.id && (
              <div className="border-t border-neutral-100 p-5 bg-neutral-50">
                <div className="grid grid-cols-3 gap-6">
                  {/* Skill gap analysis */}
                  <div>
                    <h5 className="text-xs font-semibold text-neutral-700 mb-2">Skill Gap Analysis</h5>
                    <div className="space-y-2">
                      {m.matched_skills.map(sk => (
                        <div key={sk.skill} className="text-xs">
                          <div className="flex justify-between mb-0.5">
                            <span className="text-neutral-700">{sk.skill}</span>
                            <span className={`font-medium ${sk.gap > 0 ? 'text-emerald-600' : sk.gap < 0 ? 'text-red-600' : 'text-neutral-500'}`}>
                              {sk.gap > 0 ? `+${sk.gap}` : sk.gap}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-[9px] w-8 text-neutral-400">Req</span>
                            <div className="flex-1 h-1.5 bg-neutral-200 rounded-full"><div className="h-1.5 bg-neutral-400 rounded-full" style={{ width: `${sk.required_level}%` }} /></div>
                            <span className="text-[9px] w-6 text-right">{sk.required_level}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-[9px] w-8 text-neutral-400">Has</span>
                            <div className="flex-1 h-1.5 bg-neutral-200 rounded-full"><div className={`h-1.5 rounded-full ${scoreBarColor(sk.candidate_level)}`} style={{ width: `${sk.candidate_level}%` }} /></div>
                            <span className="text-[9px] w-6 text-right">{sk.candidate_level}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Missing & exceeding */}
                  <div>
                    <h5 className="text-xs font-semibold text-neutral-700 mb-2">Skills Summary</h5>
                    {m.exceeding_skills.length > 0 && (
                      <div className="mb-3">
                        <p className="text-[10px] text-emerald-600 font-medium mb-1">Exceeding Requirements</p>
                        <div className="flex flex-wrap gap-1">
                          {m.exceeding_skills.map(sk => <span key={sk} className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded">{sk}</span>)}
                        </div>
                      </div>
                    )}
                    {m.missing_skills.length > 0 && (
                      <div>
                        <p className="text-[10px] text-red-600 font-medium mb-1">Missing / Below Requirements</p>
                        <div className="flex flex-wrap gap-1">
                          {m.missing_skills.map(sk => <span key={sk} className="text-[10px] px-2 py-0.5 bg-red-100 text-red-700 rounded">{sk}</span>)}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Risk factors */}
                  <div>
                    <h5 className="text-xs font-semibold text-neutral-700 mb-2">Risk Factors</h5>
                    {m.risk_factors.length > 0 ? (
                      <div className="space-y-2">
                        {m.risk_factors.map((r, i) => (
                          <div key={i} className="flex items-start gap-2 p-2 bg-orange-50 rounded border border-orange-200">
                            <span className="text-orange-500 text-xs mt-0.5">⚠</span>
                            <span className="text-xs text-orange-800">{r}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-emerald-600">No significant risk factors identified.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );

  const RecommendationsTab = () => (
    <div className="space-y-6">
      <div className="bg-violet-50 rounded-xl border border-violet-200 p-4">
        <h3 className="text-sm font-semibold text-violet-900 mb-1">AI-Powered Recommendations</h3>
        <p className="text-xs text-violet-700">Based on accumulated interview scores over time, the system recommends matching jobs for each candidate. These scores improve in confidence as more interviews are conducted.</p>
      </div>

      {candidates.map(c => {
        const recs = recommendations[c.id] || [];
        const scores = persistentScores.filter(s => s.candidate_id === c.id);
        const avgScore = scores.length ? Math.round(scores.reduce((a, s) => a + s.current_score, 0) / scores.length) : 0;

        return (
          <div key={c.id} className="bg-white rounded-xl border border-neutral-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 font-bold">
                  {c.name.split(' ').map(w => w[0]).join('')}
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900">{c.name}</h4>
                  <p className="text-xs text-neutral-500">{scores.length} skills tracked · Avg score: {avgScore} · {c.assessments} interview(s)</p>
                </div>
              </div>
            </div>

            {/* Top skills bar */}
            <div className="flex gap-1 mb-4 flex-wrap">
              {scores.filter(s => s.category === 'technical' || s.category === 'framework' || s.category === 'system_design').map(s => (
                <span key={s.id} className={`text-[10px] px-2 py-0.5 rounded-full ${scoreBg(s.current_score)}`}>
                  {s.skill_or_technology}: {s.current_score}
                </span>
              ))}
            </div>

            {recs.length > 0 ? (
              <div className="space-y-3">
                {recs.map(r => (
                  <div key={r.requirement_id} className="flex items-start gap-4 p-3 bg-neutral-50 rounded-lg border border-neutral-100">
                    <div className="text-center">
                      <p className={`text-xl font-bold ${r.match_score >= 80 ? 'text-emerald-600' : r.match_score >= 60 ? 'text-blue-600' : 'text-amber-600'}`}>{r.match_score}</p>
                      <p className="text-[9px] text-neutral-400">match</p>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-neutral-900">{r.title}</p>
                      <p className="text-xs text-neutral-600 mt-0.5">{r.reason}</p>
                    </div>
                    <button className="px-3 py-1.5 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700 flex-shrink-0">Submit Candidate</button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-neutral-400">No recommendations yet. More assessments needed.</p>
            )}
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Candidate Score Intelligence</h1>
        <p className="text-neutral-500 mt-1">Persistent skill scores accumulated across interviews. Used for job matching and future recommendations.</p>
      </div>

      <div className="flex gap-1 bg-neutral-100 p-1 rounded-lg w-fit">
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm rounded-md transition-all ${tab === t ? 'bg-white text-neutral-900 shadow-sm font-medium' : 'text-neutral-600 hover:text-neutral-900'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Score Profiles' && <ScoreProfilesTab />}
      {tab === 'Job Match Analysis' && <JobMatchTab />}
      {tab === 'Recommendations' && <RecommendationsTab />}
    </div>
  );
};

export default CandidateScoreIntelligence;
