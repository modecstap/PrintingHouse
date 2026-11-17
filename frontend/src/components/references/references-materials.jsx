import { MATERIAL_CATALOGS } from "./catalog-defs";
import CatalogGroupPage from "./catalog-group-page";

export default function ReferencesMaterials({ onCatalogsInvalidated }) {
  return (
    <CatalogGroupPage
      title="Материалы"
      catalogs={MATERIAL_CATALOGS}
      onCatalogsInvalidated={onCatalogsInvalidated}
    />
  );
}