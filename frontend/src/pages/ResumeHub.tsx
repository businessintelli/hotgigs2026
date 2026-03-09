import React, { useState, useEffect } from 'react';
import {
  DocumentTextIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
  SparklesIcon,
  PhotoIcon,
  DocumentDuplicateIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  CheckCircleIcon,
  ClockIcon,
  StarIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  ArrowTrendingUpIcon,
  UserIcon,
  DocumentArrowDownIcon,
  PrinterIcon,
} from '@heroicons/react/24/outline';

// ── Types ──
interface ResumeHighlightsCard {
  resume_id: number;
  candidate_id: number;
  candidate_name: string;
  thumbnail_url: string | null;
  preview_text: string | null;
  professional_summary: string | null;
  years_experience: number | null;
  top_skills: string[];
  strong_points: string[];
  education_highlight: string | null;
  certifications_count: number;
  original_format: string;
  page_count: number;
  has_condensed: boolean;
  last_updated: string | null;
  view_count: number;
  download_count: number;
}

interface CondensedResume {
  resume_id: number;
  candidate_id: number;
  professional_summary: string;
  key_stats: Record<string, any>;
  strong_points: string[];
  career_trajectory: { period: string; role: string; company: string; highlight: string }[];
  top_skills: { skill: string; proficiency: string; years: number }[];
  notable_achievements: string[];
  original_page_count: number;
  condensed_page_count: number;
  compression_ratio: number;
  condensation_quality: number;
}

interface DownloadAnalytics {
  resume_id: number;
  candidate_name: string;
  total_views: number;
  total_downloads: number;
  total_previews: number;
  unique_recruiters: number;
  last_accessed: string | null;
  access_history: { action: string; recruiter_name: string; source_page: string; accessed_at: string }[];
  daily_trend: { date: string; views: number; downloads: number }[];
}

interface ProcessingStats {
  total_resumes: number;
  total_parsed: number;
  total_converted: number;
  total_condensed: number;
  total_thumbnails: number;
  total_views: number;
  total_downloads: number;
  format_breakdown: Record<string, number>;
  avg_page_count: number;
  avg_condensation_ratio: number;
  top_viewed_resumes: { candidate_name: string; views: number; downloads: number }[];
  top_downloading_recruiters: { recruiter_name: string; downloads: number }[];
}

// ── Mock Data ──
const CANDIDATES = [
  { id: 1, name: 'Sarah Chen', role: 'Senior Software Engineer', exp: 8, skills: ['Python', 'React', 'AWS', 'Docker', 'PostgreSQL'], education: 'MS Computer Science, Stanford', certs: 3, achievements: ['Led migration to microservices saving $200K/yr', 'Built ML pipeline processing 2M records/day', 'Mentored 12 junior developers'] },
  { id: 2, name: 'James Rodriguez', role: 'Data Scientist', exp: 6, skills: ['Python', 'TensorFlow', 'SQL', 'Spark', 'Tableau'], education: 'PhD Statistics, MIT', certs: 2, achievements: ['Published 4 ML research papers', 'Built fraud detection model saving $5M annually', 'Reduced model training time by 70%'] },
  { id: 3, name: 'Priya Sharma', role: 'Product Manager', exp: 10, skills: ['Agile', 'JIRA', 'SQL', 'Figma', 'A/B Testing'], education: 'MBA, Wharton', certs: 4, achievements: ['Grew product ARR from $2M to $15M', 'Launched 3 products from 0→1', 'Led cross-functional team of 25'] },
  { id: 4, name: 'Michael Kim', role: 'DevOps Engineer', exp: 5, skills: ['Kubernetes', 'Terraform', 'CI/CD', 'AWS', 'Python'], education: 'BS Computer Engineering, Georgia Tech', certs: 5, achievements: ['Reduced deployment time from 2hr to 8min', 'Achieved 99.99% uptime SLA', 'Automated infrastructure saving 40 eng-hours/week'] },
  { id: 5, name: 'Emily Watson', role: 'Full Stack Developer', exp: 4, skills: ['TypeScript', 'React', 'Node.js', 'GraphQL', 'MongoDB'], education: 'BS Software Engineering, CMU', certs: 2, achievements: ['Built real-time collaboration feature for 50K users', 'Reduced page load time by 60%', 'Open source contributor with 2K+ GitHub stars'] },
  { id: 6, name: 'David Okafor', role: 'Cloud Architect', exp: 12, skills: ['AWS', 'Azure', 'GCP', 'Terraform', 'Security'], education: 'MS Cloud Computing, Georgia Tech', certs: 7, achievements: ['Designed multi-cloud architecture for Fortune 500', 'Reduced cloud spend by 35% ($1.2M)', 'Led SOC2 and ISO27001 compliance'] },
  { id: 7, name: 'Lisa Tanaka', role: 'ML Engineer', exp: 7, skills: ['PyTorch', 'Python', 'MLOps', 'Kubernetes', 'NLP'], education: 'MS AI, Carnegie Mellon', certs: 3, achievements: ['Deployed 15+ production ML models', 'Built NLP pipeline for 20 languages', 'Reduced model inference latency by 80%'] },
  { id: 8, name: 'Alex Petrov', role: 'Backend Engineer', exp: 9, skills: ['Go', 'Python', 'gRPC', 'Redis', 'PostgreSQL'], education: 'BS Computer Science, UC Berkeley', certs: 2, achievements: ['Built event-driven system handling 100K events/sec', 'Designed microservices for 10M+ daily users', 'Reduced API latency P99 from 500ms to 50ms'] },
];

