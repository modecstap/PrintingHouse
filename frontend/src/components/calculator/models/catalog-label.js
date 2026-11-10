import { formatMoney } from "../../../lib/format-money";

export function printerLabel(printer) {
  return `№ ${printer.id}`;
}

export function laminatorLabel(laminator) {
  return `№ ${laminator.id}`;
}

export function cutterLabel(cutter) {
  return `№ ${cutter.id}`;
}

export function operatorLabel(operator) {
  return `№ ${operator.id}, ${formatMoney(operator.salary_by_operation)}`;
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
