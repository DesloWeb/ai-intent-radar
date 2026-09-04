'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Radar } from 'lucide-react';
import Link from 'next/link';

export default function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [orgSlug, setOrgSlug] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    register.mutate({ email, password, fullName, orgSlug: orgSlug || undefined });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-radar-950 via-radar-900 to-radar-950">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-radar-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Radar className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Intent Radar</h1>
          <p className="text-radar-300 text-sm mt-1">Create your account</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Register</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-radar-500 focus:border-radar-500 outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-radar-500 focus:border-radar-500 outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-radar-500 focus:border-radar-500 outline-none"
                minLength={8}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization <span className="text-gray-400">(optional)</span>
              </label>
              <input
                type="text"
                value={orgSlug}
                onChange={(e) => setOrgSlug(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-radar-500 focus:border-radar-500 outline-none"
                placeholder="my-company"
              />
            </div>
            {register.isError && (
              <p className="text-sm text-red-600">{register.error.message}</p>
            )}
            <button
              type="submit"
              disabled={register.isPending}
              className="w-full bg-radar-600 hover:bg-radar-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {register.isPending ? 'Creating account...' : 'Create account'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account?{' '}
            <Link href="/auth/login" className="text-radar-600 hover:text-radar-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
