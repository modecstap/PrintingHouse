import ast
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from unittest.mock import patch

from backend.storage.db_config import DBConfig

_ROOT = Path(__file__).resolve().parents[3]
_VERSIONS = _ROOT / "backend" / "storage" / "alembic" / "versions"
_ALEMBIC_INI = _ROOT / "backend" / "storage" / "alembic.ini"

_OLD_TABLES = (
    "cutter_info",
    "economy",
    "list_size",
    "edition",
    "press_sheet",
    "production",
    "production_reference",
    "order_cost_report",
    "printing_cost_report",
    '"order"',
    "operation",
    "printing",
    '"user"',
)
_SIMPLE_TABLES = (
    "cutter_info",
    "economy",
    "list_size",
    "edition",
    "press_sheet",
    "production",
    "production_reference",
    "order_cost_report",
    "operation",
    '"user"',
)
_WORKPLACE_TABLES = (
    "workplace_order",
    "workplace_operation_cost",
    "workplace_printing",
    "workplace_cost_report",
    "workplace_printing_cost",
    "workplace_reference",
)
_EXPECTED_TABLES = {name.strip('"') for name in _OLD_TABLES}
_EXPECTED_TABLES.update(_WORKPLACE_TABLES)
_EXPECTED_TABLES.add("alembic_version")

_COLUMN_COMMENTS = {
    ("cutter_info", "stack_height"): "Высота стопки помещающейся в резаке в мм",
    ("economy", "markup"): "Наценка в %",
    ("economy", "tax_rate"): "Налоговая ставка (0,93 = 7%)",
    ("press_sheet", "height"): "Высота в мм",
    ("press_sheet", "width"): "Ширина в мм",
    ("press_sheet", "spacing"): "Поля в мм",
    ("production", "black_ink_cost"): "Стоимость чёрной краски на 1 листе в руб.",
    ("production", "ink_cost"): "Стоимость всех красок на 1 листе в руб.",
    ("production", "printer_salary"): "Зарплата печатнику за 1 лист в руб.",
    ("production", "lamination_cost"): "Цена ламинации 1 листа в руб.",
    ("production", "die_cutting_cost"): "Стоимость высечки 1 листа в руб.",
    ("production", "paper_cost"): "Стоимость 1кг бумаги в руб.",
    ("production", "cutting_cost"): "Цена 1 реза в руб.",
    ("production", "sheet_by_fitting"): "Количество листов на приладку в шт.",
    ("operation", "name"): "Название операции.",
    ("operation", "cost"): "Стоимость операции в руб.",
    ("operation", "description"): "Описание операции",
}
_MONEY_COLUMNS = (
    ("order_cost_report", "unit_cost_price"),
    ("order_cost_report", "unit_cost"),
    ("order_cost_report", "edition_cost"),
    ("order_cost_report", "profit_after_tax"),
    ("printing_cost_report", "unit_cost_price"),
    ("printing_cost_report", "unit_cost"),
    ("printing_cost_report", "edition_cost"),
    ("printing_cost_report", "profit_before_tax"),
    ("printing_cost_report", "profit_after_tax"),
    ("printing_cost_report", "edition_cost_price"),
)
_NUMERIC_10_4 = (
    ("economy", "markup"),
    ("economy", "tax_rate"),
    ("production", "black_ink_cost"),
    ("production", "ink_cost"),
    ("production", "printer_salary"),
    ("production", "lamination_cost"),
    ("production", "die_cutting_cost"),
    ("production", "paper_cost"),
    ("production", "cutting_cost"),
    ("operation", "cost"),
)
_FOREIGN_KEYS = (
    "edition_list_size_id_fkey",
    "production_press_sheet_id_fkey",
    "production_cutter_id_fkey",
    "production_reference_production_id_fkey",
    "printing_cost_report_order_cost_report_id_fkey",
    "fk_order_economy",
    "order_order_cost_report_id_fkey",
    "operation_order_id_fkey",
    "printing_order_id_fkey",
    "printing_production_id_fkey",
    "printing_edition_id_fkey",
    "printing_printing_cost_report_id_fkey",
)


