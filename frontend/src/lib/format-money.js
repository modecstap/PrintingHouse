function incrementWhole(whole) {
  let carry = 1;
  const digits = whole.split("");
  for (let i = digits.length - 1; i >= 0 && carry; i -= 1) {
    const code = digits[i].charCodeAt(0);
    if (code === 57) {
      digits[i] = "0";
    } else {
      digits[i] = String.fromCharCode(code + 1);
      carry = 0;
    }
  }
  if (carry) {
    digits.unshift("1");
  }
  return digits.join("");
}

function roundTwoDecimals(sign, whole, fractionDigits) {
  const f0 = fractionDigits[0] ?? "0";
  const f1 = fractionDigits[1] ?? "0";
  const f2 = fractionDigits[2] ?? "0";

  let d0 = f0;
  let d1 = f1;
  let wholePart = whole;

  if (f2 >= "5") {
    if (d1 === "9") {
      d1 = "0";
      if (d0 === "9") {
        d0 = "0";
        wholePart = incrementWhole(wholePart);
      } else {
        d0 = String.fromCharCode(d0.charCodeAt(0) + 1);
      }
    } else {
      d1 = String.fromCharCode(d1.charCodeAt(0) + 1);
    }
  }

  const amount = `${wholePart}.${d0}${d1}`;
  return sign ? `${sign}${amount}` : amount;
}

export function formatMoney(value) {
  if (value === null || value === "") {
    return "—";
  }

  const trimmed = String(value).trim();
  if (trimmed === "") {
    return "—";
  }

  const match = trimmed.match(/^(-?)(\d+)(?:\.(\d*))?$/);
  if (!match) {
    return "—";
  }

  const sign = match[1];
  const whole = match[2];
  const fraction = match[3] ?? "";
  const rounded = roundTwoDecimals(sign, whole, fraction);

  return `${rounded} ₽`;
}
