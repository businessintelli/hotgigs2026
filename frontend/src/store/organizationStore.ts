import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Organization {
  id: number;
  name: string;
  slug: string;
  org_type: 'msp' | 'client' | 'supplier';
  onboarding_status: string;
  logo_url?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  industry?: string;
  tier?: string;
  is_active: boolean;
}

interface OrganizationState {
  currentOrg: Organization | null;
  organizations: Organization[];
  roleInOrg: string;
  isLoading: boolean;

  setCurrentOrg: (org: Organization | null) => void;
  setOrganizations: (orgs: Organization[]) => void;
  setRoleInOrg: (role: string) => void;
  switchOrganization: (org: Organization, role: string, token: string) => void;
  clearOrgState: () => void;
}

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set) => ({
      currentOrg: null,
      organizations: [],
      roleInOrg: '',
      isLoading: false,

      setCurrentOrg: (org) => set({ currentOrg: org }),
      setOrganizations: (organizations) => set({ organizations }),
      setRoleInOrg: (role) => set({ roleInOrg: role }),

      switchOrganization: (org, role, token) => {
        set({ currentOrg: org, roleInOrg: role });
        // Token is handled by authStore
      },

      clearOrgState: () =>
        set({
          currentOrg: null,
          organizations: [],
          roleInOrg: '',
        }),
    }),
    {
      name: 'org-store',
      partialize: (state) => ({
        currentOrg: state.currentOrg,
        organizations: state.organizations,
        roleInOrg: state.roleInOrg,
      }),
    }
  )
);
