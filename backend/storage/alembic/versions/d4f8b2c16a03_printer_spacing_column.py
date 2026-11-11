"""printer spacing column

Revision ID: d4f8b2c16a03
Revises: c1e4a9b82f10
Create Date: 2026-11-11 20:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4f8b2c16a03"
down_revision: Union[str, Sequence[str], None] = "c1e4a9b82f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("printers", sa.Column("spacing", sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE printers SET spacing = 0"))
    op.alter_column("printers", "spacing", nullable=False)


def downgrade() -> None:
    op.drop_column("printers", "spacing")
