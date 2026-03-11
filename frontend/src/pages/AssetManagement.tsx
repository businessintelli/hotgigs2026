import React, { useState, useEffect } from 'react';

interface AssetCatalogItem {
  id: number; asset_name: string; asset_type: string; make: string | null; model: string | null;
  serial_number: string | null; asset_tag: string | null; status: string;
  provider: string; managed_by: string; location: string | null;
  building: string | null; assigned_to_candidate_name: string | null;
  purchase_cost: number | null; monthly_cost: number | null;
}
interface AllocationRequest {
  id: number; candidate_name: string; placement_id: number; asset_type: string;
  asset_description: string | null; quantity: number; status: string;
  provider: string; managed_by: string; managed_by_org_name: string | null;
  requested_by: string; requested_at: string; needed_by: string | null;
  approved_by: string | null; tracking_number: string | null;
  return_due_date: string | null; delivery_address: string | null;
}
interface AllocationRule {
  id: number; rule_name: string; client_org_name: string | null;
  job_category: string | null; location: string | null;
  asset_types: { type: string; provider: string; managed_by: string }[];
  default_provider: string; auto_request: boolean;
  lead_days_before_start: number; auto_return_on_end: boolean;
}

const statusColors: Record<string, string> = {
  available: 'bg-green-100 text-green-700', allocated: 'bg-blue-100 text-blue-700',
  in_use: 'bg-indigo-100 text-indigo-700', returned: 'bg-gray-100 text-gray-600',
  damaged: 'bg-red-100 text-red-700', lost: 'bg-red-200 text-red-800',
  retired: 'bg-gray-200 text-gray-500', in_transit: 'bg-yellow-100 text-yellow-700',
  pending_return: 'bg-orange-100 text-orange-700',
  requested: 'bg-yellow-100 text-yellow-700', approved: 'bg-blue-100 text-blue-700',
  ordered: 'bg-purple-100 text-purple-700', delivered: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700', cancelled: 'bg-gray-100 text-gray-500',
  return_initiated: 'bg-orange-100 text-orange-700', return_completed: 'bg-green-100 text-green-700',
};

const providerBadge: Record<string, string> = {
  msp: 'bg-purple-100 text-purple-700', supplier: 'bg-emerald-100 text-emerald-700',
  client: 'bg-blue-100 text-blue-700', contractor_owned: 'bg-gray-100 text-gray-700',
};

const managedByLabel: Record<string, string> = {
  system_admin_msp: 'MSP Sys Admin', system_admin_supplier: 'Supplier Sys Admin',
  system_admin_client: 'Client Sys Admin', client_it: 'Client IT',
  client_facilities: 'Client Facilities', msp_ops: 'MSP Ops',
  supplier_ops: 'Supplier Ops',
};

const assetTypeIcons: Record<string, string> = {
  laptop: '💻', desktop: '🖥️', monitor: '🖥️', phone: '📱', headset: '🎧',
  badge: '🪪', access_card: '🔑', parking_pass: '🅿️', software_license: '📀',
  vpn_access: '🔐', email_account: '📧', building_key: '🔑',
  security_token: '🛡️', furniture: '🪑', other: '📦',
};

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);

