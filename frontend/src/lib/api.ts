// API client for AI Smart Intent Radar

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('refresh_token');
  }

  setTokens(access: string, refresh: string) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getAccessToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (response.status === 401 && this.getRefreshToken()) {
      // Try refresh
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
        const retryResponse = await fetch(`${this.baseUrl}${path}`, {
          ...options,
          headers,
        });
        if (!retryResponse.ok) {
          throw new Error(`API error: ${retryResponse.status}`);
        }
        return retryResponse.json();
      }
      this.clearTokens();
      window.location.href = '/auth/login';
      throw new Error('Session expired');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return response.json();
  }

  private async refreshAccessToken(): Promise<boolean> {
    try {
      const refresh = this.getRefreshToken();
      if (!refresh) return false;

      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (!response.ok) return false;
      const data = await response.json();
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // Auth
  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string; refresh_token: string }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    );
    this.setTokens(data.access_token, data.refresh_token);
    return data;
  }

  async register(email: string, password: string, fullName: string, orgSlug?: string) {
    const data = await this.request<{ access_token: string; refresh_token: string }>(
      '/auth/register',
      {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          organization_slug: orgSlug,
        }),
      }
    );
    this.setTokens(data.access_token, data.refresh_token);
    return data;
  }

  async getMe() {
    return this.request<import('../types').User>('/auth/me');
  }

  // Dashboard
  async getDashboard(countryCode?: string) {
    const params = countryCode ? `?country_code=${countryCode}` : '';
    return this.request<import('../types').DashboardResponse>(`/dashboard${params}`);
  }

  // Opportunities
  async getOpportunities(params: {
    country_code?: string;
    category?: string;
    urgency?: string;
    min_intent_score?: number;
    status?: string;
    page?: number;
    per_page?: number;
  } = {}) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.set(key, String(value));
      }
    });
    const qs = searchParams.toString();
    return this.request<import('../types').OpportunityListResponse>(
      `/opportunities${qs ? `?${qs}` : ''}`
    );
  }

  async getOpportunity(id: string) {
    return this.request<import('../types').Opportunity>(`/opportunities/${id}`);
  }

  // Signals
  async getSignals(params: {
    country_code?: string;
    status?: string;
    page?: number;
    per_page?: number;
  } = {}) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.set(key, String(value));
      }
    });
    const qs = searchParams.toString();
    return this.request<import('../types').Signal[]>(`/signals${qs ? `?${qs}` : ''}`);
  }

  // Providers
  async getProviders(providerType?: string) {
    const params = providerType ? `?provider_type=${providerType}` : '';
    return this.request<import('../types').Provider[]>(`/providers${params}`);
  }

  async createProvider(data: {
    provider_type?: string;
    name: string;
    description?: string;
    services?: string[];
    categories?: string[];
    skills?: string[];
    locations?: string[];
    country_codes?: string[];
    min_project_value?: number;
    max_project_value?: number;
    hourly_rate_min?: number;
    hourly_rate_max?: number;
    availability?: string;
    profile_url?: string;
  }) {
    return this.request<import('../types').Provider>('/providers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async matchOpportunity(opportunityId: string) {
    return this.request<import('../types').ProviderMatch[]>(
      `/providers/${opportunityId}/match`,
      { method: 'POST' }
    );
  }

  async getMatches(opportunityId: string) {
    return this.request<import('../types').ProviderMatch[]>(
      `/providers/${opportunityId}/matches`
    );
  }

  // Feedback
  async submitFeedback(data: {
    opportunity_id: string;
    feedback_type: string;
    notes?: string;
    outcome_value?: number;
  }) {
    return this.request<import('../types').UserFeedback>('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getFeedbacks() {
    return this.request<import('../types').UserFeedback[]>('/feedback');
  }

  async getFeedbackStats() {
    return this.request<import('../types').FeedbackStats>('/feedback/stats');
  }

  // Market Intelligence
  async getMarketSummary(countryCode?: string) {
    const params = countryCode ? `?country_code=${countryCode}` : '';
    return this.request<import('../types').MarketSummary>(
      `/market-intelligence/summary${params}`
    );
  }

  async getMarketTrends(countryCode?: string) {
    const params = countryCode ? `?country_code=${countryCode}` : '';
    return this.request<import('../types').MarketTrend[]>(
      `/market-intelligence/trends${params}`
    );
  }

  // Countries
  async getCountries() {
    return this.request<import('../types').Country[]>('/countries');
  }
}

export const api = new ApiClient(API_BASE);
