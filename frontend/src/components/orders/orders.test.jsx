import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Orders from "./orders";
import { jsonResponse } from "../../test-utils/json-response";
import { renderWithToken } from "../../test-utils/render-with-token";

const SAMPLE_PRODUCT = {
  parts_markup: 30,
  blocks: [
    {
      count: 2,
      imposition: {
        target: { name: "Визитка", width: 90, height: 50 },
        sheet_id: 1,
        bleeds: 2,
        spacing: 5,
      },
      operations: [
        {
          kind: "print",
          printer_id: 1,
          operator_id: 4,
          chroma: "FOUR_ZERO",
        },
        { kind: "cut", cutter_id: 2, operator_id: 6 },
      ],
    },
  ],
  operations: [],
};

const ORDER_DTO = {
  id: 1,
  count: 10,
  description: "",
  created_at: "2026-06-15T12:00:00Z",
  product: SAMPLE_PRODUCT,
};

const LIST_SUMMARY = {
  id: 1,
  count: 10,
  description: "Визитки",
  created_at: "2026-11-11T00:00:00Z",
};

const LIST_SUMMARY_2 = {
  id: 2,
  count: 5,
  description: "",
  created_at: "2026-01-01T00:00:00Z",
};

const REPORT_RAW = {
  product_price: "12.50",
  order_price: "125.00",
  income: "30.00",
  impositions: [8],
};

const SAMPLE_SHEET_CATALOG = [
  {
    id: 1,
    paper: {
      name: "Мелованная",
      density: 150,
      thickness: 1,
      price_per_kilo: "80.50",
    },
    format: { name: "SRA3", width: 320, height: 450 },
  },
];

function stubCatalogFetch() {
  return jest.fn((url, options) => {
    if (options?.method && options.method !== "GET") {
      return jsonResponse({}, 404);
    }
    if (url.startsWith("/api/equipment/") || url.startsWith("/api/staff/")) {
      return jsonResponse([]);
    }
    if (url === "/api/materials/sheets") {
      return jsonResponse(SAMPLE_SHEET_CATALOG);
    }
    if (url === "/api/materials/films") {
      return jsonResponse([]);
    }
    if (url === "/api/references") {
      return jsonResponse([]);
    }
    return jsonResponse({}, 404);
  });
}

describe("Orders", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    localStorage.clear();
  });

  it("should show id and count from the order list", async () => {
    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders" && (!options?.method || options.method === "GET")) {
        return jsonResponse([LIST_SUMMARY, LIST_SUMMARY_2]);
      }
      return jsonResponse({}, 404);
    });

    renderWithToken(<Orders />);

    await waitFor(() => {
      expect(screen.getByText("1")).toBeInTheDocument();
    });
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "ID" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Количество" })).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: "Описание" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: "Дата создания" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Визитки")).toBeInTheDocument();
    expect(screen.getByText("11.11.2026")).toBeInTheDocument();
    expect(screen.getByText("01.01.2026")).toBeInTheDocument();

    expect(screen.queryByRole("button", { name: "Отложить" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "В работу" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Обновить" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /удалить/i })).not.toBeInTheDocument();
  });

  it("should show an empty table when the list is empty", async () => {
    global.fetch = jest.fn((url) => {
      if (url === "/api/orders") {
        return jsonResponse([]);
      }
      return jsonResponse({}, 404);
    });

    renderWithToken(<Orders />);

    await waitFor(() => {
      expect(screen.getByRole("columnheader", { name: "ID" })).toBeInTheDocument();
    });
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByRole("row", { name: /1/ })).not.toBeInTheDocument();
  });

  it("should show the server detail when the list fails", async () => {
    global.fetch = jest.fn((url) => {
      if (url === "/api/orders") {
        return jsonResponse({ detail: "Could not validate credentials" }, 401);
      }
      return jsonResponse({}, 404);
    });

    renderWithToken(<Orders />);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Could not validate credentials",
      );
    });
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("should fill the calculator and show the report when a row is opened", async () => {
    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders" && (!options?.method || options.method === "GET")) {
        return jsonResponse([LIST_SUMMARY]);
      }
      if (url === "/api/orders/1" && (!options?.method || options.method === "GET")) {
        return jsonResponse(ORDER_DTO);
      }
      if (url === "/api/orders/1/report") {
        return jsonResponse(REPORT_RAW);
      }
      return stubCatalogFetch()(url, options);
    });

    renderWithToken(<Orders />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /1.*10|10.*1/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: /1.*10|10.*1/ }));

    await waitFor(() => {
      expect(screen.getByLabelText("Бумага:")).toHaveValue("1");
    });
    await waitFor(() => {
      expect(screen.getByText("Цена изделия")).toBeInTheDocument();
    });
  });

  it("should replace via PUT and reload the list without a new id", async () => {
    let listCallCount = 0;
    let putCalled = false;

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders" && (!options?.method || options.method === "GET")) {
        listCallCount += 1;
        return jsonResponse([LIST_SUMMARY]);
      }
      if (url === "/api/orders/1" && (!options?.method || options.method === "GET")) {
        return jsonResponse(ORDER_DTO);
      }
      if (url === "/api/orders/1/report") {
        return jsonResponse(REPORT_RAW);
      }
      if (url === "/api/orders/1" && options?.method === "PUT") {
        putCalled = true;
        return jsonResponse({ id: 1 });
      }
      if (url === "/api/orders" && options?.method === "POST") {
        return jsonResponse({ id: 99 });
      }
      return stubCatalogFetch()(url, options);
    });

    renderWithToken(<Orders />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /1.*10|10.*1/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: /1.*10|10.*1/ }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Сохранить" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));

    await waitFor(() => {
      expect(putCalled).toBe(true);
    });
    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Заказ сохранён: 1");
    });
    expect(listCallCount).toBeGreaterThanOrEqual(2);
    expect(
      global.fetch.mock.calls.some(
        ([u, o]) => u === "/api/orders" && o?.method === "POST",
      ),
    ).toBe(false);
  });
});
