from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import delete, select
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
from backend.workplace.cost_order import (
    List,
    Operation,
    Order,
    Printing,
    Status,
)
from backend.workplace.reports import CostReport, PrintingCost
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import Chroma, PressSheet
from backend.workplace_order_db.tables import (
    CostReportRow,
    OperationCostRow,
    PrintingCostRow,
    PrintingRow,
    WorkplaceOrderRow,
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
    """Вставляет шапку заказа и детей расчёта.

    Результат: id, который назначила база.
    Побочные эффекты: creation_date равен date.today() процесса.
    order.creation_date не читается. Строки CostReport не пишет.
    Переданный Order не меняет.
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
    """Заменяет шапку и детей расчёта у существующей строки.

    Предусловия: row уже есть в базе.
    Побочные эффекты: creation_date не меняет. Удаляет операции
    и печати этого заказа и вставляет их заново. Строки CostReport
    не меняет. Переданный Order не меняет.
    """
    _fill_header(row, order)
    _replace_calculation(session, row.id, order)


def read_order(session: Session, row: WorkplaceOrderRow) -> Order:
    """Собирает заказ из шапки и детей расчёта.

    Результат: новый Order с id строки и creation_date колонки.
    Если драйвер вернул datetime, берётся date. Отчёты рабочих мест
    к ставкам не прикрепляет. Список CostReport не читает.
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
    """Пишет один отчёт и его PrintingCost.

    Предусловия: position уже вычислен.
    Побочные эффекты: добавляет шапку отчёта и PrintingCost
    с позицией, равной индексу в кортеже.
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
    """Возвращает отчёты заказа по position по возрастанию.

    Результат: пустой список, если отчётов нет. Пустой набор
    PrintingCost даёт пустой кортеж.
    """
    rows = session.scalars(
        select(CostReportRow)
        .where(CostReportRow.order_id == order_id)
        .order_by(CostReportRow.position)
    ).all()
    return [_cost_report(session, row) for row in rows]
