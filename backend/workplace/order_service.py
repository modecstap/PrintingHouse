from dataclasses import replace

from backend.workplace.administrator import Administrator
from backend.workplace.cost_order import (
    Order,
    Status,
    empty_reference_order,
)
from backend.workplace.order_repository import (
    OrderId,
    WorkplaceOrderRepository,
)
from backend.workplace.reports import CostReport


class WorkplaceOrderService:
    def __init__(
        self,
        orders: WorkplaceOrderRepository,
        administrator: Administrator,
    ) -> None:
        """Запоминает репозиторий заказов и администратора.

        Побочные эффекты: Engine не создаёт, переменные окружения
        не читает, репозиторий не конструирует.
        """
        self._orders = orders
        self._administrator = administrator

    def save(self, order: Order) -> OrderId:
        """Пишет данные расчёта, comment и переданный статус.

        Результат: id сохранённой строки. Пустой id вставляет заказ,
        ставит дату процесса, и id назначает база. Существующий id
        обновляет ту же строку, дату не меняет и возвращается тем же.
        Дата аргумента Order не читается.
        Побочные эффекты: CostReport не пишет. Расчёт не вызывает.
        Переданный Order не меняется. Чужой id новую строку
        не создаёт.
        Ошибки: OrderNotFound, если заданный id без строки.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        return self._orders.save(order)

    def take(self, order_id: OrderId) -> Order:
        """Возвращает один заказ без списка CostReport.

        Результат: заказ с данными расчёта, comment, status и датой
        вставки.
        Ошибки: OrderNotFound, если строки нет.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        return self._orders.take(order_id)

    def take_all(self) -> list[Order]:
        """Возвращает каждый заказ workplace_order один раз.

        Результат: заказы по убыванию id, без отчётов.
        Строк нет: пустой список.
        Ошибки: OrderStoreUnavailable, если нет соединения с базой.
        OrderNotFound не бросает.
        """
        return self._orders.take_all()

    def reference(self) -> Order:
        """Возвращает справочник или нулевой заказ.

        Результат: строка справочника, если она есть.
        Строки нет: заказ empty_reference_order.
        Побочные эффекты: базу не меняет.
        Ошибки: OrderStoreUnavailable, если нет соединения
        с базой. OrderNotFound не бросает.
        """
        stored = self._orders.reference()
        if stored is None:
            return empty_reference_order()
        return stored

    def set_reference(self, order: Order) -> None:
        """Заменяет справочник этим заказом.

        Предусловия: ставку уже проверил вызывающий.
        Результат: ничего не возвращает.
        Побочные эффекты: вызывает только set_reference.
        save не вызывается. id заменяется на None и не
        выбирает запись. Переданный Order не меняется.
        Строка workplace_order не появляется.
        Ошибки: OrderStoreUnavailable, если нет соединения
        с базой. OrderNotFound не бросает.
        """
        self._orders.set_reference(replace(order, id=None))

    def delete(self, order_id: OrderId) -> None:
        """Удаляет заказ, его расчёт и его отчёты.

        Результат: ничего не возвращает. После удаления take
        этот id не находит.
        Побочные эффекты: строка заказа и связанные строки уходят.
        Ошибки: OrderNotFound, если строки нет, база не меняется.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        self._orders.delete(order_id)

    def calculate(self, order: Order) -> CostReport:
        """Возвращает результат report_cost для этого заказа.

        Результат: CostReport этого расчёта.
        Побочные эффекты: в базу не пишет. Переданный Order
        не меняется.
        Ошибки: ошибка расчёта, включая деление на ноль,
        выходит к вызывающему. OrderStoreUnavailable из-за базы
        не бросает.
        """
        return self._administrator.report_cost(order)

    def accept(self, order: Order) -> tuple[OrderId, CostReport]:
        """Сохраняет заказ со статусом «В работе» и отчёт расчёта.

        Результат: id сохранённой строки и отчёт этого расчёта.
        Статус сохранённого заказа IN_WORK, даже если у переданного
        заказа статус другой. Данные расчёта и comment берутся
        из переданного заказа. Второй элемент пары — отчёт этого
        расчёта, не отчёт, прочитанный из базы.
        Побочные эффекты: сначала расчёт. После расчёта заказ
        и отчёт пишутся вместе. Прежние отчёты остаются, новый
        последний. Переданный Order не меняется.
        Ошибки: ошибка расчёта ничего не пишет. OrderNotFound,
        если заданного id нет: отчёт не пишется, новая строка
        не появляется. Неудачная запись не оставляет заказ этого
        вызова без отчёта этого расчёта и не меняет уже сохранённые
        заказы и отчёты. OrderStoreUnavailable, если нет соединения
        с базой.
        """
        return self._keep(order, Status.IN_WORK)

    def delay(self, order: Order) -> tuple[OrderId, CostReport]:
        """Сохраняет заказ со статусом «Отложен» и отчёт расчёта.

        Результат: id сохранённой строки и отчёт этого расчёта.
        Статус сохранённого заказа SAVED, даже если у переданного
        заказа статус другой. Данные расчёта и comment берутся
        из переданного заказа. Второй элемент пары — отчёт этого
        расчёта, не отчёт, прочитанный из базы.
        Побочные эффекты: сначала расчёт. После расчёта заказ
        и отчёт пишутся вместе. Прежние отчёты остаются, новый
        последний. Переданный Order не меняется.
        Ошибки: ошибка расчёта ничего не пишет. OrderNotFound,
        если заданного id нет: отчёт не пишется, новая строка
        не появляется. Неудачная запись не оставляет заказ этого
        вызова без отчёта этого расчёта и не меняет уже сохранённые
        заказы и отчёты. OrderStoreUnavailable, если нет соединения
        с базой.
        """
        return self._keep(order, Status.SAVED)

    def change_status(self, order_id: OrderId, status: Status) -> None:
        """Меняет только статус заказа.

        Результат: ничего не возвращает.
        Побочные эффекты: расчёт не выполняется. Данные расчёта,
        comment, дата вставки и отчёты остаются.
        Ошибки: OrderNotFound, если заказа нет.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        current = self._orders.take(order_id)
        self._orders.save(replace(current, status=status))

    def _keep(
        self, order: Order, status: Status
    ) -> tuple[OrderId, CostReport]:
        report = self._administrator.report_cost(order)
        order_id = self._orders.save_with_report(
            replace(order, status=status), report
        )
        return order_id, report
