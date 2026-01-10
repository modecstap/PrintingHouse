from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.models import Edition, Economy
from backend.models import Production
from backend.models.printing_cost_report import PrintingCostReport


class CostReportHandler:
    """Обработчик бизнес-логики формирования отчёта по стоимости."""

    def take_report(self, edition: Edition, production: Production, economy: Economy) -> PrintingCostReport:
        factory = CostReporterFactory(edition=edition, production=production, economy=economy)
        reporter = factory.create_reporter()
        return reporter.get_report()
