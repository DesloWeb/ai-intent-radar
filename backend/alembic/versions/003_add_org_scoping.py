"""Add organization_id to signals and opportunities for multi-tenant isolation.

Revision ID: 003
Revises: 002
Create Date: 2024-01-20 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add organization_id to signals table
    op.add_column(
        "signals",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=True,  # Start nullable for backfill
        ),
    )
    op.create_index("ix_signals_org", "signals", ["organization_id"])

    # Add organization_id to opportunities table
    op.add_column(
        "opportunities",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=True,  # Start nullable for backfill
        ),
    )
    op.create_index("ix_opps_org", "opportunities", ["organization_id"])

    # Backfill existing rows with the demo org (first org in the database)
    op.execute(
        """
        UPDATE signals 
        SET organization_id = (SELECT id FROM organizations ORDER BY created_at LIMIT 1)
        WHERE organization_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE opportunities 
        SET organization_id = (SELECT id FROM organizations ORDER BY created_at LIMIT 1)
        WHERE organization_id IS NULL
        """
    )

    # Now make columns non-nullable
    op.alter_column("signals", "organization_id", nullable=False)
    op.alter_column("opportunities", "organization_id", nullable=False)


def downgrade() -> None:
    op.drop_index("ix_opps_org", "opportunities")
    op.drop_column("opportunities", "organization_id")
    op.drop_index("ix_signals_org", "signals")
    op.drop_column("signals", "organization_id")