@contextmanager
def _migration_database() -> Iterator[tuple[Config, Engine]]:
    admin_config = DBConfig.from_env().model_copy(update={"db_name": "postgres"})
    admin = create_engine(
        admin_config.get_db_url("psycopg"),
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 5},
    )
    temporary_name: str | None = None
    temporary_engine: Engine | None = None
    try:
        try:
            with admin.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception as error:
            raise RuntimeError(
                "cannot connect to the postgres database; "
                "the migration test does not use the application database"
            ) from error
        name = "ph_mig_" + uuid.uuid4().hex[:8]
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
        temporary_name = name
        temporary = admin_config.model_copy(update={"db_name": name})
        temporary_engine = create_engine(temporary.get_db_url("psycopg"))

        def from_dotenv(path_to_env: str | Path) -> DBConfig:
            return temporary

        with patch.object(DBConfig, "from_dotenv", from_dotenv):
            yield Config(str(_ALEMBIC_INI)), temporary_engine
    finally:
        if temporary_engine is not None:
            temporary_engine.dispose()
        if temporary_name is not None:
            with admin.connect() as connection:
                connection.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE datname = :name AND pid <> pg_backend_pid()"
                    ),
                    {"name": temporary_name},
                )
                connection.execute(text(f'DROP DATABASE IF EXISTS "{temporary_name}"'))
        admin.dispose()


def _next_value(connection: Connection, sequence: str) -> int:
    last_value, is_called = connection.execute(
        text(f"SELECT last_value, is_called FROM {sequence}")
    ).one()
    if is_called:
        return int(last_value) + 1
    return int(last_value)


def _sequence_state(connection: Connection, sequence: str) -> tuple[int, bool]:
    last_value, is_called = connection.execute(
        text(f"SELECT last_value, is_called FROM {sequence}")
    ).one()
    return int(last_value), bool(is_called)


def _row_counts(connection: Connection, tables: tuple[str, ...]) -> dict[str, int]:
    return {
        table: int(connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one())
        for table in tables
    }


def _public_tables(connection: Connection) -> set[str]:
    rows = connection.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    ).scalars()
    return set(rows)


def _column_default(connection: Connection, table: str, column: str) -> str:
    default = connection.execute(
        text(
            """
            SELECT pg_get_expr(def.adbin, def.adrelid)
            FROM pg_attrdef AS def
            JOIN pg_attribute AS attr
              ON attr.attrelid = def.adrelid AND attr.attnum = def.adnum
            JOIN pg_class AS rel ON rel.oid = attr.attrelid
            JOIN pg_namespace AS ns ON ns.oid = rel.relnamespace
            WHERE ns.nspname = 'public'
              AND rel.relname = :table
              AND attr.attname = :column
            """
        ),
        {"table": table, "column": column},
    ).scalar_one()
    return str(default)


