"""catalog name columns

Revision ID: c1e4a9b82f10
Revises: b3a8d1f42e07
Create Date: 2026-11-11 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1e4a9b82f10"
down_revision: Union[str, Sequence[str], None] = "b3a8d1f42e07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CATALOG_TABLES = (
    "printers",
    "laminators",
    "cutters",
    "press_operators",
    "laminator_operators",
    "cutter_operators",
    "die_cutter_operators",
)


def upgrade() -> None:
    for table in _CATALOG_TABLES:
        op.add_column(table, sa.Column("name", sa.Text(), nullable=True))
        op.execute(
            sa.text(f"UPDATE {table} SET name = '№ ' || id::text"),
        )
        op.alter_column(table, "name", nullable=False)


def downgrade() -> None:
    for table in reversed(_CATALOG_TABLES):
        op.drop_column(table, "name")
