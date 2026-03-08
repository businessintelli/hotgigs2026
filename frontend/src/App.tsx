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

          {/* MSP Portal Routes */}
          <Route path="/msp/dashboard" element={<AuthenticatedLayout title="MSP Dashboard"><MSPDashboard /></AuthenticatedLayout>} />
          <Route path="/msp/clients" element={<AuthenticatedLayout title="Clients"><ClientsList /></AuthenticatedLayout>} />
          <Route path="/msp/suppliers" element={<AuthenticatedLayout title="Suppliers"><SuppliersList /></AuthenticatedLayout>} />
          <Route path="/msp/submissions" element={<AuthenticatedLayout title="Submissions Pipeline"><SubmissionsPipeline /></AuthenticatedLayout>} />
          <Route path="/msp/rate-cards" element={<AuthenticatedLayout title="Rate Cards"><RateCards /></AuthenticatedLayout>} />
          <Route path="/msp/compliance" element={<AuthenticatedLayout title="Compliance"><ComplianceDashboard /></AuthenticatedLayout>} />
          <Route path="/msp/sla" element={<AuthenticatedLayout title="SLA Monitoring"><SLADashboard /></AuthenticatedLayout>} />
          <Route path="/msp/vms-timesheets" element={<AuthenticatedLayout title="VMS Timesheets"><VMSTimesheets /></AuthenticatedLayout>} />
          <Route path="/msp/placements" element={<AuthenticatedLayout title="Placements">{PlaceholderPage('Placements')()}</AuthenticatedLayout>} />
          <Route path="/msp/analytics" element={<AuthenticatedLayout title="Analytics">{PlaceholderPage('Analytics')()}</AuthenticatedLayout>} />
          <Route path="/msp/distributions" element={<AuthenticatedLayout title="Distributions">{PlaceholderPage('Distributions')()}</AuthenticatedLayout>} />

          {/* Client Portal Routes */}
          <Route path="/client/dashboard" element={<AuthenticatedLayout title="Client Dashboard"><ClientDashboard /></AuthenticatedLayout>} />
          <Route path="/client/requirements" element={<AuthenticatedLayout title="Requirements">{PlaceholderPage('Requirements')()}</AuthenticatedLayout>} />
          <Route path="/client/requirements/new" element={<AuthenticatedLayout title="New Requirement">{PlaceholderPage('New Requirement')()}</AuthenticatedLayout>} />
          <Route path="/client/submissions" element={<AuthenticatedLayout title="Submissions">{PlaceholderPage('Submissions')()}</AuthenticatedLayout>} />
          <Route path="/client/timesheets" element={<AuthenticatedLayout title="Timesheets"><ClientTimesheets /></AuthenticatedLayout>} />
          <Route path="/client/placements" element={<AuthenticatedLayout title="Placements">{PlaceholderPage('Placements')()}</AuthenticatedLayout>} />
          <Route path="/client/analytics" element={<AuthenticatedLayout title="Analytics">{PlaceholderPage('Analytics')()}</AuthenticatedLayout>} />
          <Route path="/client/interviews" element={<AuthenticatedLayout title="Interviews">{PlaceholderPage('Interviews')()}</AuthenticatedLayout>} />

          {/* Supplier Portal Routes */}
          <Route path="/supplier/dashboard" element={<AuthenticatedLayout title="Supplier Dashboard"><SupplierDashboard /></AuthenticatedLayout>} />
          <Route path="/supplier/opportunities" element={<AuthenticatedLayout title="Opportunities">{PlaceholderPage('Opportunities')()}</AuthenticatedLayout>} />
          <Route path="/supplier/submissions" element={<AuthenticatedLayout title="Submissions">{PlaceholderPage('Submissions')()}</AuthenticatedLayout>} />
          <Route path="/supplier/timesheets" element={<AuthenticatedLayout title="Timesheets"><SupplierTimesheets /></AuthenticatedLayout>} />
          <Route path="/supplier/placements" element={<AuthenticatedLayout title="Placements">{PlaceholderPage('Placements')()}</AuthenticatedLayout>} />
          <Route path="/supplier/performance" element={<AuthenticatedLayout title="Performance">{PlaceholderPage('Performance')()}</AuthenticatedLayout>} />
          <Route path="/supplier/analytics" element={<AuthenticatedLayout title="Analytics">{PlaceholderPage('Analytics')()}</AuthenticatedLayout>} />

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
