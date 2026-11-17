import { Tabs } from "./components/generic/tabs/tabs";
import Calculator from "./components/calculator/calculator";
import Orders from "./components/orders/orders";
import ReferenceValues from "./components/references/reference-values";
import ReferencesEquipment from "./components/references/references-equipment";
import ReferencesMaterials from "./components/references/references-materials";
import ReferencesStaff from "./components/references/references-staff";
import Auth from "./components/auth/auth";
import { useCatalogs } from "./hooks/useCatalogs";
import { AuthSessionProvider, useAuthSession } from "./lib/auth-session";

function AppTabs() {
  const { catalogLoadState, reloadCatalogs } = useCatalogs();
  const { isAuthenticated } = useAuthSession();

  const catalogProps = {
    catalogs: catalogLoadState.catalogs,
    catalogLoadState,
  };

  const referenceCatalogProps = {
    onCatalogsInvalidated: reloadCatalogs,
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
      id: "references-equipment",
      label: "Оборудование",
      Content: () => <ReferencesEquipment {...referenceCatalogProps} />,
    },
    {
      id: "references-staff",
      label: "Персонал",
      Content: () => <ReferencesStaff {...referenceCatalogProps} />,
    },
    {
      id: "references-materials",
      label: "Материалы",
      Content: () => <ReferencesMaterials {...referenceCatalogProps} />,
    },
    {
      id: "reference-values",
      label: "Значения",
      Content: () => <ReferenceValues {...referenceCatalogProps} />,
    },
    { id: "auth", label: "Вход", Content: Auth },
  ];

  const isTabDisabled = (id) => !isAuthenticated && id !== "auth";

  return (
    <Tabs
      tabs={tabs}
      defaultSelectedId="auth"
      isTabDisabled={isTabDisabled}
    />
  );
}

function App() {
  return (
    <AuthSessionProvider>
      <AppTabs />
    </AuthSessionProvider>
  );
}

export default App;