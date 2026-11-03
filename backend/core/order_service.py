from dataclasses import replace

from backend.core.administrator import Administrator
from backend.core.order import (
    Order,
    Printing,
    Status,
    empty_reference_order,
)
from backend.core.sheet.format import SheetFormat
from backend.core.sheet.sheet import Sheet
from backend.core.order_repository import (
    OrderId,
    WorkplaceOrderRepository,
)
from backend.core.reports import CostReport


class WorkplaceOrderService:
    def __init__(
        self,
        orders: WorkplaceOrderRepository,
        administrator: Administrator,
    ) -> None:
        """Remembers the order repository and the administrator.

        :param orders:
        :param administrator:
        """
        self._orders = orders
        self._administrator = administrator

    def save(self, order: Order) -> OrderId:
        """Writes the calculation data, comment, and the passed status.

        :param order:

        :raises OrderNotFound: if the given id has no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved row. An empty id is assigned by the database.
        An existing id is returned unchanged.
        """
        return self._orders.save(order)

    def take(self, order_id: OrderId) -> Order:
        """Returns one order without the CostReport list.

        :param order_id:

        :raises OrderNotFound: if there is no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the order with calculation data, comment, status,
        and the insertion date.
        """
        return self._orders.take(order_id)

    def take_all(self) -> list[Order]:
        """Returns each order row once.

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the orders by descending id, without reports. No rows: an empty list.
        """
        return self._orders.take_all()

    def reference(self) -> Order:
        """Returns the reference or an empty order.

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the reference row, if it exists. No row:
        the order from empty_reference_order.
        """
        stored = self._orders.reference()
        if stored is None:
            return empty_reference_order()
        return stored

    def set_reference(self, order: Order) -> None:
        """Replaces the reference with this order.

        :param order:

        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        self._orders.set_reference(replace(order, id=None))

    def delete(self, order_id: OrderId) -> None:
        """Deletes the order, its calculation, and its reports.

        :param order_id:

        :raises OrderNotFound: if there is no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing. After the deletion, take does not find this id.
        """
        self._orders.delete(order_id)

    def calculate(self, order: Order) -> CostReport:
        """Returns the report_cost result for this order.

        :param order:

        :return: the CostReport of this calculation.
        """
        priced, sheets = _calculation_sheets(order)
        return self._administrator.report_cost(priced, sheets)

    def accept(self, order: Order) -> tuple[OrderId, CostReport]:
        """Saves the order with status В работе and the calculation report.

        :param order:

        :raises OrderNotFound: if the given id does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved row and the report of this calculation.
        The saved order's status is IN_WORK,
        even if the passed order has another status. Calculation data
        and comment come from the passed order.
        The second element of the pair is the report of this calculation,
        not a report read from the database.
        """
        return self._keep(order, Status.IN_WORK)

    def delay(self, order: Order) -> tuple[OrderId, CostReport]:
        """Saves the order with status Отложен and the calculation report.

        :param order:

        :raises OrderNotFound: if the given id does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved row and the report of this calculation.
        The saved order's status is SAVED, even if the passed order has another status.
        Calculation data and comment come from the passed order.
        The second element of the pair is the report of this calculation,
        not a report read from the database.
        """
        return self._keep(order, Status.SAVED)

    def change_status(self, order_id: OrderId, status: Status) -> None:
        """Changes only the order status.

        :param order_id:
        :param status:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        current = self._orders.take(order_id)
        self._orders.save(replace(current, status=status))

    def _keep(
        self, order: Order, status: Status
    ) -> tuple[OrderId, CostReport]:
        priced, sheets = _calculation_sheets(order)
        report = self._administrator.report_cost(priced, sheets)
        order_id = self._orders.save_with_report(
            replace(order, status=status), report
        )
        return order_id, report


def _calculation_sheets(order: Order) -> tuple[Order, dict[int, Sheet]]:
    # Справочника ещё нет. Размер и ставка лежат на печати.
    # Пустой id подставляется только в копию для этого расчёта.
    sheets: dict[int, Sheet] = {}
    printings: list[Printing] = []
    used = {
        printing.specification.press_sheet
        for printing in order.printings
        if printing.specification.press_sheet is not None
    }
    next_id = 1
    for printing in order.printings:
        spec = printing.specification
        sheet_id = spec.press_sheet
        if sheet_id is None:
            while next_id in used:
                next_id += 1
            sheet_id = next_id
            used.add(sheet_id)
            next_id += 1
            printing = replace(
                printing,
                specification=replace(spec, press_sheet=sheet_id),
            )
        stored = printing.stored_press
        sheets[sheet_id] = Sheet(
            SheetFormat("", stored.height, stored.width),
            stored.density,
            stored.paper,
        )
        printings.append(printing)
    return replace(order, printings=tuple(printings)), sheets
