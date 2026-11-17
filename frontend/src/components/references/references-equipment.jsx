import { EQUIPMENT_CATALOGS } from "./catalog-defs";
import CatalogGroupPage from "./catalog-group-page";

export default function ReferencesEquipment({ onCatalogsInvalidated }) {
  return (
    <CatalogGroupPage
      title="Оборудование"
      catalogs={EQUIPMENT_CATALOGS}
      onCatalogsInvalidated={onCatalogsInvalidated}
    />
  );
}