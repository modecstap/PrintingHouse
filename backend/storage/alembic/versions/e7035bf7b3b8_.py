"""empty message

Revision ID: e7035bf7b3b8
Revises: e0d6cef6ab55
Create Date: 2026-01-01 22:51:01.541988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7035bf7b3b8'
down_revision: Union[str, Sequence[str], None] = 'e0d6cef6ab55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. создаём таблицу printing ---
    op.create_table(
        'printing',
        sa.Column(
            'id',
            sa.BigInteger(),
            sa.Identity(always=False),
            primary_key=True
        ),
        sa.Column(
            'order_id',
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            'production_id',
            sa.BigInteger(),
            nullable=True
        ),
        sa.Column(
            'edition_id',
            sa.BigInteger(),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ['order_id'],
            ['order.id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['production_id'],
            ['production.id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['edition_id'],
            ['edition.id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
    )

    # --- 2. переносим существующие связи order → printing ---
    # для каждого order создаётся ровно одна запись
    op.execute("""
        INSERT INTO printing (order_id, production_id, edition_id)
        SELECT
            id AS order_id,
            production_id,
            edition_id
        FROM "order"
        WHERE production_id IS NOT NULL
           OR edition_id IS NOT NULL
    """)

    # --- 3. удаляем старые FK ---
    op.drop_constraint(
        op.f('order_edition_id_fkey'),
        'order',
        type_='foreignkey'
    )
    op.drop_constraint(
        op.f('order_production_id_fkey'),
        'order',
        type_='foreignkey'
    )

    # --- 4. удаляем колонки ---
    op.drop_column('order', 'production_id')
    op.drop_column('order', 'edition_id')


def downgrade() -> None:
    # --- 1. возвращаем колонки ---
    op.add_column(
        'order',
        sa.Column('production_id', sa.BigInteger(), nullable=True)
    )
    op.add_column(
        'order',
        sa.Column('edition_id', sa.BigInteger(), nullable=True)
    )

    # --- 2. восстанавливаем данные ---
    # ВНИМАНИЕ:
    # если у order было несколько printing — берём первую (по id)
    op.execute("""
        UPDATE "order" o
        SET
            production_id = p.production_id,
            edition_id = p.edition_id
        FROM (
            SELECT DISTINCT ON (order_id)
                order_id,
                production_id,
                edition_id
            FROM printing
            ORDER BY order_id, id
        ) p
        WHERE o.id = p.order_id
    """)

    # --- 3. восстанавливаем FK ---
    op.create_foreign_key(
        op.f('order_production_id_fkey'),
        'order',
        'production',
        ['production_id'],
        ['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        op.f('order_edition_id_fkey'),
        'order',
        'edition',
        ['edition_id'],
        ['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    # --- 4. удаляем таблицу printing ---
    op.drop_table('printing')