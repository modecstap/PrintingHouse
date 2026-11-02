from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.accountant.money import Money
from backend.core.accountant.pricing.cutting import CuttingCalculation
from backend.core.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.core.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.core.accountant.pricing.printing import PrintingCalculation
from backend.core.order import (
    List,
    Operation,
    Order,
    Printing,
    Status,
)
from backend.core.reports import CostReport, PrintingCost
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma, PressSheet
from backend.storage.tables.workplace_order import (
    CostReportRow,
    OperationCostRow,
    PrintingCostRow,
    PrintingRow,
    WorkplaceOrderRow,
    WorkplaceReferenceRow,
)


def _as_decimal(value: object) -> Decimal:
    # Money принимает только объект, у которого type is Decimal.
    if type(value) is Decimal:
        return value
    return Decimal(str(value))


def _money(value: object) -> Money:
    return Money(_as_decimal(value))


def _as_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise TypeError(
        "creation_date: ожидается date, пришло "
        f"{type(value).__name__}"
    )


def _fill_header(row: WorkplaceOrderRow, order: Order) -> None:
    row.comment = order.comment
    row.status = order.status.name
    row.unit_count = order.unit_count
    row.tax_rate = order.tax_rate
    row.markup = order.markup


def _printing_row(order_id: int, position: int, printing: Printing) -> PrintingRow:
    press = printing.press_pricing
    sheet = printing.list
    press_sheet = printing.press_sheet
    return PrintingRow(
        order_id=order_id,
        position=position,
        count=printing.count,
        sheet_by_fitting=printing.sheet_by_fitting,
        stack_height=printing.stack_height,
        press_sheet_density=press_sheet.density,
        press_sheet_width=press_sheet.width,
        press_sheet_height=press_sheet.height,
        press_sheet_spacing=press_sheet.spacing,
        list_width=sheet.width,
        list_height=sheet.height,
        list_bleeds=sheet.bleeds,
        chroma=printing.chroma.name,
        lamination=printing.lamination.name,
        die_cutting=printing.die_cutting,
        press_cyan=press.cyan.amount,
        press_magenta=press.magenta.amount,
        press_yellow=press.yellow.amount,
        press_black=press.black.amount,
        press_paper=press.paper.amount,
        press_salary=press.salary.amount,
        cut_salary=printing.cut_pricing.salary.amount,
        lamination_startup=printing.lamination_pricing.startup.amount,
        lamination_film_cost=printing.lamination_pricing.film_cost.amount,
        lamination_salary=printing.lamination_pricing.salary.amount,
        die_cut_salary=printing.die_cut_pricing.salary.amount,
        comment=printing.comment,
    )


def _replace_calculation(session: Session, order_id: int, order: Order) -> None:
    session.execute(
        delete(OperationCostRow).where(OperationCostRow.order_id == order_id)
    )
    session.execute(delete(PrintingRow).where(PrintingRow.order_id == order_id))
    for position, operation in enumerate(order.operations):
        session.add(
            OperationCostRow(
                order_id=order_id,
                position=position,
                amount=operation.cost,
                name=operation.name,
                description=operation.description,
            )
        )
    for position, printing in enumerate(order.printings):
        session.add(_printing_row(order_id, position, printing))


def _printing_from_row(row: PrintingRow) -> Printing:
    sheet = List(row.list_width, row.list_height, row.list_bleeds)
    return Printing(
        count=row.count,
        chroma=Chroma[row.chroma],
        lamination=Lamination[row.lamination],
        die_cutting=row.die_cutting,
        sheet_by_fitting=row.sheet_by_fitting,
        stack_height=row.stack_height,
        press_sheet=PressSheet(
            row.press_sheet_density,
            row.press_sheet_width,
            row.press_sheet_height,
            row.press_sheet_spacing,
        ),
        list=sheet,
        press_pricing=PrintingCalculation(
            _money(row.press_cyan),
            _money(row.press_magenta),
            _money(row.press_yellow),
            _money(row.press_black),
            _money(row.press_paper),
            _money(row.press_salary),
        ),
        cut_pricing=CuttingCalculation(_money(row.cut_salary)),
        lamination_pricing=LaminationCalculation(
            _money(row.lamination_startup),
            _money(row.lamination_film_cost),
            _money(row.lamination_salary),
        ),
        die_cut_pricing=DieCuttingCalculation(_money(row.die_cut_salary)),
        comment=row.comment,
    )


