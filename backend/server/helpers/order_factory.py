from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.cost_reporter.order_cost_reporter import OrderCostReporter
from backend.models import Order, Status, PrintingCostReport


class OrderFactoryService:
    """Создание заказов с различными статусами и отчётами по себестоимости."""

    def fit_order(self, order: Order, status: Status) -> Order:
        printing_reports: list[PrintingCostReport] = []

        for printing in order.printings:
            printing.edition.count *= order.unit_count
            reporter = CostReporterFactory(printing.edition, printing.production, order.economy).create_reporter()
            printing_reports.append(reporter.get_report())
            printing.cost_report = reporter.get_report()

        order_cost_report = OrderCostReporter(
            unit_count=order.unit_count,
            printing_reports=printing_reports,
            operations=order.operations,
            economy=order.economy
        ).get_report()

        order.status = status
        order.cost_report = order_cost_report

        return order
