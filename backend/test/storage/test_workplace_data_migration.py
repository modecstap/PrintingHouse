import os
import shutil
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from backend.storage.db_config import DBConfig
from backend.test.storage.test_schema_migration import _migration_database
from backend.workplace.administrator import Administrator
from backend.workplace.cost_order import List, Order, Status
from backend.workplace.order_service import WorkplaceOrderService
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import Chroma, PressSheet
from backend.workplace_order_db import SqlWorkplaceOrderRepository

_DUMP = (
    Path(__file__).resolve().parents[3]
    / ".agents"
    / "plans"
    / "dump-postgers-202610181400.sql"
)
_COLOR = Decimal("4.533333333333333333333333333")
_KEPT = (
    '"order"',
    "production_reference",
    '"user"',
    "operation",
    "printing",
)
_DUMP_KEPT = ('"order"', "production_reference", '"user"')
_FILM_SIDES = {"DONT": 0, "ONE_ZERO": 1, "ONE_ONE": 2}


def _count(connection: Connection, table: str, where: str = "") -> int:
    statement = f"SELECT count(*) FROM {table}"
    if where:
        statement = f"{statement} WHERE {where}"
    return int(connection.execute(text(statement)).scalar_one())


def _counts(connection: Connection, tables: tuple[str, ...]) -> dict[str, int]:
    return {table: _count(connection, table) for table in tables}


def _rows(connection: Connection, statement: str) -> list[tuple[object, ...]]:
    return [tuple(row) for row in connection.execute(text(statement))]


def _mismatch_count(connection: Connection, statement: str) -> int:
    wrapped = f"SELECT count(*) FROM ({statement}) AS mismatch"
    return int(connection.execute(text(wrapped)).scalar_one())


def _service(engine: Engine) -> WorkplaceOrderService:
    repository = SqlWorkplaceOrderRepository(engine)
    return WorkplaceOrderService(repository, Administrator())


def _blank_order() -> Order:
    return Order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operations=(),
        printings=(),
    )


