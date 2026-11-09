import { Tabs } from "./components/generic/tabs/tabs";
import Calculator from "./components/calculator/calculator";
import Orders from "./components/orders/orders";
import References from "./components/references/references";
import Auth from "./components/auth/auth";

const TABS = [
  { id: "calculator", label: "Калькулятор", Content: Calculator },
  { id: "orders", label: "Заказы", Content: Orders },
  { id: "references", label: "Справочники", Content: References },
  { id: "auth", label: "Вход", Content: Auth },
];

function App() {
  return <Tabs tabs={TABS} />;
}

export default App;
