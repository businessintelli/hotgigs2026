export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'recruiter' | 'admin' | 'manager' | 'viewer';
  is_active: boolean;
  avatar_url?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface Requirement {
  id: string;
  title: string;
  customer_id: string;
  customer_name: string;
  description: string;
  status: 'open' | 'closed' | 'on_hold' | 'filled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  skills_required: Skill[];
  experience_min: number;
  experience_max: number;
  experience_unit: 'months' | 'years';
  location: string;
  remote_policy: 'on_site' | 'hybrid' | 'remote';
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  submission_count: number;
  active_submissions: number;
  interviews_scheduled: number;
  placements: number;
  created_at: string;
  updated_at: string;
  filled_at?: string;
  closed_at?: string;
  deadline?: string;
  job_type: 'permanent' | 'contract' | 'temporary';
  created_by: string;
}

export interface Skill {
  name: string;
  proficiency?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  years_of_experience?: number;
}

export interface Candidate {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  location?: string;
  skills: Skill[];
  status: 'active' | 'inactive' | 'placed' | 'archived';
  total_experience_years: number;
  current_title?: string;
  current_company?: string;
  availability: 'immediate' | 'two_weeks' | 'one_month' | 'negotiable';
  rate_expected?: number;
  rate_currency?: string;
  resume_url?: string;
  video_intro_urls: string[];
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  created_at: string;
  updated_at: string;
  last_contacted_at?: string;
}

export interface Submission {
  id: string;
  requirement_id: string;
  candidate_id: string;
  candidate: Candidate;
  requirement: Requirement;
  status: 'draft' | 'pending' | 'approved' | 'submitted' | 'customer_review' | 'placed' | 'rejected';
  match_score: number;
  rate_proposed?: number;
  rate_currency?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  approved_at?: string;
  placed_at?: string;
  rejected_at?: string;
  rejected_reason?: string;
}

export interface Interview {
  id: string;
  candidate_id: string;
  requirement_id: string;
  candidate: Candidate;
  requirement: Requirement;
  interview_type: 'phone' | 'video' | 'in_person' | 'technical' | 'final';
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show';
  scheduled_at: string;
  duration_minutes: number;
  interviewer_id?: string;
  interviewer_name?: string;
  feedback?: string;
  rating?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Contract {
  id: string;
  title: string;
  contract_type: 'nda' | 'employment' | 'service_agreement' | 'vendor_agreement';
  status: 'draft' | 'pending_signature' | 'completed' | 'expired';
  parties: string[];
  content: string;
  signers: ContractSigner[];
  created_at: string;
  updated_at: string;
  signed_at?: string;
  expires_at?: string;
  created_by: string;
}

export interface ContractSigner {
  id: string;
  email: string;
  name: string;
  signed_at?: string;
  signed: boolean;
}

export interface Supplier {
  id: string;
  company_name: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  tier: 'preferred' | 'standard' | 'managed';
  total_placements: number;
  total_revenue: number;
  commission_rate: number;
  active_requirements: number;
  performance_score: number;
  created_at: string;
  updated_at: string;
}

export interface Referral {
  id: string;
  referrer_id: string;
  referrer_name: string;
  candidate_id: string;
  candidate: Candidate;
  status: 'pending' | 'placed' | 'rejected' | 'withdrawn';
  bonus_amount?: number;
  bonus_currency?: string;
  payment_status: 'pending' | 'paid' | 'forfeited';
  created_at: string;
  updated_at: string;
  placed_at?: string;
  bonus_paid_at?: string;
}

export interface DashboardOverview {
  total_active_requirements: number;
  candidates_in_pipeline: number;
  submissions_this_month: number;
  placements_this_month: number;
  average_time_to_fill_days: number;
  fill_rate_percentage: number;
  open_interviews_this_week: number;
  pending_approvals: number;
}

export interface PipelineMetrics {
  stages: PipelineStage[];
  total_candidates: number;
  conversion_rate: number;
}

export interface PipelineStage {
  name: string;
  count: number;
  average_days_in_stage: number;
  color?: string;
}

export interface SubmissionFunnel {
  draft: number;
  pending: number;
  approved: number;
  submitted: number;
  customer_review: number;
  placed: number;
  rejected: number;
}

export interface ActivityFeed {
  id: string;
  type: 'submission_created' | 'interview_scheduled' | 'candidate_added' | 'requirement_filled' | 'contract_signed';
  actor_id: string;
  actor_name: string;
  entity_id: string;
  entity_type: string;
  entity_name: string;
  description: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export interface RecruitersPerformance {
  recruiter_id: string;
  recruiter_name: string;
  placements_this_month: number;
  average_time_to_fill: number;
  submissions_pending: number;
  active_requirements: number;
  total_revenue: number;
  rank: number;
}

export interface RequirementUrgency {
  requirement_id: string;
  title: string;
  days_open: number;
  priority: string;
  submissions_count: number;
  days_remaining?: number;
}

export interface CopilotMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  metadata?: Record<string, unknown>;
}

export interface CopilotConversation {
  id: string;
  title: string;
  messages: CopilotMessage[];
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  status: number;
  message: string;
  code: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface FilterParams {
  page?: number;
  per_page?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  [key: string]: unknown;
}

export interface CreateRequirementInput {
  title: string;
  customer_id: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  skills_required: Skill[];
  experience_min: number;
  experience_max: number;
  experience_unit: 'months' | 'years';
  location: string;
  remote_policy: 'on_site' | 'hybrid' | 'remote';
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  job_type: 'permanent' | 'contract' | 'temporary';
  deadline?: string;
}

export interface CreateCandidateInput {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  location?: string;
  skills: Skill[];
  total_experience_years: number;
  current_title?: string;
  current_company?: string;
  availability: 'immediate' | 'two_weeks' | 'one_month' | 'negotiable';
  rate_expected?: number;
  rate_currency?: string;
  resume_url?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
}

export interface CreateSubmissionInput {
  requirement_id: string;
  candidate_id: string;
  rate_proposed?: number;
  notes?: string;
}

export interface ScheduleInterviewInput {
  candidate_id: string;
  requirement_id: string;
  interview_type: 'phone' | 'video' | 'in_person' | 'technical' | 'final';
  scheduled_at: string;
  duration_minutes: number;
  interviewer_id?: string;
}

export interface UpdateSubmissionStatusInput {
  status: 'pending' | 'approved' | 'submitted' | 'customer_review' | 'placed' | 'rejected';
  notes?: string;
  rejected_reason?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface Report {
  id: string;
  name: string;
  description: string;
  type: 'standard' | 'custom';
  data_source: string;
  columns: string[];
  filters?: Record<string, unknown>;
  created_at: string;
  created_by: string;
  scheduled?: boolean;
  schedule_frequency?: 'daily' | 'weekly' | 'monthly';
  last_run_at?: string;
}

export interface ReportResult {
  report_id: string;
  data: unknown[];
  total_rows: number;
  generated_at: string;
}

export interface SystemConfig {
  key: string;
  value: unknown;
  type: 'string' | 'number' | 'boolean' | 'json';
  description: string;
}

export interface SecurityAlert {
  id: string;
  level: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  affected_resource?: string;
  created_at: string;
}

export interface AgentHealthStatus {
  agent_id: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  last_heartbeat: string;
  error_message?: string;
  processing_queue_size: number;
}
