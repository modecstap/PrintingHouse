"""chroma catalog table

Revision ID: d3e6f9a12b08
Revises: a1b2c3d4e5f6
Create Date: 2026-11-18 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d3e6f9a12b08"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chroma",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("cyan", sa.Integer(), nullable=False),
        sa.Column("magenta", sa.Integer(), nullable=False),
        sa.Column("yellow", sa.Integer(), nullable=False),
        sa.Column("black", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("chroma")