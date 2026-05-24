export const formatPrice = (value) =>
  value == null ? "—" : `${Number(value).toFixed(2)} ₽`;