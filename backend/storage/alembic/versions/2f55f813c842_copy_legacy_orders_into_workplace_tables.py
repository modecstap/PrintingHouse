"""copy legacy orders into workplace tables

Revision ID: 2f55f813c842
Revises: b6d4e2a81c05
Create Date: 2026-10-27 22:16:25.129631

"""
from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection, RowMapping
from sqlalchemy.orm import Session

from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.workplace.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.workplace.accountant.pricing.printing import PrintingCalculation
from backend.workplace.cost_order import List, Order, Printing, Status
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import Chroma, PressSheet
from backend.workplace_order_db.mapping import write_reference


# revision identifiers, used by Alembic.
revision: str = '2f55f813c842'
down_revision: Union[str, Sequence[str], None] = 'b6d4e2a81c05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FILM_SIDES = {"DONT": 0, "ONE_ZERO": 1, "ONE_ONE": 2}
_WORKPLACE_TABLES = (
    "workplace_order",
    "workplace_operation_cost",
    "workplace_printing",
    "workplace_cost_report",
    "workplace_printing_cost",
    "workplace_reference",
)
_COUNT_CHECKS = (
    (
        "workplace_order",
        "SELECT count(*) FROM workplace_order",
        'SELECT count(*) FROM "order"',
    ),
    (
        "workplace_printing",
        "SELECT count(*) FROM workplace_printing",
        "SELECT count(*) FROM printing WHERE order_id IS NOT NULL",
    ),
    (
        "workplace_operation_cost",
        "SELECT count(*) FROM workplace_operation_cost",
        "SELECT count(*) FROM operation WHERE order_id IS NOT NULL",
    ),
    (
        "workplace_cost_report",
        "SELECT count(*) FROM workplace_cost_report",
        'SELECT count(*) FROM "order" WHERE order_cost_report_id IS NOT NULL',
    ),
    (
        "workplace_printing_cost",
        "SELECT count(*) FROM workplace_printing_cost",
        """
        SELECT count(*)
        FROM printing AS p
        JOIN "order" AS o ON o.id = p.order_id
        WHERE o.order_cost_report_id IS NOT NULL
        """,
    ),
)


def upgrade() -> None:
    connection = op.get_bind()
    # Урезанная таблица order в тестах схемы содержит только id. Без колонки comment читать экономику и печать нельзя.
    if not _order_has_comment(connection):
        return
    if _scalar(connection, 'SELECT count(*) FROM "order"') == 0:
        return
    _require_empty_workplace(connection)
    _require_one_production_reference(connection)
    _copy_orders(connection)
    _copy_operations(connection)
    _copy_printings(connection)
    _copy_cost_reports(connection)
    _copy_printing_costs(connection)
    _require_copied_counts(connection)
    _write_reference(connection)
    # setval не откатывается вместе с транзакцией Alembic, поэтому счётчик двигается после проверок и справочника. Назад его не двигаем: если следующее значение уже больше max(id), блок ничего не меняет.
    _advance_workplace_order_id()


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM workplace_order"))
    op.execute(sa.text("DELETE FROM workplace_reference"))


