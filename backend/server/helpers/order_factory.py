from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.models import Order, Status
from backend.server.models.order_payload import OrderPayload


class OrderFactoryService:
    """Создание заказов с различными статусами и отчётами по себестоимости."""

    async def create_order(self, payload: OrderPayload, status: Status) -> Order:
        reporter = CostReporterFactory(
            edition_data=payload.edition,
            production_data=payload.production
        ).create_reporter()
        cost_report = reporter.get_report()

        return Order(
            status=status,
            comment=payload.comment,
            cost_report=cost_report,
            edition=payload.edition,
            production=payload.production,
            markup=getattr(payload.production, "markup", None),
            paper_cost=getattr(payload.production, "paper_cost", None)
        )