import React, { useState, useEffect } from 'react';

interface ResumeCapture {
  id: number; candidate_name: string | null; candidate_email: string | null;
  source_type: string; attachment_filename: string | null;
  parsed_successfully: boolean; skills_extracted: string[] | null;
  experience_years: number | null; current_title: string | null;
  current_company: string | null; match_score: number | null;
  match_level: string | null; match_breakdown: Record<string, number> | null;
  recommendation: string | null; recommendation_notes: string | null;
  added_to_platform: boolean; review_status: string | null;
  email_subject: string | null; email_from: string | null;
}

const matchLevelColors: Record<string, string> = {
  excellent: 'bg-green-100 text-green-700 border-green-300',
  strong: 'bg-blue-100 text-blue-700 border-blue-300',
  good: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  fair: 'bg-orange-100 text-orange-700 border-orange-300',
  poor: 'bg-red-100 text-red-700 border-red-300',
};

const recColors: Record<string, string> = {
  strong_yes: 'bg-green-500 text-white', yes: 'bg-green-100 text-green-700',
  maybe: 'bg-yellow-100 text-yellow-700', no: 'bg-red-100 text-red-700',
};

const mockCaptures: ResumeCapture[] = [
  {
    id: 1, candidate_name: "Priya Sharma", candidate_email: "priya.sharma@gmail.com",
    source_type: "email_attachment", attachment_filename: "PriyaSharma_Resume.pdf",
    parsed_successfully: true,
    skills_extracted: ["Python", "Django", "FastAPI", "AWS", "PostgreSQL", "Docker", "Kubernetes", "Redis", "Celery", "React"],
    experience_years: 8.0, current_title: "Senior Software Engineer", current_company: "DataFlow Inc.",
    match_score: 87.5, match_level: "strong",
    match_breakdown: { skills: 92, experience: 88, education: 85, location: 80, culture_fit: 82 },
    recommendation: "strong_yes",
    recommendation_notes: "Excellent match for Senior Python Developer role. 8 years experience with strong backend skills. Django/FastAPI expertise directly applicable.",
    added_to_platform: true, review_status: "pending",
    email_subject: "New application: Priya Sharma applied for Senior Python Developer",
    email_from: "apply+candidate@jobs.linkedin.com",
  },
  {
    id: 2, candidate_name: "Amit Patel", candidate_email: "amit.patel@gmail.com",
    source_type: "email_attachment", attachment_filename: "AmitPatel_CV.pdf",
    parsed_successfully: true,
    skills_extracted: ["React Native", "JavaScript", "TypeScript", "iOS", "Android", "Redux", "GraphQL", "Firebase", "Node.js", "Jest"],
    experience_years: 5.5, current_title: "Mobile Developer", current_company: "AppWorks Studio",
    match_score: 72.0, match_level: "good",
    match_breakdown: { skills: 85, experience: 68, education: 65, location: 70, culture_fit: 75 },
    recommendation: "yes",
    recommendation_notes: "Good match for React Native Developer. 5+ years mobile experience with strong React Native/TypeScript skills.",
    added_to_platform: true, review_status: "pending",
    email_subject: "Application for React Native Developer Position",
    email_from: "amit.patel@gmail.com",
  },
  {
    id: 3, candidate_name: "Carlos Rivera", candidate_email: "c.rivera@yahoo.com",
    source_type: "email_attachment", attachment_filename: "resume_carlos_r.docx",
    parsed_successfully: true,
    skills_extracted: ["Data Engineering", "Python", "Spark", "Snowflake", "dbt", "Airflow", "SQL", "Terraform", "GCP", "BigQuery"],
    experience_years: 6.0, current_title: "Data Engineer", current_company: "InsightPro Analytics",
    match_score: 91.0, match_level: "excellent",
    match_breakdown: { skills: 95, experience: 85, education: 88, location: 92, culture_fit: 90 },
    recommendation: "strong_yes",
    recommendation_notes: "Excellent match for Data Engineer role at TechCorp. 6 years with Spark/Snowflake/dbt — exact tech stack match.",
    added_to_platform: true, review_status: "approved",
    email_subject: "Candidate Submission: Carlos Rivera for Data Engineer",
    email_from: "michael.chen@staffpro.com",
  },
  {
    id: 4, candidate_name: "Deepa Krishnan", candidate_email: "deepa.k@outlook.com",
    source_type: "email_attachment", attachment_filename: "DeepaKrishnan_Resume_2026.pdf",
    parsed_successfully: true,
    skills_extracted: ["Java", "Spring Boot", "Microservices", "Kafka", "AWS", "Docker", "Jenkins", "MongoDB", "Oracle", "Agile"],
    experience_years: 10.0, current_title: "Lead Software Engineer", current_company: "CloudSphere Systems",
    match_score: null, match_level: null, match_breakdown: null,
    recommendation: null,
    recommendation_notes: "Strong Java developer profile. No matching open requirement at this time. Added to talent pool.",
    added_to_platform: true, review_status: "pending",
    email_subject: "Referral: Deepa Krishnan - Java/Spring Boot Expert",
    email_from: "referrals@staffpro.com",
  },
];

