'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Header } from '@/components/layout/Header';
import { StatCard } from '@/components/ui/StatCard';
import { Card } from '@/components/ui/Card';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { UrgencyBadge } from '@/components/ui/UrgencyBadge';
import { CountryFlag } from '@/components/ui/CountryFlag';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  Target,
  TrendingUp,
  Clock,
  Globe,
  Zap,
  BarChart3,
  Activity,
  ArrowRight,
} from 'lucide-react';
import { DashboardResponse } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [countryCode, setCountryCode] = useState<string | undefined>();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data: dashboard, isLoading } = useQuery<DashboardResponse>({
    queryKey: ['dashboard', countryCode],
    queryFn: () => api.getDashboard(countryCode),
    enabled: isAuthenticated,
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
        title="Intelligence Dashboard"
        subtitle="Real-time commercial intent intelligence across your markets"
        countryCode={countryCode}
        onCountryChange={setCountryCode}
      />

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : dashboard ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard
              label="Total Opportunities"
              value={dashboard.total_opportunities}
              icon={<Target className="w-5 h-5" />}
              color="blue"
            />
            <StatCard
              label="High Priority"
              value={dashboard.high_priority_count}
              icon={<Zap className="w-5 h-5" />}
              color="yellow"
            />
            <StatCard
              label="New This Week"
              value={dashboard.new_this_week}
              icon={<Clock className="w-5 h-5" />}
              color="green"
            />
            <StatCard
              label="Markets Active"
              value={dashboard.countries_summary?.length ?? 0}
              icon={<Globe className="w-5 h-5" />}
              color="purple"
            />
          </div>

          {/* Market Summary Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            {/* Intent Distribution */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <Activity className="w-4 h-4 text-radar-500" />
                Intent Distribution
              </h3>
              <div className="space-y-3">
                {Object.entries(dashboard.intent_distribution ?? {}).map(([level, count]) => (
                  <ScoreBar
                    key={level}
                    value={count}
                    max={Math.max(...Object.values(dashboard.intent_distribution ?? {}), 1)}
                    label={`${level.charAt(0).toUpperCase() + level.slice(1)} Intent`}
                    color={level === 'high' ? 'green' : level === 'medium' ? 'yellow' : 'blue'}
                  />
                ))}
              </div>
            </Card>

            {/* Urgency Distribution */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-radar-500" />
                Urgency Breakdown
              </h3>
              <div className="space-y-3">
                {Object.entries(dashboard.urgency_distribution ?? {}).map(([level, count]) => (
                  <div key={level} className="flex items-center justify-between">
                    <UrgencyBadge urgency={level as any} size="sm" />
                    <span className="text-sm font-semibold text-gray-800">{count}</span>
                  </div>
                ))}
                {Object.keys(dashboard.urgency_distribution ?? {}).length === 0 && (
                  <p className="text-xs text-gray-400">No urgency data yet</p>
                )}
              </div>
            </Card>

            {/* Countries */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <Globe className="w-4 h-4 text-radar-500" />
                Market Coverage
              </h3>
              <div className="space-y-3">
                {(dashboard.countries_summary ?? []).map((c) => (
                  <div key={c.country_code} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CountryFlag code={c.country_code} size="sm" />
                      <span className="text-sm text-gray-700">{c.country_code}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-gray-800">{c.total}</span>
                      <span className="text-xs text-gray-400 ml-1">
                        ({(c.avg_intent_score * 100).toFixed(0)}% avg)
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Two-column: Top Opportunities + Emerging Demand */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {/* Top Opportunities */}
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-signal-yellow" />
                  Highest-Priority Opportunities
                </h3>
                <button
                  onClick={() => router.push('/opportunities')}
                  className="text-xs text-radar-600 hover:text-radar-700 font-medium flex items-center gap-1"
                >
                  View all <ArrowRight className="w-3 h-3" />
                </button>
              </div>
              {(dashboard.top_opportunities ?? []).length > 0 ? (
                <div className="space-y-3">
                  {(dashboard.top_opportunities ?? []).slice(0, 5).map((opp) => (
                    <div
                      key={opp.id}
                      className="p-3 rounded-lg border border-gray-100 hover:border-radar-200 hover:bg-radar-50/50 cursor-pointer transition-colors"
                      onClick={() => router.push(`/opportunities/${opp.id}`)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <CountryFlag code={opp.country_code} size="sm" />
                          <span className="text-xs font-medium text-gray-500 uppercase">
                            {opp.category}
                          </span>
                        </div>
                        <UrgencyBadge urgency={opp.urgency} size="sm" />
                      </div>
                      <h4 className="text-sm font-semibold text-gray-800 line-clamp-1">
                        {opp.title}
                      </h4>
                      <div className="flex items-center gap-4 mt-2">
                        <ScoreBar
                          value={opp.intent_score}
                          label="Intent"
                          size="sm"
                          color={opp.intent_score > 0.7 ? 'green' : opp.intent_score > 0.4 ? 'yellow' : 'blue'}
                        />
                      </div>
                      {opp.buyer_organization && (
                        <p className="text-xs text-gray-500 mt-1.5">
                          Buyer: {opp.buyer_organization}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No opportunities yet"
                  description="Opportunities will appear here once signals are processed."
                />
              )}
            </Card>

            {/* Emerging Demand */}
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-signal-green" />
                  Emerging Demand
                </h3>
                <button
                  onClick={() => router.push('/market-intelligence')}
                  className="text-xs text-radar-600 hover:text-radar-700 font-medium flex items-center gap-1"
                >
                  Market intel <ArrowRight className="w-3 h-3" />
                </button>
              </div>
              {(dashboard.emerging_demand ?? []).length > 0 ? (
                <div className="space-y-3">
                  {(dashboard.emerging_demand ?? []).map((d, i) => (
                    <div
                      key={`${d.category}-${d.country_code}`}
                      className="p-3 rounded-lg border border-gray-100 bg-gradient-to-r from-emerald-50/50 to-transparent"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CountryFlag code={d.country_code} size="sm" />
                          <span className="text-sm font-semibold text-gray-800 capitalize">
                            {d.category}
                          </span>
                        </div>
                        <span className="text-xs font-medium text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                          {d.count} new
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <ScoreBar
                          value={d.avg_score}
                          label="Avg intent"
                          size="sm"
                          color="green"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No emerging demand yet"
                  description="Market intelligence will appear as signals are processed."
                />
              )}
            </Card>
          </div>

          {/* Market Trends */}
          {(dashboard.market_trends ?? []).length > 0 && (
            <Card className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-radar-500" />
                Market Trends (7 days)
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {(dashboard.market_trends ?? []).map((t, i) => (
                  <div
                    key={`${t.category}-${t.country_code}`}
                    className="p-3 rounded-lg bg-gray-50 text-center"
                  >
                    <CountryFlag code={t.country_code} size="sm" />
                    <p className="text-xs font-medium text-gray-700 capitalize mt-1">
                      {t.category}
                    </p>
                    <p className="text-lg font-bold text-gray-900 mt-1">{t.count}</p>
                    <p className="text-[10px] text-gray-400">opportunities</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      ) : null}
    </AppShell>
  );
}
