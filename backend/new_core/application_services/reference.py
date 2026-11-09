"""Use cases that list reference orders and store new references."""

from __future__ import annotations

from backend.new_core.order.order import Order
from backend.new_core.order.repository import OrderRepository
from backend.new_core.reference.reference import Reference
from backend.new_core.reference.repository import ReferenceRepository


class ReferenceOrderService:
    """Loads exemplar orders behind references and saves new reference rows."""

    def __init__(
        self,
        references: ReferenceRepository,
        orders: OrderRepository,
    ) -> None:
        """Remembers the reference catalog and order store.

        :param references:
        :param orders:
        """
        self._references = references
        self._orders = orders

    def references(self) -> tuple[Reference, ...]:
        """Returns every stored reference.

        :return: the rows from :meth:`ReferenceRepository.take_all`.
        """
        return self._references.take_all()

    def save(self, reference: Reference) -> None:
        """Stores a reference after the linked order exists.

        :param reference:

        :raises OrderNotFound: if the linked order id is missing.

        :return: nothing.
        """
        self._orders.take(reference.order_id)
        self._references.save(reference)

    def reference_orders(self) -> tuple[Order, ...]:
        """Loads the order for each stored reference.

        :raises OrderNotFound: if any linked order id is missing.

        :return: orders in the same order as :meth:`references`.
        """
        return tuple(
            self._orders.take(reference.order_id)
            for reference in self._references.take_all()
        )