def _insert_legacy(connection: Connection) -> None:
    connection.execute(text(
        "INSERT INTO cutter_info (id, stack_height) VALUES (1, 30), (2, 11)"
    ))
    connection.execute(text(
        "INSERT INTO economy (id, markup, tax_rate) VALUES "
        "(1, 80.0000, 0.9300), (2, 0.0000, 1.0000)"
    ))
    connection.execute(text(
        "INSERT INTO list_size (id, width, height, bleeds) VALUES "
        "(1, 30, 40, 1), (2, 10, 20, 3), (3, 11, 22, 2)"
    ))
    connection.execute(text(
        "INSERT INTO press_sheet (id, width, height, spacing) VALUES "
        "(1, 320, 470, 5), (2, 100, 200, 4)"
    ))
    connection.execute(text(
        """
        INSERT INTO production (
            id, press_sheet_id, cutter_id, black_ink_cost, ink_cost,
            printer_salary, lamination_cost, die_cutting_cost, paper_cost,
            cutting_cost, sheet_by_fitting
        ) VALUES
            (1, 1, 1, 2.0000, 15.6000, 1.0000, 20.0000, 25.0000, 160.0000, 10.0000, 2),
            (2, 2, 2, 2.0000, 5.0000, 2.0000, 8.0000, 4.0000, 1.0000, 3.0000, 7)
        """
    ))
    connection.execute(text(
        "INSERT INTO production_reference (id, production_id, comment) "
        "VALUES (1, 1, NULL)"
    ))
    connection.execute(text(
        """
        INSERT INTO edition (
            id, list_size_id, count, density, chroma, lamination, die_cutting
        ) VALUES
            (1, 1, 4, 90, 'FOUR_FOUR', 'DONT', false),
            (2, 2, 9, 80, 'FOUR_ZERO', 'ONE_ONE', true),
            (3, 3, 5, 70, 'ONE_ZERO', 'ONE_ZERO', false),
            (4, 1, 1, 1, 'ZERO_ZERO', 'DONT', false)
        """
    ))
    connection.execute(text(
        "INSERT INTO order_cost_report "
        "(id, unit_cost_price, unit_cost, edition_cost, profit_after_tax) VALUES "
        "(1, 1.5, 2.5, 3.5, -4.5), (2, 9.9, 9.9, 9.9, 9.9)"
    ))
    connection.execute(text(
        """
        INSERT INTO printing_cost_report (
            id, items_per_sheet, sheet_count, unit_cost_price, unit_cost,
            edition_cost, profit_before_tax, profit_after_tax,
            edition_cost_price, order_cost_report_id
        ) VALUES
            (1, 2, 3, 1.1, 1.2, 1.4, 1.6, 1.7, 1.3, NULL),
            (2, 8, 9, 2.1, 2.2, 2.4, 2.5, 2.6, 2.3, NULL),
            (3, 4, 5, 3.1, 3.2, 3.4, 3.5, 3.6, 3.3, NULL),
            (4, 7, 7, 7.1, 7.2, 7.4, 7.5, 7.6, 7.3, NULL),
            (5, 6, 6, 6.1, 6.2, 6.4, 6.5, 6.6, 6.3, NULL)
        """
    ))
    connection.execute(text(
        """
        INSERT INTO "order" (
            id, creation_date, status, comment, economy_id,
            order_cost_report_id, unit_count
        ) VALUES
            (6, DATE '2024-03-15', 'DONE', '', 1, 1, 11),
            (50, DATE '2020-01-02', 'SAVED', 'заметка', 2, NULL, 2)
        """
    ))
    connection.execute(text(
        """
        INSERT INTO operation (id, order_id, name, cost, description) VALUES
            (1, 6, 'резка', 10.5000, ''),
            (2, 6, 'упаковка', 3.0000, 'короб'),
            (3, NULL, 'чужая', 1.0000, 'нет')
        """
    ))
    connection.execute(text(
        """
        INSERT INTO printing (
            id, order_id, production_id, edition_id,
            printing_cost_report_id, comment
        ) VALUES
            (10, 6, 2, 2, 1, 'плёнка'),
            (20, 6, 1, 1, 2, 'край'),
            (30, 6, 1, 3, 3, ''),
            (40, 50, 1, 4, 4, 'без итога'),
            (41, NULL, 1, 4, 5, 'сирота')
        """
    ))
    connection.execute(text(
        'INSERT INTO "user" (username, email, hashed_password) '
        "VALUES ('migrator', 'migrator@example.com', 'x')"
    ))


@contextmanager
def _upgraded_legacy() -> Iterator[tuple[Engine, dict[str, int]]]:
    with _migration_database() as (config, engine):
        command.upgrade(config, "b6d4e2a81c05")
        with engine.begin() as connection:
            _insert_legacy(connection)
            before = _counts(connection, _KEPT)
        command.upgrade(config, "head")
        yield engine, before


def _assert_reference(order: Order) -> None:
    assert order.id is None
    assert order.creation_date is None
    assert order.unit_count == 1
    assert order.tax_rate == Decimal("0")
    assert order.markup == Decimal("0")
    assert order.status is Status.SAVED
    assert order.operations == ()
    assert len(order.printings) == 1
    printing = order.printings[0]
    assert printing.count == 0
    assert printing.chroma is Chroma.ZERO_ZERO
    assert printing.lamination is Lamination.DONT
    assert printing.die_cutting is False
    assert printing.comment == ""
    assert printing.press_sheet == PressSheet(0, 320, 470, 5)
    assert printing.list == List(0, 0, 0)
    assert printing.sheet_by_fitting == 2
    assert printing.stack_height == 30
    press = printing.press_pricing
    assert press.black.amount == Decimal("2.0000")
    assert press.cyan.amount == _COLOR
    assert press.magenta.amount == _COLOR
    assert press.yellow.amount == _COLOR
    assert press.paper.amount == Decimal("160.0000")
    assert press.salary.amount == Decimal("1.0000")
    assert printing.cut_pricing.salary.amount == Decimal("10.0000")
    assert printing.die_cut_pricing.salary.amount == Decimal("25.0000")
    assert printing.lamination_pricing.startup.amount == Decimal("200")
    assert printing.lamination_pricing.film_cost.amount == Decimal("10.0000")
    assert printing.lamination_pricing.salary.amount == Decimal("0.0000")


