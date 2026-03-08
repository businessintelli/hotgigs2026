import React, { useState } from 'react';
import { CheckCircleIcon, ClockIcon, ExclamationTriangleIcon, PlusIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface Task {
  id: string;
  name: string;
  type: 'DOCUMENT' | 'BACKGROUND_CHECK' | 'EQUIPMENT' | 'TRAINING' | 'COMPLIANCE' | 'SYSTEM_ACCESS';
  assignedTo: string;
  dueDate: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Blocked' | 'Overdue';
  candidateName: string;
}

interface CandidateOnboarding {
  id: string;
  name: string;
  startDate: string;
  completedTasks: number;
  totalTasks: number;
}

const mockCandidates: CandidateOnboarding[] = [
  {
    id: '1',
    name: 'Sarah Johnson',
    startDate: 'Mar 17, 2026',
    completedTasks: 5,
    totalTasks: 8,
  },
  {
    id: '2',
    name: 'Alex Chen',
    startDate: 'Mar 20, 2026',
    completedTasks: 3,
    totalTasks: 8,
  },
  {
    id: '3',
    name: 'Emma Davis',
    startDate: 'Mar 25, 2026',
    completedTasks: 1,
    totalTasks: 8,
  },
];

const mockTasks: Task[] = [
  {
    id: '1',
    name: 'Employment Agreement',
    type: 'DOCUMENT',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 14, 2026',
    status: 'Completed',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '2',
    name: 'Background Check',
    type: 'BACKGROUND_CHECK',
    assignedTo: 'Compliance Team',
    dueDate: 'Mar 15, 2026',
    status: 'Completed',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '3',
    name: 'Equipment Setup',
    type: 'EQUIPMENT',
    assignedTo: 'IT Department',
    dueDate: 'Mar 16, 2026',
    status: 'In Progress',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '4',
    name: 'System Access',
    type: 'SYSTEM_ACCESS',
    assignedTo: 'IT Department',
    dueDate: 'Mar 16, 2026',
    status: 'Pending',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '5',
    name: 'Compliance Training',
    type: 'TRAINING',
    assignedTo: 'Learning & Dev',
    dueDate: 'Mar 17, 2026',
    status: 'Pending',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '6',
    name: 'I-9 Verification',
    type: 'COMPLIANCE',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 16, 2026',
    status: 'Completed',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '7',
    name: 'Direct Deposit Setup',
    type: 'DOCUMENT',
    assignedTo: 'Payroll',
    dueDate: 'Mar 15, 2026',
    status: 'Completed',
    candidateName: 'Sarah Johnson',
  },
  {
    id: '8',
    name: 'Orientation Program',
    type: 'TRAINING',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 17, 2026',
    status: 'Pending',
    candidateName: 'Sarah Johnson',
  },
  // Alex Chen tasks
  {
    id: '9',
    name: 'Employment Agreement',
    type: 'DOCUMENT',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 18, 2026',
    status: 'Completed',
    candidateName: 'Alex Chen',
  },
  {
    id: '10',
    name: 'Background Check',
    type: 'BACKGROUND_CHECK',
    assignedTo: 'Compliance Team',
    dueDate: 'Mar 19, 2026',
    status: 'In Progress',
    candidateName: 'Alex Chen',
  },
  {
    id: '11',
    name: 'Equipment Setup',
    type: 'EQUIPMENT',
    assignedTo: 'IT Department',
    dueDate: 'Mar 19, 2026',
    status: 'Pending',
    candidateName: 'Alex Chen',
  },
  {
    id: '12',
    name: 'System Access',
    type: 'SYSTEM_ACCESS',
    assignedTo: 'IT Department',
    dueDate: 'Mar 20, 2026',
    status: 'Pending',
    candidateName: 'Alex Chen',
  },
  {
    id: '13',
    name: 'Compliance Training',
    type: 'TRAINING',
    assignedTo: 'Learning & Dev',
    dueDate: 'Mar 20, 2026',
    status: 'Pending',
    candidateName: 'Alex Chen',
  },
  {
    id: '14',
    name: 'I-9 Verification',
    type: 'COMPLIANCE',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 19, 2026',
    status: 'Pending',
    candidateName: 'Alex Chen',
  },
  {
    id: '15',
    name: 'Direct Deposit Setup',
    type: 'DOCUMENT',
    assignedTo: 'Payroll',
    dueDate: 'Mar 19, 2026',
    status: 'Pending',
    candidateName: 'Alex Chen',
  },
  {
    id: '16',
    name: 'Orientation Program',
    type: 'TRAINING',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 20, 2026',
    status: 'Pending',
    candidateName: 'Alex Chen',
  },
  // Emma Davis tasks
  {
    id: '17',
    name: 'Employment Agreement',
    type: 'DOCUMENT',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 24, 2026',
    status: 'Completed',
    candidateName: 'Emma Davis',
  },
  {
    id: '18',
    name: 'Background Check',
    type: 'BACKGROUND_CHECK',
    assignedTo: 'Compliance Team',
    dueDate: 'Mar 25, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
  {
    id: '19',
    name: 'Equipment Setup',
    type: 'EQUIPMENT',
    assignedTo: 'IT Department',
    dueDate: 'Mar 25, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
  {
    id: '20',
    name: 'System Access',
    type: 'SYSTEM_ACCESS',
    assignedTo: 'IT Department',
    dueDate: 'Mar 25, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
  {
    id: '21',
    name: 'Compliance Training',
    type: 'TRAINING',
    assignedTo: 'Learning & Dev',
    dueDate: 'Mar 26, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
  {
    id: '22',
    name: 'I-9 Verification',
    type: 'COMPLIANCE',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 25, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
  {
    id: '23',
    name: 'Direct Deposit Setup',
    type: 'DOCUMENT',
    assignedTo: 'Payroll',
    dueDate: 'Mar 25, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
  {
    id: '24',
    name: 'Orientation Program',
    type: 'TRAINING',
    assignedTo: 'HR Manager',
    dueDate: 'Mar 25, 2026',
    status: 'Pending',
    candidateName: 'Emma Davis',
  },
];

const getTaskTypeColor = (type: Task['type']) => {
  switch (type) {
    case 'DOCUMENT':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'BACKGROUND_CHECK':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'EQUIPMENT':
      return 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400';
    case 'TRAINING':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'COMPLIANCE':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'SYSTEM_ACCESS':
      return 'bg-indigo-100 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getStatusColor = (status: Task['status']) => {
  switch (status) {
    case 'Pending':
      return 'bg-gray-100 dark:bg-gray-900/20 text-gray-700 dark:text-gray-400';
    case 'In Progress':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'Completed':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'Blocked':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'Overdue':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

export const OnboardingTracker: React.FC = () => {
  const [expandedCandidate, setExpandedCandidate] = useState<string>(mockCandidates[0].id);

  const pendingCount = mockTasks.filter(t => t.status === 'Pending').length;
  const inProgressCount = mockTasks.filter(t => t.status === 'In Progress').length;
  const completedCount = mockTasks.filter(t => t.status === 'Completed').length;
  const blockedCount = mockTasks.filter(t => t.status === 'Blocked').length;
  const overdueCount = mockTasks.filter(t => t.status === 'Overdue').length;

  const expandedCandidateTasks = mockTasks.filter(
    t => t.candidateName === mockCandidates.find(c => c.id === expandedCandidate)?.name
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Onboarding Tracker</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Manage post-offer onboarding tasks</p>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Pending Tasks</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">{pendingCount}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">In Progress</p>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">{inProgressCount}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Completed</p>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">{completedCount}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Blocked</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">{blockedCount}</p>
        </div>
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">Overdue</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">{overdueCount}</p>
        </div>
      </div>

      {/* Overdue Alerts */}
      {overdueCount > 0 && (
        <div className="bg-red-50 dark:bg-red-900/10 rounded-xl p-6 border border-red-200 dark:border-red-800">
          <div className="flex items-start gap-4">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2">Overdue Tasks</h4>
              <p className="text-sm text-red-800 dark:text-red-200">
                There are {overdueCount} overdue onboarding task(s) that require immediate attention.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Candidate Onboarding View */}
      <div className="space-y-6">
        {mockCandidates.map((candidate) => {
          const candidateTasks = mockTasks.filter(t => t.candidateName === candidate.name);
          const progressPercent = (candidate.completedTasks / candidate.totalTasks) * 100;

          return (
            <div
              key={candidate.id}
              className="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden"
            >
              {/* Candidate Header */}
              <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">{candidate.name}</h3>
                    <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
                      Start Date: {candidate.startDate}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div>
                      <p className="text-sm text-neutral-500 dark:text-neutral-400 mb-2">Progress</p>
                      <div className="flex items-center gap-2">
                        <div className="w-48 h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-300"
                            style={{ width: `${progressPercent}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-neutral-900 dark:text-white whitespace-nowrap">
                          {candidate.completedTasks}/{candidate.totalTasks}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => setExpandedCandidate(expandedCandidate === candidate.id ? '' : candidate.id)}
                      className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
                    >
                      {expandedCandidate === candidate.id ? '▼' : '▶'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Expanded Task List */}
              {expandedCandidate === candidate.id && (
                <div className="divide-y divide-neutral-200 dark:divide-neutral-700">
                  {candidateTasks.map((task) => (
                    <div key={task.id} className="p-6 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-medium text-neutral-900 dark:text-white">{task.name}</h4>
                            <span className={`px-2.5 py-1 rounded text-xs font-semibold ${getTaskTypeColor(task.type)}`}>
                              {task.type}
                            </span>
                          </div>
                          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3">
                            Assigned to {task.assignedTo} • Due {task.dueDate}
                          </p>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold inline-block ${getStatusColor(task.status)}`}>
                            {task.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {task.status === 'Completed' && (
                            <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0" />
                          )}
                          {task.status === 'Pending' && (
                            <ClockIcon className="w-5 h-5 text-gray-500 flex-shrink-0" />
                          )}
                        </div>
                      </div>
                      {task.status !== 'Completed' && (
                        <div className="flex items-center gap-2 mt-4">
                          <button className="px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded border border-emerald-200 dark:border-emerald-800 transition-colors">
                            Mark Complete
                          </button>
                          <button className="px-3 py-1 text-xs font-medium text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded border border-amber-200 dark:border-amber-800 transition-colors">
                            Block
                          </button>
                          <button className="px-3 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800 transition-colors">
                            Waive
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default OnboardingTracker;
