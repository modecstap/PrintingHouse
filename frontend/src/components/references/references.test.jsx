import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { formatMoney } from "../../lib/format-money";
import References from "./references";

function jsonResponse(data, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  });
}

function empty204Response() {
  return Promise.resolve({
    ok: true,
    status: 204,
    json: async () => {
      throw new Error("no body");
    },
  });
}

const CATALOG_GET_PATHS = [
  "/api/equipment/printers",
  "/api/equipment/laminators",
  "/api/equipment/cutters",
  "/api/staff/press-operators",
  "/api/staff/laminator-operators",
  "/api/staff/cutter-operators",
  "/api/staff/die-cut-operators",
  "/api/materials/sheets",
  "/api/materials/films",
];

function catalogGets(body = []) {
  return (url) => {
    if (CATALOG_GET_PATHS.includes(url)) {
      return jsonResponse(body);
    }
    return null;
  };
}

function templateBlock() {
  return screen.getByLabelText("Имя:").parentElement.parentElement.parentElement
    .parentElement;
}

function templateTable() {
  return screen
    .getByRole("columnheader", { name: "Имя" })
    .closest("table");
}

describe("References", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  afterEach(() => {
    global.fetch = originalFetch;
    localStorage.clear();
  });

  function mockFetch(handler) {
    global.fetch = jest.fn((url, options) => {
      const catalog = catalogGets()(url);
      if (catalog) {
        return catalog;
      }
      return handler(url, options);
    });
  }

  it("should show name, description, and order id", async () => {
    mockFetch((url) => {
      if (url === "/api/references") {
        return jsonResponse([
          { name: "Шаблон", description: "Визитка", order_id: 3 },
        ]);
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    await waitFor(() => {
      expect(within(templateTable()).getByText("Шаблон")).toBeInTheDocument();
    });
    expect(within(templateTable()).getByText("Визитка")).toBeInTheDocument();
    expect(within(templateTable()).getByText("3")).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: "Имя" })
    ).toBeInTheDocument();
  });

  it("should clear the form and show the new row after save", async () => {
    let getCount = 0;
    mockFetch((url, options) => {
      if (url === "/api/references" && options?.method === "POST") {
        return empty204Response();
      }
      if (url === "/api/references") {
        getCount += 1;
        if (getCount === 1) {
          return jsonResponse([]);
        }
        return jsonResponse([
          { name: "Новый", description: "Описание", order_id: 5 },
        ]);
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    await waitFor(() => {
      expect(
        screen.getByRole("columnheader", { name: "Имя" })
      ).toBeInTheDocument();
    });

    await userEvent.type(screen.getByLabelText("Имя:"), "Новый");
    await userEvent.type(screen.getByLabelText("Описание:"), "Описание");
    await userEvent.type(screen.getByLabelText("Заказ №:"), "5");
    await userEvent.click(
      within(templateBlock()).getByRole("button", { name: "Сохранить" })
    );

    await waitFor(() => {
      expect(within(templateTable()).getByText("Новый")).toBeInTheDocument();
    });
    expect(screen.getByLabelText("Имя:")).toHaveValue("");
    expect(screen.getByLabelText("Описание:")).toHaveValue("");
    expect(screen.getByLabelText("Заказ №:")).toHaveValue(null);
  });

  it("should show the server detail and keep the row out when the order is missing", async () => {
    mockFetch((url, options) => {
      if (url === "/api/references" && options?.method === "POST") {
        return jsonResponse({ detail: "order missing" }, 404);
      }
      if (url === "/api/references") {
        return jsonResponse([]);
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    await waitFor(() => {
      expect(
        screen.getByRole("columnheader", { name: "Имя" })
      ).toBeInTheDocument();
    });

    await userEvent.type(screen.getByLabelText("Имя:"), "X");
    await userEvent.type(screen.getByLabelText("Описание:"), "Y");
    await userEvent.type(screen.getByLabelText("Заказ №:"), "99");
    await userEvent.click(
      within(templateBlock()).getByRole("button", { name: "Сохранить" })
    );

    await waitFor(() => {
      expect(
        within(templateBlock()).getByRole("alert")
      ).toHaveTextContent("order missing");
    });
    expect(screen.getByLabelText("Заказ №:")).toHaveValue(99);

    const tbody = templateTable().querySelector("tbody");
    expect(within(tbody).queryAllByRole("row")).toHaveLength(0);
  });

  it("should show catalog group headings and all nine catalog titles", async () => {
    mockFetch((url) => {
      if (url === "/api/references") {
        return jsonResponse([]);
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Оборудование" })).toBeInTheDocument();
    });
    expect(screen.getByRole("heading", { name: "Персонал" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Материалы" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Справочники" })).toBeInTheDocument();
    expect(screen.queryByText("Справочная система")).not.toBeInTheDocument();

    await waitFor(() => {
      expect(
        within(templateTable()).getByRole("columnheader", { name: "Описание" })
      ).toBeInTheDocument();
    });

    for (const title of [
      "Принтеры",
      "Ламинаторы",
      "Резаки",
      "Печатники",
      "Ламинация",
      "Рез",
      "Высечка",
      "Листы",
      "Плёнки",
    ]) {
      expect(screen.getByRole("heading", { name: title })).toBeInTheDocument();
    }

    expect(
      within(templateTable()).getByRole("columnheader", {
        name: "Заказ №",
      })
    ).toBeInTheDocument();
  });

  it("should create a printer and show 409 on duplicate id", async () => {
    let printerGets = 0;
    let postCount = 0;

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/references") {
        return jsonResponse([]);
      }
      if (url === "/api/equipment/printers" && options?.method === "POST") {
        postCount += 1;
        if (postCount === 1) {
          return empty204Response();
        }
        return jsonResponse({ detail: "printer exists" }, 409);
      }
      if (url === "/api/equipment/printers") {
        printerGets += 1;
        if (printerGets <= 1) {
          return jsonResponse([]);
        }
        return jsonResponse([
          {
            id: 7,
            startup: "100",
            cyan: "1.5",
            magenta: "2",
            yellow: "3",
            black: "4",
          },
        ]);
      }
      const catalog = catalogGets()(url);
      if (catalog) {
        return catalog;
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    const region = await screen.findByRole("region", { name: "Принтеры" });

    await userEvent.type(within(region).getByLabelText("Номер:"), "7");
    await userEvent.type(within(region).getByLabelText("Запуск:"), "100");
    await userEvent.type(within(region).getByLabelText("C:"), "1.5");
    await userEvent.type(within(region).getByLabelText("M:"), "2");
    await userEvent.type(within(region).getByLabelText("Y:"), "3");
    await userEvent.type(within(region).getByLabelText("K:"), "4");
    await userEvent.click(
      within(region).getByRole("button", { name: "Сохранить" })
    );

    await waitFor(() => {
      const postCall = global.fetch.mock.calls.find(
        ([u, o]) => u === "/api/equipment/printers" && o?.method === "POST"
      );
      expect(postCall).toBeDefined();
      expect(JSON.parse(postCall[1].body)).toEqual({
        id: 7,
        startup: "100",
        cyan: "1.5",
        magenta: "2",
        yellow: "3",
        black: "4",
      });
    });

    await waitFor(() => {
      expect(within(region).getByText("7")).toBeInTheDocument();
      expect(within(region).getByText(formatMoney("100"))).toBeInTheDocument();
    });

    await userEvent.clear(within(region).getByLabelText("Номер:"));
    await userEvent.type(within(region).getByLabelText("Номер:"), "7");
    await userEvent.click(
      within(region).getByRole("button", { name: "Сохранить" })
    );

    await waitFor(() => {
      expect(within(region).getByRole("alert")).toHaveTextContent(
        "printer exists"
      );
    });
    expect(within(region).getByLabelText("Номер:")).toHaveValue(7);
  });

  it("should create a sheet, replace a film, and cancel edit without PUT", async () => {
    let sheetGets = 0;

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/references") {
        return jsonResponse([]);
      }
      if (url === "/api/materials/sheets" && options?.method === "POST") {
        return jsonResponse({ id: 1 });
      }
      if (url === "/api/materials/sheets") {
        sheetGets += 1;
        if (sheetGets <= 1) {
          return jsonResponse([]);
        }
        return jsonResponse([
          {
            id: 9,
            paper: {
              name: "Офсет",
              density: 80,
              thickness: 1,
              price_per_kilo: "90",
            },
            format: { name: "SRA3", width: 320, height: 450 },
          },
        ]);
      }
      if (
        url === "/api/materials/films/2" &&
        options?.method === "PUT"
      ) {
        return empty204Response();
      }
      if (url === "/api/materials/films") {
        return jsonResponse([
          { id: 2, name: "Матовая", price: "30", density: 50 },
        ]);
      }
      const catalog = catalogGets()(url);
      if (catalog) {
        return catalog;
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    const sheets = await screen.findByRole("region", { name: "Листы" });
    const films = screen.getByRole("region", { name: "Плёнки" });

    const paperFieldset = within(sheets).getByRole("group", {
      name: "Бумага",
    });
    await userEvent.type(within(paperFieldset).getByLabelText("Название:"), "Офсет");
    await userEvent.type(within(paperFieldset).getByLabelText("Плотность:"), "80");
    await userEvent.type(within(paperFieldset).getByLabelText("Толщина (мм):"), "1");
    await userEvent.type(within(paperFieldset).getByLabelText("Цена за кг:"), "90");
    const formatFieldset = within(sheets).getByRole("group", {
      name: "Формат листа",
    });
    await userEvent.type(within(formatFieldset).getByLabelText("Название:"), "SRA3");
    await userEvent.type(within(formatFieldset).getByLabelText("Ширина (мм):"), "320");
    await userEvent.type(within(formatFieldset).getByLabelText("Высота (мм):"), "450");
    await userEvent.click(
      within(sheets).getByRole("button", { name: "Сохранить" })
    );

    await waitFor(() => {
      const postCall = global.fetch.mock.calls.find(
        ([u, o]) => u === "/api/materials/sheets" && o?.method === "POST"
      );
      const body = JSON.parse(postCall[1].body);
      expect(body).toEqual({
        paper: {
          name: "Офсет",
          density: 80,
          thickness: 1,
          price_per_kilo: "90",
        },
        format: { name: "SRA3", height: 450, width: 320 },
      });
      expect(body).not.toHaveProperty("id");
    });

    await waitFor(() => {
      expect(within(sheets).getByText("9")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(within(films).getByText("Матовая")).toBeInTheDocument();
    });

    await userEvent.click(within(films).getByRole("button", { name: "Изменить" }));
    await userEvent.clear(within(films).getByLabelText("Цена:"));
    await userEvent.type(within(films).getByLabelText("Цена:"), "35");
    await userEvent.click(
      within(films).getByRole("button", { name: "Сохранить" })
    );

    await waitFor(() => {
      expect(
        global.fetch.mock.calls.some(
          ([u, o]) => u === "/api/materials/films/2" && o?.method === "PUT"
        )
      ).toBe(true);
    });

    await userEvent.click(within(films).getByRole("button", { name: "Изменить" }));
    await userEvent.type(within(films).getByLabelText("Название:"), "X");
    await userEvent.click(within(films).getByRole("button", { name: "Отмена" }));

    expect(
      global.fetch.mock.calls.filter(
        ([u, o]) => u === "/api/materials/films/2" && o?.method === "PUT"
      )
    ).toHaveLength(1);
    expect(within(films).getByLabelText("Название:")).toHaveValue("");
  });

  it("should delete a cutter row and show load error only in that catalog", async () => {
    let cutterGets = 0;
    let printerGets = 0;

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/references") {
        return jsonResponse([]);
      }
      if (url === "/api/equipment/cutters/3" && options?.method === "DELETE") {
        return empty204Response();
      }
      if (url === "/api/equipment/cutters") {
        cutterGets += 1;
        if (cutterGets <= 1) {
          return jsonResponse([{ id: 3, max_stack: 100 }]);
        }
        return jsonResponse([]);
      }
      if (url === "/api/equipment/printers") {
        printerGets += 1;
        if (printerGets === 1) {
          return jsonResponse({ detail: "printers down" }, 500);
        }
        return jsonResponse([]);
      }
      const catalog = catalogGets()(url);
      if (catalog) {
        return catalog;
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    const cutters = await screen.findByRole("region", { name: "Резаки" });
    await waitFor(() => {
      expect(within(cutters).getByText("3")).toBeInTheDocument();
    });

    await userEvent.click(within(cutters).getByRole("button", { name: "Удалить" }));

    await waitFor(() => {
      expect(
        global.fetch.mock.calls.some(
          ([u, o]) => u === "/api/equipment/cutters/3" && o?.method === "DELETE"
        )
      ).toBe(true);
      expect(within(cutters).queryByText("3")).not.toBeInTheDocument();
    });

    const printers = screen.getByRole("region", { name: "Принтеры" });
    await waitFor(() => {
      expect(within(printers).getByRole("alert")).toHaveTextContent(
        "printers down"
      );
    });
    expect(
      screen.getByRole("columnheader", { name: "Имя" })
    ).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Ламинаторы" })).toBeInTheDocument();
  });
});
