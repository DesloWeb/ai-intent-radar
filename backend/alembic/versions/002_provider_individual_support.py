"""Add provider individual support and indexes.

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add provider_type column (business or individual)
    op.add_column(
        "providers",
        sa.Column("provider_type", sa.String(20), nullable=False, server_default="business"),
    )
    
    # Add individual/freelancer fields
    op.add_column(
        "providers",
        sa.Column("skills", sa.JSON, nullable=False, server_default="[]"),
    )
    op.add_column(
        "providers",
        sa.Column("hourly_rate_min", sa.Float, nullable=True),
    )
    op.add_column(
        "providers",
        sa.Column("hourly_rate_max", sa.Float, nullable=True),
    )
    op.add_column(
        "providers",
        sa.Column("availability", sa.String(50), nullable=True),
    )
    op.add_column(
        "providers",
        sa.Column("verified", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "providers",
        sa.Column("profile_url", sa.String(500), nullable=True),
    )
    
    # Add indexes for provider type filtering
    op.create_index("ix_providers_type", "providers", ["provider_type"])
    op.create_index(
        "ix_providers_org_type", "providers", ["organization_id", "provider_type"]
    )


def downgrade() -> None:
    op.drop_index("ix_providers_org_type", "providers")
    op.drop_index("ix_providers_type", "providers")
    op.drop_column("providers", "profile_url")
    op.drop_column("providers", "verified")
    op.drop_column("providers", "availability")
    op.drop_column("providers", "hourly_rate_max")
    op.drop_column("providers", "hourly_rate_min")
    op.drop_column("providers", "skills")
    op.drop_column("providers", "provider_type")
