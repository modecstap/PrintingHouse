"""add materials catalog

Revision ID: d4e8a2f71c05
Revises: c8e4f2a91b03
Create Date: 2026-11-10 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e8a2f71c05"
down_revision: Union[str, Sequence[str], None] = "c8e4f2a91b03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_MONEY = sa.Numeric(precision=18, scale=4)


def upgrade() -> None:
    op.create_table(
        "films",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("price", _MONEY, nullable=False),
        sa.Column("density", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sheets",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("paper_density", sa.Integer(), nullable=False),
        sa.Column("paper_thickness", sa.Integer(), nullable=False),
        sa.Column("paper_name", sa.Text(), nullable=False),
        sa.Column("paper_price_per_kilo", _MONEY, nullable=False),
        sa.Column("format_name", sa.Text(), nullable=False),
        sa.Column("format_height", sa.Integer(), nullable=False),
        sa.Column("format_width", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("parts", sa.Column("sheet_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "parts_sheet_id_fkey",
        "parts",
        "sheets",
        ["sheet_id"],
        ["id"],
    )
    op.drop_column("parts", "paper_density")
    op.drop_column("parts", "paper_thickness")
    op.drop_column("parts", "paper_name")
    op.drop_column("parts", "paper_price_per_kilo")
    op.drop_column("parts", "press_format_name")
    op.drop_column("parts", "press_format_height")
    op.drop_column("parts", "press_format_width")
    op.add_column("part_laminates", sa.Column("film_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "part_laminates_film_id_fkey",
        "part_laminates",
        "films",
        ["film_id"],
        ["id"],
    )
    op.drop_column("part_laminates", "film_name")
    op.drop_column("part_laminates", "film_price")
    op.drop_column("part_laminates", "film_density")


def downgrade() -> None:
    op.add_column(
        "part_laminates",
        sa.Column("film_density", sa.Integer(), nullable=False),
    )
    op.add_column(
        "part_laminates",
        sa.Column("film_price", _MONEY, nullable=False),
    )
    op.add_column(
        "part_laminates",
        sa.Column("film_name", sa.Text(), nullable=False),
    )
    op.drop_constraint("part_laminates_film_id_fkey", "part_laminates", type_="foreignkey")
    op.drop_column("part_laminates", "film_id")
    op.add_column(
        "parts",
        sa.Column("press_format_width", sa.Integer(), nullable=False),
    )
    op.add_column(
        "parts",
        sa.Column("press_format_height", sa.Integer(), nullable=False),
    )
    op.add_column(
        "parts",
        sa.Column("press_format_name", sa.Text(), nullable=False),
    )
    op.add_column(
        "parts",
        sa.Column("paper_price_per_kilo", _MONEY, nullable=False),
    )
    op.add_column(
        "parts",
        sa.Column("paper_name", sa.Text(), nullable=False),
    )
    op.add_column(
        "parts",
        sa.Column("paper_thickness", sa.Integer(), nullable=False),
    )
    op.add_column(
        "parts",
        sa.Column("paper_density", sa.Integer(), nullable=False),
    )
    op.drop_constraint("parts_sheet_id_fkey", "parts", type_="foreignkey")
    op.drop_column("parts", "sheet_id")
    op.drop_table("sheets")
    op.drop_table("films")
