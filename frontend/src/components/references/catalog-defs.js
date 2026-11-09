import { formatMoney } from "../../lib/format-money";
import {
  toCutterList,
  toFilmList,
  toJsonInt,
  toLaminatorList,
  toOperatorList,
  toPrinterList,
  toSheetList,
} from "./models/catalog";

const MONEY = { inputMode: "decimal" };
const INT = { inputType: "number" };

function staffCatalog({ key, title, listPath }) {
  const itemPath = (id) => `${listPath}/${id}`;
  return {
    key,
    title,
    listPath,
    itemPath,
    parseList: toOperatorList,
    clientId: true,
    canReplace: false,
    columns: [
      { header: "Номер", render: (row) => row.id },
      {
        header: "Зарплата",
        render: (row) => formatMoney(row.salary_by_operation),
      },
    ],
    fields: [
      { name: "id", label: "Номер", ...INT },
      { name: "salary_by_operation", label: "Зарплата", ...MONEY },
    ],
    emptyForm: { id: "", salary_by_operation: "" },
    formFromRow: undefined,
    toPayload(form) {
      return {
        id: toJsonInt(form.id),
        salary_by_operation: form.salary_by_operation.trim(),
      };
    },
  };
}

const PRINTERS = {
  key: "printers",
  title: "Принтеры",
  listPath: "/api/equipment/printers",
  itemPath(id) {
    return `/api/equipment/printers/${id}`;
  },
  parseList: toPrinterList,
  clientId: true,
  canReplace: false,
  columns: [
    { header: "Номер", render: (row) => row.id },
    { header: "Запуск", render: (row) => formatMoney(row.startup) },
    { header: "C", render: (row) => formatMoney(row.cyan) },
    { header: "M", render: (row) => formatMoney(row.magenta) },
    { header: "Y", render: (row) => formatMoney(row.yellow) },
    { header: "K", render: (row) => formatMoney(row.black) },
  ],
  fields: [
    { name: "id", label: "Номер", ...INT },
    { name: "startup", label: "Запуск", ...MONEY },
    { name: "cyan", label: "C", ...MONEY },
    { name: "magenta", label: "M", ...MONEY },
    { name: "yellow", label: "Y", ...MONEY },
    { name: "black", label: "K", ...MONEY },
  ],
  emptyForm: {
    id: "",
    startup: "",
    cyan: "",
    magenta: "",
    yellow: "",
    black: "",
  },
  formFromRow: undefined,
  toPayload(form) {
    return {
      id: toJsonInt(form.id),
      startup: form.startup.trim(),
      cyan: form.cyan.trim(),
      magenta: form.magenta.trim(),
      yellow: form.yellow.trim(),
      black: form.black.trim(),
    };
  },
};

const LAMINATORS = {
  key: "laminators",
  title: "Ламинаторы",
  listPath: "/api/equipment/laminators",
  itemPath(id) {
    return `/api/equipment/laminators/${id}`;
  },
  parseList: toLaminatorList,
  clientId: true,
  canReplace: false,
  columns: [
    { header: "Номер", render: (row) => row.id },
    { header: "Запуск", render: (row) => formatMoney(row.startup) },
  ],
  fields: [
    { name: "id", label: "Номер", ...INT },
    { name: "startup", label: "Запуск", ...MONEY },
  ],
  emptyForm: { id: "", startup: "" },
  formFromRow: undefined,
  toPayload(form) {
    return {
      id: toJsonInt(form.id),
      startup: form.startup.trim(),
    };
  },
};

const CUTTERS = {
  key: "cutters",
  title: "Резаки",
  listPath: "/api/equipment/cutters",
  itemPath(id) {
    return `/api/equipment/cutters/${id}`;
  },
  parseList: toCutterList,
  clientId: true,
  canReplace: false,
  columns: [
    { header: "Номер", render: (row) => row.id },
    { header: "Макс. стопа", render: (row) => row.max_stack },
  ],
  fields: [
    { name: "id", label: "Номер", ...INT },
    { name: "max_stack", label: "Макс. стопа", ...INT },
  ],
  emptyForm: { id: "", max_stack: "" },
  formFromRow: undefined,
  toPayload(form) {
    return {
      id: toJsonInt(form.id),
      max_stack: toJsonInt(form.max_stack),
    };
  },
};

