// Types for AI Smart Intent Radar frontend

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'analyst' | 'viewer';
  organization_id: string;
  is_active: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  enabled_countries: string[];
  is_active: boolean;
  is_demo: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Signal {
  id: string;
  source: string;
  source_id: string;
  country_code: string;
  title: string;
  description: string;
  status: string;
  intent_score: number | null;
  confidence: number | null;
  created_at: string;
  processed_at: string | null;
}

export interface Opportunity {
  id: string;
  signal_id: string;
  country_code: string;
  title: string;
  description: string;
  category: string;
  subcategory: string | null;
  intent_score: number;
  confidence: number;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  buyer_name: string | null;
  buyer_organization: string | null;
  location: string | null;
  estimated_value_min: number | null;
  estimated_value_max: number | null;
  currency: string | null;
  deadline: string | null;
  requirements: string[];
  why_now: string | null;
  recommended_action: string | null;
  evidence: string[];
  market_context: Record<string, unknown>;
  status: string;
  created_at: string;
}

export interface OpportunityListResponse {
  opportunities: Opportunity[];
  total: number;
  page: number;
  per_page: number;
}

export interface Provider {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  services: string[];
  categories: string[];
  locations: string[];
  country_codes: string[];
  min_project_value: number | null;
  max_project_value: number | null;
  is_active: boolean;
  created_at: string;
}

export interface ProviderMatch {
  id: string;
  opportunity_id: string;
  provider_id: string;
  service_fit: number;
  geographic_fit: number;
  project_size_fit: number;
  total_score: number;
  reasoning: string | null;
  created_at: string;
}

export interface UserFeedback {
  id: string;
  user_id: string;
  opportunity_id: string;
  feedback_type: string;
  notes: string | null;
  outcome_value: number | null;
  created_at: string;
}

export interface DashboardResponse {
  total_opportunities: number;
  high_priority_count: number;
  new_this_week: number;
  countries_summary: { country_code: string; total: number; avg_intent_score: number }[];
  top_opportunities: Opportunity[];
  emerging_demand: { category: string; country_code: string; count: number; avg_score: number }[];
  market_trends: { category: string; country_code: string; count: number }[];
  recent_feedback: UserFeedback[];
  intent_distribution: Record<string, number>;
  urgency_distribution: Record<string, number>;
}

export interface MarketSummary {
  country_code: string;
  total_signals: number;
  total_opportunities: number;
  avg_intent_score: number;
  avg_confidence: number;
  top_categories: { category: string; count: number; avg_score: number }[];
  recent_trends: MarketTrend[];
  emerging_demand: { category: string; country_code: string; count: number; avg_score: number }[];
}

export interface MarketTrend {
  id: string;
  country_code: string;
  category: string;
  period_start: string;
  period_end: string;
  signal_count: number;
  opportunity_count: number;
  avg_intent_score: number;
  avg_confidence: number;
  growth_rate: number;
  top_subcategories: string[];
  created_at: string;
}

export interface FeedbackStats {
  saved?: number;
  dismissed?: number;
  contacted?: number;
  won?: number;
  lost?: number;
  win_rate: number | null;
}

export interface Country {
  id: number;
  code: string;
  name: string;
  is_enabled: boolean;
  signal_sources: { name: string; type: string; url: string }[];
  settings: Record<string, unknown>;
}
