import React, { useState, useEffect, useRef } from 'react';

/* ─── helpers ─── */
const scoreBg = (s: number) => s >= 80 ? 'bg-emerald-100 text-emerald-800' : s >= 60 ? 'bg-blue-100 text-blue-800' : s >= 40 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';
const scoreBarColor = (s: number) => s >= 80 ? 'bg-emerald-500' : s >= 60 ? 'bg-blue-500' : s >= 40 ? 'bg-amber-500' : 'bg-red-500';
const trendIcon = (t: string) => t === 'improving' ? '↑' : t === 'declining' ? '↓' : '→';
const trendColor = (t: string) => t === 'improving' ? 'text-emerald-600' : t === 'declining' ? 'text-red-600' : 'text-neutral-500';

/* ─── Chart.js via CDN ─── */
declare global { interface Window { Chart: any } }

/* ─── types ─── */
interface ScoreHistory { date: string; score: number; interview_id: number }
interface PersistentScore {
  id: number; candidate_id: number; candidate_name: string;
  skill_or_technology: string; category: string;
  current_score: number; score_count: number; highest_score: number; lowest_score: number;
  confidence_level: number; trend: string; last_assessed_at: string;
  score_history: ScoreHistory[];
}
interface InterviewSummary {
  interview_id: number; date: string; candidate_name: string; candidate_id: number;
  job_title: string; interviewer: string; type: string;
  technical_score: number; communication_score: number; immigration_score: number;
  location_score: number; availability_score: number; overall_score: number;
}

/* ─── color palette ─── */
const COLORS = [
  '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#6366f1',
];
const CATEGORY_COLORS: Record<string, string> = {
  technical: '#3b82f6', framework: '#8b5cf6', communication: '#10b981',
  immigration: '#f59e0b', system_design: '#06b6d4', experience: '#ec4899',
  location: '#14b8a6', availability: '#f97316',
};

