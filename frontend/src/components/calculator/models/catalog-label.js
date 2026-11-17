import { formatMoney } from "../../../lib/format-money";

export function printerLabel(printer) {
  return printer.name;
}

export function laminatorLabel(laminator) {
  return laminator.name;
}

export function cutterLabel(cutter) {
  return cutter.name;
}

export function operatorLabel(operator) {
  return operator.name;
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

export function filmLabel(film) {
  return `${film.name}, ${formatMoney(film.price)}, плотность ${film.density}`;
}

export function edgesLabel(edges) {
  const title = edges.name.trim() !== "" ? edges.name : `№ ${edges.id}`;
  return `${title}`;
}
