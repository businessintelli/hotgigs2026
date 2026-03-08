import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useOrganizationStore } from '@/store/organizationStore';
import { useAuthStore } from '@/store/authStore';

interface OrgTypeGuardProps {
  allowedTypes: string[];
  children: React.ReactNode;
}

/**
 * OrgTypeGuard Component
 *
 * Protects routes by checking if the user's current organization type
 * matches one of the allowed types. If not, redirects to the appropriate dashboard.
 *
 * @param allowedTypes - Array of allowed org types (e.g., ['msp'], ['client'], ['supplier'])
 * @param children - The content to render if org type is allowed
 */
export const OrgTypeGuard: React.FC<OrgTypeGuardProps> = ({ allowedTypes, children }) => {
  const { currentOrg, setCurrentOrg } = useOrganizationStore();
  const { isAuthenticated, isLoading } = useAuthStore();

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // No organization selected
  if (!currentOrg) {
    return <Navigate to="/dashboard" replace />;
  }

  // Check if current org type is allowed
  const orgTypeNormalized = currentOrg.org_type.toLowerCase();
  const isAllowed = allowedTypes.some(
    (type) => type.toLowerCase() === orgTypeNormalized
  );

  if (!isAllowed) {
    // Redirect to appropriate dashboard based on actual org type
    const redirects: Record<string, string> = {
      msp: '/msp/dashboard',
      client: '/client/dashboard',
      supplier: '/supplier/dashboard',
    };

    const redirectPath = redirects[orgTypeNormalized] || '/dashboard';
    return <Navigate to={redirectPath} replace />;
  }

  // Organization type is allowed, render children
  return <>{children}</>;
};
