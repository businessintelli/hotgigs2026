import client from './client';
import type {
  Requirement,
  CreateRequirementInput,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getRequirements = async (
  params?: FilterParams
): Promise<PaginatedResponse<Requirement>> => {
  const response = await client.get<PaginatedResponse<Requirement>>(
    '/requirements',
    { params }
  );
  return response.data;
};

export const getRequirementById = async (id: string): Promise<Requirement> => {
  const response = await client.get<Requirement>(`/requirements/${id}`);
  return response.data;
};

export const createRequirement = async (
  data: CreateRequirementInput
): Promise<Requirement> => {
  const response = await client.post<Requirement>('/requirements', data);
  return response.data;
};

export const updateRequirement = async (
  id: string,
  data: Partial<CreateRequirementInput>
): Promise<Requirement> => {
  const response = await client.put<Requirement>(`/requirements/${id}`, data);
  return response.data;
};

export const closeRequirement = async (
  id: string,
  reason?: string
): Promise<Requirement> => {
  const response = await client.patch<Requirement>(`/requirements/${id}/close`, {
    reason,
  });
  return response.data;
};

export const reopenRequirement = async (id: string): Promise<Requirement> => {
  const response = await client.patch<Requirement>(
    `/requirements/${id}/reopen`,
    {}
  );
  return response.data;
};

export const deleteRequirement = async (id: string): Promise<void> => {
  await client.delete(`/requirements/${id}`);
};

export const getRequirementPipeline = async (id: string) => {
  const response = await client.get(`/requirements/${id}/pipeline`);
  return response.data;
};

export const getRequirementStats = async (id: string) => {
  const response = await client.get(`/requirements/${id}/stats`);
  return response.data;
};

export const matchCandidates = async (
  requirementId: string,
  limit?: number
) => {
  const response = await client.get(`/requirements/${requirementId}/match`, {
    params: { limit: limit || 10 },
  });
  return response.data;
};

export const bulkUpdateStatus = async (
  ids: string[],
  status: string
): Promise<void> => {
  await client.post('/requirements/bulk-update', {
    ids,
    status,
  });
};
