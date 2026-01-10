"""empty message

Revision ID: 92fc9c6b779d
Revises: 21da23b46f7b
Create Date: 2025-12-31 18:39:07.161073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92fc9c6b779d'
down_revision: Union[str, Sequence[str], None] = '21da23b46f7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаём таблицу economy
    op.create_table(
        'economy',
        sa.Column('id', sa.BigInteger(), sa.Identity(start=1), nullable=False),
        sa.Column('markup', sa.Numeric(precision=10, scale=4), nullable=False, comment='Наценка в %'),
        sa.Column('tax_rate', sa.Numeric(precision=10, scale=4), nullable=False, comment='Налоговая ставка (0,93 = 7%)'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Добавляем колонку economy_id в order (nullable на время миграции)
    op.add_column('order', sa.Column('economy_id', sa.BigInteger(), nullable=True))

    op.create_foreign_key(
        'fk_order_economy',
        'order',
        'economy',
        ['economy_id'],
        ['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    # 3. Перенос данных:
    #    создаём economy на основе production, привязанной к order
    op.execute("""
        INSERT INTO economy (markup, tax_rate)
        SELECT p.markup, p.tax_rate
        FROM production p
        JOIN "order" o ON o.production_id = p.id
    """)

    # 4. Проставляем order.economy_id
    #    В PostgreSQL безопасно использовать CTE + join по 1-к-1
    op.execute("""
        WITH economy_map AS (
            SELECT
                o.id AS order_id,
                e.id AS economy_id
            FROM "order" o
            JOIN production p ON p.id = o.production_id
            JOIN economy e
                ON e.markup = p.markup
               AND e.tax_rate = p.tax_rate
        )
        UPDATE "order" o
        SET economy_id = em.economy_id
        FROM economy_map em
        WHERE o.id = em.order_id
    """)

    # 5. (опционально, но правильно) делаем economy_id NOT NULL
    op.alter_column('order', 'economy_id', nullable=False)

    # 6. Удаляем колонки из production
    op.drop_column('production', 'markup')
    op.drop_column('production', 'tax_rate')



def downgrade() -> None:
    # 1. Возвращаем колонки в production
    op.add_column(
        'production',
        sa.Column(
            'markup',
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment='Наценка в %'
        )
    )
    op.add_column(
        'production',
        sa.Column(
            'tax_rate',
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment='Налоговая ставка (0,93 = 7%)'
        )
    )

    # 2. Переносим данные обратно из economy → production
    op.execute("""
        UPDATE production p
        SET
            markup = e.markup,
            tax_rate = e.tax_rate
        FROM "order" o
        JOIN economy e ON e.id = o.economy_id
        WHERE o.production_id = p.id
    """)

    # 3. Удаляем FK order → economy
    op.drop_constraint(
        'fk_order_economy',
        'order',
        type_='foreignkey'
    )

    # 4. Удаляем колонку economy_id из order
    op.drop_column('order', 'economy_id')

    # 5. Удаляем таблицу economy
    op.drop_table('economy')

