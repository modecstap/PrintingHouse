"""copy unique sheet tuples into the sheet catalog

Revision ID: 53df464e9eb6
Revises: 9d3f6a2c1b7e
Create Date: 2026-11-03 14:13:11.379725

"""
from decimal import Decimal
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection


# revision identifiers, used by Alembic.
revision: str = "53df464e9eb6"
down_revision: Union[str, Sequence[str], None] = "9d3f6a2c1b7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sheet",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("height", sa.BigInteger(), nullable=False),
        sa.Column("width", sa.BigInteger(), nullable=False),
        sa.Column("density", sa.BigInteger(), nullable=False),
        sa.Column("cost", sa.Numeric(), nullable=False),
        sa.UniqueConstraint("height", "width", "density", "cost"),
    )
    _copy_sheet_rows()
    op.add_column(
        "printing",
        sa.Column("sheet_id", sa.BigInteger(), nullable=True),
    )
    _fill_printing_sheet_id()
    op.alter_column("printing", "sheet_id", nullable=False)
    op.create_foreign_key(
        "printing_sheet_id_fkey",
        "printing",
        "sheet",
        ["sheet_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.drop_column("printing", "press_sheet_density")
    op.drop_column("printing", "press_sheet_width")
    op.drop_column("printing", "press_sheet_height")
    op.drop_column("printing", "press_paper")
    op.alter_column(
        "printing",
        "press_sheet_spacing",
        new_column_name="spacing",
    )
    _rewrite_reference()


def downgrade() -> None:
    op.add_column(
        "printing",
        sa.Column("press_sheet_density", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "printing",
        sa.Column("press_sheet_width", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "printing",
        sa.Column("press_sheet_height", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "printing",
        sa.Column("press_paper", sa.Numeric(), nullable=True),
    )
    op.alter_column(
        "printing",
        "spacing",
        new_column_name="press_sheet_spacing",
    )
    _restore_printing_sheet_columns()
    op.alter_column("printing", "press_sheet_density", nullable=False)
    op.alter_column("printing", "press_sheet_width", nullable=False)
    op.alter_column("printing", "press_sheet_height", nullable=False)
    op.alter_column("printing", "press_paper", nullable=False)
    _restore_reference()
    op.drop_constraint(
        "printing_sheet_id_fkey",
        "printing",
        type_="foreignkey",
    )
    op.drop_column("printing", "sheet_id")
    op.drop_table("sheet")


def _copy_sheet_rows() -> None:
    # Высота и ширина не меняются местами: 320×450 и 450×320 остаются разными.
    op.execute(sa.text(
        """
        INSERT INTO sheet (version, name, height, width, density, cost)
        SELECT 0,
               height::text || ' x ' || width::text,
               height,
               width,
               density,
               cost
        FROM (
            SELECT press_sheet_height AS height,
                   press_sheet_width AS width,
                   press_sheet_density AS density,
                   press_paper AS cost
            FROM printing
            UNION
            SELECT (item -> 'press_sheet' ->> 'height')::bigint,
                   (item -> 'press_sheet' ->> 'width')::bigint,
                   (item -> 'press_sheet' ->> 'density')::bigint,
                   (item -> 'press_pricing' ->> 'paper')::numeric
            FROM reference AS ref
            CROSS JOIN LATERAL jsonb_array_elements(
                CASE
                    WHEN jsonb_typeof(ref.document -> 'printings') = 'array'
                    THEN ref.document -> 'printings'
                    ELSE '[]'::jsonb
                END
            ) AS printing_item(item)
        ) AS sheet_tuple
        """
    ))


def _fill_printing_sheet_id() -> None:
    op.execute(sa.text(
        """
        UPDATE printing AS printing_row
        SET sheet_id = sheet_row.id
        FROM sheet AS sheet_row
        WHERE printing_row.press_sheet_height = sheet_row.height
          AND printing_row.press_sheet_width = sheet_row.width
          AND printing_row.press_sheet_density = sheet_row.density
          AND printing_row.press_paper = sheet_row.cost
        """
    ))


def _restore_printing_sheet_columns() -> None:
    op.execute(sa.text(
        """
        UPDATE printing AS printing_row
        SET press_sheet_height = sheet_row.height,
            press_sheet_width = sheet_row.width,
            press_sheet_density = sheet_row.density,
            press_paper = sheet_row.cost
        FROM sheet AS sheet_row
        WHERE printing_row.sheet_id = sheet_row.id
        """
    ))


def _rewrite_reference() -> None:
    connection = op.get_bind()
    document = _reference_document(connection)
    if document is None:
        return
    printings = document.get("printings")
    if printings is None:
        return
    if type(printings) is not list:
        raise RuntimeError("sheet catalog: reference printings are not a list")
    rewritten = [
        _printing_with_sheet_id(connection, item) for item in printings
    ]
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
        raise RuntimeError("sheet catalog: reference printings are not a list")
    restored = [
        _printing_with_sheet_object(connection, item) for item in printings
    ]
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
        raise RuntimeError("sheet catalog: reference document is not an object")
    return row


def _printing_with_sheet_id(
    connection: Connection, item: object
) -> dict[str, object]:
    if type(item) is not dict:
        raise RuntimeError("sheet catalog: reference printing is not an object")
    sheet = item.get("press_sheet")
    pricing = item.get("press_pricing")
    if type(sheet) is not dict:
        raise RuntimeError("sheet catalog: reference press_sheet is not an object")
    if type(pricing) is not dict:
        raise RuntimeError(
            "sheet catalog: reference press_pricing is not an object"
        )
    paper = pricing.get("paper")
    if type(paper) is not str:
        raise RuntimeError("sheet catalog: reference paper is not a string")
    height = int(sheet["height"])
    width = int(sheet["width"])
    density = int(sheet["density"])
    spacing = int(sheet["spacing"])
    sheet_id = connection.execute(sa.text(
        """
        SELECT id FROM sheet
        WHERE height = :height
          AND width = :width
          AND density = :density
          AND cost = :cost
        """
    ), {
        "height": height,
        "width": width,
        "density": density,
        "cost": Decimal(paper),
    }).scalar_one()
    stored = dict(item)
    stored["press_sheet"] = int(sheet_id)
    stored["spacing"] = spacing
    rates = dict(pricing)
    del rates["paper"]
    stored["press_pricing"] = rates
    return stored


def _printing_with_sheet_object(
    connection: Connection, item: object
) -> dict[str, object]:
    if type(item) is not dict:
        raise RuntimeError("sheet catalog: reference printing is not an object")
    sheet_id = item.get("press_sheet")
    spacing = item.get("spacing")
    pricing = item.get("press_pricing")
    if type(sheet_id) is not int:
        raise RuntimeError("sheet catalog: reference press_sheet is not an id")
    if type(spacing) is not int:
        raise RuntimeError("sheet catalog: reference spacing is not an integer")
    if type(pricing) is not dict:
        raise RuntimeError(
            "sheet catalog: reference press_pricing is not an object"
        )
    row = connection.execute(sa.text(
        """
        SELECT height, width, density, cost
        FROM sheet
        WHERE id = :id
        """
    ), {"id": sheet_id}).one()
    stored = dict(item)
    del stored["spacing"]
    rates = dict(pricing)
    rates["paper"] = str(row.cost)
    stored["press_pricing"] = rates
    stored["press_sheet"] = {
        "density": int(row.density),
        "width": int(row.width),
        "height": int(row.height),
        "spacing": spacing,
    }
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
