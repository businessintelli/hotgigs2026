# Route Guards

This directory contains React components that enforce access control at the route level based on organization type and user role.

## Components

### OrgTypeGuard

Protects routes by organization type. Ensures users can only access pages intended for their organization type.

**Import:**
```tsx
import { OrgTypeGuard } from '@/components/guards/OrgTypeGuard';
```

**Basic Usage:**
```tsx
<OrgTypeGuard allowedTypes={['msp']}>
  <MSPDashboard />
</OrgTypeGuard>
```

**Props:**
- `allowedTypes: string[]` - Array of allowed org types: 'msp', 'client', 'supplier'
- `children: React.ReactNode` - Content to render if access is allowed

**Behavior:**
- Redirects to `/login` if user is not authenticated
- Redirects to `/dashboard` if no organization is selected
- Redirects to appropriate org dashboard if user's org type is not in allowedTypes
- Shows loading spinner while auth state is being verified

### RoleGuard

Protects routes by user role. Ensures users have the required permissions to access a page.

**Import:**
```tsx
import { RoleGuard } from '@/components/guards/RoleGuard';
```

**Basic Usage:**
```tsx
<RoleGuard allowedRoles={['admin', 'msp_admin']}>
  <AdminPanel />
</RoleGuard>
```

**Props:**
- `allowedRoles: string[]` - Array of allowed roles (case-insensitive)
- `children: React.ReactNode` - Content to render if access is allowed
- `fallbackPath?: string` - Path to redirect to if access denied (default: '/dashboard')

**Behavior:**
- Redirects to `/login` if user is not authenticated
- Checks both global user role and organization-specific role
- Redirects to fallbackPath if user doesn't have required role
- Shows loading spinner while auth state is being verified

## Common Patterns

### Protecting by Organization Type Only

```tsx
<Route path="/msp/dashboard" element={
  <OrgTypeGuard allowedTypes={['msp']}>
    <AuthenticatedLayout title="MSP Dashboard">
      <MSPDashboard />
    </AuthenticatedLayout>
  </OrgTypeGuard>
} />
```

### Protecting by Role Only

```tsx
<Route path="/admin" element={
  <RoleGuard allowedRoles={['admin']}>
    <AuthenticatedLayout title="Admin">
      <Admin />
    </AuthenticatedLayout>
  </RoleGuard>
} />
```

### Protecting by Both Organization Type and Role

```tsx
<Route path="/msp/admin" element={
  <OrgTypeGuard allowedTypes={['msp']}>
    <RoleGuard allowedRoles={['admin', 'msp_admin']}>
      <AuthenticatedLayout title="MSP Admin">
        <MSPAdmin />
      </AuthenticatedLayout>
    </RoleGuard>
  </OrgTypeGuard>
} />
```

### Multiple Organization Types

```tsx
<Route path="/shared-feature" element={
  <OrgTypeGuard allowedTypes={['msp', 'client']}>
    <AuthenticatedLayout title="Shared Feature">
      <SharedFeature />
    </AuthenticatedLayout>
  </OrgTypeGuard>
} />
```

### Multiple Roles

```tsx
<Route path="/recruiter-dashboard" element={
  <RoleGuard allowedRoles={['msp_recruiter', 'client_recruiter', 'admin']}>
    <AuthenticatedLayout title="Recruiter Dashboard">
      <RecruiterDashboard />
    </AuthenticatedLayout>
  </RoleGuard>
} />
```

## How Guards Work

### OrgTypeGuard Flow

```
┌─ Guard checks authentication
├─ Not authenticated? → Redirect to /login
├─ No org selected? → Redirect to /dashboard
├─ Check org type
├─ Org type matches allowedTypes? → Render children
└─ Org type doesn't match? → Redirect to org's dashboard
```

### RoleGuard Flow

```
┌─ Guard checks authentication
├─ Not authenticated? → Redirect to /login
├─ Collect user roles (global + org-specific)
├─ Check roles
├─ User has required role? → Render children
└─ User doesn't have role? → Redirect to fallbackPath
```

## Important Notes

- Guards are case-insensitive for organization types and roles
- Unauthenticated users are always redirected to `/login` first
- Guards provide UI-level protection; backend APIs must also validate permissions
- Guards show a loading spinner while auth state is being verified
- Multiple guards can be nested for combined protection

## Testing

When testing guards:

1. **Test unauthorized org type access**: Try accessing `/msp/dashboard` as a client org user
2. **Test unauthorized role access**: Try accessing admin routes without admin role
3. **Test loading state**: Guards should display spinner during auth verification
4. **Test authenticated state**: Verify children render when access is allowed
5. **Test redirects**: Verify correct redirect paths for different scenarios
