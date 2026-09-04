'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/Card';
import { CountryFlag } from '@/components/ui/CountryFlag';
import { EmptyState } from '@/components/ui/EmptyState';
import { Users, Plus, X, MapPin, Briefcase, Globe } from 'lucide-react';
import { Provider } from '@/types';

export default function ProvidersPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [showCreate, setShowCreate] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [services, setServices] = useState('');
  const [categories, setCategories] = useState('');
  const [locations, setLocations] = useState('');
  const [countryCodes, setCountryCodes] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data: providers, isLoading } = useQuery<Provider[]>({
    queryKey: ['providers'],
    queryFn: () => api.getProviders(),
    enabled: isAuthenticated,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      api.createProvider({
        name,
        description: description || undefined,
        services: services.split(',').map((s) => s.trim()).filter(Boolean),
        categories: categories.split(',').map((s) => s.trim()).filter(Boolean),
        locations: locations.split(',').map((s) => s.trim()).filter(Boolean),
        country_codes: countryCodes.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      setShowCreate(false);
      setName('');
      setDescription('');
      setServices('');
      setCategories('');
      setLocations('');
      setCountryCodes('');
    },
  });

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <AppShell>
      <Header
        title="Providers"
        subtitle="Manage businesses that can act on opportunities"
      />

      <div className="flex items-center justify-between mb-6">
        <span className="text-sm text-gray-500">
          {providers?.length || 0} provider{(providers?.length || 0) !== 1 ? 's' : ''}
        </span>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-2 bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {showCreate ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showCreate ? 'Cancel' : 'Add Provider'}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <Card className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">New Provider</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="Acme Corp"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="Technology consulting firm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Categories (comma-separated)
              </label>
              <input
                type="text"
                value={categories}
                onChange={(e) => setCategories(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="technology, infrastructure, energy"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Services (comma-separated)
              </label>
              <input
                type="text"
                value={services}
                onChange={(e) => setServices(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="cloud_migration, cybersecurity, consulting"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Locations (comma-separated)
              </label>
              <input
                type="text"
                value={locations}
                onChange={(e) => setLocations(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="New York, Washington DC, San Francisco"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Country Codes (comma-separated)
              </label>
              <input
                type="text"
                value={countryCodes}
                onChange={(e) => setCountryCodes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="US"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => createMutation.mutate()}
              disabled={!name || createMutation.isPending}
              className="bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Provider'}
            </button>
          </div>
          {createMutation.isError && (
            <p className="text-sm text-red-600 mt-2">{createMutation.error.message}</p>
          )}
        </Card>
      )}

      {/* Providers List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : providers && (providers ?? []).length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(providers ?? []).map((p) => (
            <Card key={p.id}>
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-radar-100 flex items-center justify-center">
                  <Briefcase className="w-5 h-5 text-radar-600" />
                </div>
                {p.country_codes && (p.country_codes ?? []).length > 0 && (
                  <div className="flex gap-1">
                    {(p.country_codes ?? []).map((c) => (
                      <CountryFlag key={c} code={c} size="sm" />
                    ))}
                  </div>
                )}
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">{p.name}</h3>
              {p.description && (
                <p className="text-xs text-gray-500 line-clamp-2 mb-3">{p.description}</p>
              )}

              {p.categories && (p.categories ?? []).length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {(p.categories ?? []).map((c) => (
                    <span
                      key={c}
                      className="text-[10px] font-medium bg-radar-50 text-radar-700 px-1.5 py-0.5 rounded"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              )}

              {p.locations && (p.locations ?? []).length > 0 && (
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <MapPin className="w-3 h-3" />
                  {p.locations.join(', ')}
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Users className="w-12 h-12" />}
          title="No providers yet"
          description="Add providers to enable automatic opportunity matching."
          action={
            <button
              onClick={() => setShowCreate(true)}
              className="bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
            >
              Add First Provider
            </button>
          }
        />
      )}
    </AppShell>
  );
}
