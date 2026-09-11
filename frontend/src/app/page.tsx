'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Radar, Target, Zap, Users, Globe, TrendingUp } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-radar-950">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (isAuthenticated) {
    // Redirect is in flight — render nothing rather than flash the landing page.
    return null;
  }

  return (
    <div className="min-h-screen bg-white">

      {/* ── Hero: solid blue, guarantees contrast for the white text ─────── */}
      <div className="bg-radar-950 text-white">
        <nav className="flex items-center justify-between px-6 py-4 border-b border-radar-800 max-w-5xl mx-auto">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-radar-500 rounded-lg flex items-center justify-center">
              <Radar className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-bold">Intent Radar</span>
          </Link>
          <div className="flex items-center gap-6 text-sm text-radar-300">
            <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
            <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
            <Link href="/auth/login" className="bg-radar-600 hover:bg-radar-500 text-white px-4 py-1.5 rounded-lg transition-colors">
              Sign in
            </Link>
          </div>
        </nav>

        <section className="max-w-3xl mx-auto px-6 pt-20 pb-24 text-center">
          <h1 className="text-4xl font-bold mb-4">
            Know what the market wants<br />before everyone else.
          </h1>
          <p className="text-radar-300 text-lg max-w-2xl mx-auto">
            AI Intent Radar is a commercial intelligence platform that detects where money is
            likely to move, explains why, and tells businesses what to act on — before the
            opportunity becomes obvious.
          </p>
        </section>
      </div>

      {/* ── What we do (white) ────────────────────────────────────────────── */}
      <div>
        <section className="max-w-5xl mx-auto px-6 py-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: Target,
                title: 'Detect Commercial Intent',
                desc: 'We scan public sources — job posts, procurement notices, forum requests, business announcements — and classify the commercial intent behind each signal.',
              },
              {
                icon: Zap,
                title: 'Score and Prioritise',
                desc: 'Every signal is scored 0–100% for intent strength, confidence, and urgency. You see only what matters, ranked by how actionable it is right now.',
              },
              {
                icon: Users,
                title: 'Match to Providers',
                desc: 'Opportunities are matched to businesses and individuals who can serve them — scored by skill fit, location, and project size.',
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="bg-gray-50 border border-gray-200 rounded-2xl p-6">
                <div className="w-10 h-10 bg-radar-100 rounded-xl flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-radar-600" />
                </div>
                <h3 className="text-base font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* ── What we are not (sits in the white zone) ─────────────────────── */}
      <div>
        <section className="max-w-3xl mx-auto px-6 py-16">
          <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">What Intent Radar is not</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                'A job board',
                'A tender aggregator',
                'A lead scraper',
                'An AI chatbot',
                'A notification spam service',
                'A procurement search engine',
              ].map((item) => (
                <div key={item} className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="text-red-500 font-bold">✕</span> {item}
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-600 mt-6 leading-relaxed">
              Those may be components of the system — but they are not the product. The product
              is <strong className="text-gray-900">commercial intent intelligence</strong>: turning
              scattered public signals into decisions your business can act on today.
            </p>
          </div>
        </section>
      </div>

      {/* ── Market stats (sits in the white zone) ────────────────────────── */}
      <div>
        <section className="max-w-5xl mx-auto px-6 py-16">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">Where we operate</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            {[
              { icon: Globe, stat: 'US + Nigeria', label: 'Market focus — more coming' },
              { icon: TrendingUp, stat: '$700B+', label: 'Annual US federal contracting market' },
              { icon: Target, stat: '6M+', label: 'US SMBs actively seeking contracts' },
            ].map(({ icon: Icon, stat, label }) => (
              <div key={label} className="bg-gray-50 border border-gray-200 rounded-2xl p-6">
                <Icon className="w-6 h-6 text-radar-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-gray-900 mb-1">{stat}</p>
                <p className="text-sm text-gray-600">{label}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* ── CTA: solid blue (same as hero) ───────────────────────────────── */}
      <div className="bg-radar-950 text-white">
        <section className="max-w-3xl mx-auto px-6 py-20 text-center">
          <h2 className="text-2xl font-semibold mb-4">Ready to get ahead of the market?</h2>
          <p className="text-radar-300 text-sm mb-8">
            Create your account and start seeing commercial intent in real time.
          </p>
          <Link
            href="/auth/register"
            className="inline-block bg-white hover:bg-radar-50 text-radar-700 font-medium px-8 py-3 rounded-xl transition-colors"
          >
            Get started free
          </Link>
        </section>
      </div>

      {/* ── Footer (same blue) ────────────────────────────────────────────── */}
      <footer className="bg-radar-950 py-6 px-6 text-center text-xs text-radar-400">
        <div className="flex items-center justify-center gap-6 mb-2">
          <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
        </div>
        <p>© {new Date().getFullYear()} AI Intent Radar. All rights reserved.</p>
      </footer>
    </div>
  );
}
