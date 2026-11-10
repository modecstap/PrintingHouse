import {
  emptyCutOperation,
  emptyDieCutOperation,
  emptyLaminateOperation,
  emptyPrintOperation,
} from "../models/order";
import { sheetLabel } from "../models/catalog-label";
import OperationFields from "./operation-fields";
import { Dropdown } from "../../generic/dropdown/dropdown";
import Button from "../../generic/button/button";
import { TextField } from "../../generic/text-field/text-field";
import styles from "../calculator.module.css";

function emptyPaperFields() {
  return {
    name: "",
    density: "",
    thickness: "",
    price_per_kilo: "0",
  };
}

function paperFromSheet(sheet) {
  return {
    name: sheet.paper.name,
    density: String(sheet.paper.density),
    thickness: String(sheet.paper.thickness),
    price_per_kilo: sheet.paper.price_per_kilo,
  };
}

function sheetFormatFromSheet(sheet) {
  if (!sheet.format) {
    return { name: "", width: "0", height: "0" };
  }
  return {
    name: sheet.format.name,
    width: String(sheet.format.width),
    height: String(sheet.format.height),
  };
}

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

  const removeOperation = (clientKey) => {
    update({
      operations: block.operations.filter((op) => op.clientKey !== clientKey),
    });
  };

  const addOperation = (factory) => {
    update({ operations: [...block.operations, factory()] });
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
      <div className={styles.operationHeading}>
        <h3 className={styles.blockHeading}>{`Блок ${index + 1}`}</h3>
        <Button type="button" onClick={onRemove} disabled={soleBlock}>
          Удалить
        </Button>
      </div>

      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-block-count`}
          label="Копии"
          value={block.count}
          type="number"
          onChange={(v) => update({ count: v })}
        />
        <TextField
          id={`${idPrefix}-markup`}
          label="Наценка (%)"
          value={block.markup}
          type="number"
          onChange={(v) => update({ markup: v })}
        />
      </div>

      <p className={styles.legend}>Формат</p>
      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-target-width`}
          label="Ширина (мм)"
          value={block.target.width}
          type="number"
          onChange={(v) => update({ target: { ...block.target, width: v } })}
        />
        <TextField
          id={`${idPrefix}-target-height`}
          label="Высота (мм)"
          value={block.target.height}
          type="number"
          onChange={(v) => update({ target: { ...block.target, height: v } })}
        />
      </div>

      <p className={styles.legend}>Бумага</p>
      <div className={styles.fieldRow}>
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
      </div>

      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-bleeds`}
          label="Вылеты (мм)"
          value={block.bleeds}
          type="number"
          onChange={(v) => update({ bleeds: v })}
        />
        <TextField
          id={`${idPrefix}-spacing`}
          label="Поля листа (мм)"
          value={block.spacing}
          type="number"
          onChange={(v) => update({ spacing: v })}
        />
      </div>
      
      <EdgeButtonRow
        existingKinds={existingKinds}
        onPrint={() => addOperation(emptyPrintOperation)}
        onLaminate={() => addOperation(emptyLaminateOperation)}
        onCut={() => addOperation(emptyCutOperation)}
        onDieCut={() => addOperation(emptyDieCutOperation)}
      />

      {block.operations.map((operation) => (
        <OperationFields
          key={operation.clientKey}
          operation={operation}
          catalogs={catalogs}
          onChange={(next) => updateOperation(operation.clientKey, next)}
          onRemove={() => removeOperation(operation.clientKey)}
        />
      ))}

      
    </section>
  );
}

function EdgeButtonRow({
  existingKinds,
  onPrint,
  onLaminate,
  onCut,
  onDieCut,
}) {
  return (
    <div className={styles.fieldRow}>
      {!existingKinds.has("print") ? (
        <Button type="button" onClick={onPrint}>
          + Печать
        </Button>
      ) : null}
      {!existingKinds.has("laminate") ? (
        <Button type="button" onClick={onLaminate}>
          + Ламинация
        </Button>
      ) : null}
      {!existingKinds.has("cut") ? (
        <Button type="button" onClick={onCut}>
          + Рез
        </Button>
      ) : null}
      {!existingKinds.has("die_cut") ? (
        <Button type="button" onClick={onDieCut}>
          + Высечка
        </Button>
      ) : null}
    </div>
  );
}
