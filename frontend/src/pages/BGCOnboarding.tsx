import React, { useState, useEffect } from 'react';

interface BGCRequest {
  id: number; candidate_name: string; package_name: string; status: string;
  initiated_by_role: string; coordinated_by_role: string; executed_by_role: string;
  due_date: string | null; vendor_name: string; overall_result: string | null;
  supplier_name: string; client_name: string; risk_level: string | null;
  check_items: { check_type: string; status: string; result: string | null }[];
}
interface OnboardingTask {
  id: number; candidate_name: string; task_name: string; task_type: string;
  status: string; priority: number; owner_role: string; owner_role_display: string;
  assigned_to_org: string; due_date: string; follow_up_count: number;
  blocks_start_date: boolean; is_overdue: boolean;
}
interface OnboardingDoc {
  id: number; candidate_name: string; document_name: string; category: string;
  is_received: boolean; is_verified: boolean; required_by: string;
  collected_by_role: string | null;
}

const statusColors: Record<string, string> = {
  passed: 'bg-green-100 text-green-700', completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700', blocked: 'bg-red-100 text-red-700',
  in_progress: 'bg-blue-100 text-blue-700', initiated: 'bg-blue-100 text-blue-700',
  pending_review: 'bg-yellow-100 text-yellow-700', overdue: 'bg-red-100 text-red-700',
  not_started: 'bg-gray-100 text-gray-600', not_initiated: 'bg-gray-100 text-gray-600',
  conditional: 'bg-orange-100 text-orange-700', skipped: 'bg-gray-100 text-gray-500',
};

const roleColors: Record<string, string> = {
  msp_coordinator: 'bg-blue-50 text-blue-700', supplier_coordinator: 'bg-green-50 text-green-700',
  client_hiring_manager: 'bg-purple-50 text-purple-700', client_it: 'bg-indigo-50 text-indigo-700',
  client_hr: 'bg-pink-50 text-pink-700', candidate: 'bg-yellow-50 text-yellow-700',
  system_admin_msp: 'bg-blue-50 text-blue-700', system_admin_supplier: 'bg-green-50 text-green-700',
  system_admin_client: 'bg-purple-50 text-purple-700', client_facilities: 'bg-teal-50 text-teal-700',
};

const priorityLabels: Record<number, { text: string; color: string }> = {
  1: { text: 'Critical', color: 'text-red-600' }, 2: { text: 'High', color: 'text-orange-600' },
  3: { text: 'Medium', color: 'text-yellow-600' }, 4: { text: 'Low', color: 'text-gray-500' },
};

