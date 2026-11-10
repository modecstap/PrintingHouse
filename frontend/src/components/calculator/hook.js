import { useEffect, useRef, useState } from "react";
import { fetchReferences } from "../references/api/references";
import { fetchOrderForm } from "../orders/api/orders";
import { loadCatalogs } from "./api/catalog";
import { quoteOrder, saveOrder } from "./api/order";
import {
  applyCatalogDefaultsToForm,
  applyFilmsCatalogToForm,
  applySheetsCatalogToForm,
  applyBlockCatalogDefaults,
  emptyBlock,
  emptyCalculatorForm,
  isCalculatorFormReadyForQuote,
} from "./models/order";

const EMPTY_CATALOGS = {
  printers: [],
  laminators: [],
  cutters: [],
  pressOperators: [],
  laminatorOperators: [],
  cutterOperators: [],
  dieCutOperators: [],
  sheets: [],
  films: [],
};

function applyCatalogsToForm(formState, catalogs) {
  let next = applyCatalogDefaultsToForm(formState, catalogs);
  if (catalogs.sheets.length > 0) {
    next = applySheetsCatalogToForm(next, catalogs.sheets);
  }
  if (catalogs.films.length > 0) {
    next = applyFilmsCatalogToForm(next, catalogs.films);
  }
  return next;
}

export function useCalculator({
  initialForm = emptyCalculatorForm(),
  initialReport = null,
  onSaved,
} = {}) {
  const [form, setForm] = useState(initialForm);
  const [report, setReport] = useState(initialReport);
  const [catalogState, setCatalogState] = useState({
    status: "loading",
    catalogs: EMPTY_CATALOGS,
    message: null,
  });
  const [quoteState, setQuoteState] = useState({ status: "idle" });
  const [saveState, setSaveState] = useState({ status: "idle" });
  const [savedId, setSavedId] = useState(null);
  const [referencesState, setReferencesState] = useState({
    status: "loading",
    references: [],
    message: null,
  });
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [presetLoadState, setPresetLoadState] = useState({ status: "idle" });
  const quoteRequestId = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    loadCatalogs(controller.signal).then(({ catalogs, error }) => {
      if (controller.signal.aborted) {
        return;
      }
      const merged = { ...EMPTY_CATALOGS, ...catalogs };
      setCatalogState({
        status: error ? "error" : "success",
        catalogs: merged,
        message: error,
      });
      if (!error) {
        setForm((prev) => applyCatalogsToForm(prev, merged));
      }
    });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchReferences(controller.signal)
      .then((references) => {
        if (controller.signal.aborted) {
          return;
        }
        setReferencesState({ status: "success", references, message: null });
      })
      .catch((error) => {
        if (error?.name === "AbortError" || controller.signal.aborted) {
          return;
        }
        setReferencesState({
          status: "error",
          references: [],
          message:
            error instanceof Error
              ? error.message
              : "Не удалось загрузить пресеты",
        });
      });
    return () => controller.abort();
  }, []);

  const actionBusy =
    quoteState.status === "loading" || saveState.status === "loading";

  const actionError =
    quoteState.status === "error"
      ? quoteState.message
      : saveState.status === "error"
        ? saveState.message
        : presetLoadState.status === "error"
          ? presetLoadState.message
          : catalogState.status === "error"
            ? catalogState.message
            : referencesState.status === "error"
              ? referencesState.message
              : null;

  const presetBusy = presetLoadState.status === "loading";

  useEffect(() => {
    if (
      catalogState.status !== "success" ||
      presetBusy ||
      !isCalculatorFormReadyForQuote(form)
    ) {
      return undefined;
    }

    const requestId = ++quoteRequestId.current;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setQuoteState({ status: "loading" });
      setSaveState((prev) =>
        prev.status === "error" ? { status: "idle" } : prev,
      );
      quoteOrder(form, controller.signal)
        .then((nextReport) => {
          if (requestId !== quoteRequestId.current) {
            return;
          }
          setReport(nextReport);
          setQuoteState({ status: "success" });
        })
        .catch((error) => {
          if (error?.name === "AbortError") {
            return;
          }
          if (requestId !== quoteRequestId.current) {
            return;
          }
          setQuoteState({
            status: "error",
            message:
              error instanceof Error
                ? error.message
                : "Произошла неизвестная ошибка",
          });
        });
    }, 300);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [form, catalogState.status, presetBusy]);

  const handleSave = async () => {
    setSaveState({ status: "loading" });
    setQuoteState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    setSavedId(null);
    try {
      const id = await saveOrder(form);
      setSavedId(id);
      setSaveState({ status: "success" });
      if (onSaved) {
        onSaved(id);
      }
    } catch (error) {
      setSaveState({
        status: "error",
        message:
          error instanceof Error ? error.message : "Произошла неизвестная ошибка",
      });
    }
  };

  const updateBlock = (clientKey, nextBlock) => {
    setForm({
      ...form,
      blocks: form.blocks.map((block) =>
        block.clientKey === clientKey ? nextBlock : block,
      ),
    });
  };

  const removeBlock = (clientKey) => {
    setForm({
      ...form,
      blocks: form.blocks.filter((block) => block.clientKey !== clientKey),
    });
  };

  const addBlock = () => {
    setForm({
      ...form,
      blocks: [
        ...form.blocks,
        applyBlockCatalogDefaults(emptyBlock(), catalogState.catalogs),
      ],
    });
  };

  const handlePresetChange = async (event) => {
    const orderId = event.target.value;
    setSelectedPresetId(orderId);
    setPresetLoadState({ status: "idle" });
    setQuoteState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    setSaveState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    if (orderId === "") {
      return;
    }

    setPresetLoadState({ status: "loading" });
    setReport(null);
    setSavedId(null);
    try {
      const loaded = await fetchOrderForm(Number(orderId));
      setForm(applyCatalogsToForm(loaded, catalogState.catalogs));
      setPresetLoadState({ status: "success" });
    } catch (error) {
      setPresetLoadState({
        status: "error",
        message:
          error instanceof Error ? error.message : "Не удалось загрузить пресет",
      });
    }
  };

  return {
    form,
    setForm,
    report,
    catalogState,
    quoteState,
    savedId,
    referencesState,
    selectedPresetId,
    actionBusy,
    actionError,
    presetBusy,
    handleSave,
    updateBlock,
    removeBlock,
    addBlock,
    handlePresetChange,
  };
}
