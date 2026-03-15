import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from '@/store/authStore';

// Pages
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
import { Candidates } from '@/pages/Candidates';
import { Requirements } from '@/pages/Requirements';
import { Submissions } from '@/pages/Submissions';
import { Interviews } from '@/pages/Interviews';
import { Contracts } from '@/pages/Contracts';
import { Suppliers } from '@/pages/Suppliers';
import { Referrals } from '@/pages/Referrals';
import { Copilot } from '@/pages/Copilot';
import { Reports } from '@/pages/Reports';
import { Settings } from '@/pages/Settings';
import { Admin } from '@/pages/Admin';

// Analytics Pages
import { CandidateScoreCard } from '@/pages/CandidateScoreCard';
import { JobFitAnalysis } from '@/pages/JobFitAnalysis';
import { SkillGapAnalyzer } from '@/pages/SkillGapAnalyzer';
import { RecruiterDashboard } from '@/pages/RecruiterDashboard';
import { ApplicantTracker } from '@/pages/ApplicantTracker';
import { AIPredictionsPanel } from '@/pages/AIPredictionsPanel';

// CRM & ATS Pages
import { CandidateCRM } from '@/pages/CandidateCRM';
import { JobOrderManager } from '@/pages/JobOrderManager';
import { OfferManagement } from '@/pages/OfferManagement';
import { OnboardingTracker } from '@/pages/OnboardingTracker';
import { InterviewInsights } from '@/pages/InterviewInsights';
import { AdvancedSearch } from '@/pages/AdvancedSearch';
import { AutomationCenter } from '@/pages/AutomationCenter';

// ATS Workflow
import { ATSWorkflow } from '@/pages/ATSWorkflow';

// Aggregate Reports
import { AggregateReports } from '@/pages/AggregateReports';

// Custom Report Builder
import { CustomReportBuilder } from '@/pages/CustomReportBuilder';

// Testing Dashboard
import { TestingDashboard } from '@/pages/TestingDashboard';

// Resume Hub
import { ResumeHub } from '@/pages/ResumeHub';
import { PipelineAnalytics } from '@/pages/PipelineAnalytics';
import { CandidateNotifications } from '@/pages/CandidateNotifications';
import { InterviewFeedbackForms } from '@/pages/InterviewFeedbackForms';

// Data Operations Pages
import { BulkImportCenter } from '@/pages/BulkImportCenter';
import { BulkAnalysisDashboard } from '@/pages/BulkAnalysisDashboard';
import { ExportCenter } from '@/pages/ExportCenter';

// New Feature Pages — MSP Billing, BGC/Onboarding, Asset Management
import { MSPBillingCenter } from '@/pages/MSPBillingCenter';
import { BGCOnboarding } from '@/pages/BGCOnboarding';
import { AssetManagement } from '@/pages/AssetManagement';

// Email Agent, Resume Match, Notification Hub
import { EmailAgentCenter } from '@/pages/EmailAgentCenter';
import { ResumeMatchCenter } from '@/pages/ResumeMatchCenter';
import { NotificationCollabHub } from '@/pages/NotificationCollabHub';

// Admin Configuration (App + Company Level)
import { CompanyAdminConfig } from '@/pages/CompanyAdminConfig';
import { AppAdminConfig } from '@/pages/AppAdminConfig';

// Financial Reports
import { ProfitAndLoss } from '@/pages/ProfitAndLoss';
import { RevenueExpenseBreakdown } from '@/pages/RevenueExpenseBreakdown';
import { ReceivablesPayables } from '@/pages/ReceivablesPayables';
import { AssociateFinancials } from '@/pages/AssociateFinancials';
import { RevenueAnalytics } from '@/pages/RevenueAnalytics';

// Agreement Management
import { AgreementCenter } from '@/pages/AgreementCenter';
import { AgreementBuilder } from '@/pages/AgreementBuilder';
import { ESignaturePortal } from '@/pages/ESignaturePortal';

