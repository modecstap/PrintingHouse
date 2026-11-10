import { Tabs } from "./components/generic/tabs/tabs";
import Calculator from "./components/calculator/calculator";
import Orders from "./components/orders/orders";
import References from "./components/references/references";
import Auth from "./components/auth/auth";
import { useCatalogs } from "./hooks/useCatalogs";

function App() {
  const { catalogLoadState, reloadCatalogs } = useCatalogs();

  const catalogProps = {
    catalogs: catalogLoadState.catalogs,
    catalogLoadState,
  };

  const tabs = [
    {
      id: "calculator",
      label: "Калькулятор",
      Content: () => <Calculator {...catalogProps} />,
    },
    {
      id: "orders",
      label: "Заказы",
      Content: () => <Orders {...catalogProps} />,
    },
    {
      id: "references",
      label: "Справочники",
      Content: () => (
        <References
          catalogs={catalogLoadState.catalogs}
          onCatalogsInvalidated={reloadCatalogs}
        />
      ),
    },
    { id: "auth", label: "Вход", Content: Auth },
  ];

  return <Tabs tabs={tabs} defaultSelectedId="auth" />;
}

export default App;
