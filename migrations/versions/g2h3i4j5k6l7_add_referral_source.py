"""add referral_source to referrals

Revision ID: g2h3i4j5k6l7
Revises: f1g2h3i4j5k6
Create Date: 2026-02-16

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "g2h3i4j5k6l7"
down_revision = "f1g2h3i4j5k6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "referrals",
        sa.Column("referral_source", sa.String(120), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("referrals", "referral_source")
