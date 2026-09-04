'use client';

import { Globe, Bell, Search } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  countryCode?: string;
  onCountryChange?: (code: string | undefined) => void;
}

export function Header({ title, subtitle, countryCode, onCountryChange }: HeaderProps) {
  return (
    <header className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {/* Country filter */}
        {onCountryChange && (
          <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-2">
            <Globe className="w-4 h-4 text-gray-400" />
            <select
              value={countryCode || ''}
              onChange={(e) => onCountryChange(e.target.value || undefined)}
              className="text-sm bg-transparent outline-none text-gray-700 cursor-pointer"
            >
              <option value="">All Markets</option>
              <option value="US">🇺🇸 United States</option>
            </select>
          </div>
        )}
      </div>
    </header>
  );
}
