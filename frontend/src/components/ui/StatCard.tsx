'use client';

import { clsx } from 'clsx';
import { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: { value: number; label: string };
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

const colorMap = {
  blue: 'bg-radar-50 text-radar-600',
  green: 'bg-emerald-50 text-emerald-600',
  yellow: 'bg-amber-50 text-amber-600',
  red: 'bg-red-50 text-red-600',
  purple: 'bg-purple-50 text-purple-600',
};

export function StatCard({ label, value, icon, trend, color = 'blue' }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <p
              className={clsx(
                'text-xs font-medium mt-1',
                trend.value >= 0 ? 'text-emerald-600' : 'text-red-600'
              )}
            >
              {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
            </p>
          )}
        </div>
        {icon && (
          <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', colorMap[color])}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
