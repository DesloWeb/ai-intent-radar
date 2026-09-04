'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  LayoutDashboard,
  Target,
  Radio,
  Globe,
  Users,
  Settings,
  LogOut,
  Radar,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/opportunities', label: 'Opportunities', icon: Target },
  { href: '/market-intelligence', label: 'Market Intelligence', icon: Globe },
  { href: '/providers', label: 'Providers', icon: Users },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-radar-950 text-white flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-radar-800">
        <div className="w-9 h-9 bg-radar-500 rounded-lg flex items-center justify-center">
          <Radar className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight">Intent Radar</h1>
          <p className="text-[10px] text-radar-300 uppercase tracking-widest">AI Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-radar-700/60 text-white'
                  : 'text-radar-300 hover:bg-radar-800 hover:text-white'
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="px-3 py-4 border-t border-radar-800">
        {user && (
          <div className="px-3 py-2 mb-2">
            <p className="text-sm font-medium text-white truncate">{user.full_name}</p>
            <p className="text-xs text-radar-400 truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-radar-300 hover:bg-radar-800 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
