'use client';

const flags: Record<string, string> = {
  US: '🇺🇸',
  GB: '🇬🇧',
  KE: '🇰🇪',
  ZA: '🇿🇦',
};

interface CountryFlagProps {
  code: string;
  size?: 'sm' | 'md' | 'lg';
}

export function CountryFlag({ code, size = 'md' }: CountryFlagProps) {
  const flag = flags[code] || '🌍';
  const sizeMap = { sm: 'text-sm', md: 'text-lg', lg: 'text-2xl' };
  return (
    <span className={sizeMap[size]} title={code}>
      {flag}
    </span>
  );
}
