import React, { useState } from 'react';
import {
  EnvelopeIcon,
  PhoneIcon,
  CalendarIcon,
  PencilIcon,
  ArrowPathIcon,
  XMarkIcon,
  PlusIcon,
  MapPinIcon,
  LockClosedIcon,
  ArrowUpRightIcon,
} from '@heroicons/react/24/outline';

interface Activity {
  id: string;
  type: 'email' | 'call' | 'meeting' | 'note' | 'status_change';
  title: string;
  description: string;
  timestamp: string;
  performedBy: string;
}

interface Note {
  id: string;
  type: 'GENERAL' | 'INTERVIEW' | 'FEEDBACK' | 'TODO';
  content: string;
  isPinned: boolean;
  isPrivate: boolean;
  createdAt: string;
}

interface Tag {
  id: string;
  label: string;
  color: 'blue' | 'green' | 'red' | 'amber' | 'purple';
}

interface Communication {
  id: string;
  channel: 'email' | 'phone' | 'sms' | 'call';
  subject: string;
  direction: 'inbound' | 'outbound';
  date: string;
}

const mockCandidate = {
  id: '1',
  name: 'Sarah Johnson',
  photo: 'SJ',
  matchScore: 87,
  tags: [
    { id: '1', label: 'Senior Dev', color: 'blue' as const },
    { id: '2', label: 'React Expert', color: 'green' as const },
    { id: '3', label: 'Quick Responder', color: 'amber' as const },
  ],
};

const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'status_change',
    title: 'Status Changed to Interviewed',
    description: 'Moved to Interviewed stage',
    timestamp: 'Today at 2:30 PM',
    performedBy: 'John Smith',
  },
  {
    id: '2',
    type: 'meeting',
    title: 'Interview Scheduled',
    description: 'Technical interview with hiring team',
    timestamp: 'Today at 10:15 AM',
    performedBy: 'Jane Doe',
  },
  {
    id: '3',
    type: 'email',
    title: 'Email Sent: Position Details',
    description: 'Sent details about Senior Frontend Engineer role',
    timestamp: 'Yesterday at 4:45 PM',
    performedBy: 'System',
  },
  {
    id: '4',
    type: 'call',
    title: 'Phone Call Completed',
    description: 'Initial screening call - 25 minutes',
    timestamp: 'Mar 6 at 3:00 PM',
    performedBy: 'Mike Johnson',
  },
  {
    id: '5',
    type: 'note',
    title: 'Note Added',
    description: 'Very interested in remote work options',
    timestamp: 'Mar 5 at 11:20 AM',
    performedBy: 'Mike Johnson',
  },
  {
    id: '6',
    type: 'email',
    title: 'Resume Received',
    description: 'Candidate submitted resume',
    timestamp: 'Mar 4 at 9:30 AM',
    performedBy: 'System',
  },
  {
    id: '7',
    type: 'meeting',
    title: 'Submission Created',
    description: 'Added to Senior Frontend Engineer opportunity',
    timestamp: 'Mar 3 at 2:00 PM',
    performedBy: 'Jane Doe',
  },
  {
    id: '8',
    type: 'status_change',
    title: 'Status Changed to Sourced',
    description: 'Initial creation',
    timestamp: 'Mar 2 at 10:00 AM',
    performedBy: 'System',
  },
];

const mockNotes: Note[] = [
  {
    id: '1',
    type: 'INTERVIEW',
    content: 'Strong technical background. Asked good questions about architecture.',
    isPinned: true,
    isPrivate: false,
    createdAt: 'Today at 2:45 PM',
  },
  {
    id: '2',
    type: 'FEEDBACK',
    content: 'Interviewer feedback: Excellent communication skills, demonstrated 10+ years experience',
    isPinned: false,
    isPrivate: true,
    createdAt: 'Today at 2:30 PM',
  },
  {
    id: '3',
    type: 'TODO',
    content: 'Follow up on availability for second round interview',
    isPinned: false,
    isPrivate: false,
    createdAt: 'Yesterday at 4:50 PM',
  },
  {
    id: '4',
    type: 'GENERAL',
    content: 'Background check cleared. Ready to move forward.',
    isPinned: false,
    isPrivate: false,
    createdAt: 'Mar 5 at 11:30 AM',
  },
];

