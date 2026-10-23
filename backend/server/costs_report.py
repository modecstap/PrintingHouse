from fastapi import APIRouter, Depends

from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.models import Economy, Edition, Production
from backend.models.printing_cost_report import PrintingCostReport
from backend.server.dependencies import get_current_user_with_full_permission


router = APIRouter(prefix="/api/printing/costs_report", tags=["costs_report"])


@router.post(
    "",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def build_printing_cost_report(
    edition: Edition,
    production: Production,
    economy: Economy,
) -> PrintingCostReport:
    """Считает отчёт стоимости печати по edition, production и economy.

    Результат: PrintingCostReport. Ничего не сохраняется.
    """
    reporter = CostReporterFactory(
        edition=edition,
        production=production,
        economy=economy,
    ).create_reporter()
    return reporter.get_report()
