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
import {
  Users, Plus, X, MapPin, Briefcase, User, BadgeCheck,
  Clock, DollarSign, ChevronDown, ChevronUp,
} from 'lucide-react';
import { Provider } from '@/types';

type ProviderTab = 'all' | 'business' | 'individual';

const AVAILABILITY_LABELS: Record<string, string> = {
  full_time: 'Full-time',
  part_time: 'Part-time',
  contract: 'Contract',
  weekends: 'Weekends',
};

export default function ProvidersPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [tab, setTab] = useState<ProviderTab>('all');
  const [showCreate, setShowCreate] = useState(false);
  const [providerType, setProviderType] = useState<'business' | 'individual'>('business');

  // Shared form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [locations, setLocations] = useState('');

  // Business-specific
  const [services, setServices] = useState('');
  const [categories, setCategories] = useState('');
  const [minValue, setMinValue] = useState('');
  const [maxValue, setMaxValue] = useState('');

  // Individual-specific
  const [skills, setSkills] = useState('');
  const [rateMin, setRateMin] = useState('');
  const [rateMax, setRateMax] = useState('');
  const [availability, setAvailability] = useState('');
  const [profileUrl, setProfileUrl] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data: providers, isLoading } = useQuery<Provider[]>({
    queryKey: ['providers', tab],
    queryFn: () => api.getProviders(tab === 'all' ? undefined : tab),
    enabled: isAuthenticated,
  });

  const resetForm = () => {
    setName(''); setDescription(''); setLocations('');
    setServices(''); setCategories(''); setMinValue(''); setMaxValue('');
    setSkills(''); setRateMin(''); setRateMax(''); setAvailability(''); setProfileUrl('');
    setProviderType('business');
  };

  const createMutation = useMutation({
    mutationFn: () => {
      const base = {
        provider_type: providerType,
        name,
        description: description || undefined,
        locations: locations.split(',').map((s) => s.trim()).filter(Boolean),
        country_codes: ['US'],
      };
      if (providerType === 'business') {
        return api.createProvider({
          ...base,
          services: services.split(',').map((s) => s.trim()).filter(Boolean),
          categories: categories.split(',').map((s) => s.trim()).filter(Boolean),
          min_project_value: minValue ? parseFloat(minValue) : undefined,
          max_project_value: maxValue ? parseFloat(maxValue) : undefined,
        });
      } else {
        return api.createProvider({
          ...base,
          skills: skills.split(',').map((s) => s.trim()).filter(Boolean),
          hourly_rate_min: rateMin ? parseFloat(rateMin) : undefined,
          hourly_rate_max: rateMax ? parseFloat(rateMax) : undefined,
          availability: availability || undefined,
          profile_url: profileUrl || undefined,
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      setShowCreate(false);
      resetForm();
    },
  });

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const businessCount = providers?.filter((p) => p.provider_type === 'business').length ?? 0;
  const individualCount = providers?.filter((p) => p.provider_type === 'individual').length ?? 0;

  return (
    <AppShell>
      <Header
        title="Providers"
        subtitle="Businesses and individuals that can act on opportunities"
      />

      {/* Tabs + Add button */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          {(['all', 'business', 'individual'] as ProviderTab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
                tab === t
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t === 'all'
                ? `All (${(providers?.length ?? 0)})`
                : t === 'business'
                ? `Businesses (${businessCount})`
                : `Individuals (${individualCount})`}
            </button>
          ))}
        </div>
        <button
          onClick={() => { setShowCreate(!showCreate); resetForm(); }}
          className="flex items-center gap-2 bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {showCreate ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showCreate ? 'Cancel' : 'Add Provider'}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <Card className="mb-6">
          {/* Type toggle */}
          <div className="flex items-center gap-2 mb-5">
            <span className="text-sm font-medium text-gray-600">Type:</span>
            <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setProviderType('business')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  providerType === 'business'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Briefcase className="w-3.5 h-3.5" /> Business
              </button>
              <button
                onClick={() => setProviderType('individual')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  providerType === 'individual'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <User className="w-3.5 h-3.5" /> Individual
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Shared fields */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                {providerType === 'individual' ? 'Full Name *' : 'Business Name *'}
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder={providerType === 'individual' ? 'Jane Smith' : 'Acme Corp'}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder={
                  providerType === 'individual'
                    ? 'Senior DevOps engineer, 8 years experience'
                    : 'Technology consulting firm'
                }
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
                placeholder="Austin TX, Remote"
              />
            </div>

            {/* Business-specific */}
            {providerType === 'business' && (
              <>
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
                    Min Project Value ($)
                  </label>
                  <input
                    type="number"
                    value={minValue}
                    onChange={(e) => setMinValue(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    placeholder="10000"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Max Project Value ($)
                  </label>
                  <input
                    type="number"
                    value={maxValue}
                    onChange={(e) => setMaxValue(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    placeholder="500000"
                  />
                </div>
              </>
            )}

            {/* Individual-specific */}
            {providerType === 'individual' && (
              <>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Skills (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    placeholder="python, devops, kubernetes, aws"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Hourly Rate Min ($)
                  </label>
                  <input
                    type="number"
                    value={rateMin}
                    onChange={(e) => setRateMin(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    placeholder="75"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Hourly Rate Max ($)
                  </label>
                  <input
                    type="number"
                    value={rateMax}
                    onChange={(e) => setRateMax(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    placeholder="150"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Availability
                  </label>
                  <select
                    value={availability}
                    onChange={(e) => setAvailability(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white"
                  >
                    <option value="">Select availability</option>
                    <option value="full_time">Full-time</option>
                    <option value="part_time">Part-time</option>
                    <option value="contract">Contract</option>
                    <option value="weekends">Weekends</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Profile URL (LinkedIn, portfolio, etc.)
                  </label>
                  <input
                    type="url"
                    value={profileUrl}
                    onChange={(e) => setProfileUrl(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    placeholder="https://linkedin.com/in/yourprofile"
                  />
                </div>
              </>
            )}
          </div>

          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={() => { setShowCreate(false); resetForm(); }}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => createMutation.mutate()}
              disabled={!name || createMutation.isPending}
              className="bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
            >
              {createMutation.isPending ? 'Adding...' : `Add ${providerType === 'business' ? 'Business' : 'Individual'}`}
            </button>
          </div>
          {createMutation.isError && (
            <p className="text-sm text-red-600 mt-2">{(createMutation.error as Error).message}</p>
          )}
        </Card>
      )}

      {/* Provider List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : providers && providers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map((p) =>
            p.provider_type === 'individual'
              ? <IndividualCard key={p.id} provider={p} />
              : <BusinessCard key={p.id} provider={p} />
          )}
        </div>
      ) : (
        <EmptyState
          icon={<Users className="w-12 h-12" />}
          title="No providers yet"
          description="Add businesses or individuals to enable automatic opportunity matching."
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

// ---------------------------------------------------------------------------
// Business card
// ---------------------------------------------------------------------------

function BusinessCard({ provider: p }: { provider: Provider }) {
  return (
    <Card>
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg bg-radar-100 flex items-center justify-center">
          <Briefcase className="w-5 h-5 text-radar-600" />
        </div>
        <div className="flex items-center gap-1">
          {(p.country_codes ?? []).map((c) => (
            <CountryFlag key={c} code={c} size="sm" />
          ))}
        </div>
      </div>
      <h3 className="text-sm font-semibold text-gray-900 mb-1">{p.name}</h3>
      {p.description && (
        <p className="text-xs text-gray-500 line-clamp-2 mb-3">{p.description}</p>
      )}
      {(p.categories ?? []).length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {(p.categories ?? []).map((c) => (
            <span key={c} className="text-[10px] font-medium bg-radar-50 text-radar-700 px-1.5 py-0.5 rounded">
              {c}
            </span>
          ))}
        </div>
      )}
      {(p.locations ?? []).length > 0 && (
        <div className="flex items-center gap-1 text-xs text-gray-500 mt-2">
          <MapPin className="w-3 h-3 flex-shrink-0" />
          {p.locations.join(', ')}
        </div>
      )}
      {(p.min_project_value || p.max_project_value) && (
        <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
          <DollarSign className="w-3 h-3 flex-shrink-0" />
          {p.min_project_value
            ? `$${(p.min_project_value / 1000).toFixed(0)}K`
            : 'No min'}{' '}
          —{' '}
          {p.max_project_value
            ? `$${(p.max_project_value / 1000).toFixed(0)}K`
            : 'No max'}
        </div>
      )}
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Individual card
// ---------------------------------------------------------------------------

function IndividualCard({ provider: p }: { provider: Provider }) {
  return (
    <Card>
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
          <User className="w-5 h-5 text-emerald-600" />
        </div>
        <div className="flex items-center gap-2">
          {p.verified && (
            <span className="flex items-center gap-0.5 text-[10px] font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded-full">
              <BadgeCheck className="w-3 h-3" /> Verified
            </span>
          )}
          {(p.country_codes ?? []).map((c) => (
            <CountryFlag key={c} code={c} size="sm" />
          ))}
        </div>
      </div>
      <h3 className="text-sm font-semibold text-gray-900 mb-1">{p.name}</h3>
      {p.description && (
        <p className="text-xs text-gray-500 line-clamp-2 mb-3">{p.description}</p>
      )}
      {(p.skills ?? []).length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {(p.skills ?? []).map((s) => (
            <span key={s} className="text-[10px] font-medium bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded">
              {s}
            </span>
          ))}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-3 mt-2">
        {(p.hourly_rate_min || p.hourly_rate_max) && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <DollarSign className="w-3 h-3 flex-shrink-0" />
            {p.hourly_rate_min && p.hourly_rate_max
              ? `$${p.hourly_rate_min}–$${p.hourly_rate_max}/hr`
              : p.hourly_rate_min
              ? `From $${p.hourly_rate_min}/hr`
              : `Up to $${p.hourly_rate_max}/hr`}
          </div>
        )}
        {p.availability && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="w-3 h-3 flex-shrink-0" />
            {AVAILABILITY_LABELS[p.availability] ?? p.availability}
          </div>
        )}
        {(p.locations ?? []).length > 0 && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <MapPin className="w-3 h-3 flex-shrink-0" />
            {p.locations.join(', ')}
          </div>
        )}
      </div>
      {p.profile_url && (
        <a
          href={p.profile_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block mt-2 text-xs text-radar-600 hover:text-radar-700 truncate"
        >
          {p.profile_url}
        </a>
      )}
    </Card>
  );
}