def _order_has_comment(connection: Connection) -> bool:
    found = connection.execute(sa.text(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'order'
          AND column_name = 'comment'
        """
    )).first()
    return found is not None


def _scalar(connection: Connection, statement: str) -> int:
    value = connection.execute(sa.text(statement)).scalar_one()
    return int(value)


def _require_empty_workplace(connection: Connection) -> None:
    for table in _WORKPLACE_TABLES:
        if _scalar(connection, f"SELECT count(*) FROM {table}") > 0:
            raise RuntimeError(
                "copy legacy orders: workplace tables are not empty"
            )


def _require_one_production_reference(connection: Connection) -> None:
    count = _scalar(connection, "SELECT count(*) FROM production_reference")
    if count != 1:
        raise RuntimeError(
            f"copy legacy orders: production_reference count is {count}"
        )


def _copy_orders(connection: Connection) -> None:
    connection.execute(sa.text(
        """
        INSERT INTO workplace_order (
            id, comment, status, unit_count, tax_rate, markup, creation_date
        )
        SELECT o.id, o.comment, o.status::text, o.unit_count,
               e.tax_rate, e.markup, o.creation_date
        FROM "order" AS o
        JOIN economy AS e ON e.id = o.economy_id
        ORDER BY o.id
        """
    ))


def _copy_operations(connection: Connection) -> None:
    connection.execute(sa.text(
        """
        INSERT INTO workplace_operation_cost (
            order_id, position, amount, name, description
        )
        SELECT operation.order_id,
               (row_number() OVER (
                   PARTITION BY operation.order_id ORDER BY operation.id
               ) - 1)::integer,
               operation.cost,
               operation.name,
               operation.description
        FROM operation
        WHERE operation.order_id IS NOT NULL
        """
    ))


def _copy_printings(connection: Connection) -> None:
    rows = connection.execute(sa.text(
        """
        SELECT p.id, p.order_id, p.comment, p.printing_cost_report_id,
               e.count, e.density, e.chroma::text AS chroma,
               e.lamination::text AS lamination, e.die_cutting,
               ls.width AS list_width, ls.height AS list_height,
               ls.bleeds AS list_bleeds,
               ps.width AS press_width, ps.height AS press_height,
               ps.spacing AS press_spacing,
               c.stack_height, pr.sheet_by_fitting,
               pr.black_ink_cost, pr.ink_cost, pr.paper_cost,
               pr.printer_salary, pr.cutting_cost, pr.die_cutting_cost,
               pr.lamination_cost
        FROM printing AS p
        JOIN edition AS e ON e.id = p.edition_id
        JOIN list_size AS ls ON ls.id = e.list_size_id
        JOIN production AS pr ON pr.id = p.production_id
        JOIN press_sheet AS ps ON ps.id = pr.press_sheet_id
        JOIN cutter_info AS c ON c.id = pr.cutter_id
        WHERE p.order_id IS NOT NULL
        ORDER BY p.order_id, p.id
        """
    )).mappings().all()
    position_by_order: dict[int, int] = {}
    payload: list[dict[str, object]] = []
    for row in rows:
        order_id = int(row["order_id"])
        position = position_by_order.get(order_id, 0)
        position_by_order[order_id] = position + 1
        lamination = row["lamination"]
        if type(lamination) is not str:
            raise RuntimeError("copy legacy orders: unknown lamination")
        rates = _printing_rates(row, lamination)
        payload.append({
            "order_id": order_id,
            "position": position,
            "count": row["count"],
            "press_sheet_density": row["density"],
            "list_width": row["list_width"],
            "list_height": row["list_height"],
            "list_bleeds": row["list_bleeds"],
            "press_sheet_width": row["press_width"],
            "press_sheet_height": row["press_height"],
            "press_sheet_spacing": row["press_spacing"],
            "stack_height": row["stack_height"],
            "sheet_by_fitting": row["sheet_by_fitting"],
            "comment": row["comment"],
            "die_cutting": row["die_cutting"],
            "chroma": row["chroma"],
            "lamination": lamination,
            **rates,
        })
    if not payload:
        return
    connection.execute(sa.text(
        """
        INSERT INTO workplace_printing (
            order_id, position, count, press_sheet_density,
            list_width, list_height, list_bleeds,
            press_sheet_width, press_sheet_height, press_sheet_spacing,
            stack_height, sheet_by_fitting, comment, die_cutting,
            chroma, lamination,
            press_black, press_paper, press_salary, cut_salary,
            die_cut_salary, press_cyan, press_magenta, press_yellow,
            lamination_startup, lamination_film_cost, lamination_salary
        ) VALUES (
            :order_id, :position, :count, :press_sheet_density,
            :list_width, :list_height, :list_bleeds,
            :press_sheet_width, :press_sheet_height, :press_sheet_spacing,
            :stack_height, :sheet_by_fitting, :comment, :die_cutting,
            :chroma, :lamination,
            :press_black, :press_paper, :press_salary, :cut_salary,
            :die_cut_salary, :press_cyan, :press_magenta, :press_yellow,
            :lamination_startup, :lamination_film_cost, :lamination_salary
        )
        """
    ), payload)


def _printing_rates(row: RowMapping, lamination: str) -> dict[str, Decimal]:
    black_ink_cost = _decimal(row["black_ink_cost"])
    # Цветные краски — (ink_cost - black_ink_cost) / 3, не четверть ink_cost.
    color = (_decimal(row["ink_cost"]) - black_ink_cost) / Decimal(3)
    film = _decimal(row["lamination_cost"]) / Decimal(2)
    return {
        "press_black": black_ink_cost,
        "press_paper": _decimal(row["paper_cost"]),
        "press_salary": _decimal(row["printer_salary"]),
        "cut_salary": _decimal(row["cutting_cost"]),
        "die_cut_salary": _decimal(row["die_cutting_cost"]),
        "press_cyan": color,
        "press_magenta": color,
        "press_yellow": color,
        "lamination_startup": Decimal("200"),
        "lamination_film_cost": film,
        "lamination_salary": _lamination_salary(film, lamination),
    }


def _decimal(value: object) -> Decimal:
    if type(value) is not Decimal:
        raise RuntimeError("copy legacy orders: money column is not Decimal")
    return value


def _lamination_salary(film_cost: Decimal, lamination: str) -> Decimal:
    sides = _FILM_SIDES.get(lamination)
    if sides is None:
        raise RuntimeError("copy legacy orders: unknown lamination")
    return film_cost * Decimal(sides)


def _copy_cost_reports(connection: Connection) -> None:
    connection.execute(sa.text(
        """
        INSERT INTO workplace_cost_report (
            order_id, position, unit_cost_price, unit_cost,
            edition_cost, profit_after_tax
        )
        SELECT o.id, 0, r.unit_cost_price, r.unit_cost,
               r.edition_cost, r.profit_after_tax
        FROM "order" AS o
        JOIN order_cost_report AS r ON r.id = o.order_cost_report_id
        """
    ))


def _copy_printing_costs(connection: Connection) -> None:
    connection.execute(sa.text(
        """
        INSERT INTO workplace_printing_cost (
            cost_report_id, position, items_per_sheet, sheet_count,
            unit_cost_price, unit_cost, edition_cost_price, edition_cost,
            profit_before_tax, profit_after_tax
        )
        SELECT report.id,
               ranked.position,
               cost.items_per_sheet,
               cost.sheet_count,
               cost.unit_cost_price,
               cost.unit_cost,
               cost.edition_cost_price,
               cost.edition_cost,
               cost.profit_before_tax,
               cost.profit_after_tax
        FROM (
            SELECT p.order_id,
                   p.printing_cost_report_id,
                   (row_number() OVER (
                       PARTITION BY p.order_id ORDER BY p.id
                   ) - 1) AS position
            FROM printing AS p
            WHERE p.order_id IS NOT NULL
        ) AS ranked
        JOIN "order" AS o ON o.id = ranked.order_id
        JOIN workplace_cost_report AS report
          ON report.order_id = o.id AND report.position = 0
        JOIN printing_cost_report AS cost
          ON cost.id = ranked.printing_cost_report_id
        WHERE o.order_cost_report_id IS NOT NULL
        """
    ))


def _require_copied_counts(connection: Connection) -> None:
    for name, copied_sql, source_sql in _COUNT_CHECKS:
        copied = _scalar(connection, copied_sql)
        source = _scalar(connection, source_sql)
        if copied != source:
            raise RuntimeError(
                f"copy legacy orders: {name} copied {copied}, source {source}"
            )


def _write_reference(connection: Connection) -> None:
    row = connection.execute(sa.text(
        """
        SELECT ps.width AS press_width,
               ps.height AS press_height,
               ps.spacing AS press_spacing,
               c.stack_height,
               pr.sheet_by_fitting,
               pr.black_ink_cost,
               pr.ink_cost,
               pr.paper_cost,
               pr.printer_salary,
               pr.cutting_cost,
               pr.die_cutting_cost,
               pr.lamination_cost
        FROM production_reference AS pref
        JOIN production AS pr ON pr.id = pref.production_id
        JOIN press_sheet AS ps ON ps.id = pr.press_sheet_id
        JOIN cutter_info AS c ON c.id = pr.cutter_id
        """
    )).mappings().first()
    if row is None:
        raise RuntimeError(
            "copy legacy orders: production_reference has no production"
        )
    order = _reference_order(row)
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    try:
        write_reference(session, order)
        session.commit()
    finally:
        session.close()


def _reference_order(row: RowMapping) -> Order:
    rates = _printing_rates(row, "DONT")
    zero = Decimal("0")
    printing = Printing(
        count=0,
        chroma=Chroma.ZERO_ZERO,
        lamination=Lamination.DONT,
        die_cutting=False,
        sheet_by_fitting=int(row["sheet_by_fitting"]),
        stack_height=int(row["stack_height"]),
        press_sheet=PressSheet(
            0,
            int(row["press_width"]),
            int(row["press_height"]),
            int(row["press_spacing"]),
        ),
        list=List(0, 0, 0),
        press_pricing=PrintingCalculation(
            Money(rates["press_cyan"]),
            Money(rates["press_magenta"]),
            Money(rates["press_yellow"]),
            Money(rates["press_black"]),
            Money(rates["press_paper"]),
            Money(rates["press_salary"]),
        ),
        cut_pricing=CuttingCalculation(Money(rates["cut_salary"])),
        lamination_pricing=LaminationCalculation(
            Money(rates["lamination_startup"]),
            Money(rates["lamination_film_cost"]),
            Money(rates["lamination_salary"]),
        ),
        die_cut_pricing=DieCuttingCalculation(Money(rates["die_cut_salary"])),
        comment="",
    )
    return Order(
        unit_count=1,
        tax_rate=zero,
        markup=zero,
        operations=(),
        printings=(printing,),
        id=None,
        comment="",
        status=Status.SAVED,
        creation_date=None,
    )


def _advance_workplace_order_id() -> None:
    op.execute(sa.text(
        """
        DO $$
        DECLARE
            max_id bigint;
            seq_last bigint;
            seq_called boolean;
            next_value bigint;
        BEGIN
            SELECT MAX(id) INTO max_id FROM workplace_order;
            IF max_id IS NULL THEN
                RETURN;
            END IF;
            SELECT last_value, is_called
                INTO seq_last, seq_called
            FROM workplace_order_id_seq;
            IF seq_called THEN
                next_value := seq_last + 1;
            ELSE
                next_value := seq_last;
            END IF;
            IF next_value <= max_id THEN
                PERFORM setval('workplace_order_id_seq', max_id, true);
            END IF;
        END $$;
        """
    ))
