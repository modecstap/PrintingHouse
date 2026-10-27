from typing import Literal, Protocol

from backend.workplace.cost_order import Order
from backend.workplace.reports import CostReport

OrderId = int

StoreOperation = Literal[
    "save",
    "take",
    "attach",
    "reports",
    "delete",
    "take_all",
    "save_with_report",
]


class OrderNotFound(Exception):
    def __init__(
        self,
        operation: StoreOperation,
        order_id: OrderId,
    ) -> None:
        """Сообщает, что заказа с этим id нет.

        Результат: текст «{operation}: заказа нет, id={order_id}».
        """
        super().__init__(f"{operation}: заказа нет, id={order_id}")


class OrderStoreUnavailable(Exception):
    def __init__(
        self,
        operation: StoreOperation,
        order_id: OrderId | None,
    ) -> None:
        """Сообщает, что нет соединения с базой.

        Предусловия: order_id может быть None, если обрыв случился
        при вставке нового заказа.
        Результат: текст «{operation}: нет соединения с базой,
        id={order_id}». В тексте нет сообщения драйвера, адреса
        базы и пароля.
        """
        super().__init__(
            f"{operation}: нет соединения с базой, id={order_id}"
        )


class WorkplaceOrderRepository(Protocol):
    def save(self, order: Order) -> OrderId:
        """Сохраняет данные расчёта, comment и status заказа.

        Результат: id сохранённого заказа. При пустом id его назначает
        база, и он известен только из возврата. При существующем id
        возвращается тот же id.
        Побочные эффекты: пустой id вставляет строку и не пишет
        CostReport. Существующий id заменяет данные расчёта, comment
        и status. Уже прикреплённые отчёты не удаляются и не меняют
        порядок. Переданный Order не меняется. Неудачное сохранение
        оставляет уже сохранённые заказы и отчёты как были.
        Ошибки: OrderNotFound, если заданный id без строки в базе,
        база не меняется. OrderStoreUnavailable, если нет соединения
        с базой.
        """
        ...

    def take(self, order_id: OrderId) -> Order:
        """Возвращает весь заказ с этим id, без списка CostReport.

        Результат: заказ с данными расчёта, comment и status.
        Ошибки: OrderNotFound, если строки нет.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        ...

    def attach(self, report: CostReport, order_id: OrderId) -> None:
        """Дописывает один отчёт в конец списка отчётов заказа.

        Результат: ничего не возвращает.
        Побочные эффекты: число PrintingCost с числом печатей
        не сверяется. Неудачное прикрепление оставляет уже
        сохранённые заказы и отчёты как были.
        Ошибки: OrderNotFound, если заказа нет, отчёт не пишется.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        ...

    def reports(self, order_id: OrderId) -> list[CostReport]:
        """Возвращает прикреплённые отчёты заказа.

        Результат: пустой список, если attach ещё не было.
        Иначе отчёты в порядке успешных attach, с самого раннего.
        Ошибки: OrderNotFound, если заказа нет.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        ...

    def take_all(self) -> list[Order]:
        """Возвращает все строки workplace_order, без CostReport.

        Результат: каждая строка один раз, по убыванию id.
        Строк нет: пустой список. Заказы таблицы order не читаются.
        Ошибки: OrderStoreUnavailable, если нет соединения с базой.
        OrderNotFound не бросает.
        """
        ...

    def delete(self, order_id: OrderId) -> None:
        """Удаляет этот заказ.

        Результат: ничего не возвращает.
        Побочные эффекты: строки расчёта и отчёты уходят каскадом
        базы.
        Ошибки: OrderNotFound, если заказа нет, база не меняется.
        OrderStoreUnavailable, если нет соединения с базой.
        """
        ...

    def save_with_report(
        self, order: Order, report: CostReport
    ) -> OrderId:
        """Сохраняет заказ и дописывает отчёт в одной транзакции.

        Результат: id сохранённого заказа. Пустой id вставляет
        заказ, и id назначает база. Существующий id обновляет
        эту строку и возвращается тем же.
        Побочные эффекты: уже прикреплённые отчёты остаются,
        новый становится последним. Переданный Order не меняется.
        Любая ошибка внутри транзакции откатывает и заказ, и отчёт
        этого вызова.
        Ошибки: OrderNotFound, если заданный id без строки:
        новая строка не появляется, отчёт не пишется. Текст
        собирает save. OrderStoreUnavailable, если нет соединения
        с базой.
        """
        ...
