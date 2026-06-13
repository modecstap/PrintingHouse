import { useState } from "react";
import "./MainPage.css";
import ReferencePage from "../Reference/ReferencePage";
import CostCalculator from "../CostCalculator/CostCalculator";
import OrderPage from "../Orders/OrderPage";
import AuthPage from "../AuthPage/AuthPage";

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
          <li
            className={`menu-item ${selectedPage === "auth" ? "active" : ""}`}
            onClick={() => setSelectedPage("auth")}
          >
            Авторизация
          </li>
        </ul>
      </div>

      {/* Правая панель */}
      <div className="form-display">
        {selectedPage === "calculator" && <CostCalculator/>}
        {selectedPage === "reference" && <ReferencePage />}
        {selectedPage === "orders" && (<OrderPage/>)}
        {selectedPage === "auth" && <AuthPage/>}
      </div>
    </div>
  );
};

export default MainPage;
