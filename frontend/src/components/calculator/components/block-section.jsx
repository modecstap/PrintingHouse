import { useMemo, useState } from "react";
import {
  applyOperationCatalogDefaults,
  emptyDieCutOperation,
  emptyLaminateOperation,
  emptyPaperFields,
  isDieCutOperationActive,
  isLaminateOperationActive,
  paperFromSheet,
  sheetFormatFromSheet,
  sortBlockOperationsByKind,
} from "../models/order";
import {
  catalogSelectOptionLabel,
  edgesLabel,
  operatorDetailLabel,
  operatorLabel,
  sheetLabel,
} from "../models/catalog-label";
import {
  CHROMA_OPTIONS,
  LAMINATION_OPTIONS,
} from "../models/operation-options";
import {
  filterSheetsByPaperFilters,
  isSelectedPaperSheetInFilteredList,
  resolvePaperSheetId,
  uniquePaperDensityOptionsFromSheets,
  uniquePaperTypeOptionsFromSheets,
} from "../models/sheet-paper-filters";
import OperationFields from "./operation-fields";
import { Dropdown } from "../../generic/dropdown/dropdown";
import Button from "../../generic/button/button";
import { TextField } from "../../generic/text-field/text-field";
import styles from "../calculator.module.css";

function findBlockOperation(block, kind) {
  return block.operations.find((operation) => operation.kind === kind);
}

function replaceBlockOperation(block, kind, nextOperation) {
  const hasKind = block.operations.some((operation) => operation.kind === kind);
  const operations = hasKind
    ? block.operations.map((operation) =>
        operation.kind === kind ? nextOperation : operation,
      )
    : sortBlockOperationsByKind([...block.operations, nextOperation]);
  return { ...block, operations };
}

