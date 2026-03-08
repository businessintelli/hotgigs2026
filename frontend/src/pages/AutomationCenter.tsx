import React, { useState } from 'react';
import {
  SparklesIcon,
  BellIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  PlusIcon,
  AdjustmentsHorizontalIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

interface AutomationRule {
  id: string;
  name: string;
  triggerEvent: string;
  actionType: string;
  enabled: boolean;
  executionCount: number;
  lastTriggered: string;
}

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'alert' | 'success';
  title: string;
  message: string;
  category: string;
  timeAgo: string;
  isRead: boolean;
}

const mockRules: AutomationRule[] = [
  {
    id: '1',
    name: 'Auto-send interview confirmations',
    triggerEvent: 'Interview Scheduled',
    actionType: 'Send Email',
    enabled: true,
    executionCount: 24,
    lastTriggered: 'Today at 2:30 PM',
  },
  {
    id: '2',
    name: 'Auto-move candidates to next stage',
    triggerEvent: 'Interview Completed',
    actionType: 'Update Status',
    enabled: true,
    executionCount: 12,
    lastTriggered: 'Yesterday at 4:15 PM',
  },
  {
    id: '3',
    name: 'Notify manager on offer acceptance',
    triggerEvent: 'Offer Accepted',
    actionType: 'Send Notification',
    enabled: true,
    executionCount: 8,
    lastTriggered: 'Mar 7 at 11:20 AM',
  },
  {
    id: '4',
    name: 'Auto-generate onboarding tasks',
    triggerEvent: 'Offer Accepted',
    actionType: 'Create Tasks',
    enabled: false,
    executionCount: 0,
    lastTriggered: 'Never',
  },
];

const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'success',
    title: 'Interview Confirmed',
    message: 'Sarah Johnson confirmed interview for Senior Frontend Engineer',
    category: 'Interviews',
    timeAgo: '2 minutes ago',
    isRead: false,
  },
  {
    id: '2',
    type: 'alert',
    title: 'Urgent: Offer Expiring Soon',
    message: 'Offer for Alex Chen expires in 2 days',
    category: 'Offers',
    timeAgo: '15 minutes ago',
    isRead: false,
  },
  {
    id: '3',
    type: 'warning',
    title: 'Task Overdue',
    message: 'Background check for Emma Davis is overdue',
    category: 'Onboarding',
    timeAgo: '1 hour ago',
    isRead: false,
  },
  {
    id: '4',
    type: 'info',
    title: 'Rule Executed',
    message: 'Auto-send interview confirmations rule executed 5 times',
    category: 'Automation',
    timeAgo: '3 hours ago',
    isRead: true,
  },
  {
    id: '5',
    type: 'success',
    title: 'Onboarding Complete',
    message: 'All onboarding tasks completed for Mike Johnson',
    category: 'Onboarding',
    timeAgo: '5 hours ago',
    isRead: true,
  },
  {
    id: '6',
    type: 'info',
    title: 'Status Update',
    message: 'Candidate submission created for Jennifer Martinez',
    category: 'Submissions',
    timeAgo: '1 day ago',
    isRead: true,
  },
  {
    id: '7',
    type: 'warning',
    title: 'SLA Alert',
    message: 'Interview scheduling SLA at risk for TechCorp Industries',
    category: 'SLA',
    timeAgo: '1 day ago',
    isRead: true,
  },
  {
    id: '8',
    type: 'info',
    title: 'New Submission',
    message: 'New candidate submission for DevOps Engineer role',
    category: 'Submissions',
    timeAgo: '2 days ago',
    isRead: true,
  },
];

const getTriggerColor = (trigger: string) => {
  const colors: Record<string, string> = {
    'Interview Scheduled': 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400',
    'Interview Completed': 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400',
    'Offer Accepted': 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400',
    'Offer Extended': 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400',
  };
  return colors[trigger] || 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
};

const getActionColor = (action: string) => {
  const colors: Record<string, string> = {
    'Send Email': 'bg-indigo-100 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-400',
    'Update Status': 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400',
    'Send Notification': 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400',
    'Create Tasks': 'bg-cyan-100 dark:bg-cyan-900/20 text-cyan-700 dark:text-cyan-400',
  };
  return colors[action] || 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
};

const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case 'info':
      return <InformationCircleIcon className="w-5 h-5" />;
    case 'warning':
      return <ExclamationTriangleIcon className="w-5 h-5" />;
    case 'alert':
      return <ExclamationTriangleIcon className="w-5 h-5" />;
    case 'success':
      return <CheckCircleIcon className="w-5 h-5" />;
    default:
      return <BellIcon className="w-5 h-5" />;
  }
};

const getNotificationColor = (type: Notification['type']) => {
  switch (type) {
    case 'info':
      return 'text-blue-500 bg-blue-50 dark:bg-blue-900/10';
    case 'warning':
      return 'text-amber-500 bg-amber-50 dark:bg-amber-900/10';
    case 'alert':
      return 'text-red-500 bg-red-50 dark:bg-red-900/10';
    case 'success':
      return 'text-green-500 bg-green-50 dark:bg-green-900/10';
    default:
      return 'text-neutral-500 bg-neutral-50 dark:bg-neutral-900/10';
  }
};

