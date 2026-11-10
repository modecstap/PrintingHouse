"""paper thickness numeric

Revision ID: e7f3a8912b04
Revises: d4e8a2f71c05
Create Date: 2026-11-11 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7f3a8912b04"
down_revision: Union[str, Sequence[str], None] = "d4e8a2f71c05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "sheets",
        "paper_thickness",
        type_=sa.Numeric(6, 2),
        existing_type=sa.Integer(),
        postgresql_using="paper_thickness::numeric",
    )


def downgrade() -> None:
    op.alter_column(
        "sheets",
        "paper_thickness",
        type_=sa.Integer(),
        existing_type=sa.Numeric(6, 2),
        postgresql_using="paper_thickness::integer",
    )
