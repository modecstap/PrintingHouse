import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Tabs } from "./tabs";

jest.mock("../../calculator/calculator", () => () => (
  <div data-testid="calculator-mock" />
));
jest.mock("../../orders/orders", () => () => (
  <div data-testid="orders-mock" />
));
jest.mock("../../references/references", () => () => (
  <div data-testid="references-mock" />
));
jest.mock("../../auth/auth", () => () => <div data-testid="auth-mock" />);

import Calculator from "../../calculator/calculator";
import Orders from "../../orders/orders";
import References from "../../references/references";
import Auth from "../../auth/auth";

const TABS = [
  { id: "calculator", label: "Калькулятор", Content: Calculator },
  { id: "orders", label: "Заказы", Content: Orders },
  { id: "references", label: "Справочники", Content: References },
  { id: "auth", label: "Вход", Content: Auth },
];

describe("Tabs", () => {
  it("should show the four menu labels", () => {
    render(<Tabs tabs={TABS} />);

    expect(screen.getByRole("tab", { name: "Калькулятор" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Заказы" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Справочники" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Вход" })).toBeInTheDocument();

    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
    expect(screen.queryByText("Меню")).not.toBeInTheDocument();
    expect(screen.queryByAltText("Логотип")).not.toBeInTheDocument();

    expect(screen.queryByText(/оборудован/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/персонал/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/staff/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/equipment/i)).not.toBeInTheDocument();
  });

  it("should mount every tab and hide inactive panels", () => {
    render(<Tabs tabs={TABS} />);

    expect(screen.getByTestId("calculator-mock")).toBeInTheDocument();
    expect(screen.getByTestId("orders-mock")).toBeInTheDocument();
    expect(screen.getByTestId("references-mock")).toBeInTheDocument();
    expect(screen.getByTestId("auth-mock")).toBeInTheDocument();

    const calculatorPanel = screen.getByTestId("calculator-mock").parentElement;
    const ordersPanel = screen.getByTestId("orders-mock").parentElement;

    expect(calculatorPanel).not.toHaveAttribute("hidden");
    expect(ordersPanel).toHaveAttribute("hidden");
  });

  it("should keep calculator mounted when the Orders tab is selected", async () => {
    render(<Tabs tabs={TABS} />);

    await userEvent.click(screen.getByRole("tab", { name: "Заказы" }));

    expect(screen.getByTestId("orders-mock")).toBeInTheDocument();
    expect(screen.getByTestId("calculator-mock")).toBeInTheDocument();

    const calculatorPanel = screen.getByTestId("calculator-mock").parentElement;
    const ordersPanel = screen.getByTestId("orders-mock").parentElement;

    expect(ordersPanel).not.toHaveAttribute("hidden");
    expect(calculatorPanel).toHaveAttribute("hidden");
  });
});
