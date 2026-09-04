'use client';

import { clsx } from 'clsx';

interface ScoreBarProps {
  value: number;
  max?: number;
  label: string;
  color?: 'blue' | 'green' | 'yellow' | 'red';
  size?: 'sm' | 'md' | 'lg';
}

export function ScoreBar({
  value,
  max = 1,
  label,
  color = 'blue',
  size = 'md',
}: ScoreBarProps) {
  const percentage = Math.min(100, (value / max) * 100);

  const colorMap = {
    blue: 'bg-radar-500',
    green: 'bg-signal-green',
    yellow: 'bg-signal-yellow',
    red: 'bg-signal-red',
  };

  const bgMap = {
    blue: 'bg-radar-100',
    green: 'bg-emerald-100',
    yellow: 'bg-amber-100',
    red: 'bg-red-100',
  };

  const sizeMap = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3.5',
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-medium text-gray-600">{label}</span>
        <span className="text-xs font-semibold text-gray-800">
          {percentage.toFixed(0)}%
        </span>
      </div>
      <div className={clsx('w-full rounded-full overflow-hidden', bgMap[color], sizeMap[size])}>
        <div
          className={clsx('h-full rounded-full transition-all duration-500', colorMap[color])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
