'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { PublicBrief } from '@/types';
import {
  Radar,
  Target,
  Zap,
  Clock,
  DollarSign,
  MapPin,
  Lightbulb,
  CheckCircle,
  ExternalLink,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  Send,
} from 'lucide-react';
import Link from 'next/link';

const URGENCY_COLORS: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
};

export default function PublicBriefPage() {
  const params = useParams();
  const token = params.token as string;
  const [action, setAction] = useState<'interested' | 'not_interested' | null>(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const { data: brief, isLoading, error } = useQuery<PublicBrief>({
    queryKey: ['brief', token],
    queryFn: () => api.getPublicBrief(token),
    retry: false,
  });

  const respondMutation = useMutation({
    mutationFn: (vars: { action: 'interested' | 'not_interested'; name?: string; email?: string; message?: string }) =>
      api.respondToBrief(token, {
        action: vars.action,
        provider_name: vars.name,
        provider_email: vars.email,
        message: vars.message || undefined,
      }),
    onSuccess: (_data, vars) => {
      setAction(vars.action);
      setSubmitted(true);
    },
  });

  const alreadyNotInterested = brief?.status === 'not_interested';
  const isNotInterested = action === 'not_interested' || alreadyNotInterested;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-radar-950 via-radar-900 to-radar-950 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error || !brief) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-radar-950 via-radar-900 to-radar-950 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-gray-900 mb-2">Brief Not Found</h1>
          <p className="text-sm text-gray-500">
            This brief may have expired or the link is invalid. Please contact the sender for a new link.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-radar-950 to-radar-900 text-white px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-radar-500 rounded-lg flex items-center justify-center">
              <Radar className="w-4 h-4" />
            </div>
            <div>
              <p className="text-sm font-bold">Intent Radar</p>
              <p className="text-[10px] text-radar-300 uppercase tracking-wide">Opportunity Brief</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-radar-300">Expires</p>
            <p className="text-xs font-medium">
              {new Date(brief.expires_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">

        {/* Provider greeting */}
        {brief.provider_name && (
          <div className="bg-radar-50 border border-radar-200 rounded-xl px-5 py-4">
            <p className="text-sm text-radar-800">
              <span className="font-semibold">{brief.provider_name}</span> — you've been matched to this opportunity based on your profile.
            </p>
          </div>
        )}

        {/* Opportunity header */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-500 uppercase bg-gray-100 px-2 py-0.5 rounded">
                {brief.opportunity_category}
              </span>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${URGENCY_COLORS[brief.opportunity_urgency] || URGENCY_COLORS.medium}`}>
                {brief.opportunity_urgency.charAt(0).toUpperCase() + brief.opportunity_urgency.slice(1)} Urgency
              </span>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">{(brief.opportunity_intent_score * 100).toFixed(0)}%</p>
              <p className="text-[10px] text-gray-400">Intent Score</p>
            </div>
          </div>
          <h1 className="text-xl font-bold text-gray-900 mb-3">{brief.opportunity_title}</h1>
          <p className="text-sm text-gray-600 leading-relaxed">{brief.opportunity_description}</p>

          {/* Details row */}
          <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-gray-100">
            {brief.opportunity_buyer_organization && (
              <div className="flex items-center gap-1.5 text-xs text-gray-600">
                <Target className="w-3.5 h-3.5 text-gray-400" />
                {brief.opportunity_buyer_organization}
              </div>
            )}
            {brief.opportunity_location && (
              <div className="flex items-center gap-1.5 text-xs text-gray-600">
                <MapPin className="w-3.5 h-3.5 text-gray-400" />
                {brief.opportunity_location}
              </div>
            )}
            {(brief.opportunity_estimated_value_min || brief.opportunity_estimated_value_max) && (
              <div className="flex items-center gap-1.5 text-xs text-gray-600">
                <DollarSign className="w-3.5 h-3.5 text-gray-400" />
                {brief.opportunity_currency || '$'}
                {brief.opportunity_estimated_value_min ? `${(brief.opportunity_estimated_value_min / 1000).toFixed(0)}K` : '?'}
                {' – '}
                {brief.opportunity_estimated_value_max ? `${(brief.opportunity_estimated_value_max / 1000).toFixed(0)}K` : '?'}
              </div>
            )}
            {brief.opportunity_deadline && (
              <div className="flex items-center gap-1.5 text-xs text-gray-600">
                <Clock className="w-3.5 h-3.5 text-gray-400" />
                Deadline: {new Date(brief.opportunity_deadline).toLocaleDateString()}
              </div>
            )}
          </div>
        </div>

        {/* Why Now */}
        {brief.opportunity_why_now && (
          <div className="bg-white rounded-2xl border border-radar-200 p-6">
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-radar-500 mt-0.5 flex-shrink-0" />
              <div>
                <h2 className="text-sm font-semibold text-radar-800 mb-1">Why This Matters Now</h2>
                <p className="text-sm text-gray-700 leading-relaxed">{brief.opportunity_why_now}</p>
              </div>
            </div>
          </div>
        )}

        {/* Your Match */}
        {brief.match_score !== null && (
          <div className="bg-white rounded-2xl border border-emerald-200 p-6">
            <h2 className="text-sm font-semibold text-emerald-800 mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-500" />
              Why You Were Matched
            </h2>
            <div className="flex items-center gap-4 mb-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-emerald-700">{(brief.match_score * 100).toFixed(0)}%</p>
                <p className="text-xs text-gray-400">Match Score</p>
              </div>
              <div className="flex-1 grid grid-cols-3 gap-3">
                {[
                  { label: 'Service Fit', value: brief.match_service_fit },
                  { label: 'Location Fit', value: brief.match_geographic_fit },
                  { label: 'Size Fit', value: brief.match_project_size_fit },
                ].map(({ label, value }) => value !== null && (
                  <div key={label} className="text-center">
                    <div className="w-full bg-gray-100 rounded-full h-1.5 mb-1">
                      <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${(value || 0) * 100}%` }} />
                    </div>
                    <p className="text-[10px] text-gray-500">{label}</p>
                    <p className="text-xs font-semibold text-gray-700">{((value || 0) * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </div>
            {brief.match_reasoning && (
              <p className="text-xs text-gray-600 bg-gray-50 rounded-lg px-3 py-2">{brief.match_reasoning}</p>
            )}
          </div>
        )}

        {/* Recommended Action */}
        {brief.opportunity_recommended_action && (
          <div className="bg-white rounded-2xl border border-emerald-200 p-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <h2 className="text-sm font-semibold text-emerald-800 mb-1">Recommended Next Step</h2>
                <p className="text-sm text-gray-700 leading-relaxed">{brief.opportunity_recommended_action}</p>
              </div>
            </div>
          </div>
        )}

        {/* Requirements */}
        {brief.opportunity_requirements.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Requirements</h2>
            <ul className="space-y-1">
              {brief.opportunity_requirements.map((req, i) => (
                <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-radar-500 mt-1 flex-shrink-0">•</span> {req}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Source link */}
        {brief.opportunity_source_url && (
          <div className="bg-white rounded-2xl border border-gray-200 p-4">
            <a
              href={brief.opportunity_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-radar-600 hover:text-radar-700 font-medium"
            >
              <ExternalLink className="w-4 h-4" />
              View original source
            </a>
          </div>
        )}

        {/* Response section */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6">
          {submitted || brief.already_responded ? (
            <div className="text-center py-4">
              <CheckCircle className={`w-10 h-10 mx-auto mb-3 ${isNotInterested ? 'text-gray-400' : 'text-emerald-500'}`} />
              <h2 className="text-base font-semibold text-gray-900 mb-1">
                {isNotInterested ? 'Noted' : 'Response received'}
              </h2>
              <p className="text-sm text-gray-500">
                {isNotInterested
                  ? "Thanks for letting us know — we won't follow up on this one."
                  : 'Thank you — the team will be in touch shortly.'}
              </p>
            </div>
          ) : action === 'interested' ? (
            <div className="space-y-4">
              <h2 className="text-base font-semibold text-gray-900 mb-1">Are you interested in this opportunity?</h2>
              <div className="text-sm font-medium px-3 py-2 rounded-lg bg-emerald-50 text-emerald-700">
                Great! Tell us about yourself:
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Your Name *</label>
                  <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                    placeholder="Jane Smith"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-radar-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Email Address *</label>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                    placeholder="you@company.com"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-radar-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Message (optional)</label>
                <textarea
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  rows={3}
                  placeholder="Tell us about your experience and why you're a good fit..."
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-radar-500 resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => respondMutation.mutate({ action: 'interested', name, email, message })}
                  disabled={!name || !email || respondMutation.isPending}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-radar-600 hover:bg-radar-700 text-white font-medium rounded-xl text-sm transition-colors disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                  {respondMutation.isPending ? 'Sending...' : 'Submit Response'}
                </button>
                <button
                  onClick={() => setAction(null)}
                  className="px-4 text-sm text-gray-500 hover:text-gray-700"
                >
                  Back
                </button>
              </div>
              {respondMutation.isError && (
                <p className="text-xs text-red-600">{(respondMutation.error as Error).message}</p>
              )}
            </div>
          ) : (
            <>
              <h2 className="text-base font-semibold text-gray-900 mb-4">Are you interested in this opportunity?</h2>
              <div className="flex gap-3">
                <button
                  onClick={() => setAction('interested')}
                  disabled={respondMutation.isPending}
                  className="flex-1 flex items-center justify-center gap-2 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition-colors disabled:opacity-50"
                >
                  <ThumbsUp className="w-4 h-4" /> Yes, I'm Interested
                </button>
                <button
                  onClick={() => respondMutation.mutate({ action: 'not_interested' })}
                  disabled={respondMutation.isPending}
                  className="flex-1 flex items-center justify-center gap-2 py-3 border border-gray-300 hover:bg-gray-50 text-gray-600 font-medium rounded-xl text-sm transition-colors disabled:opacity-50"
                >
                  <ThumbsDown className="w-4 h-4" />
                  {respondMutation.isPending && respondMutation.variables?.action === 'not_interested' ? 'Sending...' : 'Not for Me'}
                </button>
              </div>
              {respondMutation.isError && (
                <p className="text-xs text-red-600 mt-3">{(respondMutation.error as Error).message}</p>
              )}
            </>
          )}
        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-6 px-6 text-center text-xs text-gray-400 mt-8">
        <p>Powered by <Link href="https://ai-intent-radar.vercel.app" className="text-radar-500 hover:text-radar-600">Intent Radar</Link> · Commercial Intelligence Platform</p>
        <p className="mt-1">This brief expires {new Date(brief.expires_at).toLocaleDateString()}</p>
      </footer>
    </div>
  );
}
