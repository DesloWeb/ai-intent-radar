"""Pydantic schemas for request/response validation."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    organization_slug: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    organization_id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100)
    enabled_countries: List[str] = ["US"]


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    enabled_countries: List[str]
    is_active: bool
    is_demo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------------

class SignalCreate(BaseModel):
    source: str
    source_id: Optional[str] = None
    country_code: str
    title: str
    description: str
    raw_data: Optional[Dict] = {}


class SignalResponse(BaseModel):
    id: uuid.UUID
    source: str
    source_id: str
    country_code: str
    title: str
    description: str
    status: str
    intent_score: Optional[float] = None
    confidence: Optional[float] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Opportunity
# ---------------------------------------------------------------------------

class OpportunityResponse(BaseModel):
    id: uuid.UUID
    signal_id: uuid.UUID
    country_code: str
    title: str
    description: str
    category: str
    subcategory: Optional[str] = None
    intent_score: float
    confidence: float
    urgency: str
    buyer_name: Optional[str] = None
    buyer_organization: Optional[str] = None
    location: Optional[str] = None
    estimated_value_min: Optional[float] = None
    estimated_value_max: Optional[float] = None
    currency: Optional[str] = None
    deadline: Optional[datetime] = None
    requirements: Union[List, Dict]
    why_now: Optional[str] = None
    recommended_action: Optional[str] = None
    evidence: Union[List, Dict]
    market_context: Dict
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OpportunityListResponse(BaseModel):
    opportunities: List[OpportunityResponse]
    total: int
    page: int
    per_page: int


class OpportunityFilter(BaseModel):
    country_code: Optional[str] = None
    category: Optional[str] = None
    urgency: Optional[str] = None
    min_intent_score: Optional[float] = None
    status: Optional[str] = None
    page: int = 1
    per_page: int = 20


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    services: List[str] = []
    categories: List[str] = []
    locations: List[str] = []
    country_codes: List[str] = []
    min_project_value: Optional[float] = None
    max_project_value: Optional[float] = None


class ProviderResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str] = None
    services: Union[List, Dict]
    categories: Union[List, Dict]
    locations: Union[List, Dict]
    country_codes: Union[List, Dict]
    min_project_value: Optional[float] = None
    max_project_value: Optional[float] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Provider Match
# ---------------------------------------------------------------------------

class ProviderMatchResponse(BaseModel):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    provider_id: uuid.UUID
    service_fit: float
    geographic_fit: float
    project_size_fit: float
    total_score: float
    reasoning: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# User Feedback
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    opportunity_id: uuid.UUID
    feedback_type: str = Field(
        pattern="^(saved|dismissed|contacted|won|lost|flagged)$"
    )
    notes: Optional[str] = None
    outcome_value: Optional[float] = None


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    opportunity_id: uuid.UUID
    feedback_type: str
    notes: Optional[str] = None
    outcome_value: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Market Intelligence
# ---------------------------------------------------------------------------

class MarketTrendResponse(BaseModel):
    id: uuid.UUID
    country_code: str
    category: str
    period_start: datetime
    period_end: datetime
    signal_count: int
    opportunity_count: int
    avg_intent_score: float
    avg_confidence: float
    growth_rate: float
    top_subcategories: Union[List, Dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class MarketSummaryResponse(BaseModel):
    country_code: str
    total_signals: int
    total_opportunities: int
    avg_intent_score: float
    avg_confidence: float
    top_categories: List[Dict]
    recent_trends: List[MarketTrendResponse]
    emerging_demand: List[Dict]


class DashboardResponse(BaseModel):
    total_opportunities: int
    high_priority_count: int
    new_this_week: int
    countries_summary: List[Dict]
    top_opportunities: List[OpportunityResponse]
    emerging_demand: List[Dict]
    market_trends: List[Dict]
    recent_feedback: List[FeedbackResponse]
    intent_distribution: Dict
    urgency_distribution: Dict


# ---------------------------------------------------------------------------
# Country Config
# ---------------------------------------------------------------------------

class CountryResponse(BaseModel):
    id: int
    code: str
    name: str
    is_enabled: bool
    signal_sources: Union[List, Dict]
    settings: Dict

    model_config = {"from_attributes": True}


class CountryUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    signal_sources: Optional[List] = None
    settings: Optional[Dict] = None