function generateHighlightCards(): ResumeHighlightsCard[] {
  return CANDIDATES.map((c, i) => ({
    resume_id: c.id,
    candidate_id: c.id,
    candidate_name: c.name,
    thumbnail_url: `/api/v1/resume-processing/thumbnail/${c.id}/image`,
    preview_text: `${c.role} with ${c.exp} years experience. ${c.education}.`,
    professional_summary: `Experienced ${c.role} specializing in ${c.skills.slice(0, 3).join(', ')}. ${c.achievements[0]}.`,
    years_experience: c.exp,
    top_skills: c.skills.slice(0, 5),
    strong_points: [c.achievements[0], `${c.certs} certifications`, `Expert in ${c.skills[0]}`],
    education_highlight: c.education,
    certifications_count: c.certs,
    original_format: c.id % 3 === 0 ? 'docx' : 'pdf',
    page_count: Math.max(1, Math.floor(c.exp / 3)),
    has_condensed: c.exp > 4,
    last_updated: new Date(Date.now() - i * 86400000 * 3).toISOString(),
    view_count: 25 - i * 3,
    download_count: 8 - i,
  }));
}

function generateCondensed(c: typeof CANDIDATES[0]): CondensedResume {
  const orig = Math.max(2, Math.floor(c.exp / 2));
  return {
    resume_id: c.id,
    candidate_id: c.id,
    professional_summary: `${c.name} is a seasoned ${c.role} with ${c.exp} years of progressive experience. ${c.education}. Known for ${c.achievements[0].toLowerCase()} and other high-impact contributions.`,
    key_stats: { years_experience: c.exp, certifications: c.certs, top_skills_count: c.skills.length, projects_led: Math.max(1, Math.floor(c.exp / 2)) },
    strong_points: [`${c.exp}+ years in ${c.role} roles`, `Expert in ${c.skills.slice(0, 3).join(', ')}`, c.achievements[0], `${c.certs} professional certifications`, c.education],
    career_trajectory: [
      { period: `${2026 - c.exp}-${2026 - Math.max(0, c.exp - 3)}`, role: `Junior ${c.role.split(' ').pop()}`, company: 'StartupCo', highlight: 'Built foundational skills' },
      { period: `${2026 - Math.max(0, c.exp - 3)}-${2026 - Math.max(0, c.exp - 6)}`, role: c.role, company: 'MidCorp', highlight: c.achievements[1] || 'Key contributor' },
      { period: `${2026 - Math.max(0, c.exp - 6)}-Present`, role: `Senior ${c.role}`, company: 'Enterprise Inc', highlight: c.achievements[0] },
    ].slice(0, Math.min(3, Math.max(1, Math.floor(c.exp / 3)))),
    top_skills: c.skills.map((s, i) => ({ skill: s, proficiency: i < 2 ? 'Expert' : i < 4 ? 'Advanced' : 'Intermediate', years: Math.max(1, c.exp - i * 2) })),
    notable_achievements: c.achievements,
    original_page_count: orig,
    condensed_page_count: 3,
    compression_ratio: orig > 3 ? Math.round((3 / orig) * 100) / 100 : 1.0,
    condensation_quality: 0.92,
  };
}