const mockCommunications: Communication[] = [
  {
    id: '1',
    channel: 'email',
    subject: 'Interview Feedback - Strong Match',
    direction: 'outbound',
    date: 'Today',
  },
  {
    id: '2',
    channel: 'phone',
    subject: 'Initial Screening Call',
    direction: 'inbound',
    date: 'Mar 6',
  },
  {
    id: '3',
    channel: 'email',
    subject: 'Job Opportunity - Senior Frontend Engineer',
    direction: 'outbound',
    date: 'Mar 4',
  },
  {
    id: '4',
    channel: 'sms',
    subject: 'Interview reminder',
    direction: 'outbound',
    date: 'Mar 3',
  },
  {
    id: '5',
    channel: 'email',
    subject: 'RE: Thanks for the opportunity',
    direction: 'inbound',
    date: 'Mar 2',
  },
];

const getActivityIcon = (type: Activity['type']) => {
  switch (type) {
    case 'email':
      return <EnvelopeIcon className="w-5 h-5" />;
    case 'call':
      return <PhoneIcon className="w-5 h-5" />;
    case 'meeting':
      return <CalendarIcon className="w-5 h-5" />;
    case 'note':
      return <PencilIcon className="w-5 h-5" />;
    case 'status_change':
      return <ArrowPathIcon className="w-5 h-5" />;
    default:
      return null;
  }
};

const getActivityColor = (type: Activity['type']) => {
  switch (type) {
    case 'email':
      return 'text-blue-500 bg-blue-50 dark:bg-blue-900/20';
    case 'call':
      return 'text-green-500 bg-green-50 dark:bg-green-900/20';
    case 'meeting':
      return 'text-purple-500 bg-purple-50 dark:bg-purple-900/20';
    case 'note':
      return 'text-amber-500 bg-amber-50 dark:bg-amber-900/20';
    case 'status_change':
      return 'text-emerald-500 bg-emerald-50 dark:bg-emerald-900/20';
    default:
      return 'text-neutral-500 bg-neutral-50 dark:bg-neutral-900/20';
  }
};

