from backend.workplace.reports import DieCuttingReport


class DieCuttingWorkplace:
    def report(self, sheet_count: int) -> DieCuttingReport:
        """Возвращает число листов изделия для платы за высечку.

        Предусловие: sheet_count — число листов без приладки,
        уже посчитанное администратором.
        Результат: DieCuttingReport с тем же sheet_count.
        На ставку высечки число листов не умножается.
        Побочные эффекты: нет. Аргумент не меняется.
        """
        return DieCuttingReport(sheet_count=sheet_count)