function generateStats(): ProcessingStats {
  return {
    total_resumes: 847, total_parsed: 812, total_converted: 234, total_condensed: 156, total_thumbnails: 812,
    total_views: 3420, total_downloads: 987,
    format_breakdown: { pdf: 613, docx: 198, doc: 36 },
    avg_page_count: 4.2, avg_condensation_ratio: 0.38,
    top_viewed_resumes: CANDIDATES.slice(0, 5).map((c, i) => ({ candidate_name: c.name, views: 30 - i * 4, downloads: 10 - i })),
    top_downloading_recruiters: [
      { recruiter_name: 'Tom Brady', downloads: 45 },
      { recruiter_name: 'Anna Lopez', downloads: 37 },
      { recruiter_name: 'Chris Park', downloads: 29 },
      { recruiter_name: 'Diana Wells', downloads: 21 },
      { recruiter_name: 'Raj Patel', downloads: 15 },
    ],
  };
}


// ── Thumbnail SVG Component ──
function ResumeThumbnail({ candidate }: { candidate: typeof CANDIDATES[0] }) {
  return (
    <svg viewBox="0 0 200 280" className="w-full h-full rounded border border-gray-200 shadow-sm">
      <rect width="200" height="280" fill="#f8fafc" rx="4" />
      <rect x="15" y="12" width="100" height="5" fill="#1e293b" rx="2" />
      <text x="15" y="32" fontFamily="system-ui" fontSize="8" fill="#1e293b" fontWeight="bold">{candidate.name}</text>
      <text x="15" y="43" fontFamily="system-ui" fontSize="6.5" fill="#6366f1">{candidate.role}</text>
      <line x1="15" y1="50" x2="185" y2="50" stroke="#e2e8f0" />
      <text x="15" y="62" fontFamily="system-ui" fontSize="6" fill="#475569" fontWeight="600">SKILLS</text>
      {candidate.skills.slice(0, 3).map((s, i) => (
        <g key={s}>
          <rect x={15 + i * 55} y="66" width={50} height="12" fill="#ede9fe" rx="2" />
          <text x={17 + i * 55} y="75" fontFamily="system-ui" fontSize="5.5" fill="#6d28d9">{s}</text>
        </g>
      ))}
      <text x="15" y="94" fontFamily="system-ui" fontSize="6" fill="#475569" fontWeight="600">EXPERIENCE</text>
      {[0, 1, 2].map(i => (
        <g key={i}>
          <rect x="15" y={100 + i * 16} width="170" height="3" fill="#e2e8f0" rx="1" />
          <rect x="15" y={106 + i * 16} width={140 + Math.random() * 30} height="3" fill="#f1f5f9" rx="1" />
        </g>
      ))}
      <text x="15" y="156" fontFamily="system-ui" fontSize="6" fill="#475569" fontWeight="600">EDUCATION</text>
      <text x="15" y="167" fontFamily="system-ui" fontSize="5.5" fill="#64748b">{candidate.education.slice(0, 35)}</text>
      {[180, 190, 200, 210, 220, 230].map(y => (
        <rect key={y} x="15" y={y} width={130 + Math.random() * 40} height="3" fill="#f1f5f9" rx="1" />
      ))}
    </svg>
  );
}

