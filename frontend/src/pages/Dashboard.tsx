import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardBody, CardHeader } from '@/components/common/Card';
import { KPICard } from '@/components/common/KPICard';
import { LoadingSpinner, Skeleton } from '@/components/common/LoadingSpinner';
import { PipelineChart } from '@/components/charts/PipelineChart';
import { FunnelChart } from '@/components/charts/FunnelChart';
import { DonutChart } from '@/components/charts/DonutChart';
import { useApi } from '@/hooks/useApi';
import {
  getDashboardOverview,
  getPipelineMetrics,
  getSubmissionFunnel,
  getActivityFeed,
  getTopRecruiters,
  getRequirementUrgencies,
} from '@/api/dashboard';
import {
  UserGroupIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  SparklesIcon,
  ArrowArrowTrendingUpIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';

export const Dashboard: React.FC = () => {
  const { data: overview, isLoading: overviewLoading } = useApi(
    'dashboard-overview',
    getDashboardOverview
  );

  const { data: pipelineMetrics, isLoading: pipelineLoading } = useApi(
    'dashboard-pipeline',
    getPipelineMetrics
  );

  const { data: funnel, isLoading: funnelLoading } = useApi(
    'dashboard-funnel',
    getSubmissionFunnel
  );

  const { data: activity, isLoading: activityLoading } = useApi(
    'dashboard-activity',
    () => getActivityFeed(10)
  );

  const { data: recruiters, isLoading: recruitersLoading } = useApi(
    'dashboard-recruiters',
    () => getTopRecruiters(5)
  );

  const { data: urgencies, isLoading: urgenciesLoading } = useApi(
    'dashboard-urgencies',
    getRequirementUrgencies
  );

  return (
    <AppLayout title="Dashboard">
      <div className="p-4 md:p-6 space-y-6 pb-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {overviewLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-lg" />
            ))
          ) : overview ? (
            <>
              <KPICard
                icon={<DocumentTextIcon className="w-full h-full" />}
                label="Active Reqs"
                value={overview.total_active_requirements}
                color="primary"
              />
              <KPICard
                icon={<UserGroupIcon className="w-full h-full" />}
                label="Pipeline Size"
                value={overview.candidates_in_pipeline}
                color="success"
              />
              <KPICard
                icon={<CheckCircleIcon className="w-full h-full" />}
                label="Submissions MTD"
                value={overview.submissions_this_month}
                color="warning"
              />
              <KPICard
                icon={<SparklesIcon className="w-full h-full" />}
                label="Placements MTD"
                value={overview.placements_this_month}
                color="danger"
              />
              <KPICard
                icon={<CalendarIcon className="w-full h-full" />}
                label="Avg Time-to-Fill"
                value={`${overview.average_time_to_fill_days} days`}
                color="primary"
              />
              <KPICard
                icon={<ArrowTrendingUpIcon className="w-full h-full" />}
                label="Fill Rate"
                value={`${overview.fill_rate_percentage}%`}
                color="success"
              />
            </>
          ) : null}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {pipelineLoading ? (
              <Skeleton className="h-80" />
            ) : (
              <PipelineChart data={pipelineMetrics?.stages || []} loading={pipelineLoading} />
            )}
          </div>

          <div>
            {funnelLoading ? (
              <Skeleton className="h-80" />
            ) : (
              <FunnelChart
                data={funnel || {
                  draft: 0,
                  pending: 0,
                  approved: 0,
                  submitted: 0,
                  customer_review: 0,
                  placed: 0,
                  rejected: 0,
                }}
                loading={funnelLoading}
              />
            )}
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Activity Feed */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>Recent Activity</CardHeader>
              <CardBody className="space-y-2 max-h-96 overflow-y-auto">
                {activityLoading ? (
                  <Skeleton className="h-48" />
                ) : activity && activity.length > 0 ? (
                  activity.map((item) => (
                    <div
                      key={item.id}
                      className="pb-3 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0"
                    >
                      <p className="text-sm font-medium text-neutral-900 dark:text-white">
                        {item.actor_name}
                      </p>
                      <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                        {item.description}
                      </p>
                      <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
                        {new Date(item.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-neutral-500 dark:text-neutral-400">
                    No recent activity
                  </p>
                )}
              </CardBody>
            </Card>
          </div>

          {/* Urgent Requirements */}
          <Card>
            <CardHeader>Urgent Requirements</CardHeader>
            <CardBody className="space-y-3 max-h-96 overflow-y-auto">
              {urgenciesLoading ? (
                <Skeleton className="h-48" />
              ) : urgencies && urgencies.length > 0 ? (
                urgencies.slice(0, 5).map((req) => (
                  <div
                    key={req.requirement_id}
                    className="pb-3 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0"
                  >
                    <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                      {req.title}
                    </p>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs text-danger-600 dark:text-danger-400 font-semibold">
                        {req.days_open} days open
                      </p>
                      <span className="px-2 py-1 text-xs font-medium bg-danger-50 dark:bg-danger-900/20 text-danger-700 dark:text-danger-400 rounded">
                        {req.submissions_count} submissions
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-neutral-500 dark:text-neutral-400">
                  No urgent requirements
                </p>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Top Recruiters */}
        <Card>
          <CardHeader>Top Performing Recruiters</CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    <th className="text-left py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">
                      Rank
                    </th>
                    <th className="text-left py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">
                      Name
                    </th>
                    <th className="text-left py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">
                      This Month
                    </th>
                    <th className="text-left py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">
                      Avg Time-to-Fill
                    </th>
                    <th className="text-left py-2 px-2 font-semibold text-neutral-700 dark:text-neutral-300">
                      Revenue
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recruitersLoading ? (
                    <tr>
                      <td colSpan={5} className="py-4">
                        <Skeleton className="h-10" />
                      </td>
                    </tr>
                  ) : recruiters && recruiters.length > 0 ? (
                    recruiters.map((recruiter) => (
                      <tr
                        key={recruiter.recruiter_id}
                        className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors duration-250"
                      >
                        <td className="py-2 px-2 text-neutral-600 dark:text-neutral-400">
                          #{recruiter.rank}
                        </td>
                        <td className="py-2 px-2 font-medium text-neutral-900 dark:text-white">
                          {recruiter.recruiter_name}
                        </td>
                        <td className="py-2 px-2 text-neutral-600 dark:text-neutral-400">
                          {recruiter.placements_this_month}
                        </td>
                        <td className="py-2 px-2 text-neutral-600 dark:text-neutral-400">
                          {recruiter.average_time_to_fill} days
                        </td>
                        <td className="py-2 px-2 font-medium text-success-600 dark:text-success-400">
                          ${recruiter.total_revenue.toLocaleString()}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-neutral-500">
                        No data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      </div>
    </AppLayout>
  );
};
