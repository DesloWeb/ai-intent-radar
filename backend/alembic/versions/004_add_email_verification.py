"""Add email verification field to users table.

Revision ID: 004
Revises: 003
Create Date: 2024-01-25 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_email_verified column to users table
    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
    )

    # For demo/seed users, mark as verified (they're test accounts)
    op.execute(
        """
        UPDATE users 
        SET is_email_verified = true 
        WHERE email IN ('demo@radar.ai')
        """
    )


def downgrade() -> None:
    op.drop_column("users", "is_email_verified")