def test_should_copy_order_headers_and_advance_the_id_when_legacy_orders_are_upgraded() -> None:
    with _upgraded_legacy() as (engine, _before):
        with engine.connect() as connection:
            headers = _rows(connection, """
                SELECT id, creation_date, status, comment, unit_count, markup, tax_rate
                FROM workplace_order
                ORDER BY id
                """)
        assert headers == [
            (6, date(2024, 3, 15), "DONE", "", 11, Decimal("80.0000"), Decimal("0.9300")),
            (50, date(2020, 1, 2), "SAVED", "заметка", 2, Decimal("0.0000"), Decimal("1.0000")),
        ]
        saved_id = _service(engine).save(_blank_order())
        assert saved_id == 51


def test_should_copy_operations_and_printing_rates_when_legacy_rows_are_upgraded() -> None:
    with _upgraded_legacy() as (engine, _before):
        with engine.connect() as connection:
            operations = _rows(connection, """
                SELECT position, name, amount, description
                FROM workplace_operation_cost
                ORDER BY order_id, position
                """)
            stranger = _count(connection, "workplace_operation_cost", "name = 'чужая'")
            printing_count = _count(connection, "workplace_printing")
            order_six = _count(connection, "workplace_printing", "order_id = 6")
            order_fifty = _count(connection, "workplace_printing", "order_id = 50")
            orphan = _count(connection, "workplace_printing", "comment = 'сирота'")
            first, second, third = _rows(connection, """
                SELECT count, press_sheet_density, sheet_by_fitting, stack_height,
                       press_sheet_width, press_sheet_height, press_sheet_spacing,
                       list_width, list_height, list_bleeds, chroma, lamination,
                       die_cutting, comment, press_cyan, press_magenta, press_yellow,
                       press_black, press_paper, press_salary, cut_salary,
                       die_cut_salary, lamination_startup, lamination_film_cost,
                       lamination_salary
                FROM workplace_printing
                WHERE order_id = 6
                ORDER BY position
                """)
            kept_comment = connection.execute(text(
                "SELECT comment FROM workplace_printing WHERE order_id = 50"
            )).scalar_one()
    assert stranger == 0
    assert operations == [
        (0, "резка", Decimal("10.5000"), ""),
        (1, "упаковка", Decimal("3.0000"), "короб"),
    ]
    assert printing_count == 4
    assert order_six == 3
    assert order_fifty == 1
    assert orphan == 0
    assert kept_comment == "без итога"
    assert first == (
        9, 80, 7, 11, 100, 200, 4, 10, 20, 3, "FOUR_ZERO", "ONE_ONE", True, "плёнка",
        Decimal("1.0000"), Decimal("1.0000"), Decimal("1.0000"), Decimal("2.0000"),
        Decimal("1.0000"), Decimal("2.0000"), Decimal("3.0000"), Decimal("4.0000"),
        Decimal("200"), Decimal("4.0000"), Decimal("8.0000"),
    )
    assert second == (
        4, 90, 2, 30, 320, 470, 5, 30, 40, 1, "FOUR_FOUR", "DONT", False, "край",
        _COLOR, _COLOR, _COLOR, Decimal("2.0000"),
        Decimal("160.0000"), Decimal("1.0000"), Decimal("10.0000"), Decimal("25.0000"),
        Decimal("200"), Decimal("10.0000"), Decimal("0.0000"),
    )
    assert third == (
        5, 70, 2, 30, 320, 470, 5, 11, 22, 2, "ONE_ZERO", "ONE_ZERO", False, "",
        _COLOR, _COLOR, _COLOR, Decimal("2.0000"),
        Decimal("160.0000"), Decimal("1.0000"), Decimal("10.0000"), Decimal("25.0000"),
        Decimal("200"), Decimal("10.0000"), Decimal("10.0000"),
    )