def _cost_report(session: Session, row: CostReportRow) -> CostReport:
    costs = session.scalars(
        select(PrintingCostRow)
        .where(PrintingCostRow.cost_report_id == row.id)
        .order_by(PrintingCostRow.position)
    ).all()
    return CostReport(
        unit_cost_price=_as_decimal(row.unit_cost_price),
        unit_cost=_as_decimal(row.unit_cost),
        edition_cost=_as_decimal(row.edition_cost),
        profit_after_tax=_as_decimal(row.profit_after_tax),
        printing_cost_reports=tuple(
            PrintingCost(
                items_per_sheet=item.items_per_sheet,
                sheet_count=item.sheet_count,
                unit_cost_price=_as_decimal(item.unit_cost_price),
                unit_cost=_as_decimal(item.unit_cost),
                edition_cost_price=_as_decimal(item.edition_cost_price),
                edition_cost=_as_decimal(item.edition_cost),
                profit_before_tax=_as_decimal(item.profit_before_tax),
                profit_after_tax=_as_decimal(item.profit_after_tax),
            )
            for item in costs
        ),
    )


def insert_order(session: Session, order: Order) -> int:
    """Inserts the order header and the calculation children.

    :param session:
    :param order:

    :return: the id that the database assigned.
    """
    row = WorkplaceOrderRow()
    _fill_header(row, order)
    row.creation_date = date.today()
    session.add(row)
    session.flush()
    _replace_calculation(session, row.id, order)
    return row.id


def update_order(
    session: Session, row: WorkplaceOrderRow, order: Order
) -> None:
    """Replaces the header and the calculation children of an existing row.

    :param session:
    :param row: the row is already in the database.
    :param order:
    """
    _fill_header(row, order)
    _replace_calculation(session, row.id, order)


def read_order(session: Session, row: WorkplaceOrderRow) -> Order:
    """Builds an order from the header and the calculation children.

    :param session:
    :param row:

    :return: a new Order with the row's id and the column's creation_date.
    If the driver returned a datetime, the date is taken.
    """
    costs = session.scalars(
        select(OperationCostRow)
        .where(OperationCostRow.order_id == row.id)
        .order_by(OperationCostRow.position)
    ).all()
    printings = session.scalars(
        select(PrintingRow)
        .where(PrintingRow.order_id == row.id)
        .order_by(PrintingRow.position)
    ).all()
    return Order(
        unit_count=row.unit_count,
        tax_rate=_as_decimal(row.tax_rate),
        markup=_as_decimal(row.markup),
        operations=tuple(
            Operation(item.name, _as_decimal(item.amount), item.description)
            for item in costs
        ),
        printings=tuple(_printing_from_row(item) for item in printings),
        id=row.id,
        comment=row.comment,
        status=Status[row.status],
        creation_date=_as_date(row.creation_date),
    )


def write_report(
    session: Session,
    report: CostReport,
    order_id: int,
    position: int,
) -> None:
    """Writes one report and its PrintingCost.

    :param session:
    :param report:
    :param order_id:
    :param position: already calculated.
    """
    row = CostReportRow(
        order_id=order_id,
        position=position,
        unit_cost_price=report.unit_cost_price,
        unit_cost=report.unit_cost,
        edition_cost=report.edition_cost,
        profit_after_tax=report.profit_after_tax,
    )
    session.add(row)
    session.flush()
    for index, printing_cost in enumerate(report.printing_cost_reports):
        session.add(
            PrintingCostRow(
                cost_report_id=row.id,
                position=index,
                items_per_sheet=printing_cost.items_per_sheet,
                sheet_count=printing_cost.sheet_count,
                unit_cost_price=printing_cost.unit_cost_price,
                unit_cost=printing_cost.unit_cost,
                edition_cost_price=printing_cost.edition_cost_price,
                edition_cost=printing_cost.edition_cost,
                profit_before_tax=printing_cost.profit_before_tax,
                profit_after_tax=printing_cost.profit_after_tax,
            )
        )