const mockStats = {
  total_captures: 47, this_week: 12, today: 2,
  avg_match_score: 68.5, added_to_platform_rate: 0.78,
  pipeline_funnel: { emails_received: 120, resumes_detected: 47, parsed_successfully: 45, matched: 39, added_to_platform: 37, approved: 22 },
};

export function ResumeMatchCenter() {
  const [captures, setCaptures] = useState<ResumeCapture[]>([]);
  const [stats, setStats] = useState(mockStats);
  const [loading, setLoading] = useState(true);
  const [selectedCapture, setSelectedCapture] = useState<ResumeCapture | null>(null);

  useEffect(() => {
    const base = '/api/v1/email-resume';
    Promise.all([
      fetch(`${base}/captures`).then(r => r.ok ? r.json() : { items: mockCaptures }),
      fetch(`${base}/stats`).then(r => r.ok ? r.json() : mockStats),
    ]).then(([caps, st]) => {
      setCaptures(Array.isArray(caps.items) ? caps.items : mockCaptures);
      setStats(st.total_captures ? st : mockStats);
    }).catch(() => {
      setCaptures(mockCaptures); setStats(mockStats);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
    </div>
  );

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resume Match Center</h1>
        <p className="text-sm text-gray-500 mt-1">AI-powered resume parsing, skill extraction, and requirement matching from email</p>
      </div>

      {/* Pipeline Funnel */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Resume Processing Pipeline</h3>
        <div className="flex items-end gap-1 justify-between">
          {Object.entries(stats.pipeline_funnel).map(([stage, count], i) => {
            const maxVal = Math.max(...Object.values(stats.pipeline_funnel));
            const height = Math.max(20, (count / maxVal) * 120);
            const colors = ['bg-gray-300', 'bg-blue-300', 'bg-blue-400', 'bg-indigo-400', 'bg-green-400', 'bg-green-500'];
            return (
              <div key={stage} className="flex flex-col items-center flex-1">
                <p className="text-lg font-bold text-gray-800 mb-1">{count}</p>
                <div className={`w-full max-w-[60px] rounded-t-lg ${colors[i]}`} style={{ height: `${height}px` }} />
                <p className="text-[10px] text-gray-500 mt-2 text-center capitalize">{stage.replace(/_/g, ' ')}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* KPI Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total Captures', value: stats.total_captures, color: 'bg-indigo-50 text-indigo-700' },
          { label: 'This Week', value: stats.this_week, color: 'bg-blue-50 text-blue-700' },
          { label: 'Today', value: stats.today, color: 'bg-green-50 text-green-700' },
          { label: 'Avg Match', value: `${stats.avg_match_score}%`, color: 'bg-purple-50 text-purple-700' },
          { label: 'Platform Rate', value: `${Math.round(stats.added_to_platform_rate * 100)}%`, color: 'bg-teal-50 text-teal-700' },
        ].map(kpi => (
          <div key={kpi.label} className={`rounded-xl p-4 ${kpi.color}`}>
            <p className="text-xs font-medium opacity-70">{kpi.label}</p>
            <p className="text-2xl font-bold mt-1">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Resume Cards */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-gray-700">Recent Resume Captures</h3>
        {captures.map(cap => (
          <div key={cap.id}
            onClick={() => setSelectedCapture(selectedCapture?.id === cap.id ? null : cap)}
            className={`bg-white rounded-xl border border-gray-200 p-5 cursor-pointer transition-all hover:border-gray-300 ${
              selectedCapture?.id === cap.id ? 'ring-2 ring-indigo-400' : ''
            }`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-4 flex-1">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {cap.candidate_name?.charAt(0) || '?'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-semibold text-gray-900">{cap.candidate_name || 'Unknown'}</p>
                  <p className="text-sm text-gray-500">{cap.current_title} at {cap.current_company}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{cap.experience_years} years · {cap.candidate_email}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                {cap.match_score !== null ? (
                  <div className={`px-3 py-1.5 rounded-lg border text-center ${matchLevelColors[cap.match_level ?? 'fair']}`}>
                    <p className="text-xl font-bold">{cap.match_score}%</p>
                    <p className="text-[10px] uppercase font-medium">{cap.match_level}</p>
                  </div>
                ) : (
                  <div className="px-3 py-1.5 rounded-lg bg-gray-100 text-gray-500 text-center">
                    <p className="text-sm font-medium">No Match</p>
                    <p className="text-[10px]">Talent Pool</p>
                  </div>
                )}
                {cap.recommendation && (
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${recColors[cap.recommendation]}`}>
                    {cap.recommendation.replace('_', ' ').toUpperCase()}
                  </span>
                )}
              </div>
            </div>

            {/* Skills */}
            <div className="flex flex-wrap gap-1.5 mt-3">
              {cap.skills_extracted?.slice(0, 8).map(skill => (
                <span key={skill} className="px-2 py-0.5 rounded-full text-[11px] bg-indigo-50 text-indigo-600 font-medium">{skill}</span>
              ))}
              {(cap.skills_extracted?.length ?? 0) > 8 && (
                <span className="px-2 py-0.5 rounded-full text-[11px] bg-gray-100 text-gray-500">+{(cap.skills_extracted?.length ?? 0) - 8} more</span>
              )}
            </div>

            {/* Expanded detail */}
            {selectedCapture?.id === cap.id && (
              <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
                {cap.match_breakdown && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-2">Match Breakdown</p>
                    <div className="grid grid-cols-5 gap-3">
                      {Object.entries(cap.match_breakdown).map(([dim, score]) => (
                        <div key={dim} className="text-center">
                          <div className="relative w-12 h-12 mx-auto">
                            <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
                              <circle className="text-gray-200" strokeWidth="3" stroke="currentColor" fill="transparent" r="16" cx="18" cy="18" />
                              <circle className={score >= 80 ? 'text-green-500' : score >= 60 ? 'text-yellow-500' : 'text-red-500'}
                                strokeWidth="3" stroke="currentColor" fill="transparent" r="16" cx="18" cy="18"
                                strokeDasharray={`${(score / 100) * 100.53} 100.53`} strokeLinecap="round" />
                            </svg>
                            <span className="absolute inset-0 flex items-center justify-center text-xs font-bold">{score}</span>
                          </div>
                          <p className="text-[10px] text-gray-500 mt-1 capitalize">{dim.replace('_', ' ')}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {cap.recommendation_notes && (
                  <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                    <p className="text-xs font-medium text-indigo-700 mb-1">AI Recommendation</p>
                    <p className="text-xs text-indigo-600">{cap.recommendation_notes}</p>
                  </div>
                )}
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium hover:bg-green-700">Approve & Submit</button>
                  <button className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700">Run Match Again</button>
                  <button className="px-3 py-1.5 bg-white border border-gray-300 rounded-lg text-xs font-medium hover:bg-gray-50">View Resume</button>
                  <button className="px-3 py-1.5 bg-white border border-red-200 text-red-600 rounded-lg text-xs font-medium hover:bg-red-50">Reject</button>
                </div>
                <p className="text-xs text-gray-400">Source: {cap.email_subject} · From: {cap.email_from}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
