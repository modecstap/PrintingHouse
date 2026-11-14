"""catalog id sequences

Revision ID: e8a1c4f92b07
Revises: d4f8b2c16a03
Create Date: 2026-11-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e8a1c4f92b07"
down_revision: Union[str, Sequence[str], None] = "d4f8b2c16a03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CATALOG_SEQUENCES: tuple[tuple[str, str], ...] = (
    ("printers", "printer_id_seq"),
    ("laminators", "laminator_id_seq"),
    ("cutters", "cutter_id_seq"),
    ("press_operators", "press_operator_id_seq"),
    ("laminator_operators", "laminator_operator_id_seq"),
    ("cutter_operators", "cutter_operator_id_seq"),
    ("die_cutter_operators", "die_cutter_operator_id_seq"),
)


def upgrade() -> None:
    for table, seq in _CATALOG_SEQUENCES:
        op.execute(
            sa.text(
                f"CREATE SEQUENCE {seq} "
                "START WITH 0 INCREMENT BY 1 MINVALUE 0"
            ),
        )
        op.execute(
            sa.text(
                f"""
                SELECT setval(
                    '{seq}',
                    COALESCE((SELECT MAX(id) FROM {table}), 0),
                    (SELECT MAX(id) FROM {table}) IS NOT NULL
                )
                """
            ),
        )


def downgrade() -> None:
    for _, seq in reversed(_CATALOG_SEQUENCES):
        op.execute(sa.text(f"DROP SEQUENCE IF EXISTS {seq}"))