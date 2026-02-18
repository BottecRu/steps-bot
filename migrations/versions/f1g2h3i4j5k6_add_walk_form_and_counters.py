"""add walk_form to ledger_entries and walk_count_* to users

Revision ID: f1g2h3i4j5k6
Revises: 2f995535d1e7
Create Date: 2026-02-16

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg


revision = "f1g2h3i4j5k6"
down_revision = "2f995535d1e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    walkform = pg.ENUM("stroller", "dog", "stroller_dog", name="walkform", create_type=False)
    op.add_column(
        "ledger_entries",
        sa.Column("walk_form", walkform, nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("walk_count_stroller", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("walk_count_dog", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("walk_count_stroller_dog", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("users", "walk_count_stroller_dog")
    op.drop_column("users", "walk_count_dog")
    op.drop_column("users", "walk_count_stroller")
    op.drop_column("ledger_entries", "walk_form")
