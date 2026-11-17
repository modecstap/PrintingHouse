import CatalogPanel from "./catalog-panel";
import pageStyles from "../generic/page/page.module.css";

export default function CatalogGroupPage({
  title,
  catalogs,
  onCatalogsInvalidated,
}) {
  return (
    <div className={pageStyles.page}>
      <div className={pageStyles.pageTitle}>
        <h1>{title}</h1>
      </div>
      {catalogs.map((def) => (
        <CatalogPanel
          key={def.key}
          def={def}
          onCatalogsInvalidated={onCatalogsInvalidated}
        />
      ))}
    </div>
  );
}