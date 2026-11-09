import { formatMoney } from "../../../lib/format-money";

export function toPrinter(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("printer: id must be a number");
  }
  if (typeof raw?.startup !== "string") {
    throw new Error("printer: startup must be a string");
  }
  if (typeof raw?.cyan !== "string") {
    throw new Error("printer: cyan must be a string");
  }
  if (typeof raw?.magenta !== "string") {
    throw new Error("printer: magenta must be a string");
  }
  if (typeof raw?.yellow !== "string") {
    throw new Error("printer: yellow must be a string");
  }
  if (typeof raw?.black !== "string") {
    throw new Error("printer: black must be a string");
  }
  return {
    id: raw.id,
    startup: raw.startup,
    cyan: raw.cyan,
    magenta: raw.magenta,
    yellow: raw.yellow,
    black: raw.black,
  };
}

export function toLaminator(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("laminator: id must be a number");
  }
  if (typeof raw?.startup !== "string") {
    throw new Error("laminator: startup must be a string");
  }
  return { id: raw.id, startup: raw.startup };
}

export function toCutter(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("cutter: id must be a number");
  }
  if (typeof raw?.max_stack !== "number") {
    throw new Error("cutter: max_stack must be a number");
  }
  return { id: raw.id, max_stack: raw.max_stack };
}

export function toOperator(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("operator: id must be a number");
  }
  if (typeof raw?.salary_by_operation !== "string") {
    throw new Error("operator: salary_by_operation must be a string");
  }
  return { id: raw.id, salary_by_operation: raw.salary_by_operation };
}

export function printerLabel(printer) {
  return `№ ${printer.id}, запуск ${formatMoney(printer.startup)}, C ${formatMoney(printer.cyan)}, M ${formatMoney(printer.magenta)}, Y ${formatMoney(printer.yellow)}, K ${formatMoney(printer.black)}`;
}

export function laminatorLabel(laminator) {
  return `№ ${laminator.id}, запуск ${formatMoney(laminator.startup)}`;
}

export function cutterLabel(cutter) {
  return `№ ${cutter.id}, макс. стопа ${cutter.max_stack}`;
}

export function operatorLabel(operator) {
  return `№ ${operator.id}, зарплата ${formatMoney(operator.salary_by_operation)}`;
}