// ── Mock Data ──────────────────────────────────────────────
const mockCatalog: AssetCatalogItem[] = [
  { id: 1, asset_name: 'MacBook Pro 16" M3 Max', asset_type: 'laptop', make: 'Apple', model: 'MBP 16 2025', serial_number: 'C02X19Z8MD6T', asset_tag: 'LAP-001', status: 'in_use', provider: 'client', managed_by: 'client_it', location: 'Austin HQ', building: 'Building A', assigned_to_candidate_name: 'Rajesh Kumar', purchase_cost: 3499, monthly_cost: null },
  { id: 2, asset_name: 'Dell Latitude 5540', asset_type: 'laptop', make: 'Dell', model: 'Latitude 5540', serial_number: 'DL5540-8847', asset_tag: 'LAP-002', status: 'available', provider: 'msp', managed_by: 'system_admin_msp', location: 'MSP Warehouse', building: null, assigned_to_candidate_name: null, purchase_cost: 1299, monthly_cost: null },
  { id: 3, asset_name: 'Dell UltraSharp 27" 4K', asset_type: 'monitor', make: 'Dell', model: 'U2723QE', serial_number: null, asset_tag: 'MON-012', status: 'in_use', provider: 'client', managed_by: 'client_facilities', location: 'Austin HQ', building: 'Building A', assigned_to_candidate_name: 'Rajesh Kumar', purchase_cost: 619, monthly_cost: null },
  { id: 4, asset_name: 'Cisco VPN Access', asset_type: 'vpn_access', make: null, model: null, serial_number: null, asset_tag: null, status: 'allocated', provider: 'client', managed_by: 'client_it', location: null, building: null, assigned_to_candidate_name: 'Priya Sharma', purchase_cost: null, monthly_cost: 15 },
  { id: 5, asset_name: 'HQ Access Badge', asset_type: 'badge', make: 'HID', model: 'iCLASS SE', serial_number: 'HID-992847', asset_tag: 'BDG-045', status: 'in_use', provider: 'client', managed_by: 'client_facilities', location: 'Austin HQ', building: 'Building A', assigned_to_candidate_name: 'Amit Patel', purchase_cost: 25, monthly_cost: null },
  { id: 6, asset_name: 'Parking Pass - Lot B', asset_type: 'parking_pass', make: null, model: null, serial_number: null, asset_tag: 'PKG-221', status: 'allocated', provider: 'client', managed_by: 'client_facilities', location: 'Lot B', building: null, assigned_to_candidate_name: 'Amit Patel', purchase_cost: null, monthly_cost: 75 },
  { id: 7, asset_name: 'Jabra Evolve2 85', asset_type: 'headset', make: 'Jabra', model: 'Evolve2 85', serial_number: null, asset_tag: 'HST-033', status: 'available', provider: 'supplier', managed_by: 'supplier_ops', location: 'Supplier Office', building: null, assigned_to_candidate_name: null, purchase_cost: 449, monthly_cost: null },
  { id: 8, asset_name: 'GitHub Enterprise License', asset_type: 'software_license', make: null, model: null, serial_number: null, asset_tag: 'SW-GH-017', status: 'in_use', provider: 'client', managed_by: 'client_it', location: null, building: null, assigned_to_candidate_name: 'Rajesh Kumar', purchase_cost: null, monthly_cost: 21 },
  { id: 9, asset_name: 'YubiKey 5 NFC', asset_type: 'security_token', make: 'Yubico', model: '5 NFC', serial_number: 'YK5-449821', asset_tag: 'SEC-008', status: 'pending_return', provider: 'msp', managed_by: 'msp_ops', location: null, building: null, assigned_to_candidate_name: 'Former Contractor', purchase_cost: 55, monthly_cost: null },
  { id: 10, asset_name: 'Standing Desk - Electric', asset_type: 'furniture', make: 'Uplift', model: 'V2 Commercial', serial_number: null, asset_tag: 'FRN-102', status: 'in_use', provider: 'client', managed_by: 'client_facilities', location: 'Austin HQ', building: 'Building A', assigned_to_candidate_name: 'Priya Sharma', purchase_cost: 799, monthly_cost: null },
];