def _prepare_stamped_database(
    engine: Engine,
    *,
    full: bool,
    rows: bool,
    next_values: tuple[int, int, int],
) -> None:
    order_next, printing_next, report_next = next_values
    statements = [
        "CREATE SEQUENCE order_id_seq START WITH 1 INCREMENT BY 1",
        'CREATE TABLE "order" (id bigint PRIMARY KEY)',
        """
        CREATE TABLE printing (
            id bigint GENERATED BY DEFAULT AS IDENTITY
                (SEQUENCE NAME printing_id_seq START WITH 1 INCREMENT BY 1)
                PRIMARY KEY
        )
        """,
        "CREATE SEQUENCE printing_cost_report_id_seq START WITH 1 INCREMENT BY 1",
        """
        CREATE TABLE printing_cost_report (
            id bigint PRIMARY KEY
                DEFAULT nextval('printing_cost_report_id_seq')
        )
        """,
        """
        CREATE TABLE alembic_version (
            version_num varchar(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        )
        """,
        "INSERT INTO alembic_version (version_num) VALUES ('53a756fbc804')",
    ]
    if full:
        statements[5:5] = [
            f"CREATE TABLE {table} (id bigint PRIMARY KEY)" for table in _SIMPLE_TABLES
        ]
    if rows:
        statements.extend([
            'INSERT INTO "order" (id) VALUES (890)',
            "INSERT INTO printing (id) VALUES (893)",
            "INSERT INTO printing_cost_report (id) VALUES (1640)",
        ])
        if full:
            statements.extend(
                f"INSERT INTO {table} (id) VALUES (1)" for table in _SIMPLE_TABLES
            )
    statements.extend([
        f"SELECT setval('order_id_seq', {order_next}, false)",
        f"SELECT setval('printing_id_seq', {printing_next}, false)",
        f"SELECT setval('printing_cost_report_id_seq', {report_next}, false)",
    ])
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def test_should_create_the_production_schema_when_the_database_is_empty() -> None:
    with _migration_database() as (config, engine):
        command.upgrade(config, "head")
        with engine.connect() as connection:
            version = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            assert version == "b6d4e2a81c05"
            assert _public_tables(connection) == _EXPECTED_TABLES
            assert _row_counts(connection, _OLD_TABLES) == {table: 0 for table in _OLD_TABLES}
            assert _next_value(connection, "order_id_seq") == 1
            assert _next_value(connection, "printing_id_seq") == 1
            assert _next_value(connection, "printing_cost_report_id_seq") == 1
            order_default = _column_default(connection, "order", "id")
            assert "nextval" in order_default
            assert "order_id_seq" in order_default
            identity = connection.execute(
                text(
                    """
                    SELECT attr.attidentity
                    FROM pg_attribute AS attr
                    JOIN pg_class AS rel ON rel.oid = attr.attrelid
                    JOIN pg_namespace AS ns ON ns.oid = rel.relnamespace
                    WHERE ns.nspname = 'public'
                      AND rel.relname = 'printing'
                      AND attr.attname = 'id'
                    """
                )
            ).scalar_one()
            assert identity == "d"
            sequence_name = connection.execute(
                text(
                    """
                    SELECT seq.relname
                    FROM pg_class AS seq
                    JOIN pg_depend AS dep ON dep.objid = seq.oid
                    JOIN pg_class AS rel ON dep.refobjid = rel.oid
                    JOIN pg_attribute AS attr
                      ON attr.attrelid = rel.oid AND attr.attnum = dep.refobjsubid
                    JOIN pg_namespace AS ns ON ns.oid = rel.relnamespace
                    WHERE ns.nspname = 'public'
                      AND rel.relname = 'printing'
                      AND attr.attname = 'id'
                      AND seq.relkind = 'S'
                    """
                )
            ).scalar_one()
            assert sequence_name == "printing_id_seq"
            report_default = _column_default(connection, "printing_cost_report", "id")
            assert "printing_cost_report_id_seq" in report_default
            owned = connection.execute(
                text(
                    """
                    SELECT dep.deptype
                    FROM pg_depend AS dep
                    JOIN pg_class AS seq ON seq.oid = dep.objid
                    JOIN pg_class AS rel ON rel.oid = dep.refobjid
                    JOIN pg_attribute AS attr
                      ON attr.attrelid = rel.oid AND attr.attnum = dep.refobjsubid
                    WHERE seq.relname = 'printing_cost_report_id_seq'
                      AND rel.relname = 'printing_cost_report'
                      AND attr.attname = 'id'
                      AND dep.deptype = 'a'
                    """
                )
            ).scalar_one()
            assert owned == "a"
            inserted = connection.execute(
                text(
                    """
                    INSERT INTO "order" (creation_date, status, comment)
                    VALUES (DATE '2026-01-01', 'SAVED'::order_status, 'note')
                    RETURNING id, economy_id
                    """
                )
            ).one()
            assert inserted.id is not None
            assert inserted.economy_id is None
            order_sequence = _sequence_state(connection, "order_id_seq")
            printing_id = connection.execute(
                text("INSERT INTO printing (comment) VALUES ('note') RETURNING id")
            ).scalar_one()
            assert printing_id is not None
            assert _sequence_state(connection, "order_id_seq") == order_sequence
            cost_sequence = _sequence_state(connection, "cost_report_id_seq")
            connection.execute(
                text(
                    """
                    INSERT INTO order_cost_report (
                        unit_cost_price, unit_cost, edition_cost, profit_after_tax
                    ) VALUES (1, 1, 1, 1)
                    """
                )
            )
            moved_cost_sequence = _sequence_state(connection, "cost_report_id_seq")
            assert moved_cost_sequence != cost_sequence
            printing_report_id = connection.execute(
                text(
                    """
                    INSERT INTO printing_cost_report (
                        items_per_sheet, sheet_count, unit_cost_price, unit_cost,
                        edition_cost, profit_before_tax, profit_after_tax,
                        edition_cost_price
                    ) VALUES (1, 1, 1, 1, 1, 1, 1, 1)
                    RETURNING id
                    """
                )
            ).scalar_one()
            assert printing_report_id is not None
            assert _sequence_state(connection, "cost_report_id_seq") == moved_cost_sequence
            comments = {
                (table, column): comment
                for table, column, comment in connection.execute(
                    text(
                        """
                        SELECT rel.relname, attr.attname,
                               col_description(attr.attrelid, attr.attnum)
                        FROM pg_attribute AS attr
                        JOIN pg_class AS rel ON rel.oid = attr.attrelid
                        JOIN pg_namespace AS ns ON ns.oid = rel.relnamespace
                        WHERE ns.nspname = 'public'
                          AND attr.attnum > 0
                          AND NOT attr.attisdropped
                          AND col_description(attr.attrelid, attr.attnum) IS NOT NULL
                        """
                    )
                )
            }
            assert comments == _COLUMN_COMMENTS
            for name in _FOREIGN_KEYS:
                definition = connection.execute(
                    text(
                        """
                        SELECT pg_get_constraintdef(oid)
                        FROM pg_constraint
                        WHERE conname = :name AND contype = 'f'
                        """
                    ),
                    {"name": name},
                ).scalar_one()
                assert "ON UPDATE CASCADE" in definition
                assert "ON DELETE CASCADE" in definition
            for table, column in _MONEY_COLUMNS:
                precision = connection.execute(
                    text(
                        """
                        SELECT numeric_precision
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = :table
                          AND column_name = :column
                        """
                    ),
                    {"table": table, "column": column},
                ).scalar_one()
                assert precision is None
            for table, column in _NUMERIC_10_4:
                precision, scale = connection.execute(
                    text(
                        """
                        SELECT numeric_precision, numeric_scale
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = :table
                          AND column_name = :column
                        """
                    ),
                    {"table": table, "column": column},
                ).one()
                assert precision == 10
                assert scale == 4