def read_reports(session: Session, order_id: int) -> list[CostReport]:
    """Returns the order's reports by position, ascending.

    :param session:
    :param order_id:

    :return: an empty list if there are no reports.
    An empty PrintingCost set gives an empty tuple.
    """
    rows = session.scalars(
        select(CostReportRow)
        .where(CostReportRow.order_id == order_id)
        .order_by(CostReportRow.position)
    ).all()
    return [_cost_report(session, row) for row in rows]


def _text_money(value: Money) -> str:
    return str(value.amount)


def _object_field(
    document: dict[str, object], key: str
) -> dict[str, object]:
    value = document[key]
    if type(value) is not dict:
        raise TypeError(
            f"справочник: {key} ожидается объект, "
            f"пришло {type(value).__name__}"
        )
    # Ключи JSON-объекта — строки.
    return {str(item_key): item for item_key, item in value.items()}


def _list_field(document: dict[str, object], key: str) -> list[object]:
    value = document[key]
    if type(value) is not list:
        raise TypeError(
            f"справочник: {key} ожидается список, "
            f"пришло {type(value).__name__}"
        )
    return value


def _str_field(document: dict[str, object], key: str) -> str:
    value = document[key]
    if type(value) is not str:
        raise TypeError(
            f"справочник: {key} ожидается строка, "
            f"пришло {type(value).__name__}"
        )
    return value


def _int_field(document: dict[str, object], key: str) -> int:
    value = document[key]
    if type(value) is not int:
        raise TypeError(
            f"справочник: {key} ожидается целое, "
            f"пришло {type(value).__name__}"
        )
    return value


def _bool_field(document: dict[str, object], key: str) -> bool:
    value = document[key]
    if type(value) is not bool:
        raise TypeError(
            f"справочник: {key} ожидается булево, "
            f"пришло {type(value).__name__}"
        )
    return value


def _decimal_field(document: dict[str, object], key: str) -> Decimal:
    return Decimal(_str_field(document, key))


def _money_field(document: dict[str, object], key: str) -> Money:
    return Money(_decimal_field(document, key))


def _printing_document(printing: Printing) -> dict[str, object]:
    press = printing.press_pricing
    page = printing.list
    sheet = printing.press_sheet
    lamination = printing.lamination_pricing
    return {
        "count": printing.count,
        "chroma": printing.chroma.name,
        "lamination": printing.lamination.name,
        "die_cutting": printing.die_cutting,
        "sheet_by_fitting": printing.sheet_by_fitting,
        "stack_height": printing.stack_height,
        "press_sheet": {
            "density": sheet.density,
            "width": sheet.width,
            "height": sheet.height,
            "spacing": sheet.spacing,
        },
        "list": {
            "width": page.width,
            "height": page.height,
            "bleeds": page.bleeds,
        },
        "press_pricing": {
            "cyan": _text_money(press.cyan),
            "magenta": _text_money(press.magenta),
            "yellow": _text_money(press.yellow),
            "black": _text_money(press.black),
            "paper": _text_money(press.paper),
            "salary": _text_money(press.salary),
        },
        "cut_pricing": {
            "salary": _text_money(printing.cut_pricing.salary),
        },
        "lamination_pricing": {
            "startup": _text_money(lamination.startup),
            "film_cost": _text_money(lamination.film_cost),
            "salary": _text_money(lamination.salary),
        },
        "die_cut_pricing": {
            "salary": _text_money(printing.die_cut_pricing.salary),
        },
        "comment": printing.comment,
    }


