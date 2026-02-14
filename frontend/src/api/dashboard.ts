import client from './client';
import type {
  DashboardOverview,
  PipelineMetrics,
  SubmissionFunnel,
  ActivityFeed,
  RecruitersPerformance,
  RequirementUrgency,
} from '@/types';

export const getDashboardOverview = async (): Promise<DashboardOverview> => {
  const response = await client.get<DashboardOverview>('/dashboard/overview');
  return response.data;
};

export const getPipelineMetrics = async (): Promise<PipelineMetrics> => {
  const response = await client.get<PipelineMetrics>('/dashboard/pipeline');
  return response.data;
};

export const getSubmissionFunnel = async (): Promise<SubmissionFunnel> => {
  const response = await client.get<SubmissionFunnel>('/dashboard/funnel');
  return response.data;
};

export const getActivityFeed = async (limit?: number): Promise<ActivityFeed[]> => {
  const response = await client.get<ActivityFeed[]>('/dashboard/activity', {
    params: { limit: limit || 20 },
  });
  return response.data;
};

export const getTopRecruiters = async (
  limit?: number
): Promise<RecruitersPerformance[]> => {
  const response = await client.get<RecruitersPerformance[]>(
    '/dashboard/top-recruiters',
    {
      params: { limit: limit || 10 },
    }
  );
  return response.data;
};

export const getRequirementUrgencies = async (): Promise<RequirementUrgency[]> => {
  const response = await client.get<RequirementUrgency[]>(
    '/dashboard/urgent-requirements'
  );
  return response.data;
};

export const getDashboardStats = async (dateRange?: { start: string; end: string }) => {
  const response = await client.get('/dashboard/stats', {
    params: dateRange,
  });
  return response.data;
};

export const getMonthlyTrends = async () => {
  const response = await client.get('/dashboard/monthly-trends');
  return response.data;
};

export const getSourceDistribution = async () => {
  const response = await client.get('/dashboard/source-distribution');
  return response.data;
};

export const getCandidateSourceMetrics = async () => {
  const response = await client.get('/dashboard/candidate-sources');
  return response.data;
};

export const getPlacementMetrics = async () => {
  const response = await client.get('/dashboard/placement-metrics');
  return response.data;
};
