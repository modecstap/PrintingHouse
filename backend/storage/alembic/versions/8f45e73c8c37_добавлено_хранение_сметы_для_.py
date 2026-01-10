"""добавлено хранение сметы для многополосного тиража

Revision ID: 8f45e73c8c37
Revises: e7035bf7b3b8
Create Date: 2026-01-02 16:40:01.954836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f45e73c8c37'
down_revision: Union[str, Sequence[str], None] = 'e7035bf7b3b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Новая таблица для стоимости печати
    op.create_table(
        'printing_cost_report',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('items_per_sheet', sa.Integer(), nullable=False),
        sa.Column('sheet_count', sa.Integer(), nullable=False),
        sa.Column('unit_cost_price', sa.Numeric(), nullable=False),
        sa.Column('unit_cost', sa.Numeric(), nullable=False),
        sa.Column('edition_cost', sa.Numeric(), nullable=False),
        sa.Column('profit_before_tax', sa.Numeric(), nullable=False),
        sa.Column('profit_after_tax', sa.Numeric(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Добавляем FK в printing
    op.add_column(
        'printing',
        sa.Column('printing_cost_report_id', sa.BigInteger(), nullable=True)
    )

    # 3. Перенос данных:
    # cost_report <- order -> printing
    op.execute("""
        INSERT INTO printing_cost_report (
            id,
            items_per_sheet,
            sheet_count,
            unit_cost_price,
            unit_cost,
            edition_cost,
            profit_before_tax,
            profit_after_tax
        )
        SELECT
            cr.id,
            cr.items_per_sheet,
            cr.sheet_count,
            cr.unit_cost_price,
            cr.unit_cost,
            cr.edition_cost,
            cr.profit_before_tax,
            cr.profit_after_tax
        FROM printing p
        JOIN "order" o ON o.id = p.order_id
        JOIN cost_report cr ON cr.id = o.cost_report_id
    """)

    # 4. Проставляем printing.printing_cost_report_id
    op.execute("""
        UPDATE printing p
        SET printing_cost_report_id = cr.id
        FROM "order" o
        JOIN cost_report cr ON cr.id = o.cost_report_id
        WHERE o.id = p.order_id
    """)

    # 5. Внешний ключ
    op.create_foreign_key(
        None,
        'printing',
        'printing_cost_report',
        ['printing_cost_report_id'],
        ['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    # 6. Order больше не владеет cost_report
    op.drop_constraint(op.f('order_cost_report_id_fkey'), 'order', type_='foreignkey')
    op.drop_column('order', 'cost_report_id')

    # 7. order_id у printing теперь может быть nullable (как в твоей миграции)
    op.alter_column(
        'printing',
        'order_id',
        existing_type=sa.BIGINT(),
        nullable=True
    )

    # 8. Удаляем старую таблицу
    op.drop_table('cost_report')


def downgrade() -> None:
    pass