def _printing_from_document(value: object) -> Printing:
    if type(value) is not dict:
        raise TypeError(
            "справочник: печать ожидается объектом, "
            f"пришло {type(value).__name__}"
        )
    item = {str(key): nested for key, nested in value.items()}
    sheet = _object_field(item, "press_sheet")
    page = _object_field(item, "list")
    press = _object_field(item, "press_pricing")
    cut = _object_field(item, "cut_pricing")
    lamination = _object_field(item, "lamination_pricing")
    die_cut = _object_field(item, "die_cut_pricing")
    return Printing(
        count=_int_field(item, "count"),
        chroma=Chroma[_str_field(item, "chroma")],
        lamination=Lamination[_str_field(item, "lamination")],
        die_cutting=_bool_field(item, "die_cutting"),
        sheet_by_fitting=_int_field(item, "sheet_by_fitting"),
        stack_height=_int_field(item, "stack_height"),
        press_sheet=PressSheet(
            _int_field(sheet, "density"),
            _int_field(sheet, "width"),
            _int_field(sheet, "height"),
            _int_field(sheet, "spacing"),
        ),
        list=List(
            _int_field(page, "width"),
            _int_field(page, "height"),
            _int_field(page, "bleeds"),
        ),
        press_pricing=PrintingCalculation(
            _money_field(press, "cyan"),
            _money_field(press, "magenta"),
            _money_field(press, "yellow"),
            _money_field(press, "black"),
            _money_field(press, "paper"),
            _money_field(press, "salary"),
        ),
        cut_pricing=CuttingCalculation(_money_field(cut, "salary")),
        lamination_pricing=LaminationCalculation(
            _money_field(lamination, "startup"),
            _money_field(lamination, "film_cost"),
            _money_field(lamination, "salary"),
        ),
        die_cut_pricing=DieCuttingCalculation(
            _money_field(die_cut, "salary")
        ),
        comment=_str_field(item, "comment"),
    )


def reference_document(order: Order) -> dict[str, object]:
    """Builds a reference document from an order.

    :param order:

    :return: the reference JSON document. id is always null.
    creation_date is not in the document.
    """
    # id всегда null. creation_date в документ не входит:
    # дата есть только у строки заказа.
    return {
        "id": None,
        "unit_count": order.unit_count,
        "tax_rate": str(order.tax_rate),
        "markup": str(order.markup),
        "operations": [
            {
                "name": item.name,
                "cost": str(item.cost),
                "description": item.description,
            }
            for item in order.operations
        ],
        "printings": [
            _printing_document(item) for item in order.printings
        ],
        "comment": order.comment,
        "status": order.status.name,
    }


def _order_from_document(document: object) -> Order:
    if type(document) is not dict:
        raise TypeError(
            "справочник: документ ожидается объектом, "
            f"пришло {type(document).__name__}"
        )
    body = {str(key): value for key, value in document.items()}
    operations = _list_field(body, "operations")
    printings = _list_field(body, "printings")
    return Order(
        unit_count=_int_field(body, "unit_count"),
        tax_rate=_decimal_field(body, "tax_rate"),
        markup=_decimal_field(body, "markup"),
        operations=tuple(
            _operation_from_document(item) for item in operations
        ),
        printings=tuple(
            _printing_from_document(item) for item in printings
        ),
        id=None,
        comment=_str_field(body, "comment"),
        status=Status[_str_field(body, "status")],
        creation_date=None,
    )


def _operation_from_document(value: object) -> Operation:
    if type(value) is not dict:
        raise TypeError(
            "справочник: операция ожидается объектом, "
            f"пришло {type(value).__name__}"
        )
    item = {str(key): nested for key, nested in value.items()}
    return Operation(
        _str_field(item, "name"),
        _decimal_field(item, "cost"),
        _str_field(item, "description"),
    )


def write_reference(session: Session, order: Order) -> None:
    """Replaces the reference document with one upsert.

    :param session:
    :param order:
    """
    statement = insert(WorkplaceReferenceRow).values(
        id=1,
        document=reference_document(order),
    )
    session.execute(
        statement.on_conflict_do_update(
            index_elements=[WorkplaceReferenceRow.id],
            set_={"document": statement.excluded.document},
        )
    )


def read_reference(session: Session) -> Order | None:
    """Builds an order from the reference document.

    :param session:

    :return: None if there is no row. Otherwise an Order with id None
    and creation_date None.
    """
    row = session.get(WorkplaceReferenceRow, 1)
    if row is None:
        return None
    return _order_from_document(row.document)
