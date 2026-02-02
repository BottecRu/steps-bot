"""drop_orders_pvz_fk

Revision ID: 2f995535d1e7
Revises: e8f9g0h1i2j3
Create Date: 2026-02-02 11:55:02.915468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f995535d1e7'
down_revision: Union[str, None] = 'e8f9g0h1i2j3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем foreign key constraint, который вызывал очистку pvz_id при удалении ПВЗ
    op.drop_constraint("fk_orders_pvz_id", "orders", type_="foreignkey")


def downgrade() -> None:
    # Восстанавливаем foreign key constraint (если нужно откатить)
    op.create_foreign_key(
        "fk_orders_pvz_id",
        "orders",
        "pvz",
        ["pvz_id"],
        ["id"],
        ondelete="SET NULL"
    )
