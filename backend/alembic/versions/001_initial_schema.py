"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("enabled_countries", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_demo", sa.Boolean, default=False),
        sa.Column("settings", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Countries
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(2), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("signal_sources", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("settings", sa.JSON, nullable=False, server_default="{}"),
    )

    # Signals
    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("raw_data", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("normalized_data", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(50), nullable=False, server_default="raw"),
        sa.Column("intent_classification", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("extracted_data", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("intent_score", sa.Float, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dedup_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_signals_source_source_id", "signals", ["source", "source_id"], unique=True)
    op.create_index("ix_signals_country_status", "signals", ["country_code", "status"])
    op.create_index("ix_signals_scores", "signals", ["intent_score", "confidence"])
    op.create_index("ix_signals_dedup_hash", "signals", ["dedup_hash"])

    # Opportunities
    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signals.id"), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("intent_score", sa.Float, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("urgency", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("buyer_name", sa.String(255), nullable=True),
        sa.Column("buyer_organization", sa.String(255), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("estimated_value_min", sa.Float, nullable=True),
        sa.Column("estimated_value_max", sa.Float, nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requirements", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("why_now", sa.Text, nullable=True),
        sa.Column("recommended_action", sa.Text, nullable=True),
        sa.Column("evidence", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("market_context", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(50), nullable=False, server_default="detected"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_opps_country_category", "opportunities", ["country_code", "category"])
    op.create_index("ix_opps_scores", "opportunities", ["intent_score", "confidence"])
    op.create_index("ix_opps_status_urgency", "opportunities", ["status", "urgency"])
    op.create_index("ix_opps_deadline", "opportunities", ["deadline"])

    # Providers
    op.create_table(
        "providers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("services", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("categories", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("locations", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("country_codes", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("min_project_value", sa.Float, nullable=True),
        sa.Column("max_project_value", sa.Float, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Provider Matches
    op.create_table(
        "provider_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("opportunities.id"), nullable=False),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("service_fit", sa.Float, nullable=False),
        sa.Column("geographic_fit", sa.Float, nullable=False),
        sa.Column("project_size_fit", sa.Float, nullable=False),
        sa.Column("total_score", sa.Float, nullable=False),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_provider_matches_unique",
        "provider_matches",
        ["opportunity_id", "provider_id"],
        unique=True,
    )

    # User Feedbacks
    op.create_table(
        "user_feedbacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("opportunities.id"), nullable=False),
        sa.Column("feedback_type", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("outcome_value", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Market Trends
    op.create_table(
        "market_trends",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signal_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("opportunity_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_intent_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("avg_confidence", sa.Float, nullable=False, server_default="0"),
        sa.Column("growth_rate", sa.Float, nullable=False, server_default="0"),
        sa.Column("top_subcategories", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("metadata_extra", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_market_trends_country_category_period",
        "market_trends",
        ["country_code", "category", "period_start"],
    )


def downgrade() -> None:
    op.drop_table("market_trends")
    op.drop_table("audit_logs")
    op.drop_table("user_feedbacks")
    op.drop_table("provider_matches")
    op.drop_table("providers")
    op.drop_table("opportunities")
    op.drop_table("signals")
    op.drop_table("countries")
    op.drop_table("users")
    op.drop_table("organizations")
