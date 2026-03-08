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

// Data Operations Pages
import { BulkImportCenter } from '@/pages/BulkImportCenter';
import { BulkAnalysisDashboard } from '@/pages/BulkAnalysisDashboard';
import { ExportCenter } from '@/pages/ExportCenter';

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

          {/* Data Operations Routes */}
          <Route path="/bulk-import" element={<AuthenticatedLayout title="Bulk Import Center"><BulkImportCenter /></AuthenticatedLayout>} />
          <Route path="/bulk-analysis" element={<AuthenticatedLayout title="Bulk Analysis Dashboard"><BulkAnalysisDashboard /></AuthenticatedLayout>} />
          <Route path="/export-center" element={<AuthenticatedLayout title="Export Center"><ExportCenter /></AuthenticatedLayout>} />

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
