from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.cost_reporter.models.cost_report import CostReport
from backend.cost_reporter.models.edition import Edition
from backend.cost_reporter.models.production import Production


class CostReportHandler:
    """Обработчик бизнес-логики формирования отчёта по стоимости."""

    def take_report(self, edition: Edition, production: Production) -> CostReport:
        factory = CostReporterFactory(
            edition_data=edition,
            production_data=production,
        )
        reporter = factory.create_reporter()
        return reporter.get_report()
