from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ReportPeriod(BaseModel):
    start_date: datetime = Field(description="Начало периода")
    end_date: datetime = Field(description="Конец периода")
    label: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def convert_to_utc(cls, values: dict) -> dict:
        """
        Приводим все даты к UTC-aware datetime.
        """
        for field in ("start_date", "end_date"):
            if field in values and isinstance(values[field], datetime):
                dt = values[field]

                # если naive → считаем что это UTC
                if dt.tzinfo is None:
                    values[field] = dt.replace(tzinfo=timezone.utc)
                else:
                    values[field] = dt.astimezone(timezone.utc)

        return values

    @model_validator(mode="after")
    def build_default_label(self) -> "ReportPeriod":
        if self.start_date > self.end_date:
            raise ValueError("Дата начала периода больше даты окончания")

        if self.label is None:
            self.label = self._format_period_label()

        return self
    def _format_period_label(self) -> str:
        """
        Create readable period label.

        :return: formatted label
        """
        start_value = self._format_date(self.start_date)
        end_value = self._format_date(self.end_date)
        return f"{start_value} - {end_value}"

    def _format_date(self, value: datetime) -> str:
        """
        Convert datetime to russian readable date.

        :param value: source datetime

        :return: formatted date
        """
        month_names = {
            1: "Января",
            2: "Февраля",
            3: "Марта",
            4: "Апреля",
            5: "Мая",
            6: "Июня",
            7: "Июля",
            8: "Августа",
            9: "Сентября",
            10: "Октября",
            11: "Ноября",
            12: "Декабря",
        }
        month_name = month_names[value.month]
        return f"{value.day} {month_name} {value.year}"


class RevenueMetrics(BaseModel):
    total_revenue: Decimal = Field(description="Общая выручка")
    total_cost_price: Decimal = Field(description="Общая себестоимость")
    total_profit_before_tax: Decimal = Field(description="Общая прибыль до налога")
    total_profit_after_tax: Decimal = Field(description="Общая прибыль после налога")

    average_order_value: Decimal = Field(description="Средний чек")
    average_profit_per_order: Decimal = Field(description="Средняя прибыль на заказ")


class MarginMetrics(BaseModel):
    gross_margin_ratio: Decimal = Field(description="Валовая маржа (%)")
    net_margin_ratio: Decimal = Field(description="Чистая маржа (%)")
    average_markup: Decimal = Field(description="Средняя наценка (%)")


class UnitEconomics(BaseModel):
    average_unit_cost_price: Decimal = Field(description="Средняя себестоимость изделия")
    average_unit_price: Decimal = Field(description="Средняя цена изделия")
    average_profit_per_unit: Decimal = Field(description="Средняя прибыль на изделие")


class OrdersStats(BaseModel):
    total_orders: int = Field(description="Количество заказов")
    profitable_orders: int = Field(description="Прибыльные заказы")
    unprofitable_orders: int = Field(description="Убыточные заказы")


class TaxMetrics(BaseModel):
    total_tax: Decimal = Field(description="Общая сумма налогов")
    effective_tax_rate: Decimal = Field(description="Эффективная налоговая ставка")


class FinancialReport(BaseModel):
    period: ReportPeriod

    revenue: RevenueMetrics
    margin: MarginMetrics
    unit_economics: UnitEconomics

    orders: OrdersStats
    tax: TaxMetrics

    created_at: datetime = Field(default_factory=datetime.now)