const getNoteTypeColor = (type: Note['type']) => {
  switch (type) {
    case 'INTERVIEW':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'FEEDBACK':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'TODO':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'GENERAL':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getTagColor = (color: Tag['color']) => {
  switch (color) {
    case 'blue':
      return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400';
    case 'green':
      return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
    case 'red':
      return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400';
    case 'amber':
      return 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400';
    case 'purple':
      return 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400';
    default:
      return 'bg-neutral-100 dark:bg-neutral-900/20 text-neutral-700 dark:text-neutral-400';
  }
};

const getCommunicationIcon = (channel: Communication['channel']) => {
  switch (channel) {
    case 'email':
      return <EnvelopeIcon className="w-4 h-4" />;
    case 'phone':
      return <PhoneIcon className="w-4 h-4" />;
    case 'sms':
      return <PencilIcon className="w-4 h-4" />;
    case 'call':
      return <PhoneIcon className="w-4 h-4" />;
    default:
      return null;
  }
};

export const CandidateCRM: React.FC = () => {
  const [pinnedNotes, setPinnedNotes] = useState<Set<string>>(
    new Set(mockNotes.filter(n => n.isPinned).map(n => n.id))
  );

  const handleRemoveTag = (tagId: string) => {
    // Handle tag removal
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Candidate Relationship Management</h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">Track interactions, notes, and communications</p>
      </div>

      {/* Candidate Header */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <div className="flex items-start justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center text-white font-bold text-lg">
              {mockCandidate.photo}
            </div>
            <div>
              <h2 className="text-3xl font-bold text-neutral-900 dark:text-white">{mockCandidate.name}</h2>
              <p className="text-neutral-500 dark:text-neutral-400 mt-1">Senior Frontend Engineer</p>
              <div className="flex flex-wrap gap-2 mt-3">
                {mockCandidate.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className={`px-3 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-1 ${getTagColor(tag.color)}`}
                  >
                    {tag.label}
                    <button
                      onClick={() => handleRemoveTag(tag.id)}
                      className="hover:opacity-70 transition-opacity"
                    >
                      <XMarkIcon className="w-3 h-3" />
                    </button>
                  </span>
                ))}
                <button className="px-3 py-1 rounded-full text-xs font-semibold border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors flex items-center gap-1">
                  <PlusIcon className="w-3 h-3" />
                  Add Tag
                </button>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-neutral-500 dark:text-neutral-400 mb-1">Match Score</p>
            <div className="text-5xl font-bold text-emerald-600 dark:text-emerald-400">{mockCandidate.matchScore}%</div>
          </div>
        </div>
      </div>

      {/* Quick Actions Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors flex items-center justify-center gap-2">
          <PencilIcon className="w-5 h-5 text-blue-500" />
          <span className="text-sm font-medium text-neutral-900 dark:text-white">Add Note</span>
        </button>
        <button className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors flex items-center justify-center gap-2">
          <PhoneIcon className="w-5 h-5 text-green-500" />
          <span className="text-sm font-medium text-neutral-900 dark:text-white">Log Call</span>
        </button>
        <button className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors flex items-center justify-center gap-2">
          <EnvelopeIcon className="w-5 h-5 text-purple-500" />
          <span className="text-sm font-medium text-neutral-900 dark:text-white">Send Email</span>
        </button>
        <button className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors flex items-center justify-center gap-2">
          <CalendarIcon className="w-5 h-5 text-amber-500" />
          <span className="text-sm font-medium text-neutral-900 dark:text-white">Schedule Meeting</span>
        </button>
      </div>

      {/* Activity Timeline */}
      <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Activity Timeline</h3>
        <div className="space-y-4">
          {mockActivities.map((activity, idx) => (
            <div key={activity.id} className="relative pl-12">
              {/* Timeline line */}
              {idx !== mockActivities.length - 1 && (
                <div className="absolute left-4 top-10 w-0.5 h-12 bg-neutral-200 dark:bg-neutral-700" />
              )}
              {/* Timeline dot */}
              <div
                className={`absolute left-0 top-1 w-9 h-9 rounded-full flex items-center justify-center ${getActivityColor(activity.type)}`}
              >
                {getActivityIcon(activity.type)}
              </div>
              {/* Activity content */}
              <div className="bg-neutral-50 dark:bg-neutral-700/30 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-neutral-900 dark:text-white">{activity.title}</p>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">{activity.description}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-2">
                      {activity.timestamp} • by {activity.performedBy}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Notes Section */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Notes ({mockNotes.length})</h3>
          <div className="space-y-4">
            {mockNotes.map((note) => (
              <div key={note.id} className="border border-neutral-200 dark:border-neutral-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-2.5 py-1 rounded text-xs font-semibold ${getNoteTypeColor(note.type)}`}>
                    {note.type}
                  </span>
                  <div className="flex items-center gap-2">
                    {note.isPinned && (
                      <MapPinIcon className="w-4 h-4 text-amber-500" />
                    )}
                    {note.isPrivate && (
                      <LockClosedIcon className="w-4 h-4 text-red-500" />
                    )}
                  </div>
                </div>
                <p className="text-sm text-neutral-700 dark:text-neutral-300 mb-2">{note.content}</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-500">{note.createdAt}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Communication History */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-8 shadow-sm border border-neutral-200 dark:border-neutral-700">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">Communication History</h3>
          <div className="space-y-3">
            {mockCommunications.map((comm) => (
              <div
                key={comm.id}
                className="flex items-center gap-4 p-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/30 transition-colors"
              >
                <div className="text-neutral-600 dark:text-neutral-400">
                  {getCommunicationIcon(comm.channel)}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-neutral-900 dark:text-white">{comm.subject}</p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-500">{comm.date}</p>
                </div>
                <div className={`${comm.direction === 'inbound' ? 'text-emerald-500' : 'text-blue-500'}`}>
                  <ArrowUpRightIcon className={`w-4 h-4 ${comm.direction === 'inbound' ? 'rotate-180' : ''}`} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateCRM;