def test_should_copy_only_reports_of_orders_that_have_one_when_the_database_is_upgraded() -> None:
    with _upgraded_legacy() as (engine, _before):
        with engine.connect() as connection:
            reports = _rows(connection, """
                SELECT order_id, position, unit_cost_price, unit_cost,
                       edition_cost, profit_after_tax
                FROM workplace_cost_report
                """)
            costs = _rows(connection, """
                SELECT position, items_per_sheet, sheet_count, unit_cost_price,
                       unit_cost, edition_cost_price, edition_cost,
                       profit_before_tax, profit_after_tax
                FROM workplace_printing_cost
                ORDER BY position
                """)
            stray = _mismatch_count(connection, """
                SELECT amount FROM (
                    SELECT unit_cost_price AS amount FROM workplace_cost_report
                    UNION ALL SELECT unit_cost FROM workplace_cost_report
                    UNION ALL SELECT edition_cost FROM workplace_cost_report
                    UNION ALL SELECT profit_after_tax FROM workplace_cost_report
                    UNION ALL SELECT unit_cost_price FROM workplace_printing_cost
                    UNION ALL SELECT unit_cost FROM workplace_printing_cost
                    UNION ALL SELECT edition_cost_price FROM workplace_printing_cost
                    UNION ALL SELECT edition_cost FROM workplace_printing_cost
                    UNION ALL SELECT profit_before_tax FROM workplace_printing_cost
                    UNION ALL SELECT profit_after_tax FROM workplace_printing_cost
                ) AS amounts
                WHERE amount IN (9.9, 7.1, 6.1)
                """)
            order_fifty_reports = _count(
                connection, "workplace_cost_report", "order_id = 50"
            )
            order_fifty_costs = _count(
                connection,
                "workplace_printing_cost AS cost "
                "JOIN workplace_cost_report AS report "
                "ON report.id = cost.cost_report_id",
                "report.order_id = 50",
            )
    assert reports == [(
        6, 0, Decimal("1.5"), Decimal("2.5"), Decimal("3.5"), Decimal("-4.5"),
    )]
    assert costs == [
        (0, 2, 3, Decimal("1.1"), Decimal("1.2"), Decimal("1.3"), Decimal("1.4"), Decimal("1.6"), Decimal("1.7")),
        (1, 8, 9, Decimal("2.1"), Decimal("2.2"), Decimal("2.3"), Decimal("2.4"), Decimal("2.5"), Decimal("2.6")),
        (2, 4, 5, Decimal("3.1"), Decimal("3.2"), Decimal("3.3"), Decimal("3.4"), Decimal("3.5"), Decimal("3.6")),
    ]
    assert stray == 0
    assert order_fifty_reports == 0
    assert order_fifty_costs == 0


def test_should_write_the_reference_without_an_order_row_when_legacy_orders_are_upgraded() -> None:
    with _upgraded_legacy() as (engine, before):
        service = _service(engine)
        _assert_reference(service.reference())
        assert sorted(order.id for order in service.take_all()) == [6, 50]
        with engine.connect() as connection:
            assert _count(connection, "workplace_order") == 2
            assert _count(connection, "workplace_reference") == 1
            document = connection.execute(text(
                "SELECT document FROM workplace_reference WHERE id = 1"
            )).scalar_one()
            assert _counts(connection, _KEPT) == before
    assert document["id"] is None
    assert "creation_date" not in document
    assert before == {
        '"order"': 2,
        "production_reference": 1,
        '"user"': 1,
        "operation": 3,
        "printing": 5,
    }


def test_should_refuse_the_copy_when_workplace_tables_are_not_empty() -> None:
    with _migration_database() as (config, engine):
        command.upgrade(config, "b6d4e2a81c05")
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO economy (id, markup, tax_rate) VALUES (1, 0, 0)"
            ))
            connection.execute(text(
                """
                INSERT INTO "order" (
                    id, creation_date, status, comment, economy_id, unit_count
                ) VALUES (6, DATE '2024-03-15', 'DONE', '', 1, 11)
                """
            ))
            connection.execute(text(
                """
                INSERT INTO workplace_order (
                    id, comment, status, unit_count, tax_rate, markup, creation_date
                ) VALUES (1, 'держатель', 'SAVED', 1, 0, 0, DATE '2024-01-01')
                """
            ))
        with pytest.raises(Exception, match="workplace tables are not empty"):
            command.upgrade(config, "head")
        with engine.connect() as connection:
            version = connection.execute(text(
                "SELECT version_num FROM alembic_version"
            )).scalar_one()
            order_ids = _rows(connection, 'SELECT id FROM "order"')
            holder = _rows(connection, "SELECT id, comment FROM workplace_order")
            printings = _count(connection, "workplace_printing")
    assert version == "b6d4e2a81c05"
    assert order_ids == [(6,)]
    assert holder == [(1, "держатель")]
    assert printings == 0


