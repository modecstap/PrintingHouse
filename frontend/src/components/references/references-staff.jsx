import { STAFF_CATALOGS } from "./catalog-defs";
import CatalogGroupPage from "./catalog-group-page";

export default function ReferencesStaff({ onCatalogsInvalidated }) {
  return (
    <CatalogGroupPage
      title="Персонал"
      catalogs={STAFF_CATALOGS}
      onCatalogsInvalidated={onCatalogsInvalidated}
    />
  );
}