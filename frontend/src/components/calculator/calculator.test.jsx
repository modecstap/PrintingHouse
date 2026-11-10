import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Calculator from "./calculator";
import { toOrderReport } from "./models/order";

const PRINTER = {
  id: 1,
  startup: "10",
  cyan: "0.1",
  magenta: "0.2",
  yellow: "0.3",
  black: "0.4",
};

const PRESS_OPERATOR = { id: 4, salary_by_operation: "5" };
const LAMINATOR_OPERATOR = { id: 5, salary_by_operation: "6" };
const CUTTER = { id: 2, max_stack: 40 };
const CUTTER_OPERATOR = { id: 6, salary_by_operation: "7" };

const QUOTE_REPORT_RAW = {
  product_price: "12.50",
  order_price: "125.00",
  income: "30.00",
  impositions: [8],
};

function jsonResponse(data, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  });
}

function stubCatalogFetch(overrides = {}) {
  const catalogs = {
    printers: [PRINTER],
    laminators: [],
    cutters: [CUTTER],
    pressOperators: [PRESS_OPERATOR],
    laminatorOperators: [LAMINATOR_OPERATOR],
    cutterOperators: [CUTTER_OPERATOR],
    dieCutOperators: [],
    sheets: [
      {
        id: 1,
        paper: { name: "A", density: 150, thickness: 1, price_per_kilo: "80" },
        format: { name: "SRA3", width: 320, height: 450 },
      },
    ],
    films: [],
    ...overrides,
  };

  return jest.fn((url, options) => {
    if (options?.method && options.method !== "GET") {
      return jsonResponse({}, 404);
    }
    if (url === "/api/equipment/printers") {
      return jsonResponse(catalogs.printers);
    }
    if (url === "/api/equipment/laminators") {
      return jsonResponse(catalogs.laminators);
    }
    if (url === "/api/equipment/cutters") {
      return jsonResponse(catalogs.cutters);
    }
    if (url === "/api/staff/press-operators") {
      return jsonResponse(catalogs.pressOperators);
    }
    if (url === "/api/staff/laminator-operators") {
      return jsonResponse(catalogs.laminatorOperators);
    }
    if (url === "/api/staff/cutter-operators") {
      return jsonResponse(catalogs.cutterOperators);
    }
    if (url === "/api/staff/die-cut-operators") {
      return jsonResponse(catalogs.dieCutOperators);
    }
    if (url === "/api/materials/sheets") {
      return jsonResponse(catalogs.sheets);
    }
    if (url === "/api/materials/films") {
      return jsonResponse(catalogs.films);
    }
    if (url === "/api/references") {
      return jsonResponse([]);
    }
    if (url === "/api/orders/quote" && options?.method === "POST") {
      return jsonResponse(QUOTE_REPORT_RAW);
    }
  });
}

const SAMPLE_PRODUCT = {
  blocks: [
    {
      count: 2,
      markup: 30,
      imposition: {
        target: { name: "Визитка", width: 90, height: 50 },
        sheet_id: null,
        bleeds: 2,
        spacing: 5,
      },
      operations: [],
    },
  ],
  operations: [],
};

const ORDER_DTO = { id: 42, count: 100, product: SAMPLE_PRODUCT };

async function fillMandatoryPrintAndCut() {
  const printRegion = screen.getByRole("region", { name: /Печать/i });
  await userEvent.selectOptions(
    within(printRegion).getByLabelText("Принтер"),
    "1",
  );
  await userEvent.selectOptions(
    within(printRegion).getByLabelText("Печатник"),
    "4",
  );
  const cutRegion = screen.getByRole("region", { name: /^Рез$/i });
  await userEvent.selectOptions(
    within(cutRegion).getByLabelText("Резак"),
    "2",
  );
  await userEvent.selectOptions(
    within(cutRegion).getByLabelText("Оператор"),
    "6",
  );
}