function resetInactiveLaminateOperation(operation, lamination) {
  return {
    ...emptyLaminateOperation(),
    clientKey: operation.clientKey,
    lamination,
  };
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
  const sheets = catalogs.sheets ?? [];

  const [paperTypeFilter, setPaperTypeFilter] = useState("");
  const [paperDensityFilter, setPaperDensityFilter] = useState("");

  const printOperation = findBlockOperation(block, "print");
  const laminateOperation = findBlockOperation(block, "laminate");
  const dieCutOperation = findBlockOperation(block, "die_cut");

  const paperTypeOptions = useMemo(
    () => uniquePaperTypeOptionsFromSheets(sheets),
    [sheets],
  );
  const paperDensityOptions = useMemo(
    () => uniquePaperDensityOptionsFromSheets(sheets),
    [sheets],
  );
  const filteredSheets = useMemo(
    () =>
      filterSheetsByPaperFilters(sheets, paperTypeFilter, paperDensityFilter),
    [sheets, paperTypeFilter, paperDensityFilter],
  );

  const update = (partial) => onChange({ ...block, ...partial });

  const updateOperation = (clientKey, next) => {
    update({
      operations: block.operations.map((op) =>
        op.clientKey === clientKey ? next : op,
      ),
    });
  };

  const updatePrintOperation = (partial) => {
    if (!printOperation) {
      return;
    }
    updateOperation(printOperation.clientKey, { ...printOperation, ...partial });
  };

  const setLamination = (lamination) => {
    const base = laminateOperation ?? emptyLaminateOperation();
    let next = { ...base, lamination };
    if (isLaminateOperationActive(next)) {
      next = applyOperationCatalogDefaults(next, catalogs);
    } else {
      next = resetInactiveLaminateOperation(base, lamination);
    }
    onChange(replaceBlockOperation(block, "laminate", next));
  };

  const setDieCutOperator = (operatorId) => {
    const base = dieCutOperation ?? emptyDieCutOperation();
    let next = { ...base, operatorId };
    if (isDieCutOperationActive(next)) {
      next = applyOperationCatalogDefaults(next, catalogs);
    }
    onChange(replaceBlockOperation(block, "die_cut", next));
  };

  const edgesRows = catalogs.edges ?? [];
  const showEdgesDropdown = edgesRows.length > 0;
  const showManualEdgeFields = !showEdgesDropdown || block.edgesManual;

  const selectEdgesProfile = (edgesId) => {
    if (edgesId === "") {
      update({ edgesId: "", edgesName: "", edgesManual: true });
      return;
    }
    const row = edgesRows.find((item) => String(item.id) === edgesId);
    if (!row) {
      return;
    }
    update({
      edgesId,
      edgesName: row.name,
      edgesManual: false,
      bleeds: String(row.bleeds),
      spacing: String(row.spacing),
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
    const sheet = sheets.find((row) => String(row.id) === sheetId);
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
    sheets,
  );

  const onPaperTypeFilterChange = (nextType) => {
    const nextFiltered = filterSheetsByPaperFilters(
      sheets,
      nextType,
      paperDensityFilter,
    );
    if (
      !isSelectedPaperSheetInFilteredList(
        block.paperSheetId,
        block.paper,
        sheets,
        nextFiltered,
      )
    ) {
      selectPaperSheet("");
    }
    setPaperTypeFilter(nextType);
  };

  const onPaperDensityFilterChange = (nextDensity) => {
    const nextFiltered = filterSheetsByPaperFilters(
      sheets,
      paperTypeFilter,
      nextDensity,
    );
    if (
      !isSelectedPaperSheetInFilteredList(
        block.paperSheetId,
        block.paper,
        sheets,
        nextFiltered,
      )
    ) {
      selectPaperSheet("");
    }
    setPaperDensityFilter(nextDensity);
  };

  const visibleOperations = sortBlockOperationsByKind(block.operations).filter(
    (operation) => {
      if (operation.kind === "die_cut") {
        return false;
      }
      if (operation.kind === "laminate") {
        return isLaminateOperationActive(operation);
      }
      return true;
    },
  );

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
          {showEdgesDropdown && (
            <Dropdown
              id={`${idPrefix}-edges-profile`}
              label="Края"
              value={block.edgesManual ? "" : block.edgesId}
              onChange={selectEdgesProfile}
              emptyOptionLabel="Вручную"
              options={edgesRows.map((row) => ({
                value: String(row.id),
                label: edgesLabel(row),
              }))}
            />
          )}
          {showManualEdgeFields && (
            <>
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
            </>
          )}
        </div>
        <div className={styles.right}>
          <Dropdown
            id={`${idPrefix}-paper-type-filter`}
            label="Тип"
            value={paperTypeFilter}
            onChange={onPaperTypeFilterChange}
            emptyOptionLabel="—"
            options={paperTypeOptions}
          />
          <Dropdown
            id={`${idPrefix}-paper-density-filter`}
            label="Плотность"
            value={paperDensityFilter}
            onChange={onPaperDensityFilterChange}
            emptyOptionLabel="—"
            options={paperDensityOptions}
          />
          <Dropdown
            id={`${idPrefix}-paper-sheet`}
            label="Бумага"
            value={paperSheetValue}
            onChange={selectPaperSheet}
            emptyOptionLabel="—"
            options={filteredSheets.map((sheet) => ({
              value: String(sheet.id),
              label: sheetLabel(sheet),
            }))}
          />
        </div>
        <div className={styles.thirdColumn}>
          {printOperation && (
            <Dropdown
              id={`${idPrefix}-chroma`}
              label="Цветность"
              value={printOperation.chroma}
              onChange={(v) => updatePrintOperation({ chroma: v })}
              emptyOptionLabel="—"
              options={CHROMA_OPTIONS}
            />
          )}
          <Dropdown
            id={`${idPrefix}-lamination`}
            label="Ламинация"
            value={laminateOperation?.lamination ?? ""}
            onChange={setLamination}
            emptyOptionLabel="—"
            options={LAMINATION_OPTIONS}
          />
          <Dropdown
            id={`${idPrefix}-die-cut-operator`}
            label="Высечка"
            value={dieCutOperation?.operatorId ?? ""}
            onChange={setDieCutOperator}
            emptyOptionLabel="—"
            options={(catalogs.dieCutOperators ?? []).map((operator) => ({
              value: String(operator.id),
              label: catalogSelectOptionLabel({
                value: dieCutOperation?.operatorId ?? "",
                optionValue: operator.id,
                shortLabel: operatorLabel(operator),
                detailLabel: operatorDetailLabel(operator),
              }),
            }))}
          />
        </div>
      </div>

      <div className={styles.operations}>
        {visibleOperations.map((operation) => (
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