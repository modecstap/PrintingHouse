import { formatPrice } from "./formatters";

const PRINTING_COST_HIDDEN_TEMPLATE = (index) => [
  {
    label: `Цена изделия`,
    value: (r) => formatPrice(r.printing_cost_reports[index].unit_cost),
  },
  {
    label: `Цена тиража`,
    value: (r) =>
      formatPrice(r.printing_cost_reports[index].edition_cost),
  },
  {
    label: `Кол-во изделий на листе`,
    value: (r) => r.printing_cost_reports[index].items_per_sheet,
  },
  {
    label: `Кол-во печатных листов`,
    value: (r) => r.printing_cost_reports[index].sheet_count,
  },
  {
    label: `Себестоимость изделия`,
    value: (r) => formatPrice(r.printing_cost_reports[index].unit_cost_price),
  },
  {
    label: `Прибыль до налога`,
    value: (r) =>
      formatPrice(r.printing_cost_reports[index].profit_before_tax),
  },
  {
    label: `Прибыль после налога`,
    value: (r) =>
      formatPrice(r.printing_cost_reports[index].profit_after_tax),
  },
];


export const buildHiddenRows = (data) => {
  if (!Array.isArray(data.printing_cost_reports)) return [];

  return data.printing_cost_reports.flatMap((_, index) => [
    {
      label: `Печать №${index + 1}`,
      isGroup: true,
    },
    ...PRINTING_COST_HIDDEN_TEMPLATE(index),
  ]);
};