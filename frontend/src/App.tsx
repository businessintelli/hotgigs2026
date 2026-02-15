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

// Layout
import { AppLayout } from '@/components/layout/AppLayout';

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
          <Route
            path="/dashboard"
            element={
              <AuthenticatedLayout title="Dashboard">
                <Dashboard />
              </AuthenticatedLayout>
            }
          />
          <Route
            path="/candidates"
            element={
              <AuthenticatedLayout title="Candidates">
                <Candidates />
              </AuthenticatedLayout>
            }
          />
          <Route
            path="/requirements"
            element={
              <AuthenticatedLayout title="Requirements">
                <Requirements />
              </AuthenticatedLayout>
            }
          />
          <Route
            path="/submissions"
            element={
              <AuthenticatedLayout title="Submissions">
                <Submissions />
              </AuthenticatedLayout>
            }
          />
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
