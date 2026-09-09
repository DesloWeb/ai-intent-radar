'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Card } from '@/components/ui/Card';
import { User, Lock, CheckCircle, AlertCircle } from 'lucide-react';

export default function SettingsPage() {
  const router = useRouter();
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
      </div>
    </AppShell>
  );
}