def test_should_copy_again_after_downgrade_when_legacy_rows_remain() -> None:
    with _migration_database() as (config, engine):
        command.upgrade(config, "b6d4e2a81c05")
        with engine.begin() as connection:
            _insert_legacy(connection)
            before = _counts(connection, _KEPT)
        command.upgrade(config, "head")
        command.downgrade(config, "b6d4e2a81c05")
        with engine.connect() as connection:
            assert _count(connection, "workplace_order") == 0
            assert _count(connection, "workplace_reference") == 0
            assert _counts(connection, _KEPT) == before
        command.upgrade(config, "head")
        with engine.connect() as connection:
            order_ids = _rows(connection, "SELECT id FROM workplace_order ORDER BY id")
            reference_rows = _count(connection, "workplace_reference")
    assert order_ids == [(6,), (50,)]
    assert reference_rows == 1


def _local_pg_restore() -> str | None:
    found = shutil.which("pg_restore")
    if found:
        return found
    root = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "PostgreSQL"
    candidates = sorted(root.glob("*/bin/pg_restore.exe"))
    if not candidates:
        return None
    return str(candidates[-1])


def _restore_command(database: str, config: DBConfig) -> list[str]:
    if shutil.which("docker"):
        host = config.host
        if host in ("localhost", "127.0.0.1"):
            host = "host.docker.internal"
        return [
            "docker", "run", "--rm",
            "-v", f"{_DUMP.parent}:/dump:ro",
            "-e", "PGPASSWORD",
            "postgres:16.4",
            "pg_restore",
            "-h", host,
            "-p", str(config.port),
            "-U", config.user,
            "-d", database,
            "--no-owner",
            "--no-acl",
            "--exit-on-error",
            f"/dump/{_DUMP.name}",
        ]
    executable = _local_pg_restore()
    if executable is None:
        raise RuntimeError("copy legacy orders: pg_restore client is not installed")
    return [
        executable,
        "-h", config.host,
        "-p", str(config.port),
        "-U", config.user,
        "-d", database,
        "--no-owner",
        "--no-acl",
        "--exit-on-error",
        str(_DUMP),
    ]


