export const VisibleFields = [
    {
        label: "Кол-во изделий (шт.)",
        path: "printings[0].edition.count",
        type: "number",
        valueParser: Number,
    },
    {
        label: "Плотность бумаги (гр./м²)",
        path: "printings[0].edition.density",
        type: "number",
        valueParser: Number,
    },
    {
        label: "Ширина изделия",
        path: "printings[0].edition.list_size.width",
        type: "number",
        valueParser: Number,
    },
    {
        label: "Высота изделия",
        path: "printings[0].edition.list_size.height",
        type: "number",
        valueParser: Number,
    },
    {
        label: "Цветность",
        path: "printings[0].edition.chroma",
        type: "select",
        valueParser: Number,
        options: [
        { value: 0, label: "0+0" },
        { value: 1, label: "1+0" },
        { value: 2, label: "1+1" },
        { value: 3, label: "4+0" },
        { value: 4, label: "4+1" },
        { value: 5, label: "4+4" },
        ],
    },
    {
        label: "Ламинация",
        path: "printings[0].edition.lamination",
        type: "select",
        valueParser: Number,
        options: [
        { value: 1, label: "Без ламинации" },
        { value: 2, label: "1+0" },
        { value: 3, label: "1+1" },
        ],
    },
    {
        label: "Высечка",
        path: "printings[0].edition.die_cutting",
        type: "select",
        valueParser: (v) => v === "true",
        options: [
        { value: false, label: "Нет" },
        { value: true, label: "Да" },
        ],
    },
];

export const Hiddenfields = [
    {
      label: "Наценка (%)",
      path: "economy.markup",
      step: 0.01,
    },
    {
      label: "Вылеты (мм)",
      path: "printings[0].edition.list_size.bleeds",
    },
    {
      label: "Налоговая ставка",
      path: "economy.tax_rate",
      step: 0.01,
    },
    {
      label: "Стоимость чёрной краски (руб./лист)",
      path: "printings[0].production.black_ink_cost",
      step: 0.01,
    },
    {
      label: "Стоимость всех красок (руб./лист)",
      path: "printings[0].production.ink_cost",
      step: 0.01,
    },
    {
      label: "Цена ламинации (руб./лист)",
      path: "printings[0].production.lamination_cost",
      step: 0.01,
    },
    {
      label: "Стоимость высечки (руб./лист)",
      path: "printings[0].production.die_cutting_cost",
      step: 0.01,
    },
    {
      label: "Стоимость бумаги (руб./кг)",
      path: "printings[0].production.paper_cost",
      step: 0.01,
    },
    {
      label: "Высота печатного листа (мм)",
      path: "printings[0].production.press_sheet.height",
    },
    {
      label: "Ширина печатного листа (мм)",
      path: "printings[0].production.press_sheet.width",
    },
    {
      label: "Поля печатного листа (мм)",
      path: "printings[0].production.press_sheet.spacing",
    },
    {
      label: "Высота стопки резака (мм)",
      path: "printings[0].production.cutter.stack_height",
    },
    {
      label: "Листы на приладку (шт)",
      path: "printings[0].production.sheet_by_fitting",
    },
    {
      label: "Цена 1 реза (руб.)",
      path: "printings[0].production.cutting_cost",
      step: 0.01,
    },
    {
      label: "Зарплата печатнику за 1 лист (руб.)",
      path: "printings[0].production.printer_salary",
      step: 0.01,
    },
];
