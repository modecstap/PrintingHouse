import {
  catalogSelectOptionLabel,
  cutterDetailLabel,
  cutterLabel,
  filmLabel,
  filmShortLabel,
  laminatorDetailLabel,
  laminatorLabel,
  operatorDetailLabel,
  operatorLabel,
  printerDetailLabel,
  printerLabel,
} from "../models/catalog-label";
import {
  emptyFilmFields,
  filmOptionFromCatalog,
} from "../models/order";
import { Dropdown } from "../../generic/dropdown/dropdown";
import styles from "../calculator.module.css";

const KIND_HEADING = {
  print: "Печать",
  laminate: "Ламинация",
  cut: "Рез",
  die_cut: "Высечка",
};

function resolveFilmId(filmId, film, films) {
  if (filmId) {
    return filmId;
  }
  const match = films.find(
    (row) =>
      row.name === film.name &&
      row.price === film.price &&
      String(row.density) === String(film.density),
  );
  return match ? String(match.id) : "";
}

function catalogDropdownOptions(items, value, shortLabel, detailLabel) {
  return items.map((item) => ({
    value: String(item.id),
    label: catalogSelectOptionLabel({
      value,
      optionValue: item.id,
      shortLabel: shortLabel(item),
      detailLabel: detailLabel(item),
    }),
  }));
}

export default function OperationFields({ operation, catalogs, onChange }) {
  const heading = KIND_HEADING[operation.kind] ?? operation.kind;
  const idPrefix = `${operation.clientKey}`;

  if (operation.kind === "print") {
    return (
      <article
        className={styles.operationCard}
        role="region"
        aria-label={heading}
      >
        <div className={styles.fieldRow}>
          <Dropdown
            id={`${idPrefix}-printer`}
            label="Принтер"
            value={operation.printerId}
            onChange={(v) => onChange({ ...operation, printerId: v })}
            emptyOptionLabel="—"
            options={catalogDropdownOptions(
              catalogs.printers,
              operation.printerId,
              printerLabel,
              printerDetailLabel,
            )}
          />
          <Dropdown
            id={`${idPrefix}-press-operator`}
            label="печатник"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogDropdownOptions(
              catalogs.pressOperators,
              operation.operatorId,
              operatorLabel,
              operatorDetailLabel,
            )}
          />
        </div>
      </article>
    );
  }

  if (operation.kind === "laminate") {
    const films = catalogs.films ?? [];

    const selectFilm = (filmId) => {
      if (filmId === "") {
        onChange({
          ...operation,
          filmId: "",
          film: emptyFilmFields(),
        });
        return;
      }
      const film = films.find((row) => String(row.id) === filmId);
      if (!film) {
        onChange({ ...operation, filmId });
        return;
      }
      onChange({
        ...operation,
        filmId,
        film: filmOptionFromCatalog(film),
      });
    };

    const filmValue = resolveFilmId(operation.filmId, operation.film, films);

    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <div className={styles.fieldRow}>
          <Dropdown
            id={`${idPrefix}-laminator`}
            label="Ламинатор"
            value={operation.laminatorId}
            onChange={(v) => onChange({ ...operation, laminatorId: v })}
            emptyOptionLabel="—"
            options={catalogDropdownOptions(
              catalogs.laminators,
              operation.laminatorId,
              laminatorLabel,
              laminatorDetailLabel,
            )}
          />
          <Dropdown
            id={`${idPrefix}-laminate-operator`}
            label="Оператор"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogDropdownOptions(
              catalogs.laminatorOperators,
              operation.operatorId,
              operatorLabel,
              operatorDetailLabel,
            )}
          />
          <Dropdown
            id={`${idPrefix}-film`}
            label="Плёнка"
            value={filmValue}
            onChange={selectFilm}
            emptyOptionLabel="—"
            options={films.map((film) => ({
              value: String(film.id),
              label: catalogSelectOptionLabel({
                value: filmValue,
                optionValue: film.id,
                shortLabel: filmShortLabel(film),
                detailLabel: filmLabel(film),
              }),
            }))}
          />
        </div>
      </article>
    );
  }

  if (operation.kind === "cut") {
    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <div className={styles.fieldRow}>
          <Dropdown
            id={`${idPrefix}-cutter`}
            label="Резак"
            value={operation.cutterId}
            onChange={(v) => onChange({ ...operation, cutterId: v })}
            emptyOptionLabel="—"
            options={catalogDropdownOptions(
              catalogs.cutters,
              operation.cutterId,
              cutterLabel,
              cutterDetailLabel,
            )}
          />
          <Dropdown
            id={`${idPrefix}-cut-operator`}
            label="Рез"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogDropdownOptions(
              catalogs.cutterOperators,
              operation.operatorId,
              operatorLabel,
              operatorDetailLabel,
            )}
          />
        </div>
      </article>
    );
  }

  return null;
}