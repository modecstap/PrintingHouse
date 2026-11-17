"""chroma catalog and part_prints.chroma_id

Revision ID: c2d5e8f91a07
Revises: a1b2c3d4e5f6
Create Date: 2026-11-18 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c2d5e8f91a07"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LEGACY_CHROMA_TO_PRESET: tuple[tuple[str, str], ...] = (
    ("ZERO_ZERO", "0+0"),
    ("ONE_ZERO", "1+0"),
    ("ONE_ONE", "1+1"),
    ("FOUR_ZERO", "4+0"),
    ("FOUR_ONE", "4+1"),
    ("FOUR_FOUR", "4+4"),
)

_PRESET_FILLS: tuple[tuple[str, int, int, int, int], ...] = (
    ("0+0", 0, 0, 0, 0),
    ("1+0", 0, 0, 0, 100),
    ("1+1", 0, 0, 0, 200),
    ("4+0", 100, 100, 100, 100),
    ("4+1", 100, 100, 100, 200),
    ("4+4", 200, 200, 200, 200),
)

_FILL_TO_LEGACY: dict[tuple[int, int, int, int], str] = {
    (0, 0, 0, 0): "ZERO_ZERO",
    (0, 0, 0, 100): "ONE_ZERO",
    (0, 0, 0, 200): "ONE_ONE",
    (100, 100, 100, 100): "FOUR_ZERO",
    (100, 100, 100, 200): "FOUR_ONE",
    (200, 200, 200, 200): "FOUR_FOUR",
}


def _abort_if_null(
    connection: sa.Connection,
    *,
    column: str,
    table: str = "part_prints",
) -> None:
    count = connection.execute(
        sa.text(
            f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL",
        ),
    ).scalar_one()
    if count:
        raise RuntimeError(
            f"{table}.{column} has {count} rows that could not be migrated",
        )


def upgrade() -> None:
    op.create_table(
        "chroma",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("cyan", sa.Integer(), nullable=False),
        sa.Column("magenta", sa.Integer(), nullable=False),
        sa.Column("yellow", sa.Integer(), nullable=False),
        sa.Column("black", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    connection = op.get_bind()
    for name, cyan, magenta, yellow, black in _PRESET_FILLS:
        connection.execute(
            sa.text(
                """
                INSERT INTO chroma (name, cyan, magenta, yellow, black)
                VALUES (:name, :cyan, :magenta, :yellow, :black)
                """,
            ),
            {
                "name": name,
                "cyan": cyan,
                "magenta": magenta,
                "yellow": yellow,
                "black": black,
            },
        )
    op.add_column(
        "part_prints",
        sa.Column("chroma_id", sa.Integer(), nullable=True),
    )
    for legacy, preset_name in _LEGACY_CHROMA_TO_PRESET:
        connection.execute(
            sa.text(
                """
                UPDATE part_prints AS pp
                SET chroma_id = c.id
                FROM chroma AS c
                WHERE pp.chroma = :legacy
                  AND c.name = :preset_name
                """,
            ),
            {"legacy": legacy, "preset_name": preset_name},
        )
    _abort_if_null(connection, column="chroma_id")
    op.alter_column("part_prints", "chroma_id", nullable=False)
    op.create_foreign_key(
        "part_prints_chroma_id_fkey",
        "part_prints",
        "chroma",
        ["chroma_id"],
        ["id"],
    )
    op.drop_column("part_prints", "chroma")


def downgrade() -> None:
    connection = op.get_bind()
    op.add_column(
        "part_prints",
        sa.Column("chroma", sa.Text(), nullable=True),
    )
    for fills, legacy in _FILL_TO_LEGACY.items():
        cyan, magenta, yellow, black = fills
        connection.execute(
            sa.text(
                """
                UPDATE part_prints AS pp
                SET chroma = :legacy
                FROM chroma AS c
                WHERE pp.chroma_id = c.id
                  AND c.cyan = :cyan
                  AND c.magenta = :magenta
                  AND c.yellow = :yellow
                  AND c.black = :black
                """,
            ),
            {
                "legacy": legacy,
                "cyan": cyan,
                "magenta": magenta,
                "yellow": yellow,
                "black": black,
            },
        )
    _abort_if_null(connection, column="chroma")
    op.alter_column("part_prints", "chroma", nullable=False)
    op.drop_constraint(
        "part_prints_chroma_id_fkey",
        "part_prints",
        type_="foreignkey",
    )
    op.drop_column("part_prints", "chroma_id")
    op.drop_table("chroma")