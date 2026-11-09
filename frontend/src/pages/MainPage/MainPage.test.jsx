import { render, screen } from "@testing-library/react";
import MainPage from "./MainPage";

jest.mock("../../components/calculator/calculator", () => () => (
  <div data-testid="calculator-mock" />
));
jest.mock("../../components/orders/orders", () => () => (
  <div data-testid="orders-mock" />
));
jest.mock("../../components/references/references", () => () => (
  <div data-testid="references-mock" />
));
jest.mock("../AuthPage/AuthPage", () => () => <div data-testid="auth-mock" />);

describe("MainPage", () => {
  it("should show the four menu labels", () => {
    render(<MainPage />);

    expect(screen.getByText("Калькулятор многополосный")).toBeInTheDocument();
    expect(screen.getByText("Таблица заказов")).toBeInTheDocument();
    expect(screen.getByText("Справочная система")).toBeInTheDocument();
    expect(screen.getByText("Авторизация")).toBeInTheDocument();

    const menuItems = screen.getAllByRole("listitem");
    expect(menuItems).toHaveLength(4);

    expect(screen.queryByText(/оборудован/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/персонал/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/staff/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/equipment/i)).not.toBeInTheDocument();
  });
});
