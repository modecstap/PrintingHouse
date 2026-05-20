import { useState } from "react";
import "./MainPage.css";
import VariableTable from "../features/stuff/Table/VariableTable";
import CostCalculatorPage from "../features/cost-calculator/CostCalculatorPage";
import ReferencePage from "../features/reference-system/reference_page";
import MultiLineCalculator from "../features/cost-calculator/MultiLineCalculator";
import OrderPage from "../features/Orders/OrderPage";

const MainPage = () => {
  const [selectedPage, setSelectedPage] = useState("calculator");

  return (
    <div className="main-container">
      {/* Левая панель */}
      <div className="sidebar">
        <h2 className="sidebar-title">Меню</h2>
        <ul className="menu">
          <li
            className={`menu-item ${selectedPage === "calculator" ? "active" : ""}`}
            onClick={() => setSelectedPage("calculator")}
          >
            Калькулятор однополосный
          </li>
          <li
            className={`menu-item ${selectedPage === "calculator-multi-line" ? "active" : ""}`}
            onClick={() => setSelectedPage("calculator-multi-line")}
          >
            Калькулятор многополосный
          </li>
          <li
            className={`menu-item ${selectedPage === "orders" ? "active" : ""}`}
            onClick={() => setSelectedPage("orders")}
          >
            Таблица заказов
          </li>
          <li
            className={`menu-item ${selectedPage === "reference" ? "active" : ""}`}
            onClick={() => setSelectedPage("reference")}
          >
            Справочная система
          </li>
        </ul>
      </div>

      {/* Правая панель */}
      <div className="form-display">
        {selectedPage === "calculator" && <CostCalculatorPage />}
        {selectedPage === "calculator-multi-line" && <MultiLineCalculator />}
        {selectedPage === "reference" && <ReferencePage />}
        {selectedPage === "orders" && (
          <OrderPage/>
        )}
      </div>
    </div>
  );
};

export default MainPage;
