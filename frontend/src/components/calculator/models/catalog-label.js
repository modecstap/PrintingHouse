import { formatMoney } from "../../../lib/format-money";

export function catalogSelectOptionLabel({
  value,
  optionValue,
  shortLabel,
  detailLabel,
}) {
  if (value !== "" && value != null && String(value) === String(optionValue)) {
    return detailLabel;
  }
  return shortLabel;
}

export function printerLabel(printer) {
  return printer.name;
}

export function printerDetailLabel(printer) {
  return `${printer.name}`;
}

export function laminatorLabel(laminator) {
  return laminator.name;
}

export function laminatorDetailLabel(laminator) {
  return `${laminator.name}`;
}

export function cutterLabel(cutter) {
  return cutter.name;
}

export function cutterDetailLabel(cutter) {
  return `${cutter.name}, стопа ${cutter.max_stack}`;
}

export function operatorLabel(operator) {
  return operator.name;
}

export function operatorDetailLabel(operator) {
  return `${operator.name}`;
}

function sheetSizeLabel(format) {
  if (format.name.trim() !== "") {
    return format.name;
  }
  return `${format.width}x${format.height}`;
}

export function sheetLabel(sheet) {
  const { paper, format } = sheet;
  return `${paper.name} - ${paper.density} - ${sheetSizeLabel(format)}`;
}

export function filmShortLabel(film) {
  return film.name;
}

export function filmLabel(film) {
  return `${film.name}, ${formatMoney(film.price)}, плотность ${film.density}`;
}

export function edgesLabel(edges) {
  const title = edges.name.trim() !== "" ? edges.name : `№ ${edges.id}`;
  return `${title}`;
}

export function chromaLabel(chroma) {
  const title = chroma.name.trim() !== "" ? chroma.name : `№ ${chroma.id}`;
  return `${title}`;
}
