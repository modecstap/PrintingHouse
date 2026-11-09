"""SQL implementation of ``PrintRunRepository``."""

from __future__ import annotations

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun, PrintRunID
from backend.storage.part.mapping import part_row_to_part, persist_part
from backend.storage.part.tables import PartRow
from backend.storage.print_run.tables import PrintRunRow


class SqlPrintRunRepository:
    """Persists print runs per order in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take_all_for_order(self, order_id: OrderID) -> tuple[PrintRun, ...]:
        """Returns every print run linked to the order.

        :param order_id:

        :return: runs in repository order. No runs: an empty tuple.
        """
        stmt = (
            select(PrintRunRow)
            .where(PrintRunRow.order_id == order_id.value)
            .order_by(PrintRunRow.position)
        )
        rows = self._session.execute(stmt).scalars().all()
        runs: list[PrintRun] = []
        for row in rows:
            block = part_row_to_part(self._session, row.part_id)
            runs.append(
                PrintRun(
                    id=PrintRunID(row.id),
                    for_order=order_id,
                    block=block,
                    required_count=row.required_count,
                ),
            )
        return tuple(runs)

    def generate_id(self, order_id: OrderID) -> PrintRunID:
        """Returns the next print run id for this order.

        :param order_id: scopes the id sequence.

        :return: a new print run id. It may already be stored for this order.
        """
        engine = self._session.get_bind()
        with engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            next_value = conn.execute(
                text(
                    """
                    INSERT INTO print_run_id_counters (order_id, next_value)
                    VALUES (:order_id, 1)
                    ON CONFLICT (order_id) DO UPDATE
                    SET next_value = print_run_id_counters.next_value + 1
                    RETURNING next_value
                    """,
                ),
                {"order_id": order_id.value},
            ).scalar_one()
        return PrintRunID(int(next_value) - 1)

    def save_all_for_order(
        self,
        order_id: OrderID,
        runs: tuple[PrintRun, ...],
    ) -> None:
        """Replaces all print runs linked to the order.

        :param order_id:
        :param runs:

        :raises ValueError: if a run's for_order is not order_id.

        :return: nothing.
        """
        for run in runs:
            if run.for_order != order_id:
                raise ValueError(
                    f"run {run.id.value} for_order {run.for_order.value} "
                    f"!= {order_id.value}",
                )

        part_ids = self._session.execute(
            select(PrintRunRow.part_id).where(
                PrintRunRow.order_id == order_id.value,
            ),
        ).scalars().all()

        self._session.execute(
            delete(PrintRunRow).where(PrintRunRow.order_id == order_id.value),
        )
        for part_id in part_ids:
            self._session.execute(delete(PartRow).where(PartRow.id == part_id))

        for position, run in enumerate(runs):
            part_id = persist_part(self._session, run.block)
            self._session.add(
                PrintRunRow(
                    order_id=order_id.value,
                    id=run.id.value,
                    position=position,
                    part_id=part_id,
                    required_count=run.required_count,
                ),
            )
