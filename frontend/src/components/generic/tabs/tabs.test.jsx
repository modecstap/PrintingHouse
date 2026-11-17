import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Tabs } from "./tabs";

jest.mock("../../calculator/calculator", () => () => (
  <div data-testid="calculator-mock" />
));
jest.mock("../../orders/orders", () => () => (
  <div data-testid="orders-mock" />
));
jest.mock("../../references/reference-values", () => () => (
  <div data-testid="reference-values-mock" />
));
jest.mock("../../references/references-equipment", () => () => (
  <div data-testid="references-equipment-mock" />
));
jest.mock("../../references/references-staff", () => () => (
  <div data-testid="references-staff-mock" />
));
jest.mock("../../references/references-materials", () => () => (
  <div data-testid="references-materials-mock" />
));
jest.mock("../../auth/auth", () => () => <div data-testid="auth-mock" />);

import Calculator from "../../calculator/calculator";
import Orders from "../../orders/orders";
import ReferenceValues from "../../references/reference-values";
import ReferencesEquipment from "../../references/references-equipment";
import ReferencesMaterials from "../../references/references-materials";
import ReferencesStaff from "../../references/references-staff";
import Auth from "../../auth/auth";

const TABS = [
  { id: "calculator", label: "Калькулятор", Content: Calculator },
  { id: "orders", label: "Заказы", Content: Orders },
  { id: "references-equipment", label: "Оборудование", Content: ReferencesEquipment },
  { id: "references-staff", label: "Персонал", Content: ReferencesStaff },
  { id: "references-materials", label: "Материалы", Content: ReferencesMaterials },
  { id: "reference-values", label: "Значения", Content: ReferenceValues },
  { id: "auth", label: "Вход", Content: Auth },
];

describe("Tabs", () => {
  it("should show the main menu labels", () => {
    render(<Tabs tabs={TABS} />);

    expect(screen.getByRole("tab", { name: "Калькулятор" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Заказы" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Оборудование" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Персонал" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Материалы" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Значения" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Вход" })).toBeInTheDocument();

    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
    expect(screen.queryByText("Меню")).not.toBeInTheDocument();
    expect(screen.queryByAltText("Логотип")).not.toBeInTheDocument();
    expect(screen.queryByText("Справочники")).not.toBeInTheDocument();
  });

  it("should mount every tab and hide inactive panels", () => {
    render(<Tabs tabs={TABS} />);

    expect(screen.getByTestId("calculator-mock")).toBeInTheDocument();
    expect(screen.getByTestId("orders-mock")).toBeInTheDocument();
    expect(screen.getByTestId("references-equipment-mock")).toBeInTheDocument();
    expect(screen.getByTestId("references-staff-mock")).toBeInTheDocument();
    expect(screen.getByTestId("references-materials-mock")).toBeInTheDocument();
    expect(screen.getByTestId("reference-values-mock")).toBeInTheDocument();
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