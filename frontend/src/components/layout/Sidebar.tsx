import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import {
  HomeIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CheckCircleIcon,
  CalendarIcon,
  DocumentDuplicateIcon,
  BuildingLibraryIcon,
  BuildingOffice2Icon,
  FaceSmileIcon,
  SparklesIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon,
  ShieldExclamationIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  TruckIcon,
  ClipboardDocumentListIcon,
  ArrowPathIcon,
  ChartBarIcon,
  BriefcaseIcon,
  StarIcon,
  InboxIcon,
  PaperAirplaneIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  CloudArrowUpIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';
import { useUIStore } from '@/store/uiStore';
import { useAuth } from '@/hooks/useAuth';
import { useOrganizationStore } from '@/store/organizationStore';

interface NavItem {
  icon: React.ForwardRefExoticComponent<any>;
  label: string;
  href: string;
  roleRequired?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const mspNavigation: NavGroup[] = [
  {
    label: 'OVERVIEW',
    items: [{ icon: HomeIcon, label: 'MSP Dashboard', href: '/msp/dashboard' }],
  },
  {
    label: 'PROGRAM MANAGEMENT',
    items: [
      { icon: BuildingOffice2Icon, label: 'Clients', href: '/msp/clients' },
      { icon: TruckIcon, label: 'Suppliers', href: '/msp/suppliers' },
    ],
  },
  {
    label: 'VMS PIPELINE',
    items: [
      { icon: DocumentTextIcon, label: 'Requirements', href: '/requirements' },
      { icon: ArrowPathIcon, label: 'Distributions', href: '/msp/distributions' },
      { icon: ClipboardDocumentListIcon, label: 'Submissions Pipeline', href: '/msp/submissions' },
      { icon: CalendarIcon, label: 'Interviews', href: '/interviews' },
      { icon: BriefcaseIcon, label: 'Placements', href: '/msp/placements' },
      { icon: ClipboardDocumentListIcon, label: 'VMS Timesheets', href: '/msp/vms-timesheets' },
    ],
  },
  {
    label: 'VMS OPERATIONS',
    items: [
      { icon: ChartBarIcon, label: 'Rate Cards', href: '/msp/rate-cards' },
      { icon: ShieldExclamationIcon, label: 'Compliance', href: '/msp/compliance' },
      { icon: ExclamationTriangleIcon, label: 'SLA Monitoring', href: '/msp/sla' },
    ],
  },
  {
    label: 'AI TOOLS',
    items: [
      { icon: SparklesIcon, label: 'AI Copilot', href: '/copilot' },
    ],
  },
  {
    label: 'CRM & ATS',
    items: [
      { icon: ArrowPathIcon, label: 'ATS Workflow', href: '/msp/ats-workflow' },
      { icon: UserGroupIcon, label: 'Candidate CRM', href: '/msp/candidate-crm' },
      { icon: BriefcaseIcon, label: 'Job Orders', href: '/msp/job-orders' },
      { icon: DocumentTextIcon, label: 'Offers', href: '/msp/offers' },
      { icon: CheckCircleIcon, label: 'Onboarding', href: '/msp/onboarding' },
      { icon: StarIcon, label: 'Interview Insights', href: '/msp/interview-insights' },
    ],
  },
  {
    label: 'AI ANALYTICS',
    items: [
      { icon: ChartBarIcon, label: 'Candidate Scorecard', href: '/msp/candidate-scorecard' },
      { icon: ChartBarIcon, label: 'Job Fit Analysis', href: '/msp/job-fit-analysis' },
      { icon: ChartBarIcon, label: 'Skill Gap Analyzer', href: '/msp/skill-gap-analyzer' },
      { icon: ChartBarIcon, label: 'Recruiter Dashboard', href: '/msp/recruiter-dashboard' },
      { icon: ChartBarIcon, label: 'Applicant Tracker', href: '/msp/applicant-tracker' },
      { icon: ChartBarIcon, label: 'AI Predictions', href: '/msp/ai-predictions' },
    ],
  },
  {
    label: 'DATA OPERATIONS',
    items: [
      { icon: CloudArrowUpIcon, label: 'Bulk Import', href: '/msp/bulk-import' },
      { icon: SparklesIcon, label: 'Bulk Analysis', href: '/msp/bulk-analysis' },
      { icon: ArrowDownTrayIcon, label: 'Export Center', href: '/msp/export-center' },
    ],
  },
  {
    label: 'TOOLS',
    items: [
      { icon: MagnifyingGlassIcon, label: 'Advanced Search', href: '/msp/advanced-search' },
      { icon: SparklesIcon, label: 'Automation Center', href: '/msp/automation' },
    ],
  },
  {
    label: 'ANALYTICS & ADMIN',
    items: [
      { icon: ChartBarIcon, label: 'Analytics', href: '/msp/analytics' },
      { icon: DocumentChartBarIcon, label: 'Reports', href: '/reports' },
      { icon: ChartBarIcon, label: 'Aggregate Reports', href: '/msp/aggregate-reports' },
      { icon: DocumentChartBarIcon, label: 'Custom Reports', href: '/msp/custom-reports', roleRequired: 'admin' },
      { icon: Cog6ToothIcon, label: 'Settings', href: '/settings' },
      { icon: ShieldExclamationIcon, label: 'Admin', href: '/admin', roleRequired: 'admin' },
    ],
  },
];

const clientNavigation: NavGroup[] = [
  {
    label: 'OVERVIEW',
    items: [{ icon: HomeIcon, label: 'Dashboard', href: '/client/dashboard' }],
  },
  {
    label: 'REQUIREMENTS',
    items: [
      { icon: DocumentTextIcon, label: 'My Requirements', href: '/client/requirements' },
      { icon: PaperAirplaneIcon, label: 'Create Requirement', href: '/client/requirements/new' },
    ],
  },
  {
    label: 'CANDIDATES',
    items: [
      { icon: InboxIcon, label: 'Submissions Inbox', href: '/client/submissions' },
      { icon: CalendarIcon, label: 'Interviews', href: '/client/interviews' },
      { icon: BriefcaseIcon, label: 'Placements', href: '/client/placements' },
    ],
  },
  {
    label: 'VMS',
    items: [
      { icon: ClipboardDocumentListIcon, label: 'Timesheets', href: '/client/timesheets' },
    ],
  },
  {
    label: 'INSIGHTS',
    items: [
      { icon: ChartBarIcon, label: 'Analytics', href: '/client/analytics' },
      { icon: Cog6ToothIcon, label: 'Settings', href: '/settings' },
    ],
  },
];

const supplierNavigation: NavGroup[] = [
  {
    label: 'OVERVIEW',
    items: [{ icon: HomeIcon, label: 'Dashboard', href: '/supplier/dashboard' }],
  },
  {
    label: 'OPPORTUNITIES',
    items: [
      { icon: DocumentTextIcon, label: 'Open Requirements', href: '/supplier/opportunities' },
      { icon: UserGroupIcon, label: 'Candidates', href: '/candidates' },
    ],
  },
  {
    label: 'SUBMISSIONS',
    items: [
      { icon: PaperAirplaneIcon, label: 'My Submissions', href: '/supplier/submissions' },
      { icon: BriefcaseIcon, label: 'Placements', href: '/supplier/placements' },
      { icon: ClipboardDocumentListIcon, label: 'Timesheets', href: '/supplier/timesheets' },
    ],
  },
  {
    label: 'PERFORMANCE',
    items: [
      { icon: StarIcon, label: 'My Scorecard', href: '/supplier/performance' },
      { icon: ChartBarIcon, label: 'Analytics', href: '/supplier/analytics' },
      { icon: Cog6ToothIcon, label: 'Settings', href: '/settings' },
    ],
  },
];

const defaultNavigation: NavGroup[] = [
  {
    label: 'OVERVIEW',
    items: [{ icon: HomeIcon, label: 'Dashboard', href: '/dashboard' }],
  },
  {
    label: 'PIPELINE',
    items: [
      { icon: DocumentTextIcon, label: 'Requirements', href: '/requirements' },
      { icon: UserGroupIcon, label: 'Candidates', href: '/candidates' },
      { icon: CheckCircleIcon, label: 'Submissions', href: '/submissions' },
      { icon: CalendarIcon, label: 'Interviews', href: '/interviews' },
    ],
  },
  {
    label: 'MANAGEMENT',
    items: [
      { icon: DocumentDuplicateIcon, label: 'Contracts', href: '/contracts' },
      { icon: BuildingLibraryIcon, label: 'Suppliers', href: '/suppliers' },
      { icon: FaceSmileIcon, label: 'Referrals', href: '/referrals' },
    ],
  },
  {
    label: 'AI TOOLS',
    items: [
      { icon: SparklesIcon, label: 'Copilot', href: '/copilot' },
    ],
  },
  {
    label: 'CRM & ATS',
    items: [
      { icon: ArrowPathIcon, label: 'ATS Workflow', href: '/ats-workflow' },
      { icon: UserGroupIcon, label: 'Candidate CRM', href: '/candidate-crm' },
      { icon: BriefcaseIcon, label: 'Job Orders', href: '/job-orders' },
      { icon: DocumentTextIcon, label: 'Offers', href: '/offers' },
      { icon: CheckCircleIcon, label: 'Onboarding', href: '/onboarding' },
      { icon: StarIcon, label: 'Interview Insights', href: '/interview-insights' },
    ],
  },
  {
    label: 'AI ANALYTICS',
    items: [
      { icon: ChartBarIcon, label: 'Candidate Scorecard', href: '/candidate-scorecard' },
      { icon: ChartBarIcon, label: 'Job Fit Analysis', href: '/job-fit-analysis' },
      { icon: ChartBarIcon, label: 'Skill Gap Analyzer', href: '/skill-gap-analyzer' },
      { icon: ChartBarIcon, label: 'Recruiter Dashboard', href: '/recruiter-dashboard' },
      { icon: ChartBarIcon, label: 'Applicant Tracker', href: '/applicant-tracker' },
      { icon: ChartBarIcon, label: 'AI Predictions', href: '/ai-predictions' },
    ],
  },
  {
    label: 'DATA OPERATIONS',
    items: [
      { icon: CloudArrowUpIcon, label: 'Bulk Import', href: '/bulk-import' },
      { icon: SparklesIcon, label: 'Bulk Analysis', href: '/bulk-analysis' },
      { icon: ArrowDownTrayIcon, label: 'Export Center', href: '/export-center' },
    ],
  },
  {
    label: 'TOOLS',
    items: [
      { icon: MagnifyingGlassIcon, label: 'Advanced Search', href: '/advanced-search' },
      { icon: SparklesIcon, label: 'Automation Center', href: '/automation' },
    ],
  },
  {
    label: 'REPORTS & ADMIN',
    items: [
      { icon: DocumentChartBarIcon, label: 'Reports', href: '/reports' },
      { icon: ChartBarIcon, label: 'Aggregate Reports', href: '/aggregate-reports' },
      { icon: DocumentChartBarIcon, label: 'Custom Reports', href: '/custom-reports', roleRequired: 'admin' },
      { icon: Cog6ToothIcon, label: 'Settings', href: '/settings' },
      { icon: ShieldExclamationIcon, label: 'Admin', href: '/admin', roleRequired: 'admin' },
    ],
  },
];

function getNavigationForOrg(orgType: string | null): NavGroup[] {
  switch (orgType?.toUpperCase()) {
    case 'MSP':
      return mspNavigation;
    case 'CLIENT':
      return clientNavigation;
    case 'SUPPLIER':
      return supplierNavigation;
    default:
      return defaultNavigation;
  }
}

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const location = useLocation();
  const { user } = useAuth();
  const { sidebarCollapsed, setSidebarCollapsed } = useUIStore();
  const { currentOrg, roleInOrg } = useOrganizationStore();

  const navigationGroups = getNavigationForOrg(currentOrg?.org_type ?? null);

  const isActive = (href: string) => location.pathname === href || location.pathname.startsWith(href + '/');

  const canAccessItem = (item: NavItem) => {
    if (!item.roleRequired) return true;
    return user?.role === item.roleRequired || user?.role === 'admin' || roleInOrg?.includes('ADMIN');
  };

  const orgTypeColors: Record<string, string> = {
    MSP: 'bg-purple-500',
    CLIENT: 'bg-blue-500',
    SUPPLIER: 'bg-emerald-500',
  };

  const orgColor = orgTypeColors[currentOrg?.org_type?.toUpperCase() ?? ''] ?? 'bg-primary-500';

  return (
    <>
      {/* Mobile backdrop */}
      {!isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed left-0 top-0 h-full bg-neutral-900 dark:bg-neutral-950 text-white',
          'transition-all duration-250 z-40',
          'flex flex-col',
          sidebarCollapsed ? 'w-20' : 'w-sidebar',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          'md:translate-x-0 md:static'
        )}
      >
        {/* Logo Section */}
        <div className={clsx(
          'border-b border-neutral-800 p-4 flex items-center justify-between',
          sidebarCollapsed && 'justify-center'
        )}>
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm', orgColor)}>
                {currentOrg?.org_type === 'MSP' ? 'M' : currentOrg?.org_type === 'CLIENT' ? 'C' : currentOrg?.org_type === 'SUPPLIER' ? 'S' : 'HR'}
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-sm leading-tight">
                  {currentOrg?.name ?? 'HotGigs'}
                </span>
                {currentOrg && (
                  <span className="text-[10px] text-neutral-400 uppercase tracking-wider">
                    {currentOrg.org_type}
                  </span>
                )}
              </div>
            </div>
          )}
          {sidebarCollapsed && (
            <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm', orgColor)}>
              {currentOrg?.org_type === 'MSP' ? 'M' : currentOrg?.org_type === 'CLIENT' ? 'C' : currentOrg?.org_type === 'SUPPLIER' ? 'S' : 'H'}
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="hidden lg:block text-neutral-400 hover:text-white transition-colors"
            type="button"
          >
            {sidebarCollapsed ? (
              <ChevronRightIcon className="w-5 h-5" />
            ) : (
              <ChevronLeftIcon className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* User Section */}
        <div className={clsx(
          'border-b border-neutral-800 p-4',
          sidebarCollapsed && 'flex justify-center'
        )}>
          {!sidebarCollapsed && user && (
            <div>
              <p className="text-sm font-semibold">{user.first_name} {user.last_name}</p>
              <p className="text-xs text-neutral-400">
                {roleInOrg ?? user.role}
              </p>
            </div>
          )}
          {sidebarCollapsed && user && (
            <div className={clsx('w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm', orgColor)}>
              {user.first_name.charAt(0)}
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-6">
          {navigationGroups.map((group) => (
            <div key={group.label}>
              {!sidebarCollapsed && (
                <p className="px-4 py-2 text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                  {group.label}
                </p>
              )}
              <div className={clsx(
                'space-y-1',
                sidebarCollapsed && 'flex flex-col items-center'
              )}>
                {group.items
                  .filter(canAccessItem)
                  .map((item) => (
                    <Link
                      key={item.href}
                      to={item.href}
                      className={clsx(
                        'flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-250',
                        'text-neutral-300 hover:text-white hover:bg-neutral-800',
                        isActive(item.href) &&
                          'bg-primary-500 text-white hover:bg-primary-600'
                      )}
                      title={sidebarCollapsed ? item.label : undefined}
                      onClick={onClose}
                    >
                      <item.icon className="w-5 h-5 flex-shrink-0" />
                      {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
                    </Link>
                  ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-neutral-800 p-4">
          <p className="text-xs text-neutral-500 text-center">
            {!sidebarCollapsed && 'HotGigs v2.0'}
          </p>
        </div>
      </aside>
    </>
  );
};
