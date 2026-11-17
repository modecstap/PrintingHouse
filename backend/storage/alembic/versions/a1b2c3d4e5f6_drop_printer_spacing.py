"""drop printer spacing column

Revision ID: a1b2c3d4e5f6
Revises: f7c3e9124a08
Create Date: 2026-11-17 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f7c3e9124a08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("printers", "spacing")


def downgrade() -> None:
    op.add_column("printers", sa.Column("spacing", sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE printers SET spacing = 0"))
    op.alter_column("printers", "spacing", nullable=False)