const mockRequests: AllocationRequest[] = [
  { id: 1, candidate_name: 'Ananya Desai', placement_id: 1045, asset_type: 'laptop', asset_description: 'MacBook Pro 14" for iOS development', quantity: 1, status: 'approved', provider: 'client', managed_by: 'client_it', managed_by_org_name: 'TechCorp Inc.', requested_by: 'Sarah (MSP Coordinator)', requested_at: '2026-03-08T10:30:00Z', needed_by: '2026-03-15', approved_by: 'Client IT Admin', tracking_number: null, return_due_date: '2026-09-15', delivery_address: 'TechCorp Austin HQ, Building C' },
  { id: 2, candidate_name: 'Ananya Desai', placement_id: 1045, asset_type: 'badge', asset_description: 'Building access badge', quantity: 1, status: 'ordered', provider: 'client', managed_by: 'client_facilities', managed_by_org_name: 'TechCorp Inc.', requested_by: 'Sarah (MSP Coordinator)', requested_at: '2026-03-08T10:30:00Z', needed_by: '2026-03-15', approved_by: 'Facilities Admin', tracking_number: null, return_due_date: '2026-09-15', delivery_address: null },
  { id: 3, candidate_name: 'Vikram Singh', placement_id: 1046, asset_type: 'laptop', asset_description: 'Dell Latitude with 32GB RAM', quantity: 1, status: 'requested', provider: 'supplier', managed_by: 'supplier_ops', managed_by_org_name: 'StaffPro Solutions', requested_by: 'StaffPro Coordinator', requested_at: '2026-03-10T14:00:00Z', needed_by: '2026-03-20', approved_by: null, tracking_number: null, return_due_date: '2026-12-20', delivery_address: 'Remote - Ship to candidate' },
  { id: 4, candidate_name: 'Vikram Singh', placement_id: 1046, asset_type: 'vpn_access', asset_description: 'Cisco AnyConnect VPN', quantity: 1, status: 'allocated', provider: 'client', managed_by: 'client_it', managed_by_org_name: 'TechCorp Inc.', requested_by: 'Auto-Rule: IT Contractors', requested_at: '2026-03-10T14:01:00Z', needed_by: '2026-03-20', approved_by: 'Auto-Approved', tracking_number: null, return_due_date: '2026-12-20', delivery_address: null },
  { id: 5, candidate_name: 'Meera Joshi', placement_id: 1040, asset_type: 'laptop', asset_description: 'Return laptop - placement ended', quantity: 1, status: 'return_initiated', provider: 'msp', managed_by: 'msp_ops', managed_by_org_name: 'HotGigs MSP', requested_by: 'System (Placement End)', requested_at: '2026-03-05T09:00:00Z', needed_by: '2026-03-12', approved_by: null, tracking_number: 'UPS-1Z999AA10123456784', return_due_date: '2026-03-12', delivery_address: 'MSP Warehouse, Dallas TX' },
  { id: 6, candidate_name: 'Kiran Reddy', placement_id: 1038, asset_type: 'security_token', asset_description: 'YubiKey 5 NFC', quantity: 1, status: 'return_completed', provider: 'msp', managed_by: 'msp_ops', managed_by_org_name: 'HotGigs MSP', requested_by: 'System (Placement End)', requested_at: '2026-02-28T09:00:00Z', needed_by: '2026-03-05', approved_by: null, tracking_number: 'UPS-1Z999AA10198765432', return_due_date: '2026-03-05', delivery_address: 'MSP Warehouse, Dallas TX' },
];

const mockRules: AllocationRule[] = [
  { id: 1, rule_name: 'IT Contractors - TechCorp', client_org_name: 'TechCorp Inc.', job_category: 'Software Engineering', location: null, asset_types: [{ type: 'laptop', provider: 'client', managed_by: 'client_it' }, { type: 'badge', provider: 'client', managed_by: 'client_facilities' }, { type: 'vpn_access', provider: 'client', managed_by: 'client_it' }, { type: 'email_account', provider: 'client', managed_by: 'client_it' }], default_provider: 'client', auto_request: true, lead_days_before_start: 5, auto_return_on_end: true },
  { id: 2, rule_name: 'General Staff - All Clients', client_org_name: null, job_category: null, location: null, asset_types: [{ type: 'badge', provider: 'client', managed_by: 'client_facilities' }, { type: 'parking_pass', provider: 'client', managed_by: 'client_facilities' }], default_provider: 'client', auto_request: true, lead_days_before_start: 3, auto_return_on_end: true },
  { id: 3, rule_name: 'Remote Contractors', client_org_name: null, job_category: null, location: 'Remote', asset_types: [{ type: 'laptop', provider: 'supplier', managed_by: 'supplier_ops' }, { type: 'headset', provider: 'supplier', managed_by: 'supplier_ops' }, { type: 'vpn_access', provider: 'client', managed_by: 'client_it' }, { type: 'security_token', provider: 'msp', managed_by: 'msp_ops' }], default_provider: 'supplier', auto_request: true, lead_days_before_start: 7, auto_return_on_end: true },
];

const mockDashboard = {
  total_assets: 156, allocated_assets: 89, available_assets: 42,
  pending_returns: 8, assets_in_transit: 5, lost_or_damaged: 3,
  pending_requests: 12, auto_allocated_this_month: 34,
  by_provider: { client: 95, msp: 38, supplier: 18, contractor_owned: 5 },
  by_type: { laptop: 42, monitor: 28, badge: 35, vpn_access: 22, software_license: 15, other: 14 },
};

