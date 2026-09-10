"""Add email_sent to provider_briefs for the Resend integration.

Revision ID: 007
Revises: 006
Create Date: 2026-09-10 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "provider_briefs",
        sa.Column("email_sent", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("provider_briefs", "email_sent")
