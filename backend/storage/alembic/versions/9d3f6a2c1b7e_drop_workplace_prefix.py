"""drop workplace prefix

Revision ID: 9d3f6a2c1b7e
Revises: e7b3c91a04d6
Create Date: 2026-11-02 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d3f6a2c1b7e"
down_revision: Union[str, Sequence[str], None] = "e7b3c91a04d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Имена ограничений и счётчиков — умолчания Postgres из 733171f352dd и b6d4e2a81c05.
_RENAMES = (
    (
        "workplace_order",
        "order",
        (("workplace_order_pkey", "order_pkey"),),
        ("workplace_order_id_seq", "order_id_seq"),
    ),
    (
        "workplace_operation_cost",
        "operation_cost",
        (
            ("workplace_operation_cost_pkey", "operation_cost_pkey"),
            ("workplace_operation_cost_order_id_fkey", "operation_cost_order_id_fkey"),
            (
                "workplace_operation_cost_order_id_position_key",
                "operation_cost_order_id_position_key",
            ),
        ),
        ("workplace_operation_cost_id_seq", "operation_cost_id_seq"),
    ),
    (
        "workplace_printing",
        "printing",
        (
            ("workplace_printing_pkey", "printing_pkey"),
            ("workplace_printing_order_id_fkey", "printing_order_id_fkey"),
            (
                "workplace_printing_order_id_position_key",
                "printing_order_id_position_key",
            ),
        ),
        ("workplace_printing_id_seq", "printing_id_seq"),
    ),
    (
        "workplace_cost_report",
        "cost_report",
        (
            ("workplace_cost_report_pkey", "cost_report_pkey"),
            ("workplace_cost_report_order_id_fkey", "cost_report_order_id_fkey"),
            (
                "workplace_cost_report_order_id_position_key",
                "cost_report_order_id_position_key",
            ),
        ),
        ("workplace_cost_report_id_seq", "cost_report_id_seq"),
    ),
    (
        "workplace_printing_cost",
        "printing_cost",
        (
            ("workplace_printing_cost_pkey", "printing_cost_pkey"),
            (
                "workplace_printing_cost_cost_report_id_fkey",
                "printing_cost_cost_report_id_fkey",
            ),
            (
                "workplace_printing_cost_cost_report_id_position_key",
                "printing_cost_cost_report_id_position_key",
            ),
        ),
        ("workplace_printing_cost_id_seq", "printing_cost_id_seq"),
    ),
    (
        "workplace_reference",
        "reference",
        (
            ("workplace_reference_pkey", "reference_pkey"),
            ("ck_workplace_reference_id", "ck_reference_id"),
        ),
        ("workplace_reference_id_seq", "reference_id_seq"),
    ),
)


def upgrade() -> None:
    for old_table, new_table, constraints, (old_seq, new_seq) in _RENAMES:
        _rename(old_table, new_table, constraints, old_seq, new_seq)


def downgrade() -> None:
    for old_table, new_table, constraints, (old_seq, new_seq) in _RENAMES:
        _rename(
            new_table,
            old_table,
            tuple((new, old) for old, new in constraints),
            new_seq,
            old_seq,
        )


def _rename(
    table: str,
    renamed_table: str,
    constraints: tuple[tuple[str, str], ...],
    sequence: str,
    renamed_sequence: str,
) -> None:
    # order — зарезервированное слово SQL, поэтому все идентификаторы в кавычках.
    op.execute(sa.text(f'ALTER TABLE "{table}" RENAME TO "{renamed_table}"'))
    for name, renamed in constraints:
        op.execute(sa.text(
            f'ALTER TABLE "{renamed_table}" RENAME CONSTRAINT "{name}" TO "{renamed}"'
        ))
    op.execute(sa.text(
        f'ALTER SEQUENCE "{sequence}" RENAME TO "{renamed_sequence}"'
    ))
