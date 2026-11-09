"""add users

Revision ID: c8e4f2a91b03
Revises: 5f6bb8655c95
Create Date: 2026-11-09 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c8e4f2a91b03"
down_revision: Union[str, Sequence[str], None] = "5f6bb8655c95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    op.drop_table("users")
