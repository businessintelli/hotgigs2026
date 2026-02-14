import client from './client';
import type {
  Supplier,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getSuppliers = async (
  params?: FilterParams
): Promise<PaginatedResponse<Supplier>> => {
  const response = await client.get<PaginatedResponse<Supplier>>(
    '/suppliers',
    { params }
  );
  return response.data;
};

export const getSupplierById = async (id: string): Promise<Supplier> => {
  const response = await client.get<Supplier>(`/suppliers/${id}`);
  return response.data;
};

export const createSupplier = async (
  data: Partial<Supplier>
): Promise<Supplier> => {
  const response = await client.post<Supplier>('/suppliers', data);
  return response.data;
};

export const updateSupplier = async (
  id: string,
  data: Partial<Supplier>
): Promise<Supplier> => {
  const response = await client.put<Supplier>(`/suppliers/${id}`, data);
  return response.data;
};

export const deleteSupplier = async (id: string): Promise<void> => {
  await client.delete(`/suppliers/${id}`);
};

export const getSupplierPerformance = async (id: string) => {
  const response = await client.get(`/suppliers/${id}/performance`);
  return response.data;
};

export const getSupplierRevenue = async (id: string) => {
  const response = await client.get(`/suppliers/${id}/revenue`);
  return response.data;
};

export const getSupplierPlacements = async (
  id: string,
  params?: FilterParams
): Promise<PaginatedResponse<unknown>> => {
  const response = await client.get<PaginatedResponse<unknown>>(
    `/suppliers/${id}/placements`,
    { params }
  );
  return response.data;
};

export const updateSupplierTier = async (
  id: string,
  tier: 'preferred' | 'standard' | 'managed'
): Promise<Supplier> => {
  const response = await client.patch<Supplier>(`/suppliers/${id}/tier`, { tier });
  return response.data;
};

export const getSupplierCommissionStatement = async (id: string) => {
  const response = await client.get(`/suppliers/${id}/commission-statement`);
  return response.data;
};

export const markSupplierAsActive = async (id: string): Promise<Supplier> => {
  const response = await client.patch<Supplier>(`/suppliers/${id}/activate`, {});
  return response.data;
};

export const markSupplierAsInactive = async (id: string): Promise<Supplier> => {
  const response = await client.patch<Supplier>(`/suppliers/${id}/deactivate`, {});
  return response.data;
};