// Interview Feedback & Score Intelligence
import { DetailedFeedbackCollector } from '@/pages/DetailedFeedbackCollector';
import { CandidateScoreIntelligence } from '@/pages/CandidateScoreIntelligence';
import ScoreAnalyticsDashboard from '@/pages/ScoreAnalyticsDashboard';

// MSP Pages
import { MSPDashboard } from '@/pages/msp/MSPDashboard';
import { ClientsList } from '@/pages/msp/ClientsList';
import { SuppliersList } from '@/pages/msp/SuppliersList';
import { SubmissionsPipeline } from '@/pages/msp/SubmissionsPipeline';
import { RateCards } from '@/pages/msp/RateCards';
import { ComplianceDashboard } from '@/pages/msp/ComplianceDashboard';
import { SLADashboard } from '@/pages/msp/SLADashboard';
import { VMSTimesheets } from '@/pages/msp/VMSTimesheets';

// Client Pages
import { ClientDashboard } from '@/pages/client/ClientDashboard';
import { ClientTimesheets } from '@/pages/client/Timesheets';

// Supplier Pages
import { SupplierDashboard } from '@/pages/supplier/SupplierDashboard';
import { SupplierTimesheets } from '@/pages/supplier/Timesheets';

// Layout
import { AppLayout } from '@/components/layout/AppLayout';
import { OrgSwitcher } from '@/components/layout/OrgSwitcher';

// Guards
import { OrgTypeGuard } from '@/components/guards/OrgTypeGuard';
import { RoleGuard } from '@/components/guards/RoleGuard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const AuthenticatedLayout: React.FC<{ children: React.ReactNode; title?: string }> = ({
  children,
  title,
}) => (
  <ProtectedRoute>
    <AppLayout title={title}>{children}</AppLayout>
  </ProtectedRoute>
);

// Placeholder component factory
const PlaceholderPage = (pageName: string) => () => (
  <div className="p-8">
    <h1 className="text-2xl font-bold">{pageName}</h1>
    <p className="text-neutral-500 mt-2">Coming soon</p>
  </div>
);

