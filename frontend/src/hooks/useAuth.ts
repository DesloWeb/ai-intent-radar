'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { User } from '@/types';

export function useAuth() {
  const queryClient = useQueryClient();
  const router = useRouter();

  const userQuery = useQuery<User>({
    queryKey: ['user'],
    queryFn: () => api.getMe(),
    enabled: typeof window !== 'undefined' && !!localStorage.getItem('access_token'),
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      api.login(email, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
      router.push('/dashboard');
    },
  });

  const registerMutation = useMutation({
    mutationFn: ({
      email,
      password,
      fullName,
      orgSlug,
    }: {
      email: string;
      password: string;
      fullName: string;
      orgSlug?: string;
    }) => api.register(email, password, fullName, orgSlug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
      router.push('/dashboard');
    },
  });

  const logout = () => {
    api.clearTokens();
    queryClient.clear();
    router.push('/auth/login');
  };

  return {
    user: userQuery.data,
    isLoading: userQuery.isLoading,
    isAuthenticated: !!userQuery.data,
    login: loginMutation,
    register: registerMutation,
    logout,
  };
}
