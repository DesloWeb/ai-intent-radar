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

export interface Country {
  id: number;
  code: string;
  name: string;
  is_enabled: boolean;
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
  source_url: string | null;
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
  provider_type: 'business' | 'individual';
  name: string;
  description: string | null;
  email: string | null;
  phone: string | null;
  // Business fields
  services: string[];
  categories: string[];
  min_project_value: number | null;
  max_project_value: number | null;
  // Individual fields
  skills: string[];
  hourly_rate_min: number | null;
  hourly_rate_max: number | null;
  availability: 'full_time' | 'part_time' | 'contract' | 'weekends' | null;
  verified: boolean;
  profile_url: string | null;
  // Shared
  locations: string[];
  country_codes: string[];
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

export interface PublicBrief {
  opportunity_title: string;
  opportunity_description: string;
  opportunity_category: string;
  opportunity_urgency: 'low' | 'medium' | 'high' | 'critical';
  opportunity_intent_score: number;
  opportunity_confidence: number;
  opportunity_why_now: string | null;
  opportunity_recommended_action: string | null;
  opportunity_requirements: string[];
  opportunity_evidence: string[];
  opportunity_source_url: string | null;
  opportunity_estimated_value_min: number | null;
  opportunity_estimated_value_max: number | null;
  opportunity_currency: string | null;
  opportunity_deadline: string | null;
  opportunity_buyer_organization: string | null;
  opportunity_location: string | null;
  match_score: number | null;
  match_reasoning: string | null;
  match_service_fit: number | null;
  match_geographic_fit: number | null;
  match_project_size_fit: number | null;
  provider_name: string | null;
  brief_id: string;
  status: string;
  expires_at: string;
  already_responded: boolean;
}

export interface Brief {
  id: string;
  token: string;
  public_url: string;
  expires_at: string;
  status: string;
  view_count: number;
  created_at: string;
  opportunity_id: string;
  opportunity_title?: string;
  provider_match_id: string | null;
  provider_name?: string;
  provider_email?: string;
  provider_message?: string;
  responded_at?: string;
  email_sent?: boolean;
}
