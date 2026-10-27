"""add workplace order fields

Revision ID: b6d4e2a81c05
Revises: 733171f352dd
Create Date: 2026-10-27 17:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b6d4e2a81c05"
down_revision: Union[str, Sequence[str], None] = "733171f352dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Без server default: новую дату ставит процесс backend, не база.
    op.add_column(
        "workplace_order",
        sa.Column("creation_date", sa.Date(), nullable=True),
    )
    op.execute(sa.text(
        "UPDATE workplace_order "
        "SET creation_date = CURRENT_DATE "
        "WHERE creation_date IS NULL"
    ))
    op.alter_column("workplace_order", "creation_date", nullable=False)
    # Умолчание остаётся: уже сохранённые строки получают пустую строку.
    op.add_column(
        "workplace_operation_cost",
        sa.Column(
            "name",
            sa.Text(),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )
    op.add_column(
        "workplace_operation_cost",
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )
    op.add_column(
        "workplace_printing",
        sa.Column(
            "comment",
            sa.Text(),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )
    op.create_table(
        "workplace_reference",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("document", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_workplace_reference_id"),
    )


def downgrade() -> None:
    op.drop_table("workplace_reference")
    op.drop_column("workplace_printing", "comment")
    op.drop_column("workplace_operation_cost", "description")
    op.drop_column("workplace_operation_cost", "name")
    op.drop_column("workplace_order", "creation_date")