function App() {
  const { verifyToken, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      verifyToken().catch(() => {});
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Main Dashboard Routes */}
          <Route path="/dashboard" element={<AuthenticatedLayout title="Dashboard"><Dashboard /></AuthenticatedLayout>} />
          <Route path="/candidates" element={<AuthenticatedLayout title="Candidates"><Candidates /></AuthenticatedLayout>} />
          <Route path="/requirements" element={<AuthenticatedLayout title="Requirements"><Requirements /></AuthenticatedLayout>} />
          <Route path="/submissions" element={<AuthenticatedLayout title="Submissions"><Submissions /></AuthenticatedLayout>} />
          <Route path="/interviews" element={<AuthenticatedLayout title="Interviews"><Interviews /></AuthenticatedLayout>} />
          <Route path="/contracts" element={<AuthenticatedLayout title="Contracts"><Contracts /></AuthenticatedLayout>} />
          <Route path="/suppliers" element={<AuthenticatedLayout title="Suppliers"><Suppliers /></AuthenticatedLayout>} />
          <Route path="/referrals" element={<AuthenticatedLayout title="Referrals"><Referrals /></AuthenticatedLayout>} />
          <Route path="/copilot" element={<AuthenticatedLayout title="AI Copilot"><Copilot /></AuthenticatedLayout>} />
          <Route path="/reports" element={<AuthenticatedLayout title="Reports"><Reports /></AuthenticatedLayout>} />
          <Route path="/settings" element={<AuthenticatedLayout title="Settings"><Settings /></AuthenticatedLayout>} />
          <Route path="/admin" element={<AuthenticatedLayout title="Admin"><Admin /></AuthenticatedLayout>} />

          {/* Analytics Routes */}
          <Route path="/candidate-scorecard" element={<AuthenticatedLayout title="Candidate Scorecard"><CandidateScoreCard /></AuthenticatedLayout>} />
          <Route path="/job-fit-analysis" element={<AuthenticatedLayout title="Job Fit Analysis"><JobFitAnalysis /></AuthenticatedLayout>} />
          <Route path="/skill-gap-analyzer" element={<AuthenticatedLayout title="Skill Gap Analyzer"><SkillGapAnalyzer /></AuthenticatedLayout>} />
          <Route path="/recruiter-dashboard" element={<AuthenticatedLayout title="Recruiter Dashboard"><RecruiterDashboard /></AuthenticatedLayout>} />
          <Route path="/applicant-tracker" element={<AuthenticatedLayout title="Applicant Tracker"><ApplicantTracker /></AuthenticatedLayout>} />
          <Route path="/ai-predictions" element={<AuthenticatedLayout title="AI Predictions"><AIPredictionsPanel /></AuthenticatedLayout>} />

          {/* CRM & ATS Routes */}
          <Route path="/candidate-crm" element={<AuthenticatedLayout title="Candidate CRM"><CandidateCRM /></AuthenticatedLayout>} />
          <Route path="/job-orders" element={<AuthenticatedLayout title="Job Order Manager"><JobOrderManager /></AuthenticatedLayout>} />
          <Route path="/offers" element={<AuthenticatedLayout title="Offer Management"><OfferManagement /></AuthenticatedLayout>} />
          <Route path="/onboarding" element={<AuthenticatedLayout title="Onboarding Tracker"><OnboardingTracker /></AuthenticatedLayout>} />
          <Route path="/interview-insights" element={<AuthenticatedLayout title="Interview Insights"><InterviewInsights /></AuthenticatedLayout>} />
          <Route path="/advanced-search" element={<AuthenticatedLayout title="Advanced Search"><AdvancedSearch /></AuthenticatedLayout>} />
          <Route path="/automation" element={<AuthenticatedLayout title="Automation Center"><AutomationCenter /></AuthenticatedLayout>} />
          <Route path="/ats-workflow" element={<AuthenticatedLayout title="ATS Workflow"><ATSWorkflow /></AuthenticatedLayout>} />
          <Route path="/aggregate-reports" element={<AuthenticatedLayout title="Aggregate Reports"><AggregateReports /></AuthenticatedLayout>} />
          <Route path="/custom-reports" element={<AuthenticatedLayout title="Custom Report Builder"><CustomReportBuilder /></AuthenticatedLayout>} />
          <Route path="/testing-dashboard" element={<AuthenticatedLayout title="E2E Testing Dashboard"><TestingDashboard /></AuthenticatedLayout>} />
          <Route path="/resume-hub" element={<AuthenticatedLayout title="Resume Hub"><ResumeHub /></AuthenticatedLayout>} />
          <Route path="/pipeline-analytics" element={<AuthenticatedLayout title="Pipeline Analytics"><PipelineAnalytics /></AuthenticatedLayout>} />
          <Route path="/candidate-notifications" element={<AuthenticatedLayout title="Candidate Notifications"><CandidateNotifications /></AuthenticatedLayout>} />
          <Route path="/interview-feedback" element={<AuthenticatedLayout title="Interview Feedback Forms"><InterviewFeedbackForms /></AuthenticatedLayout>} />

          {/* Data Operations Routes */}
          <Route path="/bulk-import" element={<AuthenticatedLayout title="Bulk Import Center"><BulkImportCenter /></AuthenticatedLayout>} />
          <Route path="/bulk-analysis" element={<AuthenticatedLayout title="Bulk Analysis Dashboard"><BulkAnalysisDashboard /></AuthenticatedLayout>} />
          <Route path="/export-center" element={<AuthenticatedLayout title="Export Center"><ExportCenter /></AuthenticatedLayout>} />

          {/* MSP Billing, BGC/Onboarding, Asset Management */}
          <Route path="/msp-billing" element={<AuthenticatedLayout title="MSP Billing Center"><MSPBillingCenter /></AuthenticatedLayout>} />
          <Route path="/bgc-onboarding" element={<AuthenticatedLayout title="BGC & Onboarding"><BGCOnboarding /></AuthenticatedLayout>} />
          <Route path="/asset-management" element={<AuthenticatedLayout title="Asset Management"><AssetManagement /></AuthenticatedLayout>} />

          {/* Email Agent, Resume Match, Notification Hub */}
          <Route path="/email-agent" element={<AuthenticatedLayout title="Email Agent"><EmailAgentCenter /></AuthenticatedLayout>} />
          <Route path="/resume-match" element={<AuthenticatedLayout title="Resume Match Center"><ResumeMatchCenter /></AuthenticatedLayout>} />
          <Route path="/notification-hub" element={<AuthenticatedLayout title="Notification Hub"><NotificationCollabHub /></AuthenticatedLayout>} />

          {/* Admin Configuration */}
          <Route path="/company-admin" element={<AuthenticatedLayout title="Company Admin"><CompanyAdminConfig /></AuthenticatedLayout>} />
          <Route path="/app-admin" element={<AuthenticatedLayout title="App Admin"><AppAdminConfig /></AuthenticatedLayout>} />

          {/* Agreement Management */}
          <Route path="/agreements" element={<AuthenticatedLayout title="Agreement Center"><AgreementCenter /></AuthenticatedLayout>} />
          <Route path="/agreement-builder" element={<AuthenticatedLayout title="Agreement Builder"><AgreementBuilder /></AuthenticatedLayout>} />
          <Route path="/e-signatures" element={<AuthenticatedLayout title="E-Signature Portal"><ESignaturePortal /></AuthenticatedLayout>} />

          {/* Interview Feedback & Score Intelligence */}
          <Route path="/detailed-feedback" element={<AuthenticatedLayout title="Detailed Feedback"><DetailedFeedbackCollector /></AuthenticatedLayout>} />
          <Route path="/score-intelligence" element={<AuthenticatedLayout title="Score Intelligence"><CandidateScoreIntelligence /></AuthenticatedLayout>} />
          <Route path="/score-analytics" element={<AuthenticatedLayout title="Score Analytics"><ScoreAnalyticsDashboard /></AuthenticatedLayout>} />

          {/* Financial Reports */}
          <Route path="/financial-statements" element={<AuthenticatedLayout title="Financial Statements"><ProfitAndLoss /></AuthenticatedLayout>} />
          <Route path="/revenue-expense" element={<AuthenticatedLayout title="Revenue & Expenses"><RevenueExpenseBreakdown /></AuthenticatedLayout>} />
          <Route path="/receivables-payables" element={<AuthenticatedLayout title="Receivables & Payables"><ReceivablesPayables /></AuthenticatedLayout>} />
          <Route path="/associate-financials" element={<AuthenticatedLayout title="Associate Financials"><AssociateFinancials /></AuthenticatedLayout>} />
          <Route path="/revenue-analytics" element={<AuthenticatedLayout title="Revenue Analytics"><RevenueAnalytics /></AuthenticatedLayout>} />

          {/* MSP Portal Routes */}
          <Route path="/msp/dashboard" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="MSP Dashboard"><MSPDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/clients" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Clients"><ClientsList /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/suppliers" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Suppliers"><SuppliersList /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/submissions" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Submissions Pipeline"><SubmissionsPipeline /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/rate-cards" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Rate Cards"><RateCards /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/compliance" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Compliance"><ComplianceDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/sla" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="SLA Monitoring"><SLADashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/vms-timesheets" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="VMS Timesheets"><VMSTimesheets /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/placements" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Placements">{PlaceholderPage('Placements')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/analytics" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Analytics">{PlaceholderPage('Analytics')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/distributions" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Distributions">{PlaceholderPage('Distributions')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Analytics Routes */}
          <Route path="/msp/ai-predictions" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="AI Predictions"><AIPredictionsPanel /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/recruiter-dashboard" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Recruiter Dashboard"><RecruiterDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/applicant-tracker" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Applicant Tracker"><ApplicantTracker /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP CRM & ATS Routes */}
          <Route path="/msp/candidate-crm" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Candidate CRM"><CandidateCRM /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/job-orders" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Job Order Manager"><JobOrderManager /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/offers" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Offer Management"><OfferManagement /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/onboarding" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Onboarding Tracker"><OnboardingTracker /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/interview-insights" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Interview Insights"><InterviewInsights /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/advanced-search" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Advanced Search"><AdvancedSearch /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/automation" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Automation Center"><AutomationCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/ats-workflow" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="ATS Workflow"><ATSWorkflow /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/aggregate-reports" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Aggregate Reports"><AggregateReports /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/custom-reports" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Custom Report Builder"><CustomReportBuilder /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/testing-dashboard" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="E2E Testing Dashboard"><TestingDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/resume-hub" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Resume Hub"><ResumeHub /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/pipeline-analytics" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Pipeline Analytics"><PipelineAnalytics /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/candidate-notifications" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Candidate Notifications"><CandidateNotifications /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/interview-feedback" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Interview Feedback Forms"><InterviewFeedbackForms /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Email Agent, Resume Match, Notification Hub */}
          <Route path="/msp/email-agent" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Email Agent"><EmailAgentCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/resume-match" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Resume Match Center"><ResumeMatchCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/notification-hub" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Notification Hub"><NotificationCollabHub /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Billing, BGC & Asset Routes */}
          <Route path="/msp/billing" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="MSP Billing Center"><MSPBillingCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/bgc-onboarding" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="BGC & Onboarding"><BGCOnboarding /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/asset-management" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Asset Management"><AssetManagement /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Agreement Management */}
          <Route path="/msp/agreements" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Agreement Center"><AgreementCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/agreement-builder" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Agreement Builder"><AgreementBuilder /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/e-signatures" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="E-Signature Portal"><ESignaturePortal /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Interview Feedback & Score Intelligence */}
          <Route path="/msp/detailed-feedback" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Detailed Feedback"><DetailedFeedbackCollector /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/score-intelligence" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Score Intelligence"><CandidateScoreIntelligence /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/score-analytics" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Score Analytics"><ScoreAnalyticsDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Financial Reports */}
          <Route path="/msp/financial-statements" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Financial Statements"><ProfitAndLoss /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/revenue-expense" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Revenue & Expenses"><RevenueExpenseBreakdown /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/receivables-payables" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Receivables & Payables"><ReceivablesPayables /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/associate-financials" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Associate Financials"><AssociateFinancials /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/revenue-analytics" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Revenue Analytics"><RevenueAnalytics /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* MSP Data Operations Routes */}
          <Route path="/msp/bulk-import" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Bulk Import Center"><BulkImportCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/bulk-analysis" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Bulk Analysis Dashboard"><BulkAnalysisDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/msp/export-center" element={
            <OrgTypeGuard allowedTypes={['msp']}>
              <AuthenticatedLayout title="Export Center"><ExportCenter /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* Client Portal Routes */}
          <Route path="/client/dashboard" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Client Dashboard"><ClientDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/requirements" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Requirements">{PlaceholderPage('Requirements')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/requirements/new" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="New Requirement">{PlaceholderPage('New Requirement')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/submissions" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Submissions">{PlaceholderPage('Submissions')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/timesheets" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Timesheets"><ClientTimesheets /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/placements" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Placements">{PlaceholderPage('Placements')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/analytics" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Analytics">{PlaceholderPage('Analytics')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/client/interviews" element={
            <OrgTypeGuard allowedTypes={['client']}>
              <AuthenticatedLayout title="Interviews">{PlaceholderPage('Interviews')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* Supplier Portal Routes */}
          <Route path="/supplier/dashboard" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Supplier Dashboard"><SupplierDashboard /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/supplier/opportunities" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Opportunities">{PlaceholderPage('Opportunities')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/supplier/submissions" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Submissions">{PlaceholderPage('Submissions')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/supplier/timesheets" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Timesheets"><SupplierTimesheets /></AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/supplier/placements" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Placements">{PlaceholderPage('Placements')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/supplier/performance" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Performance">{PlaceholderPage('Performance')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />
          <Route path="/supplier/analytics" element={
            <OrgTypeGuard allowedTypes={['supplier']}>
              <AuthenticatedLayout title="Analytics">{PlaceholderPage('Analytics')()}</AuthenticatedLayout>
            </OrgTypeGuard>
          } />

          {/* Default Routes */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e293b',
            color: '#f8fafc',
            borderRadius: '0.75rem',
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;
