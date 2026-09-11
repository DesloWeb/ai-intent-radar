'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Card } from '@/components/ui/Card';
import { User, Lock, CheckCircle, AlertCircle, Globe } from 'lucide-react';

export default function SettingsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.replace('/auth/login');
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
    }
  }, [user]);

  const profileMutation = useMutation({
    mutationFn: () => api.updateProfile({ full_name: fullName, email }),
    onSuccess: () => setProfileMsg({ type: 'success', text: 'Profile updated successfully.' }),
    onError: (e: Error) => setProfileMsg({ type: 'error', text: e.message || 'Failed to update profile.' }),
  });

  const passwordMutation = useMutation({
    mutationFn: () => api.changePassword(currentPassword, newPassword),
    onSuccess: () => {
      setPasswordMsg({ type: 'success', text: 'Password changed successfully.' });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    },
    onError: (e: Error) => setPasswordMsg({ type: 'error', text: e.message || 'Failed to change password.' }),
  });

  const handlePasswordSubmit = () => {
    setPasswordMsg(null);
    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }
    if (newPassword.length < 8) {
      setPasswordMsg({ type: 'error', text: 'Password must be at least 8 characters.' });
      return;
    }
    passwordMutation.mutate();
  };

  // Target countries — which markets this org wants ingestion to run for.
  const isAdmin = user?.role === 'admin';
  const [countryMsg, setCountryMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);

  const { data: countries = [] } = useQuery({
    queryKey: ['countries'],
    queryFn: () => api.getCountries(),
    enabled: isAuthenticated,
  });

  const { data: organization } = useQuery({
    queryKey: ['organization'],
    queryFn: () => api.getOrganization(),
    enabled: isAuthenticated,
  });

  useEffect(() => {
    if (organization) setSelectedCountries(organization.enabled_countries);
  }, [organization]);

  const countryMutation = useMutation({
    mutationFn: () => api.updateOrganization(selectedCountries),
    onSuccess: () => {
      setCountryMsg({ type: 'success', text: 'Target countries updated.' });
      queryClient.invalidateQueries({ queryKey: ['organization'] });
    },
    onError: (e: Error) => setCountryMsg({ type: 'error', text: e.message || 'Failed to update target countries.' }),
  });

  const toggleCountry = (code: string) => {
    setSelectedCountries((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const handleCountrySubmit = () => {
    setCountryMsg(null);
    if (selectedCountries.length === 0) {
      setCountryMsg({ type: 'error', text: 'Select at least one country.' });
      return;
    }
    countryMutation.mutate();
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Manage your account details and password.</p>
      </div>

      <div className="max-w-xl space-y-6">
        {/* Account Details */}
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <User className="w-4 h-4" /> Account Details
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-radar-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-radar-400"
              />
            </div>
            {profileMsg && (
              <div className={`flex items-center gap-2 text-xs p-2 rounded-lg ${profileMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                {profileMsg.type === 'success' ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {profileMsg.text}
              </div>
            )}
            <button
              onClick={() => { setProfileMsg(null); profileMutation.mutate(); }}
              disabled={profileMutation.isPending}
              className="px-4 py-2 bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors"
            >
              {profileMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </Card>

        {/* Change Password */}
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Lock className="w-4 h-4" /> Change Password
          </h2>
          <div className="space-y-4">
            {(['Current Password', 'New Password', 'Confirm New Password'] as const).map((label, i) => {
              const val = [currentPassword, newPassword, confirmPassword][i];
              const setter = [setCurrentPassword, setNewPassword, setConfirmPassword][i];
              return (
                <div key={label}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                  <input
                    type="password"
                    value={val}
                    onChange={(e) => setter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-radar-400"
                  />
                </div>
              );
            })}
            {passwordMsg && (
              <div className={`flex items-center gap-2 text-xs p-2 rounded-lg ${passwordMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                {passwordMsg.type === 'success' ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {passwordMsg.text}
              </div>
            )}
            <button
              onClick={handlePasswordSubmit}
              disabled={passwordMutation.isPending}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors"
            >
              {passwordMutation.isPending ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </Card>

        {/* Target Countries */}
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Globe className="w-4 h-4" /> Target Countries
          </h2>
          <p className="text-xs text-gray-500 mb-4">
            Choose which markets Intent Radar should fetch opportunities from.
          </p>
          <div className="space-y-2">
            {countries.map((country) => (
              <label
                key={country.code}
                className={`flex items-center gap-3 px-3 py-2.5 border border-gray-200 rounded-lg text-sm ${isAdmin ? 'cursor-pointer hover:bg-gray-50' : 'opacity-70'}`}
              >
                <input
                  type="checkbox"
                  checked={selectedCountries.includes(country.code)}
                  onChange={() => toggleCountry(country.code)}
                  disabled={!isAdmin}
                  className="w-4 h-4 accent-radar-600"
                />
                <span className="font-medium text-gray-700">{country.name}</span>
                <span className="text-xs text-gray-400 ml-auto">{country.code}</span>
              </label>
            ))}
            {countries.length === 0 && (
              <p className="text-xs text-gray-400">No countries configured yet.</p>
            )}
            {!isAdmin && (
              <p className="text-xs text-gray-400">Only admins can change target countries.</p>
            )}
            {countryMsg && (
              <div className={`flex items-center gap-2 text-xs p-2 rounded-lg ${countryMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                {countryMsg.type === 'success' ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {countryMsg.text}
              </div>
            )}
            {isAdmin && (
              <button
                onClick={handleCountrySubmit}
                disabled={countryMutation.isPending}
                className="px-4 py-2 bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors"
              >
                {countryMutation.isPending ? 'Saving...' : 'Save Countries'}
              </button>
            )}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
