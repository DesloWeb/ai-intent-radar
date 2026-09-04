'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/Card';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { UrgencyBadge } from '@/components/ui/UrgencyBadge';
import { CountryFlag } from '@/components/ui/CountryFlag';
import { EmptyState } from '@/components/ui/EmptyState';
import { Target, Save, X, Phone, ChevronLeft, ChevronRight } from 'lucide-react';
import { OpportunityListResponse } from '@/types';

export default function OpportunitiesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [countryCode, setCountryCode] = useState<string | undefined>();
  const [category, setCategory] = useState<string | undefined>();
  const [urgency, setUrgency] = useState<string | undefined>();
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data, isLoading } = useQuery<OpportunityListResponse>({
    queryKey: ['opportunities', countryCode, category, urgency, page],
    queryFn: () =>
      api.getOpportunities({
        country_code: countryCode,
        category,
        urgency,
        page,
        per_page: 12,
      }),
    enabled: isAuthenticated,
  });

  const feedbackMutation = useMutation({
    mutationFn: (vars: { opportunity_id: string; feedback_type: string }) =>
      api.submitFeedback(vars),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const totalPages = data ? Math.ceil(data.total / data.per_page) : 0;

  return (
    <AppShell>
      <Header
        title="Opportunities"
        subtitle="Commercial opportunities ranked by intent strength"
        countryCode={countryCode}
        onCountryChange={(c) => { setCountryCode(c); setPage(1); }}
      />

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <select
          value={category || ''}
          onChange={(e) => { setCategory(e.target.value || undefined); setPage(1); }}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white"
        >
          <option value="">All Categories</option>
          <option value="infrastructure">Infrastructure</option>
          <option value="technology">Technology</option>
          <option value="energy">Energy</option>
          <option value="healthcare">Healthcare</option>
          <option value="agriculture">Agriculture</option>
          <option value="education">Education</option>
          <option value="manufacturing">Manufacturing</option>
          <option value="defense">Defense</option>
          <option value="finance">Finance</option>
          <option value="consulting">Consulting</option>
        </select>
        <select
          value={urgency || ''}
          onChange={(e) => { setUrgency(e.target.value || undefined); setPage(1); }}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white"
        >
          <option value="">All Urgency</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        {data && (
          <span className="text-sm text-gray-500 ml-auto">
            {data.total} opportunity{data.total !== 1 ? 'ies' : ''}
          </span>
        )}
      </div>

      {/* Opportunity Cards */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : data && (data.opportunities ?? []).length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {(data.opportunities ?? []).map((opp) => (
              <Card key={opp.id} className="hover:shadow-md transition-shadow cursor-pointer" padding="none">
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <CountryFlag code={opp.country_code} size="sm" />
                      <span className="text-xs font-medium text-gray-500 uppercase">
                        {opp.category}
                      </span>
                    </div>
                    <UrgencyBadge urgency={opp.urgency} size="sm" />
                  </div>
                  <h3
                    className="text-sm font-semibold text-gray-900 line-clamp-2 mb-2 hover:text-radar-600"
                    onClick={() => router.push(`/opportunities/${opp.id}`)}
                  >
                    {opp.title}
                  </h3>
                  <p className="text-xs text-gray-500 line-clamp-2 mb-3">
                    {opp.description}
                  </p>

                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <ScoreBar
                      value={opp.intent_score}
                      label="Intent"
                      size="sm"
                      color={opp.intent_score > 0.7 ? 'green' : opp.intent_score > 0.4 ? 'yellow' : 'blue'}
                    />
                    <ScoreBar
                      value={opp.confidence}
                      label="Confidence"
                      size="sm"
                      color="blue"
                    />
                  </div>

                  {opp.buyer_organization && (
                    <p className="text-xs text-gray-500 mb-3">
                      Buyer: <span className="font-medium">{opp.buyer_organization}</span>
                    </p>
                  )}

                  {opp.estimated_value_max && (
                    <p className="text-xs text-gray-500 mb-3">
                      Est. value: {opp.currency || '$'}{' '}
                      {opp.estimated_value_min
                        ? `${(opp.estimated_value_min / 1000).toFixed(0)}K - `
                        : ''}
                      {(opp.estimated_value_max / 1000).toFixed(0)}K
                    </p>
                  )}
                </div>

                {/* Action buttons */}
                <div className="flex border-t border-gray-100">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      feedbackMutation.mutate({
                        opportunity_id: opp.id,
                        feedback_type: 'saved',
                      });
                    }}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-gray-600 hover:bg-radar-50 hover:text-radar-600 transition-colors"
                  >
                    <Save className="w-3.5 h-3.5" /> Save
                  </button>
                  <div className="w-px bg-gray-100" />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      feedbackMutation.mutate({
                        opportunity_id: opp.id,
                        feedback_type: 'contacted',
                      });
                    }}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-gray-600 hover:bg-emerald-50 hover:text-emerald-600 transition-colors"
                  >
                    <Phone className="w-3.5 h-3.5" /> Contact
                  </button>
                  <div className="w-px bg-gray-100" />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      feedbackMutation.mutate({
                        opportunity_id: opp.id,
                        feedback_type: 'dismissed',
                      });
                    }}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-gray-600 hover:bg-red-50 hover:text-red-500 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" /> Dismiss
                  </button>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      ) : (
        <EmptyState
          icon={<Target className="w-12 h-12" />}
          title="No opportunities found"
          description="Try adjusting your filters or wait for more signals to be processed."
        />
      )}
    </AppShell>
  );
}
