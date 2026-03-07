/**
 * Tenant-aware API client.
 * Wraps fetch with automatic Authorization and X-Organization-Id headers.
 */

import { useAuthStore } from '@/store/authStore';
import { useOrganizationStore } from '@/store/organizationStore';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number>;
}

async function tenantFetch<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const token = useAuthStore.getState().token;
  const orgId = useOrganizationStore.getState().currentOrg?.id;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (orgId) {
    headers['X-Organization-Id'] = String(orgId);
  }

  // Build URL with params
  let url = `${API_BASE}${endpoint}`;
  if (options.params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(options.params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    }
    const qs = searchParams.toString();
    if (qs) url += `?${qs}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired — clear auth
    useAuthStore.getState().logout();
    throw new Error('Session expired. Please log in again.');
  }

  if (response.status === 403) {
    throw new Error('Access denied. You do not have permission for this action.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Convenience methods
export const tenantApi = {
  get: <T>(endpoint: string, params?: Record<string, string | number>) =>
    tenantFetch<T>(endpoint, { method: 'GET', params }),

  post: <T>(endpoint: string, body?: any) =>
    tenantFetch<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: any) =>
    tenantFetch<T>(endpoint, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    tenantFetch<T>(endpoint, { method: 'DELETE' }),
};

export default tenantApi;
