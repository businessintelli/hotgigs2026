import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { useApi } from '@/hooks/useApi';
import { getSubmissions } from '@/api/submissions';
import type { Submission } from '@/types';

const submissionStages = [
  { id: 'draft', label: 'Draft', color: 'bg-neutral-100 dark:bg-neutral-700' },
  { id: 'pending', label: 'Pending', color: 'bg-warning-100 dark:bg-warning-900/20' },
  { id: 'approved', label: 'Approved', color: 'bg-success-100 dark:bg-success-900/20' },
  { id: 'submitted', label: 'Submitted', color: 'bg-primary-100 dark:bg-primary-900/20' },
  { id: 'customer_review', label: 'Customer Review', color: 'bg-primary-100 dark:bg-primary-900/20' },
  { id: 'placed', label: 'Placed', color: 'bg-success-100 dark:bg-success-900/20' },
];

export const Submissions: React.FC = () => {
  const [listView, setListView] = useState(false);
  const { data: submissionsData, isLoading } = useApi(['submissions', 0, ''], () =>
    getSubmissions({ page: 1, per_page: 50 })
  );

  const submissionsByStage = (stage: string) =>
    submissionsData?.data.filter((s) => s.status === stage) || [];

  if (listView) {
    return (
      <AppLayout title="Submissions">
        <div className="p-4 md:p-6 space-y-6 pb-8">
          <div className="flex justify-end">
            <button
              onClick={() => setListView(false)}
              className="px-4 py-2 border border-neutral-200 dark:border-neutral-700 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250"
            >
              Kanban View
            </button>
          </div>

          <Card>
            <CardHeader>All Submissions</CardHeader>
            <CardBody>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 dark:border-neutral-700">
                      <th className="text-left py-2 px-2 font-semibold">Candidate</th>
                      <th className="text-left py-2 px-2 font-semibold">Requirement</th>
                      <th className="text-left py-2 px-2 font-semibold">Match</th>
                      <th className="text-left py-2 px-2 font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {submissionsData?.data.map((submission) => (
                      <tr
                        key={submission.id}
                        className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700"
                      >
                        <td className="py-2 px-2 font-medium">
                          {submission.candidate.first_name} {submission.candidate.last_name}
                        </td>
                        <td className="py-2 px-2">{submission.requirement.title}</td>
                        <td className="py-2 px-2">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                              <span className="text-xs font-bold text-primary-600 dark:text-primary-400">
                                {submission.match_score}%
                              </span>
                            </div>
                          </div>
                        </td>
                        <td className="py-2 px-2">
                          <StatusBadge status={submission.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardBody>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout title="Submissions">
      <div className="p-4 md:p-6 space-y-6 pb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">
              Submission Pipeline
            </h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Drag and drop to move submissions between stages
            </p>
          </div>
          <button
            onClick={() => setListView(true)}
            className="px-4 py-2 border border-neutral-200 dark:border-neutral-700 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250"
          >
            List View
          </button>
        </div>

        {/* Kanban Board */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 overflow-x-auto pb-4">
          {submissionStages.map((stage) => (
            <div key={stage.id} className="flex-shrink-0 w-full md:w-96">
              <Card className="h-full">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-neutral-900 dark:text-white">
                      {stage.label}
                    </h3>
                    <span className="text-xs font-bold px-2 py-1 rounded bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300">
                      {submissionsByStage(stage.id).length}
                    </span>
                  </div>
                </CardHeader>
                <CardBody className="space-y-3">
                  {submissionsByStage(stage.id).map((submission: Submission) => (
                    <div
                      key={submission.id}
                      className={`p-3 rounded-lg ${stage.color} cursor-move hover:shadow-md transition-shadow duration-250`}
                    >
                      <p className="font-medium text-sm text-neutral-900 dark:text-white">
                        {submission.candidate.first_name} {submission.candidate.last_name}
                      </p>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                        {submission.requirement.title}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs font-bold text-primary-600 dark:text-primary-400">
                          {submission.match_score}% match
                        </span>
                        {submission.rate_proposed && (
                          <span className="text-xs text-neutral-600 dark:text-neutral-400">
                            ${submission.rate_proposed}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                  {submissionsByStage(stage.id).length === 0 && (
                    <p className="text-xs text-neutral-400 dark:text-neutral-500 text-center py-8">
                      No submissions
                    </p>
                  )}
                </CardBody>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
};
