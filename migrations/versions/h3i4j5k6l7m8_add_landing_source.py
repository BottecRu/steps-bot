"""add landing_source to users

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-02-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "h3i4j5k6l7m8"
down_revision = "g2h3i4j5k6l7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("landing_source", sa.String(120), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "landing_source")