async function waitForCatalogs(fetchMock = global.fetch) {
  await waitFor(() => {
    const catalogUrls = [
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
    for (const url of catalogUrls) {
      expect(fetchMock).toHaveBeenCalledWith(
        url,
        expect.objectContaining({ method: "GET" }),
      );
    }
  });
}

describe("Calculator", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  afterEach(() => {
    global.fetch = originalFetch;
    localStorage.clear();
  });

  it("should show the quote report when the form is complete", async () => {
  let resolveQuote;
    const quotePending = new Promise((resolve) => {
      resolveQuote = resolve;
    });

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders/quote" && options?.method === "POST") {
        return quotePending.then(() => jsonResponse(QUOTE_REPORT_RAW));
      }
      return stubCatalogFetch()(url, options);
    });

    render(<Calculator />);
    await waitForCatalogs();

    expect(screen.getByText("Пропущено:")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByLabelText("Бумага")).toHaveValue("1");
    });

    await userEvent.clear(screen.getByLabelText("Тираж"));
    await userEvent.type(screen.getByLabelText("Тираж"), "10");
    await userEvent.clear(screen.getByLabelText("Ширина"));
    await userEvent.type(screen.getByLabelText("Ширина"), "90");
    await userEvent.clear(screen.getByLabelText("Высота"));
    await userEvent.type(screen.getByLabelText("Высота"), "50");
    await fillMandatoryPrintAndCut();

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Счёт...");
    });
    expect(screen.getByRole("button", { name: "Сохранить" })).toBeDisabled();

    resolveQuote();
    const quoteCall = global.fetch.mock.calls.find(
      ([u]) => u === "/api/orders/quote",
    );
    expect(quoteCall).toBeDefined();
    expect(quoteCall[0]).toBe("/api/orders/quote");

    await waitFor(() => {
      expect(screen.getByText("Цена изделия")).toBeInTheDocument();
    });
    expect(screen.getByText("Цена тиража")).toBeInTheDocument();
    expect(screen.getByText("Прибыль")).toBeInTheDocument();
    expect(screen.getByText("Блок 1: на листе")).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
  });

  it("should show the saved order id when the user saves", async () => {
    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders" && options?.method === "POST") {
        return jsonResponse({ id: 15 });
      }
      return stubCatalogFetch()(url, options);
    });

    const onSaved = jest.fn();
    render(<Calculator onSaved={onSaved} />);
    await waitForCatalogs();

    await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Заказ сохранён: 15");
    });
    expect(onSaved).toHaveBeenCalledWith(15);
  });

  it("should offer only press operators in a print operation", async () => {
    global.fetch = stubCatalogFetch();
    render(<Calculator />);
    await waitForCatalogs();

    await waitFor(() => {
      const printRegion = screen.getByRole("region", { name: /Печать/i });
      expect(within(printRegion).getByLabelText("Принтер")).toHaveValue("1");
      expect(within(printRegion).getByLabelText("Печатник")).toHaveValue("4");
    });

    const operatorSelect = within(
      screen.getByRole("region", { name: /Печать/i }),
    ).getByLabelText("Печатник");
    const options = within(operatorSelect).getAllByRole("option");
    const labels = options.map((o) => o.textContent);

    expect(labels.some((t) => t.includes("зарплата 5.00"))).toBe(true);
    expect(labels.some((t) => t.includes("зарплата 6.00"))).toBe(false);
    expect(
      screen.queryByRole("button", { name: /создать|добавить.*принтер|оператор/i }),
    ).not.toBeInTheDocument();
  });

  it("should show the server detail when the quote is rejected", async () => {
    const initialReport = toOrderReport({
      product_price: "1.00",
      order_price: "10.00",
      income: "2.00",
      impositions: [3],
    });

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders/quote" && options?.method === "POST") {
        return jsonResponse(
          { detail: "body.count: Input should be a valid integer" },
          422,
        );
      }
      return stubCatalogFetch()(url, options);
    });

    render(<Calculator initialReport={initialReport} />);
    await waitForCatalogs();

    await userEvent.clear(screen.getByLabelText("Тираж"));
    await userEvent.type(screen.getByLabelText("Тираж"), "10");
    await waitFor(() => {
      expect(screen.getByLabelText("Бумага")).toHaveValue("1");
    });
    await userEvent.clear(screen.getByLabelText("Ширина"));
    await userEvent.type(screen.getByLabelText("Ширина"), "90");
    await userEvent.clear(screen.getByLabelText("Высота"));
    await userEvent.type(screen.getByLabelText("Высота"), "50");
    await fillMandatoryPrintAndCut();

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "body.count: Input should be a valid integer",
      );
    });
    expect(screen.getByText("Цена изделия")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("should load the order form when the user picks a preset", async () => {
    global.fetch = jest.fn((url, options) => {
      if (url === "/api/references") {
        return jsonResponse([
          { name: "Визитки", description: "стандарт", order_id: 42 },
        ]);
      }
      if (url === "/api/orders/42") {
        return jsonResponse(ORDER_DTO);
      }
      return stubCatalogFetch()(url, options);
    });

    render(<Calculator />);
    await waitForCatalogs();

    await waitFor(() => {
      expect(screen.getByLabelText("Пресет")).toBeInTheDocument();
    });

    await userEvent.selectOptions(screen.getByLabelText("Пресет"), "42");

    await waitFor(() => {
      expect(screen.getByLabelText("Тираж")).toHaveValue(100);
    });
    expect(screen.getByLabelText("Ширина")).toHaveValue(90);
    expect(screen.getByLabelText("Высота")).toHaveValue(50);
  });

  it("should not offer calculate, delay, accept, or update", async () => {
    global.fetch = stubCatalogFetch();
    render(<Calculator />);
    await waitForCatalogs();

    expect(
      screen.queryByRole("button", { name: "Рассчитать" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Отложить" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "В работу" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Обновить" })).not.toBeInTheDocument();
  });
});
