"""edges catalog

Revision ID: f7c3e9124a08
Revises: e8a1c4f92b07
Create Date: 2026-11-17 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f7c3e9124a08"
down_revision: Union[str, Sequence[str], None] = "e8a1c4f92b07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "edges",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("bleeds", sa.Integer(), nullable=False),
        sa.Column("spacing", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("parts", sa.Column("edges_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            INSERT INTO edges (name, bleeds, spacing)
            SELECT DISTINCT ''::text, bleeds, spacing FROM parts
            """,
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE parts AS p
            SET edges_id = e.id
            FROM edges AS e
            WHERE e.bleeds = p.bleeds
              AND e.spacing = p.spacing
              AND e.name = ''
            """,
        ),
    )
    op.alter_column("parts", "edges_id", nullable=False)
    op.create_foreign_key(
        "parts_edges_id_fkey",
        "parts",
        "edges",
        ["edges_id"],
        ["id"],
    )
    op.drop_column("parts", "bleeds")
    op.drop_column("parts", "spacing")


def downgrade() -> None:
    op.add_column(
        "parts",
        sa.Column("spacing", sa.Integer(), nullable=True),
    )
    op.add_column(
        "parts",
        sa.Column("bleeds", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE parts AS p
            SET bleeds = e.bleeds, spacing = e.spacing
            FROM edges AS e
            WHERE p.edges_id = e.id
            """,
        ),
    )
    op.alter_column("parts", "bleeds", nullable=False)
    op.alter_column("parts", "spacing", nullable=False)
    op.drop_constraint("parts_edges_id_fkey", "parts", type_="foreignkey")
    op.drop_column("parts", "edges_id")
    op.drop_table("edges")