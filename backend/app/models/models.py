"""Database models for AI Smart Intent Radar.

Multi-tenant architecture with organization isolation.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class SignalStatus(str):
    RAW = "raw"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    EXTRACTED = "extracted"
    SCORED = "scored"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ERROR = "error"


class OpportunityStatus(str):
    DETECTED = "detected"
    VALIDATED = "validated"
    EXPOSED = "exposed"
    CONTACTED = "contacted"
    WON = "won"
    LOST = "lost"
    EXPIRED = "expired"
    DISMISSED = "dismissed"


class UrgencyLevel(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackType(str):
    SAVED = "saved"
    DISMISSED = "dismissed"
    CONTACTED = "contacted"
    WON = "won"
    LOST = "lost"
    FLAGGED = "flagged"


# ---------------------------------------------------------------------------
# Base mixin
# ---------------------------------------------------------------------------

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------

class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    enabled_countries: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=lambda: ["US"]
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    providers: Mapped[list["Provider"]] = relationship(back_populates="organization")
    user_feedbacks: Mapped[list["UserFeedback"]] = relationship(
        back_populates="organization"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="organization")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # SEC-21

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="users")
    user_feedbacks: Mapped[list["UserFeedback"]] = relationship(
        back_populates="user"
    )


class Country(Base):
    """Configuration-driven country support."""
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    signal_sources: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    settings: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class Signal(Base, TimestampMixin):
    """Raw and processed intelligence signals."""
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    normalized_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=SignalStatus.RAW
    )
    # AI classification results
    intent_classification: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    extracted_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # Scoring
    intent_score: Mapped[float] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Deduplication
    dedup_hash: Mapped[str] = mapped_column(
        String(64), nullable=True, index=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship()
    opportunities: Mapped[list["Opportunity"]] = relationship(
        back_populates="signal"
    )

    __table_args__ = (
        Index("ix_signals_source_source_id", "source", "source_id", unique=True),
        Index("ix_signals_country_status", "country_code", "status"),
        Index("ix_signals_scores", "intent_score", "confidence"),
        Index("ix_signals_org", "organization_id"),
    )


class Opportunity(Base, TimestampMixin):
    """Validated commercial opportunities with intelligence scores."""
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    signal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("signals.id"), nullable=False
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True)

    # Intelligence scores
    intent_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    urgency: Mapped[str] = mapped_column(
        String(20), nullable=False, default=UrgencyLevel.MEDIUM
    )

    # Opportunity details
    buyer_name: Mapped[str] = mapped_column(String(255), nullable=True)
    buyer_organization: Mapped[str] = mapped_column(String(255), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    estimated_value_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_value_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    requirements: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)

    # Intelligence
    why_now: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    market_context: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=OpportunityStatus.DETECTED
    )

    # Relationships
    organization: Mapped["Organization"] = relationship()
    signal: Mapped["Signal"] = relationship(back_populates="opportunities")
    matches: Mapped[list["ProviderMatch"]] = relationship(
        back_populates="opportunity"
    )
    user_feedbacks: Mapped[list["UserFeedback"]] = relationship(
        back_populates="opportunity"
    )

    __table_args__ = (
        Index("ix_opps_country_category", "country_code", "category"),
        Index("ix_opps_scores", "intent_score", "confidence"),
        Index("ix_opps_status_urgency", "status", "urgency"),
        Index("ix_opps_deadline", "deadline"),
        Index("ix_opps_org", "organization_id"),
    )


class Provider(Base, TimestampMixin):
    """Businesses and individuals that can act on opportunities."""
    __tablename__ = "providers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    # Type: "business" or "individual"
    provider_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="business"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Business fields
    services: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    categories: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    min_project_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_project_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Individual fields
    skills: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    hourly_rate_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hourly_rate_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    availability: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # "full_time", "part_time", "contract", "weekends"
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Shared fields
    locations: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    country_codes: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="providers")
    matches: Mapped[list["ProviderMatch"]] = relationship(
        back_populates="provider"
    )

    __table_args__ = (
        Index("ix_providers_type", "provider_type"),
        Index("ix_providers_org_type", "organization_id", "provider_type"),
    )


class ProviderMatch(Base, TimestampMixin):
    """Matched opportunities to providers with explainable scores."""
    __tablename__ = "provider_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False
    )
    # Individual scores
    service_fit: Mapped[float] = mapped_column(Float, nullable=False)
    geographic_fit: Mapped[float] = mapped_column(Float, nullable=False)
    project_size_fit: Mapped[float] = mapped_column(Float, nullable=False)
    # Aggregate
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship(back_populates="matches")
    provider: Mapped["Provider"] = relationship(back_populates="matches")

    __table_args__ = (
        Index(
            "ix_provider_matches_unique",
            "opportunity_id",
            "provider_id",
            unique=True,
        ),
    )


class UserFeedback(Base, TimestampMixin):
    """User feedback for learning and scoring improvement."""
    __tablename__ = "user_feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False
    )
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_feedbacks")
    organization: Mapped["Organization"] = relationship(
        back_populates="user_feedbacks"
    )
    opportunity: Mapped["Opportunity"] = relationship(
        back_populates="user_feedbacks"
    )


class AuditLog(Base, TimestampMixin):
    """Audit trail for all significant actions."""
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        back_populates="audit_logs"
    )


class MarketTrend(Base, TimestampMixin):
    """Tracked market trends and demand patterns."""
    __tablename__ = "market_trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    signal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opportunity_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_intent_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    top_subcategories: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    metadata_extra: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index(
            "ix_market_trends_country_category_period",
            "country_code",
            "category",
            "period_start",
        ),
    )
