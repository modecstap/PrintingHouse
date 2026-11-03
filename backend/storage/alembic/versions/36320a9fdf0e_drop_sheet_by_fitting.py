"""drop sheet by fitting

Revision ID: 36320a9fdf0e
Revises: 53df464e9eb6
Create Date: 2026-11-04 01:40:40.346575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection


# revision identifiers, used by Alembic.
revision: str = "36320a9fdf0e"
down_revision: Union[str, Sequence[str], None] = "53df464e9eb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _strip_reference()
    op.drop_column("printing", "sheet_by_fitting")


def downgrade() -> None:
    # Апгрейд удалил старые количества, поэтому восстановленное значение равно 0.
    _restore_reference()
    op.add_column(
        "printing",
        sa.Column(
            "sheet_by_fitting",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )
    op.alter_column("printing", "sheet_by_fitting", server_default=None)


def _strip_reference() -> None:
    connection = op.get_bind()
    document = _reference_document(connection)
    if document is None:
        return
    printings = document.get("printings")
    if printings is None:
        return
    if type(printings) is not list:
        raise RuntimeError("sheet by fitting: reference printings are not a list")
    rewritten = [_without_sheet_by_fitting(item) for item in printings]
    updated = dict(document)
    updated["printings"] = rewritten
    _store_reference(connection, updated)


def _restore_reference() -> None:
    connection = op.get_bind()
    document = _reference_document(connection)
    if document is None:
        return
    printings = document.get("printings")
    if printings is None:
        return
    if type(printings) is not list:
        raise RuntimeError("sheet by fitting: reference printings are not a list")
    restored = [_with_sheet_by_fitting(item) for item in printings]
    updated = dict(document)
    updated["printings"] = restored
    _store_reference(connection, updated)


def _reference_document(connection: Connection) -> dict[str, object] | None:
    row = connection.execute(sa.text(
        "SELECT document FROM reference WHERE id = 1"
    )).scalar_one_or_none()
    if row is None:
        return None
    if type(row) is not dict:
        raise RuntimeError("sheet by fitting: reference document is not an object")
    return row


def _without_sheet_by_fitting(item: object) -> dict[str, object]:
    if type(item) is not dict:
        raise RuntimeError("sheet by fitting: reference printing is not an object")
    stored = dict(item)
    stored.pop("sheet_by_fitting", None)
    return stored


def _with_sheet_by_fitting(item: object) -> dict[str, object]:
    if type(item) is not dict:
        raise RuntimeError("sheet by fitting: reference printing is not an object")
    stored = dict(item)
    if "sheet_by_fitting" not in stored:
        stored["sheet_by_fitting"] = 0
    return stored


def _store_reference(
    connection: Connection, document: dict[str, object]
) -> None:
    connection.execute(
        sa.text(
            "UPDATE reference SET document = :document WHERE id = 1"
        ).bindparams(sa.bindparam("document", type_=postgresql.JSONB)),
        {"document": document},
    )
