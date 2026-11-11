import {
  applyOperationCatalogDefaults,
  emptyDieCutOperation,
  emptyLaminateOperation,
  emptyPaperFields,
  paperFromSheet,
  sheetFormatFromSheet,
  sortBlockOperationsByKind,
} from "../models/order";
import { sheetLabel } from "../models/catalog-label";
import OperationFields from "./operation-fields";
import { Dropdown } from "../../generic/dropdown/dropdown";
import Button from "../../generic/button/button";
import { TextField } from "../../generic/text-field/text-field";
import { Checkbox } from "../../generic/checkbox/checkbox";
import styles from "../calculator.module.css";

const TOGGLE_OPERATION_KINDS = [
  { kind: "laminate", label: "Ламинация", factory: emptyLaminateOperation },
  { kind: "die_cut", label: "Высечка", factory: emptyDieCutOperation },
];

function resolvePaperSheetId(paperSheetId, paper, sheets) {
  if (paperSheetId) {
    return paperSheetId;
  }
  const match = sheets.find(
    (sheet) =>
      sheet.paper.name === paper.name &&
      String(sheet.paper.density) === String(paper.density) &&
      String(sheet.paper.thickness) === String(paper.thickness) &&
      sheet.paper.price_per_kilo === paper.price_per_kilo,
  );
  return match ? String(match.id) : "";
}

export default function BlockSection({
  block,
  index,
  catalogs,
  soleBlock,
  onChange,
  onRemove,
}) {
  const idPrefix = block.clientKey;

  const update = (partial) => onChange({ ...block, ...partial });

  const updateOperation = (clientKey, next) => {
    update({
      operations: block.operations.map((op) =>
        op.clientKey === clientKey ? next : op,
      ),
    });
  };

  const setOperationKindEnabled = (kind, factory, enabled) => {
    if (enabled) {
      if (block.operations.some((op) => op.kind === kind)) {
        return;
      }
      update({
        operations: sortBlockOperationsByKind([
          ...block.operations,
          applyOperationCatalogDefaults(factory(), catalogs),
        ]),
      });
      return;
    }
    update({
      operations: block.operations.filter((op) => op.kind !== kind),
    });
  };

  const selectPaperSheet = (sheetId) => {
    if (sheetId === "") {
      update({
        paperSheetId: "",
        paper: emptyPaperFields(),
        sheetFormat: { name: "", width: "0", height: "0" },
      });
      return;
    }
    const sheet = catalogs.sheets.find((row) => String(row.id) === sheetId);
    if (!sheet) {
      update({ paperSheetId: sheetId });
      return;
    }
    update({
      paperSheetId: sheetId,
      paper: paperFromSheet(sheet),
      sheetFormat: sheetFormatFromSheet(sheet),
    });
  };

  const paperSheetValue = resolvePaperSheetId(
    block.paperSheetId,
    block.paper,
    catalogs.sheets,
  );

  const existingKinds = new Set(block.operations.map((op) => op.kind));

  return (
    <section className={styles.calculatorBlock}>
      <div className={styles.heading}>
        <h3 className={styles.blockHeading}>{`Часть ${index + 1}`}</h3>
        <TextField
          id={`${idPrefix}-block-count`}
          label="Листов"
          value={block.count}
          type="number"
          onChange={(v) => update({ count: v })}
        />
        <Button type="button" onClick={onRemove} disabled={soleBlock}>
          Удалить
        </Button>
      </div>

      <div className={styles.blockContent}>
        <div className={styles.left}>
          <TextField
            id={`${idPrefix}-target-width`}
            label="Ширина"
            value={block.target.width}
            type="number"
            onChange={(v) => update({ target: { ...block.target, width: v } })}
          />
          <TextField
            id={`${idPrefix}-target-height`}
            label="Высота"
            value={block.target.height}
            type="number"
            onChange={(v) => update({ target: { ...block.target, height: v } })}
          />
        </div>
        <div className={styles.right}>
          <Dropdown
            id={`${idPrefix}-paper-sheet`}
            label="Бумага"
            value={paperSheetValue}
            onChange={selectPaperSheet}
            emptyOptionLabel="—"
            options={catalogs.sheets.map((sheet) => ({
              value: String(sheet.id),
                label: sheetLabel(sheet),
              }))}
          />
          <TextField
            id={`${idPrefix}-bleeds`}
            label="Вылеты"
            value={block.bleeds}
            type="number"
            onChange={(v) => update({ bleeds: v })}
          />
          <TextField
            id={`${idPrefix}-spacing`}
            label="Поля"
            value={block.spacing}
            type="number"
            onChange={(v) => update({ spacing: v })}
          />
        </div>
      </div>
      
      <OperationKindToggles
        idPrefix={idPrefix}
        existingKinds={existingKinds}
        onToggle={setOperationKindEnabled}
      />
      <div className={styles.operations}>
        {sortBlockOperationsByKind(block.operations).map((operation) => (
          <OperationFields
            key={operation.clientKey}
            operation={operation}
            catalogs={catalogs}
            onChange={(next) => updateOperation(operation.clientKey, next)}
          />
        ))}
      </div>
    </section>
  );
}

function OperationKindToggles({ idPrefix, existingKinds, onToggle }) {
  return (
    <div className={styles.operationKinds}>
      {TOGGLE_OPERATION_KINDS.map(({ kind, label, factory }) => {
        const inputId = `${idPrefix}-kind-${kind}`;
        return (
          <Checkbox
            key={kind}
            id={inputId}
            label={label}
            checked={existingKinds.has(kind)}
            onChange={(next) => onToggle(kind, factory, next)}
          />
        );
      })}
    </div>
  );
}
