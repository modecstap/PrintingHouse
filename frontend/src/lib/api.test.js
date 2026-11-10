import { requestJson, setUnauthorizedHandler } from "./api";

describe("requestJson", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("should send Bearer token and return parsed JSON on GET success", async () => {
    localStorage.setItem("access_token", "abc");
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: 1 }],
    });

    const data = await requestJson("/api/orders", { method: "GET" });

    expect(global.fetch).toHaveBeenCalledWith("/api/orders", {
      method: "GET",
      headers: {
        Authorization: "Bearer abc",
      },
      signal: undefined,
    });
    expect(data).toEqual([{ id: 1 }]);
  });

  it("should send Bearer with empty token when access_token is missing", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    });

    await requestJson("/api/orders", { method: "GET" });

    expect(global.fetch.mock.calls[0][1].headers.Authorization).toBe("Bearer ");
  });

  it("should reject with detail string on 422", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ detail: "body.count: Input should be a valid integer" }),
    });

    await expect(requestJson("/api/orders", { method: "POST", body: {} })).rejects.toThrow(
      "body.count: Input should be a valid integer",
    );
  });

  it("should reject with formatted validation array detail on 422", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({
        detail: [{ loc: ["body", "count"], msg: "field required" }],
      }),
    });

    await expect(requestJson("/api/orders", { method: "POST", body: {} })).rejects.toThrow(
      "body → count: field required",
    );
  });

  it("should clear token and call unauthorized handler on 401", async () => {
    localStorage.setItem("access_token", "stale");
    const onUnauthorized = jest.fn();
    setUnauthorizedHandler(onUnauthorized);

    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Unauthorized" }),
    });

    await expect(requestJson("/api/orders", { method: "GET" })).rejects.toThrow("Unauthorized");

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(onUnauthorized).toHaveBeenCalled();

    setUnauthorizedHandler(null);
  });

  it("should resolve to null on 204", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 204,
    });

    const data = await requestJson("/api/references", { method: "POST", body: {} });

    expect(data).toBeNull();
  });

  it("should reject with connection message on fetch TypeError", async () => {
    const networkError = new TypeError("Failed to fetch");
    global.fetch = jest.fn().mockRejectedValue(networkError);

    await expect(requestJson("/api/orders", { method: "GET" })).rejects.toThrow(
      "Не удалось подключиться к серверу. Проверьте соединение.",
    );
  });

  it("should rethrow AbortError unchanged", async () => {
    const abortError = new DOMException("Aborted", "AbortError");
    global.fetch = jest.fn().mockRejectedValue(abortError);

    await expect(requestJson("/api/orders", { method: "GET" })).rejects.toBe(abortError);
  });
});
