import { render } from "@testing-library/react";
import { AuthSessionProvider } from "../lib/auth-session";

const DEFAULT_TOKEN = "test-token";

/**
 * @param {null} options.token — do not write localStorage (e.g. login from empty session)
 */
export function renderWithToken(ui, options = {}) {
  const {
    token = DEFAULT_TOKEN,
    withSession = true,
    ...renderOptions
  } = options;

  if (token !== null) {
    localStorage.setItem("access_token", token);
  }

  const tree = withSession ? (
    <AuthSessionProvider>{ui}</AuthSessionProvider>
  ) : (
    ui
  );

  return render(tree, renderOptions);
}