const SHEETS = {
  key: "sheets",
  title: "Листы",
  listPath: "/api/materials/sheets",
  itemPath(id) {
    return `/api/materials/sheets/${id}`;
  },
  parseList: toSheetList,
  clientId: false,
  canReplace: true,
  columns: [
    { header: "Номер", render: (row) => row.id },
    { header: "Название", render: (row) => row.paper.name },
    { header: "Плотность", render: (row) => row.paper.density },
    { header: "Толщина (мм)", render: (row) => row.paper.thickness },
    {
      header: "Цена за кг",
      render: (row) => formatMoney(row.paper.price_per_kilo),
    },
    { header: "Название", render: (row) => row.format.name },
    { header: "Ширина (мм)", render: (row) => row.format.width },
    { header: "Высота (мм)", render: (row) => row.format.height },
  ],
  fields: [
    {
      legend: "Бумага",
      fields: [
        { name: "paper_name", label: "Название" },
        { name: "paper_density", label: "Плотность", ...INT },
        { name: "paper_thickness", label: "Толщина (мм)", ...INT },
        { name: "paper_price_per_kilo", label: "Цена за кг", ...MONEY },
      ],
    },
    {
      legend: "Формат листа",
      fields: [
        { name: "format_name", label: "Название" },
        { name: "format_width", label: "Ширина (мм)", ...INT },
        { name: "format_height", label: "Высота (мм)", ...INT },
      ],
    },
  ],
  emptyForm: {
    paper_name: "",
    paper_density: "",
    paper_thickness: "",
    paper_price_per_kilo: "",
    format_name: "",
    format_width: "",
    format_height: "",
  },
  formFromRow(row) {
    return {
      paper_name: row.paper.name,
      paper_density: String(row.paper.density),
      paper_thickness: String(row.paper.thickness),
      paper_price_per_kilo: row.paper.price_per_kilo,
      format_name: row.format.name,
      format_width: String(row.format.width),
      format_height: String(row.format.height),
    };
  },
  toPayload(form) {
    return {
      paper: {
        name: form.paper_name.trim(),
        density: toJsonInt(form.paper_density),
        thickness: toJsonInt(form.paper_thickness),
        price_per_kilo: form.paper_price_per_kilo.trim(),
      },
      format: {
        name: form.format_name.trim(),
        height: toJsonInt(form.format_height),
        width: toJsonInt(form.format_width),
      },
    };
  },
};

const FILMS = {
  key: "films",
  title: "Плёнки",
  listPath: "/api/materials/films",
  itemPath(id) {
    return `/api/materials/films/${id}`;
  },
  parseList: toFilmList,
  clientId: false,
  canReplace: true,
  columns: [
    { header: "Номер", render: (row) => row.id },
    { header: "Название", render: (row) => row.name },
    { header: "Цена", render: (row) => formatMoney(row.price) },
    { header: "Плотность", render: (row) => row.density },
  ],
  fields: [
    { name: "name", label: "Название" },
    { name: "price", label: "Цена", ...MONEY },
    { name: "density", label: "Плотность", ...INT },
  ],
  emptyForm: { name: "", price: "", density: "" },
  formFromRow(row) {
    return {
      name: row.name,
      price: row.price,
      density: String(row.density),
    };
  },
  toPayload(form) {
    return {
      name: form.name.trim(),
      price: form.price.trim(),
      density: toJsonInt(form.density),
    };
  },
};

export const EQUIPMENT_CATALOGS = [PRINTERS, LAMINATORS, CUTTERS];

export const STAFF_CATALOGS = [
  staffCatalog({
    key: "press-operators",
    title: "Печатники",
    listPath: "/api/staff/press-operators",
  }),
  staffCatalog({
    key: "laminator-operators",
    title: "Операторы ламинации",
    listPath: "/api/staff/laminator-operators",
  }),
  staffCatalog({
    key: "cutter-operators",
    title: "Операторы реза",
    listPath: "/api/staff/cutter-operators",
  }),
  staffCatalog({
    key: "die-cut-operators",
    title: "Операторы высечки",
    listPath: "/api/staff/die-cut-operators",
  }),
];

export const MATERIAL_CATALOGS = [SHEETS, FILMS];