export function BGCOnboarding() {
  const [tab, setTab] = useState<'bgc' | 'tasks' | 'documents' | 'dashboard'>('bgc');
  const [bgcRequests, setBgcRequests] = useState<BGCRequest[]>([]);
  const [tasks, setTasks] = useState<OnboardingTask[]>([]);
  const [docs, setDocs] = useState<OnboardingDoc[]>([]);
  const [bgcKpis, setBgcKpis] = useState({ total_requests: 0, pass_rate: 0, avg_completion_days: 0, pending_review: 0, overdue: 0 });
  const [taskKpis, setTaskKpis] = useState({ total_tasks: 0, overdue_tasks: 0, blocking_tasks: 0, document_collection_rate: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = '/api/v1/bgc-onboarding';
    Promise.all([
      fetch(`${base}/bgc/requests`).then(r => r.json()),
      fetch(`${base}/onboarding/tasks`).then(r => r.json()),
      fetch(`${base}/onboarding/documents`).then(r => r.json()),
      fetch(`${base}/bgc/dashboard`).then(r => r.json()),
      fetch(`${base}/onboarding/dashboard`).then(r => r.json()),
    ]).then(([b, t, d, bd, td]) => {
      setBgcRequests(b.requests || []);
      setTasks(t.tasks || []);
      setDocs(d.documents || []);
      setBgcKpis(bd);
      setTaskKpis(td);
    }).catch(() => {
      // Inline mock data
      setBgcRequests([
        { id: 1, candidate_name: 'Alice Johnson', package_name: 'Comprehensive Screening', status: 'in_progress', initiated_by_role: 'msp_coordinator', coordinated_by_role: 'msp_coordinator', executed_by_role: 'supplier_coordinator', due_date: '2026-03-20', vendor_name: 'Sterling Check', overall_result: null, supplier_name: 'TechStaff Pro', client_name: 'Client Corp 1', risk_level: null, check_items: [{ check_type: 'criminal', status: 'passed', result: 'clear' }, { check_type: 'employment', status: 'in_progress', result: null }, { check_type: 'drug_screen', status: 'not_initiated', result: null }] },
        { id: 2, candidate_name: 'Bob Martinez', package_name: 'Standard Background Check', status: 'passed', initiated_by_role: 'msp_coordinator', coordinated_by_role: 'msp_coordinator', executed_by_role: 'supplier_coordinator', due_date: '2026-03-10', vendor_name: 'HireRight', overall_result: 'pass', supplier_name: 'GlobalForce HR', client_name: 'Client Corp 2', risk_level: 'low', check_items: [{ check_type: 'criminal', status: 'passed', result: 'clear' }, { check_type: 'employment', status: 'passed', result: 'clear' }] },
        { id: 3, candidate_name: 'Carol Chen', package_name: 'Quick Drug Screen', status: 'pending_review', initiated_by_role: 'msp_coordinator', coordinated_by_role: 'msp_coordinator', executed_by_role: 'supplier_coordinator', due_date: '2026-03-15', vendor_name: 'Quest Diagnostics', overall_result: null, supplier_name: 'PrimeRecruit Inc', client_name: 'Client Corp 1', risk_level: null, check_items: [{ check_type: 'drug_screen', status: 'pending_review', result: 'review' }] },
      ]);
      setTasks([
        { id: 1, candidate_name: 'Alice Johnson', task_name: 'Collect W-4 Form', task_type: 'document_collection', status: 'completed', priority: 2, owner_role: 'supplier_coordinator', owner_role_display: 'Supplier Coordinator', assigned_to_org: 'TechStaff Pro', due_date: '2026-03-12', follow_up_count: 0, blocks_start_date: false, is_overdue: false },
        { id: 2, candidate_name: 'Alice Johnson', task_name: 'Setup VPN Access', task_type: 'system_access', status: 'in_progress', priority: 1, owner_role: 'client_it', owner_role_display: 'Client IT', assigned_to_org: 'Client Corp 1', due_date: '2026-03-15', follow_up_count: 1, blocks_start_date: true, is_overdue: false },
        { id: 3, candidate_name: 'Bob Martinez', task_name: 'Issue Building Badge', task_type: 'badge_issuance', status: 'not_started', priority: 2, owner_role: 'system_admin_client', owner_role_display: 'System Admin Client', assigned_to_org: 'Client Corp 2', due_date: '2026-03-18', follow_up_count: 0, blocks_start_date: true, is_overdue: false },
        { id: 4, candidate_name: 'Carol Chen', task_name: 'Complete NDA Signing', task_type: 'nda_signing', status: 'overdue', priority: 1, owner_role: 'candidate', owner_role_display: 'Candidate', assigned_to_org: 'N/A', due_date: '2026-03-05', follow_up_count: 3, blocks_start_date: true, is_overdue: true },
        { id: 5, candidate_name: 'Alice Johnson', task_name: 'Complete Safety Training', task_type: 'training', status: 'not_started', priority: 3, owner_role: 'msp_coordinator', owner_role_display: 'MSP Coordinator', assigned_to_org: 'HotGigs MSP', due_date: '2026-03-20', follow_up_count: 0, blocks_start_date: false, is_overdue: false },
      ]);
      setDocs([
        { id: 1, candidate_name: 'Alice Johnson', document_name: 'W-4 Tax Form', category: 'tax_forms', is_received: true, is_verified: true, required_by: '2026-03-12', collected_by_role: 'supplier_coordinator' },
        { id: 2, candidate_name: 'Alice Johnson', document_name: 'I-9 Employment Eligibility', category: 'work_authorization', is_received: true, is_verified: false, required_by: '2026-03-15', collected_by_role: 'supplier_coordinator' },
        { id: 3, candidate_name: 'Bob Martinez', document_name: 'Passport Copy', category: 'identification', is_received: false, is_verified: false, required_by: '2026-03-18', collected_by_role: null },
        { id: 4, candidate_name: 'Carol Chen', document_name: 'NDA Agreement', category: 'nda', is_received: false, is_verified: false, required_by: '2026-03-10', collected_by_role: null },
      ]);
      setBgcKpis({ total_requests: 15, pass_rate: 82.5, avg_completion_days: 6.2, pending_review: 3, overdue: 2 });
      setTaskKpis({ total_tasks: 25, overdue_tasks: 4, blocking_tasks: 3, document_collection_rate: 65.0 });
    }).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { key: 'bgc' as const, label: 'Background Checks' },
    { key: 'tasks' as const, label: 'Onboarding Tasks' },
    { key: 'documents' as const, label: 'Document Collection' },
    { key: 'dashboard' as const, label: 'Dashboard' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">BGC & Onboarding Center</h1>
        <p className="text-gray-500 mt-1">Background check initiation, onboarding task assignment, document collection & role-based workflows</p>
      </div>

      {/* Role Legend */}
      <div className="bg-white border rounded-lg p-3 mb-4 flex flex-wrap gap-2">
        <span className="text-xs text-gray-500 font-medium mr-2 self-center">ROLES:</span>
        {[['MSP Coordinator', 'msp_coordinator'], ['Supplier Coordinator', 'supplier_coordinator'], ['Client IT', 'client_it'], ['Client HR', 'client_hr'], ['Candidate', 'candidate'], ['Sys Admin MSP', 'system_admin_msp'], ['Sys Admin Client', 'system_admin_client']].map(([label, key]) => (
          <span key={key} className={`px-2 py-0.5 rounded text-xs font-medium ${roleColors[key] || 'bg-gray-100'}`}>{label}</span>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${tab === t.key ? 'bg-white shadow text-blue-700' : 'text-gray-600 hover:text-gray-900'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading ? <div className="text-center py-12 text-gray-400">Loading...</div> : (
        <>
          {/* BGC Tab */}
          {tab === 'bgc' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="font-semibold text-lg">Background Check Requests</h2>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Initiate BGC</button>
              </div>
              {bgcRequests.map(req => (
                <div key={req.id} className="bg-white border rounded-lg p-4 shadow-sm">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">{req.candidate_name}</h3>
                      <p className="text-sm text-gray-500">{req.package_name} • {req.vendor_name}</p>
                      <p className="text-xs text-gray-400 mt-1">{req.supplier_name} → {req.client_name}</p>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[req.status] || 'bg-gray-100'}`}>{req.status.replace(/_/g, ' ')}</span>
                      {req.risk_level && <p className={`text-xs mt-1 font-medium ${req.risk_level === 'low' ? 'text-green-600' : req.risk_level === 'high' ? 'text-red-600' : 'text-yellow-600'}`}>Risk: {req.risk_level}</p>}
                    </div>
                  </div>
                  {/* Role assignments */}
                  <div className="flex gap-4 mb-3 text-xs">
                    <div><span className="text-gray-400">Initiated by:</span> <span className={`ml-1 px-1.5 py-0.5 rounded ${roleColors[req.initiated_by_role]}`}>{req.initiated_by_role.replace(/_/g, ' ')}</span></div>
                    <div><span className="text-gray-400">Coordinated by:</span> <span className={`ml-1 px-1.5 py-0.5 rounded ${roleColors[req.coordinated_by_role]}`}>{req.coordinated_by_role.replace(/_/g, ' ')}</span></div>
                    <div><span className="text-gray-400">Executed by:</span> <span className={`ml-1 px-1.5 py-0.5 rounded ${roleColors[req.executed_by_role]}`}>{req.executed_by_role.replace(/_/g, ' ')}</span></div>
                  </div>
                  {/* Check items */}
                  <div className="flex gap-2">
                    {req.check_items.map((ci, i) => (
                      <span key={i} className={`px-2 py-1 rounded text-xs ${statusColors[ci.status] || 'bg-gray-100'}`}>
                        {ci.check_type} {ci.result === 'clear' ? '✓' : ci.status === 'in_progress' ? '⏳' : '○'}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tasks Tab */}
          {tab === 'tasks' && (
            <div className="bg-white border rounded-lg shadow-sm overflow-hidden">
              <div className="p-4 border-b flex justify-between items-center">
                <h2 className="font-semibold text-lg">Onboarding Tasks</h2>
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded text-sm">Filter by Role</button>
                  <button className="px-4 py-1.5 bg-blue-600 text-white rounded text-sm">+ Add Task</button>
                </div>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left p-3 font-medium text-gray-600">Candidate</th>
                    <th className="text-left p-3 font-medium text-gray-600">Task</th>
                    <th className="text-center p-3 font-medium text-gray-600">Owner Role</th>
                    <th className="text-center p-3 font-medium text-gray-600">Org</th>
                    <th className="text-center p-3 font-medium text-gray-600">Priority</th>
                    <th className="text-center p-3 font-medium text-gray-600">Due</th>
                    <th className="text-center p-3 font-medium text-gray-600">Follow-ups</th>
                    <th className="text-center p-3 font-medium text-gray-600">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {tasks.map(t => (
                    <tr key={t.id} className={`hover:bg-gray-50 ${t.is_overdue ? 'bg-red-50' : ''}`}>
                      <td className="p-3 font-medium">{t.candidate_name}</td>
                      <td className="p-3">
                        <span>{t.task_name}</span>
                        {t.blocks_start_date && <span className="ml-1 text-red-500 text-xs font-bold" title="Blocks placement start">🚫</span>}
                      </td>
                      <td className="p-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${roleColors[t.owner_role] || 'bg-gray-100'}`}>{t.owner_role_display}</span></td>
                      <td className="p-3 text-center text-gray-600 text-xs">{t.assigned_to_org}</td>
                      <td className={`p-3 text-center text-xs font-medium ${priorityLabels[t.priority]?.color}`}>{priorityLabels[t.priority]?.text}</td>
                      <td className={`p-3 text-center text-xs ${t.is_overdue ? 'text-red-600 font-bold' : 'text-gray-600'}`}>{t.due_date}</td>
                      <td className="p-3 text-center">{t.follow_up_count > 0 ? <span className="text-orange-600 font-bold">{t.follow_up_count}</span> : '—'}</td>
                      <td className="p-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[t.status] || 'bg-gray-100'}`}>{t.status.replace(/_/g, ' ')}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Documents Tab */}
          {tab === 'documents' && (
            <div className="bg-white border rounded-lg shadow-sm overflow-hidden">
              <div className="p-4 border-b"><h2 className="font-semibold text-lg">Document Collection Tracker</h2></div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left p-3 font-medium text-gray-600">Candidate</th>
                    <th className="text-left p-3 font-medium text-gray-600">Document</th>
                    <th className="text-center p-3 font-medium text-gray-600">Category</th>
                    <th className="text-center p-3 font-medium text-gray-600">Collected By</th>
                    <th className="text-center p-3 font-medium text-gray-600">Received</th>
                    <th className="text-center p-3 font-medium text-gray-600">Verified</th>
                    <th className="text-center p-3 font-medium text-gray-600">Due By</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {docs.map(d => (
                    <tr key={d.id} className="hover:bg-gray-50">
                      <td className="p-3 font-medium">{d.candidate_name}</td>
                      <td className="p-3">{d.document_name}</td>
                      <td className="p-3 text-center"><span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{d.category.replace(/_/g, ' ')}</span></td>
                      <td className="p-3 text-center">{d.collected_by_role ? <span className={`px-2 py-0.5 rounded text-xs ${roleColors[d.collected_by_role] || 'bg-gray-100'}`}>{d.collected_by_role.replace(/_/g, ' ')}</span> : <span className="text-gray-400">—</span>}</td>
                      <td className="p-3 text-center">{d.is_received ? <span className="text-green-500 text-lg">✓</span> : <span className="text-gray-300 text-lg">○</span>}</td>
                      <td className="p-3 text-center">{d.is_verified ? <span className="text-green-500 text-lg">✓</span> : <span className="text-gray-300 text-lg">○</span>}</td>
                      <td className="p-3 text-center text-xs text-gray-600">{d.required_by}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Dashboard Tab */}
          {tab === 'dashboard' && (
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white border rounded-lg p-5 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-4">BGC Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Total Requests', value: bgcKpis.total_requests, color: 'text-blue-600' },
                    { label: 'Pass Rate', value: `${bgcKpis.pass_rate}%`, color: 'text-green-600' },
                    { label: 'Avg Days', value: bgcKpis.avg_completion_days, color: 'text-purple-600' },
                    { label: 'Pending Review', value: bgcKpis.pending_review, color: 'text-yellow-600' },
                  ].map(k => (
                    <div key={k.label} className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">{k.label}</p>
                      <p className={`text-xl font-bold ${k.color}`}>{k.value}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-white border rounded-lg p-5 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-4">Onboarding Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Total Tasks', value: taskKpis.total_tasks, color: 'text-blue-600' },
                    { label: 'Overdue', value: taskKpis.overdue_tasks, color: 'text-red-600' },
                    { label: 'Blocking Start', value: taskKpis.blocking_tasks, color: 'text-orange-600' },
                    { label: 'Doc Collection', value: `${taskKpis.document_collection_rate}%`, color: 'text-green-600' },
                  ].map(k => (
                    <div key={k.label} className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">{k.label}</p>
                      <p className={`text-xl font-bold ${k.color}`}>{k.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
