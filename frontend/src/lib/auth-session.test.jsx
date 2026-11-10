import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthSessionProvider, useAuthSession } from "./auth-session";
import { requestJson, setUnauthorizedHandler } from "./api";

function SessionProbe() {
  const { isAuthenticated, login, logout } = useAuthSession();
  return (
    <div>
      <span data-testid="authenticated">
        {isAuthenticated ? "yes" : "no"}
      </span>
      <button type="button" onClick={() => login("jwt-new")}>
        Login
      </button>
      <button type="button" onClick={logout}>
        Logout
      </button>
    </div>
  );
}

describe("AuthSessionProvider", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    setUnauthorizedHandler(null);
    localStorage.clear();
  });

  it("should reflect stored token on mount", () => {
    localStorage.setItem("access_token", "jwt-stored");

    render(
      <AuthSessionProvider>
        <SessionProbe />
      </AuthSessionProvider>,
    );

    expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");
  });

  it("should update session on login and logout", async () => {
    render(
      <AuthSessionProvider>
        <SessionProbe />
      </AuthSessionProvider>,
    );

    expect(screen.getByTestId("authenticated")).toHaveTextContent("no");

    await userEvent.click(screen.getByRole("button", { name: "Login" }));

    expect(localStorage.getItem("access_token")).toBe("jwt-new");
    expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");

    await userEvent.click(screen.getByRole("button", { name: "Logout" }));

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(screen.getByTestId("authenticated")).toHaveTextContent("no");
  });

  it("should reset session when requestJson receives 401", async () => {
    localStorage.setItem("access_token", "stale");

    render(
      <AuthSessionProvider>
        <SessionProbe />
      </AuthSessionProvider>,
    );

    expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");

    global.fetch = jest.fn(async () => ({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Unauthorized" }),
    }));

    await act(async () => {
      await expect(requestJson("/api/orders")).rejects.toThrow("Unauthorized");
    });

    await waitFor(() => {
      expect(screen.getByTestId("authenticated")).toHaveTextContent("no");
    });
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});
