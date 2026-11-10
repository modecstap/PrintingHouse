export {
  toPrinter,
  toLaminator,
  toCutter,
  toOperator,
  toSheet,
  toFilm,
  toPrinterList,
  toLaminatorList,
  toCutterList,
  toOperatorList,
  toSheetList,
  toFilmList,
} from "../../../lib/catalog-parsers";

export function toJsonInt(value) {
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (/^-?\d+$/.test(trimmed)) {
      return Number(trimmed);
    }
    return trimmed;
  }
  return value;
}

export function toJsonDecimal(value) {
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (/^-?\d+(\.\d{1,2})?$/.test(trimmed)) {
      return Number(trimmed);
    }
    return trimmed;
  }
  return value;
}