def test_should_keep_existing_rows_and_advance_only_lagging_sequences_when_the_database_is_already_at_the_baseline() -> None:
    with _migration_database() as (config, engine):
        _prepare_stamped_database(
            engine,
            full=True,
            rows=True,
            next_values=(894, 108, 1),
        )
        with engine.connect() as connection:
            before = _row_counts(connection, _OLD_TABLES)
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert _row_counts(connection, _OLD_TABLES) == before
            names = _public_tables(connection)
            for name in _WORKPLACE_TABLES:
                assert name in names
            order_default = _column_default(connection, "order", "id")
            assert "order_id_seq" in order_default
            identity = connection.execute(
                text(
                    """
                    SELECT attr.attidentity
                    FROM pg_attribute AS attr
                    JOIN pg_class AS rel ON rel.oid = attr.attrelid
                    WHERE rel.relname = 'printing' AND attr.attname = 'id'
                    """
                )
            ).scalar_one()
            assert identity == "d"
            sequence_name = connection.execute(
                text(
                    """
                    SELECT seq.relname
                    FROM pg_class AS seq
                    JOIN pg_depend AS dep ON dep.objid = seq.oid
                    JOIN pg_class AS rel ON dep.refobjid = rel.oid
                    JOIN pg_attribute AS attr
                      ON attr.attrelid = rel.oid AND attr.attnum = dep.refobjsubid
                    WHERE rel.relname = 'printing'
                      AND attr.attname = 'id'
                      AND seq.relkind = 'S'
                    """
                )
            ).scalar_one()
            assert sequence_name == "printing_id_seq"
            assert _next_value(connection, "order_id_seq") == 894
            assert _next_value(connection, "printing_id_seq") == 894
            assert _next_value(connection, "printing_cost_report_id_seq") == 1641


def test_should_leave_an_empty_table_sequence_where_it_is_when_the_repair_runs() -> None:
    with _migration_database() as (config, engine):
        _prepare_stamped_database(
            engine,
            full=False,
            rows=False,
            next_values=(5, 7, 9),
        )
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert _next_value(connection, "order_id_seq") == 5
            assert _next_value(connection, "printing_id_seq") == 7
            assert _next_value(connection, "printing_cost_report_id_seq") == 9


