"""Add provider_briefs table for shareable signed opportunity briefs.

Revision ID: 006
Revises: 005
Create Date: 2024-01-23 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add email and phone to providers table
    op.add_column("providers", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("providers", sa.Column("phone", sa.String(50), nullable=True))

    # Create provider_briefs table
    op.create_table(
        "provider_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("opportunities.id"), nullable=False),
        sa.Column("provider_match_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("provider_matches.id"), nullable=True),
        sa.Column("token", sa.String(128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("provider_name", sa.String(255), nullable=True),
        sa.Column("provider_email", sa.String(255), nullable=True),
        sa.Column("provider_message", sa.Text, nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Indexes are defined in the SQLAlchemy model (models.py)
    # op.create_index("ix_provider_briefs_token", "provider_briefs", ["token"])
    # op.create_index("ix_provider_briefs_org", "provider_briefs", ["organization_id"])


def downgrade() -> None:
    # Indexes are defined in the SQLAlchemy model (models.py)
    # op.drop_index("ix_provider_briefs_org", "provider_briefs")
    # op.drop_index("ix_provider_briefs_token", "provider_briefs")
    op.drop_table("provider_briefs")
    op.drop_column("providers", "phone")
    op.drop_column("providers", "email")
