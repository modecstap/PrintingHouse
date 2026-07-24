import { useState } from "react";
import "./MainPage.css";

import ReferencePage from "../Reference/ReferencePage";
import CostCalculator from "../CostCalculator/CostCalculator";
import OrderPage from "../Orders/OrderPage";
import AuthPage from "../AuthPage/AuthPage";

import logo from "../../media/VSRT-print.png";

const MainPage = () => {
  const [selectedPage, setSelectedPage] = useState("calculator");
  const [menuOpen, setMenuOpen] = useState(false);

  const changePage = (page) => {
    setSelectedPage(page);
    setMenuOpen(false); // закрываем бургер после выбора
  };

  return (
    <div className="main-container">
      <div className="sidebar">

        <div className="sidebar-header">
          <h2 className="sidebar-title">Меню</h2>

          <button
            className="burger-btn"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            ☰
          </button>
        </div>

        <ul className={`menu ${menuOpen ? "open" : ""}`}>
          <li
            className={`menu-item ${
              selectedPage === "calculator" ? "active" : ""
            }`}
            onClick={() => changePage("calculator")}
          >
            Калькулятор многополосный
          </li>

          <li
            className={`menu-item ${
              selectedPage === "orders" ? "active" : ""
            }`}
            onClick={() => changePage("orders")}
          >
            Таблица заказов
          </li>

          <li
            className={`menu-item ${
              selectedPage === "reference" ? "active" : ""
            }`}
            onClick={() => changePage("reference")}
          >
            Справочная система
          </li>

          <li
            className={`menu-item ${
              selectedPage === "auth" ? "active" : ""
            }`}
            onClick={() => changePage("auth")}
          >
            Авторизация
          </li>
        </ul>

        <div className="sidebar-footer">
          <img src={logo} alt="Логотип" className="sidebar-image" />
        </div>
      </div>

      <div className="form-display">
        {selectedPage === "calculator" && <CostCalculator />}
        {selectedPage === "reference" && <ReferencePage />}
        {selectedPage === "orders" && <OrderPage />}
        {selectedPage === "auth" && <AuthPage />}
      </div>
    </div>
  );
};

export default MainPage;