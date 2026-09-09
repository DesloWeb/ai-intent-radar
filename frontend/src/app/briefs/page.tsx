'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  ExternalLink,
  Mail,
  Copy,
} from 'lucide-react';
import type { Brief } from '@/types';

function StatusBadge({ status }: { status: string }) {
  if (status === 'interested') {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-semibold bg-emerald-100 text-emerald-700 px-2.5 py-1 rounded-full">
        <CheckCircle className="w-3.5 h-3.5" /> Interested
      </span>
    );
  }
  if (status === 'not_interested') {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-semibold bg-red-100 text-red-600 px-2.5 py-1 rounded-full">
        <XCircle className="w-3.5 h-3.5" /> Not Interested
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium bg-yellow-100 text-yellow-700 px-2.5 py-1 rounded-full">
      <Clock className="w-3.5 h-3.5" /> Pending
    </span>
  );
}

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  const hrs = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 60) return `${mins}m ago`;
  if (hrs < 24) return `${hrs}h ago`;
  return `${days}d ago`;
}

function isExpired(expiresAt: string) {
  return new Date(expiresAt) < new Date();
}

export default function BriefsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [copied, setCopied] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'interested' | 'not_interested'>('all');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const { data: briefs = [], isLoading } = useQuery<Brief[], Error>({
    queryKey: ['briefs'],
    queryFn: () => api.getBriefs(),
    enabled: isAuthenticated,
    refetchInterval: 30000,
  });

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const filtered = filter === 'all' ? briefs : briefs.filter((b: Brief) => b.status === filter);

  const counts = {
    all: briefs.length,
    pending: briefs.filter((b: Brief) => b.status === 'pending').length,
    interested: briefs.filter((b: Brief) => b.status === 'interested').length,
    not_interested: briefs.filter((b: Brief) => b.status === 'not_interested').length,
  };

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Provider Briefs</h1>
        <p className="text-sm text-gray-500 mt-1">
          Track all shareable briefs you&apos;ve sent to providers and their responses.
        </p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {([
          { key: 'all', label: 'Total Sent', color: 'bg-gray-50 border-gray-200 text-gray-700' },
          { key: 'pending', label: 'Awaiting Response', color: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
          { key: 'interested', label: 'Interested', color: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
          { key: 'not_interested', label: 'Not Interested', color: 'bg-red-50 border-red-200 text-red-600' },
        ] as const).map(({ key, label, color }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`p-4 rounded-xl border text-left transition-all ${color} ${
              filter === key ? 'ring-2 ring-offset-1 ring-radar-400' : 'hover:opacity-80'
            }`}
          >
            <p className="text-2xl font-bold">{counts[key]}</p>
            <p className="text-xs font-medium mt-0.5">{label}</p>
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title={filter === 'all' ? 'No briefs yet' : `No ${filter.replace('_', ' ')} briefs`}
          description={
            filter === 'all'
              ? 'Generate a brief from an opportunity\'s provider matches to share with providers.'
              : 'No briefs with this status yet.'
          }
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((brief: Brief) => {
            const expired = isExpired(brief.expires_at);
            return (
              <Card key={brief.id} className={expired && brief.status === 'pending' ? 'opacity-60' : ''}>
                <div className="flex items-start justify-between gap-4">
                  {/* Left: opportunity + status */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                      <StatusBadge status={brief.status} />
                      {expired && brief.status === 'pending' && (
                        <span className="text-[11px] font-medium text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                          Expired
                        </span>
                      )}
                      <span className="text-[11px] text-gray-400 flex items-center gap-1">
                        <Eye className="w-3 h-3" />
                        {brief.view_count} view{brief.view_count !== 1 ? 's' : ''}
                      </span>
                      <span className="text-[11px] text-gray-400">· Sent {timeAgo(brief.created_at)}</span>
                    </div>

                    {/* Opportunity title */}
                    <button
                      onClick={() => router.push(`/opportunities/${brief.opportunity_id}`)}
                      className="text-sm font-semibold text-gray-800 hover:text-radar-600 text-left line-clamp-1 mb-1"
                    >
                      {brief.opportunity_title || 'View Opportunity →'}
                    </button>

                    {/* Provider response details */}
                    {brief.status !== 'pending' && (
                      <div className="mt-2 p-3 rounded-lg bg-gray-50 border border-gray-100 space-y-1">
                        {brief.provider_name && (
                          <p className="text-xs font-medium text-gray-700">
                            {brief.provider_name}
                          </p>
                        )}
                        {brief.provider_email && (
                          <a
                            href={`mailto:${brief.provider_email}`}
                            className="text-xs text-radar-600 hover:underline flex items-center gap-1"
                          >
                            <Mail className="w-3 h-3" />
                            {brief.provider_email}
                          </a>
                        )}
                        {brief.provider_message && (
                          <p className="text-xs text-gray-600 italic mt-1">
                            &ldquo;{brief.provider_message}&rdquo;
                          </p>
                        )}
                        {brief.responded_at && (
                          <p className="text-[11px] text-gray-400">
                            Responded {timeAgo(brief.responded_at)}
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Right: actions */}
                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    <button
                      onClick={async () => {
                        await navigator.clipboard.writeText(brief.public_url);
                        setCopied(brief.id);
                        setTimeout(() => setCopied(null), 2000);
                      }}
                      className="flex items-center gap-1 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 px-2.5 py-1.5 rounded-lg transition-colors"
                    >
                      {copied === brief.id ? (
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                      {copied === brief.id ? 'Copied!' : 'Copy Link'}
                    </button>
                    <a
                      href={brief.public_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs font-medium text-radar-600 hover:text-radar-700 px-2.5 py-1.5 rounded-lg hover:bg-radar-50 transition-colors"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      Preview
                    </a>
                    <p className="text-[10px] text-gray-400">
                      Expires {new Date(brief.expires_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
