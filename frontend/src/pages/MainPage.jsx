import { useState } from "react";
import "./MainPage.css";
import VariableTable from "../features/stuff/Table/VariableTable";
import CostCalculatorPage from "../features/cost-calculator/CostCalculatorPage";

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
            Калькулятор стоимости
          </li>
          <li
            className={`menu-item ${selectedPage === "orders" ? "active" : ""}`}
            onClick={() => setSelectedPage("orders")}
          >
            Таблица заказов
          </li>
        </ul>
      </div>

      {/* Правая панель */}
      <div className="form-display">
        {selectedPage === "calculator" && <CostCalculatorPage />}
        {selectedPage === "orders" && (
          <VariableTable
            endPoint="api/order/"
            title="Заказы"
            visibleFields={["id", "creation_date", "comment", "status"]}
          />
        )}
      </div>
    </div>
  );
};

export default MainPage;
