"""Add source_url to opportunities table.

Revision ID: 005
Revises: 004
Create Date: 2024-01-22 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "opportunities",
        sa.Column("source_url", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("opportunities", "source_url")
