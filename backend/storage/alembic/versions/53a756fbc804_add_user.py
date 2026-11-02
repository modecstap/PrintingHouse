"""Базовая схема до таблиц workplace.

Revision ID: 53a756fbc804
Revises:
Create Date: 2026-06-13 18:27:27.634930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "53a756fbc804"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CHROMA = ("ZERO_ZERO", "ONE_ZERO", "ONE_ONE", "FOUR_ZERO", "FOUR_ONE", "FOUR_FOUR")
_LAMINATION = ("DONT", "ONE_ZERO", "ONE_ONE")
_ORDER_STATUS = ("SAVED", "IN_WORK", "DONE")
_PERMISSION = ("FULL", "READ", "WRITE", "DELETE", "NONE")

_EXPLICIT_SEQUENCES = (
    "cost_report_id_seq",
    "cutter_info_id_seq",
    "edition_id_seq",
    "list_size_id_seq",
    "order_id_seq",
    "press_sheet_id_seq",
    "printing_cost_report_id_seq",
    "production_id_seq",
    "user_id_seq",
)

_UNOWNED_SEQUENCES = (
    "cost_report_id_seq",
    "cutter_info_id_seq",
    "edition_id_seq",
    "list_size_id_seq",
    "order_id_seq",
    "press_sheet_id_seq",
    "production_id_seq",
    "user_id_seq",
)


def _create_enum(name: str, labels: tuple[str, ...]) -> None:
    postgresql.ENUM(*labels, name=name).create(op.get_bind(), checkfirst=False)


def _enum(name: str, labels: tuple[str, ...]) -> postgresql.ENUM:
    return postgresql.ENUM(*labels, name=name, create_type=False)


def _create_sequence(name: str) -> None:
    op.execute(sa.text(
        f"CREATE SEQUENCE {name} "
        "START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1"
    ))


def _sequence_id(sequence_name: str) -> sa.Column:
    return sa.Column(
        "id",
        sa.BigInteger(),
        server_default=sa.text(f"nextval('{sequence_name}')"),
        nullable=False,
    )


def _identity_id() -> sa.Column:
    return sa.Column(
        "id",
        sa.BigInteger(),
        sa.Identity(always=False, start=1),
        nullable=False,
    )


def _foreign_key(name: str, column: str, target: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(
        [column],
        [target],
        name=name,
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def upgrade() -> None:
    _create_enum("chroma", _CHROMA)
    _create_enum("lamination", _LAMINATION)
    _create_enum("order_status", _ORDER_STATUS)
    _create_enum("permission", _PERMISSION)
    for name in _EXPLICIT_SEQUENCES:
        _create_sequence(name)

    op.create_table(
        "cutter_info",
        _sequence_id("cutter_info_id_seq"),
        sa.Column(
            "stack_height",
            sa.Integer(),
            nullable=False,
            comment="Высота стопки помещающейся в резаке в мм",
        ),
        sa.PrimaryKeyConstraint("id", name="cutter_info_pkey"),
    )
    op.create_table(
        "economy",
        _identity_id(),
        sa.Column(
            "markup",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Наценка в %",
        ),
        sa.Column(
            "tax_rate",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Налоговая ставка (0,93 = 7%)",
        ),
        sa.PrimaryKeyConstraint("id", name="economy_pkey"),
    )
    op.create_table(
        "list_size",
        _sequence_id("list_size_id_seq"),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("bleeds", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="list_size_pkey"),
    )
    op.create_table(
        "edition",
        _sequence_id("edition_id_seq"),
        sa.Column("list_size_id", sa.BigInteger(), nullable=True),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("density", sa.Integer(), nullable=False),
        sa.Column("chroma", _enum("chroma", _CHROMA), nullable=False),
        sa.Column("lamination", _enum("lamination", _LAMINATION), nullable=False),
        sa.Column("die_cutting", sa.Boolean(), nullable=False),
        _foreign_key("edition_list_size_id_fkey", "list_size_id", "list_size.id"),
        sa.PrimaryKeyConstraint("id", name="edition_pkey"),
    )
    op.create_table(
        "press_sheet",
        _sequence_id("press_sheet_id_seq"),
        sa.Column("height", sa.Integer(), nullable=False, comment="Высота в мм"),
        sa.Column("width", sa.Integer(), nullable=False, comment="Ширина в мм"),
        sa.Column("spacing", sa.Integer(), nullable=False, comment="Поля в мм"),
        sa.PrimaryKeyConstraint("id", name="press_sheet_pkey"),
    )
    op.create_table(
        "production",
        _sequence_id("production_id_seq"),
        sa.Column("press_sheet_id", sa.BigInteger(), nullable=False),
        sa.Column("cutter_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "black_ink_cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Стоимость чёрной краски на 1 листе в руб.",
        ),
        sa.Column(
            "ink_cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Стоимость всех красок на 1 листе в руб.",
        ),
        sa.Column(
            "printer_salary",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Зарплата печатнику за 1 лист в руб.",
        ),
        sa.Column(
            "lamination_cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Цена ламинации 1 листа в руб.",
        ),
        sa.Column(
            "die_cutting_cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Стоимость высечки 1 листа в руб.",
        ),
        sa.Column(
            "paper_cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Стоимость 1кг бумаги в руб.",
        ),
        sa.Column(
            "cutting_cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Цена 1 реза в руб.",
        ),
        sa.Column(
            "sheet_by_fitting",
            sa.Integer(),
            nullable=False,
            comment="Количество листов на приладку в шт.",
        ),
        _foreign_key(
            "production_press_sheet_id_fkey",
            "press_sheet_id",
            "press_sheet.id",
        ),
        _foreign_key("production_cutter_id_fkey", "cutter_id", "cutter_info.id"),
        sa.PrimaryKeyConstraint("id", name="production_pkey"),
    )
    op.create_table(
        "production_reference",
        _identity_id(),
        sa.Column("production_id", sa.BigInteger(), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=True),
        _foreign_key(
            "production_reference_production_id_fkey",
            "production_id",
            "production.id",
        ),
        sa.PrimaryKeyConstraint("id", name="production_reference_pkey"),
    )
    op.create_table(
        "order_cost_report",
        _sequence_id("cost_report_id_seq"),
        sa.Column("unit_cost_price", sa.Numeric(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(), nullable=False),
        sa.Column("edition_cost", sa.Numeric(), nullable=False),
        sa.Column("profit_after_tax", sa.Numeric(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="order_cost_report_pkey"),
    )
    op.create_table(
        "printing_cost_report",
        _sequence_id("printing_cost_report_id_seq"),
        sa.Column("items_per_sheet", sa.Integer(), nullable=False),
        sa.Column("sheet_count", sa.Integer(), nullable=False),
        sa.Column("unit_cost_price", sa.Numeric(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(), nullable=False),
        sa.Column("edition_cost", sa.Numeric(), nullable=False),
        sa.Column("profit_before_tax", sa.Numeric(), nullable=False),
        sa.Column("profit_after_tax", sa.Numeric(), nullable=False),
        sa.Column("edition_cost_price", sa.Numeric(), nullable=False),
        sa.Column("order_cost_report_id", sa.BigInteger(), nullable=True),
        _foreign_key(
            "printing_cost_report_order_cost_report_id_fkey",
            "order_cost_report_id",
            "order_cost_report.id",
        ),
        sa.PrimaryKeyConstraint("id", name="printing_cost_report_pkey"),
    )
    op.execute(sa.text(
        "ALTER SEQUENCE printing_cost_report_id_seq "
        "OWNED BY printing_cost_report.id"
    ))
    op.create_table(
        "order",
        _sequence_id("order_id_seq"),
        sa.Column("creation_date", sa.Date(), nullable=False),
        sa.Column("status", _enum("order_status", _ORDER_STATUS), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=False),
        sa.Column("economy_id", sa.BigInteger(), nullable=True),
        sa.Column("order_cost_report_id", sa.BigInteger(), nullable=True),
        sa.Column("unit_count", sa.BigInteger(), nullable=True),
        _foreign_key("fk_order_economy", "economy_id", "economy.id"),
        _foreign_key(
            "order_order_cost_report_id_fkey",
            "order_cost_report_id",
            "order_cost_report.id",
        ),
        sa.PrimaryKeyConstraint("id", name="order_pkey"),
    )
    op.create_table(
        "operation",
        _identity_id(),
        sa.Column("order_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "name",
            sa.String(length=500),
            nullable=False,
            comment="Название операции.",
        ),
        sa.Column(
            "cost",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            comment="Стоимость операции в руб.",
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
            comment="Описание операции",
        ),
        _foreign_key("operation_order_id_fkey", "order_id", "order.id"),
        sa.PrimaryKeyConstraint("id", name="operation_pkey"),
    )
    op.create_table(
        "printing",
        _identity_id(),
        sa.Column("order_id", sa.BigInteger(), nullable=True),
        sa.Column("production_id", sa.BigInteger(), nullable=True),
        sa.Column("edition_id", sa.BigInteger(), nullable=True),
        sa.Column("printing_cost_report_id", sa.BigInteger(), nullable=True),
        sa.Column("comment", sa.String(length=500), nullable=False),
        _foreign_key("printing_order_id_fkey", "order_id", "order.id"),
        _foreign_key("printing_production_id_fkey", "production_id", "production.id"),
        _foreign_key("printing_edition_id_fkey", "edition_id", "edition.id"),
        _foreign_key(
            "printing_printing_cost_report_id_fkey",
            "printing_cost_report_id",
            "printing_cost_report.id",
        ),
        sa.PrimaryKeyConstraint("id", name="printing_pkey"),
    )
    op.create_table(
        "user",
        _sequence_id("user_id_seq"),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "permissions",
            _enum("permission", _PERMISSION),
            server_default=sa.text("'NONE'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name="user_pkey"),
        sa.UniqueConstraint("username", name="user_username_key"),
        sa.UniqueConstraint("email", name="user_email_key"),
    )


def downgrade() -> None:
    op.drop_table("printing")
    op.drop_table("operation")
    op.drop_table("order")
    op.drop_table("printing_cost_report")
    op.drop_table("order_cost_report")
    op.drop_table("production_reference")
    op.drop_table("production")
    op.drop_table("edition")
    op.drop_table("list_size")
    op.drop_table("press_sheet")
    op.drop_table("cutter_info")
    op.drop_table("economy")
    op.drop_table("user")
    for name in _UNOWNED_SEQUENCES:
        op.execute(sa.text(f"DROP SEQUENCE {name}"))
    for name in ("permission", "order_status", "lamination", "chroma"):
        op.execute(sa.text(f"DROP TYPE {name}"))