export const AutomationCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'rules' | 'notifications'>('rules');
  const [showCreateRule, setShowCreateRule] = useState(false);
  const [selectedRule, setSelectedRule] = useState<AutomationRule | null>(null);

  const unreadCount = mockNotifications.filter(n => !n.isRead).length;
  const enabledRules = mockRules.filter(r => r.enabled).length;
  const totalRules = mockRules.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Automation Center</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Manage rules and notifications</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-neutral-200 dark:border-neutral-700">
        <button
          onClick={() => setActiveTab('rules')}
          className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
            activeTab === 'rules'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2">
            <SparklesIcon className="w-5 h-5" />
            Rules ({enabledRules}/{totalRules})
          </div>
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
            activeTab === 'notifications'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2">
            <BellIcon className="w-5 h-5" />
            Notifications
            {unreadCount > 0 && (
              <span className="px-2.5 py-0.5 rounded-full bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-xs font-semibold">
                {unreadCount}
              </span>
            )}
          </div>
        </button>
      </div>

      {/* Rules Tab */}
      {activeTab === 'rules' && (
        <div className="space-y-6">
          {/* Create Rule Button */}
          <div className="flex justify-between items-center">
            <button
              onClick={() => setShowCreateRule(!showCreateRule)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center gap-2"
            >
              <PlusIcon className="w-5 h-5" />
              Create Rule
            </button>
          </div>

          {/* Create Rule Form */}
          {showCreateRule && (
            <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Create New Rule</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Rule Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Auto-send confirmations"
                    className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Trigger Event
                  </label>
                  <select className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white">
                    <option>Select trigger...</option>
                    <option>Interview Scheduled</option>
                    <option>Interview Completed</option>
                    <option>Offer Accepted</option>
                    <option>Offer Extended</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Action Type
                  </label>
                  <select className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white">
                    <option>Select action...</option>
                    <option>Send Email</option>
                    <option>Update Status</option>
                    <option>Send Notification</option>
                    <option>Create Tasks</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Action Config (JSON)
                  </label>
                  <input
                    type="text"
                    placeholder='{"template": "interview_confirm"}'
                    className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white font-mono text-sm"
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors">
                  Create Rule
                </button>
                <button
                  onClick={() => setShowCreateRule(false)}
                  className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg font-medium hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Rules List */}
          <div className="space-y-4">
            {mockRules.map(rule => (
              <div
                key={rule.id}
                className="bg-white dark:bg-neutral-800 rounded-xl p-6 shadow-sm border border-neutral-200 dark:border-neutral-700"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h4 className="font-semibold text-neutral-900 dark:text-white">{rule.name}</h4>
                      <button
                        onClick={() => setSelectedRule(selectedRule?.id === rule.id ? null : rule)}
                        className="text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
                      >
                        {selectedRule?.id === rule.id ? '▼' : '▶'}
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-3 mb-4">
                      <div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getTriggerColor(rule.triggerEvent)}`}>
                          {rule.triggerEvent}
                        </span>
                      </div>
                      <span className="text-neutral-500 dark:text-neutral-400">→</span>
                      <div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getActionColor(rule.actionType)}`}>
                          {rule.actionType}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-neutral-600 dark:text-neutral-400">
                      <span>Executions: {rule.executionCount}</span>
                      <span>Last triggered: {rule.lastTriggered}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      className={`p-2 rounded-lg transition-colors ${
                        rule.enabled
                          ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400'
                          : 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-600 dark:text-neutral-400'
                      }`}
                    >
                      <AdjustmentsHorizontalIcon className="w-5 h-5" />
                    </button>
                    <button className="p-2 rounded-lg text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors">
                      <TrashIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                {selectedRule?.id === rule.id && (
                  <div className="mt-6 pt-6 border-t border-neutral-200 dark:border-neutral-700">
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
                      Rule Details: This rule triggers on {rule.triggerEvent} and executes {rule.actionType} action.
                      It has been executed {rule.executionCount} times successfully.
                    </p>
                    <div className="flex gap-2">
                      <button className="px-3 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/10 rounded border border-blue-200 dark:border-blue-800 transition-colors">
                        Edit
                      </button>
                      <button className="px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/10 rounded border border-emerald-200 dark:border-emerald-800 transition-colors">
                        Test
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </p>
            {unreadCount > 0 && (
              <button className="text-blue-600 dark:text-blue-400 text-sm font-medium hover:underline">
                Mark All Read
              </button>
            )}
          </div>

          {/* Notifications List */}
          {mockNotifications.map(notification => (
            <div
              key={notification.id}
              className={`rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 transition-colors ${
                !notification.isRead
                  ? 'bg-blue-50 dark:bg-blue-900/10'
                  : 'bg-white dark:bg-neutral-800'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`p-2 rounded-lg ${getNotificationColor(notification.type)}`}>
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <h5 className="font-semibold text-neutral-900 dark:text-white">{notification.title}</h5>
                      <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">{notification.message}</p>
                    </div>
                    {!notification.isRead && (
                      <div className="w-3 h-3 rounded-full bg-blue-500 flex-shrink-0 mt-1" />
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300">
                      {notification.category}
                    </span>
                    <span className="text-xs text-neutral-500 dark:text-neutral-500">{notification.timeAgo}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AutomationCenter;
