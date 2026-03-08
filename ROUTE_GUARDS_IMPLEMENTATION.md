# Role-Based Route Guards Implementation

## Overview

This document describes the implementation of role-based route guards for the HotGigs HR platform frontend. These guards protect routes to ensure users can only access pages appropriate for their organization type and role.

## Files Created

### 1. OrgTypeGuard Component
**Path:** `/frontend/src/components/guards/OrgTypeGuard.tsx`

A React component that wraps routes and enforces organization type-based access control.

**Key Features:**
- Checks if the user's current organization type matches the allowed types
- Handles loading states while auth state is being verified
- Redirects unauthenticated users to `/login`
- Redirects users with no selected org to `/dashboard`
- Redirects users to their appropriate dashboard if they try to access a route for a different org type:
  - MSP users → `/msp/dashboard`
  - Client users → `/client/dashboard`
  - Supplier users → `/supplier/dashboard`
  - Default fallback → `/dashboard`

**Usage Example:**
```tsx
<OrgTypeGuard allowedTypes={['msp']}>
  <AuthenticatedLayout title="MSP Dashboard">
    <MSPDashboard />
  </AuthenticatedLayout>
</OrgTypeGuard>
```

**Props:**
- `allowedTypes: string[]` - Array of allowed organization types (case-insensitive, e.g., ['msp'], ['client'], ['supplier'])
- `children: React.ReactNode` - Component content to render if access is allowed

### 2. RoleGuard Component
**Path:** `/frontend/src/components/guards/RoleGuard.tsx`

A React component that wraps routes and enforces role-based access control.

**Key Features:**
- Checks if the user has one of the required roles globally or within their organization
- Handles loading states during auth verification
- Redirects unauthenticated users to `/login`
- Redirects unauthorized users to a configurable fallback path (default: `/dashboard`)
- Case-insensitive role matching
- Combines both global user roles and organization-specific roles

**Usage Example:**
```tsx
<RoleGuard allowedRoles={['msp_admin', 'admin']}>
  <AdminPanel />
</RoleGuard>
```

**Props:**
- `allowedRoles: string[]` - Array of allowed roles (case-insensitive, e.g., ['msp_admin', 'admin'])
- `children: React.ReactNode` - Component content to render if access is allowed
- `fallbackPath?: string` - Path to redirect to if access denied (default: '/dashboard')

## Updated Files

### App.tsx
**Path:** `/frontend/src/App.tsx`

Added imports for both guard components at the top:
```tsx
import { OrgTypeGuard } from '@/components/guards/OrgTypeGuard';
import { RoleGuard } from '@/components/guards/RoleGuard';
```

All organization-specific routes are now wrapped with `OrgTypeGuard`:

#### MSP Routes (11 total)
All routes under `/msp/*` are wrapped with `<OrgTypeGuard allowedTypes={['msp']}>`
- `/msp/dashboard`
- `/msp/clients`
- `/msp/suppliers`
- `/msp/submissions`
- `/msp/rate-cards`
- `/msp/compliance`
- `/msp/sla`
- `/msp/vms-timesheets`
- `/msp/placements`
- `/msp/analytics`
- `/msp/distributions`

#### Client Routes (8 total)
All routes under `/client/*` are wrapped with `<OrgTypeGuard allowedTypes={['client']}>`
- `/client/dashboard`
- `/client/requirements`
- `/client/requirements/new`
- `/client/submissions`
- `/client/timesheets`
- `/client/placements`
- `/client/analytics`
- `/client/interviews`

#### Supplier Routes (7 total)
All routes under `/supplier/*` are wrapped with `<OrgTypeGuard allowedTypes={['supplier']}>`
- `/supplier/dashboard`
- `/supplier/opportunities`
- `/supplier/submissions`
- `/supplier/timesheets`
- `/supplier/placements`
- `/supplier/performance`
- `/supplier/analytics`

## How It Works

### Organization Type Guard Flow

1. **Check Authentication State**
   - If user is loading, show loading spinner
   - If user is not authenticated, redirect to `/login`

