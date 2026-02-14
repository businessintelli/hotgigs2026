import client from './client';
import type {
  Candidate,
  CreateCandidateInput,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getCandidates = async (
  params?: FilterParams
): Promise<PaginatedResponse<Candidate>> => {
  const response = await client.get<PaginatedResponse<Candidate>>('/candidates', {
    params,
  });
  return response.data;
};

export const getCandidateById = async (id: string): Promise<Candidate> => {
  const response = await client.get<Candidate>(`/candidates/${id}`);
  return response.data;
};

export const createCandidate = async (
  data: CreateCandidateInput
): Promise<Candidate> => {
  const response = await client.post<Candidate>('/candidates', data);
  return response.data;
};

export const updateCandidate = async (
  id: string,
  data: Partial<CreateCandidateInput>
): Promise<Candidate> => {
  const response = await client.put<Candidate>(`/candidates/${id}`, data);
  return response.data;
};

export const updateCandidateStatus = async (
  id: string,
  status: 'active' | 'inactive' | 'placed' | 'archived'
): Promise<Candidate> => {
  const response = await client.patch<Candidate>(`/candidates/${id}/status`, {
    status,
  });
  return response.data;
};

export const deleteCandidate = async (id: string): Promise<void> => {
  await client.delete(`/candidates/${id}`);
};

export const getCandidateTimeline = async (id: string) => {
  const response = await client.get(`/candidates/${id}/timeline`);
  return response.data;
};

export const getCandidateMatches = async (id: string) => {
  const response = await client.get(`/candidates/${id}/matches`);
  return response.data;
};

export const uploadResume = async (id: string, file: File): Promise<Candidate> => {
  const formData = new FormData();
  formData.append('resume', file);

  const response = await client.post<Candidate>(`/candidates/${id}/resume`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadVideoIntro = async (id: string, file: File): Promise<Candidate> => {
  const formData = new FormData();
  formData.append('video', file);

  const response = await client.post<Candidate>(
    `/candidates/${id}/video-intro`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const contactCandidate = async (
  id: string,
  message: string,
  channel: 'email' | 'sms' | 'whatsapp'
): Promise<void> => {
  await client.post(`/candidates/${id}/contact`, {
    message,
    channel,
  });
};

export const bulkUpdateStatus = async (
  ids: string[],
  status: string
): Promise<void> => {
  await client.post('/candidates/bulk-update', {
    ids,
    status,
  });
};