def _restore_dump(database: str) -> None:
    config = DBConfig.from_env()
    password = config.password or ""
    completed = subprocess.run(
        _restore_command(database, config),
        env={**os.environ, "PGPASSWORD": password},
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr
        if password:
            detail = detail.replace(password, "***")
        raise RuntimeError(detail)


def test_should_copy_the_dump_when_the_dump_file_is_upgraded() -> None:
    if not _DUMP.is_file():
        pytest.skip("dump file is absent")
    with _migration_database() as (config, engine):
        _restore_dump(str(engine.url.database))
        with engine.connect() as connection:
            before = _counts(connection, _DUMP_KEPT)
        command.upgrade(config, "head")
        with engine.connect() as connection:
            span = connection.execute(text(
                "SELECT count(*), min(id), max(id) FROM workplace_order"
            )).one()
            done = _count(connection, "workplace_order", "status = 'DONE'")
            saved = _count(connection, "workplace_order", "status = 'SAVED'")
            header_gap = _mismatch_count(connection, """
                SELECT o.id, o.creation_date, o.comment, o.status::text,
                       o.unit_count, e.markup, e.tax_rate
                FROM "order" AS o
                JOIN economy AS e ON e.id = o.economy_id
                EXCEPT
                SELECT id, creation_date, comment, status, unit_count, markup, tax_rate
                FROM workplace_order
                """)
            printing_rows = _count(connection, "workplace_printing")
            operation_rows = _count(connection, "workplace_operation_cost")
            source_printings = _count(connection, "printing", "order_id IS NOT NULL")
            source_operations = _count(connection, "operation", "order_id IS NOT NULL")
            rates = connection.execute(text(
                """
                SELECT wp.press_cyan, wp.press_magenta, wp.press_yellow, wp.press_black,
                       wp.lamination_startup, wp.lamination_film_cost, wp.lamination_salary,
                       pr.ink_cost, pr.black_ink_cost, pr.lamination_cost,
                       e.lamination::text AS lamination
                FROM printing AS p
                JOIN edition AS e ON e.id = p.edition_id
                JOIN production AS pr ON pr.id = p.production_id
                JOIN (
                    SELECT id,
                           (row_number() OVER (
                               PARTITION BY order_id ORDER BY id
                           ) - 1) AS position
                    FROM printing
                    WHERE order_id IS NOT NULL
                ) AS ranked ON ranked.id = p.id
                JOIN workplace_printing AS wp
                  ON wp.order_id = p.order_id AND wp.position = ranked.position
                WHERE p.order_id IS NOT NULL
                """
            )).all()
            report_rows = _count(connection, "workplace_cost_report")
            printing_cost_rows = _count(connection, "workplace_printing_cost")
            orders_without_report = _count(
                connection, '"order"', "order_cost_report_id IS NULL"
            )
            copied_empty_reports = _mismatch_count(connection, """
                SELECT o.id
                FROM "order" AS o
                JOIN workplace_cost_report AS report ON report.order_id = o.id
                WHERE o.order_cost_report_id IS NULL
                """)
            report_gap = _mismatch_count(connection, """
                SELECT o.id, r.unit_cost_price, r.unit_cost,
                       r.edition_cost, r.profit_after_tax
                FROM "order" AS o
                JOIN order_cost_report AS r ON r.id = o.order_cost_report_id
                EXCEPT
                SELECT order_id, unit_cost_price, unit_cost,
                       edition_cost, profit_after_tax
                FROM workplace_cost_report
                """)
            printing_cost_gap = _mismatch_count(connection, """
                SELECT o.id,
                       (row_number() OVER (PARTITION BY p.order_id ORDER BY p.id) - 1),
                       c.items_per_sheet, c.sheet_count, c.unit_cost_price, c.unit_cost,
                       c.edition_cost_price, c.edition_cost,
                       c.profit_before_tax, c.profit_after_tax
                FROM printing AS p
                JOIN "order" AS o ON o.id = p.order_id
                JOIN printing_cost_report AS c ON c.id = p.printing_cost_report_id
                WHERE o.order_cost_report_id IS NOT NULL
                EXCEPT
                SELECT report.order_id, cost.position, cost.items_per_sheet,
                       cost.sheet_count, cost.unit_cost_price, cost.unit_cost,
                       cost.edition_cost_price, cost.edition_cost,
                       cost.profit_before_tax, cost.profit_after_tax
                FROM workplace_printing_cost AS cost
                JOIN workplace_cost_report AS report ON report.id = cost.cost_report_id
                """)
            after = _counts(connection, _DUMP_KEPT)
            workplace_orders = _count(connection, "workplace_order")
        service = _service(engine)
        _assert_reference(service.reference())
        taken = service.take_all()
        saved_id = service.save(_blank_order())
    assert tuple(span) == (234, 6, 890)
    assert done == 225
    assert saved == 9
    assert header_gap == 0
    assert printing_rows == 294
    assert operation_rows == 70
    assert source_printings == 294
    assert source_operations == 70
    assert len(rates) == 294
    for row in rates:
        color = (row.ink_cost - row.black_ink_cost) / Decimal(3)
        film = row.lamination_cost / Decimal(2)
        assert row.press_cyan == color
        assert row.press_magenta == color
        assert row.press_yellow == color
        assert row.press_black == row.black_ink_cost
        assert row.lamination_startup == Decimal("200")
        assert row.lamination_film_cost == film
        assert row.lamination_salary == film * Decimal(_FILM_SIDES[row.lamination])
    assert report_rows == 127
    assert printing_cost_rows == 187
    assert orders_without_report == 107
    assert copied_empty_reports == 0
    assert report_gap == 0
    assert printing_cost_gap == 0
    assert len(taken) == 234
    assert all(order.id is not None for order in taken)
    assert workplace_orders == 234
    assert after == before
    assert before == {'"order"': 234, "production_reference": 1, '"user"': 3}
    assert saved_id > 890
