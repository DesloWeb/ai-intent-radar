'use client';

import { clsx } from 'clsx';

interface UrgencyBadgeProps {
  urgency: 'low' | 'medium' | 'high' | 'critical';
  size?: 'sm' | 'md';
}

const config = {
  low: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-400' },
  medium: { bg: 'bg-amber-100', text: 'text-amber-800', dot: 'bg-amber-500' },
  high: { bg: 'bg-orange-100', text: 'text-orange-800', dot: 'bg-orange-500' },
  critical: { bg: 'bg-red-100', text: 'text-red-800', dot: 'bg-red-500' },
};

export function UrgencyBadge({ urgency, size = 'md' }: UrgencyBadgeProps) {
  const c = config[urgency] || config.medium;
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        c.bg,
        c.text,
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
      )}
    >
      <span className={clsx('w-1.5 h-1.5 rounded-full', c.dot)} />
      {urgency.charAt(0).toUpperCase() + urgency.slice(1)}
    </span>
  );
}