/* ─── mock data: persistent scores ─── */
const persistentScores: PersistentScore[] = [
  { id: 1, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Python', category: 'technical', current_score: 90, score_count: 4, highest_score: 100, lowest_score: 60, confidence_level: 0.85, trend: 'improving', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-01-15', score: 60, interview_id: 90 }, { date: '2026-02-10', score: 75, interview_id: 95 }, { date: '2026-03-10', score: 80, interview_id: 101 }, { date: '2026-03-14', score: 100, interview_id: 104 }] },
  { id: 2, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'SQL', category: 'technical', current_score: 80, score_count: 3, highest_score: 80, lowest_score: 60, confidence_level: 0.80, trend: 'improving', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-01-15', score: 60, interview_id: 90 }, { date: '2026-03-10', score: 80, interview_id: 101 }, { date: '2026-03-14', score: 80, interview_id: 104 }] },
  { id: 3, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'React', category: 'framework', current_score: 40, score_count: 2, highest_score: 40, lowest_score: 20, confidence_level: 0.45, trend: 'improving', last_assessed_at: '2026-03-10', score_history: [{ date: '2026-01-15', score: 20, interview_id: 90 }, { date: '2026-03-10', score: 40, interview_id: 101 }] },
  { id: 4, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'AWS', category: 'technical', current_score: 60, score_count: 2, highest_score: 60, lowest_score: 40, confidence_level: 0.50, trend: 'improving', last_assessed_at: '2026-03-10', score_history: [{ date: '2026-02-10', score: 40, interview_id: 95 }, { date: '2026-03-10', score: 60, interview_id: 101 }] },
  { id: 5, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Communication', category: 'communication', current_score: 80, score_count: 3, highest_score: 80, lowest_score: 60, confidence_level: 0.82, trend: 'improving', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-01-15', score: 60, interview_id: 90 }, { date: '2026-02-10', score: 70, interview_id: 95 }, { date: '2026-03-14', score: 80, interview_id: 104 }] },
  { id: 6, candidate_id: 1, candidate_name: 'Rajesh Kumar', skill_or_technology: 'Immigration (H1B)', category: 'immigration', current_score: 60, score_count: 3, highest_score: 60, lowest_score: 40, confidence_level: 0.75, trend: 'improving', last_assessed_at: '2026-03-14', score_history: [{ date: '2026-01-15', score: 40, interview_id: 90 }, { date: '2026-02-10', score: 50, interview_id: 95 }, { date: '2026-03-14', score: 60, interview_id: 104 }] },
  { id: 10, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'Python', category: 'technical', current_score: 100, score_count: 3, highest_score: 100, lowest_score: 80, confidence_level: 0.85, trend: 'improving', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-01-20', score: 80, interview_id: 91 }, { date: '2026-02-18', score: 90, interview_id: 96 }, { date: '2026-03-11', score: 100, interview_id: 102 }] },
  { id: 11, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'SQL', category: 'technical', current_score: 80, score_count: 2, highest_score: 80, lowest_score: 60, confidence_level: 0.65, trend: 'improving', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-01-20', score: 60, interview_id: 91 }, { date: '2026-03-11', score: 80, interview_id: 102 }] },
  { id: 12, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'React', category: 'framework', current_score: 60, score_count: 2, highest_score: 60, lowest_score: 40, confidence_level: 0.55, trend: 'improving', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-02-18', score: 40, interview_id: 96 }, { date: '2026-03-11', score: 60, interview_id: 102 }] },
  { id: 13, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'System Design', category: 'system_design', current_score: 80, score_count: 2, highest_score: 80, lowest_score: 60, confidence_level: 0.60, trend: 'improving', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-01-20', score: 60, interview_id: 91 }, { date: '2026-03-11', score: 80, interview_id: 102 }] },
  { id: 14, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'Communication', category: 'communication', current_score: 100, score_count: 3, highest_score: 100, lowest_score: 80, confidence_level: 0.85, trend: 'improving', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-01-20', score: 80, interview_id: 91 }, { date: '2026-02-18', score: 90, interview_id: 96 }, { date: '2026-03-11', score: 100, interview_id: 102 }] },
  { id: 15, candidate_id: 2, candidate_name: 'Emily Chen', skill_or_technology: 'Immigration', category: 'immigration', current_score: 100, score_count: 2, highest_score: 100, lowest_score: 100, confidence_level: 0.80, trend: 'stable', last_assessed_at: '2026-03-11', score_history: [{ date: '2026-01-20', score: 100, interview_id: 91 }, { date: '2026-03-11', score: 100, interview_id: 102 }] },
  { id: 20, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'Python', category: 'technical', current_score: 60, score_count: 3, highest_score: 80, lowest_score: 40, confidence_level: 0.65, trend: 'declining', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-01-25', score: 80, interview_id: 92 }, { date: '2026-02-22', score: 60, interview_id: 97 }, { date: '2026-03-12', score: 60, interview_id: 103 }] },
  { id: 21, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'SQL', category: 'technical', current_score: 60, score_count: 2, highest_score: 60, lowest_score: 40, confidence_level: 0.50, trend: 'improving', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-01-25', score: 40, interview_id: 92 }, { date: '2026-03-12', score: 60, interview_id: 103 }] },
  { id: 22, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'React', category: 'framework', current_score: 80, score_count: 3, highest_score: 80, lowest_score: 60, confidence_level: 0.70, trend: 'improving', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-01-25', score: 60, interview_id: 92 }, { date: '2026-02-22', score: 70, interview_id: 97 }, { date: '2026-03-12', score: 80, interview_id: 103 }] },
  { id: 23, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'Immigration (OPT)', category: 'immigration', current_score: 40, score_count: 2, highest_score: 40, lowest_score: 40, confidence_level: 0.55, trend: 'stable', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-01-25', score: 40, interview_id: 92 }, { date: '2026-03-12', score: 40, interview_id: 103 }] },
  { id: 24, candidate_id: 3, candidate_name: 'Marcus Johnson', skill_or_technology: 'Communication', category: 'communication', current_score: 80, score_count: 2, highest_score: 80, lowest_score: 60, confidence_level: 0.55, trend: 'improving', last_assessed_at: '2026-03-12', score_history: [{ date: '2026-01-25', score: 60, interview_id: 92 }, { date: '2026-03-12', score: 80, interview_id: 103 }] },
  { id: 30, candidate_id: 4, candidate_name: 'Sarah Williams', skill_or_technology: 'Python', category: 'technical', current_score: 80, score_count: 3, highest_score: 80, lowest_score: 60, confidence_level: 0.75, trend: 'improving', last_assessed_at: '2026-03-13', score_history: [{ date: '2026-01-28', score: 60, interview_id: 93 }, { date: '2026-02-25', score: 70, interview_id: 98 }, { date: '2026-03-13', score: 80, interview_id: 105 }] },
  { id: 31, candidate_id: 4, candidate_name: 'Sarah Williams', skill_or_technology: 'React', category: 'framework', current_score: 100, score_count: 3, highest_score: 100, lowest_score: 80, confidence_level: 0.85, trend: 'improving', last_assessed_at: '2026-03-13', score_history: [{ date: '2026-01-28', score: 80, interview_id: 93 }, { date: '2026-02-25', score: 90, interview_id: 98 }, { date: '2026-03-13', score: 100, interview_id: 105 }] },
  { id: 32, candidate_id: 4, candidate_name: 'Sarah Williams', skill_or_technology: 'Communication', category: 'communication', current_score: 80, score_count: 2, highest_score: 80, lowest_score: 80, confidence_level: 0.60, trend: 'stable', last_assessed_at: '2026-03-13', score_history: [{ date: '2026-02-25', score: 80, interview_id: 98 }, { date: '2026-03-13', score: 80, interview_id: 105 }] },
  { id: 33, candidate_id: 4, candidate_name: 'Sarah Williams', skill_or_technology: 'Immigration', category: 'immigration', current_score: 100, score_count: 1, highest_score: 100, lowest_score: 100, confidence_level: 0.55, trend: 'stable', last_assessed_at: '2026-03-13', score_history: [{ date: '2026-03-13', score: 100, interview_id: 105 }] },
];

/* ─── mock data: interview summaries (dimension scores across interviews) ─── */
const interviewSummaries: InterviewSummary[] = [
  { interview_id: 90, date: '2026-01-15', candidate_name: 'Rajesh Kumar', candidate_id: 1, job_title: 'Sr Python Developer', interviewer: 'Alice Morgan', type: 'Technical', technical_score: 55, communication_score: 60, immigration_score: 40, location_score: 80, availability_score: 80, overall_score: 58 },
  { interview_id: 95, date: '2026-02-10', candidate_name: 'Rajesh Kumar', candidate_id: 1, job_title: 'Sr Python Developer', interviewer: 'Bob Chen', type: 'Technical', technical_score: 68, communication_score: 70, immigration_score: 50, location_score: 80, availability_score: 80, overall_score: 67 },
  { interview_id: 101, date: '2026-03-10', candidate_name: 'Rajesh Kumar', candidate_id: 1, job_title: 'Data Engineer', interviewer: 'Alice Morgan', type: 'Technical', technical_score: 75, communication_score: 75, immigration_score: 55, location_score: 80, availability_score: 100, overall_score: 74 },
  { interview_id: 104, date: '2026-03-14', candidate_name: 'Rajesh Kumar', candidate_id: 1, job_title: 'Data Engineer', interviewer: 'Carol Davis', type: 'AI Bot', technical_score: 88, communication_score: 80, immigration_score: 60, location_score: 80, availability_score: 100, overall_score: 82 },
  { interview_id: 91, date: '2026-01-20', candidate_name: 'Emily Chen', candidate_id: 2, job_title: 'Full Stack Engineer', interviewer: 'Bob Chen', type: 'Technical', technical_score: 78, communication_score: 80, immigration_score: 100, location_score: 100, availability_score: 80, overall_score: 82 },
  { interview_id: 96, date: '2026-02-18', candidate_name: 'Emily Chen', candidate_id: 2, job_title: 'Full Stack Engineer', interviewer: 'Alice Morgan', type: 'Technical', technical_score: 82, communication_score: 90, immigration_score: 100, location_score: 100, availability_score: 80, overall_score: 87 },
  { interview_id: 102, date: '2026-03-11', candidate_name: 'Emily Chen', candidate_id: 2, job_title: 'Sr Python Developer', interviewer: 'Carol Davis', type: 'AI Bot', technical_score: 92, communication_score: 100, immigration_score: 100, location_score: 100, availability_score: 80, overall_score: 94 },
  { interview_id: 92, date: '2026-01-25', candidate_name: 'Marcus Johnson', candidate_id: 3, job_title: 'React Developer', interviewer: 'Bob Chen', type: 'Technical', technical_score: 65, communication_score: 60, immigration_score: 40, location_score: 60, availability_score: 80, overall_score: 60 },
  { interview_id: 97, date: '2026-02-22', candidate_name: 'Marcus Johnson', candidate_id: 3, job_title: 'React Developer', interviewer: 'Alice Morgan', type: 'Behavioral', technical_score: 60, communication_score: 70, immigration_score: 40, location_score: 60, availability_score: 80, overall_score: 61 },
  { interview_id: 103, date: '2026-03-12', candidate_name: 'Marcus Johnson', candidate_id: 3, job_title: 'Full Stack Engineer', interviewer: 'Carol Davis', type: 'AI Bot', technical_score: 68, communication_score: 80, immigration_score: 40, location_score: 60, availability_score: 100, overall_score: 66 },
  { interview_id: 93, date: '2026-01-28', candidate_name: 'Sarah Williams', candidate_id: 4, job_title: 'Frontend Lead', interviewer: 'Bob Chen', type: 'Technical', technical_score: 70, communication_score: 75, immigration_score: 100, location_score: 100, availability_score: 80, overall_score: 78 },
  { interview_id: 98, date: '2026-02-25', candidate_name: 'Sarah Williams', candidate_id: 4, job_title: 'Frontend Lead', interviewer: 'Alice Morgan', type: 'Technical', technical_score: 82, communication_score: 80, immigration_score: 100, location_score: 100, availability_score: 80, overall_score: 86 },
  { interview_id: 105, date: '2026-03-13', candidate_name: 'Sarah Williams', candidate_id: 4, job_title: 'Sr React Developer', interviewer: 'Carol Davis', type: 'AI Bot', technical_score: 90, communication_score: 80, immigration_score: 100, location_score: 100, availability_score: 100, overall_score: 92 },
];

/* ─── Chart.js hook ─── */
function useChart(canvasRef: React.RefObject<HTMLCanvasElement | null>, config: any, deps: any[]) {
  const chartRef = useRef<any>(null);
  useEffect(() => {
    if (!canvasRef.current || !window.Chart) return;
    if (chartRef.current) chartRef.current.destroy();
    chartRef.current = new window.Chart(canvasRef.current, config);
    return () => { if (chartRef.current) chartRef.current.destroy(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

/* ═══════════════════════ COMPONENT ═══════════════════════ */
export default function ScoreAnalyticsDashboard() {
  const [activeTab, setActiveTab] = useState<'trends' | 'dimensions' | 'compare' | 'heatmap'>('trends');
  const [selectedCandidate, setSelectedCandidate] = useState(1);
  const [chartLoaded, setChartLoaded] = useState(!!window.Chart);

  /* Load Chart.js from CDN */
  useEffect(() => {
    if (window.Chart) { setChartLoaded(true); return; }
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';
    s.onload = () => setChartLoaded(true);
    document.head.appendChild(s);
  }, []);

  /* Derived data */
  const candidates = [...new Map(persistentScores.map(s => [s.candidate_id, { id: s.candidate_id, name: s.candidate_name }])).values()];
  const candidateScores = persistentScores.filter(s => s.candidate_id === selectedCandidate);
  const candidateInterviews = interviewSummaries.filter(i => i.candidate_id === selectedCandidate).sort((a, b) => a.date.localeCompare(b.date));

  /* KPIs */
  const avgTech = Math.round(candidateScores.filter(s => s.category === 'technical').reduce((a, s) => a + s.current_score, 0) / Math.max(candidateScores.filter(s => s.category === 'technical').length, 1));
  const avgComm = Math.round(candidateScores.filter(s => s.category === 'communication').reduce((a, s) => a + s.current_score, 0) / Math.max(candidateScores.filter(s => s.category === 'communication').length, 1));
  const avgImmig = Math.round(candidateScores.filter(s => s.category === 'immigration').reduce((a, s) => a + s.current_score, 0) / Math.max(candidateScores.filter(s => s.category === 'immigration').length, 1));
  const totalInterviews = candidateInterviews.length;
  const improvingCount = candidateScores.filter(s => s.trend === 'improving').length;

  /* ─── Tab: Skill Score Trends (line chart) ─── */
  const trendCanvasRef = useRef<HTMLCanvasElement | null>(null);
  useChart(trendCanvasRef, {
    type: 'line',
    data: {
      datasets: candidateScores.map((s, i) => ({
        label: s.skill_or_technology,
        data: s.score_history.map(h => ({ x: h.date, y: h.score })),
        borderColor: CATEGORY_COLORS[s.category] || COLORS[i % COLORS.length],
        backgroundColor: (CATEGORY_COLORS[s.category] || COLORS[i % COLORS.length]) + '22',
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: `Skill Score Trends — ${candidates.find(c => c.id === selectedCandidate)?.name}`, font: { size: 16 } },
        legend: { position: 'bottom' as const },
        tooltip: { callbacks: { label: (ctx: any) => `${ctx.dataset.label}: ${ctx.parsed.y}/100` } },
      },
      scales: {
        x: { type: 'time' as const, time: { unit: 'week' as const, tooltipFormat: 'MMM dd, yyyy' }, title: { display: true, text: 'Interview Date' } },
        y: { min: 0, max: 100, title: { display: true, text: 'Score' } },
      },
    },
  }, [selectedCandidate, chartLoaded]);

  /* ─── Tab: Dimension Scores (stacked bar per interview) ─── */
  const dimCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const dimLabels = candidateInterviews.map(i => `${i.date}\n${i.type}`);
  useChart(dimCanvasRef, {
    type: 'bar',
    data: {
      labels: dimLabels,
      datasets: [
        { label: 'Technical', data: candidateInterviews.map(i => i.technical_score), backgroundColor: '#3b82f6' },
        { label: 'Communication', data: candidateInterviews.map(i => i.communication_score), backgroundColor: '#10b981' },
        { label: 'Immigration', data: candidateInterviews.map(i => i.immigration_score), backgroundColor: '#f59e0b' },
        { label: 'Location', data: candidateInterviews.map(i => i.location_score), backgroundColor: '#06b6d4' },
        { label: 'Availability', data: candidateInterviews.map(i => i.availability_score), backgroundColor: '#8b5cf6' },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: `Interview Dimension Scores — ${candidates.find(c => c.id === selectedCandidate)?.name}`, font: { size: 16 } },
        legend: { position: 'bottom' as const },
      },
      scales: {
        x: { title: { display: true, text: 'Interview' } },
        y: { min: 0, max: 100, title: { display: true, text: 'Score' } },
      },
    },
  }, [selectedCandidate, chartLoaded]);

  /* ─── Tab: Cross-Candidate Comparison (radar) ─── */
  const radarCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const sharedSkills = ['Python', 'SQL', 'React', 'Communication'];
  useChart(radarCanvasRef, {
    type: 'radar',
    data: {
      labels: sharedSkills,
      datasets: candidates.map((c, ci) => {
        const cScores = persistentScores.filter(s => s.candidate_id === c.id);
        return {
          label: c.name,
          data: sharedSkills.map(sk => cScores.find(s => s.skill_or_technology === sk)?.current_score ?? 0),
          borderColor: COLORS[ci],
          backgroundColor: COLORS[ci] + '22',
          borderWidth: 2,
          pointBackgroundColor: COLORS[ci],
        };
      }),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'Cross-Candidate Skill Comparison', font: { size: 16 } },
        legend: { position: 'bottom' as const },
      },
      scales: { r: { min: 0, max: 100, ticks: { stepSize: 20 } } },
    },
  }, [chartLoaded]);

  /* ─── Tab: Heatmap (HTML table-based) ─── */
  const allSkills = [...new Set(persistentScores.map(s => s.skill_or_technology))];
  const heatmapCell = (score: number | undefined) => {
    if (score === undefined) return <td className="p-2 text-center text-xs text-neutral-300">—</td>;
    const bg = score >= 80 ? 'bg-emerald-500 text-white' : score >= 60 ? 'bg-blue-500 text-white' : score >= 40 ? 'bg-amber-400 text-white' : 'bg-red-500 text-white';
    return <td className={`p-2 text-center text-xs font-semibold rounded ${bg}`}>{score}</td>;
  };

  /* ─── Overall score evolution line (all candidates) ─── */
  const overallCanvasRef = useRef<HTMLCanvasElement | null>(null);
  useChart(overallCanvasRef, {
    type: 'line',
    data: {
      datasets: candidates.map((c, ci) => {
        const cInterviews = interviewSummaries.filter(i => i.candidate_id === c.id).sort((a, b) => a.date.localeCompare(b.date));
        return {
          label: c.name,
          data: cInterviews.map(i => ({ x: i.date, y: i.overall_score })),
          borderColor: COLORS[ci],
          backgroundColor: COLORS[ci] + '22',
          fill: false,
          tension: 0.3,
          pointRadius: 6,
          borderWidth: 2.5,
        };
      }),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'Overall Score Evolution — All Candidates', font: { size: 16 } },
        legend: { position: 'bottom' as const },
      },
      scales: {
        x: { type: 'time' as const, time: { unit: 'week' as const, tooltipFormat: 'MMM dd, yyyy' }, title: { display: true, text: 'Date' } },
        y: { min: 0, max: 100, title: { display: true, text: 'Overall Score' } },
      },
    },
  }, [chartLoaded]);

  const tabs = [
    { key: 'trends' as const, label: 'Skill Trends', icon: '📈' },
    { key: 'dimensions' as const, label: 'Dimension Analysis', icon: '📊' },
    { key: 'compare' as const, label: 'Cross-Candidate', icon: '🔀' },
    { key: 'heatmap' as const, label: 'Score Heatmap', icon: '🗺️' },
  ];

  return (
    <div className="p-6 max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Score Analytics Dashboard</h1>
          <p className="text-sm text-neutral-500 mt-1">Visualize candidate score trends and evolution across interviews</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-neutral-500">Candidate:</span>
          <select className="border rounded-lg px-3 py-1.5 text-sm" value={selectedCandidate} onChange={e => setSelectedCandidate(Number(e.target.value))}>
            {candidates.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-5 gap-4">
        {[
          { label: 'Avg Technical', value: avgTech, color: 'blue' },
          { label: 'Avg Communication', value: avgComm, color: 'emerald' },
          { label: 'Avg Immigration', value: avgImmig, color: 'amber' },
          { label: 'Interviews', value: totalInterviews, color: 'violet' },
          { label: 'Improving Skills', value: improvingCount, color: 'cyan' },
        ].map((kpi, i) => (
          <div key={i} className="bg-white rounded-xl border p-4 text-center shadow-sm">
            <p className="text-xs text-neutral-500 uppercase tracking-wide">{kpi.label}</p>
            <p className={`text-3xl font-bold mt-1 text-${kpi.color}-600`}>{kpi.value}{typeof kpi.value === 'number' && kpi.label.startsWith('Avg') ? '/100' : ''}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-neutral-100 rounded-lg p-1 w-fit">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === t.key ? 'bg-white shadow text-neutral-900' : 'text-neutral-500 hover:text-neutral-700'}`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Chart.js loading guard */}
      {!chartLoaded && (
        <div className="bg-white rounded-xl border p-12 text-center">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
          <p className="text-neutral-500 text-sm">Loading Chart.js...</p>
        </div>
      )}

      {/* Tab: Skill Trends */}
      {chartLoaded && activeTab === 'trends' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border p-6 shadow-sm" style={{ height: 420 }}>
            <canvas ref={trendCanvasRef} />
          </div>

          {/* Score cards grid */}
          <div className="grid grid-cols-3 gap-4">
            {candidateScores.map(s => (
              <div key={s.id} className="bg-white rounded-xl border p-4 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`inline-block w-2.5 h-2.5 rounded-full`} style={{ backgroundColor: CATEGORY_COLORS[s.category] || '#6b7280' }} />
                    <span className="font-semibold text-sm">{s.skill_or_technology}</span>
                    <span className="text-[10px] text-neutral-400 uppercase">{s.category}</span>
                  </div>
                  <span className={`text-sm font-bold ${trendColor(s.trend)}`}>{trendIcon(s.trend)} {s.trend}</span>
                </div>
                <div className="flex items-end gap-3 mb-2">
                  <span className={`text-2xl font-bold px-2 py-0.5 rounded ${scoreBg(s.current_score)}`}>{s.current_score}</span>
                  <span className="text-xs text-neutral-400">/ 100</span>
                  <span className="text-xs text-neutral-400 ml-auto">{s.score_count} assessment{s.score_count > 1 ? 's' : ''}</span>
                </div>
                <div className="h-2 bg-neutral-100 rounded-full overflow-hidden mb-2">
                  <div className={`h-full rounded-full ${scoreBarColor(s.current_score)}`} style={{ width: `${s.current_score}%` }} />
                </div>
                <div className="flex justify-between text-[10px] text-neutral-400">
                  <span>Low: {s.lowest_score}</span>
                  <span>Confidence: {Math.round(s.confidence_level * 100)}%</span>
                  <span>High: {s.highest_score}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Dimension Analysis */}
      {chartLoaded && activeTab === 'dimensions' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border p-6 shadow-sm" style={{ height: 420 }}>
            <canvas ref={dimCanvasRef} />
          </div>

          {/* Interview detail table */}
          <div className="bg-white rounded-xl border overflow-hidden shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-neutral-50 text-neutral-600">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Date</th>
                  <th className="px-4 py-3 text-left font-medium">Job</th>
                  <th className="px-4 py-3 text-left font-medium">Type</th>
                  <th className="px-4 py-3 text-left font-medium">Interviewer</th>
                  <th className="px-4 py-3 text-center font-medium">Tech</th>
                  <th className="px-4 py-3 text-center font-medium">Comm</th>
                  <th className="px-4 py-3 text-center font-medium">Immig</th>
                  <th className="px-4 py-3 text-center font-medium">Location</th>
                  <th className="px-4 py-3 text-center font-medium">Avail</th>
                  <th className="px-4 py-3 text-center font-medium">Overall</th>
                </tr>
              </thead>
              <tbody>
                {candidateInterviews.map(i => (
                  <tr key={i.interview_id} className="border-t hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium">{i.date}</td>
                    <td className="px-4 py-3">{i.job_title}</td>
                    <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded text-xs ${i.type === 'AI Bot' ? 'bg-violet-100 text-violet-700' : i.type === 'Behavioral' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}`}>{i.type}</span></td>
                    <td className="px-4 py-3 text-neutral-600">{i.interviewer}</td>
                    {[i.technical_score, i.communication_score, i.immigration_score, i.location_score, i.availability_score, i.overall_score].map((score, si) => (
                      <td key={si} className="px-4 py-3 text-center">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(score)}`}>{score}</span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Delta analysis */}
          {candidateInterviews.length >= 2 && (
            <div className="bg-white rounded-xl border p-5 shadow-sm">
              <h3 className="font-semibold text-neutral-800 mb-3">Score Change: First → Latest Interview</h3>
              <div className="grid grid-cols-5 gap-4">
                {(['technical_score', 'communication_score', 'immigration_score', 'location_score', 'availability_score'] as const).map(dim => {
                  const first = candidateInterviews[0][dim];
                  const last = candidateInterviews[candidateInterviews.length - 1][dim];
                  const delta = last - first;
                  return (
                    <div key={dim} className="text-center">
                      <p className="text-xs text-neutral-500 capitalize mb-1">{dim.replace('_score', '').replace('_', ' ')}</p>
                      <p className="text-lg font-bold">{first} → {last}</p>
                      <p className={`text-sm font-semibold ${delta > 0 ? 'text-emerald-600' : delta < 0 ? 'text-red-600' : 'text-neutral-500'}`}>{delta > 0 ? '+' : ''}{delta} pts</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Cross-Candidate Comparison */}
      {chartLoaded && activeTab === 'compare' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border p-6 shadow-sm" style={{ height: 420 }}>
              <canvas ref={radarCanvasRef} />
            </div>
            <div className="bg-white rounded-xl border p-6 shadow-sm" style={{ height: 420 }}>
              <canvas ref={overallCanvasRef} />
            </div>
          </div>

          {/* Ranking table */}
          <div className="bg-white rounded-xl border overflow-hidden shadow-sm">
            <div className="px-5 py-3 bg-neutral-50 font-semibold text-neutral-700 text-sm">Candidate Rankings by Dimension</div>
            <table className="w-full text-sm">
              <thead className="bg-neutral-50 text-neutral-600">
                <tr>
                  <th className="px-4 py-2 text-left font-medium">Candidate</th>
                  <th className="px-4 py-2 text-center font-medium">Avg Technical</th>
                  <th className="px-4 py-2 text-center font-medium">Avg Communication</th>
                  <th className="px-4 py-2 text-center font-medium">Avg Immigration</th>
                  <th className="px-4 py-2 text-center font-medium">Interviews</th>
                  <th className="px-4 py-2 text-center font-medium">Latest Overall</th>
                  <th className="px-4 py-2 text-center font-medium">Trend</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map(c => {
                  const cScores = persistentScores.filter(s => s.candidate_id === c.id);
                  const cInterviews = interviewSummaries.filter(i => i.candidate_id === c.id).sort((a, b) => b.date.localeCompare(a.date));
                  const techAvg = Math.round(cScores.filter(s => s.category === 'technical').reduce((a, s) => a + s.current_score, 0) / Math.max(cScores.filter(s => s.category === 'technical').length, 1));
                  const commAvg = Math.round(cScores.filter(s => s.category === 'communication').reduce((a, s) => a + s.current_score, 0) / Math.max(cScores.filter(s => s.category === 'communication').length, 1));
                  const immigAvg = Math.round(cScores.filter(s => s.category === 'immigration').reduce((a, s) => a + s.current_score, 0) / Math.max(cScores.filter(s => s.category === 'immigration').length, 1));
                  const latestOverall = cInterviews[0]?.overall_score ?? 0;
                  const improvCount = cScores.filter(s => s.trend === 'improving').length;
                  const totalCount = cScores.length;
                  return (
                    <tr key={c.id} className="border-t hover:bg-neutral-50">
                      <td className="px-4 py-3 font-semibold">{c.name}</td>
                      <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(techAvg)}`}>{techAvg}</span></td>
                      <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(commAvg)}`}>{commAvg}</span></td>
                      <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(immigAvg)}`}>{immigAvg}</span></td>
                      <td className="px-4 py-3 text-center">{cInterviews.length}</td>
                      <td className="px-4 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-semibold ${scoreBg(latestOverall)}`}>{latestOverall}</span></td>
                      <td className="px-4 py-3 text-center text-xs">
                        <span className="text-emerald-600">{improvCount} ↑</span> / <span className="text-neutral-400">{totalCount - improvCount}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Score Heatmap */}
      {chartLoaded && activeTab === 'heatmap' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border overflow-hidden shadow-sm">
            <div className="px-5 py-3 bg-neutral-50 font-semibold text-neutral-700 text-sm">Candidate × Skill Score Heatmap</div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50 text-neutral-600">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Candidate</th>
                    {allSkills.map(sk => <th key={sk} className="px-3 py-2 text-center font-medium text-xs whitespace-nowrap">{sk}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {candidates.map(c => {
                    const cScores = persistentScores.filter(s => s.candidate_id === c.id);
                    return (
                      <tr key={c.id} className="border-t">
                        <td className="px-4 py-2 font-semibold whitespace-nowrap">{c.name}</td>
                        {allSkills.map(sk => {
                          const score = cScores.find(s => s.skill_or_technology === sk);
                          return heatmapCell(score?.current_score);
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Confidence map */}
          <div className="bg-white rounded-xl border overflow-hidden shadow-sm">
            <div className="px-5 py-3 bg-neutral-50 font-semibold text-neutral-700 text-sm">Confidence Level Map (higher = more assessments)</div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50 text-neutral-600">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Candidate</th>
                    {allSkills.map(sk => <th key={sk} className="px-3 py-2 text-center font-medium text-xs whitespace-nowrap">{sk}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {candidates.map(c => {
                    const cScores = persistentScores.filter(s => s.candidate_id === c.id);
                    return (
                      <tr key={c.id} className="border-t">
                        <td className="px-4 py-2 font-semibold whitespace-nowrap">{c.name}</td>
                        {allSkills.map(sk => {
                          const score = cScores.find(s => s.skill_or_technology === sk);
                          if (!score) return <td key={sk} className="p-2 text-center text-xs text-neutral-300">—</td>;
                          const conf = Math.round(score.confidence_level * 100);
                          const bg = conf >= 75 ? 'bg-emerald-100 text-emerald-800' : conf >= 50 ? 'bg-blue-100 text-blue-800' : 'bg-neutral-100 text-neutral-600';
                          return <td key={sk} className={`p-2 text-center text-xs font-semibold rounded ${bg}`}>{conf}%</td>;
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-6 text-xs text-neutral-500">
            <span>Score Legend:</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500" /> 80-100 Excellent</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-500" /> 60-79 Good</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-400" /> 40-59 Fair</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500" /> 0-39 Needs Improvement</span>
          </div>
        </div>
      )}
    </div>
  );
}
