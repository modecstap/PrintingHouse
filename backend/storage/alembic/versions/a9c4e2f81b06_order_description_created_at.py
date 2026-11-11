"""order description and created_at

Revision ID: a9c4e2f81b06
Revises: e7f3a8912b04
Create Date: 2026-11-11 15:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9c4e2f81b06"
down_revision: Union[str, Sequence[str], None] = "e7f3a8912b04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "orders",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text("UPDATE orders SET created_at = (NOW() AT TIME ZONE 'UTC')"))
    op.alter_column("orders", "created_at", nullable=False)


def downgrade() -> None:
    op.drop_column("orders", "created_at")
    op.drop_column("orders", "description")
