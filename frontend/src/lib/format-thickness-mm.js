export function formatThicknessMm(value) {
  if (value == null || value === "") {
    return "";
  }
  const num = Number(value);
  if (!Number.isFinite(num)) {
    return String(value);
  }
  return num.toFixed(2).replace(/\.?0+$/, "");
}
