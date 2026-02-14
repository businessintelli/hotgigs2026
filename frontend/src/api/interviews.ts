import client from './client';
import type {
  Interview,
  ScheduleInterviewInput,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getInterviews = async (
  params?: FilterParams
): Promise<PaginatedResponse<Interview>> => {
  const response = await client.get<PaginatedResponse<Interview>>(
    '/interviews',
    { params }
  );
  return response.data;
};

export const getInterviewById = async (id: string): Promise<Interview> => {
  const response = await client.get<Interview>(`/interviews/${id}`);
  return response.data;
};

export const getInterviewsByCandidateAndRequirement = async (
  candidateId: string,
  requirementId: string
): Promise<Interview[]> => {
  const response = await client.get<Interview[]>(
    `/candidates/${candidateId}/requirements/${requirementId}/interviews`
  );
  return response.data;
};

export const scheduleInterview = async (
  data: ScheduleInterviewInput
): Promise<Interview> => {
  const response = await client.post<Interview>('/interviews', data);
  return response.data;
};

export const updateInterview = async (
  id: string,
  data: Partial<ScheduleInterviewInput>
): Promise<Interview> => {
  const response = await client.put<Interview>(`/interviews/${id}`, data);
  return response.data;
};

export const completeInterview = async (
  id: string,
  feedback: string,
  rating: number
): Promise<Interview> => {
  const response = await client.post<Interview>(`/interviews/${id}/complete`, {
    feedback,
    rating,
  });
  return response.data;
};

export const cancelInterview = async (
  id: string,
  reason?: string
): Promise<Interview> => {
  const response = await client.post<Interview>(`/interviews/${id}/cancel`, {
    reason,
  });
  return response.data;
};

export const deleteInterview = async (id: string): Promise<void> => {
  await client.delete(`/interviews/${id}`);
};

export const getUpcomingInterviews = async () => {
  const response = await client.get('/interviews/upcoming');
  return response.data;
};

export const getInterviewsThisWeek = async () => {
  const response = await client.get('/interviews/this-week');
  return response.data;
};

export const scheduleInterviewReminder = async (
  id: string,
  minutesBefore: number
): Promise<void> => {
  await client.post(`/interviews/${id}/reminder`, {
    minutes_before: minutesBefore,
  });
};
