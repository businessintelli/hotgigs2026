import client from './client';
import type {
  Submission,
  CreateSubmissionInput,
  UpdateSubmissionStatusInput,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getSubmissions = async (
  params?: FilterParams
): Promise<PaginatedResponse<Submission>> => {
  const response = await client.get<PaginatedResponse<Submission>>(
    '/submissions',
    { params }
  );
  return response.data;
};

export const getSubmissionById = async (id: string): Promise<Submission> => {
  const response = await client.get<Submission>(`/submissions/${id}`);
  return response.data;
};

export const getSubmissionsByRequirement = async (
  requirementId: string,
  params?: FilterParams
): Promise<PaginatedResponse<Submission>> => {
  const response = await client.get<PaginatedResponse<Submission>>(
    `/requirements/${requirementId}/submissions`,
    { params }
  );
  return response.data;
};

export const getSubmissionsByCandidate = async (
  candidateId: string,
  params?: FilterParams
): Promise<PaginatedResponse<Submission>> => {
  const response = await client.get<PaginatedResponse<Submission>>(
    `/candidates/${candidateId}/submissions`,
    { params }
  );
  return response.data;
};

export const createSubmission = async (
  data: CreateSubmissionInput
): Promise<Submission> => {
  const response = await client.post<Submission>('/submissions', data);
  return response.data;
};

export const updateSubmission = async (
  id: string,
  data: Partial<CreateSubmissionInput>
): Promise<Submission> => {
  const response = await client.put<Submission>(`/submissions/${id}`, data);
  return response.data;
};

export const updateSubmissionStatus = async (
  id: string,
  data: UpdateSubmissionStatusInput
): Promise<Submission> => {
  const response = await client.patch<Submission>(`/submissions/${id}/status`, data);
  return response.data;
};

export const approveSubmission = async (id: string, notes?: string): Promise<Submission> => {
  const response = await client.post<Submission>(`/submissions/${id}/approve`, {
    notes,
  });
  return response.data;
};

export const rejectSubmission = async (
  id: string,
  reason: string
): Promise<Submission> => {
  const response = await client.post<Submission>(`/submissions/${id}/reject`, {
    reason,
  });
  return response.data;
};

export const submitToCustomer = async (
  id: string,
  message?: string
): Promise<Submission> => {
  const response = await client.post<Submission>(`/submissions/${id}/submit`, {
    message,
  });
  return response.data;
};

export const markAsPlaced = async (
  id: string,
  startDate: string
): Promise<Submission> => {
  const response = await client.post<Submission>(`/submissions/${id}/placed`, {
    start_date: startDate,
  });
  return response.data;
};

export const deleteSubmission = async (id: string): Promise<void> => {
  await client.delete(`/submissions/${id}`);
};

export const getSubmissionFunnel = async () => {
  const response = await client.get('/submissions/funnel');
  return response.data;
};

export const bulkUpdateStatus = async (
  ids: string[],
  status: string,
  notes?: string
): Promise<void> => {
  await client.post('/submissions/bulk-update', {
    ids,
    status,
    notes,
  });
};
