import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

describe("References", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    localStorage.setItem("access_token", "test-token");
  });

  afterEach(() => {
    global.fetch = originalFetch;
    localStorage.clear();
  });

  it("should show name, description, and order id", async () => {
    global.fetch = jest.fn((url) => {
      if (url === "/api/references") {
        return jsonResponse([
          { name: "Шаблон", description: "Визитка", order_id: 3 },
        ]);
      }
      return jsonResponse({}, 404);
    });

    render(<References />);

    await waitFor(() => {
      expect(screen.getByText("Шаблон")).toBeInTheDocument();
    });
    expect(screen.getByText("Визитка")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Имя" })).toBeInTheDocument();
    expect(
      screen.queryByLabelText(/Стоимость голубой краски/)
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/лист/i)).not.toBeInTheDocument();
  });

  it("should clear the form and show the new row after save", async () => {
    let getCount = 0;
    global.fetch = jest.fn((url, options) => {
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
      expect(screen.getByRole("columnheader", { name: "Имя" })).toBeInTheDocument();
    });

    await userEvent.type(screen.getByLabelText("Имя"), "Новый");
    await userEvent.type(screen.getByLabelText("Описание"), "Описание");
    await userEvent.type(screen.getByLabelText("Номер заказа"), "5");
    await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));

    await waitFor(() => {
      expect(screen.getByText("Новый")).toBeInTheDocument();
    });
    expect(screen.getByLabelText("Имя")).toHaveValue("");
    expect(screen.getByLabelText("Описание")).toHaveValue("");
    expect(screen.getByLabelText("Номер заказа")).toHaveValue(null);
  });

  it("should show the server detail and keep the row out when the order is missing", async () => {
    global.fetch = jest.fn((url, options) => {
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
      expect(screen.getByRole("columnheader", { name: "Имя" })).toBeInTheDocument();
    });

    await userEvent.type(screen.getByLabelText("Имя"), "X");
    await userEvent.type(screen.getByLabelText("Описание"), "Y");
    await userEvent.type(screen.getByLabelText("Номер заказа"), "99");
    await userEvent.click(screen.getByRole("button", { name: "Сохранить" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("order missing");
    });
    expect(screen.getByLabelText("Номер заказа")).toHaveValue(99);

    const tbody = screen.getByRole("table").querySelector("tbody");
    expect(within(tbody).queryAllByRole("row")).toHaveLength(0);
  });
});
