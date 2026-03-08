import React, { useState, useCallback } from 'react';
import {
  BriefcaseIcon,
  UserGroupIcon,
  ChevronRightIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PhoneIcon,
  DocumentTextIcon,
  StarIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  EllipsisVerticalIcon,
  ArrowPathIcon,
  EnvelopeIcon,
  CalendarDaysIcon,
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  BuildingOffice2Icon,
} from '@heroicons/react/24/outline';
import axios from 'axios';

// ── Pipeline Phase Config ──
const PIPELINE_PHASES = [
  { key: 'sourced', label: 'Sourced', color: 'bg-slate-100 text-slate-700 border-slate-300', activeColor: 'bg-slate-500', icon: MagnifyingGlassIcon },
  { key: 'screening', label: 'Screening', color: 'bg-blue-100 text-blue-700 border-blue-300', activeColor: 'bg-blue-500', icon: FunnelIcon },
  { key: 'submitted', label: 'Submitted', color: 'bg-indigo-100 text-indigo-700 border-indigo-300', activeColor: 'bg-indigo-500', icon: DocumentTextIcon },
  { key: 'interview_scheduled', label: 'Interview', color: 'bg-amber-100 text-amber-700 border-amber-300', activeColor: 'bg-amber-500', icon: CalendarDaysIcon },
  { key: 'interview_complete', label: 'Evaluated', color: 'bg-orange-100 text-orange-700 border-orange-300', activeColor: 'bg-orange-500', icon: StarIcon },
  { key: 'offer_extended', label: 'Offer', color: 'bg-purple-100 text-purple-700 border-purple-300', activeColor: 'bg-purple-500', icon: EnvelopeIcon },
  { key: 'offer_accepted', label: 'Accepted', color: 'bg-teal-100 text-teal-700 border-teal-300', activeColor: 'bg-teal-500', icon: CheckCircleIcon },
  { key: 'placed', label: 'Placed', color: 'bg-emerald-100 text-emerald-700 border-emerald-300', activeColor: 'bg-emerald-500', icon: BriefcaseIcon },
  { key: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-700 border-red-300', activeColor: 'bg-red-500', icon: XCircleIcon },
];

const PHASE_ACTIONS: Record<string, { label: string; nextPhase: string; icon: React.ForwardRefExoticComponent<any> }[]> = {
  sourced: [
    { label: 'Screen', nextPhase: 'screening', icon: FunnelIcon },
    { label: 'Reject', nextPhase: 'rejected', icon: XCircleIcon },
  ],
  screening: [
    { label: 'Submit to Client', nextPhase: 'submitted', icon: DocumentTextIcon },
    { label: 'Reject', nextPhase: 'rejected', icon: XCircleIcon },
  ],
  submitted: [
    { label: 'Schedule Interview', nextPhase: 'interview_scheduled', icon: CalendarDaysIcon },
    { label: 'Reject', nextPhase: 'rejected', icon: XCircleIcon },
  ],
  interview_scheduled: [
    { label: 'Complete Interview', nextPhase: 'interview_complete', icon: StarIcon },
    { label: 'Reschedule', nextPhase: 'interview_scheduled', icon: ArrowPathIcon },
    { label: 'Reject', nextPhase: 'rejected', icon: XCircleIcon },
  ],
  interview_complete: [
    { label: 'Extend Offer', nextPhase: 'offer_extended', icon: EnvelopeIcon },
    { label: 'Reject', nextPhase: 'rejected', icon: XCircleIcon },
  ],
  offer_extended: [
    { label: 'Mark Accepted', nextPhase: 'offer_accepted', icon: CheckCircleIcon },
    { label: 'Mark Declined', nextPhase: 'rejected', icon: XCircleIcon },
  ],
  offer_accepted: [
    { label: 'Mark Placed', nextPhase: 'placed', icon: BriefcaseIcon },
  ],
  placed: [],
  rejected: [
    { label: 'Reconsider', nextPhase: 'sourced', icon: ArrowPathIcon },
  ],
};

// ── Mock Data ──
const mockJobs = [
  { id: 'JO-1001', title: 'Senior Full Stack Engineer', client: 'TechCorp Inc.', location: 'San Francisco, CA', status: 'open', priority: 'urgent', created: '2026-02-10', billRate: '$135/hr', applicants: 24, filled: 0, maxSubmissions: 5 },
  { id: 'JO-1002', title: 'DevOps Lead', client: 'CloudNine Systems', location: 'Austin, TX', status: 'open', priority: 'high', created: '2026-02-15', billRate: '$150/hr', applicants: 18, filled: 0, maxSubmissions: 3 },
  { id: 'JO-1003', title: 'Data Scientist', client: 'AnalyticsPro', location: 'Remote', status: 'open', priority: 'normal', created: '2026-02-20', billRate: '$125/hr', applicants: 31, filled: 0, maxSubmissions: 4 },
  { id: 'JO-1004', title: 'Product Manager', client: 'InnovateCo', location: 'New York, NY', status: 'open', priority: 'high', created: '2026-02-22', billRate: '$140/hr', applicants: 12, filled: 0, maxSubmissions: 3 },
  { id: 'JO-1005', title: 'UX Designer', client: 'DesignHub', location: 'Seattle, WA', status: 'open', priority: 'normal', created: '2026-03-01', billRate: '$110/hr', applicants: 9, filled: 0, maxSubmissions: 3 },
  { id: 'JO-1006', title: 'ML Engineer', client: 'AI Dynamics', location: 'Boston, MA', status: 'filled', priority: 'urgent', created: '2026-01-15', billRate: '$160/hr', applicants: 28, filled: 2, maxSubmissions: 4 },
];

interface Applicant {
  id: string;
  name: string;
  email: string;
  phone: string;
  currentPhase: string;
  matchScore: number;
  skills: string[];
  experience: string;
  location: string;
  salaryExpectation: string;
  appliedDate: string;
  lastActivity: string;
  source: string;
  jobId: string;
  jobTitle: string;
  client: string;
  notes: string;
  phaseHistory: { phase: string; date: string; by: string }[];
}

const mockApplicants: Applicant[] = [
  { id: 'A-001', name: 'Sarah Chen', email: 'sarah@email.com', phone: '(555) 123-4567', currentPhase: 'interview_scheduled', matchScore: 94, skills: ['React', 'Node.js', 'TypeScript', 'AWS'], experience: '8 years', location: 'San Francisco, CA', salaryExpectation: '$130/hr', appliedDate: '2026-02-12', lastActivity: '2 hours ago', source: 'LinkedIn', jobId: 'JO-1001', jobTitle: 'Senior Full Stack Engineer', client: 'TechCorp Inc.', notes: 'Strong backend experience, led 3 teams', phaseHistory: [{ phase: 'sourced', date: '2026-02-12', by: 'System' }, { phase: 'screening', date: '2026-02-14', by: 'Jane R.' }, { phase: 'submitted', date: '2026-02-16', by: 'Jane R.' }, { phase: 'interview_scheduled', date: '2026-02-20', by: 'Client' }] },
  { id: 'A-002', name: 'Michael Torres', email: 'michael@email.com', phone: '(555) 234-5678', currentPhase: 'submitted', matchScore: 88, skills: ['React', 'Python', 'PostgreSQL'], experience: '6 years', location: 'Austin, TX', salaryExpectation: '$120/hr', appliedDate: '2026-02-14', lastActivity: '1 day ago', source: 'Referral', jobId: 'JO-1001', jobTitle: 'Senior Full Stack Engineer', client: 'TechCorp Inc.', notes: 'Great cultural fit, needs TypeScript ramp-up', phaseHistory: [{ phase: 'sourced', date: '2026-02-14', by: 'System' }, { phase: 'screening', date: '2026-02-16', by: 'John M.' }, { phase: 'submitted', date: '2026-02-19', by: 'John M.' }] },
  { id: 'A-003', name: 'Emily Watson', email: 'emily@email.com', phone: '(555) 345-6789', currentPhase: 'screening', matchScore: 82, skills: ['Java', 'React', 'Docker'], experience: '5 years', location: 'Remote', salaryExpectation: '$115/hr', appliedDate: '2026-02-18', lastActivity: '3 hours ago', source: 'Job Board', jobId: 'JO-1001', jobTitle: 'Senior Full Stack Engineer', client: 'TechCorp Inc.', notes: '', phaseHistory: [{ phase: 'sourced', date: '2026-02-18', by: 'System' }, { phase: 'screening', date: '2026-02-20', by: 'Jane R.' }] },
  { id: 'A-004', name: 'James Kim', email: 'james@email.com', phone: '(555) 456-7890', currentPhase: 'offer_extended', matchScore: 96, skills: ['Kubernetes', 'Terraform', 'AWS', 'CI/CD'], experience: '10 years', location: 'Austin, TX', salaryExpectation: '$145/hr', appliedDate: '2026-02-16', lastActivity: '5 hours ago', source: 'Direct', jobId: 'JO-1002', jobTitle: 'DevOps Lead', client: 'CloudNine Systems', notes: 'Top candidate, client very interested', phaseHistory: [{ phase: 'sourced', date: '2026-02-16', by: 'System' }, { phase: 'screening', date: '2026-02-17', by: 'John M.' }, { phase: 'submitted', date: '2026-02-18', by: 'John M.' }, { phase: 'interview_scheduled', date: '2026-02-20', by: 'Client' }, { phase: 'interview_complete', date: '2026-02-24', by: 'Client' }, { phase: 'offer_extended', date: '2026-02-27', by: 'Jane R.' }] },
  { id: 'A-005', name: 'Priya Sharma', email: 'priya@email.com', phone: '(555) 567-8901', currentPhase: 'sourced', matchScore: 78, skills: ['Python', 'TensorFlow', 'SQL'], experience: '4 years', location: 'Remote', salaryExpectation: '$110/hr', appliedDate: '2026-03-01', lastActivity: '6 hours ago', source: 'LinkedIn', jobId: 'JO-1003', jobTitle: 'Data Scientist', client: 'AnalyticsPro', notes: '', phaseHistory: [{ phase: 'sourced', date: '2026-03-01', by: 'System' }] },
  { id: 'A-006', name: 'David Lee', email: 'david@email.com', phone: '(555) 678-9012', currentPhase: 'interview_complete', matchScore: 91, skills: ['Python', 'PyTorch', 'Spark', 'SQL'], experience: '7 years', location: 'Boston, MA', salaryExpectation: '$130/hr', appliedDate: '2026-02-22', lastActivity: '1 day ago', source: 'Referral', jobId: 'JO-1003', jobTitle: 'Data Scientist', client: 'AnalyticsPro', notes: 'Excellent technical round, pending panel', phaseHistory: [{ phase: 'sourced', date: '2026-02-22', by: 'System' }, { phase: 'screening', date: '2026-02-23', by: 'Jane R.' }, { phase: 'submitted', date: '2026-02-25', by: 'Jane R.' }, { phase: 'interview_scheduled', date: '2026-02-27', by: 'Client' }, { phase: 'interview_complete', date: '2026-03-03', by: 'Client' }] },
  { id: 'A-007', name: 'Anna Rodriguez', email: 'anna@email.com', phone: '(555) 789-0123', currentPhase: 'placed', matchScore: 93, skills: ['Kubernetes', 'AWS', 'Jenkins', 'Python'], experience: '9 years', location: 'Austin, TX', salaryExpectation: '$140/hr', appliedDate: '2026-01-20', lastActivity: '1 week ago', source: 'LinkedIn', jobId: 'JO-1002', jobTitle: 'DevOps Lead', client: 'CloudNine Systems', notes: 'Successfully onboarded', phaseHistory: [{ phase: 'sourced', date: '2026-01-20', by: 'System' }, { phase: 'screening', date: '2026-01-22', by: 'John M.' }, { phase: 'submitted', date: '2026-01-24', by: 'John M.' }, { phase: 'interview_scheduled', date: '2026-01-27', by: 'Client' }, { phase: 'interview_complete', date: '2026-01-31', by: 'Client' }, { phase: 'offer_extended', date: '2026-02-03', by: 'Jane R.' }, { phase: 'offer_accepted', date: '2026-02-05', by: 'Anna R.' }, { phase: 'placed', date: '2026-02-15', by: 'System' }] },
  { id: 'A-008', name: 'Tom Harris', email: 'tom@email.com', phone: '(555) 890-1234', currentPhase: 'rejected', matchScore: 65, skills: ['JavaScript', 'HTML', 'CSS'], experience: '3 years', location: 'Denver, CO', salaryExpectation: '$90/hr', appliedDate: '2026-02-13', lastActivity: '2 weeks ago', source: 'Job Board', jobId: 'JO-1001', jobTitle: 'Senior Full Stack Engineer', client: 'TechCorp Inc.', notes: 'Insufficient experience for senior role', phaseHistory: [{ phase: 'sourced', date: '2026-02-13', by: 'System' }, { phase: 'screening', date: '2026-02-15', by: 'Jane R.' }, { phase: 'rejected', date: '2026-02-16', by: 'Jane R.' }] },
  { id: 'A-009', name: 'Lisa Park', email: 'lisa@email.com', phone: '(555) 901-2345', currentPhase: 'screening', matchScore: 85, skills: ['Figma', 'Sketch', 'CSS', 'React'], experience: '6 years', location: 'Seattle, WA', salaryExpectation: '$105/hr', appliedDate: '2026-03-02', lastActivity: '4 hours ago', source: 'Direct', jobId: 'JO-1005', jobTitle: 'UX Designer', client: 'DesignHub', notes: 'Portfolio looks impressive', phaseHistory: [{ phase: 'sourced', date: '2026-03-02', by: 'System' }, { phase: 'screening', date: '2026-03-04', by: 'John M.' }] },
  { id: 'A-010', name: 'Kevin Patel', email: 'kevin@email.com', phone: '(555) 012-3456', currentPhase: 'submitted', matchScore: 87, skills: ['Product Strategy', 'Agile', 'SQL', 'Jira'], experience: '8 years', location: 'New York, NY', salaryExpectation: '$135/hr', appliedDate: '2026-02-24', lastActivity: '1 day ago', source: 'Referral', jobId: 'JO-1004', jobTitle: 'Product Manager', client: 'InnovateCo', notes: 'Strong PM background in fintech', phaseHistory: [{ phase: 'sourced', date: '2026-02-24', by: 'System' }, { phase: 'screening', date: '2026-02-26', by: 'Jane R.' }, { phase: 'submitted', date: '2026-02-28', by: 'Jane R.' }] },
];

// ── Utility ──
const getPhaseConfig = (phaseKey: string) => PIPELINE_PHASES.find(p => p.key === phaseKey) || PIPELINE_PHASES[0];

const priorityColors: Record<string, string> = {
  urgent: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  normal: 'bg-blue-100 text-blue-700',
  low: 'bg-gray-100 text-gray-600',
};

// ── Score Badge ──
const ScoreBadge: React.FC<{ score: number }> = ({ score }) => {
  const color = score >= 90 ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : score >= 75 ? 'text-blue-600 bg-blue-50 border-blue-200' : score >= 60 ? 'text-amber-600 bg-amber-50 border-amber-200' : 'text-red-600 bg-red-50 border-red-200';
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${color}`}>{score}%</span>;
};

// ══════════════════════════════════════════════
// VIEW BY JOB TAB
// ══════════════════════════════════════════════
const ViewByJob: React.FC = () => {
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [selectedPhase, setSelectedPhase] = useState<string | null>(null);
  const [applicants, setApplicants] = useState(mockApplicants);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [actionMenuOpen, setActionMenuOpen] = useState<string | null>(null);

  const filteredJobs = mockJobs.filter(j => {
    const matchesSearch = j.title.toLowerCase().includes(searchTerm.toLowerCase()) || j.client.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || j.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const jobApplicants = applicants.filter(a => a.jobId === selectedJob);
  const phaseApplicants = selectedPhase ? jobApplicants.filter(a => a.currentPhase === selectedPhase) : [];
  const selectedJobData = mockJobs.find(j => j.id === selectedJob);

  const phaseCounts = PIPELINE_PHASES.reduce((acc, phase) => {
    acc[phase.key] = jobApplicants.filter(a => a.currentPhase === phase.key).length;
    return acc;
  }, {} as Record<string, number>);

  const moveApplicant = useCallback((applicantId: string, newPhase: string) => {
    setApplicants(prev => prev.map(a => {
      if (a.id === applicantId) {
        return {
          ...a,
          currentPhase: newPhase,
          lastActivity: 'Just now',
          phaseHistory: [...a.phaseHistory, { phase: newPhase, date: new Date().toISOString().split('T')[0], by: 'You' }],
        };
      }
      return a;
    }));
    setActionMenuOpen(null);
    // In production: axios.put(`/api/v1/submissions/${applicantId}`, { status: newPhase })
  }, []);

  // ── Job List View ──
  if (!selectedJob) {
    return (
      <div>
        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input type="text" placeholder="Search jobs by title or client..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
          </div>
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="px-3 py-2 border border-neutral-200 rounded-lg text-sm">
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="filled">Filled</option>
            <option value="on_hold">On Hold</option>
          </select>
        </div>

        {/* Jobs Table */}
        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-neutral-50 border-b border-neutral-200">
                <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Job Order</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Client</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Location</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Priority</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Applicants</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Rate</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Status</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {filteredJobs.map(job => (
                <tr key={job.id} className="hover:bg-blue-50/50 cursor-pointer transition-colors" onClick={() => setSelectedJob(job.id)}>
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-sm font-semibold text-neutral-900">{job.title}</p>
                      <p className="text-xs text-neutral-500">{job.id} &middot; Posted {job.created}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <BuildingOffice2Icon className="w-4 h-4 text-neutral-400" />
                      <span className="text-sm text-neutral-700">{job.client}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4 text-neutral-400" />
                      <span className="text-sm text-neutral-600">{job.location}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${priorityColors[job.priority]}`}>{job.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-neutral-700">
                      <UserGroupIcon className="w-4 h-4" /> {job.applicants}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-sm font-medium text-emerald-600">{job.billRate}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${job.status === 'open' ? 'bg-green-100 text-green-700' : job.status === 'filled' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>{job.status}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800">
                      View Pipeline <ChevronRightIcon className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // ── Phase Pipeline View (Job selected) ──
  if (selectedJob && !selectedPhase) {
    return (
      <div>
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-6 text-sm">
          <button onClick={() => setSelectedJob(null)} className="text-blue-600 hover:text-blue-800 font-medium">All Jobs</button>
          <ChevronRightIcon className="w-4 h-4 text-neutral-400" />
          <span className="text-neutral-700 font-semibold">{selectedJobData?.title}</span>
          <span className="text-neutral-400">({selectedJobData?.client})</span>
        </div>

        {/* Job Summary Card */}
        <div className="bg-white rounded-xl border border-neutral-200 p-5 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-bold text-neutral-900">{selectedJobData?.title}</h3>
              <div className="flex items-center gap-4 mt-2 text-sm text-neutral-500">
                <span className="flex items-center gap-1"><BuildingOffice2Icon className="w-4 h-4" />{selectedJobData?.client}</span>
                <span className="flex items-center gap-1"><MapPinIcon className="w-4 h-4" />{selectedJobData?.location}</span>
                <span className="flex items-center gap-1"><CurrencyDollarIcon className="w-4 h-4" />{selectedJobData?.billRate}</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-neutral-900">{jobApplicants.length}</p>
              <p className="text-xs text-neutral-500">Total Applicants</p>
            </div>
          </div>
        </div>

        {/* Phase Pipeline Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
          {PIPELINE_PHASES.filter(p => p.key !== 'rejected').map((phase, idx) => (
            <button key={phase.key} onClick={() => { if (phaseCounts[phase.key] > 0) setSelectedPhase(phase.key); }} className={`relative bg-white rounded-xl border-2 p-4 text-left transition-all hover:shadow-md ${phaseCounts[phase.key] > 0 ? 'border-neutral-200 hover:border-blue-400 cursor-pointer' : 'border-neutral-100 opacity-60 cursor-default'}`}>
              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${phase.color}`}>
                  <phase.icon className="w-4 h-4" />
                </div>
                {idx < PIPELINE_PHASES.length - 2 && phaseCounts[phase.key] > 0 && (
                  <ArrowRightIcon className="w-4 h-4 text-neutral-300" />
                )}
              </div>
              <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider">{phase.label}</p>
              <p className="text-2xl font-bold text-neutral-900 mt-1">{phaseCounts[phase.key]}</p>
            </button>
          ))}
        </div>

        {/* Rejected count */}
        {phaseCounts['rejected'] > 0 && (
          <button onClick={() => setSelectedPhase('rejected')} className="w-full bg-red-50 rounded-xl border border-red-200 p-4 text-left hover:bg-red-100 transition-colors mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <XCircleIcon className="w-5 h-5 text-red-500" />
                <span className="text-sm font-medium text-red-700">Rejected Applicants</span>
              </div>
              <span className="text-lg font-bold text-red-700">{phaseCounts['rejected']}</span>
            </div>
          </button>
        )}

        {/* All Applicants Quick List */}
        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-200 bg-neutral-50">
            <h4 className="text-sm font-semibold text-neutral-700">All Applicants for this Job</h4>
          </div>
          <div className="divide-y divide-neutral-100">
            {jobApplicants.map(applicant => {
              const phaseConf = getPhaseConfig(applicant.currentPhase);
              return (
                <div key={applicant.id} className="flex items-center justify-between px-4 py-3 hover:bg-neutral-50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-700">{applicant.name.split(' ').map(n => n[0]).join('')}</div>
                    <div>
                      <p className="text-sm font-medium text-neutral-900">{applicant.name}</p>
                      <p className="text-xs text-neutral-500">{applicant.experience} exp &middot; {applicant.location}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <ScoreBadge score={applicant.matchScore} />
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${phaseConf.color}`}>
                      <phaseConf.icon className="w-3 h-3" /> {phaseConf.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // ── Applicants by Phase (Phase selected) ──
  const phaseConf = getPhaseConfig(selectedPhase!);
  const actions = PHASE_ACTIONS[selectedPhase!] || [];

  return (
    <div>
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6 text-sm">
        <button onClick={() => setSelectedJob(null)} className="text-blue-600 hover:text-blue-800 font-medium">All Jobs</button>
        <ChevronRightIcon className="w-4 h-4 text-neutral-400" />
        <button onClick={() => setSelectedPhase(null)} className="text-blue-600 hover:text-blue-800 font-medium">{selectedJobData?.title}</button>
        <ChevronRightIcon className="w-4 h-4 text-neutral-400" />
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${phaseConf.color}`}>
          <phaseConf.icon className="w-3 h-3" /> {phaseConf.label}
        </span>
        <span className="text-neutral-500">({phaseApplicants.length} applicants)</span>
      </div>

      {/* Applicant Cards */}
      <div className="space-y-3">
        {phaseApplicants.length === 0 ? (
          <div className="bg-white rounded-xl border border-neutral-200 p-12 text-center">
            <UserGroupIcon className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
            <p className="text-neutral-500">No applicants in this phase</p>
          </div>
        ) : phaseApplicants.map(applicant => (
          <div key={applicant.id} className="bg-white rounded-xl border border-neutral-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-700 flex-shrink-0">{applicant.name.split(' ').map(n => n[0]).join('')}</div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-neutral-900">{applicant.name}</h4>
                    <ScoreBadge score={applicant.matchScore} />
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                    <span className="flex items-center gap-1"><MapPinIcon className="w-3 h-3" />{applicant.location}</span>
                    <span className="flex items-center gap-1"><BriefcaseIcon className="w-3 h-3" />{applicant.experience}</span>
                    <span className="flex items-center gap-1"><CurrencyDollarIcon className="w-3 h-3" />{applicant.salaryExpectation}</span>
                    <span className="flex items-center gap-1"><ClockIcon className="w-3 h-3" />{applicant.lastActivity}</span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                    {applicant.skills.slice(0, 5).map(s => (
                      <span key={s} className="px-2 py-0.5 rounded bg-neutral-100 text-neutral-600 text-xs">{s}</span>
                    ))}
                  </div>
                  {applicant.notes && <p className="text-xs text-neutral-500 mt-2 italic">"{applicant.notes}"</p>}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 flex-shrink-0 relative">
                {actions.slice(0, 2).map(action => (
                  <button key={action.label} onClick={() => moveApplicant(applicant.id, action.nextPhase)} className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${action.nextPhase === 'rejected' ? 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200' : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200'}`} title={`Move to ${action.label}`}>
                    <action.icon className="w-3.5 h-3.5" />
                    {action.label}
                  </button>
                ))}
                {actions.length > 2 && (
                  <div className="relative">
                    <button onClick={() => setActionMenuOpen(actionMenuOpen === applicant.id ? null : applicant.id)} className="p-1.5 rounded-lg hover:bg-neutral-100 text-neutral-500">
                      <EllipsisVerticalIcon className="w-4 h-4" />
                    </button>
                    {actionMenuOpen === applicant.id && (
                      <div className="absolute right-0 top-8 bg-white rounded-lg shadow-lg border border-neutral-200 py-1 z-20 min-w-[160px]">
                        {actions.slice(2).map(action => (
                          <button key={action.label} onClick={() => moveApplicant(applicant.id, action.nextPhase)} className="w-full flex items-center gap-2 px-3 py-2 text-xs text-neutral-700 hover:bg-neutral-50">
                            <action.icon className="w-3.5 h-3.5" /> {action.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ══════════════════════════════════════════════
// VIEW BY APPLICANT TAB
// ══════════════════════════════════════════════
const ViewByApplicant: React.FC = () => {
  const [applicants, setApplicants] = useState(mockApplicants);
  const [selectedApplicant, setSelectedApplicant] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [phaseFilter, setPhaseFilter] = useState<string>('all');
  const [actionMenuOpen, setActionMenuOpen] = useState<string | null>(null);

  const filteredApplicants = applicants.filter(a => {
    const matchesSearch = a.name.toLowerCase().includes(searchTerm.toLowerCase()) || a.skills.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesPhase = phaseFilter === 'all' || a.currentPhase === phaseFilter;
    return matchesSearch && matchesPhase;
  });

  const applicantData = applicants.find(a => a.id === selectedApplicant);

  const moveApplicant = useCallback((applicantId: string, newPhase: string) => {
    setApplicants(prev => prev.map(a => {
      if (a.id === applicantId) {
        return {
          ...a,
          currentPhase: newPhase,
          lastActivity: 'Just now',
          phaseHistory: [...a.phaseHistory, { phase: newPhase, date: new Date().toISOString().split('T')[0], by: 'You' }],
        };
      }
      return a;
    }));
    setActionMenuOpen(null);
  }, []);

  // ── Applicant List ──
  if (!selectedApplicant) {
    return (
      <div>
        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input type="text" placeholder="Search by name or skill..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
          </div>
          <select value={phaseFilter} onChange={e => setPhaseFilter(e.target.value)} className="px-3 py-2 border border-neutral-200 rounded-lg text-sm">
            <option value="all">All Phases</option>
            {PIPELINE_PHASES.map(p => (
              <option key={p.key} value={p.key}>{p.label}</option>
            ))}
          </select>
        </div>

        {/* Phase Summary Row */}
        <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
          {PIPELINE_PHASES.filter(p => p.key !== 'rejected').map(phase => {
            const count = applicants.filter(a => a.currentPhase === phase.key).length;
            return (
              <button key={phase.key} onClick={() => setPhaseFilter(phase.key === phaseFilter ? 'all' : phase.key)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border whitespace-nowrap transition-all ${phaseFilter === phase.key ? 'bg-blue-600 text-white border-blue-600' : phase.color}`}>
                <phase.icon className="w-3 h-3" /> {phase.label} ({count})
              </button>
            );
          })}
        </div>

        {/* Applicants Table */}
        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-neutral-50 border-b border-neutral-200">
                <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Applicant</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Job / Client</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Score</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Current Phase</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Skills</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Last Activity</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {filteredApplicants.map(applicant => {
                const phaseConf = getPhaseConfig(applicant.currentPhase);
                const actions = PHASE_ACTIONS[applicant.currentPhase] || [];
                return (
                  <tr key={applicant.id} className="hover:bg-blue-50/50 transition-colors">
                    <td className="px-4 py-3 cursor-pointer" onClick={() => setSelectedApplicant(applicant.id)}>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-700">{applicant.name.split(' ').map(n => n[0]).join('')}</div>
                        <div>
                          <p className="text-sm font-semibold text-neutral-900">{applicant.name}</p>
                          <p className="text-xs text-neutral-500">{applicant.experience} &middot; {applicant.location}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-sm text-neutral-700">{applicant.jobTitle}</p>
                      <p className="text-xs text-neutral-500">{applicant.client}</p>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <ScoreBadge score={applicant.matchScore} />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${phaseConf.color}`}>
                        <phaseConf.icon className="w-3 h-3" /> {phaseConf.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1 flex-wrap max-w-[200px]">
                        {applicant.skills.slice(0, 3).map(s => (
                          <span key={s} className="px-1.5 py-0.5 rounded bg-neutral-100 text-neutral-600 text-[10px]">{s}</span>
                        ))}
                        {applicant.skills.length > 3 && <span className="text-[10px] text-neutral-400">+{applicant.skills.length - 3}</span>}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="text-xs text-neutral-500">{applicant.lastActivity}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-1 relative">
                        {actions.length > 0 && (() => {
                          const PrimaryIcon = actions[0].icon;
                          return (
                            <button onClick={() => moveApplicant(applicant.id, actions[0].nextPhase)} className={`inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-medium ${actions[0].nextPhase === 'rejected' ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'}`}>
                              <PrimaryIcon className="w-3 h-3" /> {actions[0].label}
                            </button>
                          );
                        })()}
                        {actions.length > 1 && (
                          <div className="relative">
                            <button onClick={() => setActionMenuOpen(actionMenuOpen === applicant.id ? null : applicant.id)} className="p-1 rounded hover:bg-neutral-100 text-neutral-400">
                              <EllipsisVerticalIcon className="w-4 h-4" />
                            </button>
                            {actionMenuOpen === applicant.id && (
                              <div className="absolute right-0 top-7 bg-white rounded-lg shadow-lg border border-neutral-200 py-1 z-20 min-w-[140px]">
                                {actions.slice(1).map(action => (
                                  <button key={action.label} onClick={() => moveApplicant(applicant.id, action.nextPhase)} className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-neutral-700 hover:bg-neutral-50">
                                    <action.icon className="w-3 h-3" /> {action.label}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // ── Applicant Detail View (Journey) ──
  if (!applicantData) return null;
  const currentPhaseConf = getPhaseConfig(applicantData.currentPhase);
  const currentActions = PHASE_ACTIONS[applicantData.currentPhase] || [];

  return (
    <div>
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6 text-sm">
        <button onClick={() => setSelectedApplicant(null)} className="text-blue-600 hover:text-blue-800 font-medium">All Applicants</button>
        <ChevronRightIcon className="w-4 h-4 text-neutral-400" />
        <span className="text-neutral-700 font-semibold">{applicantData.name}</span>
      </div>

      {/* Applicant Profile Card */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-lg font-bold text-blue-700">{applicantData.name.split(' ').map(n => n[0]).join('')}</div>
            <div>
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-bold text-neutral-900">{applicantData.name}</h3>
                <ScoreBadge score={applicantData.matchScore} />
                <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${currentPhaseConf.color}`}>
                  <currentPhaseConf.icon className="w-3 h-3" /> {currentPhaseConf.label}
                </span>
              </div>
              <div className="flex items-center gap-4 mt-2 text-sm text-neutral-500">
                <span className="flex items-center gap-1"><EnvelopeIcon className="w-4 h-4" />{applicantData.email}</span>
                <span className="flex items-center gap-1"><PhoneIcon className="w-4 h-4" />{applicantData.phone}</span>
                <span className="flex items-center gap-1"><MapPinIcon className="w-4 h-4" />{applicantData.location}</span>
              </div>
              <div className="flex items-center gap-4 mt-1 text-sm text-neutral-500">
                <span className="flex items-center gap-1"><BriefcaseIcon className="w-4 h-4" />{applicantData.experience}</span>
                <span className="flex items-center gap-1"><CurrencyDollarIcon className="w-4 h-4" />{applicantData.salaryExpectation}</span>
                <span className="flex items-center gap-1"><ChatBubbleLeftRightIcon className="w-4 h-4" />Source: {applicantData.source}</span>
              </div>
              <div className="flex items-center gap-1.5 mt-3">
                {applicantData.skills.map(s => (
                  <span key={s} className="px-2 py-0.5 rounded bg-blue-50 text-blue-600 text-xs font-medium">{s}</span>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {currentActions.map(action => (
              <button key={action.label} onClick={() => moveApplicant(applicantData.id, action.nextPhase)} className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${action.nextPhase === 'rejected' ? 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200' : 'bg-blue-600 text-white hover:bg-blue-700'}`}>
                <action.icon className="w-4 h-4" /> {action.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Applied Job Info */}
      <div className="bg-white rounded-xl border border-neutral-200 p-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
            <BriefcaseIcon className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-neutral-900">{applicantData.jobTitle}</p>
            <p className="text-xs text-neutral-500">{applicantData.client} &middot; Applied {applicantData.appliedDate}</p>
          </div>
        </div>
      </div>

      {/* Phase Journey Timeline */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5 mb-6">
        <h4 className="text-sm font-semibold text-neutral-700 mb-4">Pipeline Journey</h4>

        {/* Phase Progress Bar */}
        <div className="flex items-center gap-1 mb-6">
          {PIPELINE_PHASES.filter(p => p.key !== 'rejected').map((phase, idx) => {
            const isCompleted = applicantData.phaseHistory.some(h => h.phase === phase.key);
            const isCurrent = applicantData.currentPhase === phase.key;
            return (
              <React.Fragment key={phase.key}>
                <div className={`flex-1 h-2 rounded-full transition-colors ${isCompleted ? phase.activeColor : isCurrent ? phase.activeColor + ' animate-pulse' : 'bg-neutral-200'}`} title={phase.label} />
                {idx < PIPELINE_PHASES.length - 2 && <div className="w-1" />}
              </React.Fragment>
            );
          })}
        </div>

        {/* Timeline */}
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-neutral-200" />
          <div className="space-y-4">
            {applicantData.phaseHistory.map((entry, idx) => {
              const conf = getPhaseConfig(entry.phase);
              const isLast = idx === applicantData.phaseHistory.length - 1;
              return (
                <div key={idx} className="relative flex items-start gap-4 pl-9">
                  <div className={`absolute left-2.5 w-3 h-3 rounded-full border-2 border-white ${isLast ? conf.activeColor : 'bg-neutral-400'}`} style={{ top: '4px' }} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${conf.color}`}>
                        <conf.icon className="w-3 h-3" /> {conf.label}
                      </span>
                      <span className="text-xs text-neutral-400">{entry.date}</span>
                    </div>
                    <p className="text-xs text-neutral-500 mt-0.5">By {entry.by}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Notes */}
      {applicantData.notes && (
        <div className="bg-white rounded-xl border border-neutral-200 p-4">
          <h4 className="text-sm font-semibold text-neutral-700 mb-2">Notes</h4>
          <p className="text-sm text-neutral-600">{applicantData.notes}</p>
        </div>
      )}
    </div>
  );
};

// ══════════════════════════════════════════════
// MAIN ATS WORKFLOW COMPONENT
// ══════════════════════════════════════════════
export const ATSWorkflow: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'job' | 'applicant'>('job');

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">ATS Workflow</h1>
          <p className="text-sm text-neutral-500 mt-1">Track applicants through hiring pipeline phases</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-neutral-500">
          <ArrowTrendingUpIcon className="w-4 h-4" />
          <span>{mockApplicants.length} active applicants across {mockJobs.filter(j => j.status === 'open').length} open jobs</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-neutral-100 rounded-lg p-1 mb-6 w-fit">
        <button onClick={() => setActiveTab('job')} className={`flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium transition-all ${activeTab === 'job' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'}`}>
          <BriefcaseIcon className="w-4 h-4" /> View by Job
        </button>
        <button onClick={() => setActiveTab('applicant')} className={`flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium transition-all ${activeTab === 'applicant' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'}`}>
          <UserGroupIcon className="w-4 h-4" /> View by Applicant
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'job' ? <ViewByJob /> : <ViewByApplicant />}
    </div>
  );
};
