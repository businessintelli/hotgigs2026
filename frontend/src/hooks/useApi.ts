import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import type { ApiError } from '@/types';

interface UseApiOptions {
  enabled?: boolean;
  retry?: number;
  staleTime?: number;
  cacheTime?: number;
}

export const useApi = <TData, TError = ApiError>(
  key: string | string[],
  queryFn: () => Promise<TData>,
  options?: UseApiOptions
) => {
  return useQuery({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn,
    enabled: options?.enabled !== false,
    retry: options?.retry ?? 1,
    staleTime: options?.staleTime ?? 5 * 60 * 1000,
    gcTime: options?.cacheTime ?? 10 * 60 * 1000,
  });
};

interface UseMutationOptions<TData> {
  onSuccess?: (data: TData) => void;
  onError?: (error: AxiosError<ApiError>) => void;
}

export const useApiMutation = <
  TData = unknown,
  TVariables = unknown,
  TError = AxiosError<ApiError>,
>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: UseMutationOptions<TData>
) => {
  const queryClient = useQueryClient();

  return useMutation<TData, TError, TVariables>({
    mutationFn,
    onSuccess: (data) => {
      queryClient.invalidateQueries();
      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
};

export const useInvalidateQueries = () => {
  const queryClient = useQueryClient();

  return {
    invalidateAll: () => queryClient.invalidateQueries(),
    invalidate: (key: string | string[]) => {
      queryClient.invalidateQueries({
        queryKey: Array.isArray(key) ? key : [key],
      });
    },
  };
};
