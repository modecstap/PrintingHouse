from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.models import Edition
from backend.models import Production
from backend.models.cost_report import CostReport


class CostReportHandler:
    """Обработчик бизнес-логики формирования отчёта по стоимости."""

    def take_report(self, edition: Edition, production: Production) -> CostReport:
        factory = CostReporterFactory(
            edition_data=edition,
            production_data=production,
        )
        reporter = factory.create_reporter()
        return reporter.get_report()