// ── Proficiency Bar ──
function ProficiencyBar({ level }: { level: string }) {
  const pct = level === 'Expert' ? 95 : level === 'Advanced' ? 75 : 55;
  const color = level === 'Expert' ? 'bg-violet-500' : level === 'Advanced' ? 'bg-blue-500' : 'bg-emerald-500';
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 bg-gray-100 rounded-full h-2 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-500">{level}</span>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════
export function ResumeHub() {
  const [activeTab, setActiveTab] = useState<'gallery' | 'condensed' | 'tracking' | 'conversion' | 'stats'>('gallery');
  const [cards, setCards] = useState<ResumeHighlightsCard[]>([]);
  const [stats, setStats] = useState<ProcessingStats | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<typeof CANDIDATES[0] | null>(null);
  const [condensedView, setCondensedView] = useState<CondensedResume | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formatFilter, setFormatFilter] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    setCards(generateHighlightCards());
    setStats(generateStats());
  }, []);

  const filteredCards = cards.filter(c => {
    if (searchTerm && !c.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) && !c.top_skills.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))) return false;
    if (formatFilter && c.original_format !== formatFilter) return false;
    return true;
  });

  const handleCondense = (candidateId: number) => {
    const cand = CANDIDATES.find(c => c.id === candidateId);
    if (cand) {
      setCondensedView(generateCondensed(cand));
      setSelectedCandidate(cand);
      setActiveTab('condensed');
    }
  };

  const handleAutoProcess = async () => {
    setProcessing(true);
    await new Promise(r => setTimeout(r, 2000));
    setProcessing(false);
  };

  const tabs = [
    { id: 'gallery', label: 'Resume Gallery', icon: PhotoIcon },
    { id: 'condensed', label: 'Condensed View', icon: SparklesIcon },
    { id: 'tracking', label: 'Access Tracking', icon: EyeIcon },
    { id: 'conversion', label: 'PDF Conversion', icon: DocumentDuplicateIcon },
    { id: 'stats', label: 'Analytics', icon: ChartBarIcon },
  ] as const;

  return (
    <div className="p-6 max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <DocumentTextIcon className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Resume Hub</h1>
            <p className="text-sm text-gray-500">Preview thumbnails, PDF conversion, download tracking & AI condensation</p>
          </div>
        </div>
        <button
          onClick={handleAutoProcess}
          disabled={processing}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white ${processing ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'}`}
        >
          {processing ? <ArrowPathIcon className="w-4 h-4 animate-spin" /> : <SparklesIcon className="w-4 h-4" />}
          {processing ? 'Processing...' : 'Auto-Process All'}
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-1">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  activeTab === tab.id ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ═══ GALLERY TAB ═══ */}
      {activeTab === 'gallery' && (
        <div className="space-y-4">
          {/* Search & Filter */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Search by name or skill..."
                className="w-full pl-9 pr-4 py-2 border rounded-lg text-sm"
              />
            </div>
            <div className="flex items-center gap-1">
              <FunnelIcon className="w-4 h-4 text-gray-400" />
              {['all', 'pdf', 'docx', 'doc'].map(f => (
                <button
                  key={f}
                  onClick={() => setFormatFilter(f === 'all' ? null : f)}
                  className={`px-3 py-1.5 rounded text-xs font-medium ${
                    (f === 'all' && !formatFilter) || formatFilter === f
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Resume Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {filteredCards.map(card => {
              const cand = CANDIDATES.find(c => c.id === card.candidate_id)!;
              return (
                <div key={card.resume_id} className="bg-white rounded-xl border hover:shadow-lg transition-shadow overflow-hidden group">
                  {/* Thumbnail Preview */}
                  <div className="h-44 p-3 bg-gray-50 relative overflow-hidden">
                    <ResumeThumbnail candidate={cand} />
                    {/* Overlay on hover */}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                      <button className="p-2 bg-white rounded-full hover:bg-gray-100" title="Preview">
                        <EyeIcon className="w-4 h-4 text-gray-700" />
                      </button>
                      <button className="p-2 bg-white rounded-full hover:bg-gray-100" title="Download">
                        <ArrowDownTrayIcon className="w-4 h-4 text-gray-700" />
                      </button>
                      <button onClick={() => handleCondense(card.candidate_id)} className="p-2 bg-white rounded-full hover:bg-gray-100" title="Condense to 3 pages">
                        <SparklesIcon className="w-4 h-4 text-indigo-600" />
                      </button>
                    </div>
                    {/* Format badge */}
                    <div className={`absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      card.original_format === 'pdf' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {card.original_format}
                    </div>
                    {card.has_condensed && (
                      <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-violet-100 text-violet-700 text-[10px] font-medium flex items-center gap-0.5">
                        <SparklesIcon className="w-3 h-3" /> 3pg
                      </div>
                    )}
                  </div>

                  {/* Card Body */}
                  <div className="p-4 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900 text-sm">{card.candidate_name}</h3>
                        <p className="text-xs text-gray-500">{cand.role}</p>
                      </div>
                      <span className="text-xs text-gray-400">{card.page_count} pg</span>
                    </div>

                    {/* Key Stats Row */}
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><BriefcaseIcon className="w-3 h-3" /> {card.years_experience}yr</span>
                      <span className="flex items-center gap-1"><AcademicCapIcon className="w-3 h-3" /> {card.certifications_count} certs</span>
                    </div>

                    {/* Skills */}
                    <div className="flex flex-wrap gap-1">
                      {card.top_skills.slice(0, 4).map(s => (
                        <span key={s} className="px-1.5 py-0.5 bg-indigo-50 text-indigo-700 rounded text-[10px] font-medium">{s}</span>
                      ))}
                      {card.top_skills.length > 4 && <span className="text-[10px] text-gray-400">+{card.top_skills.length - 4}</span>}
                    </div>

                    {/* Strong Point */}
                    <p className="text-xs text-gray-600 line-clamp-2">{card.strong_points[0]}</p>

                    {/* Access counts */}
                    <div className="flex items-center justify-between pt-2 border-t text-xs text-gray-400">
                      <span className="flex items-center gap-1"><EyeIcon className="w-3 h-3" /> {card.view_count} views</span>
                      <span className="flex items-center gap-1"><ArrowDownTrayIcon className="w-3 h-3" /> {card.download_count} downloads</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ═══ CONDENSED VIEW TAB ═══ */}
      {activeTab === 'condensed' && (
        <div className="space-y-6">
          {!condensedView ? (
            <div className="bg-white rounded-xl border p-12 text-center">
              <SparklesIcon className="w-12 h-12 text-indigo-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700">No Resume Selected</h3>
              <p className="text-sm text-gray-500 mt-1">Select a resume from the Gallery tab and click the sparkle icon to condense it to 3 pages</p>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-6">
              {/* Left: Condensed Summary */}
              <div className="col-span-2 space-y-4">
                <div className="bg-white rounded-xl border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold">
                        {selectedCandidate?.name.charAt(0)}
                      </div>
                      <div>
                        <h2 className="text-lg font-bold text-gray-900">{selectedCandidate?.name}</h2>
                        <p className="text-sm text-gray-500">{selectedCandidate?.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-violet-50 text-violet-700 rounded text-xs font-medium">
                        {condensedView.original_page_count} → {condensedView.condensed_page_count} pages
                      </span>
                      <span className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs font-medium">
                        {Math.round(condensedView.condensation_quality * 100)}% quality
                      </span>
                    </div>
                  </div>

                  {/* Professional Summary */}
                  <div className="mb-5">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1"><UserIcon className="w-4 h-4" /> Professional Summary</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{condensedView.professional_summary}</p>
                  </div>

                  {/* Strong Points */}
                  <div className="mb-5">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1"><StarIcon className="w-4 h-4" /> Strong Points</h3>
                    <div className="space-y-1.5">
                      {condensedView.strong_points.map((sp, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <CheckCircleIcon className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-600">{sp}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Career Trajectory */}
                  <div className="mb-5">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-1"><ArrowTrendingUpIcon className="w-4 h-4" /> Career Trajectory</h3>
                    <div className="relative pl-6 space-y-4 border-l-2 border-indigo-200">
                      {condensedView.career_trajectory.map((ct, i) => (
                        <div key={i} className="relative">
                          <div className="absolute -left-[25px] w-3 h-3 rounded-full bg-indigo-500 border-2 border-white" />
                          <div className="text-xs text-indigo-600 font-medium">{ct.period}</div>
                          <div className="text-sm font-medium text-gray-900">{ct.role} at {ct.company}</div>
                          <div className="text-xs text-gray-500">{ct.highlight}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Notable Achievements */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Notable Achievements</h3>
                    <div className="space-y-1.5">
                      {condensedView.notable_achievements.map((a, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="text-indigo-500 font-bold">#{i + 1}</span>
                          {a}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right: Skills + Stats */}
              <div className="space-y-4">
                {/* Key Stats */}
                <div className="bg-white rounded-xl border p-5">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Key Stats</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(condensedView.key_stats).filter(([k]) => typeof condensedView.key_stats[k] === 'number').map(([key, val]) => (
                      <div key={key} className="bg-gray-50 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-indigo-700">{String(val)}</div>
                        <div className="text-[10px] text-gray-500 uppercase">{key.replace(/_/g, ' ')}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Skills */}
                <div className="bg-white rounded-xl border p-5">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Top Skills</h3>
                  <div className="space-y-3">
                    {condensedView.top_skills.map(s => (
                      <div key={s.skill} className="flex items-center justify-between">
                        <div>
                          <div className="text-sm font-medium text-gray-800">{s.skill}</div>
                          <div className="text-[10px] text-gray-400">{s.years} years</div>
                        </div>
                        <ProficiencyBar level={s.proficiency} />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="bg-white rounded-xl border p-5 space-y-2">
                  <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
                    <DocumentArrowDownIcon className="w-4 h-4" /> Download Condensed PDF
                  </button>
                  <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-white border text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50">
                    <PrinterIcon className="w-4 h-4" /> Print
                  </button>
                </div>

                {/* Candidate Quick Select */}
                <div className="bg-white rounded-xl border p-5">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Condense Another</h3>
                  <div className="space-y-1 max-h-48 overflow-y-auto">
                    {CANDIDATES.map(c => (
                      <button
                        key={c.id}
                        onClick={() => handleCondense(c.id)}
                        className={`w-full text-left px-3 py-2 rounded text-sm hover:bg-indigo-50 ${selectedCandidate?.id === c.id ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600'}`}
                      >
                        {c.name} — {c.role}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ═══ TRACKING TAB ═══ */}
      {activeTab === 'tracking' && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-5 gap-4">
            {[
              { label: 'Total Views', value: stats?.total_views || 0, icon: EyeIcon, color: 'text-blue-600' },
              { label: 'Downloads', value: stats?.total_downloads || 0, icon: ArrowDownTrayIcon, color: 'text-emerald-600' },
              { label: 'Resumes', value: stats?.total_resumes || 0, icon: DocumentTextIcon, color: 'text-gray-700' },
              { label: 'Parsed', value: stats?.total_parsed || 0, icon: CheckCircleIcon, color: 'text-violet-600' },
              { label: 'Condensed', value: stats?.total_condensed || 0, icon: SparklesIcon, color: 'text-indigo-600' },
            ].map(s => {
              const Icon = s.icon;
              return (
                <div key={s.label} className="bg-white rounded-xl border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-5 h-5 ${s.color}`} />
                    <span className="text-xs text-gray-500">{s.label}</span>
                  </div>
                  <div className={`text-2xl font-bold ${s.color}`}>{s.value.toLocaleString()}</div>
                </div>
              );
            })}
          </div>

          {/* Top Viewed Resumes */}
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border p-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Most Viewed Resumes</h3>
              <div className="space-y-3">
                {stats?.top_viewed_resumes.map((r, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-indigo-50 flex items-center justify-center text-xs font-bold text-indigo-600">{i + 1}</span>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-800">{r.candidate_name}</div>
                      <div className="text-xs text-gray-400">{r.views} views, {r.downloads} downloads</div>
                    </div>
                    <div className="w-24 bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(r.views / 30) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border p-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Top Downloading Recruiters</h3>
              <div className="space-y-3">
                {stats?.top_downloading_recruiters.map((r, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-emerald-50 flex items-center justify-center text-xs font-bold text-emerald-600">{i + 1}</span>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-800">{r.recruiter_name}</div>
                      <div className="text-xs text-gray-400">{r.downloads} downloads</div>
                    </div>
                    <div className="w-24 bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${(r.downloads / 45) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Access Log */}
          <div className="bg-white rounded-xl border overflow-hidden">
            <div className="px-5 py-3 bg-gray-50 border-b">
              <h3 className="text-sm font-semibold text-gray-700">Recent Resume Access Log</h3>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b text-xs text-gray-500 uppercase">
                  <th className="text-left px-5 py-2">Recruiter</th>
                  <th className="text-left px-5 py-2">Candidate</th>
                  <th className="text-left px-5 py-2">Action</th>
                  <th className="text-left px-5 py-2">Source</th>
                  <th className="text-left px-5 py-2">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {[
                  { recruiter: 'Tom Brady', candidate: 'Sarah Chen', action: 'download', source: 'ATS Workflow', time: '2 min ago' },
                  { recruiter: 'Anna Lopez', candidate: 'James Rodriguez', action: 'view', source: 'Candidate CRM', time: '15 min ago' },
                  { recruiter: 'Chris Park', candidate: 'Priya Sharma', action: 'preview', source: 'Search', time: '32 min ago' },
                  { recruiter: 'Tom Brady', candidate: 'David Okafor', action: 'download', source: 'ATS Workflow', time: '1 hr ago' },
                  { recruiter: 'Diana Wells', candidate: 'Lisa Tanaka', action: 'view', source: 'Aggregate Reports', time: '1.5 hr ago' },
                  { recruiter: 'Raj Patel', candidate: 'Alex Petrov', action: 'view', source: 'Candidate CRM', time: '2 hr ago' },
                  { recruiter: 'Anna Lopez', candidate: 'Emily Watson', action: 'print', source: 'ATS Workflow', time: '3 hr ago' },
                  { recruiter: 'Chris Park', candidate: 'Michael Kim', action: 'download', source: 'Search', time: '4 hr ago' },
                ].map((log, i) => (
                  <tr key={i} className="hover:bg-gray-50 text-sm">
                    <td className="px-5 py-2.5 text-gray-700">{log.recruiter}</td>
                    <td className="px-5 py-2.5 text-gray-700">{log.candidate}</td>
                    <td className="px-5 py-2.5">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        log.action === 'download' ? 'bg-emerald-50 text-emerald-700' :
                        log.action === 'view' ? 'bg-blue-50 text-blue-700' :
                        log.action === 'preview' ? 'bg-violet-50 text-violet-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {log.action === 'download' && <ArrowDownTrayIcon className="w-3 h-3" />}
                        {log.action === 'view' && <EyeIcon className="w-3 h-3" />}
                        {log.action === 'preview' && <PhotoIcon className="w-3 h-3" />}
                        {log.action === 'print' && <PrinterIcon className="w-3 h-3" />}
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-2.5 text-xs text-gray-500">{log.source}</td>
                    <td className="px-5 py-2.5 text-xs text-gray-400">{log.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ═══ CONVERSION TAB ═══ */}
      {activeTab === 'conversion' && (
        <div className="space-y-6">
          {/* Conversion Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border p-5 text-center">
              <div className="text-3xl font-bold text-gray-900">{stats?.total_resumes || 0}</div>
              <div className="text-xs text-gray-500 mt-1">Total Resumes</div>
            </div>
            {stats && Object.entries(stats.format_breakdown).map(([fmt, count]) => (
              <div key={fmt} className="bg-white rounded-xl border p-5 text-center">
                <div className={`text-3xl font-bold ${fmt === 'pdf' ? 'text-red-600' : fmt === 'docx' ? 'text-blue-600' : 'text-gray-600'}`}>{count}</div>
                <div className="text-xs text-gray-500 mt-1">{fmt.toUpperCase()} Files</div>
              </div>
            ))}
          </div>

          {/* Format Distribution */}
          <div className="bg-white rounded-xl border p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Format Distribution & Conversion Pipeline</h3>
            <div className="space-y-4">
              {stats && Object.entries(stats.format_breakdown).map(([fmt, count]) => {
                const total = stats.total_resumes;
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={fmt} className="flex items-center gap-4">
                    <span className={`w-16 text-sm font-bold uppercase ${fmt === 'pdf' ? 'text-red-600' : fmt === 'docx' ? 'text-blue-600' : 'text-gray-600'}`}>
                      {fmt}
                    </span>
                    <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden relative">
                      <div
                        className={`h-full rounded-full ${fmt === 'pdf' ? 'bg-red-400' : fmt === 'docx' ? 'bg-blue-400' : 'bg-gray-400'}`}
                        style={{ width: `${pct}%` }}
                      />
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-800">
                        {count} files ({pct}%)
                      </span>
                    </div>
                    {fmt !== 'pdf' && (
                      <span className="flex items-center gap-1 text-xs text-emerald-600">
                        <CheckCircleIcon className="w-4 h-4" /> Converted to PDF
                      </span>
                    )}
                    {fmt === 'pdf' && (
                      <span className="text-xs text-gray-400">Native PDF</span>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="mt-6 p-4 bg-indigo-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm font-medium text-indigo-700">
                <CheckCircleIcon className="w-5 h-5" />
                Auto-conversion enabled: All DOCX/DOC uploads are automatically converted to PDF on upload
              </div>
              <p className="text-xs text-indigo-600 mt-1">
                {stats?.total_converted || 0} files converted to date. Original files are preserved alongside PDFs.
              </p>
            </div>
          </div>

          {/* Recent Conversions */}
          <div className="bg-white rounded-xl border overflow-hidden">
            <div className="px-5 py-3 bg-gray-50 border-b">
              <h3 className="text-sm font-semibold text-gray-700">Recent Conversions</h3>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b text-xs text-gray-500 uppercase">
                  <th className="text-left px-5 py-2">Candidate</th>
                  <th className="text-left px-5 py-2">Original</th>
                  <th className="text-center px-5 py-2">→</th>
                  <th className="text-left px-5 py-2">Converted</th>
                  <th className="text-right px-5 py-2">Size Change</th>
                  <th className="text-left px-5 py-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {CANDIDATES.filter(c => c.id % 3 === 0 || c.id % 5 === 0).map(c => {
                  const origFmt = c.id % 3 === 0 ? 'DOCX' : 'DOC';
                  const origSize = 85 + c.id * 12;
                  const convSize = Math.round(origSize * 0.75);
                  return (
                    <tr key={c.id} className="hover:bg-gray-50 text-sm">
                      <td className="px-5 py-2.5 text-gray-700 font-medium">{c.name}</td>
                      <td className="px-5 py-2.5">
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700">{origFmt}</span>
                        <span className="text-xs text-gray-400 ml-2">{origSize}KB</span>
                      </td>
                      <td className="px-5 py-2.5 text-center text-gray-400">→</td>
                      <td className="px-5 py-2.5">
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-50 text-red-700">PDF</span>
                        <span className="text-xs text-gray-400 ml-2">{convSize}KB</span>
                      </td>
                      <td className="px-5 py-2.5 text-right text-xs text-emerald-600">-{Math.round((1 - convSize / origSize) * 100)}%</td>
                      <td className="px-5 py-2.5">
                        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 flex items-center gap-1 w-fit">
                          <CheckCircleIcon className="w-3 h-3" /> Completed
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ═══ ANALYTICS TAB ═══ */}
      {activeTab === 'stats' && stats && (
        <div className="space-y-6">
          {/* Stat Cards */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Avg Pages/Resume', value: stats.avg_page_count.toFixed(1), sub: 'Before condensation' },
              { label: 'Avg Condensation', value: `${Math.round(stats.avg_condensation_ratio * 100)}%`, sub: 'Compression ratio' },
              { label: 'Thumbnails Generated', value: stats.total_thumbnails, sub: `${Math.round((stats.total_thumbnails / stats.total_resumes) * 100)}% coverage` },
              { label: 'Resumes Condensed', value: stats.total_condensed, sub: `${Math.round((stats.total_condensed / stats.total_resumes) * 100)}% of total` },
            ].map(s => (
              <div key={s.label} className="bg-white rounded-xl border p-5">
                <div className="text-2xl font-bold text-gray-900">{s.value}</div>
                <div className="text-sm text-gray-600 mt-1">{s.label}</div>
                <div className="text-xs text-gray-400 mt-0.5">{s.sub}</div>
              </div>
            ))}
          </div>

          {/* Processing Pipeline */}
          <div className="bg-white rounded-xl border p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Resume Processing Pipeline</h3>
            <div className="flex items-center gap-2">
              {[
                { label: 'Uploaded', count: stats.total_resumes, color: 'bg-gray-500' },
                { label: 'Parsed', count: stats.total_parsed, color: 'bg-blue-500' },
                { label: 'Converted', count: stats.total_converted, color: 'bg-violet-500' },
                { label: 'Thumbnailed', count: stats.total_thumbnails, color: 'bg-indigo-500' },
                { label: 'Condensed', count: stats.total_condensed, color: 'bg-emerald-500' },
              ].map((step, i, arr) => (
                <React.Fragment key={step.label}>
                  <div className="flex-1 text-center">
                    <div className={`w-12 h-12 rounded-full ${step.color} mx-auto flex items-center justify-center text-white font-bold text-sm`}>
                      {step.count}
                    </div>
                    <div className="text-xs text-gray-600 mt-2 font-medium">{step.label}</div>
                    <div className="text-[10px] text-gray-400">
                      {i > 0 ? `${Math.round((step.count / arr[0].count) * 100)}%` : '100%'}
                    </div>
                  </div>
                  {i < arr.length - 1 && (
                    <div className="text-gray-300 text-lg">→</div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Views vs Downloads Trend */}
          <div className="bg-white rounded-xl border p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Daily Views vs Downloads (14 days)</h3>
            <div className="h-40 flex items-end gap-2">
              {Array.from({ length: 14 }, (_, i) => {
                const views = 15 + Math.floor(Math.random() * 20);
                const downloads = 3 + Math.floor(Math.random() * 8);
                const maxH = 35;
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full flex gap-0.5 justify-center" style={{ height: `${(views / maxH) * 100}%` }}>
                      <div className="w-2/5 bg-blue-400 rounded-t" style={{ height: '100%' }} title={`${views} views`} />
                      <div className="w-2/5 bg-emerald-400 rounded-t" style={{ height: `${(downloads / views) * 100}%` }} title={`${downloads} downloads`} />
                    </div>
                    {i % 2 === 0 && <span className="text-[9px] text-gray-400">{new Date(Date.now() - (13 - i) * 86400000).toLocaleDateString('en', { month: 'short', day: 'numeric' })}</span>}
                  </div>
                );
              })}
            </div>
            <div className="flex items-center gap-4 mt-3 justify-center">
              <div className="flex items-center gap-1 text-xs text-gray-500"><div className="w-3 h-3 bg-blue-400 rounded" /> Views</div>
              <div className="flex items-center gap-1 text-xs text-gray-500"><div className="w-3 h-3 bg-emerald-400 rounded" /> Downloads</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
