'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/Card';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { CountryFlag } from '@/components/ui/CountryFlag';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  Globe,
  TrendingUp,
  BarChart3,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from 'lucide-react';
import { MarketSummary } from '@/types';

export default function MarketIntelligencePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [countryCode, setCountryCode] = useState<string | undefined>();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data: summary, isLoading } = useQuery<MarketSummary>({
    queryKey: ['marketSummary', countryCode],
    queryFn: () => api.getMarketSummary(countryCode),
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
        title="Market Intelligence"
        subtitle="Understand demand patterns and market movements"
        countryCode={countryCode}
        onCountryChange={setCountryCode}
      />

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : summary ? (
        <>
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-radar-100 flex items-center justify-center">
                  <Activity className="w-5 h-5 text-radar-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{summary.total_signals}</p>
                  <p className="text-xs text-gray-500">Raw Signals</p>
                </div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <Globe className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{summary.total_opportunities}</p>
                  <p className="text-xs text-gray-500">Validated Opportunities</p>
                </div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {(summary.avg_intent_score * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-gray-500">Avg Intent Score</p>
                </div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {(summary.avg_confidence * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-gray-500">Avg Confidence</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {/* Top Categories */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-radar-500" />
                Top Categories by Demand
              </h3>
              {(summary.top_categories ?? []).length > 0 ? (
                <div className="space-y-3">
                  {(summary.top_categories ?? []).map((cat, i) => (
                    <div key={cat.category}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {cat.category}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">{cat.count} opps</span>
                          <span className="text-xs font-semibold text-gray-700">
                            {(cat.avg_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                      <ScoreBar
                        value={cat.avg_score}
                        label=""
                        size="sm"
                        color={cat.avg_score > 0.7 ? 'green' : cat.avg_score > 0.4 ? 'yellow' : 'blue'}
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400">No category data yet</p>
              )}
            </Card>

            {/* Emerging Demand */}
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-500" />
                Emerging Demand Signals
              </h3>
              {(summary.emerging_demand ?? []).length > 0 ? (
                <div className="space-y-3">
                  {(summary.emerging_demand ?? []).map((d) => (
                    <div
                      key={`${d.category}-${d.country_code}`}
                      className="p-3 rounded-lg bg-gradient-to-r from-emerald-50/80 to-transparent border border-emerald-100"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CountryFlag code={d.country_code} size="sm" />
                          <span className="text-sm font-semibold text-gray-800 capitalize">
                            {d.category}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                            {d.count} new
                          </span>
                          <span className="text-xs font-semibold text-emerald-800">
                            {(d.avg_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400">No emerging demand yet</p>
              )}
            </Card>
          </div>

          {/* Signals vs Opportunities Distinction */}
          <Card className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">
              Signal Intelligence Pipeline
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {[
                { label: 'Raw Signals', count: summary.total_signals, color: 'bg-gray-100 text-gray-600', icon: '📡' },
                { label: 'Classified', count: Math.floor(summary.total_signals * 0.8), color: 'bg-blue-100 text-blue-600', icon: '🔍' },
                { label: 'Extracted', count: Math.floor(summary.total_signals * 0.6), color: 'bg-indigo-100 text-indigo-600', icon: '📋' },
                { label: 'Validated', count: summary.total_opportunities, color: 'bg-emerald-100 text-emerald-600', icon: '✅' },
                { label: 'High Intent', count: Math.floor(summary.total_opportunities * 0.3), color: 'bg-amber-100 text-amber-600', icon: '⚡' },
              ].map((stage) => (
                <div key={stage.label} className={`p-4 rounded-lg text-center ${stage.color}`}>
                  <p className="text-2xl mb-1">{stage.icon}</p>
                  <p className="text-lg font-bold">{stage.count}</p>
                  <p className="text-xs font-medium">{stage.label}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Market Trends */}
          {(summary.recent_trends ?? []).length > 0 && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-radar-500" />
                Recent Market Trends
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 text-xs font-medium text-gray-500">Market</th>
                      <th className="text-left py-2 text-xs font-medium text-gray-500">Category</th>
                      <th className="text-right py-2 text-xs font-medium text-gray-500">Opportunities</th>
                      <th className="text-right py-2 text-xs font-medium text-gray-500">Avg Intent</th>
                      <th className="text-right py-2 text-xs font-medium text-gray-500">Growth</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(summary.recent_trends ?? []).map((t) => (
                      <tr key={t.id} className="border-b border-gray-50 hover:bg-gray-50">
                        <td className="py-2">
                          <div className="flex items-center gap-2">
                            <CountryFlag code={t.country_code} size="sm" />
                            <span>{t.country_code}</span>
                          </div>
                        </td>
                        <td className="py-2 capitalize">{t.category}</td>
                        <td className="py-2 text-right font-medium">{t.opportunity_count}</td>
                        <td className="py-2 text-right">
                          <span className="font-medium">{(t.avg_intent_score * 100).toFixed(0)}%</span>
                        </td>
                        <td className="py-2 text-right">
                          <span
                            className={
                              t.growth_rate > 0
                                ? 'text-emerald-600 font-medium'
                                : t.growth_rate < 0
                                ? 'text-red-600 font-medium'
                                : 'text-gray-400'
                            }
                          >
                            {t.growth_rate > 0 ? '↑' : t.growth_rate < 0 ? '↓' : '—'}{' '}
                            {Math.abs(t.growth_rate * 100).toFixed(0)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      ) : (
        <EmptyState
          icon={<Globe className="w-12 h-12" />}
          title="No market intelligence available"
          description="Process some signals to generate market intelligence."
        />
      )}
    </AppShell>
  );
}
