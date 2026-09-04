'use client';

import { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Card } from '@/components/ui/Card';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { UrgencyBadge } from '@/components/ui/UrgencyBadge';
import { CountryFlag } from '@/components/ui/CountryFlag';
import {
  ArrowLeft,
  Save,
  X,
  Phone,
  Trophy,
  ThumbsDown,
  Target,
  Clock,
  DollarSign,
  Users,
  MapPin,
  Lightbulb,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';
import { Opportunity, ProviderMatch } from '@/types';

export default function OpportunityDetailPage() {
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const id = params.id as string;

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data: opp, isLoading } = useQuery<Opportunity>({
    queryKey: ['opportunity', id],
    queryFn: () => api.getOpportunity(id),
    enabled: isAuthenticated && !!id,
  });

  const { data: matches } = useQuery<ProviderMatch[]>({
    queryKey: ['matches', id],
    queryFn: () => api.getMatches(id),
    enabled: isAuthenticated && !!id,
  });

  const feedbackMutation = useMutation({
    mutationFn: (vars: { opportunity_id: string; feedback_type: string }) =>
      api.submitFeedback(vars),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunity', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const matchMutation = useMutation({
    mutationFn: () => api.matchOpportunity(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches', id] });
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
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft className="w-4 h-4" /> Back to opportunities
      </button>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : opp ? (
        <div className="max-w-4xl">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <CountryFlag code={opp.country_code} size="lg" />
              <span className="text-sm font-medium text-gray-500 uppercase bg-gray-100 px-2 py-0.5 rounded">
                {opp.category}
              </span>
              <UrgencyBadge urgency={opp.urgency} />
              <span className="text-xs font-medium text-gray-400 bg-gray-50 px-2 py-0.5 rounded">
                {opp.status}
              </span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{opp.title}</h1>
            <p className="text-sm text-gray-600 leading-relaxed">{opp.description}</p>
          </div>

          {/* Score Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">
                  {(opp.intent_score * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">Intent Score</p>
                <ScoreBar
                  value={opp.intent_score}
                  label=""
                  color={opp.intent_score > 0.7 ? 'green' : opp.intent_score > 0.4 ? 'yellow' : 'blue'}
                  size="md"
                />
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">
                  {(opp.confidence * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">Confidence</p>
                <ScoreBar value={opp.confidence} label="" color="blue" size="md" />
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <UrgencyBadge urgency={opp.urgency} />
                <p className="text-xs text-gray-500 mt-2">Urgency Level</p>
              </div>
            </Card>
          </div>

          {/* Why Now */}
          {opp.why_now && (
            <Card className="mb-6 bg-gradient-to-r from-radar-50 to-white border-radar-200">
              <div className="flex items-start gap-3">
                <Lightbulb className="w-5 h-5 text-radar-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-semibold text-radar-800 mb-1">Why Now?</h3>
                  <p className="text-sm text-radar-700 leading-relaxed">{opp.why_now}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Buyer Info */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <Users className="w-4 h-4" /> Buyer Information
              </h3>
              <div className="space-y-2">
                {opp.buyer_organization && (
                  <div>
                    <p className="text-xs text-gray-500">Organization</p>
                    <p className="text-sm font-medium text-gray-800">{opp.buyer_organization}</p>
                  </div>
                )}
                {opp.buyer_name && (
                  <div>
                    <p className="text-xs text-gray-500">Contact</p>
                    <p className="text-sm font-medium text-gray-800">{opp.buyer_name}</p>
                  </div>
                )}
                {opp.location && (
                  <div>
                    <p className="text-xs text-gray-500">Location</p>
                    <p className="text-sm font-medium text-gray-800 flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> {opp.location}
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {/* Value & Timeline */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <DollarSign className="w-4 h-4" /> Value & Timeline
              </h3>
              <div className="space-y-2">
                {(opp.estimated_value_min || opp.estimated_value_max) && (
                  <div>
                    <p className="text-xs text-gray-500">Estimated Value</p>
                    <p className="text-sm font-medium text-gray-800">
                      {opp.currency || '$'}{' '}
                      {opp.estimated_value_min
                        ? `${(opp.estimated_value_min / 1000).toFixed(0)}K`
                        : '?'}{' '}
                      -{' '}
                      {opp.estimated_value_max
                        ? `${(opp.estimated_value_max / 1000).toFixed(0)}K`
                        : '?'}
                    </p>
                  </div>
                )}
                {opp.deadline && (
                  <div>
                    <p className="text-xs text-gray-500">Deadline</p>
                    <p className="text-sm font-medium text-gray-800 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(opp.deadline).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Recommended Action */}
          {opp.recommended_action && (
            <Card className="mb-6 bg-gradient-to-r from-emerald-50 to-white border-emerald-200">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-semibold text-emerald-800 mb-1">Recommended Action</h3>
                  <p className="text-sm text-emerald-700 leading-relaxed">{opp.recommended_action}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Evidence */}
          {opp.evidence && (opp.evidence ?? []).length > 0 && (
            <Card className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <ExternalLink className="w-4 h-4" /> Evidence & Sources
              </h3>
              <div className="space-y-2">
                {(opp.evidence ?? []).map((e, i) => (
                  <div key={i} className="p-2 bg-gray-50 rounded text-xs text-gray-600">
                    {e}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Requirements */}
          {opp.requirements && (opp.requirements ?? []).length > 0 && (
            <Card className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Requirements</h3>
              <ul className="space-y-1">
                {(opp.requirements ?? []).map((r, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-radar-500 mt-1">•</span> {r}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Provider Matches */}
          <Card className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <Target className="w-4 h-4" /> Provider Matches
              </h3>
              <button
                onClick={() => matchMutation.mutate()}
                disabled={matchMutation.isPending}
                className="text-xs bg-radar-600 hover:bg-radar-700 text-white px-3 py-1.5 rounded-lg font-medium disabled:opacity-50"
              >
                {matchMutation.isPending ? 'Matching...' : 'Run Matching'}
              </button>
            </div>
            {matches && (matches ?? []).length > 0 ? (
              <div className="space-y-3">
                {(matches ?? []).map((m) => (
                  <div key={m.id} className="p-3 rounded-lg border border-gray-100 bg-gray-50">
                    <div className="grid grid-cols-4 gap-2 mb-2">
                      <ScoreBar value={m.service_fit} label="Service" size="sm" color="green" />
                      <ScoreBar value={m.geographic_fit} label="Geographic" size="sm" color="blue" />
                      <ScoreBar value={m.project_size_fit} label="Size" size="sm" color="yellow" />
                      <div className="text-center">
                        <p className="text-lg font-bold text-gray-800">{(m.total_score * 100).toFixed(0)}%</p>
                        <p className="text-[10px] text-gray-400">Total</p>
                      </div>
                    </div>
                    {m.reasoning && (
                      <p className="text-xs text-gray-600 mt-1">{m.reasoning}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-400">
                No matches yet. Click &quot;Run Matching&quot; to match providers.
              </p>
            )}
          </Card>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => feedbackMutation.mutate({ opportunity_id: id, feedback_type: 'saved' })}
              className="flex items-center gap-2 px-4 py-2.5 bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <Save className="w-4 h-4" /> Save Opportunity
            </button>
            <button
              onClick={() => feedbackMutation.mutate({ opportunity_id: id, feedback_type: 'contacted' })}
              className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <Phone className="w-4 h-4" /> Mark as Contacted
            </button>
            <button
              onClick={() => feedbackMutation.mutate({ opportunity_id: id, feedback_type: 'won' })}
              className="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <Trophy className="w-4 h-4" /> Won
            </button>
            <button
              onClick={() => feedbackMutation.mutate({ opportunity_id: id, feedback_type: 'lost' })}
              className="flex items-center gap-2 px-4 py-2.5 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <ThumbsDown className="w-4 h-4" /> Lost
            </button>
            <button
              onClick={() => feedbackMutation.mutate({ opportunity_id: id, feedback_type: 'dismissed' })}
              className="flex items-center gap-2 px-4 py-2.5 border border-gray-300 hover:bg-red-50 hover:text-red-600 text-sm font-medium rounded-lg transition-colors"
            >
              <X className="w-4 h-4" /> Dismiss
            </button>
          </div>
        </div>
      ) : null}
    </AppShell>
  );
}
