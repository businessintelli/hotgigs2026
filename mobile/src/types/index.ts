export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'recruiter' | 'manager' | 'candidate';
  avatar?: string;
  phone?: string;
  department?: string;
  joinedDate: string;
}

export interface Requirement {
  id: string;
  title: string;
  description: string;
  department: string;
  location: string;
  salary_range: {
    min: number;
    max: number;
    currency: string;
  };
  status: 'open' | 'filled' | 'closed';
  posted_date: string;
  deadline?: string;
  required_skills: string[];
  experience_level: string;
  candidate_count: number;
  applications_count: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface Candidate {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  location: string;
  current_title: string;
  skills: string[];
  experience_years: number;
  avatar?: string;
  resume_url?: string;
  ratings: number;
  preferred_locations?: string[];
  availability: 'immediate' | '2weeks' | '1month' | '2months';
}

export interface Submission {
  id: string;
  candidate_id: string;
  requirement_id: string;
  status: 'submitted' | 'screening' | 'interview' | 'offer' | 'rejected' | 'hired';
  submitted_date: string;
  last_updated: string;
  notes?: string;
  interview_scheduled?: string;
  rating?: number;
  offer_amount?: number;
  candidate: Candidate;
  requirement: Requirement;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  attachments?: Array<{
    type: 'image' | 'file';
    url: string;
    name: string;
  }>;
}

export interface Contract {
  id: string;
  title: string;
  candidate_name: string;
  status: 'pending' | 'signed' | 'executed' | 'expired';
  created_date: string;
  signature_date?: string;
  expiry_date?: string;
  document_url: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'action';
  timestamp: string;
  read: boolean;
  action_url?: string;
  data?: Record<string, any>;
}

export interface KPI {
  title: string;
  value: string | number;
  change?: number;
  trend: 'up' | 'down' | 'neutral';
  icon: string;
  color: string;
}

export interface PipelineData {
  stage: string;
  count: number;
  percentage: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface DashboardStats {
  total_requirements: number;
  open_requirements: number;
  active_candidates: number;
  pending_submissions: number;
  interviews_this_week: number;
  offers_pending: number;
  hire_rate: number;
  avg_time_to_hire: number;
  pipeline: PipelineData[];
  recent_activity: Array<{
    id: string;
    action: string;
    timestamp: string;
    candidate?: string;
    requirement?: string;
  }>;
}

export interface FilterOptions {
  status?: string;
  department?: string;
  location?: string;
  skills?: string[];
  experience_level?: string;
  salary_range?: {
    min: number;
    max: number;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, any>;
}

export interface BiometricConfig {
  enabled: boolean;
  type: 'faceId' | 'touchId' | 'faceRecognition' | 'fingerprint' | null;
  available: boolean;
}

export interface ThemeConfig {
  primary: string;
  accent: string;
  background: string;
  surface: string;
  error: string;
  success: string;
  warning: string;
  info: string;
}

export interface AppSettings {
  theme: 'light' | 'dark';
  notifications_enabled: boolean;
  push_notifications: boolean;
  email_notifications: boolean;
  biometric_auth: boolean;
  remember_me: boolean;
  language: string;
  timezone: string;
}
