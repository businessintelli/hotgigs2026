import client from './client';
import type {
  Referral,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const getReferrals = async (
  params?: FilterParams
): Promise<PaginatedResponse<Referral>> => {
  const response = await client.get<PaginatedResponse<Referral>>(
    '/referrals',
    { params }
  );
  return response.data;
};

export const getReferralById = async (id: string): Promise<Referral> => {
  const response = await client.get<Referral>(`/referrals/${id}`);
  return response.data;
};

export const getReferralsByUser = async (
  userId: string,
  params?: FilterParams
): Promise<PaginatedResponse<Referral>> => {
  const response = await client.get<PaginatedResponse<Referral>>(
    `/users/${userId}/referrals`,
    { params }
  );
  return response.data;
};

export const createReferral = async (data: Partial<Referral>): Promise<Referral> => {
  const response = await client.post<Referral>('/referrals', data);
  return response.data;
};

export const updateReferral = async (
  id: string,
  data: Partial<Referral>
): Promise<Referral> => {
  const response = await client.put<Referral>(`/referrals/${id}`, data);
  return response.data;
};

export const deleteReferral = async (id: string): Promise<void> => {
  await client.delete(`/referrals/${id}`);
};

export const markAsPlaced = async (
  id: string,
  placedDate: string
): Promise<Referral> => {
  const response = await client.post<Referral>(`/referrals/${id}/placed`, {
    placed_at: placedDate,
  });
  return response.data;
};

export const markAsRejected = async (
  id: string,
  reason: string
): Promise<Referral> => {
  const response = await client.post<Referral>(`/referrals/${id}/reject`, {
    reason,
  });
  return response.data;
};

export const withdrawReferral = async (id: string): Promise<Referral> => {
  const response = await client.post<Referral>(`/referrals/${id}/withdraw`, {});
  return response.data;
};

export const getReferralLeaderboard = async () => {
  const response = await client.get('/referrals/leaderboard');
  return response.data;
};

export const getUserReferralStats = async (userId: string) => {
  const response = await client.get(`/users/${userId}/referral-stats`);
  return response.data;
};

export const getBonusHistory = async (
  userId: string,
  params?: FilterParams
): Promise<PaginatedResponse<unknown>> => {
  const response = await client.get<PaginatedResponse<unknown>>(
    `/users/${userId}/bonus-history`,
    { params }
  );
  return response.data;
};

export const requestBonusPayment = async (id: string): Promise<void> => {
  await client.post(`/referrals/${id}/request-payment`, {});
};

export const processBonusPayment = async (referralIds: string[]): Promise<void> => {
  await client.post('/referrals/process-payments', {
    referral_ids: referralIds,
  });
};
