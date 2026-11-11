"""product parts_markup on orders, drop parts.markup

Revision ID: b3a8d1f42e07
Revises: a9c4e2f81b06
Create Date: 2026-11-11 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3a8d1f42e07"
down_revision: Union[str, Sequence[str], None] = "a9c4e2f81b06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("parts_markup", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute(
        sa.text(
            """
            UPDATE orders o
            SET parts_markup = COALESCE(
                (
                    SELECT p.markup
                    FROM order_blocks ob
                    JOIN parts p ON p.id = ob.part_id
                    WHERE ob.order_id = o.id
                      AND ob.position = 0
                    LIMIT 1
                ),
                0
            )
            """
        )
    )
    op.drop_column("parts", "markup")


def downgrade() -> None:
    op.add_column(
        "parts",
        sa.Column("markup", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute(
        sa.text(
            """
            UPDATE parts p
            SET markup = o.parts_markup
            FROM order_blocks ob
            JOIN orders o ON o.id = ob.order_id
            WHERE ob.part_id = p.id
            """
        )
    )
    op.drop_column("orders", "parts_markup")
