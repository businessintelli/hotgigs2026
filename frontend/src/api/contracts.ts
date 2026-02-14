import client from './client';
import type {
  Contract,
  ContractSigner,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getContracts = async (
  params?: FilterParams
): Promise<PaginatedResponse<Contract>> => {
  const response = await client.get<PaginatedResponse<Contract>>('/contracts', {
    params,
  });
  return response.data;
};

export const getContractById = async (id: string): Promise<Contract> => {
  const response = await client.get<Contract>(`/contracts/${id}`);
  return response.data;
};

export const createContract = async (data: Partial<Contract>): Promise<Contract> => {
  const response = await client.post<Contract>('/contracts', data);
  return response.data;
};

export const updateContract = async (
  id: string,
  data: Partial<Contract>
): Promise<Contract> => {
  const response = await client.put<Contract>(`/contracts/${id}`, data);
  return response.data;
};

export const deleteContract = async (id: string): Promise<void> => {
  await client.delete(`/contracts/${id}`);
};

export const sendForSignature = async (
  id: string,
  signers: Array<{ email: string; name: string }>
): Promise<Contract> => {
  const response = await client.post<Contract>(
    `/contracts/${id}/send-signature`,
    { signers }
  );
  return response.data;
};

export const getSigningStatus = async (id: string): Promise<ContractSigner[]> => {
  const response = await client.get<ContractSigner[]>(
    `/contracts/${id}/signing-status`
  );
  return response.data;
};

export const downloadContractPdf = async (id: string): Promise<Blob> => {
  const response = await client.get(`/contracts/${id}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

export const getContractTemplates = async () => {
  const response = await client.get('/contracts/templates');
  return response.data;
};

export const createFromTemplate = async (
  templateId: string,
  data: Record<string, unknown>
): Promise<Contract> => {
  const response = await client.post<Contract>(
    `/contracts/templates/${templateId}/create`,
    data
  );
  return response.data;
};

export const markAsExpired = async (id: string): Promise<Contract> => {
  const response = await client.patch<Contract>(`/contracts/${id}/expire`, {});
  return response.data;
};