def test_should_not_move_sequences_or_delete_old_rows_when_the_workplace_revision_runs_again() -> None:
    with _migration_database() as (config, engine):
        _prepare_stamped_database(
            engine,
            full=True,
            rows=True,
            next_values=(894, 108, 1),
        )
        command.upgrade(config, "head")
        with engine.connect() as connection:
            remembered = (
                _next_value(connection, "order_id_seq"),
                _next_value(connection, "printing_id_seq"),
                _next_value(connection, "printing_cost_report_id_seq"),
            )
            counts = _row_counts(connection, _OLD_TABLES)
        command.downgrade(config, "53a756fbc804")
        with engine.connect() as connection:
            names = _public_tables(connection)
            for name in _WORKPLACE_TABLES:
                assert name not in names
            assert _row_counts(connection, _OLD_TABLES) == counts
            assert "order_id_seq" in _column_default(connection, "order", "id")
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert (
                _next_value(connection, "order_id_seq"),
                _next_value(connection, "printing_id_seq"),
                _next_value(connection, "printing_cost_report_id_seq"),
            ) == remembered
            assert _row_counts(connection, _OLD_TABLES) == counts


def test_should_fill_creation_date_and_empty_texts_when_old_workplace_rows_upgrade() -> None:
    with _migration_database() as (config, engine):
        command.upgrade(config, "733171f352dd")
        with engine.begin() as connection:
            order_id = connection.execute(text(
                """
                INSERT INTO workplace_order
                    (comment, status, unit_count, tax_rate, markup)
                VALUES ('старый', 'SAVED', 1, 0, 0)
                RETURNING id
                """
            )).scalar_one()
            connection.execute(text(
                """
                INSERT INTO workplace_operation_cost
                    (order_id, position, amount)
                VALUES (:order_id, 0, 10.5)
                """
            ), {"order_id": order_id})
            connection.execute(text(
                """
                INSERT INTO workplace_printing (
                    order_id, position, count, sheet_by_fitting,
                    stack_height, press_sheet_density, press_sheet_width,
                    press_sheet_height, press_sheet_spacing, list_width,
                    list_height, list_bleeds, chroma, lamination,
                    die_cutting, press_cyan, press_magenta, press_yellow,
                    press_black, press_paper, press_salary, cut_salary,
                    lamination_startup, lamination_film_cost,
                    lamination_salary, die_cut_salary
                ) VALUES (
                    :order_id, 0, 1, 0,
                    0, 80, 100,
                    100, 0, 10,
                    20, 0, 'ZERO_ZERO', 'DONT',
                    false, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0,
                    0, 0
                )
                """
            ), {"order_id": order_id})
        command.upgrade(config, "head")
        with engine.connect() as connection:
            same_day = connection.execute(text(
                "SELECT creation_date = CURRENT_DATE "
                "FROM workplace_order WHERE id = :id"
            ), {"id": order_id}).scalar_one()
            assert same_day is True
            operation = connection.execute(text(
                "SELECT name, description, amount "
                "FROM workplace_operation_cost WHERE order_id = :id"
            ), {"id": order_id}).one()
            assert operation.name == ""
            assert operation.description == ""
            assert operation.amount == Decimal("10.5")
            comment = connection.execute(text(
                "SELECT comment FROM workplace_printing "
                "WHERE order_id = :id"
            ), {"id": order_id}).scalar_one()
            assert comment == ""
            reference_count = connection.execute(text(
                "SELECT count(*) FROM workplace_reference"
            )).scalar_one()
            assert reference_count == 0


def test_versions_directory_keeps_the_baseline_workplace_tables_and_order_fields() -> None:
    paths = list(_VERSIONS.glob("*.py"))
    revisions: list[tuple[str, object]] = []
    for path in paths:
        values: dict[str, object] = {}
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            target = None
            value = None
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target = node.target.id
                value = node.value
            elif (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                target = node.targets[0].id
                value = node.value
            if target in {"revision", "down_revision"} and value is not None:
                values[target] = ast.literal_eval(value)
        revisions.append((str(values["revision"]), values["down_revision"]))
    assert len(paths) == 3
    assert ("53a756fbc804", None) in revisions
    assert ("733171f352dd", "53a756fbc804") in revisions
    assert ("b6d4e2a81c05", "733171f352dd") in revisions
