import {
  cutterLabel,
  filmLabel,
  laminatorLabel,
  operatorLabel,
  printerLabel,
} from "../models/catalog-label";
import { Dropdown } from "../../generic/dropdown/dropdown";
import styles from "../calculator.module.css";

const CHROMA_OPTIONS = [
  { value: "ZERO_ZERO", label: "0+0" },
  { value: "ONE_ZERO", label: "1+0" },
  { value: "ONE_ONE", label: "1+1" },
  { value: "FOUR_ZERO", label: "4+0" },
  { value: "FOUR_ONE", label: "4+1" },
  { value: "FOUR_FOUR", label: "4+4" },
];

const LAMINATION_OPTIONS = [
  { value: "DONT", label: "Нет" },
  { value: "ONE_ZERO", label: "1+0" },
  { value: "ONE_ONE", label: "1+1" },
];

const KIND_HEADING = {
  print: "Печать",
  laminate: "Ламинация",
  cut: "Рез",
  die_cut: "Высечка",
};

function emptyFilmFields() {
  return { name: "", price: "0", density: "0" };
}

function filmFromCatalog(film) {
  return {
    name: film.name,
    price: film.price,
    density: String(film.density),
  };
}

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
            options={catalogs.printers.map((p) => ({
              value: String(p.id),
              label: printerLabel(p),
            }))}
          />
          <Dropdown
            id={`${idPrefix}-press-operator`}
            label="Печатник"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogs.pressOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
          <Dropdown
            id={`${idPrefix}-chroma`}
            label="Цветность"
            value={operation.chroma}
            onChange={(v) => onChange({ ...operation, chroma: v })}
            options={CHROMA_OPTIONS}
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
        film: filmFromCatalog(film),
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
            options={catalogs.laminators.map((l) => ({
              value: String(l.id),
              label: laminatorLabel(l),
            }))}
          />
          <Dropdown
            id={`${idPrefix}-laminate-operator`}
            label="Оператор"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogs.laminatorOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
          <Dropdown
            id={`${idPrefix}-lamination`}
            label="Ламинация"
            value={operation.lamination}
            onChange={(v) => onChange({ ...operation, lamination: v })}
            options={LAMINATION_OPTIONS}
          />
          <Dropdown
            id={`${idPrefix}-film`}
            label="Плёнка"
            value={filmValue}
            onChange={selectFilm}
            emptyOptionLabel="—"
            options={films.map((film) => ({
              value: String(film.id),
              label: filmLabel(film),
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
            options={catalogs.cutters.map((c) => ({
              value: String(c.id),
              label: cutterLabel(c),
            }))}
          />
          <Dropdown
            id={`${idPrefix}-cut-operator`}
            label="Оператор"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogs.cutterOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
        </div>
      </article>
    );
  }

  if (operation.kind === "die_cut") {
    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <div className={styles.fieldRow}>
          <Dropdown
            id={`${idPrefix}-die-cut-operator`}
            label="Оператор"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            emptyOptionLabel="—"
            options={catalogs.dieCutOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
        </div>
      </article>
    );
  }

  return null;
}
