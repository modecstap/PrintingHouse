import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Orders from "./orders";

const SAMPLE_PRODUCT = {
  blocks: [
    {
      count: 2,
      markup: 30,
      imposition: {
        target: { name: "Визитка", width: 90, height: 50 },
        sheet_id: 1,
        bleeds: 2,
        spacing: 5,
      },
      operations: [],
    },
  ],
  operations: [],
};

const ORDER_DTO = { id: 1, count: 10, product: SAMPLE_PRODUCT };

const REPORT_RAW = {
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
    return jsonResponse({}, 404);
  });
}

describe("Orders", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  afterEach(() => {
    global.fetch = originalFetch;
    localStorage.clear();
  });

  it("should show id and count from the order list", async () => {
    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders" && (!options?.method || options.method === "GET")) {
        return jsonResponse([
          { id: 1, count: 10 },
          { id: 2, count: 5 },
        ]);
      }
      return jsonResponse({}, 404);
    });

    render(<Orders />);

    await waitFor(() => {
      expect(screen.getByText("1")).toBeInTheDocument();
    });
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "ID" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Количество" })).toBeInTheDocument();

    expect(screen.queryByRole("button", { name: "Отложить" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "В работу" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Обновить" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /удалить/i })).not.toBeInTheDocument();
  });

  it("should show an empty table when the list is empty", async () => {
    global.fetch = jest.fn((url) => {
      if (url === "/api/orders") {
        return jsonResponse([]);
      }
      return jsonResponse({}, 404);
    });

    render(<Orders />);

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

    render(<Orders />);

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
        return jsonResponse([{ id: 1, count: 10 }]);
      }
      if (url === "/api/orders/1" && (!options?.method || options.method === "GET")) {
        return jsonResponse(ORDER_DTO);
      }
      if (url === "/api/orders/1/report") {
        return jsonResponse(REPORT_RAW);
      }
      return stubCatalogFetch()(url, options);
    });

    render(<Orders />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /1.*10|10.*1/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: /1.*10|10.*1/ }));

    await waitFor(() => {
      expect(screen.getByDisplayValue("SRA3")).toBeInTheDocument();
    });
    expect(screen.getByText("Цена изделия")).toBeInTheDocument();
  });

  it("should reload the list after a save from the open order", async () => {
    let listCallCount = 0;

    global.fetch = jest.fn((url, options) => {
      if (url === "/api/orders" && (!options?.method || options.method === "GET")) {
        listCallCount += 1;
        if (listCallCount === 1) {
          return jsonResponse([{ id: 1, count: 10 }]);
        }
        return jsonResponse([
          { id: 1, count: 10 },
          { id: 16, count: 10 },
        ]);
      }
      if (url === "/api/orders/1") {
        return jsonResponse(ORDER_DTO);
      }
      if (url === "/api/orders/1/report") {
        return jsonResponse(REPORT_RAW);
      }
      if (url === "/api/orders" && options?.method === "POST") {
        return jsonResponse({ id: 16 });
      }
      return stubCatalogFetch()(url, options);
    });

    render(<Orders />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /1.*10|10.*1/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: /1.*10|10.*1/ }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Сохранить" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Заказ сохранён: 16");
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /16.*10|10.*16/ })).toBeInTheDocument();
    });
    expect(listCallCount).toBeGreaterThanOrEqual(2);
  });
});