2. **Check Organization Selection**
   - If no organization is selected, redirect to `/dashboard`

3. **Check Organization Type**
   - Normalize both the current org type and allowed types to lowercase
   - If current org type matches one of the allowed types, render children
   - If not, redirect to the user's appropriate org-type dashboard

### Role Guard Flow

1. **Check Authentication State**
   - If user is loading, show loading spinner
   - If user is not authenticated, redirect to `/login`

2. **Collect User Roles**
   - Gather global user role and organization-specific role
   - Filter out empty/undefined values
   - Normalize all roles to lowercase

3. **Check Role Permissions**
   - If user has one of the required roles, render children
   - If not, redirect to fallback path (default: `/dashboard`)

## Integration Points

### Store Integration

**Organization Store** (`/store/organizationStore.ts`):
- `currentOrg` - The user's currently selected organization with `org_type` property
- `roleInOrg` - The user's role within the current organization
- `setCurrentOrg()` - Updates the current organization
- `setRoleInOrg()` - Updates the organization role

**Auth Store** (`/store/authStore.ts`):
- `isAuthenticated` - Boolean indicating if user is logged in
- `isLoading` - Boolean indicating if auth state is being verified
- `user` - Current user object with role property

### Hook Integration

**useAuth Hook** (used in RoleGuard):
- Provides access to the authenticated user

## Usage Patterns

### Protecting a Single Org Type Route

```tsx
<Route path="/msp/dashboard" element={
  <OrgTypeGuard allowedTypes={['msp']}>
    <AuthenticatedLayout title="MSP Dashboard">
      <MSPDashboard />
    </AuthenticatedLayout>
  </OrgTypeGuard>
} />
```

### Protecting Multiple Org Types (Future Use)

```tsx
<Route path="/shared-feature" element={
  <OrgTypeGuard allowedTypes={['msp', 'client']}>
    <AuthenticatedLayout title="Shared Feature">
      <SharedFeature />
    </AuthenticatedLayout>
  </OrgTypeGuard>
} />
```

### Protecting by Role

```tsx
<Route path="/admin" element={
  <RoleGuard allowedRoles={['admin', 'msp_admin']}>
    <AuthenticatedLayout title="Admin">
      <Admin />
    </AuthenticatedLayout>
  </RoleGuard>
} />
```

### Combining Org Type and Role Guards

```tsx
<Route path="/msp/sensitive-feature" element={
  <OrgTypeGuard allowedTypes={['msp']}>
    <RoleGuard allowedRoles={['msp_admin']}>
      <AuthenticatedLayout title="Sensitive Feature">
        <SensitiveFeature />
      </AuthenticatedLayout>
    </RoleGuard>
  </OrgTypeGuard>
} />
```

## Security Considerations

1. **Client-Side Protection**: These guards provide UI-level protection and improved user experience. Backend API endpoints must also validate user permissions.

2. **Organization Context**: Always ensure the backend API validates that the requested resource belongs to the user's current organization.

3. **Role Validation**: Backend should independently verify user roles and permissions, not relying solely on frontend claims.

4. **Token Verification**: The auth store handles token verification via `verifyToken()` which is called on app initialization.

## Testing Recommendations

1. **Test Unauthorized Access**: Try accessing MSP routes as a Client user - should redirect to client dashboard
2. **Test No Org Selection**: Logout and login - should redirect to main dashboard if no org is selected
3. **Test Role Guards**: Try accessing admin routes without admin role - should redirect to fallback path
4. **Test Combined Guards**: Verify that combining multiple guards works correctly

## Future Enhancements

1. **Toast Notifications**: Add toast notifications when users are redirected due to insufficient permissions
2. **Specific Error Pages**: Create organization-specific "Access Denied" pages
3. **Conditional Features**: Hide UI elements based on user role in addition to route-level protection
4. **Audit Logging**: Log unauthorized access attempts for security monitoring
5. **Feature Flags**: Integrate with feature flag system for gradual rollouts of new features
