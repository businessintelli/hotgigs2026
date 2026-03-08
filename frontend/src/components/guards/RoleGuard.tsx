import React from 'react';
import { Navigate } from 'react-router-dom';
import { useOrganizationStore } from '@/store/organizationStore';
import { useAuth } from '@/hooks/useAuth';
import { useAuthStore } from '@/store/authStore';

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
  fallbackPath?: string;
}

/**
 * RoleGuard Component
 *
 * Protects routes by checking if the user has one of the required roles
 * within their current organization or globally.
 *
 * @param allowedRoles - Array of allowed roles (e.g., ['msp_admin', 'msp_recruiter', 'admin'])
 * @param children - The content to render if user has required role
 * @param fallbackPath - Path to redirect to if access is denied (default: '/dashboard')
 */
export const RoleGuard: React.FC<RoleGuardProps> = ({
  allowedRoles,
  children,
  fallbackPath = '/dashboard',
}) => {
  const { user } = useAuth();
  const { roleInOrg } = useOrganizationStore();
  const { isLoading } = useAuthStore();

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // No user
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has required role
  const userRoles = [user.role, roleInOrg].filter(Boolean).map((r) => r.toLowerCase());
  const hasRequiredRole = allowedRoles.some((role) =>
    userRoles.includes(role.toLowerCase())
  );

  if (!hasRequiredRole) {
    return <Navigate to={fallbackPath} replace />;
  }

  // User has required role, render children
  return <>{children}</>;
};