// ── Component ──────────────────────────────────────────────
export function AssetManagement() {
  const [tab, setTab] = useState<'catalog' | 'requests' | 'rules' | 'dashboard'>('dashboard');
  const [catalog, setCatalog] = useState<AssetCatalogItem[]>([]);
  const [requests, setRequests] = useState<AllocationRequest[]>([]);
  const [rules, setRules] = useState<AllocationRule[]>([]);
  const [dashboard, setDashboard] = useState(mockDashboard);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    const base = '/api/v1/asset-management';
    Promise.all([
      fetch(`${base}/catalog`).then(r => r.ok ? r.json() : mockCatalog),
      fetch(`${base}/requests`).then(r => r.ok ? r.json() : mockRequests),
      fetch(`${base}/rules`).then(r => r.ok ? r.json() : mockRules),
      fetch(`${base}/dashboard`).then(r => r.ok ? r.json() : mockDashboard),
    ]).then(([c, rq, rl, d]) => {
      setCatalog(Array.isArray(c) ? c : mockCatalog);
      setRequests(Array.isArray(rq) ? rq : mockRequests);
      setRules(Array.isArray(rl) ? rl : mockRules);
      setDashboard(d?.total_assets ? d : mockDashboard);
    }).catch(() => {
      setCatalog(mockCatalog); setRequests(mockRequests);
      setRules(mockRules); setDashboard(mockDashboard);
    }).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { key: 'dashboard', label: 'Dashboard', count: null },
    { key: 'catalog', label: 'Asset Catalog', count: catalog.length },
    { key: 'requests', label: 'Allocation Requests', count: requests.filter(r => ['requested','approved','ordered'].includes(r.status)).length },
    { key: 'rules', label: 'Auto-Allocation Rules', count: rules.length },
  ] as const;

  const filteredCatalog = catalog.filter(a =>
    (typeFilter === 'all' || a.asset_type === typeFilter) &&
    (statusFilter === 'all' || a.status === statusFilter)
  );

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
    </div>
  );

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Asset Management</h1>
          <p className="text-sm text-gray-500 mt-1">Track hardware, software, badges, and access across MSP, Supplier & Client orgs</p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">
          + New Allocation Request
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-6">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}>
              {t.label}
              {t.count !== null && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">{t.count}</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* ─── Dashboard Tab ─── */}
      {tab === 'dashboard' && (
        <div className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { label: 'Total Assets', value: dashboard.total_assets, color: 'bg-indigo-50 text-indigo-700' },
              { label: 'Allocated', value: dashboard.allocated_assets, color: 'bg-blue-50 text-blue-700' },
              { label: 'Available', value: dashboard.available_assets, color: 'bg-green-50 text-green-700' },
              { label: 'Pending Returns', value: dashboard.pending_returns, color: 'bg-orange-50 text-orange-700' },
              { label: 'In Transit', value: dashboard.assets_in_transit, color: 'bg-yellow-50 text-yellow-700' },
              { label: 'Lost/Damaged', value: dashboard.lost_or_damaged, color: 'bg-red-50 text-red-700' },
            ].map(kpi => (
              <div key={kpi.label} className={`rounded-xl p-4 ${kpi.color}`}>
                <p className="text-xs font-medium opacity-70">{kpi.label}</p>
                <p className="text-2xl font-bold mt-1">{kpi.value}</p>
              </div>
            ))}
          </div>

          {/* Provider Breakdown & Type Breakdown */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Assets by Provider</h3>
              <div className="space-y-3">
                {Object.entries(dashboard.by_provider).map(([key, count]) => {
                  const pct = Math.round((count / dashboard.total_assets) * 100);
                  const colors: Record<string, string> = { client: 'bg-blue-500', msp: 'bg-purple-500', supplier: 'bg-emerald-500', contractor_owned: 'bg-gray-400' };
                  return (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="capitalize font-medium text-gray-700">{key.replace('_', ' ')}</span>
                        <span className="text-gray-500">{count} ({pct}%)</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${colors[key] ?? 'bg-gray-400'}`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Assets by Type</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(dashboard.by_type).map(([type, count]) => (
                  <div key={type} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50">
                    <span className="text-lg">{assetTypeIcons[type] ?? '📦'}</span>
                    <div>
                      <p className="text-sm font-medium text-gray-700 capitalize">{type.replace('_', ' ')}</p>
                      <p className="text-xs text-gray-500">{count} units</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Pending Allocation Requests</h3>
            <div className="space-y-3">
              {requests.filter(r => ['requested', 'approved', 'ordered'].includes(r.status)).map(r => (
                <div key={r.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{assetTypeIcons[r.asset_type] ?? '📦'}</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{r.candidate_name} — {r.asset_description || r.asset_type}</p>
                      <p className="text-xs text-gray-500">Needed by {r.needed_by} · Managed by {managedByLabel[r.managed_by] ?? r.managed_by}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${providerBadge[r.provider] ?? 'bg-gray-100'}`}>
                      {r.provider.toUpperCase()}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[r.status] ?? 'bg-gray-100 text-gray-600'}`}>
                      {r.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ─── Catalog Tab ─── */}
      {tab === 'catalog' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Types</option>
              {[...new Set(catalog.map(a => a.asset_type))].map(t => (
                <option key={t} value={t}>{assetTypeIcons[t] ?? ''} {t.replace('_', ' ')}</option>
              ))}
            </select>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Statuses</option>
              {[...new Set(catalog.map(a => a.status))].map(s => (
                <option key={s} value={s}>{s.replace('_', ' ')}</option>
              ))}
            </select>
          </div>

          {/* Catalog Table */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Asset</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Tag</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Provider</th>
                  <th className="px-4 py-3">Managed By</th>
                  <th className="px-4 py-3">Assigned To</th>
                  <th className="px-4 py-3">Location</th>
                  <th className="px-4 py-3 text-right">Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredCatalog.map(a => (
                  <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span>{assetTypeIcons[a.asset_type] ?? '📦'}</span>
                        <div>
                          <p className="font-medium text-gray-900">{a.asset_name}</p>
                          {a.make && <p className="text-xs text-gray-400">{a.make} {a.model}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-600">{a.asset_type.replace('_', ' ')}</td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">{a.asset_tag ?? '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[a.status] ?? 'bg-gray-100'}`}>
                        {a.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${providerBadge[a.provider] ?? 'bg-gray-100'}`}>
                        {a.provider.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">{managedByLabel[a.managed_by] ?? a.managed_by}</td>
                    <td className="px-4 py-3">
                      {a.assigned_to_candidate_name
                        ? <span className="text-indigo-600 font-medium">{a.assigned_to_candidate_name}</span>
                        : <span className="text-gray-400">Unassigned</span>}
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{a.location ?? '—'}</td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {a.purchase_cost ? fmt(a.purchase_cost) : a.monthly_cost ? `${fmt(a.monthly_cost)}/mo` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ─── Allocation Requests Tab ─── */}
      {tab === 'requests' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Candidate</th>
                  <th className="px-4 py-3">Asset</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Provider</th>
                  <th className="px-4 py-3">Managed By</th>
                  <th className="px-4 py-3">Requested By</th>
                  <th className="px-4 py-3">Needed By</th>
                  <th className="px-4 py-3">Return Due</th>
                  <th className="px-4 py-3">Tracking</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {requests.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900">{r.candidate_name}</p>
                      <p className="text-xs text-gray-400">Placement #{r.placement_id}</p>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span>{assetTypeIcons[r.asset_type] ?? '📦'}</span>
                        <div>
                          <p className="text-gray-700 capitalize">{r.asset_type.replace('_', ' ')}</p>
                          {r.asset_description && <p className="text-xs text-gray-400">{r.asset_description}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[r.status] ?? 'bg-gray-100'}`}>
                        {r.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${providerBadge[r.provider] ?? 'bg-gray-100'}`}>
                        {r.provider.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-xs text-gray-600">{managedByLabel[r.managed_by] ?? r.managed_by}</p>
                      {r.managed_by_org_name && <p className="text-xs text-gray-400">{r.managed_by_org_name}</p>}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">{r.requested_by}</td>
                    <td className="px-4 py-3 text-xs text-gray-600">{r.needed_by ?? '—'}</td>
                    <td className="px-4 py-3 text-xs text-gray-600">{r.return_due_date ?? '—'}</td>
                    <td className="px-4 py-3 text-xs font-mono text-gray-500">
                      {r.tracking_number ? r.tracking_number.substring(0, 16) + '…' : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Responsibility Legend */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Responsibility Matrix</h3>
            <div className="grid md:grid-cols-3 gap-4 text-xs">
              <div className="p-3 rounded-lg bg-purple-50 border border-purple-100">
                <p className="font-semibold text-purple-700 mb-2">MSP Responsibilities</p>
                <ul className="space-y-1 text-purple-600">
                  <li>• Coordinate allocation requests</li>
                  <li>• Manage MSP-owned assets (tokens, equipment)</li>
                  <li>• Track returns for placement endings</li>
                  <li>• Auto-allocation rule configuration</li>
                </ul>
              </div>
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                <p className="font-semibold text-emerald-700 mb-2">Supplier Responsibilities</p>
                <ul className="space-y-1 text-emerald-600">
                  <li>• Provide laptops/headsets for remote workers</li>
                  <li>• Manage supplier-owned equipment pool</li>
                  <li>• Coordinate shipping to candidates</li>
                  <li>• Handle return logistics</li>
                </ul>
              </div>
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-100">
                <p className="font-semibold text-blue-700 mb-2">Client Responsibilities</p>
                <ul className="space-y-1 text-blue-600">
                  <li>• Provide badges, access cards, building keys</li>
                  <li>• Manage VPN, email, software licenses</li>
                  <li>• Facilities: parking, furniture, desks</li>
                  <li>• IT provisioning and deprovisioning</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── Auto-Allocation Rules Tab ─── */}
      {tab === 'rules' && (
        <div className="space-y-4">
          {rules.map(rule => (
            <div key={rule.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-base font-semibold text-gray-900">{rule.rule_name}</h3>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {rule.client_org_name && (
                      <span className="px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700">Client: {rule.client_org_name}</span>
                    )}
                    {rule.job_category && (
                      <span className="px-2 py-0.5 rounded text-xs bg-indigo-50 text-indigo-700">Category: {rule.job_category}</span>
                    )}
                    {rule.location && (
                      <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">Location: {rule.location}</span>
                    )}
                    {!rule.client_org_name && !rule.job_category && !rule.location && (
                      <span className="px-2 py-0.5 rounded text-xs bg-yellow-50 text-yellow-700">Applies to All</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {rule.auto_request && (
                    <span className="px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700 font-medium">Auto-Request</span>
                  )}
                  {rule.auto_return_on_end && (
                    <span className="px-2 py-0.5 rounded-full text-xs bg-orange-100 text-orange-700 font-medium">Auto-Return</span>
                  )}
                  <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">{rule.lead_days_before_start}d lead time</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {rule.asset_types.map((at, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50 border border-gray-100">
                    <span className="text-lg">{assetTypeIcons[at.type] ?? '📦'}</span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-700 capitalize truncate">{at.type.replace('_', ' ')}</p>
                      <div className="flex gap-1 mt-0.5">
                        <span className={`px-1.5 py-0 rounded text-[10px] font-medium ${providerBadge[at.provider] ?? 'bg-gray-100'}`}>
                          {at.provider.toUpperCase()}
                        </span>
                        <span className="px-1.5 py-0 rounded text-[10px] bg-gray-100 text-gray-500">
                          {managedByLabel[at.managed_by] ?? at.managed_by}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* How It Works */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100 p-5">
            <h3 className="text-sm font-semibold text-indigo-800 mb-3">How Auto-Allocation Works</h3>
            <div className="grid md:grid-cols-4 gap-4 text-xs text-indigo-700">
              <div className="text-center">
                <div className="w-8 h-8 bg-indigo-200 rounded-full flex items-center justify-center mx-auto mb-2 text-indigo-800 font-bold">1</div>
                <p className="font-medium">New Placement Created</p>
                <p className="text-indigo-500 mt-1">System checks matching rules by client, job category, and location</p>
              </div>
              <div className="text-center">
                <div className="w-8 h-8 bg-indigo-200 rounded-full flex items-center justify-center mx-auto mb-2 text-indigo-800 font-bold">2</div>
                <p className="font-medium">Requests Generated</p>
                <p className="text-indigo-500 mt-1">Asset allocation requests created automatically {'{lead_days}'} before start</p>
              </div>
              <div className="text-center">
                <div className="w-8 h-8 bg-indigo-200 rounded-full flex items-center justify-center mx-auto mb-2 text-indigo-800 font-bold">3</div>
                <p className="font-medium">Routed to Managers</p>
                <p className="text-indigo-500 mt-1">Each request routed to the responsible system admin (MSP, Supplier, or Client)</p>
              </div>
              <div className="text-center">
                <div className="w-8 h-8 bg-indigo-200 rounded-full flex items-center justify-center mx-auto mb-2 text-indigo-800 font-bold">4</div>
                <p className="font-medium">Auto-Return on End</p>
                <p className="text-indigo-500 mt-1">When placement ends, return requests are automatically created</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
