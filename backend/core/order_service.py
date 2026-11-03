from dataclasses import replace

from backend.core.administrator import Administrator
from backend.core.order import (
    Order,
    Status,
    empty_reference_order,
)
from backend.core.order_repository import (
    OrderId,
    WorkplaceOrderRepository,
)
from backend.core.reports import CostReport
from backend.core.sheet.repository import (
    SheetIdEmpty,
    SheetRepository,
)
from backend.core.sheet.sheet import Sheet


class WorkplaceOrderService:
    def __init__(
        self,
        orders: WorkplaceOrderRepository,
        sheets: SheetRepository,
        administrator: Administrator,
    ) -> None:
        """Remembers the order repository, the sheet repository, and the administrator.

        :param orders:
        :param sheets:
        :param administrator:
        """
        self._orders = orders
        self._sheets = sheets
        self._administrator = administrator

    def save(self, order: Order) -> OrderId:
        """Writes the calculation data, comment, and the passed status.

        :param order:

        :raises SheetIdEmpty: if a printing has no sheet id.
        The order is not written.
        :raises SheetNotFound: if a printing names a sheet id that has no row.
        The order is not written.
        :raises SheetStoreUnavailable: if there is no connection to the database.
        The order is not written.
        :raises OrderNotFound: if the given id has no row.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved row. An empty id is assigned by the database.
        An existing id is returned unchanged.
        """
        self._load_sheets(order, "save")
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

        :raises SheetIdEmpty: if a printing has no sheet id.
        The reference is not replaced.
        :raises SheetNotFound: if a printing names a sheet id that has no row.
        The reference is not replaced.
        :raises SheetStoreUnavailable: if there is no connection to the database.
        The reference is not replaced.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        self._load_sheets(order, "set_reference")
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

        :raises SheetIdEmpty: if a printing has no sheet id.
        There is no report and the order is not written.
        :raises SheetNotFound: if a printing names a sheet id that has no row.
        There is no report and the order is not written.
        :raises SheetStoreUnavailable: if there is no connection to the database.
        There is no report and the order is not written.

        :return: the CostReport of this calculation. The order is not written.
        Each printing is priced from the loaded sheet.
        """
        sheets = self._load_sheets(order, "calculate")
        return self._administrator.report_cost(order, sheets)

    def accept(self, order: Order) -> tuple[OrderId, CostReport]:
        """Saves the order with status В работе and the calculation report.

        :param order:

        :raises SheetIdEmpty: if a printing has no sheet id.
        The order is not written and there is no report.
        :raises SheetNotFound: if a printing names a sheet id that has no row.
        The order is not written and there is no report.
        :raises SheetStoreUnavailable: if there is no connection to the database.
        The order is not written and there is no report.
        :raises OrderNotFound: if the given id does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved row and the report of this calculation.
        The saved order's status is IN_WORK,
        even if the passed order has another status. Calculation data
        and comment come from the passed order.
        The second element of the pair is the report of this calculation,
        not a report read from the database.
        The sheet check runs before the calculation and before the save.
        """
        return self._keep(order, Status.IN_WORK, "accept")

    def delay(self, order: Order) -> tuple[OrderId, CostReport]:
        """Saves the order with status Отложен and the calculation report.

        :param order:

        :raises SheetIdEmpty: if a printing has no sheet id.
        The order is not written and there is no report.
        :raises SheetNotFound: if a printing names a sheet id that has no row.
        The order is not written and there is no report.
        :raises SheetStoreUnavailable: if there is no connection to the database.
        The order is not written and there is no report.
        :raises OrderNotFound: if the given id does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: the id of the saved row and the report of this calculation.
        The saved order's status is SAVED, even if the passed order has another status.
        Calculation data and comment come from the passed order.
        The second element of the pair is the report of this calculation,
        not a report read from the database.
        The sheet check runs before the calculation and before the save.
        """
        return self._keep(order, Status.SAVED, "delay")

    def change_status(self, order_id: OrderId, status: Status) -> None:
        """Changes only the order status.

        :param order_id:
        :param status:

        :raises OrderNotFound: if the order does not exist.
        :raises OrderStoreUnavailable: if there is no connection to the database.

        :return: returns nothing.
        """
        # Уже сохранённый заказ. Пустой лист здесь не проверяется:
        # метод меняет только статус.
        current = self._orders.take(order_id)
        self._orders.save(replace(current, status=status))

    def _keep(
        self, order: Order, status: Status, operation: str
    ) -> tuple[OrderId, CostReport]:
        sheets = self._load_sheets(order, operation)
        report = self._administrator.report_cost(order, sheets)
        order_id = self._orders.save_with_report(
            replace(order, status=status), report
        )
        return order_id, report

    def _load_sheets(self, order: Order, operation: str) -> dict[int, Sheet]:
        sheets: dict[int, Sheet] = {}
        for printing in order.printings:
            sheet_id = printing.specification.press_sheet
            if sheet_id is None:
                raise SheetIdEmpty(operation)
            if sheet_id not in sheets:
                sheets[sheet_id] = self._sheets.take(sheet_id)
        return sheets
