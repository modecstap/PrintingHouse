"""add workplace order tables

Revision ID: 733171f352dd
Revises: 53a756fbc804
Create Date: 2026-10-25 01:44:38.628726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '733171f352dd'
down_revision: Union[str, Sequence[str], None] = '53a756fbc804'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workplace_order",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("unit_count", sa.BigInteger(), nullable=False),
        sa.Column("tax_rate", sa.Numeric(), nullable=False),
        sa.Column("markup", sa.Numeric(), nullable=False),
    )
    op.create_table(
        "workplace_operation_cost",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["workplace_order.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("order_id", "position"),
    )
    op.create_table(
        "workplace_printing",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("sheet_by_fitting", sa.BigInteger(), nullable=False),
        sa.Column("stack_height", sa.BigInteger(), nullable=False),
        sa.Column("press_sheet_density", sa.BigInteger(), nullable=False),
        sa.Column("press_sheet_width", sa.BigInteger(), nullable=False),
        sa.Column("press_sheet_height", sa.BigInteger(), nullable=False),
        sa.Column("press_sheet_spacing", sa.BigInteger(), nullable=False),
        sa.Column("list_width", sa.BigInteger(), nullable=False),
        sa.Column("list_height", sa.BigInteger(), nullable=False),
        sa.Column("list_bleeds", sa.BigInteger(), nullable=False),
        sa.Column("chroma", sa.String(length=64), nullable=False),
        sa.Column("lamination", sa.String(length=64), nullable=False),
        sa.Column("die_cutting", sa.Boolean(), nullable=False),
        sa.Column("press_cyan", sa.Numeric(), nullable=False),
        sa.Column("press_magenta", sa.Numeric(), nullable=False),
        sa.Column("press_yellow", sa.Numeric(), nullable=False),
        sa.Column("press_black", sa.Numeric(), nullable=False),
        sa.Column("press_paper", sa.Numeric(), nullable=False),
        sa.Column("press_salary", sa.Numeric(), nullable=False),
        sa.Column("cut_salary", sa.Numeric(), nullable=False),
        sa.Column("lamination_startup", sa.Numeric(), nullable=False),
        sa.Column("lamination_film_cost", sa.Numeric(), nullable=False),
        sa.Column("lamination_salary", sa.Numeric(), nullable=False),
        sa.Column("die_cut_salary", sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["workplace_order.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("order_id", "position"),
    )
    op.create_table(
        "workplace_cost_report",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("unit_cost_price", sa.Numeric(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(), nullable=False),
        sa.Column("edition_cost", sa.Numeric(), nullable=False),
        sa.Column("profit_after_tax", sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["workplace_order.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("order_id", "position"),
    )
    op.create_table(
        "workplace_printing_cost",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("cost_report_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("items_per_sheet", sa.BigInteger(), nullable=False),
        sa.Column("sheet_count", sa.BigInteger(), nullable=False),
        sa.Column("unit_cost_price", sa.Numeric(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(), nullable=False),
        sa.Column("edition_cost_price", sa.Numeric(), nullable=False),
        sa.Column("edition_cost", sa.Numeric(), nullable=False),
        sa.Column("profit_before_tax", sa.Numeric(), nullable=False),
        sa.Column("profit_after_tax", sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cost_report_id"],
            ["workplace_cost_report.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("cost_report_id", "position"),
    )
    op.execute(sa.text(
        """ALTER TABLE \"order\" ALTER COLUMN id SET DEFAULT nextval('order_id_seq')"""
    ))
    # На заполненной базе счётчик может отставать от max(id); двигать его только вперёд. setval не откатывается вместе с транзакцией Alembic. Повтор блока этого не портит: после продвижения следующее значение уже больше максимума, и второй проход ничего не меняет.
    _advance_lagging_sequence("order_id_seq", '"order"')
    _advance_lagging_sequence("printing_id_seq", "printing")
    _advance_lagging_sequence("printing_cost_report_id_seq", "printing_cost_report")


def _advance_lagging_sequence(sequence_name: str, table_name: str) -> None:
    op.execute(sa.text(
        f"""
        DO $$
        DECLARE
            max_id bigint;
            seq_last bigint;
            seq_called boolean;
            next_value bigint;
        BEGIN
            SELECT MAX(id) INTO max_id FROM {table_name};
            IF max_id IS NULL THEN
                RETURN;
            END IF;
            SELECT last_value, is_called
                INTO seq_last, seq_called
            FROM {sequence_name};
            IF seq_called THEN
                next_value := seq_last + 1;
            ELSE
                next_value := seq_last;
            END IF;
            IF next_value <= max_id THEN
                PERFORM setval('{sequence_name}', max_id, true);
            END IF;
        END $$;
        """
    ))


def downgrade() -> None:
    op.drop_table("workplace_printing_cost")
    op.drop_table("workplace_cost_report")
    op.drop_table("workplace_printing")
    op.drop_table("workplace_operation_cost")
    op.drop_table("workplace_order")
