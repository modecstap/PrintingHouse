import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AuthPage from "./AuthPage";

function jsonResponse(data, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  });
}

describe("AuthPage", () => {
  const originalFetch = global.fetch;
  let alertSpy;

  beforeEach(() => {
    if (!global.structuredClone) {
      global.structuredClone = (value) => JSON.parse(JSON.stringify(value));
    }
    alertSpy = jest.spyOn(window, "alert").mockImplementation(() => {});
    localStorage.clear();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    alertSpy.mockRestore();
    localStorage.clear();
  });

  it("should store the access token when login succeeds", async () => {
    global.fetch = jest.fn((url, options) => {
      if (url === "/auth/token" && options?.method === "POST") {
        const body = JSON.parse(options.body);
        expect(body).toEqual({
          username: "alice",
          password: "secret",
        });
        return jsonResponse({ access_token: "jwt-abc" });
      }
      return jsonResponse({}, 404);
    });

    const { container } = render(<AuthPage />);
    const [usernameInput, passwordInput] = container.querySelectorAll("input");

    await userEvent.type(usernameInput, "alice");
    await userEvent.type(passwordInput, "secret");
    await userEvent.click(screen.getByRole("button", { name: "Войти" }));

    await waitFor(() => {
      expect(localStorage.getItem("access_token")).toBe("jwt-abc");
    });
  });

  it("should remove the access token when the user logs out", async () => {
    localStorage.setItem("access_token", "jwt-abc");

    render(<AuthPage />);
    await userEvent.click(screen.getByRole("button", { name: "Выйти" }));

    expect(localStorage.getItem("access_token")).toBeNull();
  });
});
